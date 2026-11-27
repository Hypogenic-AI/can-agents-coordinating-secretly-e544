#!/bin/bash
#SBATCH --job-name=analyze
#SBATCH --partition=general
#SBATCH --account=general_group
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=dsi-slurm-artifacts/%j/slurm_%j.out
#SBATCH --error=dsi-slurm-artifacts/%j/slurm_%j.err
# Analysis (E2 analysis needs the LM for the active-warden and re-tokenization checks).
# Usage: sbatch ... scripts/slurm/analyze.sbatch <script.py>
source scripts/slurm/common.sh
"$PY" "$1"
echo "done $(date -u +%FT%TZ)"
