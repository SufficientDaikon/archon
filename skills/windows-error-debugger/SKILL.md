---
name: windows-error-debugger
description: >
  Diagnose, debug, and fix Windows crashes, BSODs, driver failures, and system errors via PowerShell.
  Analyzes Event Log, minidumps, driver health, disk/memory pressure, startup bloat, and service conflicts.
  Builds a growing knowledge base of resolved issues per machine. Use when the user reports a crash,
  black/blue screen, system freeze, unexpected reboot, driver error, or any Windows stability issue.
  Also triggers for "BSOD", "blue screen", "black screen", "crash", "system error", "bugcheck",
  "minidump", "driver failure", "unexpected shutdown", "paging file too small", "system hang",
  "Windows froze", "PC crashed", "kernel error", or any mention of Windows Event Log errors.
---

# Windows Error Debugger

Systematic Windows crash investigation and repair. Every debug session follows a structured pipeline,
saves its findings to a growing knowledge base, and produces actionable fix scripts the user can review.

## Prerequisites

- Windows 10/11
- PowerShell access (admin/elevated for full diagnostics)
- Reports directory: `$HOME\windows-debug\`
- Knowledge base: this skill's `knowledge-base/` folder (grows across sessions)

## When to Use

- User reports PC crash, freeze, black screen, blue screen, or unexpected reboot
- User asks to investigate Event Log errors or system instability
- User wants to prevent future crashes
- User asks "why did my PC crash?"
- User reports driver errors, service failures, or "paging file too small"
- After a Windows Update causes issues

## When NOT to Use

- Network-only issues → use `windows-network-optimizer`
- Pure registry tweaks → use `windows-registry-editor`
- Hardware failure diagnostics (bad RAM sticks, dead drives) → recommend memtest86 / CrystalDiskInfo

## Core Principles

1. **Investigate before fixing.** Never apply fixes without understanding the root cause.
2. **Read the knowledge base first.** Check `knowledge-base/resolved-issues.md` for patterns already seen on this machine. Don't re-diagnose known issues.
3. **Save everything.** Every diagnostic run and fix attempt gets logged to `H:\windows/`.
4. **Scripts are reviewable.** Write fix scripts to `H:\windows/`, explain what they do, let the user review before executing.
5. **Grow the knowledge base.** After resolving an issue, append it to `knowledge-base/resolved-issues.md` with root cause, fix applied, and date.

## Phase 1: Triage (always start here)

Determine crash type and severity by querying the Event Log.

Run the triage script:
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File "[skill-root]/scripts\Triage-Crash.ps1"
```

Or run inline:
```powershell
# 1. Last unexpected shutdown
Get-WinEvent -FilterHashtable @{LogName='System'; Id=6008} -MaxEvents 5 -EA SilentlyContinue |
    Select-Object TimeCreated, Message | Format-List

# 2. BSOD / bugcheck events
Get-WinEvent -FilterHashtable @{LogName='System'; Id=1001; ProviderName='Microsoft-Windows-WER-SystemErrorReporting'} -MaxEvents 5 -EA SilentlyContinue |
    Select-Object TimeCreated, Message | Format-List

# 3. Critical kernel power events (forced reboots)
Get-WinEvent -FilterHashtable @{LogName='System'; Id=41; ProviderName='Microsoft-Windows-Kernel-Power'} -MaxEvents 5 -EA SilentlyContinue |
    Select-Object TimeCreated, Message | Format-List

# 4. Driver crashes and service failures (last 7 days)
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddDays(-7)} -MaxEvents 50 -EA SilentlyContinue |
    Select-Object TimeCreated, ProviderName, @{N='Msg';E={$_.Message.Substring(0, [Math]::Min(150, $_.Message.Length))}} |
    Format-Table -AutoSize -Wrap

# 5. Application crashes
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=1,2; StartTime=(Get-Date).AddDays(-7)} -MaxEvents 20 -EA SilentlyContinue |
    Select-Object TimeCreated, ProviderName, @{N='Msg';E={$_.Message.Substring(0, [Math]::Min(150, $_.Message.Length))}} |
    Format-Table -AutoSize -Wrap

# 6. Minidump files
Get-ChildItem "C:\WINDOWS\Minidump\" -EA SilentlyContinue |
    Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

# 7. System uptime
$os = Get-CimInstance Win32_OperatingSystem
Write-Host "Last boot: $($os.LastBootUpTime)"
Write-Host "Uptime: $([math]::Round(((Get-Date) - $os.LastBootUpTime).TotalHours, 1)) hours"
```

### Bugcheck Code Reference

After extracting the bugcheck code from Event ID 1001, look it up:

