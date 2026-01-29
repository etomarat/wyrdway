setlocal

set "TIC80_EXE=D:\Projects\tic80\tic80.exe"
set "PROJ_DIR=.\tic80\python"
set "MAIN=main.py"

if not exist "%PROJ_DIR%" mkdir "%PROJ_DIR%"

REM Create a starter cart on first run (optional)
if not exist "%PROJ_DIR%\%MAIN%" (
  "%TIC80_EXE%" --fs "%PROJ_DIR%" --cmd "new python & save %MAIN%"
)

REM Auto-load and run the game
"%TIC80_EXE%" --fs "%PROJ_DIR%" --cmd "load %MAIN% & run" --crt

endlocal