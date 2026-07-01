#!/usr/bin/env bash
# 拉 Lark 群历史消息为本地 markdown 镜像。
#
# 用法:
#   chat_pull.sh <chat-alias-or-oc-id> [--days N] [--out PATH]
#   chat_pull.sh <chat-alias-or-oc-id> --since YYYY-MM-DD [--until YYYY-MM-DD] [--out PATH]
#
# 示例:
#   ./tools/lark_cli/chat_pull.sh rimbo_core --days 14
#   ./tools/lark_cli/chat_pull.sh oc_xxx --since 2026-05-01 --until 2026-05-18
#
# 别名解析自 contexts/team_config.yml 的 lark.chats。
# 默认输出 contexts/lark_mirror/chats/<alias>/<since>_<until>.md。
#
# 依赖: lark-cli (OAuth)、jq。不需要 LARK_APP_ID/SECRET。
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

usage() {
  sed -n '2,18p' "$0" >&2
  exit 2
}

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

ALIAS_OR_ID="$1"; shift
DAYS=""
SINCE=""
UNTIL=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --days) DAYS="$2"; shift 2 ;;
    --since) SINCE="$2"; shift 2 ;;
    --until) UNTIL="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; usage ;;
  esac
done

# ---------- 解析 chat_id ----------
if [[ "$ALIAS_OR_ID" == oc_* ]]; then
  CHAT_ID="$ALIAS_OR_ID"
  ALIAS_FOR_PATH="$ALIAS_OR_ID"
else
  CFG="contexts/team_config.yml"
  if [[ ! -f "$CFG" ]]; then
    echo "abort: $CFG 不存在,无法解析别名 $ALIAS_OR_ID。请用 oc_xxx 直接传 chat_id。" >&2
    exit 1
  fi
  # 在 lark.chats: 块下找 "  <alias>: oc_xxx"
  CHAT_ID=$(awk -v alias="$ALIAS_OR_ID" '
    /^  chats:/ { in_chats=1; next }
    in_chats && /^  [^ ]/ { in_chats=0 }
    in_chats && $1 == alias":" { print $2; exit }
  ' "$CFG")
  if [[ -z "$CHAT_ID" ]]; then
    echo "abort: 别名 $ALIAS_OR_ID 在 $CFG 的 lark.chats 里找不到。" >&2
    exit 1
  fi
  ALIAS_FOR_PATH="$ALIAS_OR_ID"
fi

# ---------- 时间窗 ----------
if [[ -n "$SINCE" || -n "$UNTIL" ]]; then
  # 显式时间窗
  : "${UNTIL:=$(date -u '+%Y-%m-%d')}"
  : "${SINCE:=$(date -u -v-7d '+%Y-%m-%d')}"
  START_ISO="${SINCE}T00:00:00Z"
  END_ISO="${UNTIL}T23:59:59Z"
else
  : "${DAYS:=7}"
  START_ISO=$(date -u -v-"${DAYS}"d '+%Y-%m-%dT%H:%M:%SZ')
  END_ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
  SINCE=$(echo "$START_ISO" | cut -dT -f1)
  UNTIL=$(echo "$END_ISO" | cut -dT -f1)
fi

# ---------- 默认输出路径 ----------
if [[ -z "$OUT" ]]; then
  OUT="contexts/lark_mirror/chats/${ALIAS_FOR_PATH}/${SINCE}_${UNTIL}.md"
fi
mkdir -p "$(dirname "$OUT")"

echo "chat=${ALIAS_FOR_PATH} chat_id=${CHAT_ID}" >&2
echo "window: ${START_ISO} → ${END_ISO}" >&2
echo "out: ${OUT}" >&2

# ---------- 拉数据(手动分页,子命令不接 --page-all) ----------
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

PAGE=0
PAGE_TOKEN=""
while :; do
  PAGE=$((PAGE + 1))
  PAGE_FILE="${TMP_DIR}/page_${PAGE}.json"
  if [[ -z "$PAGE_TOKEN" ]]; then
    npx --no-install lark-cli im +chat-messages-list \
      --chat-id "$CHAT_ID" \
      --start "$START_ISO" \
      --end "$END_ISO" \
      --sort asc \
      --page-size 50 \
      --format json > "$PAGE_FILE"
  else
    npx --no-install lark-cli im +chat-messages-list \
      --chat-id "$CHAT_ID" \
      --start "$START_ISO" \
      --end "$END_ISO" \
      --sort asc \
      --page-size 50 \
      --page-token "$PAGE_TOKEN" \
      --format json > "$PAGE_FILE"
  fi
  HAS_MORE=$(jq -r '.data.has_more // false' "$PAGE_FILE")
  PAGE_TOKEN=$(jq -r '.data.page_token // ""' "$PAGE_FILE")
  if [[ "$HAS_MORE" != "true" || -z "$PAGE_TOKEN" ]]; then
    break
  fi
done

# 合并所有 page 的 messages 数组
jq -s '[.[] | .data.messages // [] | .[]]' "${TMP_DIR}"/page_*.json > "${TMP_DIR}/all.json"
COUNT=$(jq 'length' "${TMP_DIR}/all.json")
echo "fetched ${COUNT} messages across ${PAGE} page(s)" >&2

# ---------- 渲染 markdown ----------
SYNCED_AT=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

{
  echo "<!-- lark-mirror chat_id=${CHAT_ID} alias=${ALIAS_FOR_PATH} since=${START_ISO} until=${END_ISO} synced=${SYNCED_AT} count=${COUNT} -->"
  echo
  echo "# Lark 群聊镜像 — ${ALIAS_FOR_PATH}"
  echo
  echo "窗口: ${START_ISO} → ${END_ISO}  "
  echo "消息数: ${COUNT}"
  echo
  echo "---"
  echo

  if [[ "$COUNT" -eq 0 ]]; then
    echo "_(窗口内无消息)_"
  else
    # 按日期分组 → 渲染
    jq -r '
      group_by(.create_time[0:10])[]
      | "## " + .[0].create_time[0:10] + "\n",
        ( .[] |
          "- **\(.create_time[11:16]) \(.sender.name // .sender.id // "unknown")**: " +
          (
            if .msg_type == "text" then
              (.content // "" | gsub("\n"; "\n  "))
            elif .msg_type == "post" then
              "[post] " + (.content // "" | gsub("\n"; "\n  "))
            else
              "[" + .msg_type + "]"
            end
          )
        ),
        ""
    ' "${TMP_DIR}/all.json"
  fi
} > "$OUT"

echo "wrote ${COUNT} messages → ${OUT}"
