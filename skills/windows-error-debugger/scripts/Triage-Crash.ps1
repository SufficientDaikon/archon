# Triage-Crash.ps1 — Quick crash triage for windows-error-debugger skill
# Collects all relevant crash data in one pass and outputs a structured summary

param(
    [int]$DaysBack = 7,
    [string]$ReportDir = "H:\windows"
)

$ErrorActionPreference = 'SilentlyContinue'

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Windows Crash Triage — $(Get-Date -Format 'yyyy-MM-dd HH:mm')" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# --- 1. System Info ---
Write-Host "`n[1/8] SYSTEM INFO" -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor
$gpu = Get-CimInstance Win32_VideoController
$board = Get-CimInstance Win32_BaseBoard
Write-Host "  OS:    $($os.Caption) Build $($os.BuildNumber)"
Write-Host "  CPU:   $($cpu.Name.Trim()) ($($cpu.NumberOfCores)C/$($cpu.NumberOfLogicalProcessors)T)"
Write-Host "  GPU:   $($gpu.Name) (driver $($gpu.DriverVersion))"
Write-Host "  Board: $($board.Manufacturer) $($board.Product)"
$totalRAM = [math]::Round($os.TotalVisibleMemorySize/1MB, 1)
$freeRAM = [math]::Round($os.FreePhysicalMemory/1MB, 1)
Write-Host "  RAM:   ${freeRAM}GB free / ${totalRAM}GB total ($([math]::Round((1 - $os.FreePhysicalMemory/$os.TotalVisibleMemorySize)*100,0))% used)"
Write-Host "  Boot:  $($os.LastBootUpTime)"

# --- 2. Disk Space ---
Write-Host "`n[2/8] DISK SPACE" -ForegroundColor Yellow
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $usedPct = [math]::Round((1 - $_.FreeSpace/$_.Size)*100,0)
    $freeGB = [math]::Round($_.FreeSpace/1GB, 1)
    $totalGB = [math]::Round($_.Size/1GB, 1)
    $color = if ($usedPct -ge 90) { "Red" } elseif ($usedPct -ge 80) { "Yellow" } else { "Green" }
    Write-Host "  $($_.DeviceID) ${freeGB}GB free / ${totalGB}GB ($usedPct% used)" -ForegroundColor $color
}

# --- 3. Page File ---
Write-Host "`n[3/8] PAGE FILE" -ForegroundColor Yellow
Get-CimInstance Win32_PageFileUsage | ForEach-Object {
    Write-Host "  $($_.Name): $($_.AllocatedBaseSize)MB allocated, $($_.CurrentUsage)MB used, peak $($_.PeakUsage)MB"
}

# --- 4. BSOD / Bugcheck Events ---
Write-Host "`n[4/8] BSOD HISTORY" -ForegroundColor Red
$bsods = Get-WinEvent -FilterHashtable @{LogName='System'; Id=1001; ProviderName='Microsoft-Windows-WER-SystemErrorReporting'} -MaxEvents 10
if ($bsods) {
    foreach ($e in $bsods) {
        $match = [regex]::Match($e.Message, '0x[0-9a-fA-F]+')
        $code = if ($match.Success) { $match.Value } else { "unknown" }
        Write-Host "  $($e.TimeCreated.ToString('yyyy-MM-dd HH:mm')) — Bugcheck $code" -ForegroundColor Red
    }
} else {
    Write-Host "  No BSOD events found" -ForegroundColor Green
}

# --- 5. Unexpected Shutdowns ---
Write-Host "`n[5/8] UNEXPECTED SHUTDOWNS" -ForegroundColor Yellow
$shutdowns = Get-WinEvent -FilterHashtable @{LogName='System'; Id=6008} -MaxEvents 10
if ($shutdowns) {
    foreach ($e in $shutdowns) {
        Write-Host "  $($e.TimeCreated.ToString('yyyy-MM-dd HH:mm')) — $($e.Message.Substring(0, [Math]::Min(100, $e.Message.Length)))"
    }
} else {
    Write-Host "  No unexpected shutdowns found" -ForegroundColor Green
}

# --- 6. Critical/Error Events (last N days) ---
Write-Host "`n[6/8] CRITICAL & ERROR EVENTS (last $DaysBack days)" -ForegroundColor Yellow
$errors = Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddDays(-$DaysBack)} -MaxEvents 30
if ($errors) {
    $grouped = $errors | Group-Object ProviderName | Sort-Object Count -Descending
    foreach ($g in $grouped) {
        Write-Host "  $($g.Name): $($g.Count) events" -ForegroundColor $(if ($g.Count -ge 5) { "Red" } else { "Yellow" })
        $g.Group | Select-Object -First 2 | ForEach-Object {
            $msg = $_.Message.Substring(0, [Math]::Min(100, $_.Message.Length))
            Write-Host "    $($_.TimeCreated.ToString('MM-dd HH:mm')) $msg" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  No critical/error events" -ForegroundColor Green
}

# --- 7. Failing Services ---
Write-Host "`n[7/8] FAILING AUTO-START SERVICES" -ForegroundColor Yellow
$failedSvc = Get-Service | Where-Object { $_.StartType -eq 'Automatic' -and $_.Status -ne 'Running' }
if ($failedSvc) {
    foreach ($s in $failedSvc) {
        Write-Host "  $($s.Name) — $($s.DisplayName) [$($s.Status)]" -ForegroundColor Yellow
    }
} else {
    Write-Host "  All auto-start services running" -ForegroundColor Green
}

# --- 8. Minidumps ---
Write-Host "`n[8/8] MINIDUMP FILES" -ForegroundColor Yellow
$dumps = Get-ChildItem "C:\WINDOWS\Minidump\*.dmp" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($dumps) {
    foreach ($d in $dumps | Select-Object -First 5) {
        Write-Host "  $($d.Name) — $([math]::Round($d.Length/1KB,0))KB — $($d.LastWriteTime)"
    }
} else {
    Write-Host "  No minidump files found" -ForegroundColor Gray
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Triage complete. Review findings above." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
