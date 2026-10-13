#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
rm -rf "$ROOT/generated" "$ROOT/dist"
echo "Removed generated files and distribution files."
