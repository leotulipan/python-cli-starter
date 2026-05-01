$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$setupScript = Join-Path $scriptDir "initial_setup.py"

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    & py -3 $setupScript @args
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python $setupScript @args
    exit $LASTEXITCODE
}

Write-Error "Python 3 is required to run initial setup."
exit 1
