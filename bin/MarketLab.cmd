@echo off

rem MarketLab launcher (same runtime as gaffer.cmd; branding differs in the UI).

setlocal EnableDelayedExpansion

set "HOME=%USERPROFILE:\=/%"

set PYTHONHOME=%~dp0%..
set PATH=%PYTHONHOME%\bin;%PATH%

if "%GAFFER_DEBUG%" NEQ "" (
	%GAFFER_DEBUGGER% "%PYTHONHOME%"\bin\__private\gaffer.exe "%PYTHONHOME%"/bin/__private/_gaffer.py %*
) else (
	"%PYTHONHOME%"\bin\__private\gaffer.exe "%PYTHONHOME%"/bin/__private/_gaffer.py %*
)

endlocal
exit /B %ERRORLEVEL%
