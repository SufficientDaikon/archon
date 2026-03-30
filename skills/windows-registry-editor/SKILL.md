---
name: windows-registry-editor
description: >
  Expert Windows Registry editor and optimizer via PowerShell. Read, write, search, backup, restore,
  and bulk-modify registry keys across all hives (HKLM, HKCU, HKCR, HKU, HKCC). Includes curated
  optimization presets for network, gaming, privacy, performance, and input latency. Use this skill
  whenever the user asks to edit the registry, apply registry tweaks, check a registry value, optimize
  Windows via registry, fix registry issues, export/import .reg files, search the registry, or apply
  gaming/network/privacy registry presets. Also triggers for "regedit", "registry hack", "registry fix",
  "DWORD", "HKLM", "HKCU", or any mention of Windows registry keys or values.
---

# Windows Registry Editor & Optimizer

A comprehensive, safety-first registry management skill. Every modification is backed up before changes, dangerous keys are protected, and all operations go through PowerShell for scriptability and auditability.

## Prerequisites

- Windows 10/11
- Admin/elevated PowerShell access
- Use `mcp__Windows-MCP__PowerShell` tool for all commands

## Core Principles

1. **Backup before every write.** Before modifying any key, export it with `reg export` to a timestamped .reg file in the backup directory.
2. **Never touch protected keys** without explicit user confirmation. See `references/safety-rules.md` for the full blocklist.
3. **Validate types.** Registry values have strict types (REG_DWORD, REG_SZ, REG_EXPAND_SZ, REG_MULTI_SZ, REG_BINARY, REG_QWORD). Always specify the correct `-Type` parameter.
4. **Explain what each change does** before applying it. Users deserve to understand what's happening to their system.

## Backup Directory

All backups go to `$HOME\windows-debug\RegistryBackups\`. Create it if it doesn't exist.

```powershell
$backupDir = '$HOME\windows-debug\RegistryBackups'
if (-not (Test-Path $backupDir)) { New-Item -Path $backupDir -ItemType Directory -Force | Out-Null }
```

## Operations Reference

### 1. Read / Query

```powershell
# Read all values under a key
Get-ItemProperty -Path 'HKLM:\path\to\key'

# Read a specific value
Get-ItemPropertyValue -Path 'HKLM:\path\to\key' -Name 'ValueName'

# List subkeys
Get-ChildItem -Path 'HKLM:\path\to\key'

# Check if a key exists
Test-Path -Path 'HKLM:\path\to\key'

# Check if a specific value exists
$null -ne (Get-ItemProperty -Path 'HKLM:\path\to\key' -Name 'ValueName' -EA SilentlyContinue)
```

### 2. Backup / Export

Always run before any modification. Use `reg export` for human-readable .reg files.

```powershell
# Export a specific key (recursive) to .reg file
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupFile = "$backupDir\backup_${timestamp}_description.reg"
reg export 'HKLM\path\to\key' $backupFile /y

# For full hive binary backup (fast restore with reg restore)
reg save 'HKLM\SYSTEM' "$backupDir\SYSTEM_${timestamp}.hiv" /y
```

### 3. Create / Modify

```powershell
# Create a key if it doesn't exist
if (-not (Test-Path 'HKLM:\path\to\key')) {
    New-Item -Path 'HKLM:\path\to\key' -Force | Out-Null
}

# Set a DWORD value (most common for optimizations)
Set-ItemProperty -Path 'HKLM:\path\to\key' -Name 'ValueName' -Value 1 -Type DWord -Force

# Set a String value
Set-ItemProperty -Path 'HKLM:\path\to\key' -Name 'ValueName' -Value 'string data' -Type String -Force

# Set an ExpandString (contains %VARIABLES%)
Set-ItemProperty -Path 'HKLM:\path\to\key' -Name 'ValueName' -Value '%SystemRoot%\file' -Type ExpandString -Force

# Set a MultiString (array of strings)
Set-ItemProperty -Path 'HKLM:\path\to\key' -Name 'ValueName' -Value @('line1','line2') -Type MultiString -Force

# Set a QWORD (64-bit integer)
Set-ItemProperty -Path 'HKLM:\path\to\key' -Name 'ValueName' -Value 0xFFFFFFFFFFFFFFFF -Type QWord -Force

# Set Binary data
$bytes = [byte[]](0x00, 0x01, 0x02)
Set-ItemProperty -Path 'HKLM:\path\to\key' -Name 'ValueName' -Value $bytes -Type Binary -Force
```

### 4. Delete

```powershell
# Delete a specific value
Remove-ItemProperty -Path 'HKLM:\path\to\key' -Name 'ValueName' -Force

# Delete a key and all its subkeys (DANGEROUS - always backup first)
Remove-Item -Path 'HKLM:\path\to\key' -Recurse -Force
```

### 5. Import .reg Files

```powershell
# Import a .reg file (merges into registry)
reg import 'C:\path\to\file.reg'

# Restore a binary hive backup
reg restore 'HKLM\SYSTEM' 'C:\path\to\SYSTEM.hiv'
```

### 6. Search

Searching the registry is slow because it's huge. Use targeted searches with scope limits.

```powershell
# Search for a value name under a specific key tree
Get-ChildItem -Path 'HKLM:\SOFTWARE' -Recurse -EA SilentlyContinue |
    Where-Object { $_.GetValueNames() -contains 'TargetValueName' } |
    Select-Object -ExpandProperty PSPath

