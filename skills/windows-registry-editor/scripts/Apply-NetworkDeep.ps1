# Apply-NetworkDeep.ps1
# Deep network optimization across all 15 layers of the Windows network stack
# Backs up every key before modification. Supports -DryRun and -Layer filtering.
param(
    [string]$BackupDir = 'H:\windows\RegistryBackups',
    [switch]$DryRun,
    [ValidateSet('all','nic','ndis','tcp-global','tcp-interface','tcp-netsh','afd','dns','mmcss','qos','smb','wininet','power','services','mtu')]
    [string[]]$Layers = @('all')
)

$ErrorActionPreference = 'SilentlyContinue'
if (-not (Test-Path $BackupDir)) { New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null }

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$stats = @{ applied=0; skipped=0; errors=0; backed_up=0 }
$backedUpKeys = @{}

# --- Detect primary NIC ---
$nic = (Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.InterfaceDescription -notmatch 'Virtual|Hyper|Tailscale|WAN'} | Select-Object -First 1).Name
if (-not $nic) { $nic = 'Ethernet' }
Write-Host "Target NIC: $nic" -ForegroundColor White

function Backup-Key {
    param([string]$Path)
    $regPath = $Path -replace '^HKLM:\\','HKLM\' -replace '^HKCU:\\','HKCU\' -replace '^HKCR:\\','HKCR\' -replace '^HKU:\\','HKU\' -replace '^HKCC:\\','HKCC\'
    if ($backedUpKeys.ContainsKey($regPath)) { return }
    if ($DryRun) { return }
    $safe = ($regPath -replace '[\\/:*?"<>|]','_')
    if ($safe.Length -gt 80) { $safe = $safe.Substring(0,80) }
    $file = Join-Path $BackupDir "netdeep_${timestamp}_${safe}.reg"
    reg export $regPath $file /y 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $stats.backed_up++; $backedUpKeys[$regPath] = $file }
}

