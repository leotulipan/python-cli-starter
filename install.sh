#!/usr/bin/env bash
# Build & install helper for python-cli
# Removes stray desktop.ini files, then installs via uv

set -e
cd "$(dirname "$0")"

# Warn if the project hasn't been renamed yet
if grep -q '^name = "python-cli"' pyproject.toml 2>/dev/null; then
  echo "WARNING: Project is still named 'python-cli'."
  echo "Run 'python init.py my-tool' first to rename it."
  echo ""
fi

echo "Removing desktop.ini files..."
rm -f desktop.ini scripts/desktop.ini

echo "Installing python-cli (editable)..."
uv tool install --editable .

echo ""
python-cli --version
echo "Done."
