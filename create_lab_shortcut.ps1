$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "ExamHall.lnk"
$targetPath = Join-Path $projectRoot "launch_lab.bat"

if (-not (Test-Path $targetPath)) {
    throw "launch_lab.bat not found at $targetPath"
}

$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $projectRoot
$shortcut.WindowStyle = 1

$iconCandidate1 = Join-Path $projectRoot "allocation\static\allocation\images\college_logo.ico"
$iconCandidate2 = Join-Path $projectRoot "allocation\static\allocation\images\college_logo.png"

if (Test-Path $iconCandidate1) {
    $shortcut.IconLocation = $iconCandidate1
} elseif (Test-Path $iconCandidate2) {
    $shortcut.IconLocation = "$iconCandidate2,0"
}

$shortcut.Description = "Academic Management System"
$shortcut.Save()

Write-Host "Desktop shortcut created: $shortcutPath"
