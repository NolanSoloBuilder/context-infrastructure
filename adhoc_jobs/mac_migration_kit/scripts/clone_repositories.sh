#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_MANIFEST="${REPO_MANIFEST:-${ROOT_DIR}/manifests/git_repositories.current.tsv}"
DRY_RUN="${DRY_RUN:-1}"

log() {
  printf '[clone] %s\n' "$*"
}

if [ ! -f "${REPO_MANIFEST}" ]; then
  log "missing repo manifest: ${REPO_MANIFEST}"
  exit 1
fi

tail -n +2 "${REPO_MANIFEST}" | while IFS=$'\t' read -r repo_path branch origin; do
  [ -n "${repo_path}" ] || continue
  if [ -z "${origin}" ]; then
    log "skip local-only repo without origin: ${repo_path}"
    continue
  fi
  if printf '%s' "${origin}" | grep -q '<redacted>'; then
    log "skip redacted remote, fix manifest manually: ${repo_path}"
    continue
  fi
  if [ -e "${repo_path}" ]; then
    log "exists: ${repo_path}"
    continue
  fi

  log "clone ${origin} -> ${repo_path}"
  if [ "${DRY_RUN}" = "1" ]; then
    continue
  fi

  mkdir -p "$(dirname "${repo_path}")"
  git clone "${origin}" "${repo_path}"
  if [ -n "${branch}" ]; then
    git -C "${repo_path}" checkout "${branch}" || true
  fi
done

if [ "${DRY_RUN}" = "1" ]; then
  log "dry run complete; rerun with DRY_RUN=0 to clone"
else
  log "clone run complete"
fi
