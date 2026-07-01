#!/usr/bin/env bash
# 向 Lark IM 发送文字消息（默认带 AI 标签）。
#   im_send.sh [--no-tag] <chat-id-or-user-id> <text>
#
# <chat-id> 形如 oc_xxxxxx（群）；<user-id> 形如 ou_xxxxxx（直接消息）。
# 多行 text 用引号包裹。
#
# 默认行为：消息会被自动包装成
#   [AI] <text>
#   — <handle> / via lark-cli
# 这样群内能区分 AI 自动通知 vs 真人手发。<handle> 从仓库根 .me 读取。
# 极少数场景（caller 自己手写、不希望被打 AI 标签）传 --no-tag 跳过包装。
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

NO_TAG=0
if [[ "${1:-}" == "--no-tag" ]]; then
  NO_TAG=1
  shift
fi

if [[ $# -lt 2 ]]; then
  echo "usage: im_send.sh [--no-tag] <chat-id-or-user-id> <text>" >&2
  exit 2
fi

ID="$1"
TEXT="$2"

# 区分 oc_ (chat) vs ou_ (user)
case "$ID" in
  oc_*) ID_FLAG=(--chat-id "$ID") ;;
  ou_*) ID_FLAG=(--user-id "$ID") ;;
  *)
    echo "abort: id 必须以 oc_（群）或 ou_（用户）开头：$ID" >&2
    exit 1
    ;;
esac

if [[ "$NO_TAG" -eq 0 ]]; then
  HANDLE=""
  if [[ -f .me ]]; then
    HANDLE=$(grep -E '^handle:' .me | head -1 | sed 's/^handle:[[:space:]]*//' | tr -d '"' | tr -d "'")
  fi
  [[ -z "$HANDLE" ]] && HANDLE="${USER:-unknown}"
  TEXT="[AI] ${TEXT}
— ${HANDLE} / via lark-cli"
fi

exec npx --no-install lark-cli im +messages-send \
  "${ID_FLAG[@]}" \
  --text "$TEXT"
