#!/usr/bin/env bash
# 推 markdown 文件到 Lark 文档（覆盖远端正文）。
#   push.sh <doc-id-or-url> <file>
#
# 用 lark-cli docs +update --command overwrite。
#
# 强制安全约束（与 rules/skills/lark_write.md 一致）：
#   1. 工作树干净（无未提交改动）
#   2. HEAD 已推到 origin/main（不允许从 feature 分支直接写 Lark）
#
# 失败时退出非 0。绝不提供 --skip 标志。
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

if [[ $# -lt 2 ]]; then
  echo "usage: push.sh <doc-id-or-url> <file>" >&2
  exit 2
fi

DOC="$1"
FILE="$2"

if [[ ! -f "$FILE" ]]; then
  echo "abort: file not found: $FILE" >&2
  exit 1
fi

# 1. 工作树干净
if [[ -n "$(git status --porcelain)" ]]; then
  echo "abort: 工作树有未提交改动。先 commit / stash 再推 Lark。" >&2
  exit 1
fi

# 2. HEAD 已 push 到 origin/main
git fetch --quiet origin main
LOCAL_HEAD=$(git rev-parse HEAD)
ORIGIN_MAIN=$(git rev-parse origin/main)
if ! git merge-base --is-ancestor "$LOCAL_HEAD" "$ORIGIN_MAIN"; then
  AHEAD=$(git rev-list --count "$ORIGIN_MAIN..$LOCAL_HEAD")
  echo "abort: HEAD 比 origin/main 多 $AHEAD 个 commit。先走 workflow_publish 把改动 merge 到 main。" >&2
  exit 1
fi

# 3. push（@file 让 lark-cli 读本地 markdown 文件）
echo "pushing $FILE -> Lark docs $DOC ..."
npx --no-install lark-cli docs +update \
  --doc "$DOC" \
  --command overwrite \
  --content "@$FILE" \
  --doc-format markdown \
  --api-version v2
echo "pushed."
