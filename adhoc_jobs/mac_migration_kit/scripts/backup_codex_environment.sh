#!/usr/bin/env bash
set -Eeuo pipefail

STAMP="$(date +%Y%m%dT%H%M%S)"
DEST_DIR="${DEST_DIR:-${HOME}/Documents/CodexMigration}"
ARCHIVE="${DEST_DIR}/codex-environment-${STAMP}.tar.gz"
STAGING_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-migration.XXXXXX")"
KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_MANIFEST="${SKILL_MANIFEST:-${KIT_DIR}/manifests/codex-skills-migrate.txt}"

cleanup() {
  rm -rf "${STAGING_DIR}"
}
trap cleanup EXIT

log() {
  printf '[codex-backup] %s\n' "$*"
}

copy_if_exists() {
  local relative_path="$1"
  local source_path="${HOME}/${relative_path}"
  local target_path="${STAGING_DIR}/home/${relative_path}"

  if [ ! -e "${source_path}" ] && [ ! -L "${source_path}" ]; then
    return
  fi

  mkdir -p "$(dirname "${target_path}")"
  cp -a "${source_path}" "${target_path}"
}

sync_if_exists() {
  local relative_path="$1"
  local source_path="${HOME}/${relative_path}"
  local target_path="${STAGING_DIR}/home/${relative_path}"

  if [ ! -e "${source_path}" ] && [ ! -L "${source_path}" ]; then
    return
  fi

  mkdir -p "$(dirname "${target_path}")"
  rsync -a \
    --exclude='.DS_Store' \
    --exclude='__pycache__/' \
    --exclude='node_modules/' \
    --exclude='agents-sdk/' \
    --exclude='agents-sdk' \
    --exclude='cloudflare/' \
    --exclude='cloudflare' \
    --exclude='cloudflare-deploy/' \
    --exclude='cloudflare-deploy' \
    --exclude='durable-objects/' \
    --exclude='durable-objects' \
    --exclude='figma/' \
    --exclude='figma' \
    --exclude='figma-code-connect-components/' \
    --exclude='figma-code-connect-components' \
    --exclude='figma-create-design-system-rules/' \
    --exclude='figma-create-design-system-rules' \
    --exclude='figma-implement-design/' \
    --exclude='figma-implement-design' \
    --exclude='gh-fix-ci/' \
    --exclude='gh-fix-ci' \
    --exclude='pdf/' \
    --exclude='pdf' \
    --exclude='remotion-best-practices/' \
    --exclude='remotion-best-practices' \
    --exclude='sandbox-sdk/' \
    --exclude='sandbox-sdk' \
    --exclude='sentry/' \
    --exclude='sentry' \
    --exclude='web-perf/' \
    --exclude='web-perf' \
    --exclude='workers-best-practices/' \
    --exclude='workers-best-practices' \
    --exclude='wrangler/' \
    --exclude='wrangler' \
    --exclude='lark-*/' \
    --exclude='lark-*' \
    --exclude='claude-code-handoff-plugin-installer/' \
    --exclude='claude-code-handoff-plugin-installer' \
    --exclude='codewiz-handoff/' \
    --exclude='codewiz-handoff' \
    --exclude='codewiz-handoff-plugin-installer/' \
    --exclude='codewiz-handoff-plugin-installer' \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='*.sqlite-wal' \
    --exclude='*.sqlite-shm' \
    "${source_path}" "${target_path%/*}/"
}

