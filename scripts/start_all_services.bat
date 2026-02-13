@echo off
REM Start all services for fall detection system
REM Get the project root directory (parent of scripts folder)
setlocal enabledelayedexpansion
set "PROJECT_ROOT=%~dp0.."

echo Project Root: %PROJECT_ROOT%
echo.

echo Starting Frame Server...
start "Frame Server" cmd /k "cd /d %PROJECT_ROOT% && python src/video/frame_server.py"

echo Starting Node-RED...
start "Node-RED" cmd /k "cd /d %PROJECT_ROOT% && node-red"

echo Starting Main Application...
start "Main App" cmd /k "cd /d %PROJECT_ROOT% && streamlit run src/main.py"

echo.
echo All services started in separate windows
echo.
pause
