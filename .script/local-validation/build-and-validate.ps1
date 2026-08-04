#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build and validate a Microsoft Sentinel solution — packages with V3 tool, then runs all local validations.

.DESCRIPTION
    This script is the single entry point for building a Sentinel solution locally.
    It performs two steps in sequence:
      1. Packages the solution using createSolutionV3.ps1
      2. Runs all local validation checks (the same checks GitHub Actions CI performs)

    Designed to be called by any agent (GitHub Copilot, Cursor, Windsurf, etc.)
    or by a human developer from the command line.

.PARAMETER SolutionName
    The name of the solution folder under Solutions/.
    Example: "CrowdStrike Falcon Endpoint Protection"

.PARAMETER VersionBump
    How to increment the version. Options: patch (default), minor, major.

.PARAMETER SkipValidation
    If set, skips the validation step (packaging only).

.PARAMETER SkipPackaging
    If set, skips the packaging step (validation only).

.PARAMETER ValidationSkip
    Comma-separated list of validators to skip.
    Default: "kql,detection-schema,non-ascii,arm-ttk" (these run natively in Step 3).

.PARAMETER ReleaseNotes
    Description of what changed in this release. Added as a new row in ReleaseNotes.md.
    If omitted, the script warns that release notes were not updated.
    Example: "Added new data connector for RTEM events"

.PARAMETER Verbose
    Show detailed validation output.

.EXAMPLE
    # Build and validate CrowdStrike solution (patch version bump)
    ./build-and-validate.ps1 -SolutionName "CrowdStrike Falcon Endpoint Protection"

.EXAMPLE
    # Build with minor version bump
    ./build-and-validate.ps1 -SolutionName "CrowdStrike Falcon Endpoint Protection" -VersionBump minor

.EXAMPLE
    # Validate only (no packaging)
    ./build-and-validate.ps1 -SolutionName "CrowdStrike Falcon Endpoint Protection" -SkipPackaging

.EXAMPLE
    # Package only (no validation)
    ./build-and-validate.ps1 -SolutionName "CrowdStrike Falcon Endpoint Protection" -SkipValidation
#>

param(
    [Parameter(Mandatory = $true, Position = 0, HelpMessage = "Solution folder name under Solutions/")]
    [string]$SolutionName,

    [ValidateSet("patch", "minor", "major")]
    [string]$VersionBump = "patch",

    [switch]$SkipValidation,

    [switch]$SkipPackaging,

    [string]$ValidationSkip = "kql,detection-schema,non-ascii,arm-ttk",

    [string]$ReleaseNotes = ""
)

# =============================================================================
# SETUP
# =============================================================================

$ErrorActionPreference = "Stop"

