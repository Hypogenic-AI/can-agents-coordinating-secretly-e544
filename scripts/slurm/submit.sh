#!/bin/bash
# submit.sh <script> <description> [extra sbatch args...] [-- script args]; prints JOB_ID, creates bundle dir.
set -euo pipefail
SCRIPT=$1; DESC=$2; shift 2
JOB_ID=$(sbatch --parsable --hold --chdir="$PWD" "$@" | tail -n 1); JOB_ID="${JOB_ID%%;*}"
mkdir -p "dsi-slurm-artifacts/$JOB_ID"
printf '{"job_id":"%s","script":"%s","description":"%s","submitted_at_utc":"%s"}\n' "$JOB_ID" "$SCRIPT" "$DESC" "$(date -u +%FT%TZ)" > "dsi-slurm-artifacts/$JOB_ID/submitted.json"
scontrol release "$JOB_ID"
echo "$JOB_ID"
