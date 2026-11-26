@echo off
rem Stop backend services / Agent / frontend / Neo4j (PostgreSQL is kept running)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-all.ps1"
