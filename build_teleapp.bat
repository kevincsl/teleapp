@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv. Run bootstrap_teleapp.bat first.
  exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade build
python -m build

