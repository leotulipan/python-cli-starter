param(
  [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

if ($Clean) {
  Write-Host "Cleaning build artifacts..."
  Remove-Item -Recurse -Force "..\build" -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force "..\dist" -ErrorAction SilentlyContinue
}

Write-Host "Installing build deps..."
uv sync --group build

Write-Host "Building executable..."
uv run pyinstaller --clean --onefile --name python-cli ..\python-cli.spec

Write-Host "Built: ..\dist\python-cli.exe"
