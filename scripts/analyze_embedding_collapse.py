"""Check whether weight=0 model has representation collapse.

Trains LeWM with given SIGReg weight, then analyzes validation embeddings:
- Mean/std of embedding norms
- Per-dimension variance (mean across dims)
- Mean pairwise cosine similarity (collapse → 1.0)
- Mean pairwise L2 distance

Usage:
  cd scripts && python analyze_embedding_collapse.py --sigreg-weight 0
  cd scripts && python analyze_embedding_collapse.py --sigreg-weight 0.09
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
import stable_worldmodel as swm
import torch
from omegaconf import open_dict

from stable_worldmodel.data import column_normalizer as get_column_normalizer
from stable_worldmodel.wm.loss import SIGReg
from train_lewm_diagnostics import (
    LatentDiagnosticsCallback,
    SafeDataset,
    get_img_preprocessor,
    safe_collate,
)
from train_lewm_robomind import load_robomind_datasets
from train_sigreg_ablation import lejepa_forward

ROBOMIND_DIR = "/tmp/robomind_lerobot/benchmark1_1_release/ur_1rgb"


def analyze_embeddings(model, dataloader, device, max_samples=8192):
    model.eval()
    all_emb = []
    n = 0
    with torch.no_grad():
        for batch in dataloader:
            if batch is None:
                continue
            pixels = batch["pixels"].to(device)
            B, T = pixels.shape[:2]
            enc_dtype = next(model.encoder.parameters()).dtype
            emb = model.encoder(
                pixels.reshape(-1, *pixels.shape[2:]).to(enc_dtype),
                interpolate_pos_encoding=True,
            ).last_hidden_state[:, 0]
            emb = model.projector(emb).float().cpu()
            all_emb.append(emb)
            n += emb.shape[0]
            if n >= max_samples:
                break

    all_emb = torch.cat(all_emb, dim=0)[:max_samples]
    N, D = all_emb.shape

    norms = all_emb.norm(dim=1)
    per_dim_var = all_emb.var(dim=0)

    idx = torch.randperm(N)[: min(1000, N)]
    sample = all_emb[idx]
    sample_norm = sample / (sample.norm(dim=1, keepdim=True) + 1e-10)
    cosine_sim = (sample_norm @ sample_norm.T).triu(diagonal=1)
    n_pairs = cosine_sim.nonzero().shape[0]
    mean_cosine = cosine_sim.sum() / max(n_pairs, 1)

    diffs = sample.unsqueeze(0) - sample.unsqueeze(1)
    l2_dists = diffs.norm(dim=2).triu(diagonal=1)
    mean_l2 = l2_dists.sum() / max(n_pairs, 1)

    results = {
        "n_embeddings": N,
        "dim": D,
        "norm_mean": round(norms.mean().item(), 4),
        "norm_std": round(norms.std().item(), 4),
        "norm_min": round(norms.min().item(), 4),
        "norm_max": round(norms.max().item(), 4),
        "per_dim_variance_mean": round(per_dim_var.mean().item(), 6),
        "per_dim_variance_std": round(per_dim_var.std().item(), 6),
        "total_variance": round(per_dim_var.sum().item(), 4),
        "mean_cosine_similarity": round(mean_cosine.item(), 6),
        "mean_pairwise_l2": round(mean_l2.item(), 4),
    }

    print(f"\n  Embedding Analysis ({N} samples, {D} dims):")
    print(
        f"  Norm:     mean={results['norm_mean']:.4f}  std={results['norm_std']:.4f}  "
        f"range=[{results['norm_min']:.4f}, {results['norm_max']:.4f}]"
    )
    print(
        f"  Variance: per-dim mean={results['per_dim_variance_mean']:.6f}  "
        f"total={results['total_variance']:.4f}"
    )
    print(f"  Cosine:   mean={results['mean_cosine_similarity']:.6f}")
    print(f"  L2 dist:  mean={results['mean_pairwise_l2']:.4f}")

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sigreg-weight", type=float, required=True)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()

    weight = args.sigreg_weight
    output_dir = Path(__file__).resolve().parent.parent / "notes/LOGS/sigreg_ablation"
    output_dir.mkdir(parents=True, exist_ok=True)
    weight_str = f"{weight:.4f}".replace(".", "p")
    output_path = output_dir / f"collapse_check_w{weight_str}.json"

    print(f"\n{'=' * 60}")
    print(f"  Collapse Check: SIGReg weight={weight}")
    print(f"{'=' * 60}\n")

    with hydra.initialize(version_base=None, config_path="config"):
        cfg = hydra.compose(config_name="lewm", overrides=["data=ur5"])

    with open_dict(cfg):
        cfg.loss.sigreg.weight = weight
        cfg.trainer.max_epochs = args.epochs
        cfg.loader.batch_size = args.batch_size

    dataset = load_robomind_datasets(ROBOMIND_DIR, num_steps=cfg.data.dataset.num_steps)
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

    n_total = len(dataset)
    n_train = int(n_total * cfg.train_split)
    rnd_gen = torch.Generator().manual_seed(cfg.seed)
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

    diagnostics_cb = LatentDiagnosticsCallback(output_path="/dev/null")
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

    # Analyze embeddings
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    world_model = world_model.to(device).float()
    emb_stats = analyze_embeddings(world_model, val_loader, device)

    final = diagnostics_cb.epoch_results[-1] if diagnostics_cb.epoch_results else {}
    combined = {
        "sigreg_weight": weight,
        "pred_loss": final.get("avg_pred_loss", None),
        "effective_rank": final.get("effective_rank", None),
        "embedding_stats": emb_stats,
    }
    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\n  Saved: {output_path}")


if __name__ == "__main__":
    main()
