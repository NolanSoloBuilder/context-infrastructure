# Restore Notes

## Safe to restore by automation

- Homebrew formula/cask list, after reviewing untrusted taps.
- npm global package names.
- VS Code/Cursor extension IDs.
- Git repository URLs or local path manifest, after confirming which repos need fresh clone.
- AI tool rules/skills/config templates that do not contain tokens.

## Restore manually

- Keychain, browser sessions, app logins.
- SSH private keys, unless deliberately moved through encrypted storage.
- `~/.codex/auth.json`, `~/.config/gcloud`, `~/.config/op`, `.env`, `*.secrets.yaml`, `~/.npmrc`.
- Paid apps or internal company apps that require device enrollment.

## Current machine warnings

Check `WARNINGS.txt` and `*.err` in this folder before trusting generated manifests.
