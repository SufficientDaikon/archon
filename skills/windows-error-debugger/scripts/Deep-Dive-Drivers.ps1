# Deep-Dive-Drivers.ps1 — Driver health analysis for windows-error-debugger skill
# Identifies problem drivers, recently changed drivers, and third-party kernel modules

param(
    [int]$DaysBack = 30
)

$ErrorActionPreference = 'SilentlyContinue'

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Driver Deep Dive — $(Get-Date -Format 'yyyy-MM-dd HH:mm')" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# --- 1. Problem Devices ---
Write-Host "`n[1/5] DEVICES WITH ERRORS" -ForegroundColor Red
$problems = Get-CimInstance Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 }
if ($problems) {
    foreach ($p in $problems) {
        Write-Host "  ERROR $($p.ConfigManagerErrorCode): $($p.Name)" -ForegroundColor Red
        Write-Host "    DeviceID: $($p.DeviceID)" -ForegroundColor Gray
    }
} else {
    Write-Host "  All devices healthy" -ForegroundColor Green
}

# --- 2. Drivers that failed to start ---
Write-Host "`n[2/5] DRIVER SERVICE FAILURES (last $DaysBack days)" -ForegroundColor Yellow
$driverErrors = Get-WinEvent -FilterHashtable @{LogName='System'; Level=2; StartTime=(Get-Date).AddDays(-$DaysBack)} -MaxEvents 200 |
    Where-Object { $_.Message -match 'driver|service failed to start' }
if ($driverErrors) {
    $grouped = $driverErrors | Group-Object { ($_.Message -split "`n")[0].Substring(0, [Math]::Min(80, ($_.Message -split "`n")[0].Length)) } | Sort-Object Count -Descending
    foreach ($g in $grouped | Select-Object -First 10) {
        Write-Host "  [$($g.Count)x] $($g.Name)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  No driver failures found" -ForegroundColor Green
}

# --- 3. Third-party kernel drivers (loaded now) ---
Write-Host "`n[3/5] THIRD-PARTY KERNEL DRIVERS (loaded)" -ForegroundColor Yellow
$drivers = Get-CimInstance Win32_SystemDriver | Where-Object {
    $_.PathName -and
    $_.PathName -notmatch '\\Windows\\' -and
    $_.PathName -notmatch 'Microsoft'
}
if ($drivers) {
    foreach ($d in $drivers | Sort-Object DisplayName) {
        $status = if ($d.State -eq 'Running') { "Green" } else { "Yellow" }
        Write-Host "  $($d.DisplayName) [$($d.State)]" -ForegroundColor $status
        Write-Host "    Path: $($d.PathName)" -ForegroundColor Gray
    }
} else {
    Write-Host "  No third-party kernel drivers detected" -ForegroundColor Green
}

# --- 4. Recently updated drivers ---
Write-Host "`n[4/5] DRIVER INSTALLS/UPDATES (last $DaysBack days)" -ForegroundColor Yellow
$pnpEvents = Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-Kernel-PnP'; StartTime=(Get-Date).AddDays(-$DaysBack)} -MaxEvents 30
if ($pnpEvents) {
    foreach ($e in $pnpEvents) {
        $msg = $e.Message.Substring(0, [Math]::Min(120, $e.Message.Length))
        Write-Host "  $($e.TimeCreated.ToString('yyyy-MM-dd HH:mm')) $msg" -ForegroundColor Gray
    }
} else {
    Write-Host "  No driver changes in the last $DaysBack days" -ForegroundColor Green
}

# --- 5. Kernel-level software (anti-cheat, AV, hypervisors) ---
Write-Host "`n[5/5] KERNEL-LEVEL SOFTWARE" -ForegroundColor Yellow
$kernelSoftware = @(
    @{Name='Riot Vanguard (vgc)'; Service='vgc'},
    @{Name='EasyAntiCheat'; Service='EasyAntiCheat'},
    @{Name='BattlEye'; Service='BEService'},
    @{Name='Kaspersky'; Service='klvssbrigde64'},
    @{Name='Kaspersky AVP'; Service='AVP'},
    @{Name='Hyper-V'; Service='vmms'},
    @{Name='Docker/HCS'; Service='HvHost'},
    @{Name='VirtualBox'; Service='VBoxDrv'},
    @{Name='VMware'; Service='vmware-authd'}
)
foreach ($ks in $kernelSoftware) {
    $svc = Get-Service -Name $ks.Service -EA SilentlyContinue
    if ($svc) {
        $color = if ($svc.Status -eq 'Running') { "Yellow" } else { "Gray" }
        Write-Host "  $($ks.Name): $($svc.Status) (StartType: $($svc.StartType))" -ForegroundColor $color
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Driver analysis complete." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
