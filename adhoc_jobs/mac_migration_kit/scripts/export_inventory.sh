#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%dT%H%M%S)"
OUT_DIR="${ROOT_DIR}/inventory/${STAMP}"
mkdir -p "${OUT_DIR}"

log() {
  printf '[export] %s\n' "$*"
}

run_or_warn() {
  local name="$1"
  shift
  if ! "$@" >"${OUT_DIR}/${name}.txt" 2>"${OUT_DIR}/${name}.err"; then
    printf '%s\n' "${name}" >>"${OUT_DIR}/WARNINGS.txt"
  fi
}

log "writing system profile"
{
  date
  sw_vers
  uname -a
  printf 'arch=%s\n' "$(uname -m)"
  printf 'shell=%s\n' "${SHELL:-unknown}"
} >"${OUT_DIR}/system.txt"

if command -v brew >/dev/null 2>&1; then
  log "exporting Homebrew inventory"
  brew --prefix >"${OUT_DIR}/brew_prefix.txt" 2>&1 || true
  brew tap >"${OUT_DIR}/brew_taps.txt" 2>"${OUT_DIR}/brew_taps.err" || true
  brew list --formula --versions >"${OUT_DIR}/brew_formula_versions.txt" 2>"${OUT_DIR}/brew_formula_versions.err" || true
  brew list --cask >"${OUT_DIR}/brew_casks.txt" 2>"${OUT_DIR}/brew_casks.err" || true
  if ! brew bundle dump --file="${OUT_DIR}/Brewfile.generated" --force --describe >"${OUT_DIR}/brew_bundle_dump.log" 2>"${OUT_DIR}/brew_bundle_dump.err"; then
    printf '%s\n' "brew_bundle_dump" >>"${OUT_DIR}/WARNINGS.txt"
  fi
else
  printf '%s\n' "brew_missing" >>"${OUT_DIR}/WARNINGS.txt"
fi

if command -v npm >/dev/null 2>&1; then
  log "exporting npm global inventory"
  npm prefix -g >"${OUT_DIR}/npm_prefix_global.txt" 2>&1 || true
  npm root -g >"${OUT_DIR}/npm_root_global.txt" 2>&1 || true
  npm ls -g --depth=0 --json >"${OUT_DIR}/npm-global.json" 2>"${OUT_DIR}/npm-global.err" || true
  node -e 'const fs=require("fs"); const p=process.argv[1]; const j=JSON.parse(fs.readFileSync(p,"utf8")); const deps=Object.keys(j.dependencies||{}).filter((x)=>x!=="npm").sort(); console.log(deps.join("\n"));' "${OUT_DIR}/npm-global.json" >"${OUT_DIR}/npm-global.txt" 2>"${OUT_DIR}/npm-global-list.err" || true
else
  printf '%s\n' "npm_missing" >>"${OUT_DIR}/WARNINGS.txt"
fi

log "exporting editor extension lists"
if command -v code >/dev/null 2>&1; then
  code --list-extensions >"${OUT_DIR}/vscode_extensions.txt" 2>"${OUT_DIR}/vscode_extensions.err" || true
fi
if command -v cursor >/dev/null 2>&1; then
  cursor --list-extensions >"${OUT_DIR}/cursor_extensions.txt" 2>"${OUT_DIR}/cursor_extensions.err" || true
fi

log "exporting app and repo manifests"
find /Applications -maxdepth 1 -name '*.app' -print 2>/dev/null | sed 's#^/Applications/##; s#.app$##' | sort >"${OUT_DIR}/applications.txt"
find "${HOME}/Applications" -maxdepth 1 -name '*.app' -print 2>/dev/null | sed "s#^${HOME}/Applications/##; s#.app\$##" | sort >"${OUT_DIR}/user_applications.txt" || true
find "${HOME}/Documents" -name .git -type d -prune 2>/dev/null | sed 's#/.git$##' | sort >"${OUT_DIR}/git_repositories.txt" || true
{
  printf 'path\tbranch\torigin\n'
  while IFS= read -r repo_path; do
    [ -n "${repo_path}" ] || continue
    branch="$(git -C "${repo_path}" branch --show-current 2>/dev/null || true)"
    origin="$(git -C "${repo_path}" remote get-url origin 2>/dev/null || true)"
    origin="$(printf '%s' "${origin}" | sed -E 's#https://([^/@:]+(:[^/@]+)?@)#https://<redacted>@#')"
    printf '%s\t%s\t%s\n' "${repo_path}" "${branch}" "${origin}"
  done <"${OUT_DIR}/git_repositories.txt"
} >"${OUT_DIR}/git_repositories.tsv"

log "exporting AI tool config paths without secret contents"
{
  printf '# AI tool config candidates\n'
  for path in \
    "${HOME}/.codex" \
    "${HOME}/.claude" \
    "${HOME}/.config/opencode" \
    "${HOME}/.config/gh" \
    "${HOME}/.config/gcloud" \
    "${HOME}/.config/op" \
    "${HOME}/.ssh" \
    "${HOME}/.gitconfig" \
    "${HOME}/.zshrc" \
    "${HOME}/.npmrc"; do
    if [ -e "${path}" ]; then
      printf '%s\n' "${path}"
    fi
  done
} >"${OUT_DIR}/config_paths.txt"

log "exporting Codex skill, plugin, and MCP manifests"
{
  for root in "${HOME}/.codex/skills" "${HOME}/.agents/skills"; do
    [ -d "${root}" ] || continue
    find "${root}" -mindepth 1 -maxdepth 2 \( -type f -name SKILL.md -o -type l \) -print
  done
} | sed "s#^${HOME}/##" | sort -u >"${OUT_DIR}/codex_skills.txt"

if [ -f "${HOME}/.codex/config.toml" ]; then
  sed -nE 's/^\[plugins\."([^"]+)"\]$/\1/p' "${HOME}/.codex/config.toml" | sort -u >"${OUT_DIR}/codex_plugins.txt"
  sed -nE 's/^\[mcp_servers\.([^].]+)\]$/\1/p' "${HOME}/.codex/config.toml" | sort -u >"${OUT_DIR}/codex_mcp_servers.txt"
else
  : >"${OUT_DIR}/codex_plugins.txt"
  : >"${OUT_DIR}/codex_mcp_servers.txt"
fi

cat >"${OUT_DIR}/RESTORE_NOTES.md" <<'NOTES'
# Restore Notes

## Safe to restore by automation

- Homebrew formula/cask list, after reviewing untrusted taps.
- npm global package names.
- VS Code/Cursor extension IDs.
- Git repository URLs or local path manifest, after confirming which repos need fresh clone.
- AI tool rules/skills/config templates that do not contain tokens.
- Codex Skill, plugin, and MCP names. Use `backup_codex_environment.sh` for the
  private portable payload; never commit that archive.

## Restore manually

- Keychain, browser sessions, app logins.
- SSH private keys, unless deliberately moved through encrypted storage.
- `~/.codex/auth.json`, `~/.config/gcloud`, `~/.config/op`, `.env`, `*.secrets.yaml`, `~/.npmrc`.
- Paid apps or internal company apps that require device enrollment.

## Current machine warnings

Check `WARNINGS.txt` and `*.err` in this folder before trusting generated manifests.
NOTES

log "done: ${OUT_DIR}"
