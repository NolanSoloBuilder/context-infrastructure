#!/usr/bin/env bash
set -Eeuo pipefail

ARCHIVE="${1:-}"
DRY_RUN="${DRY_RUN:-1}"
STAGING_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-restore.XXXXXX")"

cleanup() {
  rm -rf "${STAGING_DIR}"
}
trap cleanup EXIT

log() {
  printf '[codex-restore] %s\n' "$*"
}

if [ -z "${ARCHIVE}" ] || [ ! -f "${ARCHIVE}" ]; then
  printf 'Usage: %s /path/to/codex-environment-YYYYMMDDTHHMMSS.tar.gz\n' "$0" >&2
  exit 2
fi

if [ -f "${ARCHIVE}.sha256" ]; then
  log "verifying checksum"
  (cd "$(dirname "${ARCHIVE}")" && shasum -a 256 -c "$(basename "${ARCHIVE}.sha256")")
fi

if tar -tzf "${ARCHIVE}" | grep -Eq '(^/|(^|/)\.\.(/|$))'; then
  printf 'Archive contains an unsafe path; refusing to extract.\n' >&2
  exit 1
fi

tar -C "${STAGING_DIR}" -xzf "${ARCHIVE}"
if [ ! -d "${STAGING_DIR}/home" ]; then
  printf 'Archive does not contain the expected home payload.\n' >&2
  exit 1
fi

SOURCE_HOME="$(awk -F= '$1 == "source_home" {sub(/^source_home=/, ""); print; exit}' "${STAGING_DIR}/BACKUP_METADATA.txt" 2>/dev/null || true)"
if [ -n "${SOURCE_HOME}" ] && [ "${SOURCE_HOME}" != "${HOME}" ]; then
  log "warning: source home was ${SOURCE_HOME}; review absolute paths in config.toml after restore"
fi

log "payload preview"
find "${STAGING_DIR}/home" -maxdepth 3 -mindepth 1 -print | sed "s#^${STAGING_DIR}/home#~#" | sort

if [ "${DRY_RUN}" != "0" ]; then
  log "dry-run only; rerun with DRY_RUN=0 after quitting Codex App and CLI processes"
  exit 0
fi

BACKUP_DIR="${HOME}/Documents/CodexMigration/pre-restore-$(date +%Y%m%dT%H%M%S)"
mkdir -p "${BACKUP_DIR}"
chmod 700 "${BACKUP_DIR}"

log "backing up existing target files to ${BACKUP_DIR}"
mkdir -p "${HOME}/.codex" "${HOME}/.agents" "${HOME}/.config"
rsync -a --backup --backup-dir="${BACKUP_DIR}" "${STAGING_DIR}/home/" "${HOME}/"

if [ -d "${HOME}/.codex/superpowers/skills" ]; then
  mkdir -p "${HOME}/.agents/skills"
  ln -sfn ../../.codex/superpowers/skills "${HOME}/.agents/skills/superpowers"
fi

log "restore complete; reopen Codex, sign in, and run doctor_migration.sh"