| Code | Name | Common Cause |
|------|------|-------------|
| 0x0000003B | SYSTEM_SERVICE_EXCEPTION | Faulty driver, corrupted system file, AV conflict |
| 0x0000009F | DRIVER_POWER_STATE_FAILURE | Driver can't handle sleep/wake — usually WiFi or GPU |
| 0x00000050 | PAGE_FAULT_IN_NONPAGED_AREA | Bad RAM, driver accessing freed memory, disk corruption |
| 0x0000007E | SYSTEM_THREAD_EXCEPTION_NOT_HANDLED | Driver crash during thread execution |
| 0x0000007F | UNEXPECTED_KERNEL_MODE_TRAP | Hardware failure, overheating, driver stack overflow |
| 0x000000D1 | DRIVER_IRQL_NOT_LESS_OR_EQUAL | Driver accessing memory at wrong IRQL — faulty driver |
| 0x000000EF | CRITICAL_PROCESS_DIED | Essential process (csrss, wininit) terminated |
| 0x00000116 | VIDEO_TGI_TIMEOUT_DETECTED | GPU driver hung and didn't recover |
| 0x00000124 | WHEA_UNCORRECTABLE_ERROR | Hardware error — CPU, RAM, or motherboard issue |
| 0x0000013A | KERNEL_MODE_HEAP_CORRUPTION | Kernel memory corruption — usually driver bug |
| 0x000001CA | SYNTHETIC_WATCHDOG_TIMEOUT | Hyper-V watchdog fired — VM or hypervisor issue |
| 0xC000021A | STATUS_SYSTEM_PROCESS_TERMINATED | Winlogon or CSRSS crashed |

## Phase 2: Deep Dive

Based on triage results, run targeted diagnostics.

### 2a. Driver Health Check

```powershell
# Problem drivers (unsigned, stopped, errored)
Get-CimInstance Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 } |
    Select-Object Name, DeviceID, ConfigManagerErrorCode | Format-Table -AutoSize -Wrap

# Recently installed/updated drivers
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-Kernel-PnP'; StartTime=(Get-Date).AddDays(-30)} -MaxEvents 20 -EA SilentlyContinue |
    Select-Object TimeCreated, @{N='Msg';E={$_.Message.Substring(0, [Math]::Min(120, $_.Message.Length))}} |
    Format-Table -AutoSize -Wrap

# Third-party kernel drivers loaded
driverquery /v | findstr /i /v "Microsoft Windows"
```

### 2b. Resource Pressure Check

```powershell
# RAM usage
$os = Get-CimInstance Win32_OperatingSystem
$totalGB = [math]::Round($os.TotalVisibleMemorySize/1MB, 1)
$freeGB = [math]::Round($os.FreePhysicalMemory/1MB, 1)
$usedPct = [math]::Round((1 - $os.FreePhysicalMemory/$os.TotalVisibleMemorySize) * 100, 0)
Write-Host "RAM: ${freeGB}GB free / ${totalGB}GB total (${usedPct}% used)"

# Page file
Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage, PeakUsage | Format-List

# Disk space (all drives)
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" |
    Select-Object DeviceID,
        @{N='SizeGB';E={[math]::Round($_.Size/1GB,1)}},
        @{N='FreeGB';E={[math]::Round($_.FreeSpace/1GB,1)}},
        @{N='UsedPct';E={[math]::Round((1-$_.FreeSpace/$_.Size)*100,0)}} |
    Format-Table -AutoSize

# Top memory consumers
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 15 Name,
    @{N='MemMB';E={[math]::Round($_.WorkingSet64/1MB,0)}},
    @{N='CPU_s';E={[math]::Round($_.CPU,1)}} |
    Format-Table -AutoSize
```

### 2c. Startup & Service Audit

```powershell
# Startup programs
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Format-Table -AutoSize -Wrap

# Failing auto-start services
Get-Service | Where-Object { $_.StartType -eq 'Automatic' -and $_.Status -ne 'Running' } |
    Select-Object Name, DisplayName, Status | Format-Table -AutoSize -Wrap

# Services that crashed recently
Get-WinEvent -FilterHashtable @{LogName='System'; Id=7031,7034; StartTime=(Get-Date).AddDays(-7)} -MaxEvents 20 -EA SilentlyContinue |
    Select-Object TimeCreated, @{N='Msg';E={$_.Message.Substring(0, [Math]::Min(120, $_.Message.Length))}} |
    Format-Table -AutoSize -Wrap
```

### 2d. Hardware Info

```powershell
# CPU (check core count matches spec)
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | Format-List

# GPU
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate, Status | Format-List

# Motherboard
Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, Version | Format-List

# BIOS
Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate | Format-List

# RAM sticks
Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel, Capacity, Speed, Manufacturer | Format-Table -AutoSize
```

### 2e. System File Integrity

```powershell
# Check for corruption (requires admin)
sfc /scannow

# If SFC finds issues, repair the Windows image first:
DISM /Online /Cleanup-Image /RestoreHealth

# Then re-run SFC
sfc /scannow
```

### 2f. Minidump Analysis (if available)

Windows doesn't ship with WinDbg by default. Check if debugging tools are available:

```powershell
# Check for WinDbg / kd
$debuggers = @(
    "${env:ProgramFiles(x86)}\Windows Kits\10\Debuggers\x64\kd.exe",
    "${env:ProgramFiles}\Windows Kits\10\Debuggers\x64\kd.exe",
    (Get-Command kd.exe -EA SilentlyContinue).Source
) | Where-Object { $_ -and (Test-Path $_) }

if ($debuggers) {
    $kd = $debuggers[0]
    # Analyze most recent minidump
    $dump = Get-ChildItem C:\WINDOWS\Minidump\*.dmp -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($dump) {
        & $kd -z $dump.FullName -c "!analyze -v; q" 2>&1
    }
} else {
    Write-Host "WinDbg/kd not found. Install Windows SDK debugging tools or use:"
    Write-Host "  winget install Microsoft.WinDbg"
    Write-Host ""
    Write-Host "Alternative: Read minidump header for basic info"
    $dump = Get-ChildItem C:\WINDOWS\Minidump\*.dmp -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($dump) {
        Write-Host "Latest dump: $($dump.FullName) ($([math]::Round($dump.Length/1KB,0)) KB, $($dump.LastWriteTime))"
        # Read first bytes to identify dump type
        $bytes = [System.IO.File]::ReadAllBytes($dump.FullName)
        $sig = [System.Text.Encoding]::ASCII.GetString($bytes[0..3])
        Write-Host "Signature: $sig (MDMP = valid minidump)"
    }
}
```

## Phase 3: Diagnose

After gathering data, correlate findings to identify root cause(s). Consider:

1. **Timeline correlation** — Did the crash happen right after a driver update, Windows Update, or new software install?
2. **Bugcheck pattern** — Same code repeating? Different codes = multiple issues.
3. **Resource exhaustion** — Was disk/RAM/page file under pressure before the crash?
4. **Driver conflicts** — Broken drivers, kernel-level software (anti-cheat, AV), or orphaned services.

## Phase 4: Fix

Write fix scripts to `$HOME\windows-debug\` with clear names and comments. Each script should:

1. Explain what it fixes and why
2. Be safe to review before execution
3. Create backups/restore points where applicable
4. Be idempotent (safe to run multiple times)

Common fix patterns:

```powershell
# Disable a broken service
Set-Service -Name "ServiceName" -StartupType Disabled
Stop-Service -Name "ServiceName" -Force -EA SilentlyContinue

# Disable a startup program (via registry)
Remove-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'ProgramName' -EA SilentlyContinue

# Disable USB/WiFi power management (prevents 0x9F crashes)
$adapter = Get-NetAdapter -Name "Wi-Fi" -EA SilentlyContinue
if ($adapter) {
    powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_NONE CONNECTIVITYINSTANDBY 1
    # Disable selective suspend
    $key = "HKLM:\SYSTEM\CurrentControlSet\Services\$($adapter.InterfaceDescription -replace '\s','_')\Parameters"
    # Each WiFi driver has different power management registry keys
}

# Clean temp files
Remove-Item "$env:TEMP\*" -Recurse -Force -EA SilentlyContinue
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -EA SilentlyContinue
```

## Phase 5: Verify & Report

1. Re-run the triage script to confirm errors are resolved
2. Save a report to `$HOME\windows-debug\CRASH_REPORT.md` with:
   - System info (CPU, RAM, GPU, drives)
   - Crash timeline and bugcheck codes
   - Root cause analysis
   - Fixes applied (with script file references)
   - Remaining issues / recommendations
3. Update the knowledge base (see below)

## Knowledge Base Management

The skill maintains a growing knowledge base at:
`[skill-root]/knowledge-base\`

### Files

| File | Purpose |
|------|---------|
| `resolved-issues.md` | Log of all diagnosed and fixed issues with dates |
| `machine-profile.md` | Hardware/software profile of this machine |
| `driver-watchlist.md` | Drivers known to cause issues, with versions to avoid |
| `recurring-patterns.md` | Patterns that keep showing up across sessions |

### Adding a Resolved Issue

After fixing something, append to `knowledge-base/resolved-issues.md`:

```markdown
## [DATE] — Brief title
- **Bugcheck / Error:** code or event description
- **Root cause:** what actually caused it
- **Fix applied:** what was done (link to fix script)
- **Verified:** yes/no
- **Notes:** any additional context
```

### Checking Known Issues

**ALWAYS read `knowledge-base/resolved-issues.md` at the start of a debug session.**
If the current error matches a known pattern, reference the previous fix instead of re-investigating.

## Hardware Profile (This Machine)

Read `knowledge-base/machine-profile.md` for specs. Update it when hardware changes are detected.

## Useful External Tools (recommend when needed)

| Tool | Purpose | How to Get |
|------|---------|-----------|
| WinDbg | Minidump analysis | `winget install Microsoft.WinDbg` |
| CrystalDiskInfo | Disk health (SMART) | `winget install CrystalDewWorld.CrystalDiskInfo` |
| HWiNFO64 | Temperatures, voltages, sensors | `winget install REALiX.HWiNFO` |
| memtest86 | RAM reliability test | Boot from USB — https://memtest86.com |
| BlueScreenView | Visual minidump viewer | nirsoft.net/utils/blue_screen_view.html |
| WhoCrashed | Automated crash analysis | https://www.resplendence.com/whocrashed |
| DriverView | List all loaded drivers | nirsoft.net/utils/driverview.html |
