#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BREWFILE="${BREWFILE:-${ROOT_DIR}/manifests/Brewfile}"
NPM_GLOBAL_FILE="${NPM_GLOBAL_FILE:-${ROOT_DIR}/manifests/npm-global.txt}"
VSCODE_EXTENSIONS_FILE="${VSCODE_EXTENSIONS_FILE:-${ROOT_DIR}/manifests/vscode_extensions.txt}"
CURSOR_EXTENSIONS_FILE="${CURSOR_EXTENSIONS_FILE:-${ROOT_DIR}/manifests/cursor_extensions.txt}"

log() {
  printf '[bootstrap] %s\n' "$*"
}

ensure_xcode_cli() {
  if ! xcode-select -p >/dev/null 2>&1; then
    log "installing Xcode Command Line Tools; finish the system dialog, then rerun this script"
    xcode-select --install
    exit 1
  fi
}

ensure_homebrew() {
  if command -v brew >/dev/null 2>&1; then
    return
  fi
  log "installing Homebrew"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -x /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
}

ensure_homebrew_path() {
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -x /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
}

install_brew_bundle() {
  if [ ! -f "${BREWFILE}" ]; then
    log "missing Brewfile: ${BREWFILE}"
    return
  fi

  if grep -q 'xdevplatform/tap' "${BREWFILE}" && [ "${ALLOW_UNTRUSTED_TAPS:-0}" = "1" ]; then
    log "trusting xdevplatform/tap because ALLOW_UNTRUSTED_TAPS=1"
    brew tap xdevplatform/tap || true
    brew trust xdevplatform/tap || true
  fi

  log "running brew bundle"
  brew update
  brew bundle --file="${BREWFILE}"
}

install_npm_globals() {
  if [ ! -f "${NPM_GLOBAL_FILE}" ]; then
    log "missing npm global manifest: ${NPM_GLOBAL_FILE}"
    return
  fi
  if ! command -v npm >/dev/null 2>&1; then
    log "npm missing after brew bundle; skip npm global packages"
    return
  fi

  log "installing npm globals into current global node environment"
  grep -vE '^\s*(#|$)' "${NPM_GLOBAL_FILE}" | while read -r package_name; do
    npm install -g "${package_name}"
  done
}

install_extensions() {
  if command -v code >/dev/null 2>&1 && [ -f "${VSCODE_EXTENSIONS_FILE}" ]; then
    log "installing VS Code extensions"
    grep -vE '^\s*(#|$)' "${VSCODE_EXTENSIONS_FILE}" | while read -r extension_id; do
      code --install-extension "${extension_id}" || true
    done
  fi

  if command -v cursor >/dev/null 2>&1 && [ -f "${CURSOR_EXTENSIONS_FILE}" ]; then
    log "installing Cursor extensions"
    grep -vE '^\s*(#|$)' "${CURSOR_EXTENSIONS_FILE}" | while read -r extension_id; do
      cursor --install-extension "${extension_id}" || true
    done
  fi
}

create_base_dirs() {
  log "creating base workspace directories"
  mkdir -p "${HOME}/Documents/Basic" "${HOME}/Documents/Other" "${HOME}/Documents/Codex"
}

ensure_xcode_cli
ensure_homebrew
ensure_homebrew_path
create_base_dirs
install_brew_bundle
install_npm_globals
install_extensions

log "done; run scripts/doctor_migration.sh next"
