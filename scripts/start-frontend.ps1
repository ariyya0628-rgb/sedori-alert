param(
  [switch]$InstallOnly
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $root "frontend"
$node = "C:\Users\allja\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$vite = Join-Path $frontend "node_modules\vite\bin\vite.js"
$localPnpmRoot = Join-Path $root "tools\pnpm"
$pnpm = Join-Path $localPnpmRoot "package\bin\pnpm.cjs"
$fallbackPnpm = Join-Path (Split-Path -Parent $root) "work\tools\package\bin\pnpm.cjs"

function Ensure-LocalPnpm {
  if (Test-Path $pnpm) {
    return
  }

  if (Test-Path $fallbackPnpm) {
    $fallbackPackage = Split-Path -Parent (Split-Path -Parent $fallbackPnpm)
    New-Item -ItemType Directory -Force -Path $localPnpmRoot | Out-Null
    Copy-Item -Path $fallbackPackage -Destination $localPnpmRoot -Recurse -Force
    return
  }

  $python = "C:\Users\allja\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  if (!(Test-Path $python)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
      $python = $pythonCommand.Source
    }
  }

  if (!(Test-Path $python)) {
    throw "npm is not available and Python was not found, so pnpm could not be prepared."
  }

  New-Item -ItemType Directory -Force -Path $localPnpmRoot | Out-Null

  $bootstrap = @'
import json
import os
import shutil
import sys
import tarfile
import urllib.request

tool_dir = sys.argv[1]
archive = os.path.join(tool_dir, "pnpm.tgz")
package_dir = os.path.join(tool_dir, "package")

with urllib.request.urlopen("https://registry.npmjs.org/pnpm/latest", timeout=30) as response:
    metadata = json.load(response)

tarball_url = metadata["dist"]["tarball"]
with urllib.request.urlopen(tarball_url, timeout=60) as response, open(archive, "wb") as target:
    shutil.copyfileobj(response, target)

if os.path.exists(package_dir):
    shutil.rmtree(package_dir)

with tarfile.open(archive, "r:gz") as tar:
    tar.extractall(tool_dir)
'@

  $bootstrap | & $python - $localPnpmRoot
}

Push-Location $frontend
try {
  if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm install
    if ($InstallOnly) {
      return
    }
    npm run dev
  } elseif (Test-Path $node) {
    Ensure-LocalPnpm
    & $node $pnpm install
    if ($InstallOnly) {
      return
    }
    & $node $vite --host 127.0.0.1
  } else {
    throw "npm is not available and bundled Node.js was not found. Install Node.js, then run npm install and npm run dev."
  }
} finally {
  Pop-Location
}
