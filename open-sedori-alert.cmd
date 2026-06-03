@echo off
cd /d "%~dp0"
start "Sedori Alert Browser" powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\wait-and-open-site.ps1" -TimeoutSeconds 120
powershell -NoProfile -ExecutionPolicy Bypass -NoExit -File "%~dp0scripts\start-site.ps1"
