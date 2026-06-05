"""Evaluate LeWM multi-step prediction accuracy (Stage 2).

Loads a trained LeWM checkpoint, runs autoregressive rollout on held-out
episodes, and measures latent-space MSE at horizons 1, 5, 10.
Includes a copy baseline (repeat last context embedding).

Usage:
  python scripts/eval_multistep_prediction.py \
      --checkpoint ~/.cache/stable-pretraining/runs/.../last.ckpt \
      --repo lerobot/berkeley_autolab_ur5 \
      --camera observation.images.image \
      --max-horizon 10 \
      --output notes/LOGS/multistep_prediction.json
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


def evaluate_multistep(
    model,
    dataloader,
    history_size: int,
    max_horizon: int,
    device: torch.device,
):
    model.eval()
    horizon_mses = {h: [] for h in range(1, max_horizon + 1)}
    copy_mses = {h: [] for h in range(1, max_horizon + 1)}
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
                next_pred = model.predict(ctx_emb, ctx_act)[:, -1]
                next_pred = next_pred.float()
                pred_emb_list.append(next_pred)

                gt = all_emb[:, t]
                horizon = step + 1

                mse = (next_pred - gt).pow(2).mean(dim=-1)
                horizon_mses[horizon].extend(mse.cpu().tolist())

                copy_mse = (last_ctx_emb - gt).pow(2).mean(dim=-1)
                copy_mses[horizon].extend(copy_mse.cpu().tolist())

            n_evaluated += B

    results = {
        "n_sequences": n_evaluated,
        "history_size": history_size,
        "horizons": {},
    }

    for h in range(1, max_horizon + 1):
        if horizon_mses[h]:
            pred_mean = float(np.mean(horizon_mses[h]))
            pred_std = float(np.std(horizon_mses[h]))
            copy_mean = float(np.mean(copy_mses[h]))
            copy_std = float(np.std(copy_mses[h]))
            results["horizons"][str(h)] = {
                "pred_mse_mean": round(pred_mean, 6),
                "pred_mse_std": round(pred_std, 6),
                "copy_mse_mean": round(copy_mean, 6),
                "copy_mse_std": round(copy_std, 6),
                "pred_vs_copy": round(pred_mean / max(copy_mean, 1e-10), 4),
            }

    return results


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
    parser.add_argument("--output", default="notes/LOGS/multistep_prediction.json")
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

    print(f"Evaluating multi-step prediction (horizons 1-{args.max_horizon})...")
    results = evaluate_multistep(
        model, val_loader, history_size, args.max_horizon, device
    )

    print(f"\n{'=' * 60}")
    print(f"  MULTI-STEP PREDICTION RESULTS ({results['n_sequences']} sequences)")
    print(f"{'=' * 60}")
    print(f"  {'Horizon':<10} {'Pred MSE':<15} {'Copy MSE':<15} {'Pred/Copy':<10}")
    print(f"  {'-' * 50}")
    for h_str, v in results["horizons"].items():
        h = int(h_str)
        marker = " <--" if h in (1, 5, 10) else ""
        print(
            f"  {h:<10} {v['pred_mse_mean']:<15.6f} {v['copy_mse_mean']:<15.6f} "
            f"{v['pred_vs_copy']:<10.4f}{marker}"
        )

    key_horizons = {1: None, 5: None, 10: None}
    for h in key_horizons:
        if str(h) in results["horizons"]:
            key_horizons[h] = results["horizons"][str(h)]

    print(f"\n  Key horizons:")
    for h, v in key_horizons.items():
        if v:
            if v["pred_vs_copy"] > 1.0:
                verdict = "model WORSE than copy"
            elif v["pred_vs_copy"] > 0.8:
                verdict = "marginal improvement"
            else:
                verdict = "model better"
            print(f"    h={h}: pred/copy={v['pred_vs_copy']:.4f} -> {verdict}")

    out_path = args.output
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
