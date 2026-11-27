#!/bin/bash
#SBATCH --job-name=e2_keyless_ke
#SBATCH --partition=general
#SBATCH --account=general_group
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=05:00:00
#SBATCH --array=0-9
#SBATCH --output=dsi-slurm-artifacts/%A/slurm_%A_%a.out
#SBATCH --error=dsi-slurm-artifacts/%A/slurm_%A_%a.err
# E2: toy keyless covert key exchange through Qwen2.5-0.5B sampling. One config per array task.
source scripts/slurm/common.sh
case "$SLURM_ARRAY_TASK_ID" in
  0) ARGS="--conds honest,rank_code,public_plain --sessions 10 --tag main_base" ;;
  1) ARGS="--conds keyless_ke --sessions 5 --s0 0 --Bmax 256 --tag main_ke0" ;;
  2) ARGS="--conds keyless_ke --sessions 5 --s0 5 --Bmax 256 --tag main_ke1" ;;
  3) ARGS="--conds keyless_ke --sessions 10 --pbits 64 --k 1 --tau 0.0 --tag sw_k1_t0" ;;
  4) ARGS="--conds keyless_ke --sessions 10 --pbits 64 --k 1 --tau 1.0 --tag sw_k1_t1" ;;
  5) ARGS="--conds keyless_ke --sessions 10 --pbits 64 --k 2 --tau 1.0 --tag sw_k2_t1" ;;
  6) ARGS="--conds keyless_ke --sessions 10 --pbits 64 --k 4 --tau 0.0 --tag sw_k4_t0" ;;
  7) ARGS="--conds keyless_ke --sessions 10 --pbits 64 --k 4 --tau 1.0 --tag sw_k4_t1" ;;
  8) ARGS="--conds keyless_ke --sessions 10 --pbits 64 --k 8 --tau 1.0 --tag sw_k8_t1" ;;
  9) ARGS="--conds keyless_ke --sessions 1 --pbits 2048 --Bmax 256 --max_msgs 1200 --tag rfc2048" ;;
esac
echo "ARGS=$ARGS"
"$PY" src/keyless_ke.py $ARGS
echo "done $(date -u +%FT%TZ)"
