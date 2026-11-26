@echo off
rem One-click launcher: PostgreSQL -> Neo4j -> 8 Java services -> Agent -> frontend
rem Logic lives in start-all.ps1 (PowerShell handles UTF-8 output correctly)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-all.ps1"
