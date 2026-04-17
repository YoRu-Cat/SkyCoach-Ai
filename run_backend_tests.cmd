@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
  "%PYTHON_EXE%" -m pytest -q tests test_auto_judge.py %*
) else (
  echo Project venv not found at .venv\Scripts\python.exe
  echo Falling back to py launcher.
  py -m pytest -q tests test_auto_judge.py %*
)

endlocal