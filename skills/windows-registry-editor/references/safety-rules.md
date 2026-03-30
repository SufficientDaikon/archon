# Registry Safety Rules

## BLOCKED Keys - NEVER Modify

These keys can brick the system. Do not write to them under any circumstances, even if the user asks. Explain the risk and refuse.

### Boot / Recovery
- `HKLM:\BCD00000000` - Boot Configuration Data
- `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\BootExecute` - Boot-time programs
- `HKLM:\SYSTEM\Setup` - Windows Setup state

### Security / Authentication Core
- `HKLM:\SAM` - Security Account Manager (password hashes)
- `HKLM:\SECURITY` - LSA secrets, cached credentials
- `HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\*` (core LSA keys only — subkeys like `RunAsPPL` are WARN level)

### Critical System Integrity
- `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\SubSystems` - Subsystem definitions (csrss)
- `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment\ComSpec` - Command processor path
- `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment\Path` - System PATH (delete = unbootable)
- `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs` - DLL injection vector (malware target)
- `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options` - Debugger hijacking vector
- `HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl` - Blue screen dump settings (leave alone)

### Driver Core
- `HKLM:\SYSTEM\CurrentControlSet\Services\*\ImagePath` - Service/driver executable paths (changing = BSOD)
- `HKLM:\SYSTEM\CurrentControlSet\Services\*\Start` for boot-critical drivers (Type 0x01 = kernel driver)

## WARN Keys - Require User Confirmation

These are powerful but legitimate optimization targets. Always explain what the change does and ask for confirmation before modifying.

### Session Manager / Memory
- `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\*` - Memory tuning
- `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters\*` - Prefetch/Superfetch

### Services (Start Type)
- `HKLM:\SYSTEM\CurrentControlSet\Services\*\Start` - Changing service start types (non-driver services only)
- Any service the user didn't explicitly name

### Authentication / Security Settings
- `HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\RunAsPPL` - Protected Process Light
- `HKLM:\SOFTWARE\Policies\Microsoft\Windows\*` - Group Policy overrides
- `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\*` - System policies

### Network Core
- `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\*` - Per-interface TCP (safe values, but verify interface GUID)
- `HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\*` - DNS cache behavior

### User Shell
- `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` - Startup programs
- `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` - System startup programs
- `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\*` - Shell behavior

## SAFE Keys - Modify Freely

These are standard optimization targets that are well-documented and safe to change.

### Network Optimization
- `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\*` - MMCSS / throttling
- `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` - Global TCP settings (DefaultTTL, SackOpts, etc.)
- `HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters` - Winsock buffer sizes
- `HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched` - QoS bandwidth reservation
- `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings` - WinINet connections
- `HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters` - SMB client tuning

### Gaming / GPU
- `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\*` - MMCSS task priorities
- `HKCU:\SOFTWARE\Microsoft\DirectX\UserGpuPreferences` - Per-app GPU preference
- `HKLM:\SOFTWARE\Microsoft\DirectX\*` - DirectX settings

### Privacy / Telemetry
- `HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection` - Telemetry level
- `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo` - Advertising ID
- `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy` - Privacy settings
- `HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent` - Suggested content / tips
- `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager` - Suggested apps

### Performance
- `HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl` - Process priority separation
- `HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling` - Power throttling

### Visual / UI
- `HKCU:\Control Panel\Desktop` - Visual effects, menu delay
- `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects` - Animation settings
- `HKCU:\SOFTWARE\Microsoft\Windows\DWM` - Desktop Window Manager

## Validation Function

Use this before any write operation:

```powershell
function Test-RegistrySafety {
    param([string]$Path, [string]$ValueName)

    $blocked = @(
        'HKLM:\BCD00000000',
        'HKLM:\SAM',
        'HKLM:\SECURITY',
        'HKLM:\SYSTEM\Setup',
        'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\SubSystems',
        'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\BootExecute',
        'HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl'
    )

    $blockedValues = @(
        'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows|AppInit_DLLs',
        'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment|ComSpec',
        'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment|Path'
    )

    foreach ($b in $blocked) {
        if ($Path -like "$b*") { return 'BLOCKED' }
    }

    foreach ($bv in $blockedValues) {
        $parts = $bv -split '\|'
        if ($Path -eq $parts[0] -and $ValueName -eq $parts[1]) { return 'BLOCKED' }
    }

    if ($Path -match 'Image File Execution Options') { return 'BLOCKED' }
    if ($Path -match '\\Services\\.*\\ImagePath$') { return 'BLOCKED' }

    $warn = @(
        'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management',
        'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa',
        'HKLM:\SOFTWARE\Policies\Microsoft\Windows',
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        'HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache'
    )

    foreach ($w in $warn) {
        if ($Path -like "$w*") { return 'WARN' }
    }

    return 'SAFE'
}
```
