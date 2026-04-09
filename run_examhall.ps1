param()
# Handle callers that wrap the script path in extra quotes (single or double)
$rawDef = $MyInvocation.MyCommand.Definition
$rawDef = $rawDef.Trim("'\"")
$scriptDir = Split-Path -Parent $rawDef

function Test-IsAdmin {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    (New-Object Security.Principal.WindowsPrincipal($current)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-IsAdmin)) {
    Write-Output 'Not running as Administrator - relaunching with elevation to apply firewall rule and start server. You may be prompted.'
    Start-Process -FilePath 'powershell' -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',$rawDef -Verb RunAs
    exit
}

Write-Output "Running elevated. Ensuring firewall rule for port 8000..."
try {
    New-NetFirewallRule -DisplayName "Examhall Django" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000 -ErrorAction Stop
    Write-Output "Firewall rule created or already present."
} catch {
    Write-Output "Could not create firewall rule or it already exists: $_"
}

# Activate (or create) virtualenv
$venvDir = $null
if (Test-Path (Join-Path $scriptDir "venv\Scripts\Activate.ps1")) {
    $venvDir = "venv"
} elseif (Test-Path (Join-Path $scriptDir ".venv\Scripts\Activate.ps1")) {
    $venvDir = ".venv"
} else {
    $venvDir = "venv"
}

$venvActivate = Join-Path $scriptDir "$venvDir\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Output "Activating virtualenv..."
    . $venvActivate
} else {
    Write-Output "Virtualenv not found. Creating $venvDir and installing requirements (this may take a while)..."
    python -m venv (Join-Path $scriptDir $venvDir)
    . $venvActivate
    python -m pip install --upgrade pip
    if (Test-Path (Join-Path $scriptDir 'requirements_clean.txt')) {
        python -m pip install -r (Join-Path $scriptDir 'requirements_clean.txt')
    } elseif (Test-Path (Join-Path $scriptDir 'requirements.txt')) {
        python -m pip install -r (Join-Path $scriptDir 'requirements.txt')
    }
}

Write-Output "Starting Django development server on 0.0.0.0:8000"
Set-Location $scriptDir
python manage.py runserver 0.0.0.0:8000
