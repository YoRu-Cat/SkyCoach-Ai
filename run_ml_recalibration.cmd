@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
pushd "%PROJECT_ROOT%"

set "PY=.\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=E:/Anaconda/Installed/python.exe"

"%PY%" -c "from ml_system.config.settings import CONFIG; from ml_system.api import get_ml_system; import json; CONFIG.linear_backend='scratch'; result=get_ml_system().train('ml_system/data/datasets/train.jsonl','ml_system/data/datasets/val.jsonl','ml_system/data/datasets/test.jsonl','ml_system/data/datasets/hardset.jsonl'); print(json.dumps(result, indent=2))"
set "EXIT_CODE=%ERRORLEVEL%"

popd
exit /b %EXIT_CODE%