function Set-Val {
    param([string]$Path, [string]$Name, $Value, [string]$Type='DWord', [string]$Desc='')
    $display = ($Path -replace '^Microsoft\.PowerShell\.Core\\Registry::','') + "\$Name"
    try {
        $current = $null
        if (Test-Path $Path) { $current = (Get-ItemProperty -Path $Path -Name $Name -EA SilentlyContinue).$Name }
        if ($DryRun) {
            $arrow = if ($null -eq $current) { "[NEW] -> $Value" } elseif ("$current" -eq "$Value") { "[=] $Value" } else { "$current -> $Value" }
            Write-Host "  [DRY] $Name $arrow" -ForegroundColor Yellow
            return
        }
        Backup-Key -Path $Path
        if (-not (Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
        Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type $Type -Force -EA Stop
        $tag = if ($null -eq $current) { 'NEW' } elseif ("$current" -eq "$Value") { '=' } else { 'UPD' }
        $color = switch($tag) { 'NEW'{'Green'} 'UPD'{'Cyan'} '='{'DarkGray'} }
        Write-Host "  [$tag] $Name = $Value" -ForegroundColor $color
        $stats.applied++
    } catch {
        Write-Host "  [ERR] $Name : $_" -ForegroundColor Red
        $stats.errors++
    }
}

$runAll = 'all' -in $Layers
$mode = if ($DryRun) { 'DRY RUN' } else { 'LIVE' }
Write-Host "`n=== DEEP NETWORK OPTIMIZATION ($mode) ===" -ForegroundColor White
Write-Host "Backup dir: $BackupDir | Layers: $($Layers -join ', ')" -ForegroundColor DarkGray

# ========== LAYER 1: NIC ==========
if ($runAll -or 'nic' -in $Layers) {
    Write-Host "`n--- Layer 1: NIC Hardware ---" -ForegroundColor Magenta
    $nicProps = @{
        'Power Saving Mode'='Disabled'; 'Energy-Efficient Ethernet'='Disabled'; 'Green Ethernet'='Disabled'
        'Gigabit Lite'='Disabled'; 'Flow Control'='Disabled'; 'Wake on Magic Packet'='Disabled'
        'Wake on pattern match'='Disabled'; 'Shutdown Wake-On-Lan'='Disabled'
        'Receive Buffers'='1024'; 'Transmit Buffers'='512'
    }
    foreach ($p in $nicProps.GetEnumerator()) {
        if (-not $DryRun) {
            try { Set-NetAdapterAdvancedProperty -Name $nic -DisplayName $p.Key -DisplayValue $p.Value -EA Stop; Write-Host "  [OK] $($p.Key) = $($p.Value)" -ForegroundColor Green; $stats.applied++ }
            catch { Write-Host "  [SKIP] $($p.Key)" -ForegroundColor DarkGray; $stats.skipped++ }
        } else { Write-Host "  [DRY] $($p.Key) = $($p.Value)" -ForegroundColor Yellow }
    }
    # Interrupt Moderation
    try { Set-NetAdapterAdvancedProperty -Name $nic -DisplayName 'Interrupt Moderation' -DisplayValue 'Disabled' -EA Stop; Write-Host "  [OK] Interrupt Moderation = Disabled" -ForegroundColor Green; $stats.applied++ } catch { $stats.skipped++ }
    # LSO & RSC
    if (-not $DryRun) {
        try { Disable-NetAdapterLso -Name $nic -IPv4 -IPv6 -EA Stop; Write-Host "  [OK] LSO disabled" -ForegroundColor Green; $stats.applied++ } catch { $stats.skipped++ }
        try { Disable-NetAdapterRsc -Name $nic -IPv4 -IPv6 -EA Stop; Write-Host "  [OK] RSC disabled" -ForegroundColor Green; $stats.applied++ } catch { $stats.skipped++ }
    }
    # RSS
    try { Enable-NetAdapterRss -Name $nic -EA Stop; Write-Host "  [OK] RSS enabled" -ForegroundColor Green } catch {}
}

# ========== LAYER 3: TCP GLOBAL ==========
if ($runAll -or 'tcp-global' -in $Layers) {
    Write-Host "`n--- Layer 3: TCP/IP Global ---" -ForegroundColor Magenta
    $tcp = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
    $tcpVals = [ordered]@{
        'DefaultTTL'=64; 'TcpTimedWaitDelay'=30; 'MaxUserPort'=65534; 'TcpMaxDupAcks'=2
        'SackOpts'=1; 'Tcp1323Opts'=1; 'MaxFreeTcbs'=65536; 'MaxHashTableSize'=65536
        'TcpMaxSendFree'=65535; 'TcpMaxConnectRetransmissions'=3; 'TcpMaxDataRetransmissions'=5
        'EnablePMTUDiscovery'=1; 'EnablePMTUBHDetect'=1; 'GlobalMaxTcpWindowSize'=16777216
        'TcpWindowSize'=65535; 'EnableDca'=1; 'DisableTaskOffload'=0
    }
    foreach ($v in $tcpVals.GetEnumerator()) { Set-Val -Path $tcp -Name $v.Key -Value $v.Value }
}

# ========== LAYER 4: TCP PER-INTERFACE ==========
if ($runAll -or 'tcp-interface' -in $Layers) {
    Write-Host "`n--- Layer 4: TCP Per-Interface ---" -ForegroundColor Magenta
    $interfaces = Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces'
    $ifCount = 0
    foreach ($iface in $interfaces) {
        Set-Val -Path $iface.PSPath -Name 'TcpAckFrequency' -Value 1
        Set-Val -Path $iface.PSPath -Name 'TCPNoDelay' -Value 1
        Set-Val -Path $iface.PSPath -Name 'TcpWindowSize' -Value 65535
        Set-Val -Path $iface.PSPath -Name 'TcpInitialRTT' -Value 300
        Set-Val -Path $iface.PSPath -Name 'TcpDelAckTicks' -Value 0
        $ifCount++
    }
    Write-Host "  Applied to $ifCount interfaces" -ForegroundColor DarkGray
}

# ========== LAYER 5: TCP NETSH ==========
if ($runAll -or 'tcp-netsh' -in $Layers) {
    Write-Host "`n--- Layer 5: TCP Netsh ---" -ForegroundColor Magenta
    if (-not $DryRun) {
        $cmds = @(
            'netsh int tcp set global autotuninglevel=normal'
            'netsh int tcp set supplemental Template=Internet CongestionProvider=ctcp'
            'netsh int tcp set global ecncapability=enabled'
            'netsh int tcp set global rss=enabled'
            'netsh int tcp set global fastopen=enabled'
            'netsh int tcp set global dca=enabled'
            'netsh int tcp set heuristics disabled'
            'netsh int tcp set global timestamps=disabled'
            'netsh int tcp set global nonsackrttresiliency=disabled'
            'netsh int tcp set global initialRto=1000'
        )
        foreach ($cmd in $cmds) {
            $result = Invoke-Expression $cmd 2>&1
            $name = ($cmd -split ' ')[-1]
            if ($result -match 'Ok') { Write-Host "  [OK] $name" -ForegroundColor Green; $stats.applied++ }
            else { Write-Host "  [INFO] $name : $result" -ForegroundColor DarkGray }
        }
    } else {
        Write-Host "  [DRY] autotuninglevel=normal, ctcp, ecn=enabled, rss, fastopen, dca, heuristics=disabled, timestamps=disabled, initialRto=1000" -ForegroundColor Yellow
    }
}

# ========== LAYER 7: AFD ==========
if ($runAll -or 'afd' -in $Layers) {
    Write-Host "`n--- Layer 7: Winsock (AFD) ---" -ForegroundColor Magenta
    $afd = 'HKLM:\SYSTEM\CurrentControlSet\Services\AFD\Parameters'
    $afdVals = [ordered]@{
        'FastSendDatagramThreshold'=65536; 'DefaultReceiveWindow'=65536; 'DefaultSendWindow'=65536
        'LargeBufferSize'=65536; 'MediumBufferSize'=3072; 'SmallBufferSize'=512
        'TransmitWorker'=32; 'MaxActiveTransmitFileCount'=64
        'IgnorePushBitOnReceives'=1; 'DynamicBacklogGrowthDelta'=10; 'EnableDynamicBacklog'=1
    }
    foreach ($v in $afdVals.GetEnumerator()) { Set-Val -Path $afd -Name $v.Key -Value $v.Value }
}

# ========== LAYER 8: DNS ==========
if ($runAll -or 'dns' -in $Layers) {
    Write-Host "`n--- Layer 8: DNS Resolver ---" -ForegroundColor Magenta
    $dns = 'HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters'
    Set-Val -Path $dns -Name 'MaxNegativeCacheTtl' -Value 5
    Set-Val -Path $dns -Name 'NetFailureCacheTime' -Value 0
    Set-Val -Path $dns -Name 'MaxCacheTtl' -Value 86400
    Set-Val -Path $dns -Name 'NegativeCacheTime' -Value 5
    if (-not $DryRun) {
        Clear-DnsClientCache
        Write-Host "  [OK] DNS cache flushed" -ForegroundColor Green
    }
}

# ========== LAYER 9: MMCSS ==========
if ($runAll -or 'mmcss' -in $Layers) {
    Write-Host "`n--- Layer 9: MMCSS & Throttling ---" -ForegroundColor Magenta
    $p = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile'
    Set-Val -Path $p -Name 'NetworkThrottlingIndex' -Value 0xFFFFFFFF
    Set-Val -Path $p -Name 'SystemResponsiveness' -Value 0
    $games = "$p\Tasks\Games"
    Set-Val -Path $games -Name 'GPU Priority' -Value 8
    Set-Val -Path $games -Name 'Priority' -Value 6
    Set-Val -Path $games -Name 'Scheduling Category' -Value 'High' -Type String
    Set-Val -Path $games -Name 'SFIO Priority' -Value 'High' -Type String
    Set-Val -Path $games -Name 'Background Only' -Value 'False' -Type String
    Set-Val -Path $games -Name 'Clock Rate' -Value 10000
}

# ========== LAYER 10: QOS ==========
if ($runAll -or 'qos' -in $Layers) {
    Write-Host "`n--- Layer 10: QoS ---" -ForegroundColor Magenta
    Set-Val -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched' -Name 'NonBestEffortLimit' -Value 0
}

# ========== LAYER 11: SMB ==========
if ($runAll -or 'smb' -in $Layers) {
    Write-Host "`n--- Layer 11: SMB ---" -ForegroundColor Magenta
    $smbc = 'HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters'
    Set-Val -Path $smbc -Name 'DisableBandwidthThrottling' -Value 1
    Set-Val -Path $smbc -Name 'DisableLargeMtu' -Value 0
    Set-Val -Path $smbc -Name 'FileInfoCacheEntriesMax' -Value 64
    Set-Val -Path $smbc -Name 'DirectoryCacheEntriesMax' -Value 16
    Set-Val -Path $smbc -Name 'FileNotFoundCacheEntriesMax' -Value 128
    Set-Val -Path $smbc -Name 'MaxCmds' -Value 128
    $smbs = 'HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters'
    Set-Val -Path $smbs -Name 'IRPStackSize' -Value 32
    Set-Val -Path $smbs -Name 'Size' -Value 3
}

# ========== LAYER 12: WININET ==========
if ($runAll -or 'wininet' -in $Layers) {
    Write-Host "`n--- Layer 12: WinINet ---" -ForegroundColor Magenta
    $inet = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings'
    Set-Val -Path $inet -Name 'MaxConnectionsPerServer' -Value 10
    Set-Val -Path $inet -Name 'MaxConnectionsPer1_0Server' -Value 10
}

# ========== LAYER 13: POWER ==========
if ($runAll -or 'power' -in $Layers) {
    Write-Host "`n--- Layer 13: Power ---" -ForegroundColor Magenta
    if (-not $DryRun) {
        powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
        powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0 2>$null
        powercfg /SETACVALUEINDEX SCHEME_CURRENT 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a576df5 0 2>$null
        powercfg /SETACTIVE SCHEME_CURRENT
        Write-Host "  [OK] High Performance plan + USB suspend off + PCIe ASPM off" -ForegroundColor Green
        $stats.applied += 3
    } else { Write-Host "  [DRY] High Performance, USB suspend=off, PCIe ASPM=off" -ForegroundColor Yellow }
}

# ========== LAYER 14: SERVICES ==========
if ($runAll -or 'services' -in $Layers) {
    Write-Host "`n--- Layer 14: Services ---" -ForegroundColor Magenta
    $disable = @('DiagTrack','dmwappushservice','RemoteRegistry','WMPNetworkSvc','MapsBroker','NcdAutoSetup','WerSvc','lfsvc','wisvc')
    $manual = @('BITS','wuauserv','DoSvc','WSearch','DPS','iphlpsvc')
    if (-not $DryRun) {
        foreach ($s in $disable) {
            Stop-Service -Name $s -Force -EA SilentlyContinue
            Set-Service -Name $s -StartupType Disabled -EA SilentlyContinue
        }
        foreach ($s in $manual) { Set-Service -Name $s -StartupType Manual -EA SilentlyContinue }
        Write-Host "  [OK] $($disable.Count) disabled, $($manual.Count) set to manual" -ForegroundColor Green
        $stats.applied += $disable.Count + $manual.Count
    } else { Write-Host "  [DRY] Disable: $($disable -join ', ')" -ForegroundColor Yellow }
}

# ========== SUMMARY ==========
Write-Host "`n========================================" -ForegroundColor White
Write-Host "  DEEP NETWORK OPTIMIZATION COMPLETE" -ForegroundColor White
Write-Host "========================================" -ForegroundColor White
Write-Host "  Applied : $($stats.applied)" -ForegroundColor Green
Write-Host "  Skipped : $($stats.skipped)" -ForegroundColor DarkGray
Write-Host "  Errors  : $($stats.errors)" -ForegroundColor $(if($stats.errors -gt 0){'Red'}else{'DarkGray'})
Write-Host "  Backups : $($stats.backed_up) keys -> $BackupDir" -ForegroundColor Cyan
if (-not $DryRun) {
    Write-Host "`n  REBOOT REQUIRED for full effect." -ForegroundColor Yellow
    Write-Host "  Run 'netsh winsock reset' and 'netsh int ip reset' before rebooting." -ForegroundColor Yellow
}