copy_filtered_skills() {
  local section=""
  local name=""
  local target=""
  local codex_count=0
  local agents_count=0
  local symlink_count=0

  if [ ! -f "${SKILL_MANIFEST}" ]; then
    printf 'Skill manifest not found: %s\n' "${SKILL_MANIFEST}" >&2
    exit 1
  fi

  mkdir -p \
    "${STAGING_DIR}/home/.codex/skills" \
    "${STAGING_DIR}/home/.agents/skills" \
    "${STAGING_DIR}/MANIFESTS"
  cp -a "${SKILL_MANIFEST}" "${STAGING_DIR}/MANIFESTS/codex-skills-migrate.txt"

  while IFS= read -r line || [ -n "${line}" ]; do
    case "${line}" in
      "[codex]") section="codex"; continue ;;
      "[agents]") section="agents"; continue ;;
      "[symlinks]") section="symlinks"; continue ;;
      "["*) section=""; continue ;;
      ""|"#"*) continue ;;
    esac

    case "${section}" in
      codex)
        name="${line}"
        target="${HOME}/.codex/skills/${name}"
        if [ -d "${target}" ] && [ -f "${target}/SKILL.md" ]; then
          sync_if_exists ".codex/skills/${name}"
          codex_count=$((codex_count + 1))
        else
          printf 'Invalid Codex skill in manifest: %s\n' "${name}" >&2
          exit 1
        fi
        ;;
      agents)
        name="${line}"
        target="${HOME}/.agents/skills/${name}"
        if [ -d "${target}" ] && [ -f "${target}/SKILL.md" ]; then
          sync_if_exists ".agents/skills/${name}"
          agents_count=$((agents_count + 1))
        else
          printf 'Invalid Agent skill in manifest: %s\n' "${name}" >&2
          exit 1
        fi
        ;;
      symlinks)
        name="${line%%[[:space:]]*}"
        target="${line#${name}}"
        target="${target#"${target%%[![:space:]]*}"}"
        if [ -z "${name}" ] || [ -z "${target}" ] || [ "${target}" = "${line}" ]; then
          printf 'Invalid symlink entry in manifest: %s\n' "${line}" >&2
          exit 1
        fi
        ln -sfn "${target}" "${STAGING_DIR}/home/.codex/skills/${name}"
        symlink_count=$((symlink_count + 1))
        ;;
    esac
  done <"${SKILL_MANIFEST}"

  cat >"${STAGING_DIR}/SKILL_COUNTS.txt" <<EOF
codex_skills=${codex_count}
agent_skills=${agents_count}
skill_symlinks=${symlink_count}
EOF
}

mkdir -p "${DEST_DIR}" "${STAGING_DIR}/home"
chmod 700 "${DEST_DIR}"

log "collecting portable Codex configuration"
for relative_path in \
  .codex/config.toml \
  .codex/AGENTS.md \
  .codex/hooks.json \
  .codex/rules \
  .codex/superpowers \
  .codex/memories \
  .codex/memories_1.sqlite \
  .codex/sqlite/memories_1.sqlite \
  .codex/automations \
  .codex/claude-companion \
  .codex/codewiz-companion \
  .codex/browser/config.toml \
  .codex/computer-use/config.json; do
  sync_if_exists "${relative_path}"
done

log "collecting filtered Codex and Agent skills from ${SKILL_MANIFEST}"
copy_filtered_skills

if [ "${INCLUDE_HISTORY:-0}" = "1" ]; then
  log "including local session history because INCLUDE_HISTORY=1"
  for relative_path in \
    .codex/history.jsonl \
    .codex/session_index.jsonl \
    .codex/sessions \
    .codex/archived_sessions; do
    copy_if_exists "${relative_path}"
  done
fi

cat >"${STAGING_DIR}/BACKUP_METADATA.txt" <<EOF
created_at=${STAMP}
source_home=${HOME}
source_arch=$(uname -m)
include_history=${INCLUDE_HISTORY:-0}
skill_manifest=${SKILL_MANIFEST}
EOF

cat >"${STAGING_DIR}/README.txt" <<'EOF'
This archive may contain private rules, memories, MCP configuration, and API
configuration. It intentionally excludes Codex auth files, app state, plugin
caches, attachments, generated media, logs, shell snapshots, and live SQLite
WAL/SHM files. Codex and Agent skills are filtered by MANIFESTS/codex-skills-migrate.txt
instead of copied wholesale. Keep it in encrypted storage and never commit it to Git.
EOF

log "creating archive"
tar -C "${STAGING_DIR}" -czf "${ARCHIVE}" BACKUP_METADATA.txt README.txt SKILL_COUNTS.txt MANIFESTS home
chmod 600 "${ARCHIVE}"
shasum -a 256 "${ARCHIVE}" >"${ARCHIVE}.sha256"
chmod 600 "${ARCHIVE}.sha256"

log "archive: ${ARCHIVE}"
log "checksum: ${ARCHIVE}.sha256"
