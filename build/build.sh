#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1 && python -c 'import sys; raise SystemExit(0 if sys.version_info.major == 3 else 1)' 2>/dev/null; then
    PYTHON=python
else
    echo "Pigmatic requires Python 3."
    echo
    echo "Debian / Ubuntu:"
    echo "  sudo apt install python3"
    exit 1
fi
exec "$PYTHON" "$ROOT/build/build.py"
