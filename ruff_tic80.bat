@echo off
setlocal

set ROOT=%~dp0
cd /d "%ROOT%"

ruff check tic80/python %*

endlocal
