---
name: windows-network-optimizer
description: Diagnose, optimize, and verify Windows 11 network and system performance via PowerShell. Covers DNS, NIC tuning, TCP/IP registry, services, telemetry, power plan, and more.
---

# Windows Network & System Optimizer

Use this skill when the user asks to optimize their internet, fix slow network, tune Windows performance, or run network diagnostics.

## When to Use
- User reports slow internet, high latency, packet loss
- User asks to optimize Windows network settings
- User asks to diagnose network or system performance
- User asks to check/audit optimization status
- User asks to re-apply optimizations after a Windows update

## Prerequisites
- Windows 11 (also works on Windows 10)
- Admin/elevated PowerShell access
- Use `mcp__Windows-MCP__PowerShell` tool for all commands

## Phase 1: Diagnose

Run the diagnostic script if it exists:
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File "$HOME\windows-debug\NetworkDiagnostics\diagnose.ps1"
```

Or run inline diagnostics:
```powershell
# Quick health check
Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object Name, InterfaceDescription, LinkSpeed, Status
Get-NetAdapterAdvancedProperty -Name "Ethernet" | Where-Object {$_.DisplayName -match 'Power|Energy|Wake|Flow|Buffer|Speed'} | Select-Object DisplayName, DisplayValue
netsh int tcp show global
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' | Select-Object NetworkThrottlingIndex, SystemResponsiveness
ping -n 5 1.1.1.1
Measure-Command { Resolve-DnsName google.com }
```

## Phase 2: Optimize

**IMPORTANT: Always create a System Restore Point first:**
```powershell
Checkpoint-Computer -Description "Before Network Optimization" -RestorePointType MODIFY_SETTINGS
```

### DNS
```powershell
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses ("1.1.1.1","1.0.0.1")
$dnsParams = 'HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters'
Set-ItemProperty -Path $dnsParams -Name 'MaxNegativeCacheTtl' -Value 5 -Type DWord -Force
Set-ItemProperty -Path $dnsParams -Name 'NetFailureCacheTime' -Value 0 -Type DWord -Force
Clear-DnsClientCache
```

### NIC Adapter (Realtek)
```powershell
$nic = "Ethernet"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Power Saving Mode" -DisplayValue "Disabled"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Energy-Efficient Ethernet" -DisplayValue "Disabled"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Wake on Magic Packet" -DisplayValue "Disabled"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Wake on pattern match" -DisplayValue "Disabled"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Shutdown Wake-On-Lan" -DisplayValue "Disabled"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Green Ethernet" -DisplayValue "Disabled"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Gigabit Lite" -DisplayValue "Disabled"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Flow Control" -DisplayValue "Disabled"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Transmit Buffers" -DisplayValue "256"
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName "Receive Buffers" -DisplayValue "1024"
```

### TCP/IP Registry (Per-Interface Nagle Disable)
```powershell
$interfaces = Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
foreach ($iface in $interfaces) {
    Set-ItemProperty -Path $iface.PSPath -Name "TcpAckFrequency" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $iface.PSPath -Name "TCPNoDelay" -Value 1 -Type DWord -Force
}
```

### TCP/IP Global Registry
```powershell
$tcp = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
Set-ItemProperty -Path $tcp -Name 'DefaultTTL' -Value 64 -Type DWord -Force
Set-ItemProperty -Path $tcp -Name 'TcpTimedWaitDelay' -Value 30 -Type DWord -Force
Set-ItemProperty -Path $tcp -Name 'MaxUserPort' -Value 65534 -Type DWord -Force
Set-ItemProperty -Path $tcp -Name 'TcpMaxDupAcks' -Value 2 -Type DWord -Force
Set-ItemProperty -Path $tcp -Name 'SackOpts' -Value 1 -Type DWord -Force
Set-ItemProperty -Path $tcp -Name 'Tcp1323Opts' -Value 1 -Type DWord -Force
Set-ItemProperty -Path $tcp -Name 'MaxFreeTcbs' -Value 65536 -Type DWord -Force
Set-ItemProperty -Path $tcp -Name 'MaxHashTableSize' -Value 65536 -Type DWord -Force
```

### TCP netsh
```powershell
netsh int tcp set global autotuninglevel=normal
netsh int tcp set supplemental Template=Internet CongestionProvider=ctcp
netsh int tcp set global ecncapability=enabled
netsh int tcp set global rss=enabled
netsh int tcp set global fastopen=enabled
netsh int tcp set global dca=enabled
netsh int tcp set heuristics disabled
```

### MMCSS / Network Throttling
```powershell
$p = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile'
Set-ItemProperty -Path $p -Name 'NetworkThrottlingIndex' -Value 0xFFFFFFFF -Type DWord -Force
Set-ItemProperty -Path $p -Name 'SystemResponsiveness' -Value 10 -Type DWord -Force
```

### AFD Parameters
```powershell
$afd = 'HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters'
if (-not (Test-Path $afd)) { New-Item -Path $afd -Force | Out-Null }
Set-ItemProperty -Path $afd -Name 'FastSendDatagramThreshold' -Value 65536 -Type DWord -Force
Set-ItemProperty -Path $afd -Name 'DefaultReceiveWindow' -Value 65536 -Type DWord -Force
Set-ItemProperty -Path $afd -Name 'DefaultSendWindow' -Value 65536 -Type DWord -Force
```

### QoS + WinINet + SMB
```powershell
$qos = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched'
if (-not (Test-Path $qos)) { New-Item -Path $qos -Force | Out-Null }
Set-ItemProperty -Path $qos -Name 'NonBestEffortLimit' -Value 0 -Type DWord -Force

Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings' -Name 'MaxConnectionsPerServer' -Value 10 -Type DWord -Force
Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings' -Name 'MaxConnectionsPer1_0Server' -Value 10 -Type DWord -Force

Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters' -Name 'DisableBandwidthThrottling' -Value 1 -Type DWord -Force
```

### Services
```powershell
$disable = @('DiagTrack','dmwappushservice','RemoteRegistry','WMPNetworkSvc','MapsBroker','NcdAutoSetup','WerSvc','SysMain')
foreach ($s in $disable) { Stop-Service -Name $s -Force -EA SilentlyContinue; Set-Service -Name $s -StartupType Disabled -EA SilentlyContinue }
$manual = @('BITS','wuauserv','WSearch','DoSvc','DPS','iphlpsvc')
foreach ($s in $manual) { Set-Service -Name $s -StartupType Manual -EA SilentlyContinue }
```

### Telemetry
```powershell
$dc = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection'
if (-not (Test-Path $dc)) { New-Item -Path $dc -Force | Out-Null }
Set-ItemProperty -Path $dc -Name 'AllowTelemetry' -Value 0 -Type DWord -Force
```

### Memory + CPU + Power
```powershell
$mem = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'
Set-ItemProperty -Path $mem -Name 'DisablePagingExecutive' -Value 1 -Type DWord -Force
Set-ItemProperty -Path "$mem\PrefetchParameters" -Name 'EnablePrefetcher' -Value 0 -Type DWord -Force
Set-ItemProperty -Path "$mem\PrefetchParameters" -Name 'EnableSuperfetch' -Value 0 -Type DWord -Force
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' -Name 'Win32PrioritySeparation' -Value 0x26 -Type DWord -Force
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
```

### Defender (without disabling)
```powershell
Set-MpPreference -ScanAvgCPULoadFactor 20
Set-MpPreference -DisableScanningNetworkFiles $true
```

### Network Stack Reset (requires reboot)
```powershell
ipconfig /flushdns
netsh winsock reset
netsh int ip reset
```

## Phase 3: Verify

Run the diagnostic script again and compare critical/warning/optimized counts:
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File "$HOME\windows-debug\NetworkDiagnostics\diagnose.ps1"
```

## Phase 4: Report

Summarize:
- Before: X critical, Y warnings, Z optimized
- After: X critical, Y warnings, Z optimized
- Remaining issues (typically: cable needs replacing for Gbps, disk space on C:)
- Remind user to reboot for full effect

## Known Hardware Issues (Per-Machine)

Document machine-specific issues here after diagnosis:
- [Cable type limitations, if any]
- [Disk space constraints affecting performance]
- [VPN/proxy configurations that affect DNS routing]
