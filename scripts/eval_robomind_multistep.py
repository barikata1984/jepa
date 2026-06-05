"""Multi-step prediction + signal/noise MSE evaluation on RoboMIND UR5e.

Combines Stage 2 + signal/noise decomposition in one script.

Usage:
  cd scripts && python eval_robomind_multistep.py \
      --checkpoint <path> --data-dir <path>
"""

import argparse
import json
from functools import partial
from pathlib import Path

import hydra
import numpy as np
import stable_pretraining as spt
from stable_pretraining import data as dt
import torch
from omegaconf import OmegaConf, open_dict
from stable_worldmodel.data import column_normalizer as get_column_normalizer

from train_lewm_robomind import CombinedDataset, SafeDataset, load_robomind_datasets
from eval_multistep_prediction import get_img_preprocessor, load_model, safe_collate
from eval_signal_noise_mse import compute_principal_components, project_mse


def evaluate_combined(
    model,
    dataloader,
    history_size: int,
    max_horizon: int,
    device: torch.device,
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
        "dataset": "RoboMIND UR5e (5 tasks)",
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
            "noise_mse_mean": round(float(np.mean(r["noise"])), 6),
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
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument(
        "--data-dir",
        default="/tmp/robomind_lerobot/benchmark1_1_release/ur_1rgb",
    )
    parser.add_argument("--max-horizon", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).resolve().parent.parent
            / "notes/LOGS/robomind_multistep_prediction.json"
        ),
    )
    args = parser.parse_args()

    with hydra.initialize(version_base=None, config_path="config"):
        cfg = hydra.compose(config_name="lewm", overrides=["data=ur5"])

    history_size = cfg.wm.history_size
    num_steps = history_size + args.max_horizon

    print(f"Loading RoboMIND UR5e datasets (num_steps={num_steps})...")
    dataset = load_robomind_datasets(args.data_dir, num_steps=num_steps)

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
    n_val = n_total - n_train
    rnd_gen = torch.Generator().manual_seed(cfg.seed)
    _, val_set = torch.utils.data.random_split(
        dataset, [n_train, n_val], generator=rnd_gen
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

    print("Pass 1: Computing principal components...")
    mean, Vh, S, eff_rank = compute_principal_components(model, val_loader, device)

    print(f"\nPass 2: Evaluating (signal={eff_rank}, noise={192 - eff_rank})...")
    results = evaluate_combined(
        model, val_loader, history_size, args.max_horizon, device, Vh, eff_rank
    )

    print(f"\n{'=' * 80}")
    print(f"  RoboMIND UR5e: SIGNAL vs NOISE MSE ({results['n_sequences']} sequences)")
    print(
        f"  Signal dims: {results['signal_dims']} | Noise dims: {results['total_dims'] - results['signal_dims']}"
    )
    print(f"{'=' * 80}")
    print(
        f"  {'H':<4} {'Sig MSE':<12} {'Noise MSE':<12} {'Full MSE':<12} "
        f"{'Sig/Copy':<10} {'Noise/Copy':<10}"
    )
    print(f"  {'-' * 60}")
    for h_str, v in results["horizons"].items():
        print(
            f"  {h_str:<4} {v['signal_mse_mean']:<12.6f} {v['noise_mse_mean']:<12.6f} "
            f"{v['full_mse_mean']:<12.6f} {v['signal_pred_vs_copy']:<10.4f} "
            f"{v['noise_pred_vs_copy']:<10.4f}"
        )

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
