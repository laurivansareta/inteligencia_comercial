@echo off
title CYCLE AI - Inicializando Sistema
echo ======================================================================
echo CYCLE AI - Plataforma B2B SaaS de Customer Intelligence
echo ======================================================================
echo.

echo 1. Iniciando Backend TypeScript (Porta 3001)...
start "CYCLE AI - Backend API" cmd /k "cd backend && npm run dev"

echo 2. Iniciando Frontend React + TypeScript (Porta 3000)...
start "CYCLE AI - Frontend Web" cmd /k "cd frontend && npm run dev"

echo.
echo ======================================================================
echo Sistema em inicializacao!
echo Backend:  http://localhost:3001/api/health
echo Frontend: http://localhost:3000
echo ======================================================================
timeout /t 5
start http://localhost:3000

