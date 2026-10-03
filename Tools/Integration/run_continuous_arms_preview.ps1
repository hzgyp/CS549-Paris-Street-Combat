$ErrorActionPreference='Stop'
# Native migration supersedes the Slate/Python preview. Keep the familiar entry point safe.
# Historical Python source/evidence remain for diagnostics, not current-map launch authority.
& (Join-Path $PSScriptRoot 'run_paris_native_preview.ps1')
