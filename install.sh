#!/usr/bin/env bash
# Install or update skills and agents using Python 3.9+.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$ROOT/adapters/install.py" "$@"
