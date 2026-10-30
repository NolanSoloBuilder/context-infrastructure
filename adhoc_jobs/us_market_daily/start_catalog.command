#!/bin/zsh
set -e
catalog_home="$(cd "$(dirname "$0")" && pwd)"
"$catalog_home/.venv/bin/python" "$catalog_home/catalog_server.py" --background
print '本地观察台：http://127.0.0.1:8789/'
