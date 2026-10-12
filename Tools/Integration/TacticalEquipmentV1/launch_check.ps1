param([string]$Revision='candidate_v1',[string]$Mode='inventory',[ValidatePattern('^[a-z0-9_]+$')][string]$Identity='inventory_v1',[string]$SeedDirectory='',[string]$SeedPrefix='')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-tactical-equipment-20261010'
$taskOut=Join-Path $taskBase ('checks/'+$Identity)
if(Get-Process WW2FranceLiberation*,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Preserve active game/build'}
$taskEditors=@(Get-Process UnrealEditor -ErrorAction SilentlyContinue)
if($taskEditors.Count){
 $taskOwnerPath=Join-Path $taskBase 'editor-sessions.json'
 if(-not (Test-Path -LiteralPath $taskOwnerPath)){$taskOwnerPath=Join-Path $taskBase 'editor-session.json'}
 $taskOwners=@(Get-Content -LiteralPath $taskOwnerPath -Raw | ConvertFrom-Json)
 foreach($taskEditor in $taskEditors){if($taskEditor.Id -notin @($taskOwners.pid)){throw 'Preserve unrelated editor session'}}
 # This owned Editor stays open without PIE/content writes. These Game checks read immutable cooked files.
}
if(Test-Path -LiteralPath $taskOut){throw 'Preserve test identity'}
New-Item -ItemType Directory -Path $taskOut | Out-Null
$taskRuntime=Get-Content -LiteralPath (Join-Path $taskBase ($Revision+'/runtime.json')) -Raw | ConvertFrom-Json
$taskExe=Join-Path $taskRuntime.path 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
if((Get-FileHash -LiteralPath $taskExe).Hash.ToLowerInvariant() -ne $taskRuntime.game_sha256){throw 'Runtime changed'}
$taskUser=Join-Path $taskOut 'User'
if($SeedDirectory){
 if(-not $SeedPrefix){throw 'Explicit seed prefix required'}
 $taskSaveDirectory=Join-Path $taskUser 'Saved/SaveGames'
 New-Item -ItemType Directory -Path $taskSaveDirectory -Force | Out-Null
 $taskSeeds=@()
 foreach($taskSuffix in @('_A.sav','_B.sav')){
  $taskSeed=Join-Path $SeedDirectory ($SeedPrefix+$taskSuffix)
  if(Test-Path -LiteralPath $taskSeed){
   $taskDestination=Join-Path $taskSaveDirectory ('ParisEquipment_'+$Identity+$taskSuffix)
   Copy-Item -LiteralPath $taskSeed -Destination $taskDestination
   $taskSeeds+=@{source=$taskSeed;destination=$taskDestination;sha256=(Get-FileHash -LiteralPath $taskDestination).Hash.ToLowerInvariant()}
  }
 }
 if(-not $taskSeeds.Count){throw 'No seed checkpoint copied'}
 $taskSeeds | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'seed.json')
}
$taskArgs=@('-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',('-UserDir="'+$taskUser+'"'),('-abslog="'+$taskOut+'/game.log"'),('-ParisSavePrefix=ParisEquipment_'+$Identity),'-ExecCmds="sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 60"')
$taskArgs+=@('-DPCVars="sg.ViewDistanceQuality=2,sg.AntiAliasingQuality=2,sg.ShadowQuality=2,sg.GlobalIlluminationQuality=2,sg.ReflectionQuality=2,sg.PostProcessQuality=2,sg.TextureQuality=2,sg.EffectsQuality=2,sg.FoliageQuality=2,sg.ShadingQuality=2,r.ScreenPercentage=100,r.Streaming.PoolSize=1536,r.VSync=0,t.MaxFPS=60"')
if($Mode -in @('menu','enemy_clear')){$taskArgs+=@('-ParisInteractionProbe='+$Mode,('-ParisInteractionOut="'+$taskOut+'"'))}
elseif($Mode -eq 'p1'){$taskArgs+=@('-ParisP1Probe',('-ParisP1Out="'+$taskOut+'"'))}
else{$taskArgs+=@('-ParisEquipmentCheck='+$Mode,('-ParisEquipmentOut="'+$taskOut+'"'))}
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskReceipt=[ordered]@{status='running';mode=$Mode;identity=$Identity;revision=$Revision;pid=$taskProcess.Id;started=[DateTimeOffset]::Now.ToString('o');game_sha256=$taskRuntime.game_sha256;arguments=$taskArgs}
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
[ordered]@{pid=$taskProcess.Id;mode=$Mode;identity=$Identity}|ConvertTo-Json -Compress
$taskDeadline=[DateTime]::UtcNow.AddSeconds(180)
while(-not $taskProcess.WaitForExit(1000)){
 if([DateTime]::UtcNow -gt $taskDeadline){$taskReceipt.status='deadline_preserve_owned_process';$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json');throw 'Inspect owned process without force termination'}
}
$taskReceipt.exit_code=$taskProcess.ExitCode;$taskReceipt.status='exited';$taskReceipt.finished=[DateTimeOffset]::Now.ToString('o')
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
if($taskProcess.ExitCode -ne 0){throw 'Abnormal game exit; preserve evidence'}
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut $(if($Mode -eq 'inventory'){'INVENTORY.json'}else{'RESULT.json'})) -Raw | ConvertFrom-Json
[ordered]@{status=$taskResult.status;reason=$taskResult.reason;checks=$taskResult.checks.Count;events=$taskResult.events.Count;exit_code=$taskProcess.ExitCode} | ConvertTo-Json -Compress
