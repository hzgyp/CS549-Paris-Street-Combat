param([int]$Port = 0, [ValidateSet('LocalSubnet','Any')][string]$RemoteAddress = 'LocalSubnet')
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskState = Join-Path $taskRoot 'Assets/LocalWorking/AssetWorkbench'
$taskResult = Join-Path $taskState 'runtime/firewall-result.json'
try {
    $taskIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $taskPrincipal = [Security.Principal.WindowsPrincipal]::new($taskIdentity)
    if (-not $taskPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Administrator rights required for the Windows firewall rule.' }
    $taskSession = Get-Content -LiteralPath (Join-Path $taskState 'runtime/session.json') -Raw | ConvertFrom-Json
    if ($Port -eq 0) { $Port = $taskSession.port }
    if ($Port -lt 1 -or $Port -gt 65535 -or $Port -ne $taskSession.port -or $taskSession.host -ne '0.0.0.0') { throw 'The shared service/port must match the session.' }
    if ($RemoteAddress -eq 'Any' -and -not $taskSession.external_origin) { throw 'Configure and restart the explicit external sharing address first.' }
    $taskPython = Join-Path $taskState 'runtime/venv/Scripts/python.exe'
    $taskServer = Get-CimInstance Win32_Process -Filter "ProcessId=$($taskSession.pid)"
    if (-not $taskServer -or -not $taskServer.CommandLine.Contains($taskPython) -or -not $taskServer.CommandLine.Contains("-m app.cli serve --port $Port")) { throw 'Server identity mismatch.' }
    $taskRuleName = "ParisAssetWorkbench-TCP-$Port"
    $taskExisting = Get-NetFirewallRule -Name $taskRuleName -ErrorAction SilentlyContinue
    if ($taskExisting) { Remove-NetFirewallRule -Name $taskRuleName }
    New-NetFirewallRule -Name $taskRuleName -DisplayName "Paris Asset Workbench (TCP $Port)" -Direction Inbound -Action Allow -Enabled True -Profile Private,Domain -Protocol TCP -LocalPort $Port -RemoteAddress $RemoteAddress -Program $taskServer.ExecutablePath | Out-Null
    $taskRule = Get-NetFirewallRule -Name $taskRuleName
    $taskPorts = $taskRule | Get-NetFirewallPortFilter
    $taskAddresses = $taskRule | Get-NetFirewallAddressFilter
    $taskApp = $taskRule | Get-NetFirewallApplicationFilter
    if ($taskRule.Enabled -ne 'True' -or $taskRule.Action -ne 'Allow' -or $taskPorts.LocalPort -ne "$Port" -or $taskAddresses.RemoteAddress -ne $RemoteAddress -or $taskApp.Program -ne $taskServer.ExecutablePath) { throw 'Firewall readback mismatch.' }
    @{ status='enabled'; name=$taskRuleName; port=$Port; protocol='TCP'; remote_address=$RemoteAddress; profiles='Private,Domain'; program=$taskServer.ExecutablePath } | ConvertTo-Json | Set-Content -LiteralPath $taskResult -Encoding utf8
} catch {
    @{ status='failed'; error=$_.Exception.Message } | ConvertTo-Json | Set-Content -LiteralPath $taskResult -Encoding utf8
    exit 1
}
