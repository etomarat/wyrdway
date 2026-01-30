@echo off
setlocal

set ROOT=%~dp0
cd /d "%ROOT%"

mypy --config-file tic80\python\mypy.ini --exclude tic80/python/build.py tic80/python %*

endlocal

