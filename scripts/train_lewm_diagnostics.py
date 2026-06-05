"""LeWM training with latent space diagnostics (Stage 1a).

Logs per-epoch:
  - Effective rank (RankMe) of encoder embeddings
  - Top singular values of the embedding matrix
  - pred_loss, sigreg_loss, and their ratio

Usage:
  python scripts/train_lewm_diagnostics.py \
      --repo lerobot/berkeley_autolab_ur5 \
      --camera observation.images.image \
      --epochs 5 \
      --output notes/LOGS/lewm_diagnostics.json
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
from stable_worldmodel.wm.utils import save_pretrained


def effective_rank(embeddings: torch.Tensor) -> tuple[float, list[float]]:
    """Compute effective rank and return singular values.

    Args:
        embeddings: (N, D) tensor of embeddings.

    Returns:
        (effective_rank, singular_values_list)
    """
    s = torch.linalg.svdvals(embeddings.float())
    p = s / s.sum()
    p = p + 1e-10
    entropy = -(p * p.log()).sum()
    return torch.exp(entropy).item(), s.tolist()


class LatentDiagnosticsCallback(pl.Callback):
    """Collect encoder embeddings during validation and compute diagnostics."""

    def __init__(self, output_path: str, max_samples: int = 4096):
        super().__init__()
        self.output_path = output_path
        self.max_samples = max_samples
        self._val_embeddings = []
        self._epoch_pred_losses = []
        self._epoch_sigreg_losses = []
        self.epoch_results = []

    def on_validation_batch_end(
        self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx=0
    ):
        if outputs is None:
            return
        emb = outputs.get("emb")
        if emb is None:
            return
        flat = emb.detach().float().reshape(-1, emb.shape[-1])
        self._val_embeddings.append(flat.cpu())

        pred_loss = outputs.get("pred_loss")
        sigreg_loss = outputs.get("sigreg_loss")
        if pred_loss is not None:
            self._epoch_pred_losses.append(pred_loss.detach().item())
        if sigreg_loss is not None:
            self._epoch_sigreg_losses.append(sigreg_loss.detach().item())

    def on_validation_epoch_end(self, trainer, pl_module):
        if not self._val_embeddings:
            return

        all_emb = torch.cat(self._val_embeddings, dim=0)
        if all_emb.shape[0] > self.max_samples:
            perm = torch.randperm(all_emb.shape[0])[: self.max_samples]
            all_emb = all_emb[perm]

        eff_rank, singular_values = effective_rank(all_emb)
        epoch = trainer.current_epoch

        avg_pred_loss = (
            float(np.mean(self._epoch_pred_losses)) if self._epoch_pred_losses else 0.0
        )
        avg_sigreg_loss = (
            float(np.mean(self._epoch_sigreg_losses))
            if self._epoch_sigreg_losses
            else 0.0
        )
        ratio = avg_sigreg_loss / max(avg_pred_loss, 1e-10)

        result = {
            "epoch": epoch,
            "effective_rank": round(eff_rank, 2),
            "latent_dim": all_emb.shape[1],
            "n_embeddings": all_emb.shape[0],
            "top_20_singular_values": [round(v, 4) for v in singular_values[:20]],
            "avg_pred_loss": round(avg_pred_loss, 6),
            "avg_sigreg_loss": round(avg_sigreg_loss, 6),
            "sigreg_pred_ratio": round(ratio, 4),
        }
        self.epoch_results.append(result)

        pl_module.log("diagnostics/effective_rank", eff_rank, on_epoch=True)
        pl_module.log("diagnostics/sigreg_pred_ratio", ratio, on_epoch=True)

        print(
            f"\n[Diagnostics] Epoch {epoch}: effective_rank={eff_rank:.1f}/{all_emb.shape[1]}, "
            f"pred_loss={avg_pred_loss:.6f}, sigreg_loss={avg_sigreg_loss:.6f}, ratio={ratio:.2f}"
        )
        print(f"  Top-5 singular values: {[round(v, 2) for v in singular_values[:5]]}")

        self._val_embeddings.clear()
        self._epoch_pred_losses.clear()
        self._epoch_sigreg_losses.clear()

    def on_fit_end(self, trainer, pl_module):
        if not self.epoch_results:
            return
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(self.epoch_results, f, indent=2)
        print(f"\n[Diagnostics] Results saved to {self.output_path}")


def get_img_preprocessor(source: str, target: str, img_size: int = 224):
    imagenet_stats = dt.dataset_stats.ImageNet
    to_image = dt.transforms.ToImage(**imagenet_stats, source=source, target=target)
    resize = dt.transforms.Resize(img_size, source=source, target=target)
    return dt.transforms.Compose(to_image, resize)


def safe_collate(batch):
    batch = [b for b in batch if b is not None]
    if not batch:
        return None
    return torch.utils.data.dataloader.default_collate(batch)


class SafeDataset(torch.utils.data.Dataset):
    def __init__(self, dataset):
        self.dataset = dataset

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        try:
            return self.dataset[idx]
        except (IndexError, RuntimeError, ValueError):
            return None


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
    output["sigreg_loss"] = self.sigreg(emb.transpose(0, 1))
    output["loss"] = output["pred_loss"] + lambd * output["sigreg_loss"]

    losses_dict = {f"{stage}/{k}": v.detach() for k, v in output.items() if "loss" in k}
    self.log_dict(losses_dict, on_step=True, sync_dist=True)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="lerobot/berkeley_autolab_ur5")
    parser.add_argument("--camera", default="observation.images.image")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--output", default="notes/LOGS/lewm_diagnostics.json")
    args = parser.parse_args()

    with hydra.initialize(
        version_base=None,
        config_path="config",
    ):
        cfg = hydra.compose(config_name="lewm", overrides=[f"data=ur5"])

    with open_dict(cfg):
        cfg.data.dataset.name = f"lerobot://{args.repo}"
        cfg.data.dataset.primary_camera_key = args.camera
        cfg.trainer.max_epochs = args.epochs

    dataset_cfg = OmegaConf.to_container(cfg.data.dataset, resolve=True)
    dataset_name = dataset_cfg.pop("name")
    cache_dir = os.environ.get("LOCAL_DATASET_DIR", None)
    print(f'Loading dataset "{dataset_name}"')
    dataset = swm.data.load_dataset(
        dataset_name, transform=None, cache_dir=cache_dir, **dataset_cfg
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

    rnd_gen = torch.Generator().manual_seed(cfg.seed)
    train_set, val_set = spt.data.random_split(
        dataset,
        lengths=[cfg.train_split, 1 - cfg.train_split],
        generator=rnd_gen,
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

    data_module = spt.data.DataModule(train=train_loader, val=val_loader)
    diagnostics_cb = LatentDiagnosticsCallback(output_path=args.output)

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
    manager = spt.Manager(
        trainer=trainer,
        module=module,
        data=data_module,
    )
    manager()

    if diagnostics_cb.epoch_results:
        final = diagnostics_cb.epoch_results[-1]
        print(f"\n{'=' * 60}")
        print(f"  SUMMARY (after {args.epochs} epochs)")
        print(f"{'=' * 60}")
        print(
            f"  Effective rank: {final['effective_rank']:.1f} / {final['latent_dim']}"
        )
        print(f"  Pred loss: {final['avg_pred_loss']:.6f}")
        print(f"  SIGReg loss: {final['avg_sigreg_loss']:.6f}")
        print(f"  SIGReg/pred ratio: {final['sigreg_pred_ratio']:.2f}")
        rank_ratio = final["effective_rank"] / final["latent_dim"]
        if rank_ratio < 0.3:
            print(
                f"\n  Warning: effective rank ({final['effective_rank']:.0f}) is "
                f"<30% of latent dim ({final['latent_dim']})"
            )
            print(f"  -> SIGReg may be injecting noise into unused dimensions")
        else:
            print(f"\n  Effective rank utilization: {rank_ratio:.0%}")


if __name__ == "__main__":
    main()