# Find repository root
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    # Fallback: walk up from script location
    $repoRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
}
$repoRoot = $repoRoot.Replace('\', '/')

# Resolve solution name (supports partial/fuzzy matching)
$solutionsDir = Join-Path $repoRoot "Solutions"
$solutionPath = Join-Path $solutionsDir $SolutionName

if (-not (Test-Path $solutionPath)) {
    # No exact match — search for partial matches (case-insensitive)
    $searchTerms = $SolutionName -split '\s+' | Where-Object { $_.Length -gt 0 }
    $allSolutions = Get-ChildItem $solutionsDir -Directory

    # Match: every search term must appear somewhere in the folder name
    $matches = $allSolutions | Where-Object {
        $name = $_.Name
        ($searchTerms | ForEach-Object { $name -imatch [regex]::Escape($_) }) -notcontains $false
    }

    if ($matches.Count -eq 0) {
        Write-Host "❌ No solutions matching '$SolutionName'" -ForegroundColor Red
        Write-Host ""
        Write-Host "Available solutions:" -ForegroundColor Yellow
        $allSolutions | Sort-Object Name | ForEach-Object { Write-Host "  - $($_.Name)" }
        exit 2
    }
    elseif ($matches.Count -eq 1) {
        # Single match — use it automatically
        $SolutionName = $matches[0].Name
        $solutionPath = $matches[0].FullName
        Write-Host "🔍 Matched: $SolutionName" -ForegroundColor Green
        Write-Host ""
    }
    else {
        # Multiple matches — list them so the agent/user can pick
        Write-Host "⚠️  Multiple solutions match '$SolutionName':" -ForegroundColor Yellow
        Write-Host ""
        $i = 1
        foreach ($m in ($matches | Sort-Object Name)) {
            Write-Host "  $i. $($m.Name)" -ForegroundColor White
            $i++
        }
        Write-Host ""
        Write-Host "Please re-run with the exact solution name from the list above." -ForegroundColor Yellow
        exit 2
    }
}

$dataPath = Join-Path $solutionPath "Data"
if (-not (Test-Path $dataPath)) {
    Write-Host "❌ Data folder not found: $dataPath" -ForegroundColor Red
    exit 2
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Microsoft Sentinel Solution Builder                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Solution:     $SolutionName" -ForegroundColor White
Write-Host "  Version Bump: $VersionBump" -ForegroundColor White
Write-Host "  Packaging:    $(if ($SkipPackaging) { '⏭ Skipped' } else { '✅ Enabled' })" -ForegroundColor White
Write-Host "  Validation:   $(if ($SkipValidation) { '⏭ Skipped' } else { '✅ Enabled' })" -ForegroundColor White
Write-Host "  Release Notes:$(if ($ReleaseNotes) { " ✅ Provided" } else { ' ⚠️  Not provided' })" -ForegroundColor White
Write-Host ""

$overallSuccess = $true

# Report tracking
$reportEntries = [System.Collections.ArrayList]::new()
$reportMeta = @{
    SolutionName        = $SolutionName
    VersionBump         = $VersionBump
    OldVersion          = $null
    NewVersion          = $null
    PackageFile         = $null
    StartTime           = Get-Date
    VersionSynced       = $false
    ReleaseNotesUpdated = $false
    ReleaseNotesText    = $ReleaseNotes
}

# =============================================================================
# STEP 1: PACKAGE THE SOLUTION
# =============================================================================

if (-not $SkipPackaging) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  STEP 1: Packaging Solution (V3)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""

    $v3ScriptPath = Join-Path $repoRoot "Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1"

    if (-not (Test-Path $v3ScriptPath)) {
        Write-Host "❌ V3 packaging script not found: $v3ScriptPath" -ForegroundColor Red
        exit 2
    }

    try {
        # Run packaging from repo root so relative paths work
        Push-Location $repoRoot

        & $v3ScriptPath `
            -SolutionDataFolderPath $dataPath `
            -VersionMode "local" `
            -VersionBump $VersionBump

        $packagingExitCode = $LASTEXITCODE
        Pop-Location

        if ($packagingExitCode -ne 0 -and $null -ne $packagingExitCode) {
            Write-Host ""
            Write-Host "❌ Packaging failed with exit code $packagingExitCode" -ForegroundColor Red
            $overallSuccess = $false
        }
        else {
            Write-Host ""
            Write-Host "✅ Packaging completed successfully" -ForegroundColor Green

            # Show generated package files
            $packageDir = Join-Path $solutionPath "Package"
            if (Test-Path $packageDir) {
                $latestZip = Get-ChildItem $packageDir -Filter "*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                if ($latestZip) {
                    Write-Host "   📦 Package: $($latestZip.Name)" -ForegroundColor Gray
                    $reportMeta.PackageFile = "Package/$($latestZip.Name)"
                }
            }
        }
    }
    catch {
        Pop-Location -ErrorAction SilentlyContinue
        Write-Host ""
        Write-Host "❌ Packaging failed: $($_.Exception.Message)" -ForegroundColor Red
        $overallSuccess = $false
    }

    # Add packaging report entry
    $null = $reportEntries.Add(@{
        Step      = 1
        Name      = "Packaging"
        Status    = if ($overallSuccess) { "passed" } else { "failed" }
        Detail    = if ($reportMeta.PackageFile) { $reportMeta.PackageFile } else { "No package created" }
    })

    Write-Host ""
}

# =============================================================================
# STEP 1.5: READ VERSION INFO (file updates deferred until after validation)
# =============================================================================

if (-not $SkipPackaging -and $overallSuccess) {
    $mainTemplatePath = Join-Path $solutionPath "Package/mainTemplate.json"
    $releaseNotesPath = Join-Path $solutionPath "ReleaseNotes.md"

    # Read new version from the generated mainTemplate
    $newVersion = $null
    if (Test-Path $mainTemplatePath) {
        try {
            $mt = Get-Content $mainTemplatePath -Raw | ConvertFrom-Json
            $newVersion = $mt.variables._solutionVersion
            if (-not $reportMeta.NewVersion) { $reportMeta.NewVersion = $newVersion }
        }
        catch {
            Write-Host "⚠️  Could not read version from mainTemplate.json" -ForegroundColor Yellow
        }
    }

    # Read old version for report (but don't write yet)
    if ($newVersion) {
        $solutionDataFile = Get-ChildItem $dataPath -Filter "Solution_*.json" | Select-Object -First 1
        if ($solutionDataFile) {
            try {
                $solutionJson = Get-Content $solutionDataFile.FullName -Raw | ConvertFrom-Json
                $oldVersion = $solutionJson.Version
                if ($oldVersion -ne $newVersion) {
                    $reportMeta.OldVersion = $oldVersion
                    $reportMeta.NewVersion = $newVersion
                }
            }
            catch {
                Write-Host "⚠️  Could not read version from $($solutionDataFile.Name)" -ForegroundColor Yellow
            }
        }
    }

    if (-not $ReleaseNotes) {
        Write-Host ""
        Write-Host "⚠️  No release notes provided. ReleaseNotes.md will NOT be updated." -ForegroundColor Yellow
        Write-Host "   Tip: Use -ReleaseNotes `"Description of changes`" to document what changed." -ForegroundColor Yellow
        Write-Host ""
    }
}

# =============================================================================
# STEP 2: RUN LOCAL VALIDATIONS
# =============================================================================

if (-not $SkipValidation) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  STEP 2: Running Local Validations" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""

    $validateScript = Join-Path $repoRoot ".script/local-validation/validate.js"

    if (-not (Test-Path $validateScript)) {
        Write-Host "❌ Validation script not found: $validateScript" -ForegroundColor Red
        Write-Host "   Run 'npx tsc' from the repo root to compile TypeScript first." -ForegroundColor Yellow
        $overallSuccess = $false
    }
    else {
        # Build the validation command — use --json for structured output
        $solutionRelativePath = "Solutions/$SolutionName"
        $validateArgs = @("$validateScript", "--path", "$solutionRelativePath", "--json")

        if ($ValidationSkip) {
            $validateArgs += @("--skip", $ValidationSkip)
        }

        try {
            Push-Location $repoRoot
            $rawOutput = & node @validateArgs 2>&1
            $validationExitCode = $LASTEXITCODE
            Pop-Location

            # Separate JSON stdout from stderr lines
            $jsonString = ($rawOutput | Where-Object { $_ -is [string] }) -join "`n"
            $stderrLines = $rawOutput | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] }

            # Show stderr lines (warnings, progress) as-is
            $stderrLines | ForEach-Object { Write-Host $_.ToString() -ForegroundColor Yellow }

            # Try to parse JSON output and generate human-readable display
            $jsonParsed = $null
            try {
                $jsonParsed = $jsonString | ConvertFrom-Json
            }
            catch {
                # Fallback: show raw output if JSON parsing fails
                Write-Host $jsonString
            }

            if ($jsonParsed) {
                # Group results by validator and display human-readable output
                $byValidator = @{}
                foreach ($r in $jsonParsed.results) {
                    $vName = $r.validator
                    if (-not $byValidator.ContainsKey($vName)) { $byValidator[$vName] = @() }
                    $byValidator[$vName] += $r
                }

                foreach ($vName in $byValidator.Keys | Sort-Object) {
                    $vResults = $byValidator[$vName]
                    $vPassed = @($vResults | Where-Object { $_.passed -and -not $_.skipped })
                    $vFailed = @($vResults | Where-Object { -not $_.passed })
                    $vSkipped = @($vResults | Where-Object { $_.skipped })

                    if ($vFailed.Count -gt 0) {
                        Write-Host "  ❌ $vName  ($($vFailed.Count) failed, $($vPassed.Count) passed, $($vSkipped.Count) skipped)" -ForegroundColor Red
                        foreach ($f in $vFailed) {
                            Write-Host "     FAIL  $($f.filePath)" -ForegroundColor Red
                            if ($f.error) { Write-Host "           $($f.error)" -ForegroundColor Red }
                        }
                    }
                    else {
                        Write-Host "  ✅ $vName  ($($vPassed.Count) passed, $($vSkipped.Count) skipped)" -ForegroundColor Green
                    }

                    # Add report entry per validator
                    $status = if ($vFailed.Count -gt 0) { "failed" } elseif ($vPassed.Count -eq 0 -and $vSkipped.Count -gt 0) { "skipped" } else { "passed" }
                    $errors = @($vFailed | ForEach-Object { "$($_.filePath): $($_.error)" })
                    $skipReasons = @($vSkipped | Where-Object { $_.skipReason } | Select-Object -First 1 -ExpandProperty skipReason)
                    $null = $reportEntries.Add(@{
                        Step        = 2
                        Name        = $vName
                        Status      = $status
                        Passed      = $vPassed.Count
                        Failed      = $vFailed.Count
                        Skipped     = $vSkipped.Count
                        Errors      = $errors
                        SkipReason  = if ($skipReasons) { $skipReasons } else { $null }
                    })
                }

                $totalPassed = @($jsonParsed.results | Where-Object { $_.passed -and -not $_.skipped }).Count
                $totalFailed = @($jsonParsed.results | Where-Object { -not $_.passed }).Count
                $totalSkipped = @($jsonParsed.results | Where-Object { $_.skipped }).Count
                Write-Host ""
                Write-Host "  TOTAL: $($jsonParsed.results.Count) checks  |  ✅ $totalPassed passed  |  ❌ $totalFailed failed  |  ⏭ $totalSkipped skipped" -ForegroundColor Gray
            }

            if ($validationExitCode -ne 0) {
                Write-Host ""
                Write-Host "❌ Validation found errors (exit code $validationExitCode)" -ForegroundColor Red
                $overallSuccess = $false
            }
            else {
                Write-Host ""
                Write-Host "✅ All validations passed" -ForegroundColor Green
            }
        }
        catch {
            Pop-Location -ErrorAction SilentlyContinue
            Write-Host ""
            Write-Host "❌ Validation failed: $($_.Exception.Message)" -ForegroundColor Red
            $overallSuccess = $false
        }
    }

    Write-Host ""
}

