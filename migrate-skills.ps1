# Skill Migration Script to OMNISKILL Format
param(
    [string]$SourceDir = "C:\Users\tahaa\.copilot\skills",
    [string]$ClaudeDir = "C:\Users\tahaa\.claude\skills",
    [string]$TargetDir = "C:\Users\tahaa\omniskill\skills"
)

function Extract-SkillMetadata {
    param([string]$SkillMdPath)
    
    $content = Get-Content $SkillMdPath -Raw
    
    # Extract YAML frontmatter
    if ($content -match '(?s)^---\s*\n(.*?)\n---') {
        $yaml = $matches[1]
        
        # Parse YAML
        $metadata = @{}
        $yaml -split "`n" | ForEach-Object {
            if ($_ -match '^(\w+):\s*(.+)$') {
                $key = $matches[1]
                $value = $matches[2].Trim()
                if ($value -match '^[">](.*)') {
                    $value = $matches[1].Trim()
                }
                $metadata[$key] = $value
            }
        }
        
        return $metadata
    }
    
    return @{}
}

function Determine-Priority {
    param([string]$Name, [string]$Description)
    
    # P1: Core/Framework skills
    $p1 = @('implementer', 'spec-writer', 'reviewer', 'systematic-debugging', 'writing-skills', 'find-skills')
    
    # P3: Nice-to-have/specialized
    $p3 = @('packager', 'skills-index', 'mcp-server-index', 'omega-gdscript-expert')
    
    if ($p1 -contains $Name) { return 'P1' }
    if ($p3 -contains $Name) { return 'P3' }
    
    return 'P2'
}

function Extract-Tags {
    param([string]$Name, [string]$Description)
    
    $tags = @()
    
    # Domain tags
    if ($Name -match 'godot|gdscript|particles') { $tags += 'godot', 'game-dev' }
    if ($Name -match 'django') { $tags += 'django', 'python', 'backend' }
    if ($Name -match 'react|vercel|frontend|mobile') { $tags += 'frontend', 'react' }
    if ($Name -match 'ui|ux|design|wireframe') { $tags += 'design', 'ui-ux' }
    if ($Name -match 'test|qa|e2e') { $tags += 'testing', 'quality' }
    if ($Name -match 'mcp') { $tags += 'mcp', 'integration' }
    if ($Name -match 'capacitor') { $tags += 'mobile', 'capacitor' }
    
    # Methodology tags
    if ($Description -match 'spec|implementation|review') { $tags += 'spec-driven-development' }
    if ($Description -match 'best practices|patterns|guidelines') { $tags += 'best-practices' }
    if ($Description -match 'architecture|structure') { $tags += 'architecture' }
    
    return $tags | Select-Object -Unique
}

function Extract-Triggers {
    param([string]$Content, [string]$Description)
    
    $keywords = @()
    $patterns = @()
    
    # Extract from "When to Use" section
    if ($Content -match '(?s)##\s*When to Use.*?\n(.*?)(?=\n##|\z)') {
        $section = $matches[1]
        $section -split "`n" | ForEach-Object {
            if ($_ -match '-\s*(.+)') {
                $trigger = $matches[1].Trim()
                if ($trigger -match '"([^"]+)"') {
                    $keywords += $matches[1]
                }
            }
        }
    }
    
    # Extract from description triggers
    if ($Description -match 'Trigger[s]?.*?:?\s*(.+)') {
        $triggerText = $matches[1]
        $triggerText -split ',' | ForEach-Object {
            $t = $_.Trim()
            if ($t) { $keywords += $t }
        }
    }
    
    # Extract keyword triggers from frontmatter description
    if ($Description -match 'keywords?:\s*([^.]+)') {
        $kw = $matches[1] -split ',' | ForEach-Object { $_.Trim() }
        $keywords += $kw
    }
    
    return @{
        keywords = $keywords | Select-Object -Unique
        patterns = $patterns
    }
}

