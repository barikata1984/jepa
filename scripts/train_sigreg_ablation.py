"""SIGReg weight ablation: train LeWM with varying regularization pressure.

Tests whether SIGReg pressure directly hurts prediction quality by varying
only the regularization weight while keeping architecture constant (d=192).

Usage:
  cd scripts && python train_sigreg_ablation.py --sigreg-weight 0.009 --dataset robomind
"""

import argparse
import json
import os
from functools import partial
from pathlib import Path

import hydra
import lightning as pl
import numpy as np
import stable_pretraining as spt
from stable_pretraining import data as dt
import stable_worldmodel as swm
import torch
from omegaconf import OmegaConf, open_dict

from stable_worldmodel.data import column_normalizer as get_column_normalizer
from stable_worldmodel.wm.loss import SIGReg
from train_lewm_diagnostics import (
    LatentDiagnosticsCallback,
    SafeDataset,
    get_img_preprocessor,
    safe_collate,
)
from train_lewm_robomind import load_robomind_datasets

ROBOMIND_DIR = "/tmp/robomind_lerobot/benchmark1_1_release/ur_1rgb"


def lejepa_forward(self, batch, stage, cfg):
    ctx_len = cfg.wm.history_size
    n_preds = cfg.wm.num_preds
    lambd = cfg.loss.sigreg.weight

    batch["action"] = torch.nan_to_num(batch["action"], 0.0)
    output = self.model.encode(batch)

    emb = output["emb"]
    act_emb = output["act_emb"]

    ctx_emb = emb[:, :ctx_len]
    ctx_act = act_emb[:, :ctx_len]
    tgt_emb = emb[:, n_preds:]
    pred_emb = self.model.predict(ctx_emb, ctx_act)

    output["pred_loss"] = (pred_emb - tgt_emb).pow(2).mean()

    if lambd > 0:
        output["sigreg_loss"] = self.sigreg(emb.transpose(0, 1))
        output["loss"] = output["pred_loss"] + lambd * output["sigreg_loss"]
    else:
        output["sigreg_loss"] = torch.tensor(0.0, device=emb.device)
        output["loss"] = output["pred_loss"]

    losses_dict = {f"{stage}/{k}": v.detach() for k, v in output.items() if "loss" in k}
    self.log_dict(losses_dict, on_step=True, sync_dist=True)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sigreg-weight", type=float, required=True)
    parser.add_argument(
        "--dataset", choices=["berkeley", "robomind"], default="robomind"
    )
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    weight = args.sigreg_weight
    output_dir = Path(args.output_dir or "notes/LOGS/sigreg_ablation")
    output_dir = (
        (Path(__file__).resolve().parent.parent / output_dir)
        if not output_dir.is_absolute()
        else output_dir
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    weight_str = f"{weight:.4f}".replace(".", "p")
    output_path = output_dir / f"{args.dataset}_w{weight_str}.json"

    print(f"\n{'=' * 60}")
    print(f"  SIGReg Weight Ablation: weight={weight}")
    print(f"  dataset={args.dataset}, epochs={args.epochs}, d_latent=192")
    print(f"{'=' * 60}\n")

    with hydra.initialize(version_base=None, config_path="config"):
        cfg = hydra.compose(config_name="lewm", overrides=["data=ur5"])

    with open_dict(cfg):
        cfg.loss.sigreg.weight = weight
        cfg.trainer.max_epochs = args.epochs
        cfg.loader.batch_size = args.batch_size

    # Load dataset
    if args.dataset == "berkeley":
        with open_dict(cfg):
            cfg.data.dataset.name = "lerobot://lerobot/berkeley_autolab_ur5"
            cfg.data.dataset.primary_camera_key = "observation.images.image"
        dataset_cfg = OmegaConf.to_container(cfg.data.dataset, resolve=True)
        ds_name = dataset_cfg.pop("name")
        cache_dir = os.environ.get("LOCAL_DATASET_DIR", None)
        dataset = swm.data.load_dataset(
            ds_name, transform=None, cache_dir=cache_dir, **dataset_cfg
        )
    else:
        dataset = load_robomind_datasets(
            ROBOMIND_DIR, num_steps=cfg.data.dataset.num_steps
        )

    transforms = [
        get_img_preprocessor(source="pixels", target="pixels", img_size=cfg.img_size)
    ]
    with open_dict(cfg):
        for col in cfg.data.dataset.keys_to_load:
            if col.startswith("pixels"):
                continue
            normalizer = get_column_normalizer(dataset, col, col)
            transforms.append(normalizer)
        cfg.model.action_encoder.input_dim = (
            cfg.data.dataset.frameskip * dataset.get_dim("action")
        )

    transform = spt.data.transforms.Compose(*transforms)
    dataset.transform = transform

    # Split
    rnd_gen = torch.Generator().manual_seed(cfg.seed)
    if args.dataset == "berkeley":
        train_set, val_set = spt.data.random_split(
            dataset, lengths=[cfg.train_split, 1 - cfg.train_split], generator=rnd_gen
        )
    else:
        n_total = len(dataset)
        n_train = int(n_total * cfg.train_split)
        train_set, val_set = torch.utils.data.random_split(
            dataset, [n_train, n_total - n_train], generator=rnd_gen
        )

    train_set = SafeDataset(train_set)
    val_set = SafeDataset(val_set)

    train_loader = torch.utils.data.DataLoader(
        train_set, **cfg.loader, generator=rnd_gen, collate_fn=safe_collate
    )
    val_cfg = {**cfg.loader}
    val_cfg["shuffle"] = False
    val_cfg["drop_last"] = False
    val_loader = torch.utils.data.DataLoader(
        val_set, **val_cfg, collate_fn=safe_collate
    )

    world_model = hydra.utils.instantiate(cfg.model)
    n_params = sum(p.numel() for p in world_model.parameters())
    print(f"Model parameters: {n_params:,}")

    total_steps = cfg.trainer.max_epochs * len(train_loader)
    optimizers = {
        "model_opt": {
            "modules": "model",
            "optimizer": dict(cfg.optimizer),
            "scheduler": {
                "type": "LinearWarmupCosineAnnealingLR",
                "warmup_steps": max(1, int(0.01 * total_steps)),
                "max_steps": total_steps,
            },
            "interval": "epoch",
        },
    }

    diagnostics_cb = LatentDiagnosticsCallback(
        output_path=str(output_path).replace(".json", "_diag.json")
    )
    module = spt.Module(
        model=world_model,
        sigreg=SIGReg(**cfg.loss.sigreg.kwargs),
        forward=partial(lejepa_forward, cfg=cfg),
        optim=optimizers,
    )
    trainer = pl.Trainer(
        **cfg.trainer,
        num_sanity_val_steps=0,
        logger=False,
        enable_checkpointing=False,
        callbacks=[diagnostics_cb],
    )
    data_module = spt.data.DataModule(train=train_loader, val=val_loader)
    manager = spt.Manager(trainer=trainer, module=module, data=data_module)
    manager()

    stage1 = diagnostics_cb.epoch_results

    # Save results
    combined = {
        "config": {
            "sigreg_weight": weight,
            "d_latent": 192,
            "dataset": args.dataset,
            "epochs": args.epochs,
            "n_params": n_params,
        },
        "diagnostics": stage1,
    }
    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)

    if stage1:
        final = stage1[-1]
        eff = final["effective_rank"]
        pred = final["avg_pred_loss"]
        sig = final["avg_sigreg_loss"]
        ratio = final["sigreg_pred_ratio"]
        print(f"\n{'=' * 70}")
        print(f"  RESULT: SIGReg weight={weight}, {args.dataset}")
        print(f"{'=' * 70}")
        print(f"  Eff rank: {eff:.1f}/192 ({eff / 192:.0%})")
        print(f"  pred_loss: {pred:.6f}")
        print(f"  sigreg_loss: {sig:.6f}")
        print(f"  SIGReg/pred: {ratio:.1f}")
        collapsed = eff < 5
        print(f"  Collapsed: {'YES' if collapsed else 'No'}")
        print(f"  Saved: {output_path}")


if __name__ == "__main__":
    main()
