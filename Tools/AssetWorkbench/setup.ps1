param([string]$Python = 'python', [string]$Pnpm = 'pnpm')
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskVenv = Join-Path $taskRoot 'Assets/LocalWorking/AssetWorkbench/runtime/venv'
$taskPython = Join-Path $taskVenv 'Scripts/python.exe'
& $Python -c "import sys; assert sys.version_info >= (3,13), 'Python 3.13+ required'"
if ($LASTEXITCODE -ne 0) { throw 'Python prerequisite check failed.' }
if (-not (Test-Path -LiteralPath $taskPython)) {
    & $Python -m venv $taskVenv
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
& $taskPython -m pip install -r (Join-Path $PSScriptRoot 'requirements.lock')
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
Push-Location (Join-Path $PSScriptRoot 'frontend')
try {
    & $Pnpm install --frozen-lockfile
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    & $Pnpm run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
} finally { Pop-Location }
Write-Output 'Setup complete. Run Tools/AssetWorkbench/run.ps1 to open the workbench.'
