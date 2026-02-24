#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# Build standalone executable using PyInstaller
uv sync --group build
uv run pyinstaller --clean --onefile --name python-cli ..\python-cli.spec

echo "Built: ..\dist\python-cli"
