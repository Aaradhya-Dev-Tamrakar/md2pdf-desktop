@echo off
setlocal
REM ============================================================================
REM setup_context_menu.bat - Zero-Friction Execution Wrapper for setup_context_menu.ps1
REM ============================================================================

where pwsh >nul 2>nul
if %ERRORLEVEL% equ 0 (
    pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_context_menu.ps1" %*
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_context_menu.ps1" %*
)
exit /b %ERRORLEVEL%
