# Apply-Preset.ps1
# Applies registry optimization presets with automatic backup
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('network','gaming','privacy','performance','input-latency','all')]
    [string]$Preset,

    [string]$BackupDir = 'H:\windows\RegistryBackups',

    [switch]$DryRun,

    [switch]$Force
)

$ErrorActionPreference = 'Stop'

# Ensure backup directory exists
if (-not (Test-Path $BackupDir)) { New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null }

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$applied = 0
$skipped = 0
$errors = 0

function Set-RegValue {
    param(
        [string]$Path,
        [string]$Name,
        $Value,
        [string]$Type = 'DWord',
        [string]$Description = ''
    )

    $displayPath = $Path -replace '^Microsoft\.PowerShell\.Core\\Registry::', ''

    try {
        # Get current value for comparison
        $current = $null
        if (Test-Path $Path) {
            $current = Get-ItemProperty -Path $Path -Name $Name -EA SilentlyContinue | Select-Object -ExpandProperty $Name -EA SilentlyContinue
        }

        if ($DryRun) {
            Write-Host "  [DRY RUN] $displayPath\$Name : $current -> $Value ($Type)" -ForegroundColor Yellow
            if ($Description) { Write-Host "            $Description" -ForegroundColor DarkGray }
            return
        }

        # Create key if it doesn't exist
        if (-not (Test-Path $Path)) {
            New-Item -Path $Path -Force | Out-Null
            Write-Host "  [CREATED] $displayPath" -ForegroundColor DarkCyan
        }

        # Backup the specific key before modification
        $regPath = ($Path -replace '^HKLM:\\', 'HKLM\' -replace '^HKCU:\\', 'HKCU\' -replace '^HKCR:\\', 'HKCR\' -replace '^HKU:\\', 'HKU\' -replace '^HKCC:\\', 'HKCC\')
        $safeName = ($regPath -replace '[\\/:*?"<>|]', '_').Substring(0, [Math]::Min(80, ($regPath -replace '[\\/:*?"<>|]', '_').Length))
        $backupFile = Join-Path $BackupDir "preset_${Preset}_${timestamp}_${safeName}.reg"

        if (-not (Test-Path $backupFile)) {
            reg export $regPath $backupFile /y 2>$null | Out-Null
        }

        # Apply the value
        Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type $Type -Force

        $status = if ($null -eq $current) { 'NEW' } elseif ($current -eq $Value) { 'UNCHANGED' } else { 'UPDATED' }
        $color = switch ($status) { 'NEW' { 'Green' } 'UPDATED' { 'Cyan' } 'UNCHANGED' { 'DarkGray' } }

        Write-Host "  [$status] $Name = $Value ($current -> $Value)" -ForegroundColor $color
        if ($Description) { Write-Host "           $Description" -ForegroundColor DarkGray }

        $script:applied++
    } catch {
        Write-Host "  [ERROR] $displayPath\$Name : $_" -ForegroundColor Red
        $script:errors++
    }
}

# ============================================================
# PRESET DEFINITIONS
# ============================================================

function Apply-NetworkPreset {
    Write-Host "`n=== NETWORK PRESET ===" -ForegroundColor White

    $tcp = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
    Set-RegValue -Path $tcp -Name 'DefaultTTL' -Value 64 -Description 'Standard TTL'
    Set-RegValue -Path $tcp -Name 'TcpTimedWaitDelay' -Value 30 -Description 'Faster port recycling'
    Set-RegValue -Path $tcp -Name 'MaxUserPort' -Value 65534 -Description 'Max ephemeral ports'
    Set-RegValue -Path $tcp -Name 'TcpMaxDupAcks' -Value 2 -Description 'Faster retransmit trigger'
    Set-RegValue -Path $tcp -Name 'SackOpts' -Value 1 -Description 'Selective ACK enabled'
    Set-RegValue -Path $tcp -Name 'Tcp1323Opts' -Value 1 -Description 'Window scaling enabled'
    Set-RegValue -Path $tcp -Name 'MaxFreeTcbs' -Value 65536 -Description 'TCP control block pool'
    Set-RegValue -Path $tcp -Name 'MaxHashTableSize' -Value 65536 -Description 'TCP hash table size'

    # Per-interface Nagle disable
    $interfaces = Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces'
    foreach ($iface in $interfaces) {
        Set-RegValue -Path $iface.PSPath -Name 'TcpAckFrequency' -Value 1 -Description "Immediate ACK ($($iface.PSChildName.Substring(0,8))...)"
        Set-RegValue -Path $iface.PSPath -Name 'TCPNoDelay' -Value 1 -Description "Nagle disabled ($($iface.PSChildName.Substring(0,8))...)"
    }

    # MMCSS
    $mmcss = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile'
    Set-RegValue -Path $mmcss -Name 'NetworkThrottlingIndex' -Value 0xFFFFFFFF -Description 'Network throttling disabled'
    Set-RegValue -Path $mmcss -Name 'SystemResponsiveness' -Value 10 -Description '10% background CPU reservation'

    # AFD
    $afd = 'HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters'
    Set-RegValue -Path $afd -Name 'FastSendDatagramThreshold' -Value 65536 -Description '64KB UDP fast path'
    Set-RegValue -Path $afd -Name 'DefaultReceiveWindow' -Value 65536 -Description '64KB receive buffer'
    Set-RegValue -Path $afd -Name 'DefaultSendWindow' -Value 65536 -Description '64KB send buffer'

    # QoS
    Set-RegValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched' -Name 'NonBestEffortLimit' -Value 0 -Description 'No QoS bandwidth reservation'

    # WinINet
    $inet = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings'
    Set-RegValue -Path $inet -Name 'MaxConnectionsPerServer' -Value 10 -Description '10 HTTP connections/server'
    Set-RegValue -Path $inet -Name 'MaxConnectionsPer1_0Server' -Value 10 -Description '10 HTTP/1.0 connections/server'

    # SMB
    Set-RegValue -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters' -Name 'DisableBandwidthThrottling' -Value 1 -Description 'SMB throttling disabled'

    # DNS
    $dns = 'HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters'
    Set-RegValue -Path $dns -Name 'MaxNegativeCacheTtl' -Value 5 -Description '5s negative DNS cache'
    Set-RegValue -Path $dns -Name 'NetFailureCacheTime' -Value 0 -Description 'No network failure caching'
}

function Apply-GamingPreset {
    Write-Host "`n=== GAMING PRESET ===" -ForegroundColor White

    $games = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games'
    Set-RegValue -Path $games -Name 'Scheduling Category' -Value 'High' -Type String -Description 'High thread scheduling'
    Set-RegValue -Path $games -Name 'SFIO Priority' -Value 'High' -Type String -Description 'High storage I/O'
    Set-RegValue -Path $games -Name 'GPU Priority' -Value 8 -Description 'Maximum GPU priority'
    Set-RegValue -Path $games -Name 'Priority' -Value 6 -Description 'High CPU priority'
    Set-RegValue -Path $games -Name 'Background Only' -Value 'False' -Type String -Description 'Not background-only'
    Set-RegValue -Path $games -Name 'Clock Rate' -Value 10000 -Description '1ms timer resolution'
    Set-RegValue -Path $games -Name 'Affinity' -Value 0 -Description 'All CPU cores'

    # Power throttling
    Set-RegValue -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling' -Name 'PowerThrottlingOff' -Value 1 -Description 'CPU power throttling disabled'

    # DirectX
    Set-RegValue -Path 'HKLM:\SOFTWARE\Microsoft\DirectX' -Name 'MaxPreRenderedFrames' -Value 1 -Description 'Minimum input lag'

    # GameDVR
    Set-RegValue -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR' -Name 'AppCaptureEnabled' -Value 0 -Description 'Game DVR capture off'
    Set-RegValue -Path 'HKCU:\System\GameConfigStore' -Name 'GameDVR_Enabled' -Value 0 -Description 'Game Bar recording off'
    Set-RegValue -Path 'HKCU:\System\GameConfigStore' -Name 'GameDVR_FSEBehaviorMode' -Value 2 -Description 'Prefer exclusive fullscreen'
    Set-RegValue -Path 'HKCU:\System\GameConfigStore' -Name 'GameDVR_HonorUserFSEBehaviorMode' -Value 1 -Description 'Respect fullscreen pref'
    Set-RegValue -Path 'HKCU:\System\GameConfigStore' -Name 'GameDVR_DXGIHonorFSEWindowsCompatible' -Value 1 -Description 'Honor exclusive FS for DX'
    Set-RegValue -Path 'HKCU:\System\GameConfigStore' -Name 'GameDVR_EFSEFeatureFlags' -Value 0 -Description 'Disable FSO overlay'
}

function Apply-PrivacyPreset {
    Write-Host "`n=== PRIVACY PRESET ===" -ForegroundColor White

    Set-RegValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection' -Name 'AllowTelemetry' -Value 0 -Description 'Telemetry off'
    Set-RegValue -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo' -Name 'Enabled' -Value 0 -Description 'Advertising ID off'
    Set-RegValue -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy' -Name 'TailoredExperiencesWithDiagnosticDataEnabled' -Value 0 -Description 'Tailored experiences off'
    Set-RegValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent' -Name 'DisableWindowsConsumerFeatures' -Value 1 -Description 'Consumer features off'
    Set-RegValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent' -Name 'DisableSoftLanding' -Value 1 -Description 'Windows tips off'
    Set-RegValue -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager' -Name 'SystemPaneSuggestionsEnabled' -Value 0 -Description 'Start suggestions off'
    Set-RegValue -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager' -Name 'SilentInstalledAppsEnabled' -Value 0 -Description 'Silent app installs off'
    Set-RegValue -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager' -Name 'SoftLandingEnabled' -Value 0 -Description 'Tips notifications off'
    Set-RegValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo' -Name 'DisabledByGroupPolicy' -Value 1 -Description 'Ad ID policy enforced'
    Set-RegValue -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced' -Name 'Start_TrackProgs' -Value 0 -Description 'Program tracking off'
    Set-RegValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\System' -Name 'EnableActivityFeed' -Value 0 -Description 'Activity feed off'
    Set-RegValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\System' -Name 'PublishUserActivities' -Value 0 -Description 'Activity publishing off'
    Set-RegValue -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\System' -Name 'UploadUserActivities' -Value 0 -Description 'Activity upload off'
}

function Apply-PerformancePreset {
    Write-Host "`n=== PERFORMANCE PRESET ===" -ForegroundColor White

    $mem = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'
    Set-RegValue -Path $mem -Name 'DisablePagingExecutive' -Value 1 -Description 'Keep kernel in RAM'
    Set-RegValue -Path $mem -Name 'LargeSystemCache' -Value 0 -Description 'Optimize for apps'
    Set-RegValue -Path "$mem\PrefetchParameters" -Name 'EnablePrefetcher' -Value 0 -Description 'Prefetcher off (SSD)'
    Set-RegValue -Path "$mem\PrefetchParameters" -Name 'EnableSuperfetch' -Value 0 -Description 'Superfetch off (SSD)'

    Set-RegValue -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' -Name 'Win32PrioritySeparation' -Value 0x26 -Description 'Short variable high FG boost'

    $desktop = 'HKCU:\Control Panel\Desktop'
    Set-RegValue -Path $desktop -Name 'MenuShowDelay' -Value '0' -Type String -Description 'Instant menus'
    Set-RegValue -Path $desktop -Name 'AutoEndTasks' -Value '1' -Type String -Description 'Auto-close hung apps'
    Set-RegValue -Path $desktop -Name 'WaitToKillAppTimeout' -Value '2000' -Type String -Description '2s app kill timeout'
    Set-RegValue -Path $desktop -Name 'HungAppTimeout' -Value '1000' -Type String -Description '1s hung detection'

    Set-RegValue -Path 'HKLM:\SYSTEM\CurrentControlSet\Control' -Name 'WaitToKillServiceTimeout' -Value '2000' -Type String -Description '2s service kill timeout'
}

function Apply-InputLatencyPreset {
    Write-Host "`n=== INPUT LATENCY PRESET ===" -ForegroundColor White

    $mouse = 'HKCU:\Control Panel\Mouse'
    Set-RegValue -Path $mouse -Name 'MouseHoverTime' -Value '10' -Type String -Description 'Fast hover'
    Set-RegValue -Path $mouse -Name 'MouseSensitivity' -Value '10' -Type String -Description '1:1 sensitivity'

    # Linear mouse curves
    $xCurve = [byte[]](0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xC0,0xCC,0x0C,0x00,0x00,0x00,0x00,0x00,0x80,0x99,0x19,0x00,0x00,0x00,0x00,0x00,0x40,0x66,0x26,0x00,0x00,0x00,0x00,0x00,0x00,0x33,0x33,0x00,0x00,0x00,0x00,0x00)
    $yCurve = [byte[]](0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x38,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x70,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xA8,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xE0,0x00,0x00,0x00,0x00,0x00)
    Set-RegValue -Path $mouse -Name 'SmoothMouseXCurve' -Value $xCurve -Type Binary -Description 'Linear X curve (no accel)'
    Set-RegValue -Path $mouse -Name 'SmoothMouseYCurve' -Value $yCurve -Type Binary -Description 'Linear Y curve (no accel)'

    $kb = 'HKCU:\Control Panel\Keyboard'
    Set-RegValue -Path $kb -Name 'KeyboardDelay' -Value '0' -Type String -Description 'Min repeat delay'
    Set-RegValue -Path $kb -Name 'KeyboardSpeed' -Value '31' -Type String -Description 'Max repeat rate'

    Set-RegValue -Path 'HKCU:\Control Panel\Desktop' -Name 'ForegroundLockTimeout' -Value 0 -Description 'Instant window focus'
}

# ============================================================
# MAIN
# ============================================================

$mode = if ($DryRun) { 'DRY RUN' } else { 'LIVE' }
Write-Host "Registry Optimization - Preset: $Preset ($mode)" -ForegroundColor White
Write-Host "Backup directory: $BackupDir" -ForegroundColor DarkGray
Write-Host "Timestamp: $timestamp" -ForegroundColor DarkGray

switch ($Preset) {
    'network'       { Apply-NetworkPreset }
    'gaming'        { Apply-GamingPreset }
    'privacy'       { Apply-PrivacyPreset }
    'performance'   { Apply-PerformancePreset }
    'input-latency' { Apply-InputLatencyPreset }
    'all' {
        Apply-NetworkPreset
        Apply-GamingPreset
        Apply-PrivacyPreset
        Apply-PerformancePreset
        Apply-InputLatencyPreset
    }
}

Write-Host "`n=== SUMMARY ===" -ForegroundColor White
Write-Host "Applied: $applied | Skipped: $skipped | Errors: $errors" -ForegroundColor $(if($errors -gt 0){'Red'}else{'Green'})
if (-not $DryRun) {
    Write-Host "Backups saved to: $BackupDir" -ForegroundColor DarkGray
    Write-Host "`nSome changes require a REBOOT to take effect." -ForegroundColor Yellow
}
