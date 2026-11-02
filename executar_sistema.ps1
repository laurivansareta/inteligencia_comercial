# CYCLE AI - Inicializador PowerShell do Sistema Completo
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "CYCLE AI - Plataforma B2B SaaS de Customer Intelligence" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host "`n1. Iniciando Backend TypeScript (Porta 3001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; npm run dev"

Write-Host "2. Iniciando Frontend React (Porta 3002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "`nAguardando 3 segundos para abertura do navegador..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://localhost:3002"

