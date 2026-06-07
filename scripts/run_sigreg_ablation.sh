#!/bin/bash
# SIGReg weight ablation on RoboMIND UR5e (d=192 fixed)
set -e

WEIGHTS="0 0.009 0.03 0.09 0.9"

echo "=========================================="
echo "  SIGReg Weight Ablation"
echo "  Weights: $WEIGHTS"
echo "  Dataset: robomind, d_latent=192"
echo "=========================================="

cd /workspace/scripts

for w in $WEIGHTS; do
    echo ""
    echo "[$(date '+%H:%M:%S')] >>> weight=$w"
    python train_sigreg_ablation.py --sigreg-weight "$w" --dataset robomind --epochs 5
    echo "[$(date '+%H:%M:%S')] <<< weight=$w done"
done

echo ""
echo "=========================================="
echo "  All conditions complete"
echo "  Results: notes/LOGS/sigreg_ablation/"
echo "=========================================="
