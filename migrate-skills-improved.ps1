# Improved Skill Migration Script with better YAML parsing
param(
    [string]$SourceDir = "C:\Users\tahaa\.copilot\skills",
    [string]$ClaudeDir = "C:\Users\tahaa\.claude\skills",
    [string]$TargetDir = "C:\Users\tahaa\omniskill\skills"
)

function Extract-YAMLFrontmatter {
    param([string]$Content)
    
    if ($Content -match '(?s)^---\s*\n(.*?)\n---') {
        $yamlBlock = $matches[1]
        $metadata = @{}
        
        $lines = $yamlBlock -split "`n"
        $currentKey = $null
        $currentValue = ""
        
        foreach ($line in $lines) {
            if ($line -match '^\s*(\w+):\s*(.*)$') {
                # Save previous key-value if exists
                if ($currentKey) {
                    $metadata[$currentKey] = $currentValue.Trim()
                }
                
                $currentKey = $matches[1]
                $val = $matches[2].Trim()
                
                # Handle different value formats
                if ($val -match '^[">-]') {
                    $currentValue = ""  # Multi-line value
                } else {
                    $currentValue = $val
                }
            } elseif ($currentKey -and $line.Trim()) {
                # Continuation of multi-line value
                $currentValue += " " + $line.Trim()
            }
        }
        
        # Save last key-value
        if ($currentKey) {
            $metadata[$currentKey] = $currentValue.Trim()
        }
        
        return $metadata
    }
    
    return @{}
}

function Extract-Tags {
    param([string]$Name, [string]$Description)
    
    $tags = @()
    
    # Domain-specific tags
    if ($Name -match 'godot|gdscript|particles') { 
        $tags += 'godot'
        $tags += 'game-dev'
        $tags += 'gdscript'
    }
    if ($Name -match 'django') { 
        $tags += 'django'
        $tags += 'python'
        $tags += 'backend'
        $tags += 'web-framework'
    }
    if ($Name -match 'react|vercel') { 
        $tags += 'react'
        $tags += 'frontend'
        $tags += 'javascript'
    }
    if ($Name -match 'ui-|ux-|design|wireframe') { 
        $tags += 'design'
        $tags += 'ui-ux'
    }
    if ($Name -match 'frontend') { 
        $tags += 'frontend'
        $tags += 'web-development'
    }
    if ($Name -match 'backend') { 
        $tags += 'backend'
        $tags += 'api'
    }
    if ($Name -match 'test|qa|e2e') { 
        $tags += 'testing'
        $tags += 'quality-assurance'
    }
    if ($Name -match 'mcp') { 
        $tags += 'mcp'
        $tags += 'integration'
        $tags += 'model-context-protocol'
    }
    if ($Name -match 'capacitor') { 
        $tags += 'mobile'
        $tags += 'capacitor'
        $tags += 'hybrid-apps'
    }
    if ($Name -match 'mobile') { 
        $tags += 'mobile'
        $tags += 'ios'
        $tags += 'android'
    }
    
    # Methodology tags
    if ($Description -match 'spec|specification|implementation|review') { 
        $tags += 'spec-driven-development'
    }
    if ($Description -match 'best practices|patterns|guidelines') { 
        $tags += 'best-practices'
    }
    if ($Description -match 'architecture|structure|design') { 
        $tags += 'architecture'
    }
    if ($Name -match 'debug') { 
        $tags += 'debugging'
        $tags += 'troubleshooting'
    }
    
    return ($tags | Select-Object -Unique)
}

function Extract-Triggers {
    param([string]$Description)
    
    $keywords = @()
    
    # Extract quoted phrases from description
    $matches = [regex]::Matches($Description, '"([^"]+)"')
    foreach ($match in $matches) {
        $keywords += $match.Groups[1].Value
    }
    
    # Common trigger patterns
    if ($Description -match 'Use when ([^.]+)') {
        $trigger = $matches[1]
        # Extract key phrases
        if ($trigger -match 'building|creating|implementing|writing|developing') {
            $keywords += $trigger
        }
    }
    
    # Extract from "Triggers on" phrase
    if ($Description -match 'Triggers on ([^.]+)') {
        $triggerText = $matches[1]
        # Split by commas and clean
        $triggerText -split ',' | ForEach-Object {
            $t = $_ -replace 'tasks involving', '' -replace 'or when', ''
            $t = $t.Trim()
            if ($t -and $t.Length -gt 5) {
                $keywords += $t
            }
        }
    }
    
    return ($keywords | Select-Object -Unique | Where-Object { $_.Length -gt 0 })
}

function Determine-Priority {
    param([string]$Name)
    
    # P1: Core/Essential skills
    $p1Skills = @(
        'implementer', 'spec-writer', 'reviewer', 
        'systematic-debugging', 'writing-skills', 'find-skills'
    )
    
    # P3: Specialized/Index skills
    $p3Skills = @(
        'packager', 'skills-index', 'mcp-server-index', 
        'omega-gdscript-expert'
    )
    
    if ($p1Skills -contains $Name) { return 'P1' }
    if ($p3Skills -contains $Name) { return 'P3' }
    
    return 'P2'
}

