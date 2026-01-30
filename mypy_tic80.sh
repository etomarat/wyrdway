#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

mypy --config-file tic80/python/mypy.ini --exclude tic80/python/build.py tic80/python "$@"

