#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
rm -rf "$ROOT/tools"
echo "Removed downloaded build tools."
