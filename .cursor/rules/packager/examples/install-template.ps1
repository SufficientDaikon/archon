# {{PACKAGE_NAME}} Installer — Windows PowerShell
# Run: .\install.ps1

param(
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$CopilotDir = "$env:USERPROFILE\.copilot"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "  ╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║  {{PACKAGE_NAME}} Installer          ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Copilot directory
if (!(Test-Path $CopilotDir)) {
    Write-Host "  Creating $CopilotDir ..." -ForegroundColor Yellow
    if (!$DryRun) { New-Item -ItemType Directory -Path $CopilotDir -Force | Out-Null }
}

# Directories to ensure exist
$Dirs = @(
    "agents",
    "skills",
    "sdd\prompts",
    "sdd\templates",
    "sdd\specs",
    "sdd\reports"
)

foreach ($Dir in $Dirs) {
    $FullPath = Join-Path $CopilotDir $Dir
    if (!(Test-Path $FullPath)) {
        Write-Host "  Creating $Dir ..." -ForegroundColor DarkGray
        if (!$DryRun) { New-Item -ItemType Directory -Path $FullPath -Force | Out-Null }
    }
}

$Installed = @()

# Install agents
$AgentsDir = Join-Path $ScriptDir "agents"
if (Test-Path $AgentsDir) {
    Get-ChildItem -Path $AgentsDir -Filter "*.agent.md" | ForEach-Object {
        $Dest = Join-Path "$CopilotDir\agents" $_.Name
        $Exists = Test-Path $Dest
        if ($Exists -and !$Force) {
            Write-Host "  ⚠  $($_.Name) already exists (use -Force to overwrite)" -ForegroundColor Yellow
        } else {
            Write-Host "  ✅ Installing agent: $($_.Name)" -ForegroundColor Green
            if (!$DryRun) { Copy-Item $_.FullName $Dest -Force }
            $Installed += "Agent: $($_.Name)"
        }
    }
}

# Install skills
$SkillsDir = Join-Path $ScriptDir "skills"
if (Test-Path $SkillsDir) {
    Get-ChildItem -Path $SkillsDir -Directory | ForEach-Object {
        $SkillName = $_.Name
        $Dest = Join-Path "$CopilotDir\skills" $SkillName
        $Exists = Test-Path $Dest
        if ($Exists -and !$Force) {
            Write-Host "  ⚠  Skill '$SkillName' already exists (use -Force to overwrite)" -ForegroundColor Yellow
        } else {
            Write-Host "  ✅ Installing skill: $SkillName" -ForegroundColor Green
            if (!$DryRun) { Copy-Item $_.FullName $Dest -Recurse -Force }
            $Installed += "Skill: $SkillName"
        }
    }
}

# Install prompts
$PromptsDir = Join-Path $ScriptDir "prompts"
if (Test-Path $PromptsDir) {
    Get-ChildItem -Path $PromptsDir -Filter "*.md" | ForEach-Object {
        $Dest = Join-Path "$CopilotDir\sdd\prompts" $_.Name
        Write-Host "  ✅ Installing prompt: $($_.Name)" -ForegroundColor Green
        if (!$DryRun) { Copy-Item $_.FullName $Dest -Force }
        $Installed += "Prompt: $($_.Name)"
    }
}

# Install templates
$TemplatesDir = Join-Path $ScriptDir "templates"
if (Test-Path $TemplatesDir) {
    Get-ChildItem -Path $TemplatesDir | ForEach-Object {
        $Dest = Join-Path "$CopilotDir\sdd\templates" $_.Name
        Write-Host "  ✅ Installing template: $($_.Name)" -ForegroundColor Green
        if (!$DryRun) { Copy-Item $_.FullName $Dest -Force }
        $Installed += "Template: $($_.Name)"
    }
}

# Summary
Write-Host ""
Write-Host "  ── Installation Complete ──" -ForegroundColor Cyan
Write-Host ""
if ($DryRun) {
    Write-Host "  (DRY RUN — no files were actually copied)" -ForegroundColor Yellow
}
Write-Host "  Installed to: $CopilotDir" -ForegroundColor White
Write-Host "  Items installed: $($Installed.Count)" -ForegroundColor White
foreach ($Item in $Installed) {
    Write-Host "    • $Item" -ForegroundColor DarkGray
}
Write-Host ""
Write-Host "  Next: Open a Copilot CLI session and try:" -ForegroundColor White
Write-Host "    /skills              — verify skills are loaded" -ForegroundColor DarkGray
Write-Host "    @{{AGENT_NAME}} hello — invoke an agent" -ForegroundColor DarkGray
Write-Host ""
