@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY=C:\Users\28120\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" server.py
pause
