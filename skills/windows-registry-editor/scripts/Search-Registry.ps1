# Search-Registry.ps1
# Fast registry search with scope limiting and result caps
param(
    [Parameter(Mandatory=$true)]
    [string]$Path,

    [Parameter(Mandatory=$true)]
    [string]$Pattern,

    [ValidateSet('KeyName','ValueName','ValueData','All')]
    [string]$SearchIn = 'All',

    [int]$MaxResults = 50,

    [int]$MaxDepth = 10
)

$ErrorActionPreference = 'SilentlyContinue'
$results = [System.Collections.ArrayList]::new()
$searched = 0

function Search-Key {
    param([string]$KeyPath, [int]$Depth)

    if ($Depth -gt $MaxDepth -or $results.Count -ge $MaxResults) { return }

    $script:searched++
    if ($script:searched % 500 -eq 0) {
        Write-Host "  Searched $($script:searched) keys, found $($results.Count) matches..." -ForegroundColor DarkGray
    }

    try {
        $key = Get-Item -LiteralPath $KeyPath -EA Stop

        # Search key name
        if ($SearchIn -in 'KeyName','All') {
            if ($key.PSChildName -match $Pattern) {
                [void]$results.Add([PSCustomObject]@{
                    Type = 'KeyName'
                    Path = $KeyPath
                    Name = $key.PSChildName
                    Value = ''
                })
                if ($results.Count -ge $MaxResults) { return }
            }
        }

        # Search value names and data
        if ($SearchIn -in 'ValueName','ValueData','All') {
            foreach ($valName in $key.GetValueNames()) {
                if ($results.Count -ge $MaxResults) { return }

                $valData = $key.GetValue($valName)

                if ($SearchIn -in 'ValueName','All') {
                    if ($valName -match $Pattern) {
                        [void]$results.Add([PSCustomObject]@{
                            Type = 'ValueName'
                            Path = $KeyPath
                            Name = $valName
                            Value = $valData
                        })
                        if ($results.Count -ge $MaxResults) { return }
                    }
                }

                if ($SearchIn -in 'ValueData','All') {
                    if ("$valData" -match $Pattern) {
                        [void]$results.Add([PSCustomObject]@{
                            Type = 'ValueData'
                            Path = $KeyPath
                            Name = $valName
                            Value = $valData
                        })
                        if ($results.Count -ge $MaxResults) { return }
                    }
                }
            }
        }

        # Recurse into subkeys
        foreach ($child in (Get-ChildItem -LiteralPath $KeyPath -EA SilentlyContinue)) {
            if ($results.Count -ge $MaxResults) { return }
            Search-Key -KeyPath $child.PSPath -Depth ($Depth + 1)
        }
    } catch { }
}

Write-Host "Searching '$Path' for pattern '$Pattern' (max $MaxResults results, depth $MaxDepth)..." -ForegroundColor Cyan
Search-Key -KeyPath $Path -Depth 0

Write-Host "`nSearched $searched keys, found $($results.Count) matches." -ForegroundColor Green
$results | Format-Table -AutoSize -Wrap
