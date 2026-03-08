# OMNISKILL Validation Script
param(
    [string]$SkillsDir = "C:\Users\tahaa\omniskill\skills"
)

function Test-SkillStructure {
    param([string]$SkillPath, [string]$SkillName)
    
    $issues = @()
    
    # Check required files
    if (-not (Test-Path (Join-Path $SkillPath "SKILL.md"))) {
        $issues += "Missing SKILL.md"
    }
    if (-not (Test-Path (Join-Path $SkillPath "manifest.yaml"))) {
        $issues += "Missing manifest.yaml"
    }
    
    # Check required directories
    $requiredDirs = @('resources', 'examples', 'tests\cases', 'overrides')
    foreach ($dir in $requiredDirs) {
        if (-not (Test-Path (Join-Path $SkillPath $dir))) {
            $issues += "Missing directory: $dir"
        }
    }
    
    # Validate manifest.yaml
    $manifestPath = Join-Path $SkillPath "manifest.yaml"
    if (Test-Path $manifestPath) {
        $content = Get-Content $manifestPath -Raw
        
        $requiredFields = @('name:', 'version:', 'description:', 'author:', 'license:', 'platforms:', 'tags:', 'triggers:', 'priority:')
        foreach ($field in $requiredFields) {
            if ($content -notmatch $field) {
                $issues += "Manifest missing field: $field"
            }
        }
        
        # Check priority is valid
        if ($content -match 'priority:\s*(\w+)') {
            $priority = $matches[1]
            if ($priority -notin @('P1', 'P2', 'P3')) {
                $issues += "Invalid priority: $priority (must be P1, P2, or P3)"
            }
        }
    }
    
    return $issues
}

Write-Host "`n=== OMNISKILL Structure Validation ===" -ForegroundColor Yellow
Write-Host "Validating: $SkillsDir`n" -ForegroundColor Gray

$allSkills = Get-ChildItem $SkillsDir -Directory | Where-Object { $_.Name -ne '_template' }
$validSkills = 0
$invalidSkills = 0
$totalIssues = 0

foreach ($skill in $allSkills) {
    $issues = Test-SkillStructure -SkillPath $skill.FullName -SkillName $skill.Name
    
    if ($issues.Count -eq 0) {
        Write-Host "✓ $($skill.Name)" -ForegroundColor Green
        $validSkills++
    } else {
        Write-Host "✗ $($skill.Name)" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "  - $issue" -ForegroundColor Yellow
        }
        $invalidSkills++
        $totalIssues += $issues.Count
    }
}

Write-Host "`n=== Validation Summary ===" -ForegroundColor Yellow
Write-Host "Total skills: $($allSkills.Count)" -ForegroundColor Gray
Write-Host "Valid: $validSkills" -ForegroundColor Green
Write-Host "Invalid: $invalidSkills" -ForegroundColor $(if ($invalidSkills -eq 0) { 'Green' } else { 'Red' })
Write-Host "Total issues: $totalIssues" -ForegroundColor $(if ($totalIssues -eq 0) { 'Green' } else { 'Yellow' })

if ($invalidSkills -eq 0) {
    Write-Host "`n✅ All skills passed validation!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some skills have issues that need attention." -ForegroundColor Yellow
}
