# Each diagnostic runs in a fresh process; no existing report/capture is replaced.
param([switch]$Stride)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$descriptor = Join-Path $projectRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
$engineExe = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$evidenceRoot = Join-Path $projectRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/Movement'
if (Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue) { throw 'Close affected editors first' }
foreach ($variant in @('Allied_A','Allied_B','German_A','German_B')) {
    foreach ($fps in @(30,60,120)) {
        $prefix = if ($Stride) { 'v6' } else { 'v5' }
        $identity = "${prefix}_${variant}_${fps}"
        $reportPath = Join-Path $evidenceRoot "movement_probe_$identity.json"
        if (Test-Path -LiteralPath $reportPath) {
            $caseReport = [IO.File]::ReadAllText($reportPath) | ConvertFrom-Json -Depth 50
            if ($caseReport.result -ne 'pass_numeric_directional_only') { throw "Existing failed/incomplete report: $identity" }
            Write-Output "Retained prior completed case: $identity"
            continue
        }
        $logPath = Join-Path $projectRoot "tmp/paris-integration-20261001/p2-directional-$identity.log"
        $consolePath = Join-Path $projectRoot "tmp/paris-integration-20261001/p2-directional-$identity-console.log"
        $arguments = @($descriptor,'-EnablePlugins=PythonScriptPlugin,EditorScriptingUtilities,ParisEditorBridge',
            '-run=pythonscript',"-script=$(Join-Path $projectRoot 'Tools/Integration/ue_directional_probe.py')",
            "-ParisVariant=$variant","-ParisFPS=$fps","-ParisProbeIdentity=$identity",'-AllowCommandletRendering',
            '-RenderOffscreen','-unattended','-NoP4',"-abslog=$logPath")
        if ($Stride) { $arguments += '-ParisStride=true' }
        & $engineExe @arguments *> $consolePath
        if ($LASTEXITCODE -ne 0) { throw "Engine failed: $identity; preserve logs/evidence" }
        $caseReport = [IO.File]::ReadAllText($reportPath) | ConvertFrom-Json -Depth 50
        if ($caseReport.result -ne 'pass_numeric_directional_only') { throw "Numeric probe failed: $identity" }
        Write-Output "Completed numeric case: $identity; contact/stride requires separate review"
    }
}
