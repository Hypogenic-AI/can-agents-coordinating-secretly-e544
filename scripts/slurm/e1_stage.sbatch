#!/bin/bash
#SBATCH --job-name=e1_schelling
#SBATCH --partition=general
#SBATCH --account=general_group
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=dsi-slurm-artifacts/%j/slurm_%j.out
#SBATCH --error=dsi-slurm-artifacts/%j/slurm_%j.err
# E1: Schelling coordination on hidden-message schemes (local Qwen3-14B / gemma-4-E4B / Qwen3-1.7B).
# Qwen3-14B in bf16 needs ~30 GB; every GPU type on `general` has >= 40 GB, so no type pin.
# Usage: sbatch ... scripts/slurm/e1_stage.sbatch <stages>
source scripts/slurm/common.sh
"$PY" src/schelling_steg.py --stages "$1" --n_payloads 100 --n_elicit 100
echo "done $(date -u +%FT%TZ)"
