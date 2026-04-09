function Test-IsAdmin {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    return (New-Object Security.Principal.WindowsPrincipal($current)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath

if (-not (Test-IsAdmin)) {
    Write-Output 'Requesting elevation...'
    Start-Process -FilePath 'powershell' -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$scriptPath) -Verb RunAs
    exit
}

Write-Output 'Running elevated. Creating firewall rule for port 8000 (if missing)...'
try {
    $rule = Get-NetFirewallRule -DisplayName 'Examhall Django' -ErrorAction SilentlyContinue
    if (-not $rule) {
        New-NetFirewallRule -DisplayName 'Examhall Django' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000 -Profile Any | Out-Null
        Write-Output 'Firewall rule created.'
    } else {
        Write-Output 'Firewall rule already exists.'
    }
} catch {
    Write-Output "Firewall rule creation failed: $($_.Exception.Message)"
}

Set-Location $scriptDir

$venvPython = $null
if (Test-Path (Join-Path $scriptDir 'venv\Scripts\python.exe')) {
    $venvPython = Join-Path $scriptDir 'venv\Scripts\python.exe'
} elseif (Test-Path (Join-Path $scriptDir '.venv\Scripts\python.exe')) {
    $venvPython = Join-Path $scriptDir '.venv\Scripts\python.exe'
} else {
    $venvPython = Join-Path $scriptDir 'venv\Scripts\python.exe'
    Write-Output 'Virtualenv not found; creating venv...'
    python -m venv (Join-Path $scriptDir 'venv')
    & $venvPython -m pip install --upgrade pip
    if (Test-Path (Join-Path $scriptDir 'requirements_clean.txt')) {
        & $venvPython -m pip install -r (Join-Path $scriptDir 'requirements_clean.txt')
    } elseif (Test-Path (Join-Path $scriptDir 'requirements.txt')) {
        & $venvPython -m pip install -r (Join-Path $scriptDir 'requirements.txt')
    }
}

Write-Output 'Starting Django dev server on 0.0.0.0:8000...'
Write-Output 'Server URL(s):'
try {
    $ips = Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.*' } |
        Select-Object -ExpandProperty IPAddress
    foreach ($ip in $ips) {
        Write-Output "http://$ip`:8000"
    }
} catch {
    Write-Output 'Could not enumerate IPs.'
}

& $venvPython manage.py runserver 0.0.0.0:8000
