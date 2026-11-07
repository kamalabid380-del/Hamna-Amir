@echo off
cd /d "%~dp0"
wscript //nologo "%~dp0start-hidden.vbs"
set "URL=http://hamnaamir.com/%~1"
set "PROFILE=%TEMP%\hamna-amir-browser"
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
  start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="%PROFILE%" --no-first-run --no-default-browser-check --new-window "%URL%"
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
  start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --user-data-dir="%PROFILE%" --no-first-run --no-default-browser-check --new-window "%URL%"
) else (
  start "" "%URL%"
)