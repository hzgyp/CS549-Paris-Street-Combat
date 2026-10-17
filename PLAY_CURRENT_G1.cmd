@echo off
cd /d "%~dp0"
if not exist "Releases\Paris-Tutorial-1.0-20261017\PLAY_TUTORIAL.cmd" (
  echo Restore the private tutorial release described in Docs\Development\CURRENT_TUTORIAL_RELEASE.json
  pause
  exit /b 1
)
call "Releases\Paris-Tutorial-1.0-20261017\PLAY_TUTORIAL.cmd"
