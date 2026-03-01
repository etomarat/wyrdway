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
set "FS_ROOT=%ROOT%"
if "%FS_ROOT:~-1%"=="\" set "FS_ROOT=%FS_ROOT:~0,-1%"
pushd "%ROOT%" >nul

REM --- Project paths
set "PROJ_DIR=%ROOT%tic80\python"
set "GAME_FILE=tic80\python\game.py"
set "MAIN_FILE=tic80\python\main.py"
set "BUILD_FILE=tic80\python\build.py"
set "MIN_BUILD_FILE=build.min.py"
set "MINIFY_SCRIPT=%ROOT%scripts\minify_tic80_build.py"
set "MINIFY_SCRIPT_REL=scripts\minify_tic80_build.py"
set "DIST_DIR=%ROOT%dist"
set "OUT_BASE=wyrdway"

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
REM   run_tic80_python.bat        -> bundle + minify(via tq-bundler post-build) + run
REM   run_tic80_python.bat dev    -> bundle + minify(via tq-bundler post-build) + run
REM   run_tic80_python.bat build  -> bundle + minify(via tq-bundler post-build) only
REM   run_tic80_python.bat dist   -> bundle + minify(via tq-bundler post-build) + export .tic/.exe/html
set "MODE=%~1"
if "%MODE%"=="" set "MODE=run"
if /i not "%MODE%"=="run" if /i not "%MODE%"=="dev" if /i not "%MODE%"=="build" if /i not "%MODE%"=="dist" (
  echo [ERROR] Unknown mode: %MODE%
  echo Usage: run_tic80_python.bat [run^|dev^|build^|dist]
  popd >nul
  exit /b 1
)

if not exist "%MINIFY_SCRIPT%" (
  echo [ERROR] Missing: %MINIFY_SCRIPT%
  popd >nul
  exit /b 1
)

if /i "%MODE%"=="dev" goto :run_dev
if /i "%MODE%"=="build" goto :build_only
if /i "%MODE%"=="dist" goto :dist
if /i not "%MODE%"=="run" (
  echo [ERROR] Internal mode dispatch failure: %MODE%
  popd >nul
  exit /b 1
)

echo [INFO] Using tq-bundler: %TQ_BUNDLER_PATH%
echo [INFO] Using tic80:     %TIC80_EXE_PATH%
echo [INFO] Bundling + minifying via tq-bundler post-build...
echo        "%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --post-output "%MIN_BUILD_FILE%" --post-build "python %MINIFY_SCRIPT_REL% {input} {output}"
echo.
"%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --post-output "%MIN_BUILD_FILE%" --post-build "python %MINIFY_SCRIPT_REL% {input} {output}"
set "EC=%errorlevel%"
if %EC% neq 0 (
  popd >nul
  exit /b %EC%
)
echo [INFO] Launching TIC-80 with minified bundle...
echo        "%TIC80_EXE_PATH%" --fs "%FS_ROOT%" --cmd "load tic80/python/game.py & import code tic80/python/build.min.py & run" --crt
echo.
"%TIC80_EXE_PATH%" --fs "%FS_ROOT%" --cmd "load tic80/python/game.py & import code tic80/python/build.min.py & run" --crt
set "EC=%errorlevel%"
popd >nul
exit /b %EC%

:run_dev
echo [INFO] Using tq-bundler: %TQ_BUNDLER_PATH%
echo [INFO] Using tic80:     %TIC80_EXE_PATH%
echo [INFO] Bundling + minifying via tq-bundler post-build (dev)...
echo        "%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --post-output "%MIN_BUILD_FILE%" --post-build "python %MINIFY_SCRIPT_REL% {input} {output}"
echo.
"%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --post-output "%MIN_BUILD_FILE%" --post-build "python %MINIFY_SCRIPT_REL% {input} {output}"
set "EC=%errorlevel%"
if %EC% neq 0 (
  popd >nul
  exit /b %EC%
)
echo [INFO] Launching TIC-80 with minified bundle (dev)...
echo        "%TIC80_EXE_PATH%" --fs "%FS_ROOT%" --cmd "load tic80/python/game.py & import code tic80/python/build.min.py & run" --crt
echo.
"%TIC80_EXE_PATH%" --fs "%FS_ROOT%" --cmd "load tic80/python/game.py & import code tic80/python/build.min.py & run" --crt
set "EC=%errorlevel%"
popd >nul
exit /b %EC%

:build_only
echo [INFO] Using tq-bundler: %TQ_BUNDLER_PATH%
echo [INFO] Bundling + minifying via tq-bundler post-build (build only)...
echo        "%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --post-output "%MIN_BUILD_FILE%" --post-build "python %MINIFY_SCRIPT_REL% {input} {output}"
echo.
"%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --post-output "%MIN_BUILD_FILE%" --post-build "python %MINIFY_SCRIPT_REL% {input} {output}"
set "EC=%errorlevel%"
popd >nul
exit /b %EC%

:dist
echo [INFO] Using tq-bundler: %TQ_BUNDLER_PATH%
echo [INFO] Using tic80:     %TIC80_EXE_PATH%
echo [INFO] Cleaning dist folder...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"
echo [INFO] Bundling + minifying via tq-bundler post-build...
echo        "%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --post-output "%MIN_BUILD_FILE%" --post-build "python %MINIFY_SCRIPT_REL% {input} {output}"
echo.
"%TQ_BUNDLER_PATH%" run "%GAME_FILE%" "%MAIN_FILE%" --post-output "%MIN_BUILD_FILE%" --post-build "python %MINIFY_SCRIPT_REL% {input} {output}"
if errorlevel 1 (
  set "EC=%errorlevel%"
  popd >nul
  exit /b %EC%
)
echo [INFO] Exporting .tic/.exe/html/linux/mac to dist...
echo        "%TIC80_EXE_PATH%" --cli --crt --fs "%FS_ROOT%" --cmd "load tic80/python/game.py & import code tic80/python/build.min.py & save dist/%OUT_BASE%.tic & export win dist/%OUT_BASE% alone=0 & export linux dist/%OUT_BASE%-linux alone=0 & export mac dist/%OUT_BASE%-mac alone=0 & export html dist/%OUT_BASE% alone=0 & exit"
echo.
"%TIC80_EXE_PATH%" --cli --crt --fs "%FS_ROOT%" --cmd "load tic80/python/game.py & import code tic80/python/build.min.py & save dist/%OUT_BASE%.tic & export win dist/%OUT_BASE% alone=0 & export linux dist/%OUT_BASE%-linux alone=0 & export mac dist/%OUT_BASE%-mac alone=0 & export html dist/%OUT_BASE% alone=0 & exit"
set "EC=%errorlevel%"
popd >nul
exit /b %EC%
