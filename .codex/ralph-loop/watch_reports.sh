#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || cd "$SCRIPT_DIR/../.." && pwd)"
FEEDBACK="$ROOT/.codex/ralph-loop/feedback.md"

REPORTS=(
  "benchmarks/results/longmemeval-oracle-20260321b/full.report.json"
  "benchmarks/results/longmemeval-s-20260321b/full.report.json"
  "benchmarks/results/longmemeval-m-20260321b/full.report.json"
)

cd "$ROOT"

{
  echo "# Ralph Watch"
  echo
  echo "Status: IN_PROGRESS"
  echo
  echo "Watching for expected report files:"
  for report in "${REPORTS[@]}"; do
    echo "- $report"
  done
  echo
  echo "Started: $(date -Is)"
} > "$FEEDBACK"

for _ in $(seq 1 120); do
  {
    echo
    echo "## Check $(date -Is)"
  } >> "$FEEDBACK"

  all_found=1
  for report in "${REPORTS[@]}"; do
    if [ -f "$report" ]; then
      echo "- FOUND $report" >> "$FEEDBACK"
    else
      echo "- MISSING $report" >> "$FEEDBACK"
      all_found=0
    fi
  done

  if [ "$all_found" -eq 1 ]; then
    {
      echo
      echo "Status: COMPLETE"
      echo "Completed: $(date -Is)"
    } >> "$FEEDBACK"
    exit 0
  fi

  sleep 60
done

{
  echo
  echo "Status: BLOCKED"
  echo "Reason: No expected report files appeared during the watch window."
  echo "Completed: $(date -Is)"
} >> "$FEEDBACK"
