@echo off
setlocal

set "ROOT=%~dp0"
set "FS_ROOT=%ROOT%"
if "%FS_ROOT:~-1%"=="\" set "FS_ROOT=%FS_ROOT:~0,-1%"
pushd "%ROOT%" >nul

set "LUA_ENTRY=tic80\lua\src\main.lua"
set "LUA_CART=tic80\lua\main.lua"
set "BUILD_FILE=tic80\lua\build.lua"
set "BUNDLE_SCRIPT=%ROOT%scripts\bundle_tic80_lua.py"
set "DIST_DIR=%ROOT%dist"
set "OUT_BASE=wyrdway-lua-experiment"

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

if not exist "%LUA_ENTRY%" (
  echo [ERROR] Missing: %LUA_ENTRY%
  popd >nul
  exit /b 1
)
if not exist "%LUA_CART%" (
  echo [ERROR] Missing: %LUA_CART%
  popd >nul
  exit /b 1
)

if not exist "%BUNDLE_SCRIPT%" (
  echo [ERROR] Missing: %BUNDLE_SCRIPT%
  popd >nul
  exit /b 1
)

set "MODE=%~1"
if "%MODE%"=="" set "MODE=run"
if /i not "%MODE%"=="run" if /i not "%MODE%"=="dev" if /i not "%MODE%"=="build" if /i not "%MODE%"=="dist" (
  echo [ERROR] Unknown mode: %MODE%
  echo Usage: run_tic80_lua.bat [run^|dev^|build^|dist]
  popd >nul
  exit /b 1
)

if /i "%MODE%"=="build" goto :build_only
if /i "%MODE%"=="dist" goto :dist
if /i "%MODE%"=="dev" goto :run_mode
if /i "%MODE%"=="run" goto :run_mode

:build_only
echo [INFO] Bundling Lua experiment...
echo        python "%BUNDLE_SCRIPT%" "%LUA_ENTRY%" "%BUILD_FILE%"
echo.
python "%BUNDLE_SCRIPT%" "%LUA_ENTRY%" "%BUILD_FILE%"
set "EC=%errorlevel%"
popd >nul
exit /b %EC%

:run_mode
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
echo [INFO] Bundling Lua experiment...
python "%BUNDLE_SCRIPT%" "%LUA_ENTRY%" "%BUILD_FILE%"
if errorlevel 1 (
  set "EC=%errorlevel%"
  popd >nul
  exit /b %EC%
)
echo [INFO] Launching TIC-80 with Lua experiment...
echo        "%TIC80_EXE_PATH%" --fs "%FS_ROOT%" --cmd "load %LUA_CART% & import code %BUILD_FILE% & run" --crt
echo.
"%TIC80_EXE_PATH%" --fs "%FS_ROOT%" --cmd "load %LUA_CART% & import code %BUILD_FILE% & run" --crt
set "EC=%errorlevel%"
popd >nul
exit /b %EC%

:dist
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
echo [INFO] Cleaning dist folder...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"
echo [INFO] Bundling Lua experiment...
python "%BUNDLE_SCRIPT%" "%LUA_ENTRY%" "%BUILD_FILE%"
if errorlevel 1 (
  set "EC=%errorlevel%"
  popd >nul
  exit /b %EC%
)
echo [INFO] Exporting Lua experiment cart...
echo        "%TIC80_EXE_PATH%" --cli --crt --fs "%FS_ROOT%" --cmd "load %LUA_CART% & import code %BUILD_FILE% & save dist/%OUT_BASE%.tic & export win dist/%OUT_BASE% alone=0 & export html dist/%OUT_BASE% alone=0 & exit"
echo.
"%TIC80_EXE_PATH%" --cli --crt --fs "%FS_ROOT%" --cmd "load %LUA_CART% & import code %BUILD_FILE% & save dist/%OUT_BASE%.tic & export win dist/%OUT_BASE% alone=0 & export html dist/%OUT_BASE% alone=0 & exit"
set "EC=%errorlevel%"
popd >nul
exit /b %EC%