# =============================================================================
# STEP 3: RUN .NET VALIDATORS (Detection Schema, Non-ASCII, KQL)
# =============================================================================

if (-not $SkipValidation) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  STEP 3: Running .NET Validators & ARM-TTK" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""

    # Check if .NET SDK is available
    $dotnetAvailable = $false
    try {
        $null = & dotnet --version 2>$null
        $dotnetAvailable = ($LASTEXITCODE -eq 0)
    }
    catch {
        $dotnetAvailable = $false
    }

    if (-not $dotnetAvailable) {
        Write-Host "⏭  .NET SDK not found — skipping Detection Schema, Non-ASCII, and KQL validators." -ForegroundColor Yellow
        Write-Host "   Install .NET SDK to enable these checks: https://dotnet.microsoft.com/download" -ForegroundColor Yellow
        Write-Host ""
        foreach ($vName in @("Detection Schema", "Non-ASCII", "KQL")) {
            $null = $reportEntries.Add(@{
                Step = 3; Name = $vName; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                Duration = [TimeSpan]::Zero; SkipReason = ".NET SDK not installed"
            })
        }
    }
    else {
        # Check if .NET Core 3.1 runtime is available (required by Detection Schema & Non-ASCII)
        $runtimes = & dotnet --list-runtimes 2>$null
        $has31 = $runtimes | Where-Object { $_ -match "Microsoft\.NETCore\.App 3\.1\." }
        # .NET 8.0 runtime (required by KQL)
        $has80 = $runtimes | Where-Object { $_ -match "Microsoft\.NETCore\.App 8\." }

        # ---------------------------------------------------------------
        # Helper: Build dotnet test --filter from solution YAML/JSON files
        # ---------------------------------------------------------------
        # The .NET test projects use [Theory]+[ClassData] which discover ALL files in the repo
        # at initialization time. We can't prevent discovery, but --filter restricts which tests
        # actually EXECUTE. This turns a 30-minute full-repo run into a 30-second scoped run.
        #
        # Display names look like: TestMethod(fileName: "SomeRule.yaml", ...)
        # We match on bare filenames. Filenames with filter-special chars ( ) | & ! are handled
        # by truncating to the safe prefix before the first special character.

        function Get-SolutionContentFiles {
            param([string]$SolPath, [string[]]$SubDirs, [string[]]$Extensions)
            $files = @()
            foreach ($sub in $SubDirs) {
                $dir = Join-Path $SolPath $sub
                if (Test-Path $dir) {
                    foreach ($ext in $Extensions) {
                        $files += Get-ChildItem $dir -Filter $ext -Recurse -File
                    }
                }
            }
            return $files
        }

        function Build-DotnetTestFilter {
            param([System.IO.FileInfo[]]$Files)
            $parts = @()
            foreach ($f in $Files) {
                $name = $f.Name
                # Truncate at first filter-special character to avoid breaking dotnet test --filter parser
                $idx = $name.IndexOfAny([char[]]@('(', ')', '|', '&', '!'))
                if ($idx -gt 0) {
                    $name = $name.Substring(0, $idx).TrimEnd(' ', '-', '_')
                }
                if ($name.Length -gt 3) {
                    $parts += "DisplayName~$name"
                }
            }
            if ($parts.Count -eq 0) { return $null }
            return ($parts -join " | ")
        }

        # Helper: Parse "Passed!  - Failed: 0, Passed: 8, Skipped: 0, Total: 8" or similar
        function Parse-DotnetTestSummary {
            param([string[]]$OutputLines)
            $summary = @{ Passed = 0; Failed = 0; Skipped = 0; Total = 0 }
            $line = $OutputLines | Where-Object { $_ -match "^(Failed|Passed)!" } | Select-Object -Last 1
            if ($line -and $line -match "Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)") {
                $summary.Failed  = [int]$Matches[1]
                $summary.Passed  = [int]$Matches[2]
                $summary.Skipped = [int]$Matches[3]
                $summary.Total   = [int]$Matches[4]
            }
            return $summary
        }

        # --- Detection Schema Validator ---
        $detectionProject = Join-Path $repoRoot ".script/tests/detectionTemplateSchemaValidation/DetectionTemplateSchemaValidation.Tests.csproj"
        if ($has31 -and (Test-Path $detectionProject)) {
            # Scope to solution's Analytic Rules only
            $detFiles = Get-SolutionContentFiles -SolPath $solutionPath -SubDirs @("Analytic Rules") -Extensions @("*.yaml")

            if ($detFiles.Count -gt 0) {
                $detFilter = Build-DotnetTestFilter -Files $detFiles
                Write-Host "  🔍 Detection Schema Validation (scoped to $SolutionName — $($detFiles.Count) files)..." -ForegroundColor White
                $detSw = [System.Diagnostics.Stopwatch]::StartNew()
                try {
                    Push-Location $repoRoot
                    $detOutput = & dotnet test $detectionProject --filter "$detFilter" -v q --nologo 2>&1
                    $detExitCode = $LASTEXITCODE
                    Pop-Location
                    $detSw.Stop()

                    $detSummary = Parse-DotnetTestSummary -OutputLines ($detOutput | ForEach-Object { "$_" })

                    if ($detExitCode -ne 0) {
                        $failLines = $detOutput | Where-Object { $_ -match "Failed|Error|FAIL" }
                        $failLines | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
                        $summaryLine = $detOutput | Where-Object { $_ -match "^(Failed|Passed)!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Red }
                        Write-Host "  ❌ Detection Schema validation failed" -ForegroundColor Red
                        $overallSuccess = $false
                    }
                    else {
                        $summaryLine = $detOutput | Where-Object { $_ -match "^Passed!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Gray }
                        Write-Host "  ✅ Detection Schema validation passed" -ForegroundColor Green
                    }

                    $detErrors = @($detOutput | Where-Object { $_ -match "Failed|FAIL" -and $_ -notmatch "^(Failed|Passed)!" } | ForEach-Object { "$_".Trim() })
                    $null = $reportEntries.Add(@{
                        Step      = 3
                        Name      = "Detection Schema"
                        Status    = if ($detExitCode -ne 0) { "failed" } else { "passed" }
                        Passed    = $detSummary.Passed
                        Failed    = $detSummary.Failed
                        Skipped   = $detSummary.Skipped
                        FileCount = $detFiles.Count
                        Duration  = $detSw.Elapsed
                        Errors    = $detErrors
                    })
                }
                catch {
                    $detSw.Stop()
                    Pop-Location -ErrorAction SilentlyContinue
                    Write-Host "  ❌ Detection Schema validation error: $($_.Exception.Message)" -ForegroundColor Red
                    $overallSuccess = $false
                    $null = $reportEntries.Add(@{
                        Step     = 3; Name = "Detection Schema"; Status = "failed"
                        Passed = 0; Failed = 0; Skipped = 0; FileCount = $detFiles.Count
                        Duration = $detSw.Elapsed; Errors = @($_.Exception.Message)
                    })
                }
            }
            else {
                Write-Host "  ⏭  Detection Schema validation skipped — no Analytic Rules found in $SolutionName." -ForegroundColor Yellow
                $null = $reportEntries.Add(@{
                    Step = 3; Name = "Detection Schema"; Status = "skipped"
                    Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = [TimeSpan]::Zero; SkipReason = "No Analytic Rules found"
                })
            }
        }
        elseif (-not $has31) {
            Write-Host "  ⏭  Detection Schema validation skipped — .NET Core 3.1 runtime not installed." -ForegroundColor Yellow
            Write-Host "     Install it from: https://dotnet.microsoft.com/download/dotnet/3.1" -ForegroundColor Yellow
            $null = $reportEntries.Add(@{
                Step = 3; Name = "Detection Schema"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                Duration = [TimeSpan]::Zero; SkipReason = ".NET Core 3.1 not installed"
            })
        }

        Write-Host ""

        # --- Non-ASCII Validator (scoped to solution's YAML/JSON files) ---
        $nonAsciiProject = Join-Path $repoRoot ".script/tests/NonAsciiValidationsTests/NonAsciiValidations.Tests.csproj"
        if ($has31 -and (Test-Path $nonAsciiProject)) {
            # Scope to solution content files (same approach as Detection Schema)
            $naFiles = Get-SolutionContentFiles -SolPath $solutionPath `
                -SubDirs @("Analytic Rules", "Hunting Queries", "Parsers", "Data Connectors", "Playbooks", "Workbooks") `
                -Extensions @("*.yaml", "*.json")

            if ($naFiles.Count -gt 0) {
                $naFilter = Build-DotnetTestFilter -Files $naFiles
                Write-Host "  🔍 Non-ASCII Validation (scoped to $SolutionName — $($naFiles.Count) files)..." -ForegroundColor White
                $naSw = [System.Diagnostics.Stopwatch]::StartNew()
                try {
                    Push-Location $repoRoot
                    $naOutput = & dotnet test $nonAsciiProject --filter "$naFilter" -v q --nologo 2>&1
                    $naExitCode = $LASTEXITCODE
                    Pop-Location
                    $naSw.Stop()

                    $naSummary = Parse-DotnetTestSummary -OutputLines ($naOutput | ForEach-Object { "$_" })

                    if ($naExitCode -ne 0) {
                        $failLines = $naOutput | Where-Object { $_ -match "Failed|Error|FAIL" }
                        $failLines | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
                        $summaryLine = $naOutput | Where-Object { $_ -match "^(Failed|Passed)!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Red }
                        Write-Host "  ❌ Non-ASCII validation failed" -ForegroundColor Red
                        $overallSuccess = $false
                    }
                    else {
                        $summaryLine = $naOutput | Where-Object { $_ -match "^Passed!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Gray }
                        Write-Host "  ✅ Non-ASCII validation passed" -ForegroundColor Green
                    }

                    $naErrors = @($naOutput | Where-Object { $_ -match "Failed|FAIL" -and $_ -notmatch "^(Failed|Passed)!" } | ForEach-Object { "$_".Trim() })
                    $null = $reportEntries.Add(@{
                        Step      = 3
                        Name      = "Non-ASCII"
                        Status    = if ($naExitCode -ne 0) { "failed" } else { "passed" }
                        Passed    = $naSummary.Passed
                        Failed    = $naSummary.Failed
                        Skipped   = $naSummary.Skipped
                        FileCount = $naFiles.Count
                        Duration  = $naSw.Elapsed
                        Errors    = $naErrors
                    })
                }
                catch {
                    $naSw.Stop()
                    Pop-Location -ErrorAction SilentlyContinue
                    Write-Host "  ❌ Non-ASCII validation error: $($_.Exception.Message)" -ForegroundColor Red
                    $overallSuccess = $false
                    $null = $reportEntries.Add(@{
                        Step = 3; Name = "Non-ASCII"; Status = "failed"
                        Passed = 0; Failed = 0; Skipped = 0; FileCount = $naFiles.Count
                        Duration = $naSw.Elapsed; Errors = @($_.Exception.Message)
                    })
                }
            }
            else {
                Write-Host "  ⏭  Non-ASCII validation skipped — no content files found in $SolutionName." -ForegroundColor Yellow
                $null = $reportEntries.Add(@{
                    Step = 3; Name = "Non-ASCII"; Status = "skipped"
                    Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = [TimeSpan]::Zero; SkipReason = "No content files found"
                })
            }
        }
        elseif (-not $has31) {
            Write-Host "  ⏭  Non-ASCII validation skipped — .NET Core 3.1 runtime not installed." -ForegroundColor Yellow
            Write-Host "     Install it from: https://dotnet.microsoft.com/download/dotnet/3.1" -ForegroundColor Yellow
            $null = $reportEntries.Add(@{
                Step = 3; Name = "Non-ASCII"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = $null
                Duration = [TimeSpan]::Zero; Scope = "entire repo"; SkipReason = ".NET Core 3.1 not installed"
            })
        }

        Write-Host ""

        # --- KQL Validator (scoped to solution) ---
        $kqlProject = Join-Path $repoRoot ".script/tests/KqlvalidationsTests/Kqlvalidations.Tests.csproj"
        if ($has80 -and (Test-Path $kqlProject)) {
            # Collect all YAML/JSON content files from the solution for scoping
            $kqlFiles = Get-SolutionContentFiles -SolPath $solutionPath `
                -SubDirs @("Analytic Rules", "Hunting Queries", "Parsers", "Data Connectors") `
                -Extensions @("*.yaml", "*.json")

            if ($kqlFiles.Count -gt 0) {
                $kqlFilter = Build-DotnetTestFilter -Files $kqlFiles
                Write-Host "  🔍 KQL Validation (scoped to $SolutionName — $($kqlFiles.Count) files)..." -ForegroundColor White

                # KQL's GitHubApiClient.Create() throws without GitHub App credentials.
                # Setting SYSTEM_PULLREQUEST_ISFORK=true bypasses credential checks and creates
                # an unauthenticated client. With no PRNUM set, it loads all files for discovery
                # but --filter ensures only the solution's tests execute.
                $previousForkFlag = $env:SYSTEM_PULLREQUEST_ISFORK
                $env:SYSTEM_PULLREQUEST_ISFORK = "true"

                $kqlSw = [System.Diagnostics.Stopwatch]::StartNew()
                try {
                    Push-Location $repoRoot
                    $kqlOutput = & dotnet test $kqlProject --filter "$kqlFilter" -v q --nologo 2>&1
                    $kqlExitCode = $LASTEXITCODE
                    Pop-Location
                    $kqlSw.Stop()

                    $kqlSummary = Parse-DotnetTestSummary -OutputLines ($kqlOutput | ForEach-Object { "$_" })

                    if ($kqlExitCode -ne 0) {
                        $failLines = $kqlOutput | Where-Object { $_ -match "Failed|Error|FAIL" }
                        $failLines | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
                        $summaryLine = $kqlOutput | Where-Object { $_ -match "^(Failed|Passed)!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Red }
                        Write-Host "  ❌ KQL validation failed" -ForegroundColor Red
                        $overallSuccess = $false
                    }
                    else {
                        $summaryLine = $kqlOutput | Where-Object { $_ -match "^Passed!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Gray }
                        Write-Host "  ✅ KQL validation passed" -ForegroundColor Green
                    }

                    $kqlErrors = @($kqlOutput | Where-Object { $_ -match "Failed|FAIL" -and $_ -notmatch "^(Failed|Passed)!" } | ForEach-Object { "$_".Trim() })
                    $null = $reportEntries.Add(@{
                        Step      = 3
                        Name      = "KQL"
                        Status    = if ($kqlExitCode -ne 0) { "failed" } else { "passed" }
                        Passed    = $kqlSummary.Passed
                        Failed    = $kqlSummary.Failed
                        Skipped   = $kqlSummary.Skipped
                        FileCount = $kqlFiles.Count
                        Duration  = $kqlSw.Elapsed
                        Errors    = $kqlErrors
                    })
                }
                catch {
                    $kqlSw.Stop()
                    Pop-Location -ErrorAction SilentlyContinue
                    Write-Host "  ❌ KQL validation error: $($_.Exception.Message)" -ForegroundColor Red
                    $overallSuccess = $false
                    $null = $reportEntries.Add(@{
                        Step = 3; Name = "KQL"; Status = "failed"
                        Passed = 0; Failed = 0; Skipped = 0; FileCount = $kqlFiles.Count
                        Duration = $kqlSw.Elapsed; Errors = @($_.Exception.Message)
                    })
                }
                finally {
                    # Restore original env var state
                    if ($previousForkFlag) {
                        $env:SYSTEM_PULLREQUEST_ISFORK = $previousForkFlag
                    }
                    else {
                        Remove-Item Env:SYSTEM_PULLREQUEST_ISFORK -ErrorAction SilentlyContinue
                    }
                }
            }
            else {
                Write-Host "  ⏭  KQL validation skipped — no content files (Analytic Rules, Hunting Queries, Parsers, Data Connectors) found in $SolutionName." -ForegroundColor Yellow
                $null = $reportEntries.Add(@{
                    Step = 3; Name = "KQL"; Status = "skipped"
                    Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = [TimeSpan]::Zero; SkipReason = "No content files found"
                })
            }
        }
        elseif (-not $has80) {
            Write-Host "  ⏭  KQL validation skipped — .NET 8.0 runtime not installed." -ForegroundColor Yellow
            Write-Host "     Install it from: https://dotnet.microsoft.com/download/dotnet/8.0" -ForegroundColor Yellow
            $null = $reportEntries.Add(@{
                Step = 3; Name = "KQL"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                Duration = [TimeSpan]::Zero; SkipReason = ".NET 8.0 not installed"
            })
        }

        Write-Host ""
    }

    # -----------------------------------------------------------------
    # ARM-TTK Validator (local — calls run-arm-ttk.ps1, same checks as entrypoint.ps1)
    # -----------------------------------------------------------------
    $packageDir = Join-Path $solutionPath "Package"
    if (Test-Path $packageDir) {
        $armTtkScript = Join-Path $repoRoot ".script/local-validation/run-arm-ttk.ps1"
        if (-not (Test-Path $armTtkScript)) {
            Write-Host "  ⏭  ARM-TTK validation skipped — run-arm-ttk.ps1 not found." -ForegroundColor Yellow
            $null = $reportEntries.Add(@{
                Step = 3; Name = "ARM-TTK"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                Duration = [TimeSpan]::Zero; SkipReason = "run-arm-ttk.ps1 not found"
            })
        }
        else {
            Write-Host "  🔍 ARM-TTK Validation (same checks as GitHub CI)..." -ForegroundColor White
            $armSw = [System.Diagnostics.Stopwatch]::StartNew()
            try {
                $armOutput = & pwsh -NoProfile -File $armTtkScript -SolutionPath $solutionPath 2>&1
                $armExitCode = $LASTEXITCODE
                $armSw.Stop()

                # Show output
                $armOutput | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }

                # Parse the summary line: ARM-TTK-SUMMARY: Pass=29 Fail=1 Total=30
                $armSummaryLine = ($armOutput | ForEach-Object { "$_" }) | Where-Object { $_ -match '^ARM-TTK-SUMMARY:' } | Select-Object -Last 1
                $armPass = 0; $armFail = 0; $armSkippedFlag = $false
                if ($armSummaryLine -match 'Pass=(\d+)\s+Fail=(\d+)\s+Total=(\d+)') {
                    $armPass = [int]$Matches[1]
                    $armFail = [int]$Matches[2]
                }
                if ($armSummaryLine -match 'Skipped=true') {
                    $armSkippedFlag = $true
                }

                if ($armSkippedFlag) {
                    Write-Host "  ⏭  ARM-TTK validation skipped — no Package/ templates found." -ForegroundColor Yellow
                    $null = $reportEntries.Add(@{
                        Step = 3; Name = "ARM-TTK"; Status = "skipped"
                        Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                        Duration = $armSw.Elapsed; SkipReason = "No templates in Package/"
                    })
                }
                elseif ($armExitCode -ne 0) {
                    Write-Host "  ❌ ARM-TTK validation failed ($armFail failed, $armPass passed)" -ForegroundColor Red
                    $overallSuccess = $false
                    $armErrors = @(($armOutput | ForEach-Object { "$_" }) | Where-Object { $_ -match '\[-\]|hardcoded|not pass|rectify' } | ForEach-Object { $_.Trim() })
                    $null = $reportEntries.Add(@{
                        Step = 3; Name = "ARM-TTK"; Status = "failed"
                        Passed = $armPass; Failed = $armFail; Skipped = 0; FileCount = 0
                        Duration = $armSw.Elapsed; Errors = $armErrors
                    })
                }
                else {
                    Write-Host "  ✅ ARM-TTK validation passed ($armPass tests)" -ForegroundColor Green
                    $null = $reportEntries.Add(@{
                        Step = 3; Name = "ARM-TTK"; Status = "passed"
                        Passed = $armPass; Failed = 0; Skipped = 0; FileCount = 0
                        Duration = $armSw.Elapsed
                    })
                }
            }
            catch {
                $armSw.Stop()
                Write-Host "  ❌ ARM-TTK validation error: $($_.Exception.Message)" -ForegroundColor Red
                $overallSuccess = $false
                $null = $reportEntries.Add(@{
                    Step = 3; Name = "ARM-TTK"; Status = "failed"
                    Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = $armSw.Elapsed; Errors = @($_.Exception.Message)
                })
            }
        }

        Write-Host ""
    }
    else {
        Write-Host "  ⏭  ARM-TTK validation skipped — Package/ folder does not exist." -ForegroundColor Yellow
        $null = $reportEntries.Add(@{
            Step = 3; Name = "ARM-TTK"; Status = "skipped"
            Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
            Duration = [TimeSpan]::Zero; SkipReason = "Package/ folder not found"
        })
        Write-Host ""
    }
}

# =============================================================================
# STEP 4: CI POWERSHELL VALIDATORS & SECRET SCANNING
# =============================================================================

if (-not $SkipValidation) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  STEP 4: CI PowerShell Validators & Secret Scanning" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  ℹ️  These validators check committed changes (git diff HEAD^ HEAD)." -ForegroundColor Gray
    Write-Host "     Commit your changes before running for full coverage." -ForegroundColor Gray
    Write-Host ""

    # Ensure powershell-yaml module is available (needed by all 3 PS validators)
    if (-not (Get-Module -ListAvailable powershell-yaml -ErrorAction SilentlyContinue)) {
        Write-Host "  📦 Installing powershell-yaml module..." -ForegroundColor Gray
        try {
            Install-Module powershell-yaml -Force -Scope CurrentUser -ErrorAction SilentlyContinue
        }
        catch {
            Write-Host "  ⚠️  Could not install powershell-yaml module — PS validators may fail." -ForegroundColor Yellow
        }
    }

    # --- Validate Field Types ---
    $fieldTypesScript = Join-Path $repoRoot ".script/package-automation/validateFieldTypes.ps1"
    if (Test-Path $fieldTypesScript) {
        Write-Host "  🔍 Field Types Validation..." -ForegroundColor White
        $ftSw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            Push-Location $repoRoot
            $ftOutput = & pwsh -NoProfile -File $fieldTypesScript `
                -runId "local-validation" `
                -pullRequestNumber 0 `
                -instrumentationKey "" `
                -baseFolderPath $repoRoot 2>&1
            $ftExitCode = $LASTEXITCODE
            Pop-Location
            $ftSw.Stop()

            # Show relevant output (filter noise)
            $ftOutput | ForEach-Object {
                $line = "$_"
                if ($line.Trim()) { Write-Host "     $line" -ForegroundColor Gray }
            }

            if ($ftExitCode -ne 0) {
                Write-Host "  ❌ Field Types validation failed" -ForegroundColor Red
                $overallSuccess = $false
                $ftErrors = @($ftOutput | Where-Object { "$_" -match "Error|FAIL|failed|invalid" } | ForEach-Object { "$_".Trim() })
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Field Types"; Status = "failed"
                    Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                    Duration = $ftSw.Elapsed; Errors = $ftErrors
                })
            }
            else {
                Write-Host "  ✅ Field Types validation passed" -ForegroundColor Green
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Field Types"; Status = "passed"
                    Passed = 1; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = $ftSw.Elapsed
                })
            }
        }
        catch {
            $ftSw.Stop()
            Pop-Location -ErrorAction SilentlyContinue
            Write-Host "  ❌ Field Types validation error: $($_.Exception.Message)" -ForegroundColor Red
            $overallSuccess = $false
            $null = $reportEntries.Add(@{
                Step = 4; Name = "Field Types"; Status = "failed"
                Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                Duration = $ftSw.Elapsed; Errors = @($_.Exception.Message)
            })
        }
    }
    else {
        Write-Host "  ⏭  Field Types validation skipped — script not found." -ForegroundColor Yellow
        $null = $reportEntries.Add(@{
            Step = 4; Name = "Field Types"; Status = "skipped"
            Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
            Duration = [TimeSpan]::Zero; SkipReason = "Script not found"
        })
    }

    Write-Host ""

    # --- Validate Classic App Insights ---
    $classicAIScript = Join-Path $repoRoot ".script/package-automation/validateClassicAppInsights.ps1"
    if (Test-Path $classicAIScript) {
        Write-Host "  🔍 Classic App Insights Validation..." -ForegroundColor White
        $caiSw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            Push-Location $repoRoot
            $caiOutput = & pwsh -NoProfile -File $classicAIScript `
                -runId "local-validation" `
                -pullRequestNumber 0 `
                -instrumentationKey "" `
                -baseFolderPath $repoRoot 2>&1
            $caiExitCode = $LASTEXITCODE
            Pop-Location
            $caiSw.Stop()

            $caiOutput | ForEach-Object {
                $line = "$_"
                if ($line.Trim()) { Write-Host "     $line" -ForegroundColor Gray }
            }

            if ($caiExitCode -ne 0) {
                Write-Host "  ❌ Classic App Insights validation failed" -ForegroundColor Red
                $overallSuccess = $false
                $caiErrors = @($caiOutput | Where-Object { "$_" -match "Error|FAIL|failed|classic|deprecated" } | ForEach-Object { "$_".Trim() })
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Classic App Insights"; Status = "failed"
                    Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                    Duration = $caiSw.Elapsed; Errors = $caiErrors
                })
            }
            else {
                Write-Host "  ✅ Classic App Insights validation passed" -ForegroundColor Green
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Classic App Insights"; Status = "passed"
                    Passed = 1; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = $caiSw.Elapsed
                })
            }
        }
        catch {
            $caiSw.Stop()
            Pop-Location -ErrorAction SilentlyContinue
            Write-Host "  ❌ Classic App Insights validation error: $($_.Exception.Message)" -ForegroundColor Red
            $overallSuccess = $false
            $null = $reportEntries.Add(@{
                Step = 4; Name = "Classic App Insights"; Status = "failed"
                Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                Duration = $caiSw.Elapsed; Errors = @($_.Exception.Message)
            })
        }
    }
    else {
        Write-Host "  ⏭  Classic App Insights validation skipped — script not found." -ForegroundColor Yellow
        $null = $reportEntries.Add(@{
            Step = 4; Name = "Classic App Insights"; Status = "skipped"
            Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
            Duration = [TimeSpan]::Zero; SkipReason = "Script not found"
        })
    }

    Write-Host ""

    # --- Hyperlink Validation ---
    $hyperlinkScript = Join-Path $repoRoot ".script/package-automation/hyperlink-validation.ps1"
    if (Test-Path $hyperlinkScript) {
        # Check network connectivity first (hyperlink validation makes HTTP requests)
        $networkAvailable = $false
        try {
            $null = Invoke-WebRequest -Uri "https://www.microsoft.com" -Method Head -TimeoutSec 5 -ErrorAction Stop
            $networkAvailable = $true
        }
        catch { $networkAvailable = $false }

        if (-not $networkAvailable) {
            Write-Host "  ⏭  Hyperlink validation skipped — network not available." -ForegroundColor Yellow
            $null = $reportEntries.Add(@{
                Step = 4; Name = "Hyperlink Validation"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                Duration = [TimeSpan]::Zero; SkipReason = "Network not available"
            })
        }
        else {
            Write-Host "  🔍 Hyperlink Validation (slow — makes HTTP requests with 20s timeout per URL)..." -ForegroundColor White
            $hlSw = [System.Diagnostics.Stopwatch]::StartNew()
            try {
                Push-Location $repoRoot
                $hlOutput = & pwsh -NoProfile -File $hyperlinkScript `
                    -runId "local-validation" `
                    -pullRequestNumber 0 `
                    -instrumentationKey "" `
                    -baseFolderPath $repoRoot 2>&1
                $hlExitCode = $LASTEXITCODE
                Pop-Location
                $hlSw.Stop()

                $hlOutput | ForEach-Object {
                    $line = "$_"
                    if ($line.Trim()) { Write-Host "     $line" -ForegroundColor Gray }
                }

                if ($hlExitCode -ne 0) {
                    Write-Host "  ❌ Hyperlink validation failed" -ForegroundColor Red
                    $overallSuccess = $false
                    $hlErrors = @($hlOutput | Where-Object { "$_" -match "Error|FAIL|failed|404|500|broken" } | ForEach-Object { "$_".Trim() })
                    $null = $reportEntries.Add(@{
                        Step = 4; Name = "Hyperlink Validation"; Status = "failed"
                        Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                        Duration = $hlSw.Elapsed; Errors = $hlErrors
                    })
                }
                else {
                    Write-Host "  ✅ Hyperlink validation passed" -ForegroundColor Green
                    $null = $reportEntries.Add(@{
                        Step = 4; Name = "Hyperlink Validation"; Status = "passed"
                        Passed = 1; Failed = 0; Skipped = 0; FileCount = 0
                        Duration = $hlSw.Elapsed
                    })
                }
            }
            catch {
                $hlSw.Stop()
                Pop-Location -ErrorAction SilentlyContinue
                Write-Host "  ❌ Hyperlink validation error: $($_.Exception.Message)" -ForegroundColor Red
                $overallSuccess = $false
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Hyperlink Validation"; Status = "failed"
                    Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                    Duration = $hlSw.Elapsed; Errors = @($_.Exception.Message)
                })
            }
        }
    }
    else {
        Write-Host "  ⏭  Hyperlink validation skipped — script not found." -ForegroundColor Yellow
        $null = $reportEntries.Add(@{
            Step = 4; Name = "Hyperlink Validation"; Status = "skipped"
            Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
            Duration = [TimeSpan]::Zero; SkipReason = "Script not found"
        })
    }

    Write-Host ""

    # --- TruffleHog Secret Scanning ---
    $trufflehogCmd = Get-Command trufflehog -ErrorAction SilentlyContinue
    if ($trufflehogCmd) {
        Write-Host "  🔍 TruffleHog Secret Scanning..." -ForegroundColor White
        $thSw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $excludePathsFile = Join-Path $repoRoot ".script/SecretScanning/Excludepathlist"
            $thArgs = @("git", "file://$repoRoot", "--only-verified", "--fail")
            if (Test-Path $excludePathsFile) {
                $thArgs += @("--exclude-paths=$excludePathsFile")
            }

            Push-Location $repoRoot
            $thOutput = & trufflehog @thArgs 2>&1
            $thExitCode = $LASTEXITCODE
            Pop-Location
            $thSw.Stop()

            $thOutput | ForEach-Object {
                $line = "$_"
                if ($line.Trim()) { Write-Host "     $line" -ForegroundColor Gray }
            }

            if ($thExitCode -ne 0) {
                Write-Host "  ❌ TruffleHog found verified secrets!" -ForegroundColor Red
                $overallSuccess = $false
                $thErrors = @($thOutput | Where-Object { "$_" -match "Found|Detector|Raw|File|Commit" } | ForEach-Object { "$_".Trim() })
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "TruffleHog (Secrets)"; Status = "failed"
                    Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                    Duration = $thSw.Elapsed; Errors = $thErrors
                })
            }
            else {
                Write-Host "  ✅ TruffleHog scan passed — no verified secrets found" -ForegroundColor Green
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "TruffleHog (Secrets)"; Status = "passed"
                    Passed = 1; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = $thSw.Elapsed
                })
            }
        }
        catch {
            $thSw.Stop()
            Pop-Location -ErrorAction SilentlyContinue
            Write-Host "  ❌ TruffleHog error: $($_.Exception.Message)" -ForegroundColor Red
            $overallSuccess = $false
            $null = $reportEntries.Add(@{
                Step = 4; Name = "TruffleHog (Secrets)"; Status = "failed"
                Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                Duration = $thSw.Elapsed; Errors = @($_.Exception.Message)
            })
        }
    }
    else {
        Write-Host "  ⏭  TruffleHog secret scanning skipped — trufflehog CLI not installed." -ForegroundColor Yellow
        Write-Host "     Install from: https://github.com/trufflesecurity/trufflehog#installation" -ForegroundColor Yellow
        $null = $reportEntries.Add(@{
            Step = 4; Name = "TruffleHog (Secrets)"; Status = "skipped"
            Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
            Duration = [TimeSpan]::Zero; SkipReason = "trufflehog CLI not installed"
        })
    }

    Write-Host ""
}

