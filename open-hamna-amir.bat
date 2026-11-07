@echo off
cd /d "%~dp0"
wscript //nologo "%~dp0start-hidden.vbs"
start "" "http://127.0.0.1:8002/%~1"