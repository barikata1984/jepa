"""Estimate the intrinsic dimensionality of image observations in a LeRobot dataset.

Methods:
  1. Two-NN (Facco et al., 2017) — local estimator based on nearest-neighbor distance ratios.
  2. PCA cumulative explained variance — number of components for 90%/95%/99% variance.

Usage:
  python scripts/estimate_intrinsic_dim.py \
      --repo lerobot/berkeley_autolab_ur5 \
      --camera observation.images.image \
      --n-samples 2000 \
      --seed 42
"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA


def two_nn_id(X: np.ndarray) -> float:
    """Two-NN intrinsic dimension estimator (Facco et al., 2017).

    For each point, compute mu = r2/r1 where r1, r2 are distances to the
    1st and 2nd nearest neighbors. The MLE of the intrinsic dimension is:
        d = n / sum(log(mu_i))
    """
    nn = NearestNeighbors(n_neighbors=3, algorithm="auto").fit(X)
    distances, _ = nn.kneighbors(X)
    r1 = distances[:, 1]
    r2 = distances[:, 2]
    valid = r1 > 0
    mu = r2[valid] / r1[valid]
    mu = mu[mu > 1.0]
    n = len(mu)
    d = n / np.sum(np.log(mu))
    return d


def pca_analysis(X: np.ndarray, thresholds: list[float] = [0.90, 0.95, 0.99]):
    n_components = min(X.shape[0], X.shape[1], 512)
    pca = PCA(n_components=n_components, random_state=42)
    pca.fit(X)
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    results = {}
    for t in thresholds:
        k = int(np.searchsorted(cumvar, t) + 1)
        results[f"pca_{int(t * 100)}pct"] = k
    results["top_10_singular_values"] = pca.singular_values_[:10].tolist()
    results["cumvar_at_32"] = float(cumvar[min(31, len(cumvar) - 1)])
    results["cumvar_at_64"] = float(cumvar[min(63, len(cumvar) - 1)])
    results["cumvar_at_128"] = float(cumvar[min(127, len(cumvar) - 1)])
    results["cumvar_at_192"] = float(cumvar[min(191, len(cumvar) - 1)])
    return results


def load_images(repo: str, camera: str, n_samples: int, seed: int) -> torch.Tensor:
    from stable_worldmodel.data import load_dataset

    ds = load_dataset(
        f"lerobot://{repo}",
        num_steps=1,
        primary_camera_key=camera,
    )
    n = len(ds)
    rng = np.random.default_rng(seed)
    indices = rng.choice(n, size=min(n_samples, n), replace=False)
    indices.sort()

    images = []
    skipped = 0
    for idx in indices:
        try:
            sample = ds[int(idx)]
            img = sample["pixels"].squeeze(0)  # (3, H, W)
            images.append(img)
        except (IndexError, RuntimeError, ValueError):
            skipped += 1
            continue

    print(f"Loaded {len(images)} images, skipped {skipped}")
    return torch.stack(images)  # (N, 3, H, W)


def pixels_to_flat(pixels: torch.Tensor) -> np.ndarray:
    downsampled = torch.nn.functional.interpolate(
        pixels, size=(64, 64), mode="bilinear"
    )
    return downsampled.reshape(downsampled.shape[0], -1).numpy()


def encode_with_vit(pixels: torch.Tensor, batch_size: int = 64) -> np.ndarray:
    from stable_pretraining.backbone.utils import vit_hf

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    encoder = vit_hf(size="tiny", patch_size=14, image_size=224, pretrained=False)
    encoder = encoder.to(device).eval()

    resized = torch.nn.functional.interpolate(pixels, size=(224, 224), mode="bilinear")
    # ImageNet normalization
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
    resized = (resized - mean) / std

    features = []
    with torch.no_grad():
        for i in range(0, len(resized), batch_size):
            batch = resized[i : i + batch_size].to(device)
            out = encoder(batch)
            feat = out.last_hidden_state[:, 0]  # CLS token (B, D)
            features.append(feat.cpu())
    return torch.cat(features, dim=0).numpy()


def run_analysis(X: np.ndarray, space_name: str) -> dict:
    print(f"\n{'=' * 60}")
    print(f"  {space_name}: {X.shape}")
    print(f"{'=' * 60}")

    print("\n--- Two-NN estimator ---")
    d_two_nn = two_nn_id(X)
    print(f"  Intrinsic dimension: {d_two_nn:.1f}")

    print("\n--- PCA analysis ---")
    pca_results = pca_analysis(X)
    for k, v in pca_results.items():
        if isinstance(v, list):
            print(f"  {k}: [{', '.join(f'{x:.1f}' for x in v)}]")
        elif isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")

    return {"two_nn_id": round(d_two_nn, 2), **pca_results}


def main():
    parser = argparse.ArgumentParser(description="Estimate intrinsic dimensionality")
    parser.add_argument("--repo", default="lerobot/berkeley_autolab_ur5")
    parser.add_argument("--camera", default="observation.images.image")
    parser.add_argument("--n-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    print(f"Dataset: {args.repo}")
    print(f"Camera: {args.camera}")
    print(f"Sampling {args.n_samples} images...")

    pixels = load_images(args.repo, args.camera, args.n_samples, args.seed)

    # Pixel space (64x64)
    X_pixel = pixels_to_flat(pixels)
    pixel_results = run_analysis(X_pixel, "Pixel space (64x64)")

    # ViT feature space (192-dim, untrained)
    X_vit = encode_with_vit(pixels)
    vit_results = run_analysis(X_vit, f"ViT-tiny feature space ({X_vit.shape[1]}-dim)")

    results = {
        "dataset": args.repo,
        "camera": args.camera,
        "n_samples": int(pixels.shape[0]),
        "pixel_space": {
            "dim": X_pixel.shape[1],
            "image_size": "64x64",
            **pixel_results,
        },
        "vit_space": {"dim": X_vit.shape[1], **vit_results},
    }

    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    print(f"  LeWM latent dim: 192")
    print(f"  Pixel two-NN: {pixel_results['two_nn_id']}")
    print(f"  ViT   two-NN: {vit_results['two_nn_id']}")
    print(f"  Pixel PCA 95%: {pixel_results['pca_95pct']} components")
    print(f"  ViT   PCA 95%: {vit_results['pca_95pct']} components")

    d = max(pixel_results["two_nn_id"], vit_results["two_nn_id"])
    if d < 50:
        print(f"\n  ⚠ 固有次元 (~{d:.0f}) << 192: SIGReg ミスマッチのリスクあり")
    else:
        print(f"\n  固有次元 (~{d:.0f}) は 192 に対して深刻な乖離なし")

    out_path = (
        args.output or f"notes/LOGS/intrinsic_dim_{args.repo.replace('/', '_')}.json"
    )
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
