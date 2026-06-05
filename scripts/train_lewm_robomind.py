"""LeWM training with latent diagnostics on RoboMIND UR5e data.

Loads multiple per-task LeRobot datasets from local paths, combines them,
and trains LeWM with the same diagnostics as train_lewm_diagnostics.py.

Usage:
  cd scripts && python train_lewm_robomind.py --epochs 5
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
from stable_worldmodel.data.formats.lerobot import LeRobotAdapter
from stable_worldmodel.data import column_normalizer as get_column_normalizer
from stable_worldmodel.wm.loss import SIGReg
from train_lewm_diagnostics import (
    LatentDiagnosticsCallback,
    SafeDataset,
    get_img_preprocessor,
    lejepa_forward,
    safe_collate,
)


class CombinedDataset(torch.utils.data.Dataset):
    """Combine multiple LeRobotAdapter datasets into one."""

    def __init__(self, datasets: list[LeRobotAdapter]):
        self.datasets = datasets
        self._lengths = [len(d) for d in datasets]
        self._cumulative = np.cumsum([0] + self._lengths)
        self._ref = datasets[0]

    def __len__(self):
        return self._cumulative[-1]

    def __getitem__(self, idx):
        for i, (lo, hi) in enumerate(zip(self._cumulative[:-1], self._cumulative[1:])):
            if lo <= idx < hi:
                return self.datasets[i][idx - lo]
        raise IndexError(f"Index {idx} out of range")

    @property
    def column_names(self):
        return self._ref.column_names

    @property
    def transform(self):
        return self._ref.transform

    @transform.setter
    def transform(self, t):
        for d in self.datasets:
            d.transform = t

    def get_dim(self, col: str) -> int:
        return self._ref.get_dim(col)

    def get_col_data(self, col: str) -> np.ndarray:
        return np.concatenate([d.get_col_data(col) for d in self.datasets])


def load_robomind_datasets(
    base_dir: str,
    num_steps: int,
    frameskip: int = 1,
) -> CombinedDataset:
    base = Path(base_dir)
    task_dirs = sorted(d for d in base.iterdir() if d.is_dir())

    datasets = []
    for td in task_dirs:
        ds = LeRobotAdapter(
            repo_id=f"ur_1rgb/{td.name}",
            root=str(td),
            revision="main",
            num_steps=num_steps,
            frameskip=frameskip,
            primary_camera_key="observation.images.camera_top",
            key_aliases={
                "actions.joint_position": "action",
                "observation.states.joint_position": "proprio",
            },
            keys_to_load=["pixels", "action", "proprio"],
            keys_to_cache=["action", "proprio"],
        )
        print(f"  {td.name}: {len(ds)} clips")
        datasets.append(ds)

    combined = CombinedDataset(datasets)
    print(f"  Total: {len(combined)} clips from {len(datasets)} tasks")
    return combined


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default="/tmp/robomind_lerobot/benchmark1_1_release/ur_1rgb",
    )
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).resolve().parent.parent
            / "notes/LOGS/lewm_diagnostics_robomind.json"
        ),
    )
    args = parser.parse_args()

    with hydra.initialize(version_base=None, config_path="config"):
        cfg = hydra.compose(config_name="lewm", overrides=["data=ur5"])

    with open_dict(cfg):
        cfg.trainer.max_epochs = args.epochs
        cfg.loader.batch_size = args.batch_size

    num_steps = cfg.data.dataset.num_steps
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
    train_set, val_set = torch.utils.data.random_split(
        dataset, [n_train, n_val], generator=rnd_gen
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
        enable_checkpointing=True,
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
        print(f"  SUMMARY: RoboMIND UR5e (after {args.epochs} epochs)")
        print(f"{'=' * 60}")
        print(
            f"  Effective rank: {final['effective_rank']:.1f} / {final['latent_dim']}"
        )
        print(f"  Pred loss: {final['avg_pred_loss']:.6f}")
        print(f"  SIGReg loss: {final['avg_sigreg_loss']:.6f}")
        print(f"  SIGReg/pred ratio: {final['sigreg_pred_ratio']:.2f}")


if __name__ == "__main__":
    main()
