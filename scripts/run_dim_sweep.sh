#!/bin/bash
# Latent dimension sweep: train + evaluate LeWM with varying ViT hidden_size.
# RoboMIND first (primary, faster), then berkeley (secondary).
set -e

DIMS="12 24 48 96 192"

echo "=========================================="
echo "  Latent Dimension Sweep"
echo "  Conditions: d_latent ∈ {$DIMS}"
echo "  Datasets: robomind (primary), berkeley"
echo "=========================================="

cd /workspace/scripts

for d in $DIMS; do
    echo ""
    echo "[$(date '+%H:%M:%S')] >>> RoboMIND d_latent=$d"
    python train_dim_sweep.py --d-latent "$d" --dataset robomind --epochs 5
    echo "[$(date '+%H:%M:%S')] <<< RoboMIND d_latent=$d done"
done

for d in $DIMS; do
    echo ""
    echo "[$(date '+%H:%M:%S')] >>> berkeley d_latent=$d"
    python train_dim_sweep.py --d-latent "$d" --dataset berkeley --epochs 5
    echo "[$(date '+%H:%M:%S')] <<< berkeley d_latent=$d done"
done

echo ""
echo "=========================================="
echo "  All conditions complete"
echo "  Results: notes/LOGS/dim_sweep/"
echo "=========================================="
