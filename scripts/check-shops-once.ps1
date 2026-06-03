param(
  [string]$Keyword = "recolte",
  [int]$Limit = 3
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$python = Join-Path $backend ".venv\Scripts\python.exe"
$createdVenv = $false

if (!(Test-Path $python)) {
  $runtimePython = "C:\Users\allja\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  if (Test-Path $runtimePython) {
    & $runtimePython -m venv (Join-Path $backend ".venv")
  } else {
    python -m venv (Join-Path $backend ".venv")
  }
  $createdVenv = $true
}

Push-Location $backend
try {
  if ($createdVenv) {
    & $python -m pip install --no-cache-dir --progress-bar off --index-url https://pypi.org/simple -r requirements.txt
  }
  & $python -m app.cli.check_shops_once --keyword $Keyword --limit $Limit
} finally {
  Pop-Location
}
