@echo off
cd /d "%~dp0"
if not exist "tmp\Playtest-G1-GrenadeEquip-20261011\PLAY_GRENADE_EQUIP.cmd" (
  echo Read Docs\Development\CURRENT_DEVELOPMENT_BASELINE.md
  pause
  exit /b 1
)
call "tmp\Playtest-G1-GrenadeEquip-20261011\PLAY_GRENADE_EQUIP.cmd"
