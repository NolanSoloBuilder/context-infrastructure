#!/bin/sh
set -eu

project_dir="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$project_dir/data"
cd "$project_dir"

if [ -n "${SUPPRESSION_CSV:-}" ]; then
  exec node src/cli.mjs run \
    --input "${TARGETS_CSV:-examples/targets.csv}" \
    --output "${OUTPUT_DIR:-data/daily}" \
    --suppression "$SUPPRESSION_CSV"
fi

exec node src/cli.mjs run \
  --input "${TARGETS_CSV:-examples/targets.csv}" \
  --output "${OUTPUT_DIR:-data/daily}"
