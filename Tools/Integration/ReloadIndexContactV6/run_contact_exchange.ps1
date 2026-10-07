param([string]$Identity='contact_exchange_v1')
$ErrorActionPreference='Stop'
$indexRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if($Identity -notmatch '^[a-z0-9_]+$'){throw 'Invalid evidence identity'}
if(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue){throw 'Another Unreal process owns slot'}
$indexRows=(Get-Content -LiteralPath (Join-Path $indexRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadIndexContactV6/preflight_v1/result.json') -Raw|ConvertFrom-Json).files
if($indexRows.Count -ne 528){throw 'Expected current528 snapshot'}
foreach($indexRow in $indexRows){$indexFile=Join-Path $indexRoot $indexRow.path;if((Get-Item -LiteralPath $indexFile).Length -ne $indexRow.size_bytes -or (Get-FileHash -LiteralPath $indexFile -Algorithm SHA256).Hash.ToLower() -ne $indexRow.sha256){throw ('Current byte changed: '+$indexRow.path)}}
$indexLog=Join-Path $indexRoot ('tmp/reload-index-contact-v6/'+$Identity+'.log')
$indexOut=Join-Path $indexRoot ('Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadIndexContactV6/'+$Identity)
if((Test-Path -LiteralPath $indexLog)-or(Test-Path -LiteralPath $indexOut)){throw 'Occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $indexLog) -Force|Out-Null
$env:CS549_INDEX_V6_ID=$Identity
$indexArgs=@(('"'+(Join-Path $indexRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),'/Engine/Maps/Entry','-DisablePlugins=ParisEditorBridge','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',('-ExecCmds="py '+(Join-Path $PSScriptRoot 'ue_contact_exchange.py').Replace('\','/')+'"'),('-abslog="'+$indexLog+'"'))
$indexProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $indexArgs -WindowStyle Hidden -PassThru
$indexHandle=$indexProcess.Handle
Write-Output ('Task-owned PID '+$indexProcess.Id+', '+$Identity)
$indexDone=$indexProcess.WaitForExit(180000)
if(-not $indexDone){Stop-Process -Id $indexProcess.Id -Force;$indexProcess.WaitForExit()}
$indexProcess.Refresh()
@{pid=$indexProcess.Id;identity=$Identity;exit_code=$indexProcess.ExitCode;timeout_terminated=(-not $indexDone);user_owned=$false}|ConvertTo-Json|Set-Content -LiteralPath ($indexLog+'.exit.json') -Encoding UTF8
if(-not $indexDone -or $indexProcess.ExitCode -ne 0){throw 'Contact probe failed, preserve evidence'}
Get-Content -LiteralPath ($indexLog+'.exit.json')
