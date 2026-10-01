# Launch ComicRack CE (FBCNN) with script console; tail Artifact Cleaner debug log.
param(
  [switch]$NoKill
)

$ErrorActionPreference = "Stop"
$exe = Join-Path $env:LOCALAPPDATA "ComicRackCE-FBCNN\ComicRack.exe"
$log = Join-Path $env:APPDATA "cYo\ComicRack Community Edition\Scripts\ArtifactCleaner\artifact_cleaner_debug.log"
$iniDir = Join-Path $env:APPDATA "cYo\ComicRack Community Edition"
$ini = Join-Path $iniDir "ComicRack.ini"

New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
New-Item -ItemType Directory -Force -Path $iniDir | Out-Null

$iniBody = @"
; Auto-written by launch-fbcnn-debug.ps1 for Artifact Cleaner debugging
ShowScriptConsole = true
DisableScriptOptimization = true
"@
if (-not (Test-Path $ini) -or -not (Select-String -Path $ini -Pattern '^ShowScriptConsole' -Quiet)) {
  Add-Content -Path $ini -Value $iniBody
  Write-Host "Updated $ini"
}

Set-Content -Path $log -Value "" -Encoding UTF8
Write-Host "Debug log: $log"
Write-Host "Starting: $exe -ssc -dso"
Write-Host "After CE is up: Preferences > Scripts > Artifact Cleaner > Configure (or toolbar Configure...)"

if (-not $NoKill) {
  Get-Process ComicRack -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 1
}

Start-Process -FilePath $exe -ArgumentList @("-ssc", "-dso") -WorkingDirectory (Split-Path $exe)
Write-Host "Tailing log (Ctrl+C stops tail; CE keeps running)"
Get-Content -Path $log -Wait -Tail 50
