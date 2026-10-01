param([string]$PythonExecutable)
$ErrorActionPreference = 'Stop'
if (-not $PythonExecutable) {
    $taskBundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $taskBundled) { $PythonExecutable = $taskBundled }
    else { $PythonExecutable = (Get-Command python -ErrorAction Stop).Source }
}
$taskPython = (Resolve-Path -LiteralPath $PythonExecutable).Path
& $taskPython -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
if ($LASTEXITCODE -ne 0) { throw 'Python runtime check failed' }
$taskRoot = Split-Path $PSScriptRoot -Parent
git -C $taskRoot config --local assets.pythonExecutable $taskPython
git -C $taskRoot config --local core.hooksPath .githooks
if ($LASTEXITCODE -ne 0) { throw 'Git hook configuration failed' }
Write-Output 'Configured local asset/source guards; no global Git configuration changed.'
