@echo off
echo ============================================
echo  RAW - AI-Powered Investigation OS
echo  Combined Backend (Person 1 + Person 2)
echo ============================================

echo.
echo Activating Virtual Environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI Backend on http://localhost:8000
echo API Docs at http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
