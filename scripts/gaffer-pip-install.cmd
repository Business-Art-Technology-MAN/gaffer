@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem Install Python packages using Gaffer's embedded Python.
rem Packages go to %%USERPROFILE%%\gaffer\python_packages (on PYTHONPATH when using this repo's _gaffer.py).
rem
rem Finds a built install (bin\__private\gaffer.exe), in order:
rem   1. GAFFER_ROOT if you set it (install root or ...\bin folder)
rem   2. GAFFER_BUILD_DIR (same as SCons / CI: folder that contains bin\, e.g. gaffer-build-11a8)
rem   3. Walk up from %%CD%% looking for bin\__private\gaffer.exe
rem   4. Walk up from this script's repo root (scripts\..) — finds builds under the checkout
rem
rem If this still errors, your tree has no gaffer.exe yet, or it lives outside these paths: set GAFFER_ROOT
rem explicitly to the directory that contains bin\__private\gaffer.exe's parent (the usual Gaffer root).

call :normalize_and_validate || exit /b 1

set "PIP_TARGET=%USERPROFILE%\gaffer\python_packages"
if not exist "%PIP_TARGET%" mkdir "%PIP_TARGET%"

echo Using GAFFER_ROOT=!GAFFER_ROOT!
echo pip install --target "%PIP_TARGET%"
"%GAFFER_ROOT%\bin\gaffer.cmd" env python -m pip install %* --target "%PIP_TARGET%"
exit /b %ERRORLEVEL%

rem Subroutines -----------------------------------------------------------

:normalize_and_validate
if defined GAFFER_ROOT goto :user_root
if defined GAFFER_BUILD_DIR (
	call :try_set_root "%GAFFER_BUILD_DIR%"
	if defined GAFFER_ROOT goto :have_root
)
set "D=%CD%"
:call_climb_cd
	call :try_set_root "!D!"
	if defined GAFFER_ROOT goto :have_root
	for %%I in ("!D!\..") do set "PARENT=%%~fI"
	if /i "!PARENT!"=="!D!" goto :call_climb_repo
	set "D=!PARENT!"
goto :call_climb_cd

:call_climb_repo
for %%I in ("%~dp0..") do set "D=%%~fI"
:call_climb_repo_loop
	call :try_set_root "!D!"
	if defined GAFFER_ROOT goto :have_root
	for %%I in ("!D!\..") do set "PARENT=%%~fI"
	if /i "!PARENT!"=="!D!" goto :notfound
	set "D=!PARENT!"
goto :call_climb_repo_loop

:user_root
set "_UR=%GAFFER_ROOT%"
set "GAFFER_ROOT="
call :try_set_root "%_UR%"
if not defined GAFFER_ROOT (
	echo ERROR: GAFFER_ROOT was "%_UR%" but bin\__private\gaffer.exe was not found there ^(or __private\gaffer.exe if that path is ...\bin^).
	set "_UR="
	exit /b 1
)
set "_UR="
goto :have_root

:have_root
if not exist "!GAFFER_ROOT!\bin\gaffer.cmd" (
	echo ERROR: "!GAFFER_ROOT!\bin\gaffer.cmd" not found.
	exit /b 1
)
exit /b 0

:notfound
	echo ERROR: No bin\__private\gaffer.exe found.
	echo   Build Gaffer first, then either:
	echo   - set GAFFER_BUILD_DIR to your SCons output folder ^(contains bin\, e.g. gaffer-build-11a8^), or
	echo   - set GAFFER_ROOT to that same folder, or
	echo   - cd to that folder or its bin\ subfolder and run this script again.
	exit /b 1

rem Sets GAFFER_ROOT to the install root if "%~1" is install root or ...\bin, else leaves unset.
:try_set_root
set "R=%~1"
if not defined R exit /b 0
if exist "!R!\bin\__private\gaffer.exe" (
	set "GAFFER_ROOT=!R!"
	exit /b 0
)
if exist "!R!\__private\gaffer.exe" (
	for %%I in ("!R!\..") do set "GAFFER_ROOT=%%~fI"
	exit /b 0
)
exit /b 0
