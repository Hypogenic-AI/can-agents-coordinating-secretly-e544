#!/bin/bash
# record.sh <JOB_ID>: write dsi-slurm-artifacts/<JOB_ID>/job.json from sacct (after the job ended)
set -euo pipefail
J=$1; D=dsi-slurm-artifacts/$J
S=$(python3 -c "import json;d=json.load(open('$D/submitted.json'));print(d['script']+'|'+d['description']+'|'+d['submitted_at_utc'])")
SCRIPT=${S%%|*}; R=${S#*|}; DESC=${R%%|*}; SUB=${R#*|}
TASKS=$(sacct -j "$J" -X --format=JobID,State,ExitCode -P -n | paste -sd';' -)
LINE=$(sacct -j "$J" -X --format=State,ExitCode -P -n | sort -u | head -n1)
ST=${LINE%%|*}; EC=${LINE#*|}
NST=$(sacct -j "$J" -X --format=State -P -n | sort -u | wc -l)
case "$ST" in COMPLETED) STATUS=completed;; CANCELLED*) STATUS=cancelled;; TIMEOUT*) STATUS=timeout;; PREEMPTED*) STATUS=preempted;; FAILED|NODE_FAIL|OUT_OF_MEMORY) STATUS=failed;; *) STATUS=unknown;; esac
[ "$NST" -gt 1 ] && STATUS=unknown
cat > $D/job.json <<EOT
{
  "job_id": "$J",
  "status": "$STATUS",
  "slurm_state": "$ST",
  "exit_code": "$EC",
  "script": "$SCRIPT",
  "description": "$DESC",
  "tasks": "$TASKS",
  "submitted_at_utc": "$SUB",
  "recorded_at_utc": "$(date -u +%FT%TZ)"
}
EOT
echo "$J $STATUS $ST"
