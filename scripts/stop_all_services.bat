@echo off
REM Stop all services for fall detection system

echo Stopping all services...

taskkill /F /IM python.exe
taskkill /F /IM node.exe

echo All services stopped
pause
