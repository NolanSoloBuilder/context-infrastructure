#!/usr/bin/env bash
# 拉单 Lark 文档为 markdown。
#   pull.sh <doc-id-or-url>           # 输出到 stdout
#   pull.sh <doc-id-or-url> <outfile> # 写入指定路径
#
# <doc-id-or-url> 可以是 obj_token（25-32 位）或完整 docx URL。
# 用 lark-cli docs +fetch (api v2) + markdown 格式。
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

if [[ $# -lt 1 ]]; then
  echo "usage: pull.sh <doc-id-or-url> [outfile]" >&2
  exit 2
fi

DOC="$1"
OUT="${2:-}"

if [[ -n "$OUT" ]]; then
  npx --no-install lark-cli docs +fetch \
    --doc "$DOC" \
    --doc-format markdown \
    --api-version v2 \
    --jq '.data.document.content' \
    > "$OUT"
  echo "wrote: $OUT"
else
  npx --no-install lark-cli docs +fetch \
    --doc "$DOC" \
    --doc-format markdown \
    --api-version v2 \
    --jq '.data.document.content'
fi
