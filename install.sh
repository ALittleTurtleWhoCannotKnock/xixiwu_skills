#!/usr/bin/env bash
# Install or update skills and agents using Python 3.9+.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "${1:-}" == multica ]]; then
  shift
  exec python3 -B "$ROOT/adapters/multica.py" "$@"
fi
exec python3 -B "$ROOT/adapters/install.py" "$@"
