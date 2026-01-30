@REM setlocal

@REM set "TIC80_EXE=D:\Projects\tic80\tic80.exe"
@REM set "PROJ_DIR=.\tic80\python"
@REM set "MAIN=main.py"

@REM if not exist "%PROJ_DIR%" mkdir "%PROJ_DIR%"

@REM REM Create a starter cart on first run (optional)
@REM if not exist "%PROJ_DIR%\%MAIN%" (
@REM   "%TIC80_EXE%" --fs "%PROJ_DIR%" --cmd "new python & save %MAIN%"
@REM )

@REM REM Auto-load and run the game
@REM "%TIC80_EXE%" --fs "%PROJ_DIR%" --cmd "load %MAIN% & run" --crt

@REM endlocal


@echo off
setlocal

REM --- Root = folder of this .bat (WYRDWAY)
set "ROOT=%~dp0"
pushd "%ROOT%" >nul

REM --- Project paths
set "PROJ_DIR=%ROOT%tic80\python"
set "GAME_FILE=tic80\python\game.py"
set "MAIN_FILE=tic80\python\main.py"

REM --- Find tq-bundler.exe (1) root, (2) tools\, (3) PATH
set "TQ_BUNDLER_PATH="
if exist "%ROOT%tq-bundler.exe" set "TQ_BUNDLER_PATH=%ROOT%tq-bundler.exe"
if not defined TQ_BUNDLER_PATH if exist "%ROOT%tools\tq-bundler.exe" set "TQ_BUNDLER_PATH=%ROOT%tools\tq-bundler.exe"
if not defined TQ_BUNDLER_PATH (
  for /f "delims=" %%i in ('where tq-bundler.exe 2^>nul') do (
    set "TQ_BUNDLER_PATH=%%i"
    goto :tq_done
  )
)
:tq_done

if not defined TQ_BUNDLER_PATH (
  echo [ERROR] tq-bundler.exe not found.
  echo Put tq-bundler.exe in the repo root, or in .\tools\, or add it to PATH.
  popd >nul
  exit /b 1
)

REM --- Find tic80.exe (1) root, (2) tic80\, (3) env var TIC80_EXE, (4) PATH
set "TIC80_EXE_PATH="
if exist "%ROOT%tic80.exe" set "TIC80_EXE_PATH=%ROOT%tic80.exe"
if not defined TIC80_EXE_PATH if exist "%ROOT%tic80\tic80.exe" set "TIC80_EXE_PATH=%ROOT%tic80\tic80.exe"
if not defined TIC80_EXE_PATH if defined TIC80_EXE set "TIC80_EXE_PATH=%TIC80_EXE%"
if not defined TIC80_EXE_PATH (
  for /f "delims=" %%i in ('where tic80.exe 2^>nul') do (
    set "TIC80_EXE_PATH=%%i"
    goto :tic_done
  )
)
:tic_done

if not defined TIC80_EXE_PATH (
  echo [ERROR] tic80.exe not found.
  echo Put tic80.exe in the repo root, or in .\tic80\, or set env var TIC80_EXE, or add it to PATH.
  popd >nul
  exit /b 1
)

if not exist "%TIC80_EXE_PATH%" (
  echo [ERROR] tic80.exe path resolved but file doesn't exist:
  echo %TIC80_EXE_PATH%
  popd >nul
  exit /b 1
)

REM --- Validate project files
if not exist "%PROJ_DIR%\" (
  echo [ERROR] Project folder not found: %PROJ_DIR%
  popd >nul
  exit /b 1
)
if not exist "%GAME_FILE%" (
  echo [ERROR] Missing: %GAME_FILE%
  popd >nul
  exit /b 1
)
if not exist "%MAIN_FILE%" (
  echo [ERROR] Missing: %MAIN_FILE%
  popd >nul
  exit /b 1
)

REM --- Modes:
REM   run_tic80_python.bat           -> bundle + run
REM   run_tic80_python.bat build     -> bundle only
set "MODE=%~1"
if /i "%MODE%"=="build" goto :build_only

echo [INFO] Using tq-bundler: %TQ_BUNDLER_PATH%
echo [INFO] Using tic80:     %TIC80_EXE_PATH%
echo [INFO] Bundling + launching TIC-80...
echo        "%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --tic "%TIC80_EXE_PATH%"
echo.
"%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --tic "%TIC80_EXE_PATH%"
set "EC=%errorlevel%"
popd >nul
exit /b %EC%

:build_only
echo [INFO] Using tq-bundler: %TQ_BUNDLER_PATH%
echo [INFO] Bundling only...
echo        "%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%"
echo.
"%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%"
set "EC=%errorlevel%"
popd >nul
exit /b %EC%
