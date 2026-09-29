Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  ⚖️  Starting LexiClear AI: Legal Document Demystifier" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Navigating to http://127.0.0.1:8000 ..." -ForegroundColor Yellow

python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
