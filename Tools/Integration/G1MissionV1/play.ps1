param([switch]$LoadSave,[switch]$CheckOnly,
 [string]$EngineEditor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe')
$ErrorActionPreference='Stop'
$taskLauncher=Join-Path $PSScriptRoot '../run_paris_native_preview.ps1'
& $taskLauncher -Entry G1 -LoadSave:$LoadSave -CheckOnly:$CheckOnly -EngineEditor $EngineEditor