function Create-Manifest {
    param(
        [string]$Name,
        [hashtable]$Metadata,
        [string]$FullContent
    )
    
    $description = $Metadata['description']
    if (-not $description) {
        $description = "Skill: $Name"
    }
    
    $priority = Determine-Priority -Name $Name -Description $description
    $tags = Extract-Tags -Name $Name -Description $description
    $triggers = Extract-Triggers -Content $FullContent -Description $description
    
    $manifest = @"
name: $Name
version: 1.0.0
description: "$description"
author: tahaa
license: MIT
platforms: [claude-code, copilot-cli, cursor, windsurf, antigravity]
tags: [$($tags -join ', ')]
triggers:
  keywords: [$($triggers.keywords -join ', ')]
  patterns: [$($triggers.patterns -join ', ')]
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
    Copy-Item $skillMdSource $skillMdTarget -Force
    
    # Read SKILL.md for manifest creation
    $skillContent = Get-Content $skillMdSource -Raw
    $metadata = Extract-SkillMetadata -SkillMdPath $skillMdSource
    
    # Create manifest.yaml
    $manifest = Create-Manifest -Name $SkillName -Metadata $metadata -FullContent $skillContent
    $manifestPath = Join-Path $targetPath "manifest.yaml"
    Set-Content -Path $manifestPath -Value $manifest
    
    # Create empty directories with .gitkeep
    $dirs = @('resources', 'examples', 'tests\cases', 'overrides')
    foreach ($dir in $dirs) {
        $dirPath = Join-Path $targetPath $dir
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        New-Item -ItemType File -Path (Join-Path $dirPath ".gitkeep") -Force | Out-Null
    }
    
    # Copy examples/ or templates/ if they exist
    $examplesSource = Join-Path $SourcePath "examples"
    if (Test-Path $examplesSource) {
        $examplesTarget = Join-Path $targetPath "examples"
        Copy-Item "$examplesSource\*" $examplesTarget -Recurse -Force
    }
    
    $templatesSource = Join-Path $SourcePath "templates"
    if (Test-Path $templatesSource) {
        $templatesTarget = Join-Path $targetPath "examples"
        Copy-Item "$templatesSource\*" $templatesTarget -Recurse -Force
    }
    
    # Copy scripts/ if exists
    $scriptsSource = Join-Path $SourcePath "scripts"
    if (Test-Path $scriptsSource) {
        $scriptsTarget = Join-Path $targetPath "resources"
        Copy-Item "$scriptsSource\*" $scriptsTarget -Recurse -Force
    }
    
    Write-Host "  ✓ Completed: $SkillName" -ForegroundColor Green
}

# Main execution
Write-Host "`n=== OMNISKILL Migration ===" -ForegroundColor Yellow
Write-Host "Source: $SourceDir" -ForegroundColor Gray
Write-Host "Target: $TargetDir`n" -ForegroundColor Gray

# Ensure target directory exists
New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

# Migrate all skills from .copilot
$copilotSkills = Get-ChildItem $SourceDir -Directory
Write-Host "Found $($copilotSkills.Count) skills in .copilot/skills" -ForegroundColor Yellow

foreach ($skill in $copilotSkills) {
    Migrate-Skill -SourcePath $skill.FullName -SkillName $skill.Name
}

# Migrate additional skills from .claude
$additionalSkills = @('backend-development', 'frontend-design', 'react-best-practices', 'systematic-debugging', 'godot-debugging')
Write-Host "`nMigrating additional skills from .claude/skills..." -ForegroundColor Yellow

foreach ($skillName in $additionalSkills) {
    $claudeSkillPath = Join-Path $ClaudeDir $skillName
    if (Test-Path $claudeSkillPath) {
        Migrate-Skill -SourcePath $claudeSkillPath -SkillName $skillName
    } else {
        Write-Host "  ⚠ Not found: $skillName" -ForegroundColor Red
    }
}

Write-Host "`n=== Migration Complete ===" -ForegroundColor Green
Write-Host "Total skills migrated: $((Get-ChildItem $TargetDir -Directory).Count)" -ForegroundColor Green
