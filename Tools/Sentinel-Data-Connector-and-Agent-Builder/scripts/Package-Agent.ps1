<#
.SYNOPSIS
    Packages the Security Copilot agent for Security Store publishing.
.DESCRIPTION
    Builds a package.zip containing PackageManifest.yaml and AgentName/AgentManifest.yaml
    with validation checks for common publishing errors.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AgentName,

    [Parameter(Mandatory=$true)]
    [string]$PublisherName,

    [Parameter(Mandatory=$true)]
    [string]$AgentInstructionsFile,

    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "./package.zip",

    [Parameter(Mandatory=$false)]
    [string]$Version = "1.0.0",

    [Parameter(Mandatory=$false)]
    [string]$Description = "",

    [Parameter(Mandatory=$false)]
    [string]$ProgressFile = (Join-Path $PSScriptRoot "../config/progress.json")
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Packaging Security Copilot Agent ===`n"

# Validate inputs
if (-not (Test-Path $AgentInstructionsFile)) {
    Write-Host "❌ Agent instructions file not found: $AgentInstructionsFile"
    exit 1
}

# -----------------------------------------------------------------------------
# Phase 5 Security Copilot Validation Gate (HARD-BLOCK)
# -----------------------------------------------------------------------------
# Packaging is blocked until the agent instructions have been validated end-to-end
# inside a real Security Copilot workspace (all 7 scenarios pass). Validation
# status is tracked in config/progress.json under:
#   phases.5_agent_build.securityCopilotValidation.status
# Allowed terminal value to proceed: "validated"
# -----------------------------------------------------------------------------
Write-Host "Checking Phase 5 Security Copilot validation gate..."
if (-not (Test-Path $ProgressFile)) {
    Write-Host "❌ Progress file not found: $ProgressFile"
    Write-Host "   Cannot verify Phase 5 Security Copilot validation gate."
    Write-Host "   Run scripts/Test-AgentInSecurityCopilot.ps1 and update config/progress.json before packaging."
    exit 1
}

try {
    $progress = Get-Content $ProgressFile -Raw | ConvertFrom-Json
} catch {
    Write-Host "❌ Failed to parse $ProgressFile : $($_.Exception.Message)"
    exit 1
}

$scv = $progress.phases.'5_agent_build'.securityCopilotValidation
if ($null -eq $scv) {
    Write-Host "❌ phases.5_agent_build.securityCopilotValidation block missing from $ProgressFile"
    Write-Host "   Phase 5 validation gate cannot be verified. Aborting."
    exit 1
}

if ($scv.status -ne "validated") {
    Write-Host ""
    Write-Host "❌ Phase 5 Security Copilot Validation Gate: BLOCKED"
    Write-Host "   Current status: '$($scv.status)'"
    Write-Host "   Required status: 'validated'"
    Write-Host ""
    Write-Host "   The agent instructions have not been validated end-to-end in a real"
    Write-Host "   Security Copilot workspace. Phase 6 packaging cannot proceed until"
    Write-Host "   every scenario in scenarios/<slug>.json passes in Security Copilot."
    Write-Host ""
    Write-Host "   To unblock:"
    Write-Host "     1. Run: pwsh scripts/Test-AgentInSecurityCopilot.ps1"
    Write-Host "     2. Execute every scenario from scenarios/<slug>.json.scenarioCoverage[]"
    Write-Host "        in your Security Copilot workspace"
    Write-Host "        (see knowledge/security-copilot-agent-guide.md)"
    Write-Host "     3. Update config/progress.json:"
    Write-Host "          phases.5_agent_build.securityCopilotValidation.status = 'validated'"
    Write-Host "          phases.5_agent_build.securityCopilotValidation.validatedAt = <ISO-8601 UTC>"
    Write-Host "          phases.5_agent_build.securityCopilotValidation.validatedBy = <your alias>"
    Write-Host "          scenariosPassed[].result = 'pass' for all 7 entries"
    Write-Host "     4. Re-run this packaging command."
    Write-Host ""
    exit 1
}

# Defense-in-depth: confirm all 7 scenario results are 'pass'
$failedScenarios = @()
if ($scv.scenariosPassed) {
    foreach ($s in $scv.scenariosPassed) {
        if ($s.result -ne "pass") {
            $failedScenarios += "    - Scenario $($s.id) '$($s.name)': result='$($s.result)'"
        }
    }
}
if ($failedScenarios.Count -gt 0) {
    Write-Host "❌ Phase 5 status is 'validated' but $($failedScenarios.Count) scenario(s) not marked 'pass':"
    $failedScenarios | ForEach-Object { Write-Host $_ }
    Write-Host "   Resolve scenario results in config/progress.json before packaging."
    exit 1
}

Write-Host "  ✓ Phase 5 Security Copilot validation gate: PASSED"
Write-Host "    validatedAt: $($scv.validatedAt)  validatedBy: $($scv.validatedBy)"
Write-Host ""

$instructionsSource = Get-Content $AgentInstructionsFile -Raw

# -----------------------------------------------------------------------------
# Conditional _CL -> native-table rename (Phase 3 redesign)
# -----------------------------------------------------------------------------
# Tables on the native-mirror RENAME LIST are 1P native tables (written by a
# Microsoft service via diagnostic settings; classification rule documented in
# knowledge/data-ingestion-guide.md and SKILL.md). We ingest into *_CL during
# the sample-data phase, but the published agent's KQL must reference the real
# native table names. All other *_CL tables are genuine custom tables (defined
# in config/isv-schema.json or delivered by a Sentinel Solution) and must be
# preserved verbatim (the _CL suffix is part of their permanent identity).
# -----------------------------------------------------------------------------
$nativeMirrorRenameList = @('SigninLogs_CL','SecurityAlert_CL','DeviceLogonEvents_CL')

Write-Host "`nApplying conditional _CL rename (native-mirror rename list)..."

