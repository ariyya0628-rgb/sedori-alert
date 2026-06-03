param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$GitArgs
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$repo = $root.Replace("\", "/")
$git = "C:\Users\allja\AppData\Local\GitHubDesktop\app-3.5.8\resources\app\git\cmd\git.exe"

if (!(Test-Path $git)) {
  throw "Git was not found. Install Git for Windows or GitHub Desktop, then try again."
}

& $git -c "safe.directory=$repo" -C $root @GitArgs
