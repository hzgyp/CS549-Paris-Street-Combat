param([ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
      [ValidateSet('actions','checkpoint')][string]$Mode,
      [string]$BuildIdentity='candidate_v3')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve active user engine'}
$taskBuild=Join-Path $taskRoot ('tmp/g1-playtest-revision-20261008/'+$BuildIdentity)
$taskOut=Join-Path $taskRoot ('tmp/g1-playtest-revision-20261008/'+$Identity)
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied evidence identity'}
New-Item -ItemType Directory -Path $taskOut|Out-Null
$taskBinary=Join-Path $taskBuild 'Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
$taskBuilt=Get-Content (Join-Path $taskBuild 'build_revision.json') -Raw|ConvertFrom-Json
if($taskBuilt.status -ne 'built_private_revision_runtime_unverified' -or (Get-FileHash $taskBinary).Hash.ToLower() -ne $taskBuilt.game_sha256){throw 'Built binary identity mismatch'}
$taskQuality='sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0'
$taskQuality='DisableAllScreenMessages,'+$taskQuality
$taskArgs=@('-RenderOffscreen','-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-NoSound','-unattended','-DisablePython','-noraytracing',
 ('-ParisUXTest='+$Mode),('-ParisUXTestOut="'+$taskOut.Replace('\','/')+'"'),('-ParisSavePrefix=ParisUX_'+$Identity),
 ('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),('-ExecCmds="'+$taskQuality+'"'))
$taskProcess=Start-Process $taskBinary -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskRecord=[ordered]@{identity=$Identity;build=$BuildIdentity;mode=$Mode;pid=$taskProcess.Id;arguments=$taskArgs;
 binary_sha256=(Get-FileHash $taskBinary).Hash.ToLower();scope='Finite simulated engine input/native path integration check; no model/resource/health/death writes; not human acceptance'}
$taskRecord|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'launch.json')
if(-not $taskProcess.WaitForExit(300000)){$taskRecord.deadline_terminated=$true;$taskProcess.Kill();$taskProcess.WaitForExit()}
$taskRecord.exit_code=$taskProcess.ExitCode
$taskRecord|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'launch.json')
if($taskRecord.exit_code -ne 0){throw 'Test process failed; preserve evidence'}
$taskResult=Get-Content (Join-Path $taskOut 'result.json') -Raw|ConvertFrom-Json
if($taskResult.status -notlike 'pass_*'){throw ('Finite integration check stopped: '+$taskResult.status)}
Write-Output $taskResult.status
