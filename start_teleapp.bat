@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv. Run bootstrap_teleapp.bat first.
  exit /b 1
)

call .venv\Scripts\activate.bat

if "%~1"=="" (
  teleapp
) else (
  teleapp %*
)
