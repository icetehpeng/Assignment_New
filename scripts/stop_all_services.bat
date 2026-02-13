@echo off
REM Stop all services for fall detection system
REM Get the project root directory (parent of scripts folder)
setlocal enabledelayedexpansion
set "PROJECT_ROOT=%~dp0.."

echo Project Root: %PROJECT_ROOT%
echo.
echo Stopping all services...

taskkill /F /IM python.exe
taskkill /F /IM node.exe

echo All services stopped
pause
