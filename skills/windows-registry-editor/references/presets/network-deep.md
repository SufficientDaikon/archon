# Network Deep Optimization — Complete Registry & System Reference

This is the exhaustive network optimization reference. It goes far beyond the basic preset and covers every tunable layer of the Windows network stack: NIC hardware offloads, interrupt handling, TCP/IP parameters, UDP, DNS, Winsock, NDIS, QoS, SMB, WinHTTP, power management, and diagnostic validation.

Organized bottom-up: hardware layer first, then kernel, then protocol, then application.

---

## Table of Contents

1. [Layer 1: NIC Hardware & Driver Tuning](#layer-1-nic-hardware--driver-tuning)
2. [Layer 2: NDIS & Interrupt Handling](#layer-2-ndis--interrupt-handling)
3. [Layer 3: TCP/IP Global Parameters](#layer-3-tcpip-global-parameters)
4. [Layer 4: TCP Per-Interface Parameters](#layer-4-tcp-per-interface-parameters)
5. [Layer 5: TCP Netsh Global Settings](#layer-5-tcp-netsh-global-settings)
6. [Layer 6: TCP Advanced — Congestion, ECN, Timestamps](#layer-6-tcp-advanced)
7. [Layer 7: UDP & Winsock (AFD)](#layer-7-udp--winsock-afd)
8. [Layer 8: DNS Resolver](#layer-8-dns-resolver)
9. [Layer 9: MMCSS & Network Throttling](#layer-9-mmcss--network-throttling)
10. [Layer 10: QoS & Bandwidth Reservation](#layer-10-qos--bandwidth-reservation)
11. [Layer 11: SMB & File Sharing](#layer-11-smb--file-sharing)
12. [Layer 12: WinHTTP & WinINet](#layer-12-winhttp--wininet)
13. [Layer 13: Power Management](#layer-13-power-management)
14. [Layer 14: Services & Background Noise](#layer-14-services--background-noise)
15. [Layer 15: MTU & Path Discovery](#layer-15-mtu--path-discovery)
16. [Diagnostics & Validation](#diagnostics--validation)

---

## Layer 1: NIC Hardware & Driver Tuning

These are adapter-level settings. They control what the NIC hardware does before packets even reach the OS.

### Via PowerShell (Set-NetAdapterAdvancedProperty)

All commands use `-Name "Ethernet"` — adjust if your adapter has a different name.

```powershell
$nic = (Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.InterfaceDescription -notmatch 'Virtual|Hyper|Tailscale'}).Name
```

| Setting | Value | Why |
|---------|-------|-----|
| Power Saving Mode | Disabled | Prevents the NIC from throttling to save power |
| Energy-Efficient Ethernet | Disabled | EEE adds 15-30us latency on wake from low-power state |
| Green Ethernet | Disabled | Similar to EEE — saves power at the cost of responsiveness |
| Gigabit Lite | Disabled | Forces the NIC to negotiate at full Gigabit instead of downclocking |
| Flow Control | Disabled | Prevents the NIC from sending PAUSE frames that stall traffic |
| Interrupt Moderation | Disabled | Delivers each packet interrupt immediately instead of batching — critical for latency |
| Interrupt Moderation Rate | Off | Companion to above; ensures no coalescing timer |
| Wake on Magic Packet | Disabled | No reason to keep this on unless you use WoL |
| Wake on Pattern Match | Disabled | Same as above |
| Shutdown Wake-On-Lan | Disabled | Same as above |
| Large Send Offload v2 (IPv4) | Disabled | LSO batches outbound packets — adds latency for gaming/voip. Keep enabled for bulk throughput |
| Large Send Offload v2 (IPv6) | Disabled | Same for IPv6 |
| Receive Side Coalescing | Disabled | RSC merges received segments — adds latency. Disable for real-time, keep for throughput |
| Receive Buffers | 1024 | Larger receive ring buffer prevents drops under burst. Max depends on driver (usually 1024 or 2048) |
| Transmit Buffers | 512 | Larger transmit ring buffer for smoother sends. 256-512 is optimal |
| Speed & Duplex | Auto Negotiation | Leave auto unless cable issues force manual 1Gbps Full Duplex |

```powershell
# Apply all NIC optimizations
$props = @{
    'Power Saving Mode' = 'Disabled'
    'Energy-Efficient Ethernet' = 'Disabled'
    'Green Ethernet' = 'Disabled'
    'Gigabit Lite' = 'Disabled'
    'Flow Control' = 'Disabled'
    'Wake on Magic Packet' = 'Disabled'
    'Wake on pattern match' = 'Disabled'
    'Shutdown Wake-On-Lan' = 'Disabled'
    'Receive Buffers' = '1024'
    'Transmit Buffers' = '512'
}

foreach ($p in $props.GetEnumerator()) {
    try {
        Set-NetAdapterAdvancedProperty -Name $nic -DisplayName $p.Key -DisplayValue $p.Value -EA Stop
        Write-Host "[OK] $($p.Key) = $($p.Value)" -ForegroundColor Green
    } catch {
        Write-Host "[SKIP] $($p.Key) - not available on this adapter" -ForegroundColor DarkGray
    }
}

# These need separate cmdlets
try { Disable-NetAdapterLso -Name $nic -IPv4 -IPv6 -EA Stop; Write-Host "[OK] LSO disabled" -ForegroundColor Green } catch { Write-Host "[SKIP] LSO" -ForegroundColor DarkGray }
try { Disable-NetAdapterRsc -Name $nic -IPv4 -IPv6 -EA Stop; Write-Host "[OK] RSC disabled" -ForegroundColor Green } catch { Write-Host "[SKIP] RSC" -ForegroundColor DarkGray }
```

### Interrupt Moderation (Deep Dive)

Interrupt moderation is the single most impactful NIC setting for latency. When enabled, the NIC holds incoming packets and delivers them in batches at a set interval (typically 1ms). This saves CPU but adds up to 1ms of latency per packet.

```powershell
# Check current state
Get-NetAdapterAdvancedProperty -Name $nic -DisplayName '*Interrupt*' | Format-Table DisplayName, DisplayValue

# Disable (lowest latency)
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName 'Interrupt Moderation' -DisplayValue 'Disabled' -EA SilentlyContinue

# Or set to Minimal if Disabled causes high CPU
Set-NetAdapterAdvancedProperty -Name $nic -DisplayName 'Interrupt Moderation Rate' -DisplayValue 'Minimal' -EA SilentlyContinue
```

### RSS (Receive Side Scaling)

RSS distributes packet processing across CPU cores. Keep enabled, but tune the queue count.

```powershell
# Check RSS status
Get-NetAdapterRss -Name $nic

# Enable with optimal settings
Enable-NetAdapterRss -Name $nic
Set-NetAdapterRss -Name $nic -NumberOfReceiveQueues 4 -MaxProcessors 8

# Verify
Get-NetAdapterRss -Name $nic | Select-Object Enabled, NumberOfReceiveQueues, Profile
```

### Checksum Offload

Keep TCP/UDP checksum offload ENABLED. Disabling it forces the CPU to calculate checksums, wasting cycles for no latency benefit. The NIC does this in hardware at zero cost.

```powershell
# Verify it's enabled (it should be)
Get-NetAdapterChecksumOffload -Name $nic
# Enable if somehow disabled
Enable-NetAdapterChecksumOffload -Name $nic -TcpIPv4 -TcpIPv6 -UdpIPv4 -UdpIPv6 -IpIPv4
```

---

## Layer 2: NDIS & Interrupt Handling

The Network Driver Interface Specification (NDIS) layer sits between the NIC driver and the TCP/IP stack.

### Registry: NDIS Parameters

```powershell
# Find your NIC's registry path
$nicGuid = (Get-NetAdapter -Name $nic).InterfaceGuid
$ndisPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"

# Each subkey (0000, 0001, etc.) is a NIC. Find yours by matching DriverDesc
Get-ChildItem $ndisPath | ForEach-Object {
    $desc = (Get-ItemProperty $_.PSPath -EA SilentlyContinue).DriverDesc
    if ($desc) { "$($_.PSChildName): $desc" }
}
```

| Path (under NIC subkey) | Value | Type | Data | Purpose |
|------------------------|-------|------|------|---------|
| `*InterruptModeration` | DWord | 0 | Disable interrupt batching at NDIS level |
| `*RSS` | DWord | 1 | Enable Receive Side Scaling |
| `*NumRssQueues` | DWord | 4 | Number of RSS queues (match physical cores) |
| `*FlowControl` | DWord | 0 | Disable PAUSE frames |
| `*LsoV2IPv4` | DWord | 0 | Disable Large Send Offload v2 for IPv4 |
| `*LsoV2IPv6` | DWord | 0 | Disable Large Send Offload v2 for IPv6 |
| `*PriorityVLANTag` | DWord | 1 | Enable VLAN priority tagging |
| `*ReceiveBuffers` | DWord | 1024 | Receive ring buffer size |
| `*TransmitBuffers` | DWord | 512 | Transmit ring buffer size |
| `EEELinkAdvertisement` | DWord | 0 | Disable Energy Efficient Ethernet advertisement |
| `GreenEthernet` | DWord | 0 | Disable Green Ethernet |
| `PowerSavingMode` | DWord | 0 | Disable power saving on the NIC |
| `S5WakeOnLan` | DWord | 0 | Disable WoL from shutdown |
| `WakeOnMagicPacket` | DWord | 0 | Disable WoL magic packet |
| `WakeOnPattern` | DWord | 0 | Disable WoL pattern match |

---

## Layer 3: TCP/IP Global Parameters

These are the core TCP/IP stack registry tweaks. Path: `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters`

| Value | Type | Data | Default | Purpose |
|-------|------|------|---------|---------|
| DefaultTTL | DWord | 64 | 128 | Optimal Time-To-Live (64 is the Linux/modern standard; 128 is Windows default — both work, 64 is slightly more efficient) |
| TcpTimedWaitDelay | DWord | 30 | 240 | Seconds a closed connection stays in TIME_WAIT. 30s frees ports 8x faster |
| MaxUserPort | DWord | 65534 | 5000 | Maximum ephemeral port number. 65534 = full range available |
| TcpMaxDupAcks | DWord | 2 | 3 | Fast retransmit triggers after 2 dup ACKs instead of 3. Slightly faster loss recovery |
| SackOpts | DWord | 1 | 1 | Selective ACK (RFC 2018). Already default, ensure it's on |
| Tcp1323Opts | DWord | 1 | 3 | 1 = window scaling only (no timestamps). Timestamps add 12 bytes per packet overhead; disable unless needed for high-latency WAN |
| MaxFreeTcbs | DWord | 65536 | 2000 | Max TCP control blocks in free pool. Prevents allocation stalls under high connection counts |
| MaxHashTableSize | DWord | 65536 | 512 | Hash table for TCB lookups. Larger = faster lookups with many connections |
| TcpMaxSendFree | DWord | 65535 | varies | Max pending send buffers before throttling |
| TcpMaxConnectRetransmissions | DWord | 3 | 2 | SYN retries for new connections. 3 gives slightly more resilience without much delay |
| TcpMaxDataRetransmissions | DWord | 5 | 5 | Max retransmits for a data segment before dropping the connection |
| EnablePMTUDiscovery | DWord | 1 | 1 | Path MTU discovery. Essential for avoiding fragmentation |
| EnablePMTUBHDetect | DWord | 1 | 0 | Detect black-hole routers that silently drop large packets. Helps PMTUD succeed |
| GlobalMaxTcpWindowSize | DWord | 16777216 | 65535 | 16MB max TCP window. Allows full throughput on high-BDP paths |
| TcpWindowSize | DWord | 65535 | varies | Default receive window. 64KB is good for most connections |
| EnableDca | DWord | 1 | 0 | Direct Cache Access — allows NIC DMA to write directly to CPU cache. Reduces memory latency |
| DisableTaskOffload | DWord | 0 | 0 | Ensure task offload is NOT disabled |
| EnableTCPA | DWord | 1 | varies | TCP/IP chimney offload enablement |

```powershell
$tcp = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
$values = @{
    'DefaultTTL' = 64
    'TcpTimedWaitDelay' = 30
    'MaxUserPort' = 65534
    'TcpMaxDupAcks' = 2
    'SackOpts' = 1
    'Tcp1323Opts' = 1
    'MaxFreeTcbs' = 65536
    'MaxHashTableSize' = 65536
    'TcpMaxSendFree' = 65535
    'TcpMaxConnectRetransmissions' = 3
    'TcpMaxDataRetransmissions' = 5
    'EnablePMTUDiscovery' = 1
    'EnablePMTUBHDetect' = 1
    'GlobalMaxTcpWindowSize' = 16777216
    'TcpWindowSize' = 65535
    'EnableDca' = 1
    'DisableTaskOffload' = 0
}

foreach ($v in $values.GetEnumerator()) {
    Set-ItemProperty -Path $tcp -Name $v.Key -Value $v.Value -Type DWord -Force
}
```

---

## Layer 4: TCP Per-Interface Parameters

Applied to every network interface. Path: `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{GUID}`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| TcpAckFrequency | DWord | 1 | ACK every segment immediately (disables delayed ACK). Reduces round-trip for interactive protocols |
| TCPNoDelay | DWord | 1 | Disables Nagle's algorithm. Sends small packets immediately instead of buffering |
| TcpWindowSize | DWord | 65535 | Per-interface receive window size |
| TcpInitialRTT | DWord | 300 | Initial round-trip time estimate in ms (lower = faster first retransmit for lost SYN) |
| TcpDelAckTicks | DWord | 0 | Delayed ACK timer in 100ms ticks. 0 = immediate ACK (same effect as TcpAckFrequency=1) |

```powershell
$interfaces = Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces'
foreach ($iface in $interfaces) {
    Set-ItemProperty -Path $iface.PSPath -Name 'TcpAckFrequency' -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $iface.PSPath -Name 'TCPNoDelay' -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $iface.PSPath -Name 'TcpWindowSize' -Value 65535 -Type DWord -Force
    Set-ItemProperty -Path $iface.PSPath -Name 'TcpInitialRTT' -Value 300 -Type DWord -Force
    Set-ItemProperty -Path $iface.PSPath -Name 'TcpDelAckTicks' -Value 0 -Type DWord -Force
}
```

---

## Layer 5: TCP Netsh Global Settings

These are set via `netsh` rather than registry. They control the TCP stack behavior at the transport layer.

```powershell
# Auto-tuning: 'normal' lets Windows scale the receive window dynamically. Best for general use.
# Use 'disabled' only if behind a broken router/firewall that can't handle window scaling.
netsh int tcp set global autotuninglevel=normal

# Congestion provider: CTCP (Compound TCP) is more aggressive than default CUBIC for throughput
netsh int tcp set supplemental Template=Internet CongestionProvider=ctcp

# ECN: Explicit Congestion Notification. Allows routers to signal congestion without dropping.
# Beneficial on modern networks. Disable if you see connection issues with old equipment.
netsh int tcp set global ecncapability=enabled

# RSS: Receive Side Scaling. Distributes processing across CPU cores.
netsh int tcp set global rss=enabled

# TCP Fast Open: Reduces handshake latency by sending data in the SYN packet.
netsh int tcp set global fastopen=enabled

# DCA: Direct Cache Access. NIC writes to CPU cache directly.
netsh int tcp set global dca=enabled

# Heuristics: Windows may override your auto-tuning settings. Disable to keep your settings.
netsh int tcp set heuristics disabled

# Chimney offload: Let the NIC handle TCP state for established connections.
netsh int tcp set global chimney=enabled

# Initial RTO: Time before first retransmit of a SYN. Default 3000ms is very conservative.
# 1000ms is more aggressive but fine for non-satellite links.
netsh int tcp set global initialRto=1000

# Timestamps: RFC 1323. Adds 12 bytes overhead per packet but enables PAWS and better RTT.
# Disable for minimal overhead on LAN; keep for WAN reliability.
netsh int tcp set global timestamps=disabled

# Non-SACK RTT resiliency: Extra retransmit logic for non-SACK connections. Low value.
netsh int tcp set global nonsackrttresiliency=disabled
```

---

## Layer 6: TCP Advanced

### Congestion Control Comparison

| Provider | Best For | Behavior |
|----------|----------|----------|
| default (CUBIC) | General use | Conservative, fair sharing |
| ctcp (Compound) | High throughput | More aggressive window growth |
| DCTCP | Data centers | ECN-aware, low queue depth |
| NewReno | Legacy | Oldest, least efficient |

```powershell
# View current
netsh int tcp show supplemental

# Set CTCP for internet template
netsh int tcp set supplemental Template=Internet CongestionProvider=ctcp

# Verify
netsh int tcp show supplemental
```

### ECN Deep Dive

ECN eliminates the need for routers to drop packets to signal congestion. Instead they set a bit in the IP header. The receiver echoes it back. The sender reduces window. No packet loss = no retransmit delay.

**When to enable:** Modern ISP, modern router, no VPN issues.
**When to disable:** Old/cheap routers that drop ECN-marked packets, or VPN tunnels that strip ECN bits.

```powershell
# Enable
netsh int tcp set global ecncapability=enabled
# Disable
netsh int tcp set global ecncapability=disabled
```

---

## Layer 7: UDP & Winsock (AFD)

The AFD (Ancillary Function Driver) is the kernel-mode Winsock implementation. It manages socket buffers for all TCP and UDP connections.

Path: `HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters`

| Value | Type | Data | Default | Purpose |
|-------|------|------|---------|---------|
| FastSendDatagramThreshold | DWord | 65536 | 1024 | UDP datagrams up to this size use the fast I/O path instead of IRP-based I/O. 64KB covers all common game/voip packets |
| DefaultReceiveWindow | DWord | 65536 | 8192 | Default receive buffer per socket. 64KB prevents small-buffer drops |
| DefaultSendWindow | DWord | 65536 | 8192 | Default send buffer per socket |
| LargeBufferSize | DWord | 65536 | 32768 | Size of "large" buffer pool allocations |
| MediumBufferSize | DWord | 3072 | 1504 | Size of "medium" buffer pool. 3072 covers jumbo-ish frames |
| SmallBufferSize | DWord | 512 | 128 | Size of "small" buffer pool |
| TransmitWorker | DWord | 32 | 8 | Transmit worker threads in AFD |
| MaxActiveTransmitFileCount | DWord | 64 | 16 | Max concurrent TransmitFile operations |
| IgnorePushBitOnReceives | DWord | 1 | 0 | Ignore TCP PUSH bit for more efficient receive batching |
| DynamicBacklogGrowthDelta | DWord | 10 | 5 | How quickly the listen backlog grows under load |
| EnableDynamicBacklog | DWord | 1 | 0 | Allow listen backlog to grow dynamically |

```powershell
$afd = 'HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters'
if (-not (Test-Path $afd)) { New-Item -Path $afd -Force | Out-Null }

$afdValues = @{
    'FastSendDatagramThreshold' = 65536
    'DefaultReceiveWindow' = 65536
    'DefaultSendWindow' = 65536
    'LargeBufferSize' = 65536
    'MediumBufferSize' = 3072
    'SmallBufferSize' = 512
    'TransmitWorker' = 32
    'MaxActiveTransmitFileCount' = 64
    'IgnorePushBitOnReceives' = 1
    'DynamicBacklogGrowthDelta' = 10
    'EnableDynamicBacklog' = 1
}

foreach ($v in $afdValues.GetEnumerator()) {
    Set-ItemProperty -Path $afd -Name $v.Key -Value $v.Value -Type DWord -Force
}
```

---

## Layer 8: DNS Resolver

Path: `HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| MaxNegativeCacheTtl | DWord | 5 | Cache negative (NXDOMAIN) responses for only 5 seconds |
| NetFailureCacheTime | DWord | 0 | Don't cache network-level DNS failures at all |
| MaxCacheTtl | DWord | 86400 | Max positive cache TTL: 24 hours (prevents stale entries) |
| MaxCacheEntryTtlLimit | DWord | 86400 | Same as above, different Windows versions |
| NegativeCacheTime | DWord | 5 | Alternative key for negative cache TTL |
| ServiceConnectivityEvents | DWord | 0 | Reduce DNS service event logging noise |

```powershell
$dns = 'HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters'
Set-ItemProperty -Path $dns -Name 'MaxNegativeCacheTtl' -Value 5 -Type DWord -Force
Set-ItemProperty -Path $dns -Name 'NetFailureCacheTime' -Value 0 -Type DWord -Force
Set-ItemProperty -Path $dns -Name 'MaxCacheTtl' -Value 86400 -Type DWord -Force
Set-ItemProperty -Path $dns -Name 'NegativeCacheTime' -Value 5 -Type DWord -Force
```

### DNS Server Configuration

```powershell
# Cloudflare (fastest average)
Set-DnsClientServerAddress -InterfaceAlias $nic -ServerAddresses ("1.1.1.1","1.0.0.1")

# Google (most reliable)
# Set-DnsClientServerAddress -InterfaceAlias $nic -ServerAddresses ("8.8.8.8","8.8.4.4")

# Quad9 (security-focused, blocks malware domains)
# Set-DnsClientServerAddress -InterfaceAlias $nic -ServerAddresses ("9.9.9.9","149.112.112.112")

# Flush after changing
Clear-DnsClientCache
ipconfig /flushdns
```

---

## Layer 9: MMCSS & Network Throttling

The Multimedia Class Scheduler Service (MMCSS) can throttle network traffic during multimedia playback to prevent glitches. For gaming/streaming PCs, this is counterproductive.

Path: `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| NetworkThrottlingIndex | DWord | 0xFFFFFFFF (4294967295) | Disables all network throttling. Default 10 limits to 10 packets per ms |
| SystemResponsiveness | DWord | 0 | 0% CPU reserved for background. Use 10 if you multitask heavily |

Path: `...\SystemProfile\Tasks\Games`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| Scheduling Category | String | High | Thread scheduling priority |
| SFIO Priority | String | High | Storage I/O priority |
| GPU Priority | DWord | 8 | GPU scheduling priority (max) |
| Priority | DWord | 6 | CPU priority (6 = high) |
| Background Only | String | False | Don't treat as background |
| Clock Rate | DWord | 10000 | 1ms timer resolution |

```powershell
$p = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile'
Set-ItemProperty -Path $p -Name 'NetworkThrottlingIndex' -Value 0xFFFFFFFF -Type DWord -Force
Set-ItemProperty -Path $p -Name 'SystemResponsiveness' -Value 0 -Type DWord -Force
```

---

## Layer 10: QoS & Bandwidth Reservation

Windows reserves 20% of bandwidth for QoS by default (even if no QoS policies are configured). Remove this.

Path: `HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| NonBestEffortLimit | DWord | 0 | Zero percent reserved for QoS |

```powershell
$qos = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched'
if (-not (Test-Path $qos)) { New-Item -Path $qos -Force | Out-Null }
Set-ItemProperty -Path $qos -Name 'NonBestEffortLimit' -Value 0 -Type DWord -Force
```

---

## Layer 11: SMB & File Sharing

SMB client tuning for faster LAN file transfers.

Path: `HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| DisableBandwidthThrottling | DWord | 1 | No throttling on remote file operations |
| DisableLargeMtu | DWord | 0 | Allow large MTU for SMB |
| FileInfoCacheEntriesMax | DWord | 64 | Cache more file metadata |
| DirectoryCacheEntriesMax | DWord | 16 | Cache more directory listings |
| FileNotFoundCacheEntriesMax | DWord | 128 | Cache more "not found" results |
| MaxCmds | DWord | 128 | Max outstanding SMB commands |

Path: `HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters` (server-side)

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| IRPStackSize | DWord | 32 | I/O Request Packet stack depth (prevents "not enough server storage" errors) |
| Size | DWord | 3 | Optimize SMB server memory for file sharing |

```powershell
$smbc = 'HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters'
Set-ItemProperty -Path $smbc -Name 'DisableBandwidthThrottling' -Value 1 -Type DWord -Force
Set-ItemProperty -Path $smbc -Name 'DisableLargeMtu' -Value 0 -Type DWord -Force
Set-ItemProperty -Path $smbc -Name 'FileInfoCacheEntriesMax' -Value 64 -Type DWord -Force
Set-ItemProperty -Path $smbc -Name 'DirectoryCacheEntriesMax' -Value 16 -Type DWord -Force
Set-ItemProperty -Path $smbc -Name 'FileNotFoundCacheEntriesMax' -Value 128 -Type DWord -Force
Set-ItemProperty -Path $smbc -Name 'MaxCmds' -Value 128 -Type DWord -Force

$smbs = 'HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters'
Set-ItemProperty -Path $smbs -Name 'IRPStackSize' -Value 32 -Type DWord -Force
Set-ItemProperty -Path $smbs -Name 'Size' -Value 3 -Type DWord -Force
```

---

## Layer 12: WinHTTP & WinINet

Controls browser and application HTTP connection limits.

### WinINet (Internet Explorer / Edge / many apps)

Path: `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| MaxConnectionsPerServer | DWord | 10 | HTTP/1.1 connections per server (default 2) |
| MaxConnectionsPer1_0Server | DWord | 10 | HTTP/1.0 connections per server (default 4) |

### WinHTTP (system-level HTTP client)

Path: `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\WinHttp`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| TcpAutotuning | DWord | 1 | Enable TCP auto-tuning for WinHTTP |

```powershell
$inet = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings'
Set-ItemProperty -Path $inet -Name 'MaxConnectionsPerServer' -Value 10 -Type DWord -Force
Set-ItemProperty -Path $inet -Name 'MaxConnectionsPer1_0Server' -Value 10 -Type DWord -Force
```

---

## Layer 13: Power Management

Ensure the NIC never enters power-saving states.

```powershell
# Disable device power management on the NIC
$nicPnp = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Realtek' -and $_.Class -eq 'Net' }
if ($nicPnp) {
    $instancePath = $nicPnp.InstanceId
    $pmPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$instancePath\Device Parameters"
    # Check if power management keys exist
    if (Test-Path $pmPath) {
        Write-Host "NIC device parameters path: $pmPath"
    }
}

# System-wide: High Performance power plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable USB selective suspend (affects USB NICs/dongles)
powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
powercfg /SETACTIVE SCHEME_CURRENT

# Disable PCI Express Link State Power Management
powercfg /SETACVALUEINDEX SCHEME_CURRENT 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a576df5 0
powercfg /SETACTIVE SCHEME_CURRENT
```

---

## Layer 14: Services & Background Noise

Services that consume network bandwidth or add latency.

```powershell
# Disable bandwidth-wasting services
$disable = @(
    'DiagTrack',           # Telemetry (sends data to Microsoft constantly)
    'dmwappushservice',    # WAP push message routing (telemetry helper)
    'RemoteRegistry',      # Remote registry editing (security risk + overhead)
    'WMPNetworkSvc',       # Windows Media Player network sharing
    'MapsBroker',          # Downloaded Maps Manager (background downloads)
    'NcdAutoSetup',        # Network Connected Devices auto-setup
    'WerSvc',              # Windows Error Reporting (uploads crash data)
    'lfsvc',               # Geolocation (background network calls)
    'RetailDemo',          # Retail demo service
    'wisvc'                # Windows Insider Service
)

foreach ($s in $disable) {
    Stop-Service -Name $s -Force -EA SilentlyContinue
    Set-Service -Name $s -StartupType Disabled -EA SilentlyContinue
}

# Set to Manual (they'll start when needed, not at boot)
$manual = @(
    'BITS',        # Background Intelligent Transfer (Windows Update)
    'wuauserv',    # Windows Update
    'DoSvc',       # Delivery Optimization (P2P updates)
    'WSearch',     # Windows Search (disk + network indexing)
    'DPS',         # Diagnostic Policy Service
    'iphlpsvc'     # IPv6 transition technologies (6to4, ISATAP, etc.)
)

foreach ($s in $manual) {
    Set-Service -Name $s -StartupType Manual -EA SilentlyContinue
}
```

---

## Layer 15: MTU & Path Discovery

MTU (Maximum Transmission Unit) determines the largest packet that can traverse a link without fragmentation. The standard Ethernet MTU is 1500. Fragmentation kills performance.

### Find Optimal MTU

```powershell
# Test MTU with ping (subtract 28 for ICMP/IP headers)
# Start at 1472 (1500 - 28) and decrease until no fragmentation
ping -f -l 1472 1.1.1.1
# If "Packet needs to be fragmented", try lower:
ping -f -l 1464 1.1.1.1
ping -f -l 1400 1.1.1.1

# Once you find the max that works, add 28 = your optimal MTU
```

### Set MTU

```powershell
# View current MTU
netsh int ipv4 show interfaces

# Set MTU (use value from ping test + 28)
$ifIndex = (Get-NetAdapter -Name $nic).ifIndex
netsh int ipv4 set subinterface $ifIndex mtu=1500 store=persistent
```

### Registry MTU Override

Path: `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{GUID}`

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| MTU | DWord | 1500 | Override interface MTU (only if netsh doesn't stick) |
| EnablePMTUDiscovery | DWord | 1 | Allow automatic MTU discovery |

---

## Diagnostics & Validation

Run after applying all optimizations to verify everything took effect.

```powershell
Write-Host "=== NIC Status ===" -ForegroundColor Cyan
Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.InterfaceDescription -notmatch 'Virtual|Hyper|Tailscale'} |
    Select-Object Name, InterfaceDescription, LinkSpeed | Format-Table -AutoSize

Write-Host "`n=== NIC Advanced Properties ===" -ForegroundColor Cyan
Get-NetAdapterAdvancedProperty -Name $nic |
    Where-Object {$_.DisplayName -match 'Power|Energy|Wake|Flow|Buffer|Speed|Green|Gigabit|Interrupt|Offload'} |
    Select-Object DisplayName, DisplayValue | Format-Table -AutoSize

Write-Host "`n=== TCP Global ===" -ForegroundColor Cyan
netsh int tcp show global

Write-Host "`n=== TCP Supplemental ===" -ForegroundColor Cyan
netsh int tcp show supplemental

Write-Host "`n=== MMCSS ===" -ForegroundColor Cyan
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' |
    Select-Object NetworkThrottlingIndex, SystemResponsiveness | Format-List

Write-Host "`n=== Latency Test ===" -ForegroundColor Cyan
ping -n 5 1.1.1.1

Write-Host "`n=== DNS Speed ===" -ForegroundColor Cyan
1..3 | ForEach-Object { (Measure-Command { Resolve-DnsName google.com }).TotalMilliseconds }
```
