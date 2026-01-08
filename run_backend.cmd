@echo off
set PORT=8001
cd /d %~dp0
py -3.12 firstperson_backend.py
pause
