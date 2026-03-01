@echo off
setlocal

set ROOT=%~dp0
cd /d "%ROOT%"

pyright -p pyrightconfig.json tic80/python %*

endlocal