# Capture all _CL table names referenced in source (for preservation check)
$clTableRegex = '\b([A-Za-z][A-Za-z0-9]*_CL)\b'
$sourceClNames = [System.Collections.Generic.HashSet[string]]::new()
$matches = [regex]::Matches($instructionsSource, $clTableRegex)
foreach ($m in $matches) { [void]$sourceClNames.Add($m.Groups[1].Value) }

$instructions = $instructionsSource
foreach ($name in $nativeMirrorRenameList) {
    $native = $name -replace '_CL$',''
    $before = ([regex]::Matches($instructions, "\b$name\b")).Count
    if ($before -gt 0) {
        $instructions = [regex]::Replace($instructions, "\b$name\b", $native)
        Write-Host "  ✓ $name -> $native ($before occurrence$(if($before -ne 1){'s'}))"
    }
}

# Validator: (a) rename-list names must NOT appear in packaged output
#            (b) all _CL names NOT on the rename list must still appear in output
$packagingErrors = @()
foreach ($name in $nativeMirrorRenameList) {
    if ([regex]::IsMatch($instructions, "\b$name\b")) {
        $packagingErrors += "❌ Native-mirror table '$name' survived rename — packaging would publish to non-existent custom table."
    }
}
$preservedCount = 0
foreach ($name in $sourceClNames) {
    if ($nativeMirrorRenameList -contains $name) { continue }
    if (-not [regex]::IsMatch($instructions, "\b$name\b")) {
        $packagingErrors += "❌ Custom-table '$name' present in source but missing from packaged output — rename rule corrupted a table that is not on the native-mirror rename list."
    } else {
        $preservedCount++
    }
}
if ($packagingErrors.Count -gt 0) {
    Write-Host "`nPackaging rename validator FAILED:"
    $packagingErrors | ForEach-Object { Write-Host "  $_" }
    exit 1
}
Write-Host "  ✓ Validator: $preservedCount custom-table _CL name(s) preserved unchanged."

# Validation checks
Write-Host "`nRunning validation checks..."
$errors = @()

if ($instructions -notmatch "TimeGenerated > ago") {
    $errors += "⚠️  Instructions should include TimeGenerated filter (e.g., 'where TimeGenerated > ago(24h)')"
}

if ($AgentName -match " ") {
    $errors += "❌ AgentName cannot contain spaces. Use PascalCase (e.g., 'MyISVAgent')"
}

if ($PublisherName -eq "Custom" -or $PublisherName -eq "Microsoft") {
    $errors += "❌ Publisher must be ISV company name, not 'Custom' or 'Microsoft'"
}

if ($errors.Count -gt 0) {
    Write-Host "`nValidation issues found:"
    $errors | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") { exit 1 }
}

Write-Host "✅ Validation passed."

# Create temp directory structure
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) "agent-package-$(Get-Random)"
$agentDir = Join-Path $tempDir $AgentName
New-Item -ItemType Directory -Path $agentDir -Force | Out-Null

# Create PackageManifest.yaml
$packageManifest = @"
SchemaVersion: 0.1.0
Agents:
  - Name: $AgentName
    Path: ./$AgentName
"@

$packageManifest | Out-File -FilePath (Join-Path $tempDir "PackageManifest.yaml") -Encoding utf8

# Create AgentManifest.yaml
$agentManifest = @"
Name: $AgentName
DisplayName: "$AgentName"
Description: "$Description"
Version: "$Version"
Product: "$PublisherName"
Publisher: "$PublisherName"
Plan:
  Description: "Estimated < 1 SCU per invocation"
Instructions: |
$($instructions -split "`n" | ForEach-Object { "  $_" } | Out-String)
RequiredSkillsets:
  - MCP.Sentinel
Settings:
  Inputs: []
"@

$agentManifest | Out-File -FilePath (Join-Path $agentDir "AgentManifest.yaml") -Encoding utf8

Write-Host "`nPackage structure:"
Write-Host "  PackageManifest.yaml"
Write-Host "  $AgentName/"
Write-Host "    AgentManifest.yaml"

# Create zip (exclude hidden files for Mac compatibility)
if ($OutputPath -and (Test-Path $OutputPath)) {
    Remove-Item $OutputPath -Force
}

$currentDir = Get-Location
Set-Location $tempDir

if ($IsMacOS -or $IsLinux) {
    zip -r $currentDir/$OutputPath . -x ".*" -x "__MACOSX" 2>$null
} else {
    Compress-Archive -Path "$tempDir/*" -DestinationPath "$currentDir/$OutputPath" -Force
}

Set-Location $currentDir

# Cleanup
Remove-Item $tempDir -Recurse -Force

if (Test-Path $OutputPath) {
    $size = (Get-Item $OutputPath).Length
    Write-Host "`n✅ Package created: $OutputPath ($size bytes)"
    Write-Host "`n=== Next Steps ==="
    Write-Host "1. Go to Partner Center: https://partner.microsoft.com/dashboard"
    Write-Host "2. Create new Security Copilot Agent offer"
    Write-Host "3. Upload $OutputPath in Technical Configuration"
    Write-Host "4. Submit for review (allow 3-5 business days)"
} else {
    Write-Host "❌ Failed to create package."
    exit 1
}
