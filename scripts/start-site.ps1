param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$python = Join-Path $backend ".venv\Scripts\python.exe"
$requirements = Join-Path $backend "requirements.txt"
$depsMarker = Join-Path $backend ".venv\.requirements-installed"
$node = "C:\Users\allja\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$pnpm = Join-Path $root "tools\pnpm\package\bin\pnpm.cjs"
$frontendDist = Join-Path $frontend "dist\index.html"
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

if (!(Test-Path $frontendDist)) {
  powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "scripts\start-frontend.ps1") -InstallOnly
  Push-Location $frontend
  try {
    if (Test-Path $node) {
      if (Test-Path $pnpm) {
        & $node $pnpm build
      } else {
        & $node .\node_modules\vite\bin\vite.js build
      }
    } elseif (Get-Command npm -ErrorAction SilentlyContinue) {
      npm run build
    } else {
      throw "Node.js was not found. Build the frontend first, then try again."
    }
  } finally {
    Pop-Location
  }
}

Push-Location $backend
try {
  $requirementsChanged = !(Test-Path $depsMarker) -or ((Get-Item $requirements).LastWriteTimeUtc -gt (Get-Item $depsMarker).LastWriteTimeUtc)
  if ($createdVenv -or $requirementsChanged) {
    & $python -m pip install --no-cache-dir --progress-bar off --index-url https://pypi.org/simple -r requirements.txt
    New-Item -ItemType File -Force -Path $depsMarker | Out-Null
  }
  & $python -m uvicorn app.main:app --host 127.0.0.1 --port $Port
} finally {
  Pop-Location
}
