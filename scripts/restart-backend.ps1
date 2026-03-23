# Run from repo root. Stops guessing which folder uvicorn uses - always this codebase.
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'apps\backend'
$VenvPy = Join-Path $Backend '.venv\Scripts\python.exe'

if (-not (Test-Path $VenvPy)) {
  Write-Host ('Missing ' + $VenvPy + ' - create venv and pip install -r requirements.txt first.')
  exit 1
}

# If something else is already listening on 8000, you may see only {"status":"ok"} or wrong JSON — not this app.
$listeners = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($listeners) {
  Write-Host ''
  Write-Host 'Port 8000 is already in use. Stop that process first, then re-run this script.' -ForegroundColor Yellow
  Write-Host '(Another listener often serves a different / minimal /api/health and hides email_format_version.)' -ForegroundColor Yellow
  Write-Host 'Tip: uvicorn --reload uses two Python processes (reloader + worker). Prefer Ctrl+C in the server terminal.' -ForegroundColor DarkGray
  $pids = @($listeners | ForEach-Object { $_.OwningProcess } | Where-Object { $_ -gt 0 } | Sort-Object -Unique)
  foreach ($procId in $pids) {
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($null -eq $proc) {
      Write-Host ('  PID ' + $procId + ' (already exited — ignore; re-run this script in 1–2 seconds)')
    } else {
      Write-Host ('  PID ' + $procId + ' (' + $proc.ProcessName + ')')
    }
  }
  Write-Host 'Or: Stop-Process -Id <pid> -Force   Last resort: Stop-Process -Name python -Force (stops ALL Python).' -ForegroundColor Yellow
  Write-Host ''
  exit 1
}

Write-Host 'Removing app\**\__pycache__ under apps\backend ...'
Get-ChildItem -Path (Join-Path $Backend 'app') -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue |
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Set-Location $Backend
Write-Host ('Starting uvicorn from: ' + $Backend)
Write-Host ''
Write-Host 'Health check: http://127.0.0.1:8000/api/health'
& $VenvPy -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
