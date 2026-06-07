"""Latent dimension sweep: train LeWM with varying ViT hidden_size + evaluate.

Trains one condition (one d_latent value on one dataset), records per-epoch
diagnostics (Stage 1), then runs signal/noise MSE evaluation (Stage 2).

Usage:
  cd scripts && python train_dim_sweep.py --d-latent 48 --dataset robomind
  cd scripts && python train_dim_sweep.py --d-latent 12 --dataset berkeley
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
    lejepa_forward,
    safe_collate,
)
from train_lewm_robomind import load_robomind_datasets
from eval_signal_noise_mse import compute_principal_components, project_mse

ROBOMIND_DIR = "/tmp/robomind_lerobot/benchmark1_1_release/ur_1rgb"


def get_num_heads(d_latent: int) -> int:
    if d_latent % 3 == 0:
        return 3
    if d_latent % 2 == 0:
        return 2
    return 1


def load_dataset_and_cfg(cfg, dataset_name: str, num_steps: int | None = None):
    """Load dataset, apply transforms, configure action_encoder input_dim."""
    if num_steps is not None:
        with open_dict(cfg):
            cfg.data.dataset.num_steps = num_steps

    if dataset_name == "berkeley":
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
        ns = num_steps if num_steps is not None else cfg.data.dataset.num_steps
        dataset = load_robomind_datasets(ROBOMIND_DIR, num_steps=ns)

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
    return dataset


def split_dataset(dataset, cfg, dataset_name: str):
    rnd_gen = torch.Generator().manual_seed(cfg.seed)
    if dataset_name == "berkeley":
        train_set, val_set = spt.data.random_split(
            dataset, lengths=[cfg.train_split, 1 - cfg.train_split], generator=rnd_gen
        )
    else:
        n_total = len(dataset)
        n_train = int(n_total * cfg.train_split)
        train_set, val_set = torch.utils.data.random_split(
            dataset, [n_train, n_total - n_train], generator=rnd_gen
        )
    return SafeDataset(train_set), SafeDataset(val_set)


def evaluate_signal_noise(model, val_loader, history_size, max_horizon, device, Vh, k):
    model.eval()
    Vh_dev = Vh.to(device)
    d_latent = Vh.shape[0]

    results_per_h = {
        h: {
            "signal": [],
            "noise": [],
            "full": [],
            "copy_signal": [],
            "copy_noise": [],
            "copy_full": [],
        }
        for h in range(1, max_horizon + 1)
    }
    n_evaluated = 0

    with torch.no_grad():
        for batch in val_loader:
            if batch is None:
                continue
            pixels = batch["pixels"].to(device)
            action = torch.nan_to_num(batch["action"].to(device), 0.0)
            B, T = pixels.shape[:2]
            if T < history_size + max_horizon:
                continue

            enc_dtype = next(model.encoder.parameters()).dtype
            all_emb = model.encoder(
                pixels.reshape(-1, *pixels.shape[2:]).to(enc_dtype),
                interpolate_pos_encoding=True,
            ).last_hidden_state[:, 0]
            all_emb = model.projector(all_emb).reshape(B, T, -1).float()
            all_act_emb = model.action_encoder(action)

            pred_emb_list = list(all_emb[:, :history_size].unbind(dim=1))
            last_ctx_emb = all_emb[:, history_size - 1]

            for step in range(max_horizon):
                t = history_size + step
                lo = max(0, t - history_size)
                ctx_emb = torch.stack(pred_emb_list[lo:], dim=1)
                ctx_act = all_act_emb[:, lo:t]
                next_pred = model.predict(ctx_emb, ctx_act)[:, -1].float()
                pred_emb_list.append(next_pred)

                gt = all_emb[:, t]
                h = step + 1

                sig, noi, full = project_mse(next_pred - gt, Vh_dev, k)
                results_per_h[h]["signal"].extend(sig.cpu().tolist())
                results_per_h[h]["noise"].extend(noi.cpu().tolist())
                results_per_h[h]["full"].extend(full.cpu().tolist())

                csig, cnoi, cfull = project_mse(last_ctx_emb - gt, Vh_dev, k)
                results_per_h[h]["copy_signal"].extend(csig.cpu().tolist())
                results_per_h[h]["copy_noise"].extend(cnoi.cpu().tolist())
                results_per_h[h]["copy_full"].extend(cfull.cpu().tolist())

            n_evaluated += B

    output = {
        "n_sequences": n_evaluated,
        "signal_dims": k,
        "noise_dims": d_latent - k,
        "total_dims": d_latent,
        "horizons": {},
    }
    for h in range(1, max_horizon + 1):
        r = results_per_h[h]
        if not r["signal"]:
            continue
        sig_mean = float(np.mean(r["signal"]))
        noi_mean = float(np.mean(r["noise"]))
        copy_sig = float(np.mean(r["copy_signal"]))
        copy_noi = float(np.mean(r["copy_noise"]))
        output["horizons"][str(h)] = {
            "signal_mse": round(sig_mean, 6),
            "noise_mse": round(noi_mean, 6),
            "full_mse": round(float(np.mean(r["full"])), 6),
            "copy_signal_mse": round(copy_sig, 6),
            "copy_noise_mse": round(copy_noi, 6),
            "copy_full_mse": round(float(np.mean(r["copy_full"])), 6),
            "signal_pred_copy": round(sig_mean / max(copy_sig, 1e-10), 4),
            "noise_pred_copy": round(noi_mean / max(copy_noi, 1e-10), 4),
        }
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--d-latent", type=int, required=True)
    parser.add_argument("--dataset", choices=["berkeley", "robomind"], required=True)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--max-horizon", type=int, default=10)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    d_latent = args.d_latent
    num_heads = get_num_heads(d_latent)
    output_dir = Path(args.output_dir or "notes/LOGS/dim_sweep")
    output_dir = (
        (Path(__file__).resolve().parent.parent / output_dir)
        if not output_dir.is_absolute()
        else output_dir
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.dataset}_d{d_latent:03d}.json"

    print(f"\n{'=' * 60}")
    print(f"  d_latent={d_latent}, heads={num_heads}, head_dim={d_latent // num_heads}")
    print(f"  dataset={args.dataset}, epochs={args.epochs}")
    print(f"{'=' * 60}\n")

    with hydra.initialize(version_base=None, config_path="config"):
        cfg = hydra.compose(config_name="lewm", overrides=["data=ur5"])

    with open_dict(cfg):
        cfg.embed_dim = d_latent
        cfg.model.encoder.hidden_size = d_latent
        cfg.model.encoder.intermediate_size = d_latent * 4
        cfg.model.encoder.num_attention_heads = num_heads
        cfg.trainer.max_epochs = args.epochs
        cfg.loader.batch_size = args.batch_size

    # --- Stage 1: Train ---
    print("Loading training data...")
    dataset = load_dataset_and_cfg(cfg, args.dataset)
    train_set, val_set = split_dataset(dataset, cfg, args.dataset)

    rnd_gen = torch.Generator().manual_seed(cfg.seed)
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

    # --- Stage 2: Signal/noise MSE evaluation ---
    print(f"\n{'=' * 60}")
    print(f"  Stage 2: Signal/Noise MSE (d_latent={d_latent})")
    print(f"{'=' * 60}\n")

    eval_num_steps = cfg.wm.history_size + args.max_horizon
    eval_dataset = load_dataset_and_cfg(cfg, args.dataset, num_steps=eval_num_steps)
    _, eval_val_set = split_dataset(eval_dataset, cfg, args.dataset)

    eval_loader = torch.utils.data.DataLoader(
        eval_val_set,
        batch_size=32,
        num_workers=4,
        shuffle=False,
        drop_last=False,
        collate_fn=safe_collate,
        pin_memory=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    world_model = world_model.to(device).float()
    world_model.eval()

    print("Computing principal components...")
    mean, Vh, S, eff_rank = compute_principal_components(
        world_model, eval_loader, device
    )

    print(f"Evaluating (signal={eff_rank}, noise={d_latent - eff_rank})...")
    stage2 = evaluate_signal_noise(
        world_model,
        eval_loader,
        cfg.wm.history_size,
        args.max_horizon,
        device,
        Vh,
        eff_rank,
    )

    # --- Save combined results ---
    combined = {
        "config": {
            "d_latent": d_latent,
            "dataset": args.dataset,
            "epochs": args.epochs,
            "num_heads": num_heads,
            "head_dim": d_latent // num_heads,
            "n_params": n_params,
        },
        "stage1": stage1,
        "stage2": stage2,
    }
    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)

    # Summary
    if stage1:
        final = stage1[-1]
        eff = final["effective_rank"]
        ratio = final["sigreg_pred_ratio"]
        h1 = stage2["horizons"].get("1", {})
        h10 = stage2["horizons"].get("10", {})
        print(f"\n{'=' * 70}")
        print(f"  RESULT: d={d_latent}, {args.dataset}")
        print(f"{'=' * 70}")
        print(f"  Params: {n_params:,}")
        print(f"  Eff rank: {eff:.1f}/{d_latent} ({eff / d_latent:.0%})")
        print(f"  SIGReg/pred: {ratio:.1f}")
        if h1:
            print(f"  h=1  sig Pred/Copy: {h1.get('signal_pred_copy', 'N/A')}")
        if h10:
            print(f"  h=10 sig Pred/Copy: {h10.get('signal_pred_copy', 'N/A')}")
        print(f"  Saved: {output_path}")


if __name__ == "__main__":
    main()
