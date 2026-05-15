@echo off
setlocal

set "APP_DIR=%~dp0"
set "APP_FILE=%APP_DIR%memento_mori_calendar.py"
set "BUNDLED_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist "%BUNDLED_PY%" (
    "%BUNDLED_PY%" "%APP_FILE%"
    exit /b %ERRORLEVEL%
)

py -3 "%APP_FILE%"
if %ERRORLEVEL% EQU 0 exit /b 0

python "%APP_FILE%"
exit /b %ERRORLEVEL%
