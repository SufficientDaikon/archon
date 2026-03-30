# Backup-RegistryKey.ps1
# Exports a registry key to a timestamped .reg file
param(
    [Parameter(Mandatory=$true)]
    [string]$KeyPath,

    [string]$BackupDir = 'H:\windows\RegistryBackups',

    [string]$Description = 'manual'
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $BackupDir)) { New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null }

# Convert PowerShell path to reg.exe path
$regPath = $KeyPath -replace '^HKLM:\\', 'HKLM\' -replace '^HKCU:\\', 'HKCU\' -replace '^HKCR:\\', 'HKCR\' -replace '^HKU:\\', 'HKU\' -replace '^HKCC:\\', 'HKCC\'

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$safeName = ($Description -replace '[\\/:*?"<>|\s]', '_')
$backupFile = Join-Path $BackupDir "backup_${timestamp}_${safeName}.reg"

Write-Host "Backing up: $regPath" -ForegroundColor Cyan
Write-Host "To: $backupFile" -ForegroundColor DarkGray

$result = reg export $regPath $backupFile /y 2>&1
if ($LASTEXITCODE -eq 0) {
    $size = (Get-Item $backupFile).Length
    Write-Host "Success! Backup size: $([math]::Round($size/1KB, 1)) KB" -ForegroundColor Green
    Write-Output $backupFile
} else {
    Write-Host "Failed: $result" -ForegroundColor Red
    exit 1
}
