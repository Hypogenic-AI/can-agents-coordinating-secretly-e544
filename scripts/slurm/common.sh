# sourced by every job: environment + GPU log
set -euo pipefail
export HF_HOME=/net/spaces/scratch/chenhao/hf_cache
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
PY="$PWD/.venv/bin/python"
[ -x "$PY" ] || { echo "venv python missing"; exit 127; }
echo "host=$(hostname) job=${SLURM_JOB_ID:-} task=${SLURM_ARRAY_TASK_ID:-} start=$(date -u +%FT%TZ)"
nvidia-smi --query-gpu=name,memory.total --format=csv || true