function Create-Manifest {
    param(
        [string]$Name,
        [string]$Description,
        [array]$Tags,
        [array]$Keywords
    )
    
    $priority = Determine-Priority -Name $Name
    
    # Clean description - remove quotes if present
    $cleanDesc = $Description -replace '"', ''
    
    # Format keywords for YAML array
    $keywordsYaml = if ($Keywords.Count -gt 0) {
        ($Keywords | ForEach-Object { '"' + $_ + '"' }) -join ', '
    } else {
        ""
    }
    
    # Format tags for YAML array
    $tagsYaml = if ($Tags.Count -gt 0) {
        ($Tags | ForEach-Object { '"' + $_ + '"' }) -join ', '
    } else {
        ""
    }
    
    $manifest = @"
name: $Name
version: 1.0.0
description: "$cleanDesc"
author: tahaa
license: MIT
platforms: [claude-code, copilot-cli, cursor, windsurf, antigravity]
tags: [$tagsYaml]
triggers:
  keywords: [$keywordsYaml]
  patterns: []
priority: $priority
"@
    
    return $manifest
}

function Migrate-Skill {
    param(
        [string]$SourcePath,
        [string]$SkillName
    )
    
    Write-Host "Migrating: $SkillName" -ForegroundColor Cyan
    
    # Create target directory
    $targetPath = Join-Path $TargetDir $SkillName
    New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
    
    # Copy SKILL.md
    $skillMdSource = Join-Path $SourcePath "SKILL.md"
    $skillMdTarget = Join-Path $targetPath "SKILL.md"
    
    if (-not (Test-Path $skillMdSource)) {
        Write-Host "  ✗ SKILL.md not found!" -ForegroundColor Red
        return
    }
    
    Copy-Item $skillMdSource $skillMdTarget -Force
    
    # Read and parse SKILL.md
    $skillContent = Get-Content $skillMdSource -Raw
    $metadata = Extract-YAMLFrontmatter -Content $skillContent
    
    # Get description
    $description = if ($metadata['description']) {
        $metadata['description']
    } else {
        "Skill: $SkillName"
    }
    
    # Extract tags and triggers
    $tags = Extract-Tags -Name $SkillName -Description $description
    $keywords = Extract-Triggers -Description $description
    
    # Create manifest
    $manifest = Create-Manifest -Name $SkillName -Description $description -Tags $tags -Keywords $keywords
    $manifestPath = Join-Path $targetPath "manifest.yaml"
    Set-Content -Path $manifestPath -Value $manifest -Encoding UTF8
    
    # Create directory structure
    $dirs = @('resources', 'examples', 'tests\cases', 'overrides')
    foreach ($dir in $dirs) {
        $dirPath = Join-Path $targetPath $dir
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        New-Item -ItemType File -Path (Join-Path $dirPath ".gitkeep") -Force | Out-Null
    }
    
    # Copy additional content
    @('examples', 'templates', 'scripts', 'reference') | ForEach-Object {
        $sourceExtra = Join-Path $SourcePath $_
        if (Test-Path $sourceExtra) {
            $targetExtra = if ($_ -eq 'templates' -or $_ -eq 'examples') {
                Join-Path $targetPath "examples"
            } else {
                Join-Path $targetPath "resources"
            }
            
            Copy-Item "$sourceExtra\*" $targetExtra -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Host "  ✓ Completed" -ForegroundColor Green
}

# Main execution
Write-Host "`n=== OMNISKILL Migration (Improved) ===" -ForegroundColor Yellow
Write-Host "Target: $TargetDir`n" -ForegroundColor Gray

# Ensure target exists
New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

# Process .copilot skills
$skillDirs = Get-ChildItem $SourceDir -Directory
Write-Host "Processing $($skillDirs.Count) skills from .copilot/skills`n" -ForegroundColor Yellow

foreach ($skillDir in $skillDirs) {
    Migrate-Skill -SourcePath $skillDir.FullName -SkillName $skillDir.Name
}

# Process additional .claude skills
$additionalSkills = @('backend-development', 'frontend-design', 'react-best-practices', 'systematic-debugging', 'godot-debugging')
Write-Host "`nProcessing additional skills from .claude/skills`n" -ForegroundColor Yellow

foreach ($skillName in $additionalSkills) {
    $claudeSkillPath = Join-Path $ClaudeDir $skillName
    if (Test-Path $claudeSkillPath) {
        Migrate-Skill -SourcePath $claudeSkillPath -SkillName $skillName
    } else {
        Write-Host "  ⚠ Not found: $skillName" -ForegroundColor Yellow
    }
}

$totalSkills = (Get-ChildItem $TargetDir -Directory).Count
Write-Host "`n=== Migration Complete ===" -ForegroundColor Green
Write-Host "Total skills migrated: $totalSkills" -ForegroundColor Green
Write-Host "Location: $TargetDir" -ForegroundColor Gray
