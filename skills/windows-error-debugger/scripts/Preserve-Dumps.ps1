# Ensure minidumps are configured and preserved
# Run as Administrator

Write-Host "=== Configuring Crash Dump Settings ===" -ForegroundColor Cyan

# Ensure small memory dumps (minidumps) are enabled
$crashKey = 'HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl'
$currentType = (Get-ItemProperty -Path $crashKey -Name 'CrashDumpEnabled' -EA SilentlyContinue).CrashDumpEnabled

Write-Host "Current dump type: $currentType (1=Complete, 2=Kernel, 3=Small/Mini, 7=Automatic)"

# Set to Automatic (7) if not already — Windows picks the best dump type
if ($currentType -ne 7 -and $currentType -ne 1) {
    Set-ItemProperty -Path $crashKey -Name 'CrashDumpEnabled' -Value 7 -Type DWord -Force
    Write-Host "  Changed to Automatic (7)" -ForegroundColor Green
} else {
    Write-Host "  Already set to good value" -ForegroundColor Green
}

# Ensure minidump directory exists
$miniDir = 'C:\WINDOWS\Minidump'
if (-not (Test-Path $miniDir)) {
    New-Item -Path $miniDir -ItemType Directory -Force | Out-Null
    Write-Host "  Created $miniDir" -ForegroundColor Green
}
Set-ItemProperty -Path $crashKey -Name 'MinidumpDir' -Value $miniDir -Type ExpandString -Force
Write-Host "  Minidump dir: $miniDir" -ForegroundColor Green

# Ensure overwrite is OFF so we keep all dumps
Set-ItemProperty -Path $crashKey -Name 'Overwrite' -Value 0 -Type DWord -Force
Write-Host "  Overwrite: disabled (keep all dumps)" -ForegroundColor Green

# Check if Disk Cleanup or a third-party tool is deleting dumps
Write-Host "`n=== Checking for dump cleanup culprits ===" -ForegroundColor Yellow
$cleanMgr = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\*' -EA SilentlyContinue |
    Where-Object { $_.PSChildName -match 'Dump|Error' }
if ($cleanMgr) {
    foreach ($c in $cleanMgr) {
        Write-Host "  Found cleanup entry: $($c.PSChildName)" -ForegroundColor Yellow
    }
    Write-Host "  Note: Disk Cleanup may remove dump files. Disable 'System error memory dump files' in Disk Cleanup settings." -ForegroundColor Yellow
} else {
    Write-Host "  No dump cleanup entries found in Disk Cleanup config" -ForegroundColor Green
}

Write-Host "`nDone. Future crashes will generate minidumps in $miniDir" -ForegroundColor Cyan
Write-Host "Tip: If a crash occurs, immediately back up C:\WINDOWS\Minidump\ before running any cleanup tools." -ForegroundColor Cyan
