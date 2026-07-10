#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

check() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    printf '[ok] %s\n' "${label}"
  else
    printf '[missing] %s\n' "${label}"
    FAILED=1
  fi
}

check_path() {
  local label="$1"
  local path="$2"
  if [ -e "${path}" ]; then
    printf '[ok] %s: %s\n' "${label}" "${path}"
  else
    printf '[missing] %s: %s\n' "${label}" "${path}"
    FAILED=1
  fi
}

printf '# Mac migration doctor\n'
check "Xcode Command Line Tools" xcode-select -p
check "Homebrew" command -v brew
check "git" command -v git
check "gh" command -v gh
check "node" command -v node
check "npm" command -v npm
check "opencode" command -v opencode
check "Codex npm package" bash -lc 'npm ls -g @openai/codex --depth=0'
check "1Password CLI" command -v op
check "Google Cloud CLI" command -v gcloud
check "VS Code CLI" command -v code

check_path "workspace root" "${HOME}/Documents/Other/context-infrastructure"
check_path "Basic workspace" "${HOME}/Documents/Basic"
check_path "Other workspace" "${HOME}/Documents/Other"
check_path "Codex config dir" "${HOME}/.codex"
check_path "Codex config" "${HOME}/.codex/config.toml"
check_path "Codex global rules" "${HOME}/.codex/AGENTS.md"
check_path "Codex skills" "${HOME}/.codex/skills"
check_path "shared agent skills" "${HOME}/.agents/skills"
check_path "Codex memories" "${HOME}/.codex/memories"
check_path "Codex automations" "${HOME}/.codex/automations"
check_path "OpenCode config dir" "${HOME}/.config/opencode"
check_path "SSH config" "${HOME}/.ssh/config"
check_path "gitconfig" "${HOME}/.gitconfig"
check_path "zshrc" "${HOME}/.zshrc"

printf '\n# Manual auth checks\n'
printf '%s\n' '- Run: gh auth status'
printf '%s\n' '- Run: op account list'
printf '%s\n' '- Run: gcloud auth list'
printf '%s\n' '- Run: ssh -T git@github.com'
printf '%s\n' '- Re-login Codex, Cursor, Chrome, Lark, WeChat, Google Drive/iCloud as needed.'
printf '%s\n' '- Open Codex and verify Skills, plugins, MCP servers, memories, automations, and Chrome control.'

if [ "${FAILED}" -ne 0 ]; then
  printf '\nDoctor found missing items.\n'
  exit 1
fi

printf '\nDoctor passed basic checks.\n'
