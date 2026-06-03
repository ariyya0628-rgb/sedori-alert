param(
  [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
  [string[]]$GitArgs
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$repo = $root.Replace("\", "/")
$git = "C:\Users\allja\AppData\Local\GitHubDesktop\app-3.5.8\resources\app\git\cmd\git.exe"
$gitMingwBin = "C:\Users\allja\AppData\Local\GitHubDesktop\app-3.5.8\resources\app\git\mingw64\bin"

if (!(Test-Path $git)) {
  throw "Git was not found. Install Git for Windows or GitHub Desktop, then try again."
}

if (Test-Path $gitMingwBin) {
  $env:PATH = "$gitMingwBin;$env:PATH"
  $env:GIT_EXEC_PATH = $gitMingwBin
}

& $git -c "safe.directory=$repo" -C $root @GitArgs
