#!/usr/bin/env bash
set -euo pipefail

python3 -m compileall -q .

tracked_generated="$(
  git ls-files \
    '.DS_Store' \
    '.history' \
    'venv' \
    '*.log' \
    '*.sqlite' \
    '*.sqlite3' \
    '*.db'
)"

if [[ -n "$tracked_generated" ]]; then
  echo "Generated/local files are tracked:" >&2
  echo "$tracked_generated" >&2
  exit 1
fi

echo "Validation passed."
