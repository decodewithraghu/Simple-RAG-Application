@echo off
REM RAG Application Startup Script for Windows
REM This script starts both backend and frontend services

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    Starting RAG Application
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

REM Start Backend
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Starting Backend Server...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Check if backend directory exists
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Backend directory not found at %BACKEND_DIR%
    exit /b 1
)

cd /d "%BACKEND_DIR%"

REM Find Python executable
set "PYTHON_BIN=python"
if exist "C:\rag\venv\Scripts\python.exe" (
    set "PYTHON_BIN=C:\rag\venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PYTHON_BIN=%BACKEND_DIR%\venv\Scripts\python.exe"
)

echo Using Python: !PYTHON_BIN!
echo.

REM Check if required packages are installed
!PYTHON_BIN! -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [WARNING] Python dependencies not found. Installing...
    !PYTHON_BIN! -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install backend dependencies
        exit /b 1
    )
)

REM Kill any existing process on port 8000
echo Checking for processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing existing process on port 8000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM Start backend
echo Starting FastAPI server on http://localhost:8000
start "RAG Backend" cmd /c "!PYTHON_BIN! main.py > backend.log 2>&1"

REM Wait for backend to start
echo.
echo Waiting for backend to start...
set /a count=0
:wait_backend
set /a count+=1
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    if !count! lss 30 (
        timeout /t 1 /nobreak >nul
        goto wait_backend
    ) else (
        echo [ERROR] Backend failed to start. Check backend.log
        exit /b 1
    )
)

echo [SUCCESS] Backend is ready!
echo.

REM Start Frontend
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Starting Frontend Server...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Check if frontend directory exists
if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found at %FRONTEND_DIR%
    exit /b 1
)

cd /d "%FRONTEND_DIR%"

REM Check if node_modules exists
if not exist "node_modules" (
    echo [WARNING] node_modules not found. Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies
        exit /b 1
    )
)

REM Kill any existing process on port 3000
echo Checking for processes on port 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    echo Killing existing process on port 3000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM Start frontend
echo Starting React development server on http://localhost:3000
set "BROWSER=none"
start "RAG Frontend" cmd /c "npm start > frontend.log 2>&1"

REM Wait for frontend to start
echo.
echo Waiting for frontend to start...
set /a count=0
:wait_frontend
set /a count+=1
netstat -an | findstr :3000 | findstr LISTENING >nul 2>&1
if errorlevel 1 (
    if !count! lss 60 (
        timeout /t 1 /nobreak >nul
        goto wait_frontend
    ) else (
        echo [ERROR] Frontend failed to start. Check frontend.log
        exit /b 1
    )
)

echo [SUCCESS] Frontend is ready!
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  RAG Application Started Successfully!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Application URLs:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Logs:
echo   Backend:  %BACKEND_DIR%\backend.log
echo   Frontend: %FRONTEND_DIR%\frontend.log
echo.
echo Opening application in browser...
timeout /t 2 /nobreak >nul
start http://localhost:3000
echo.
echo Press any key to stop all services...
pause >nul

REM Cleanup on exit
echo.
echo Shutting down services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo Shutdown complete!
