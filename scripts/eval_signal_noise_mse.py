"""Evaluate multi-step prediction MSE decomposed into signal vs noise dimensions.

Uses SVD of validation embeddings to identify signal subspace (top-k PCs where
k = effective rank) and noise subspace (remaining dims). Reports per-horizon MSE
for each subspace separately, removing the dilution effect of SIGReg noise.

Usage:
  cd scripts && python eval_signal_noise_mse.py
"""

import argparse
import json
import os
from pathlib import Path

import hydra
import numpy as np
import stable_pretraining as spt
from stable_pretraining import data as dt
import stable_worldmodel as swm
import torch
from omegaconf import OmegaConf, open_dict

from stable_worldmodel.data import column_normalizer as get_column_normalizer


def get_img_preprocessor(source: str, target: str, img_size: int = 224):
    imagenet_stats = dt.dataset_stats.ImageNet
    to_image = dt.transforms.ToImage(**imagenet_stats, source=source, target=target)
    resize = dt.transforms.Resize(img_size, source=source, target=target)
    return dt.transforms.Compose(to_image, resize)


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


def safe_collate(batch):
    batch = [b for b in batch if b is not None]
    if not batch:
        return None
    return torch.utils.data.dataloader.default_collate(batch)


def load_model(checkpoint_path: str, cfg):
    world_model = hydra.utils.instantiate(cfg.model)
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    state_dict = {}
    for k, v in ckpt["state_dict"].items():
        if k.startswith("model."):
            state_dict[k[len("model.") :]] = v
    world_model.load_state_dict(state_dict)
    return world_model


def compute_principal_components(model, dataloader, device, max_samples: int = 8192):
    """Collect encoder embeddings and compute SVD to get principal components."""
    model.eval()
    all_emb = []
    n_collected = 0

    with torch.no_grad():
        for batch in dataloader:
            if batch is None:
                continue
            pixels = batch["pixels"].to(device)
            B, T = pixels.shape[:2]

            emb = model.encoder(
                pixels.reshape(-1, *pixels.shape[2:]).to(
                    next(model.encoder.parameters()).dtype
                ),
                interpolate_pos_encoding=True,
            ).last_hidden_state[:, 0]
            emb = model.projector(emb)
            emb = emb.reshape(B * T, -1).float().cpu()
            all_emb.append(emb)
            n_collected += B * T
            if n_collected >= max_samples:
                break

    all_emb = torch.cat(all_emb, dim=0)[:max_samples]
    mean = all_emb.mean(dim=0)
    centered = all_emb - mean

    U, S, Vh = torch.linalg.svd(centered, full_matrices=False)

    p = S / S.sum()
    entropy = -(p * (p + 1e-10).log()).sum()
    eff_rank = int(torch.exp(entropy).item() + 0.5)

    print(f"  Collected {all_emb.shape[0]} embeddings, dim={all_emb.shape[1]}")
    print(f"  Effective rank: {eff_rank}")
    print(f"  Top-5 singular values: {S[:5].tolist()}")

    return mean, Vh, S, eff_rank


def project_mse(error: torch.Tensor, Vh: torch.Tensor, k: int):
    """Decompose MSE into signal (top-k) and noise (rest) subspaces.

    Args:
        error: (B, D) prediction error vectors
        Vh: (D, D) right singular vectors (rows = PC directions)
        k: number of signal dimensions

    Returns:
        signal_mse: (B,) MSE in top-k PC subspace (per-dim average over k dims)
        noise_mse: (B,) MSE in remaining subspace (per-dim average over D-k dims)
        full_mse: (B,) MSE over all D dims
    """
    D = error.shape[1]
    signal_dirs = Vh[:k]  # (k, D)
    noise_dirs = Vh[k:]  # (D-k, D)

    signal_proj = error @ signal_dirs.T  # (B, k)
    noise_proj = error @ noise_dirs.T  # (B, D-k)

    signal_mse = signal_proj.pow(2).mean(dim=-1)
    noise_mse = noise_proj.pow(2).mean(dim=-1)
    full_mse = error.pow(2).mean(dim=-1)

    return signal_mse, noise_mse, full_mse