# Search for keys by name pattern
Get-ChildItem -Path 'HKLM:\SOFTWARE' -Recurse -EA SilentlyContinue |
    Where-Object { $_.PSChildName -match 'pattern' } |
    Select-Object -ExpandProperty PSPath

# Search for a specific value data
Get-ChildItem -Path 'HKLM:\SOFTWARE' -Recurse -EA SilentlyContinue | ForEach-Object {
    $key = $_
    $key.GetValueNames() | ForEach-Object {
        $val = $key.GetValue($_)
        if ($val -match 'searchterm') {
            [PSCustomObject]@{ Key=$key.PSPath; Name=$_; Value=$val }
        }
    }
}
```

For fast registry searches, prefer the bundled script:
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File "[skill-root]/scripts/Search-Registry.ps1" -Path 'HKLM:\SOFTWARE' -Pattern 'searchterm' -MaxResults 20
```

## Optimization Presets

The skill includes curated, researched optimization presets. Before applying any preset, read `references/optimization-presets.md` for the full list of tweaks with explanations.

Available presets:
- **network** - Basic TCP/IP, Nagle, throttling, DNS, AFD, QoS, WinINet
- **network-deep** - **15-layer** exhaustive network optimization (NIC hardware, NDIS, TCP global, per-interface, netsh, AFD, DNS, MMCSS, QoS, SMB, WinINet, power, services, MTU). Read `references/presets/network-deep.md` for the full reference.
- **gaming** - GPU priority, MMCSS scheduling, input latency, pre-rendered frames, power throttling
- **privacy** - Telemetry, data collection, advertising ID, activity history, feedback
- **performance** - Memory management, prefetch, priority separation, power plan
- **input-latency** - Mouse/keyboard registry tweaks for responsiveness
- **all** - Apply all presets

### Applying a Preset

The workflow for any preset:
1. Read `references/optimization-presets.md` (or `references/presets/network-deep.md` for network-deep) for the specific preset section
2. Show the user what will change and current vs. new values
3. Back up every key that will be modified
4. Apply changes
5. Verify by re-reading the values
6. Report what changed

```powershell
# Basic network preset
powershell -ExecutionPolicy Bypass -NoProfile -File "[skill-root]/scripts/Apply-Preset.ps1" -Preset 'network' -BackupDir '$HOME\windows-debug\RegistryBackups'

# Deep network preset (all 15 layers)
powershell -ExecutionPolicy Bypass -NoProfile -File "[skill-root]/scripts/Apply-NetworkDeep.ps1" -BackupDir '$HOME\windows-debug\RegistryBackups'

# Deep network - specific layers only
powershell -ExecutionPolicy Bypass -NoProfile -File "[skill-root]/scripts/Apply-NetworkDeep.ps1" -Layers 'nic','tcp-global','afd' -BackupDir '$HOME\windows-debug\RegistryBackups'

# Dry run first (preview changes without applying)
powershell -ExecutionPolicy Bypass -NoProfile -File "[skill-root]/scripts/Apply-NetworkDeep.ps1" -DryRun
```

## Safety Rules

Before modifying ANY key, check it against the safety rules in `references/safety-rules.md`. The rules define:
- **BLOCKED keys**: Never modify under any circumstances (boot config, SAM, security hive core)
- **WARN keys**: Require explicit user confirmation before modifying (Session Manager, driver keys, authentication)
- **SAFE keys**: Can be modified freely (most optimization targets)

## Hive Mapping

PowerShell uses drive notation for registry hives:

| Hive | PowerShell Path | Description |
|------|----------------|-------------|
| HKEY_LOCAL_MACHINE | `HKLM:\` | System-wide settings |
| HKEY_CURRENT_USER | `HKCU:\` | Current user settings |
| HKEY_CLASSES_ROOT | `HKCR:\` | File associations (requires `New-PSDrive HKCR Registry HKEY_CLASSES_ROOT`) |
| HKEY_USERS | `HKU:\` | All user profiles (requires `New-PSDrive HKU Registry HKEY_USERS`) |
| HKEY_CURRENT_CONFIG | `HKCC:\` | Current hardware profile (requires `New-PSDrive HKCC Registry HKEY_CURRENT_CONFIG`) |

Mount non-default hives before use:
```powershell
if (-not (Get-PSDrive -Name HKCR -EA SilentlyContinue)) { New-PSDrive -Name HKCR -PSProvider Registry -Root HKEY_CLASSES_ROOT | Out-Null }
if (-not (Get-PSDrive -Name HKU -EA SilentlyContinue)) { New-PSDrive -Name HKU -PSProvider Registry -Root HKEY_USERS | Out-Null }
if (-not (Get-PSDrive -Name HKCC -EA SilentlyContinue)) { New-PSDrive -Name HKCC -PSProvider Registry -Root HKEY_CURRENT_CONFIG | Out-Null }
```

## Troubleshooting

- **Access Denied**: Some keys require SYSTEM-level access. Use `PsExec -s powershell` or take ownership first.
- **Key not found**: Check the path carefully. Use `Test-Path` before reading. Some keys only exist on certain Windows editions.
- **Type mismatch**: If a value already exists with a different type, delete it first then recreate with the correct type.
- **Changes not taking effect**: Many registry changes require a reboot, service restart, or logoff/logon. Note this when applying changes.
