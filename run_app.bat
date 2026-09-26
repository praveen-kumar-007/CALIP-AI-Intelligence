@echo off
echo ==============================================
echo Starting CALIP Unified Server (FastAPI + React)
echo ==============================================
if not exist "frontend\dist\index.html" (
    echo React build not found. Building frontend first...
    cd frontend
    call npm install
    call npm run build
    cd ..
)
echo Launching FastAPI on http://localhost:8000 ...
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
pause
