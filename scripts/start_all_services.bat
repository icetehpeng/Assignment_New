@echo off
REM Start all services for fall detection system

echo Starting Frame Server...
start "Frame Server" cmd /k python src/video/frame_server.py

echo Starting Node-RED...
start "Node-RED" cmd /k node-red

echo Starting Main Application...
start "Main App" cmd /k streamlit run src/main.py

echo.
echo All services started in separate windows
echo.
pause