# =============================================================================
# APPLY FILE UPDATES (only if all validations passed)
# =============================================================================

if (-not $SkipPackaging -and $newVersion) {
    if ($overallSuccess) {
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "  Applying Version Sync & Release Notes" -ForegroundColor Cyan
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""

        # Update Solution_*.json version
        $solutionDataFile = Get-ChildItem $dataPath -Filter "Solution_*.json" | Select-Object -First 1
        if ($solutionDataFile) {
            try {
                $solutionJson = Get-Content $solutionDataFile.FullName -Raw | ConvertFrom-Json
                if ($solutionJson.Version -ne $newVersion) {
                    $solutionJson.Version = $newVersion
                    $solutionJson | ConvertTo-Json -Depth 100 | Set-Content $solutionDataFile.FullName -Encoding UTF8
                    Write-Host "✅ Solution data file version updated: $($reportMeta.OldVersion) → $newVersion" -ForegroundColor Green
                    Write-Host "   📝 File: $($solutionDataFile.FullName)" -ForegroundColor Gray
                    $reportMeta.VersionSynced = $true
                }
            }
            catch {
                Write-Host "⚠️  Could not update version in $($solutionDataFile.Name): $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }

        # Update ReleaseNotes.md
        $releaseNotesPath = Join-Path $solutionPath "ReleaseNotes.md"
        if ($ReleaseNotes) {
            $todayFormatted = (Get-Date).ToString("dd-MM-yyyy")
            $newRow = "| $newVersion       | $todayFormatted                     | $ReleaseNotes |"

            if (Test-Path $releaseNotesPath) {
                $lines = Get-Content $releaseNotesPath
                if ($lines.Count -ge 2) {
                    $updatedLines = @($lines[0], $lines[1], $newRow) + $lines[2..($lines.Count - 1)]
                }
                else {
                    $updatedLines = $lines + @($newRow)
                }
                $updatedLines | Set-Content $releaseNotesPath -Encoding UTF8
            }
            else {
                $header = @(
                    "| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                             |",
                    "|-------------|--------------------------------|--------------------------------------------------------------------------------|",
                    $newRow
                )
                $header | Set-Content $releaseNotesPath -Encoding UTF8
            }

            Write-Host "✅ Release notes updated: v$newVersion — $ReleaseNotes" -ForegroundColor Green
            Write-Host "   📝 File: $releaseNotesPath" -ForegroundColor Gray
            $reportMeta.ReleaseNotesUpdated = $true
        }

        Write-Host ""
    }
    else {
        Write-Host ""
        Write-Host "⚠️  Version sync and release notes skipped — validation failed. No files were modified." -ForegroundColor Yellow
        Write-Host ""
    }
}

# =============================================================================
# FINAL SUMMARY — Inline Build & Validation Report
# =============================================================================

function Format-Duration {
    param([TimeSpan]$ts)
    if ($ts.TotalMinutes -ge 1) {
        return "{0}m {1}s" -f [math]::Floor($ts.TotalMinutes), $ts.Seconds
    }
    return "{0}s" -f [math]::Floor($ts.TotalSeconds)
}

function Write-BuildReport {
    param(
        [hashtable]$Meta,
        [System.Collections.ArrayList]$Entries,
        [bool]$Success
    )

    $endTime = Get-Date
    $totalDuration = $endTime - $Meta.StartTime
    $dateStr = $endTime.ToString("yyyy-MM-dd HH:mm:ss")
    $durationStr = Format-Duration $totalDuration

    # Version display
    $versionStr = if ($Meta.OldVersion -and $Meta.NewVersion -and $Meta.OldVersion -ne $Meta.NewVersion) {
        "$($Meta.OldVersion) → $($Meta.NewVersion) ($($Meta.VersionBump))"
    }
    elseif ($Meta.NewVersion) { $Meta.NewVersion }
    else { "N/A" }

    $w = 70  # box width

    # Build report as a string array so we can write to both stdout and file
    $lines = [System.Collections.ArrayList]::new()
    function Add-Line { param([string]$text = "") $null = $lines.Add($text) }

    Add-Line "# BUILD & VALIDATION REPORT"
    Add-Line ""
    Add-Line "Solution: $($Meta.SolutionName)"
    Add-Line "Version: $versionStr"
    Add-Line "Date: $dateStr"
    Add-Line "Duration: $durationStr"
    Add-Line "Result: $(if ($Success) { 'PASSED' } else { 'FAILED' })"
    Add-Line ""

    # --- STEP 1: PACKAGING ---
    $step1Entries = @($Entries | Where-Object { $_.Step -eq 1 })
    if ($step1Entries.Count -gt 0 -or (-not $SkipPackaging)) {
        Add-Line "## Step 1: Packaging"
        Add-Line ""
        if ($step1Entries.Count -gt 0) {
            $pkgEntry = $step1Entries[0]
            Add-Line "- Package: $($pkgEntry.Detail) ($($pkgEntry.Status))"
        }
        if ($Meta.VersionSynced) {
            Add-Line "- Version synced: $($Meta.OldVersion) -> $($Meta.NewVersion)"
        }
        if ($Meta.ReleaseNotesUpdated) {
            $rnText = if ($Meta.ReleaseNotesText.Length -gt 60) { $Meta.ReleaseNotesText.Substring(0, 57) + "..." } else { $Meta.ReleaseNotesText }
            Add-Line "- Release notes updated: $rnText"
        }
        elseif (-not $Meta.ReleaseNotesText) {
            Add-Line "- Release notes: not provided"
        }
        Add-Line ""
    }

    # --- Validation results table ---
    $allValEntries = @($Entries | Where-Object { $_.Step -in 2, 3, 4 })
    if ($allValEntries.Count -gt 0) {
        Add-Line "## Validation Results"
        Add-Line ""
        Add-Line "| Step | Validator | Status | Details |"
        Add-Line "|------|-----------|--------|---------|"

        foreach ($e in $allValEntries) {
            $stepLabel = switch ($e.Step) { 2 { "TS" } 3 { ".NET" } 4 { "CI-PS" } }
            $status = switch ($e.Status) { "passed" { "PASS" } "failed" { "FAIL" } "skipped" { "SKIP" } }
            $detailParts = @()
            if ($e.Passed -and $e.Passed -gt 0) { $detailParts += "$($e.Passed) passed" }
            if ($e.Failed -and $e.Failed -gt 0) { $detailParts += "$($e.Failed) failed" }
            if ($e.Skipped -and $e.Skipped -gt 0) { $detailParts += "$($e.Skipped) skipped" }
            if ($e.Duration -and $e.Duration.TotalSeconds -gt 0) { $detailParts += (Format-Duration $e.Duration) }
            if ($e.FileCount -and $e.FileCount -gt 0) { $detailParts += "$($e.FileCount) files" }
            if ($e.SkipReason) { $detailParts += $e.SkipReason }
            $detail = if ($detailParts.Count -gt 0) { $detailParts -join ", " } else { "-" }
            Add-Line "| $stepLabel | $($e.Name) | $status | $detail |"

            if ($e.Status -eq "failed" -and $e.Errors) {
                foreach ($err in $e.Errors | Select-Object -First 3) {
                    $cleanErr = ($err -replace '\|', '/' -replace '\r?\n', ' ').Trim()
                    if ($cleanErr.Length -gt 80) { $cleanErr = $cleanErr.Substring(0, 77) + "..." }
                    Add-Line "| | | | $cleanErr |"
                }
            }
        }
        Add-Line ""
    }

    # --- SUMMARY ---
    $allValidators = @($Entries | Where-Object { $_.Step -in 2, 3, 4 })
    $totalValidators = $allValidators.Count
    $totalPassed  = @($allValidators | Where-Object { $_.Status -eq "passed" }).Count
    $totalFailed  = @($allValidators | Where-Object { $_.Status -eq "failed" }).Count
    $totalSkipped = @($allValidators | Where-Object { $_.Status -eq "skipped" }).Count

    Add-Line "## Summary"
    Add-Line ""
    Add-Line "Total: $totalValidators validators | $totalPassed passed | $totalFailed failed | $totalSkipped skipped"
    Add-Line ""
    if ($Success) {
        Add-Line "**BUILD SUCCESSFUL**"
    }
    else {
        Add-Line "**BUILD FAILED**"
    }
    Add-Line ""

    # --- Write report to stdout ---
    Write-Host "[REPORT_START]"
    foreach ($l in $lines) { Write-Host $l }
    Write-Host "[REPORT_END]"
}

Write-BuildReport -Meta $reportMeta -Entries $reportEntries -Success $overallSuccess

if ($overallSuccess) {
    exit 0
}
else {
    exit 1
}
