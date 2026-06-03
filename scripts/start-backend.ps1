$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$python = Join-Path $backend ".venv\Scripts\python.exe"

if (!(Test-Path $python)) {
  $runtimePython = "C:\Users\allja\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  if (Test-Path $runtimePython) {
    & $runtimePython -m venv (Join-Path $backend ".venv")
  } else {
    python -m venv (Join-Path $backend ".venv")
  }
}

Push-Location $backend
try {
  & $python -m pip install --no-cache-dir --progress-bar off --index-url https://pypi.org/simple -r requirements.txt
  & $python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
} finally {
  Pop-Location
}