def evaluate_signal_noise(
    model,
    dataloader,
    history_size: int,
    max_horizon: int,
    device: torch.device,
    mean: torch.Tensor,
    Vh: torch.Tensor,
    k: int,
):
    model.eval()
    Vh_dev = Vh.to(device)

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
        for batch in dataloader:
            if batch is None:
                continue
            pixels = batch["pixels"].to(device)
            action = torch.nan_to_num(batch["action"].to(device), 0.0)
            B, T = pixels.shape[:2]

            if T < history_size + max_horizon:
                continue

            all_emb = model.encoder(
                pixels.reshape(-1, *pixels.shape[2:]).to(
                    next(model.encoder.parameters()).dtype
                ),
                interpolate_pos_encoding=True,
            ).last_hidden_state[:, 0]
            all_emb = model.projector(all_emb)
            all_emb = all_emb.reshape(B, T, -1).float()

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
                horizon = step + 1

                pred_error = next_pred - gt
                sig, noi, full = project_mse(pred_error, Vh_dev, k)
                results_per_h[horizon]["signal"].extend(sig.cpu().tolist())
                results_per_h[horizon]["noise"].extend(noi.cpu().tolist())
                results_per_h[horizon]["full"].extend(full.cpu().tolist())

                copy_error = last_ctx_emb - gt
                csig, cnoi, cfull = project_mse(copy_error, Vh_dev, k)
                results_per_h[horizon]["copy_signal"].extend(csig.cpu().tolist())
                results_per_h[horizon]["copy_noise"].extend(cnoi.cpu().tolist())
                results_per_h[horizon]["copy_full"].extend(cfull.cpu().tolist())

            n_evaluated += B

    output = {
        "n_sequences": n_evaluated,
        "signal_dims": k,
        "total_dims": Vh.shape[0],
        "horizons": {},
    }
    for h in range(1, max_horizon + 1):
        r = results_per_h[h]
        if not r["signal"]:
            continue
        output["horizons"][str(h)] = {
            "signal_mse_mean": round(float(np.mean(r["signal"])), 6),
            "signal_mse_std": round(float(np.std(r["signal"])), 6),
            "noise_mse_mean": round(float(np.mean(r["noise"])), 6),
            "noise_mse_std": round(float(np.std(r["noise"])), 6),
            "full_mse_mean": round(float(np.mean(r["full"])), 6),
            "copy_signal_mse_mean": round(float(np.mean(r["copy_signal"])), 6),
            "copy_noise_mse_mean": round(float(np.mean(r["copy_noise"])), 6),
            "copy_full_mse_mean": round(float(np.mean(r["copy_full"])), 6),
            "signal_pred_vs_copy": round(
                float(np.mean(r["signal"]))
                / max(float(np.mean(r["copy_signal"])), 1e-10),
                4,
            ),
            "noise_pred_vs_copy": round(
                float(np.mean(r["noise"]))
                / max(float(np.mean(r["copy_noise"])), 1e-10),
                4,
            ),
        }
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint",
        default="/home/developer/.cache/stable-pretraining/runs/20260605/050438/b61f7d1e393c/checkpoints/last.ckpt",
    )
    parser.add_argument("--repo", default="lerobot/berkeley_autolab_ur5")
    parser.add_argument("--camera", default="observation.images.image")
    parser.add_argument("--max-horizon", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).resolve().parent.parent / "notes/LOGS/signal_noise_mse.json"
        ),
    )
    args = parser.parse_args()

    with hydra.initialize(version_base=None, config_path="config"):
        cfg = hydra.compose(config_name="lewm", overrides=["data=ur5"])

    history_size = cfg.wm.history_size
    num_steps = history_size + args.max_horizon

    with open_dict(cfg):
        cfg.data.dataset.name = f"lerobot://{args.repo}"
        cfg.data.dataset.primary_camera_key = args.camera
        cfg.data.dataset.num_steps = num_steps

    dataset_cfg = OmegaConf.to_container(cfg.data.dataset, resolve=True)
    dataset_name = dataset_cfg.pop("name")
    cache_dir = os.environ.get("LOCAL_DATASET_DIR", None)
    print(f'Loading dataset "{dataset_name}" with num_steps={num_steps}')
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
    val_set = SafeDataset(val_set)
    val_loader = torch.utils.data.DataLoader(
        val_set,
        batch_size=args.batch_size,
        num_workers=4,
        shuffle=False,
        drop_last=False,
        collate_fn=safe_collate,
        pin_memory=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading model from {args.checkpoint}")
    model = load_model(args.checkpoint, cfg).to(device)
    model.eval()

    print("Pass 1: Computing principal components from validation embeddings...")
    mean, Vh, S, eff_rank = compute_principal_components(model, val_loader, device)

    print(
        f"\nPass 2: Evaluating signal/noise MSE (signal={eff_rank} dims, noise={192 - eff_rank} dims)..."
    )
    results = evaluate_signal_noise(
        model, val_loader, history_size, args.max_horizon, device, mean, Vh, eff_rank
    )

    print(f"\n{'=' * 80}")
    print(f"  SIGNAL vs NOISE MSE ({results['n_sequences']} sequences)")
    print(
        f"  Signal dims: {results['signal_dims']} | Noise dims: {results['total_dims'] - results['signal_dims']}"
    )
    print(f"{'=' * 80}")
    print(
        f"  {'H':<4} {'Sig MSE':<12} {'Noise MSE':<12} {'Full MSE':<12} "
        f"{'Sig/Copy':<10} {'Noise/Copy':<10} {'Sig/Noise':<10}"
    )
    print(f"  {'-' * 70}")
    for h_str, v in results["horizons"].items():
        sig_noise_ratio = v["signal_mse_mean"] / max(v["noise_mse_mean"], 1e-10)
        print(
            f"  {h_str:<4} {v['signal_mse_mean']:<12.6f} {v['noise_mse_mean']:<12.6f} "
            f"{v['full_mse_mean']:<12.6f} {v['signal_pred_vs_copy']:<10.4f} "
            f"{v['noise_pred_vs_copy']:<10.4f} {sig_noise_ratio:<10.4f}"
        )

    out_path = args.output
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
