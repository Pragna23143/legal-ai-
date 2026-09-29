@echo off
title LexiClear AI - Legal Document Demystifier
echo ================================================================
echo   ⚖️  Starting LexiClear AI: Legal Document Demystifier
echo ================================================================
echo.

python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
