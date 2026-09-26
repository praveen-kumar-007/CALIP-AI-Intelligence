@echo off
echo ==============================================
echo Building CALIP React Frontend...
echo ==============================================
cd frontend
call npm install
call npm run build
cd ..
echo Frontend build complete in frontend/dist!
pause
