#!/bin/zsh
set -eu

# Reuse the existing Android SDK and avoid installing a second ADB version.
adb_bin="${HOME}/Library/Android/sdk/platform-tools/adb"
scrcpy_bin="/opt/homebrew/bin/scrcpy"
device_serial="${1:-a78e52ce}"
desktop_app="${HOME}/Applications/Android投屏.app"

# Launch through the app entry so macOS desktop-control tools can identify it.
if [[ $# -eq 0 && -d "$desktop_app" ]]; then
  exec /usr/bin/open -a "$desktop_app"
fi

[[ -x "$adb_bin" ]] || { print -u2 "Android SDK adb not found: $adb_bin"; exit 1; }
[[ -x "$scrcpy_bin" ]] || { print -u2 "scrcpy not found: $scrcpy_bin"; exit 1; }

exec env ADB="$adb_bin" "$scrcpy_bin" \
  --serial "$device_serial" \
  --no-audio \
  --max-size=1440 \
  --max-fps=30 \
  --window-title=Android-PFFM10 \
  --window-height=900 \
  --no-clipboard-autosync
