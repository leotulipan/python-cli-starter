#!/usr/bin/env bash
# Build & install helper for python-cli
# Removes stray desktop.ini files, then installs via uv

set -e
cd "$(dirname "$0")"

echo "Removing desktop.ini files..."
rm -f desktop.ini scripts/desktop.ini

echo "Installing python-cli (editable)..."
uv tool install --editable .

echo ""
python-cli --version
echo "Done."
