# Playbook Studio - local launcher (native, no Docker).
#
# Starts both halves with hot reload:
#   - studio backend  -> http://127.0.0.1:8907   (FastAPI; PORT env below)
#   - studio frontend -> http://localhost:5199   (vite; /api proxied to :8907)
#
# First run provisions everything:
#   - backend venv + deps, plus pytest-intent from the sibling checkout
#     (../pytest-intent) so the validation gates can run the playbook's suite
#   - frontend node_modules (npm ci) and the generated API types (api:generate)
# Subsequent runs just spawn the two server windows.
#
# Requires the sibling-clone topology: the playbook checkout must exist at
# <workspace>/ai-coding-prompts next to this csd-library checkout.
#
# Run by double-clicking start.bat, or:
#   powershell -ExecutionPolicy Bypass -File devops\start.ps1

$ErrorActionPreference = 'Stop'

$studio     = Split-Path -Parent $PSScriptRoot
$csdLibrary = Split-Path -Parent $studio
$workspace  = Split-Path -Parent $csdLibrary
$backend    = Join-Path $studio 'studio-backend'
$frontend   = Join-Path $studio 'studio-frontend'
$py         = Join-Path $backend '.venv\Scripts\python.exe'

Write-Host '== Playbook Studio (native dev) ==' -ForegroundColor Cyan

# --- Resolve and verify the playbook checkout the studio edits ----------------
# Convention: ai-coding-prompts cloned as a sibling of csd-library under one
# workspace. STUDIO_PLAYBOOK_ROOT overrides for non-sibling setups; the spawned
# backend is pinned to whichever path this check validated.
$playbook = $env:STUDIO_PLAYBOOK_ROOT
if ([string]::IsNullOrWhiteSpace($playbook)) {
    $playbook = Join-Path $workspace 'ai-coding-prompts'
}
if (-not (Test-Path (Join-Path $playbook 'AI-PLAYBOOK.md'))) {
    Write-Warning "No playbook checkout found at $playbook."
    Write-Warning 'Clone ai-coding-prompts as a sibling of csd-library (or set STUDIO_PLAYBOOK_ROOT), then re-run.'
    Read-Host 'Press Enter to exit'
    exit 1
}
Write-Host "Playbook checkout -> $playbook" -ForegroundColor Green

# --- First-run setup: backend -------------------------------------------------
if (-not (Test-Path $py)) {
    Write-Host 'First run: creating backend venv and installing deps...'
    python -m venv (Join-Path $backend '.venv')
    & $py -m pip install --quiet -e "$backend"
    $pytestIntent = Join-Path $csdLibrary 'pytest-intent'
    if (Test-Path $pytestIntent) {
        & $py -m pip install --quiet -e $pytestIntent
        & $py -m pip install --quiet pytest
    } else {
        Write-Warning "pytest-intent not found at $pytestIntent; the validation gates will fail until it is installed."
    }
}

# --- First-run setup: frontend -------------------------------------------------
if (-not (Test-Path (Join-Path $frontend 'node_modules'))) {
    Write-Host 'First run: installing frontend deps...'
    Push-Location $frontend
    npm ci
    Pop-Location
}
if (-not (Test-Path (Join-Path $frontend 'src\models\index.ts'))) {
    Write-Host 'First run: generating API types from openapi.json...'
    Push-Location $frontend
    npm run api:generate
    Pop-Location
}

# --- Launch both servers in their own PowerShell windows -----------------------
Write-Host 'Studio backend  -> http://127.0.0.1:8907' -ForegroundColor Green
Start-Process pwsh -ArgumentList '-NoExit', '-Command',
    "`$Host.UI.RawUI.WindowTitle = 'Playbook Studio backend (:8907)'; `$env:PORT='8907'; `$env:STUDIO_PLAYBOOK_ROOT='$playbook'; & '$py' -m studio.adapters.inbound.http.run" `
    -WorkingDirectory $backend

Write-Host 'Studio frontend -> http://localhost:5199' -ForegroundColor Green
Start-Process pwsh -ArgumentList '-NoExit', '-Command',
    "`$Host.UI.RawUI.WindowTitle = 'Playbook Studio frontend (:5199)'; npm run dev -- --port 5199 --strictPort" `
    -WorkingDirectory $frontend

Start-Sleep -Seconds 4
Start-Process 'http://localhost:5199'
Write-Host 'Started. Two PowerShell windows host the servers; close them to stop.' -ForegroundColor Green
