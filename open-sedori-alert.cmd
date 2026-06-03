@echo off
setlocal
cd /d "%~dp0"

start "Sedori Alert Server" powershell -NoProfile -ExecutionPolicy Bypass -NoExit -File "%~dp0scripts\start-site.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\wait-and-open-site.ps1"

endlocal
