# Registry Optimization Presets

Each preset is a curated collection of registry modifications. Every value includes:
- The registry path and value name
- The type and optimal value
- What it does and why it helps

## Preset: network

Optimizes TCP/IP stack, disables throttling, tunes DNS and socket buffers.

### TCP Global Parameters
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | DefaultTTL | DWord | 64 | Standard hop limit; prevents packets being dropped by over-aggressive routers |
| `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | TcpTimedWaitDelay | DWord | 30 | Reduces TIME_WAIT from 240s to 30s, freeing ports faster |
| `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | MaxUserPort | DWord | 65534 | Expands ephemeral port range for high-connection workloads |
| `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | TcpMaxDupAcks | DWord | 2 | Triggers fast retransmit after 2 duplicate ACKs instead of 3 |
| `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | SackOpts | DWord | 1 | Enables Selective ACK for efficient loss recovery |
| `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | Tcp1323Opts | DWord | 1 | Enables TCP window scaling (RFC 1323) for high-bandwidth paths |
| `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | MaxFreeTcbs | DWord | 65536 | Increases TCP control block pool for many concurrent connections |
| `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters` | MaxHashTableSize | DWord | 65536 | Larger hash table for faster TCP connection lookups |

### Per-Interface Nagle Disable
Applied to ALL interfaces under `HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{GUID}`:

| Value | Type | Data | Purpose |
|-------|------|------|---------|
| TcpAckFrequency | DWord | 1 | ACK every packet immediately instead of batching (reduces latency) |
| TCPNoDelay | DWord | 1 | Disables Nagle's algorithm (send small packets immediately) |
| TcpWindowSize | DWord | 65535 | Sets receive window to 64KB for better throughput |

### MMCSS / Network Throttling
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile` | NetworkThrottlingIndex | DWord | 0xFFFFFFFF | Disables network throttling during multimedia playback |
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile` | SystemResponsiveness | DWord | 10 | Reserves only 10% CPU for background tasks (default 20%) |

### AFD (Winsock) Buffers
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters` | FastSendDatagramThreshold | DWord | 65536 | Larger fast-path threshold for UDP sends |
| `HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters` | DefaultReceiveWindow | DWord | 65536 | 64KB receive buffer per socket |
| `HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters` | DefaultSendWindow | DWord | 65536 | 64KB send buffer per socket |

### QoS Bandwidth
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched` | NonBestEffortLimit | DWord | 0 | Removes QoS bandwidth reservation (default reserves 20%) |

### WinINet Connections
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings` | MaxConnectionsPerServer | DWord | 10 | Allows 10 concurrent HTTP connections per server (default 2) |
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings` | MaxConnectionsPer1_0Server | DWord | 10 | Same for HTTP/1.0 servers |

### SMB Client
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters` | DisableBandwidthThrottling | DWord | 1 | Disables SMB bandwidth throttling for faster file transfers |

### DNS Cache
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters` | MaxNegativeCacheTtl | DWord | 5 | Cache DNS failures for only 5 seconds instead of 900 |
| `HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters` | NetFailureCacheTime | DWord | 0 | Don't cache network failures at all |

---

## Preset: gaming

Optimizes GPU scheduling, input priority, and game thread handling.

### MMCSS Game Tasks
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` | Scheduling Category | String | High | Elevates game thread scheduling priority |
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` | SFIO Priority | String | High | Higher storage I/O priority for games |
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` | GPU Priority | DWord | 8 | Maximum GPU priority for game tasks |
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` | Priority | DWord | 6 | High CPU priority class for game threads |
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` | Background Only | String | False | Games are not treated as background tasks |
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` | Clock Rate | DWord | 10000 | 1ms timer resolution for smoother frame pacing |
| `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` | Affinity | DWord | 0 | Use all CPU cores |

### Power Throttling
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling` | PowerThrottlingOff | DWord | 1 | Disables CPU power throttling (full speed always) |

### Pre-rendered Frames
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SOFTWARE\Microsoft\DirectX` | MaxPreRenderedFrames | DWord | 1 | Minimum frame queue = lowest input lag |

### GameDVR (disable background recording overhead)
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR` | AppCaptureEnabled | DWord | 0 | Disables Game DVR capture |
| `HKCU:\System\GameConfigStore` | GameDVR_Enabled | DWord | 0 | Disables Game Bar recording |
| `HKCU:\System\GameConfigStore` | GameDVR_FSEBehaviorMode | DWord | 2 | Prefer exclusive fullscreen over borderless |
| `HKCU:\System\GameConfigStore` | GameDVR_HonorUserFSEBehaviorMode | DWord | 1 | Respect user fullscreen preference |

### Fullscreen Optimizations
| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKCU:\System\GameConfigStore` | GameDVR_DXGIHonorFSEWindowsCompatible | DWord | 1 | Honor exclusive fullscreen for DX games |
| `HKCU:\System\GameConfigStore` | GameDVR_EFSEFeatureFlags | DWord | 0 | Disable enhanced fullscreen optimizations overlay |

---

## Preset: privacy

Reduces telemetry, advertising, and background data collection.

| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection` | AllowTelemetry | DWord | 0 | Disable telemetry (Security level only) |
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo` | Enabled | DWord | 0 | Disable advertising ID |
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy` | TailoredExperiencesWithDiagnosticDataEnabled | DWord | 0 | Disable tailored experiences |
| `HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent` | DisableWindowsConsumerFeatures | DWord | 1 | Disable suggested apps and consumer features |
| `HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent` | DisableSoftLanding | DWord | 1 | Disable Windows tips |
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager` | SystemPaneSuggestionsEnabled | DWord | 0 | Disable Start menu suggestions |
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager` | SilentInstalledAppsEnabled | DWord | 0 | Prevent silent app installs |
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager` | SoftLandingEnabled | DWord | 0 | Disable tips/tricks notifications |
| `HKLM:\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo` | DisabledByGroupPolicy | DWord | 1 | Enforce advertising ID off via policy |
| `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced` | Start_TrackProgs | DWord | 0 | Stop tracking recently opened programs |
| `HKLM:\SOFTWARE\Policies\Microsoft\Windows\System` | EnableActivityFeed | DWord | 0 | Disable activity history / timeline |
| `HKLM:\SOFTWARE\Policies\Microsoft\Windows\System` | PublishUserActivities | DWord | 0 | Don't publish user activities to Microsoft |
| `HKLM:\SOFTWARE\Policies\Microsoft\Windows\System` | UploadUserActivities | DWord | 0 | Don't upload user activities |

---

## Preset: performance

Memory, prefetch, process priority, and power settings.

| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management` | DisablePagingExecutive | DWord | 1 | Keep kernel in RAM (never page to disk) |
| `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management` | LargeSystemCache | DWord | 0 | Optimize for applications, not file cache |
| `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters` | EnablePrefetcher | DWord | 0 | Disable prefetcher (SSD systems don't need it) |
| `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters` | EnableSuperfetch | DWord | 0 | Disable Superfetch (SSD systems don't need it) |
| `HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl` | Win32PrioritySeparation | DWord | 0x26 | Short, variable, high foreground boost (best for interactive use) |
| `HKCU:\Control Panel\Desktop` | MenuShowDelay | String | 0 | Instant menu appearance (default 400ms) |
| `HKCU:\Control Panel\Desktop` | AutoEndTasks | String | 1 | Auto-close hung apps on shutdown |
| `HKCU:\Control Panel\Desktop` | WaitToKillAppTimeout | String | 2000 | Kill hung apps after 2s instead of 20s |
| `HKCU:\Control Panel\Desktop` | HungAppTimeout | String | 1000 | Detect hung apps after 1s instead of 5s |
| `HKLM:\SYSTEM\CurrentControlSet\Control` | WaitToKillServiceTimeout | String | 2000 | Kill hung services after 2s on shutdown |

---

## Preset: input-latency

Reduces mouse and keyboard input delay.

| Path | Value | Type | Data | Purpose |
|------|-------|------|------|---------|
| `HKCU:\Control Panel\Mouse` | MouseHoverTime | String | 10 | Fastest hover detection |
| `HKCU:\Control Panel\Mouse` | MouseSensitivity | String | 10 | Default 1:1 sensitivity (no acceleration at this level) |
| `HKCU:\Control Panel\Mouse` | SmoothMouseXCurve | Binary | (see below) | Linear mouse curve - removes acceleration |
| `HKCU:\Control Panel\Mouse` | SmoothMouseYCurve | Binary | (see below) | Linear mouse curve - removes acceleration |
| `HKCU:\Control Panel\Keyboard` | KeyboardDelay | String | 0 | Minimum repeat delay |
| `HKCU:\Control Panel\Keyboard` | KeyboardSpeed | String | 31 | Maximum repeat rate |
| `HKCU:\Control Panel\Desktop` | ForegroundLockTimeout | DWord | 0 | Instant foreground window switching |

### Mouse Acceleration Curves (Linear 1:1)

To set truly linear mouse movement with no acceleration:

```powershell
# Linear X curve (no acceleration)
$xCurve = [byte[]](0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                    0xC0,0xCC,0x0C,0x00,0x00,0x00,0x00,0x00,
                    0x80,0x99,0x19,0x00,0x00,0x00,0x00,0x00,
                    0x40,0x66,0x26,0x00,0x00,0x00,0x00,0x00,
                    0x00,0x33,0x33,0x00,0x00,0x00,0x00,0x00)

# Linear Y curve (no acceleration)
$yCurve = [byte[]](0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                    0x00,0x00,0x38,0x00,0x00,0x00,0x00,0x00,
                    0x00,0x00,0x70,0x00,0x00,0x00,0x00,0x00,
                    0x00,0x00,0xA8,0x00,0x00,0x00,0x00,0x00,
                    0x00,0x00,0xE0,0x00,0x00,0x00,0x00,0x00)

Set-ItemProperty -Path 'HKCU:\Control Panel\Mouse' -Name 'SmoothMouseXCurve' -Value $xCurve -Type Binary -Force
Set-ItemProperty -Path 'HKCU:\Control Panel\Mouse' -Name 'SmoothMouseYCurve' -Value $yCurve -Type Binary -Force
```
