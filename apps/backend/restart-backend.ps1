# Thin wrapper: run this from apps\backend (or double-click from Explorer).
# Delegates to repo root scripts\restart-backend.ps1 — same behavior.
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Script = Join-Path $RepoRoot 'scripts\restart-backend.ps1'
if (-not (Test-Path $Script)) {
  Write-Host "Expected script not found: $Script"
  exit 1
}
& $Script
