#!/usr/bin/env bash
# 查当前 lark-cli 的登录身份。返回 user_id / name 即授权成功。
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
exec npx --no-install lark-cli api GET /open-apis/authen/v1/user_info "$@"
