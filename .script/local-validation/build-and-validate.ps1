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

.PARAMETER ContentRoot
    Repository checkout containing the selected Solutions/ content. Defaults to the
    toolkit checkout that contains this script. Cross-checkout validation requires
    -SkipPackaging; tooling and dependencies continue to load from this script's checkout.

.PARAMETER EvidenceDirectory
    Ignored evidence parent under .script/local-validation/Logs in the toolkit checkout.
    A unique run folder stores complete TypeScript JSON results and child output logs.

.PARAMETER PackageReportPath
    Exact V3.1 packaging report under the selected solution. When supplied, the runner
    requires validation-only mode and emits hash-bound evidence for that package.

.PARAMETER ArmValidationMethod
    arm-ttk (legacy default) runs ARM-TTK. lab-deployment replaces only ARM-TTK
    with pending external approved deployment validation; its report is not acceptance.

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

    [string]$ContentRoot,

    [string]$EvidenceDirectory,

    [ValidateSet("none", "patch", "minor", "major")]
    [string]$VersionBump = "patch",

    [switch]$SkipValidation,

    [switch]$SkipPackaging,

    [string]$ValidationSkip = "kql,detection-schema,non-ascii,arm-ttk",

    [string]$ReleaseNotes = "",

    [string]$PackageReportPath,

    [ValidateSet("arm-ttk", "lab-deployment")]
    [string]$ArmValidationMethod = "arm-ttk"
)

# =============================================================================
# SETUP
# =============================================================================

$ErrorActionPreference = "Stop"
if ($ArmValidationMethod -eq "lab-deployment") {
    if (-not $SkipPackaging -or $SkipValidation -or -not $PackageReportPath) {
        Write-Host "❌ lab-deployment requires -SkipPackaging, -PackageReportPath and all static validators." -ForegroundColor Red
        exit 2
    }
    $labAllowedSkips = @("kql", "detection-schema", "non-ascii", "arm-ttk")
    if (@($ValidationSkip -split ',' | Where-Object { $_ -and $_ -notin $labAllowedSkips }).Count -gt 0) {
        Write-Host "❌ lab-deployment cannot skip other static validators." -ForegroundColor Red
        exit 2
    }
    # These checks run natively below; only ARM-TTK is replaced by the lab route.
    $ValidationSkip = "kql,detection-schema,non-ascii,arm-ttk"
}

# The toolkit root is anchored to this script, never to the caller's current directory.
$toolkitRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../.."))
$toolkitRoot = $toolkitRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
. (Join-Path $PSScriptRoot "validation-binding.ps1")
$pathComparison = if ($IsWindows) { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }
$ContentRoot = if ($ContentRoot) { [System.IO.Path]::GetFullPath($ContentRoot) } else { $toolkitRoot }
$ContentRoot = $ContentRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
$rootsAreSame = [string]::Equals($toolkitRoot, $ContentRoot, $pathComparison)

if (-not (Test-Path $toolkitRoot -PathType Container) -or
    -not (Test-Path (Join-Path $toolkitRoot ".script/local-validation/validate.ts") -PathType Leaf)) {
    Write-Host "❌ Toolkit root is invalid: '$toolkitRoot'." -ForegroundColor Red
    exit 2
}
if (-not (Test-Path $ContentRoot -PathType Container) -or
    -not (Test-Path (Join-Path $ContentRoot "Solutions") -PathType Container) -or
    ((Get-Item $ContentRoot).Attributes -band [System.IO.FileAttributes]::ReparsePoint) -or
    ((Get-Item (Join-Path $ContentRoot "Solutions")).Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
    Write-Host "❌ Content root must be an existing repository checkout containing Solutions/: '$ContentRoot'." -ForegroundColor Red
    exit 2
}
$contentGitRoot = & git -C $ContentRoot rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0 -or
    -not [string]::Equals(
        [System.IO.Path]::GetFullPath("$contentGitRoot").TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar),
        $ContentRoot,
        $pathComparison)) {
    Write-Host "❌ Content root must be the canonical Git worktree root: '$ContentRoot'." -ForegroundColor Red
    exit 2
}
if (-not $rootsAreSame -and -not $SkipPackaging) {
    Write-Host "❌ Cross-checkout validation is validation-only; pass -SkipPackaging to avoid modifying content or package artifacts." -ForegroundColor Red
    exit 2
}

# Resolve solution name (supports partial/fuzzy matching)
$solutionsDir = Join-Path $ContentRoot "Solutions"
$solutionsRoot = [System.IO.Path]::GetFullPath($solutionsDir).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
if ([System.IO.Path]::IsPathRooted($SolutionName) -or $SolutionName.Contains('/') -or $SolutionName.Contains('\') -or $SolutionName -in @('.', '..')) {
    Write-Host "❌ Solution must be a folder name directly under Solutions/: '$SolutionName'" -ForegroundColor Red
    exit 2
}
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

$solutionPath = [System.IO.Path]::GetFullPath($solutionPath)
$solutionsPrefix = $solutionsRoot + [System.IO.Path]::DirectorySeparatorChar
if (-not $solutionPath.StartsWith($solutionsPrefix, $pathComparison) -or
    -not [string]::Equals([System.IO.Path]::GetDirectoryName($solutionPath), $solutionsRoot, $pathComparison) -or
    -not (Test-Path $solutionPath -PathType Container) -or
    ((Get-Item $solutionPath).Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
    Write-Host "❌ Invalid solution folder: '$solutionPath'. Expected an existing folder directly under '$solutionsRoot'." -ForegroundColor Red
    exit 2
}

if ($PackageReportPath) {
    if (-not $SkipPackaging -or $SkipValidation) {
        Write-Host "❌ -PackageReportPath requires validation-only mode: pass -SkipPackaging and do not pass -SkipValidation." -ForegroundColor Red
        exit 2
    }
    try {
        $null = Get-ValidationV31PackageEvidence `
            -SolutionPath $solutionPath `
            -PackageReportPath $PackageReportPath
        $PackageReportPath = Resolve-ValidationEvidencePath `
            -Root $solutionPath `
            -Reference $PackageReportPath
    }
    catch {
        Write-Host "❌ V3.1 package evidence is invalid: $($_.Exception.Message)" -ForegroundColor Red
        exit 2
    }
}

$dataPath = Join-Path $solutionPath "Data"
if (-not (Test-Path $dataPath)) {
    Write-Host "❌ Data folder not found: $dataPath" -ForegroundColor Red
    exit 2
}

if (-not $EvidenceDirectory) {
    $EvidenceDirectory = Join-Path $toolkitRoot ".script/local-validation/Logs"
}
$evidenceCandidate = if ([System.IO.Path]::IsPathRooted($EvidenceDirectory)) {
    $EvidenceDirectory
} else {
    Join-Path $toolkitRoot $EvidenceDirectory
}
$evidenceParent = [System.IO.Path]::GetFullPath($evidenceCandidate)
$evidenceRoot = [System.IO.Path]::GetFullPath((Join-Path $toolkitRoot ".script/local-validation/Logs"))
$evidencePrefix = $evidenceRoot + [System.IO.Path]::DirectorySeparatorChar
if (-not $evidenceParent.StartsWith($evidencePrefix, $pathComparison) -and
    -not [string]::Equals($evidenceParent, $evidenceRoot, $pathComparison)) {
    Write-Host "❌ EvidenceDirectory must be inside '$evidenceRoot'." -ForegroundColor Red
    exit 2
}
$evidenceCursor = $toolkitRoot
foreach ($component in ([System.IO.Path]::GetRelativePath($toolkitRoot, $evidenceParent) -split '[\\/]')) {
    if (-not $component -or $component -eq '.') { continue }
    $evidenceCursor = Join-Path $evidenceCursor $component
    if (Test-Path $evidenceCursor) {
        $evidenceItem = Get-Item -Force $evidenceCursor
        if (($evidenceItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -or
            -not $evidenceItem.PSIsContainer) {
            Write-Host "❌ EvidenceDirectory cannot traverse a link or file: '$evidenceCursor'." -ForegroundColor Red
            exit 2
        }
    }
}
$evidenceRelative = [System.IO.Path]::GetRelativePath($toolkitRoot, $evidenceParent).Replace('\', '/')
$null = & git -C $toolkitRoot check-ignore --no-index --quiet -- ($evidenceRelative.TrimEnd('/') + '/') 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ EvidenceDirectory is not ignored by the toolkit checkout: '$evidenceRelative'." -ForegroundColor Red
    exit 2
}
$runStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
$evidenceRunPath = Join-Path $evidenceParent $runStamp
if (Test-Path $evidenceRunPath) {
    Write-Host "❌ Evidence run directory already exists: '$evidenceRunPath'." -ForegroundColor Red
    exit 2
}
$null = New-Item -ItemType Directory -Path $evidenceParent -Force
$null = New-Item -ItemType Directory -Path $evidenceRunPath -Force:$false

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Microsoft Sentinel Solution Builder                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Solution:     $SolutionName" -ForegroundColor White
Write-Host "  Toolkit Root: $toolkitRoot" -ForegroundColor White
Write-Host "  Content Root: $ContentRoot" -ForegroundColor White
Write-Host "  Version Bump: $VersionBump" -ForegroundColor White
Write-Host "  Evidence:     $evidenceRunPath" -ForegroundColor White
Write-Host "  Packaging:    $(if ($SkipPackaging) { '⏭ Skipped' } else { '✅ Enabled' })" -ForegroundColor White
Write-Host "  Validation:   $(if ($SkipValidation) { '⏭ Skipped' } else { '✅ Enabled' })" -ForegroundColor White
Write-Host "  Release Notes:$(if ($ReleaseNotes) { " ✅ Provided" } else { ' ⚠️  Not provided' })" -ForegroundColor White
Write-Host ""

$overallSuccess = $true

# Report tracking
$reportEntries = [System.Collections.ArrayList]::new()
$saveProcessOutput = {
    param([string]$Name, [object[]]$Output)
    $outputPath = Join-Path $evidenceRunPath $Name
    [System.IO.File]::WriteAllLines(
        $outputPath,
        @($Output | ForEach-Object { "$_" }),
        [System.Text.UTF8Encoding]::new($false)
    )
    return $outputPath
}
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
    EvidenceRunPath     = $evidenceRunPath
    ValidationBindingPath = $null
    ValidationBindingSha256 = $null
    ValidationBindingResult = $null
}

# =============================================================================
# STEP 1: PACKAGE THE SOLUTION
# =============================================================================

if (-not $SkipPackaging) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  STEP 1: Packaging Solution (V3)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""

    $v3ScriptPath = Join-Path $toolkitRoot "Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1"

    if (-not (Test-Path $v3ScriptPath)) {
        Write-Host "❌ V3 packaging script not found: $v3ScriptPath" -ForegroundColor Red
        exit 2
    }

    try {
        # Run packaging from repo root so relative paths work
        Push-Location $toolkitRoot

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

$validationEvidenceBefore = $null
$validationEvidenceCaptureError = $null
if ($PackageReportPath) {
    try {
        $validationEvidenceBefore = Get-ValidationEvidenceSnapshot `
            -ToolkitRoot $toolkitRoot `
            -ContentRoot $ContentRoot `
            -SolutionPath $solutionPath `
            -PackageReportPath $PackageReportPath
    }
    catch {
        $validationEvidenceCaptureError = $_.Exception.Message
        $overallSuccess = $false
        $null = $reportEntries.Add(@{
            Step = 4; Name = "Validation Evidence Integrity"; Status = "failed"
            Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
            Errors = @("Could not capture V3.1 validation evidence before validation: $validationEvidenceCaptureError")
        })
    }
}

if (-not $SkipValidation) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  STEP 2: Running Local Validations" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""

    $validateScript = Join-Path $toolkitRoot ".script/local-validation/validate.js"

    $validateSource = Join-Path $toolkitRoot ".script/local-validation/validate.ts"
    if (-not (Test-Path $validateSource)) {
        Write-Host "❌ TypeScript validation source not found: $validateSource" -ForegroundColor Red
        $overallSuccess = $false
        $null = $reportEntries.Add(@{
            Step = 2; Name = "TypeScript Compilation"; Status = "failed"
            Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
            Errors = @("TypeScript validation source not found: $validateSource")
        })
    }
    else {
        # validate.js and its imported checker modules are generated from TypeScript and
        # ignored by git. Compile them here so this wrapper cannot execute stale output.
        $typescriptCompileSucceeded = $false
        $tscSw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            Push-Location $toolkitRoot
            $tscOutput = & npm run tsc 2>&1
            $tscExitCode = $LASTEXITCODE
            Pop-Location
            $tscSw.Stop()
            [System.IO.File]::WriteAllLines(
                (Join-Path $evidenceRunPath "typescript-compile.log"),
                @($tscOutput | ForEach-Object { "$_" }),
                [System.Text.UTF8Encoding]::new($false)
            )

            $tscOutput | ForEach-Object {
                $line = "$_"
                if ($line.Trim()) { Write-Host "     $line" -ForegroundColor Gray }
            }

            if ($tscExitCode -eq 0) {
                $typescriptCompileSucceeded = $true
                $null = $reportEntries.Add(@{
                    Step = 2; Name = "TypeScript Compilation"; Status = "passed"
                    Passed = 1; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = $tscSw.Elapsed
                })
            }
            else {
                Write-Host "❌ TypeScript compilation failed — local validation will not run stale JavaScript output." -ForegroundColor Red
                $overallSuccess = $false
                $tscErrors = @($tscOutput | ForEach-Object { "$_".Trim() } | Where-Object { $_ })
                $null = $reportEntries.Add(@{
                    Step = 2; Name = "TypeScript Compilation"; Status = "failed"
                    Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                    Duration = $tscSw.Elapsed; Errors = $tscErrors
                })
            }
        }
        catch {
            $tscSw.Stop()
            Pop-Location -ErrorAction SilentlyContinue
            Write-Host "❌ TypeScript compilation error: $($_.Exception.Message)" -ForegroundColor Red
            $overallSuccess = $false
            $null = $reportEntries.Add(@{
                Step = 2; Name = "TypeScript Compilation"; Status = "failed"
                Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                Duration = $tscSw.Elapsed; Errors = @($_.Exception.Message)
            })
        }

        if (-not $typescriptCompileSucceeded) {
            Write-Host "⏭  Local TypeScript validators skipped because compilation failed." -ForegroundColor Yellow
        }
        elseif (-not (Test-Path $validateScript)) {
            Write-Host "❌ Validation script not found after TypeScript compilation: $validateScript" -ForegroundColor Red
            $overallSuccess = $false
            $null = $reportEntries.Add(@{
                Step = 2; Name = "TypeScript Runner"; Status = "failed"
                Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                Errors = @("Validation script not found after successful compilation: $validateScript")
            })
        }
        else {
        # Build the validation command — use --json for structured output
        $solutionRelativePath = "Solutions/$SolutionName"
        $typescriptJsonPath = Join-Path $evidenceRunPath "typescript-results.json"
        $typescriptStdoutPath = Join-Path $evidenceRunPath "typescript.stdout.log"
        $typescriptStderrPath = Join-Path $evidenceRunPath "typescript.stderr.log"
        $validateArgs = @(
            $validateScript,
            "--path", $solutionRelativePath,
            "--repository-root", $ContentRoot,
            "--json-file", $typescriptJsonPath
        )

        if ($ValidationSkip) {
            $validateArgs += @("--skip", $ValidationSkip)
        }

        try {
            $nodeProcess = [System.Diagnostics.Process]::new()
            $nodeProcess.StartInfo = [System.Diagnostics.ProcessStartInfo]::new()
            $nodeProcess.StartInfo.FileName = "node"
            $nodeProcess.StartInfo.WorkingDirectory = $toolkitRoot
            $nodeProcess.StartInfo.UseShellExecute = $false
            $nodeProcess.StartInfo.RedirectStandardOutput = $true
            $nodeProcess.StartInfo.RedirectStandardError = $true
            foreach ($argument in $validateArgs) {
                $null = $nodeProcess.StartInfo.ArgumentList.Add($argument)
            }
            if (-not $nodeProcess.Start()) {
                throw "Could not start Node.js local validation process."
            }
            $stdoutTask = $nodeProcess.StandardOutput.ReadToEndAsync()
            $stderrTask = $nodeProcess.StandardError.ReadToEndAsync()
            $nodeProcess.WaitForExit()
            $validationExitCode = $nodeProcess.ExitCode
            $nodeStdout = $stdoutTask.GetAwaiter().GetResult()
            $nodeStderr = $stderrTask.GetAwaiter().GetResult()
            [System.IO.File]::WriteAllText($typescriptStdoutPath, $nodeStdout, [System.Text.UTF8Encoding]::new($false))
            [System.IO.File]::WriteAllText($typescriptStderrPath, $nodeStderr, [System.Text.UTF8Encoding]::new($false))
            if ($nodeStdout.Trim()) { Write-Host "     $($nodeStdout.Trim())" -ForegroundColor Gray }
            if ($nodeStderr.Trim()) { Write-Host $nodeStderr.Trim() -ForegroundColor Yellow }

            if (-not (Test-Path $typescriptJsonPath -PathType Leaf)) {
                throw "TypeScript validator exited $validationExitCode without writing its structured report. See $typescriptStdoutPath and $typescriptStderrPath."
            }
            $jsonParsed = Get-Content $typescriptJsonPath -Raw | ConvertFrom-Json
            if ($null -eq $jsonParsed.results) {
                throw "TypeScript validator report has no results array. See $typescriptJsonPath."
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
                    $vFailed = @($vResults | Where-Object { -not $_.passed -and -not $_.skipped })
                    $vSkipped = @($vResults | Where-Object { $_.skipped })
                    $skipReasonText = ($vSkipped | Where-Object { $_.skipReason } | Select-Object -ExpandProperty skipReason -Unique) -join "; "

                    if ($vFailed.Count -gt 0) {
                        Write-Host "  ❌ $vName  ($($vFailed.Count) failed, $($vPassed.Count) passed, $($vSkipped.Count) skipped)" -ForegroundColor Red
                        foreach ($f in $vFailed) {
                            Write-Host "     FAIL  $($f.filePath)" -ForegroundColor Red
                            if ($f.error) { Write-Host "           $($f.error)" -ForegroundColor Red }
                        }
                    }
                    elseif ($vPassed.Count -eq 0 -and $vSkipped.Count -gt 0) {
                        Write-Host "  ⏭  $vName  ($($vSkipped.Count) skipped$(if ($skipReasonText) { " — $skipReasonText" }))" -ForegroundColor Yellow
                    }
                    else {
                        Write-Host "  ✅ $vName  ($($vPassed.Count) passed, $($vSkipped.Count) skipped)" -ForegroundColor Green
                    }

                    # Add report entry per validator
                    $status = if ($vFailed.Count -gt 0) { "failed" } elseif ($vPassed.Count -eq 0 -and $vSkipped.Count -gt 0) { "skipped" } else { "passed" }
                    $errors = @($vFailed | ForEach-Object { "$($_.filePath): $($_.error)" })
                    $null = $reportEntries.Add(@{
                        Step        = 2
                        Name        = $vName
                        Status      = $status
                        Passed      = $vPassed.Count
                        Failed      = $vFailed.Count
                        Skipped     = $vSkipped.Count
                        Errors      = $errors
                        SkipReason  = if ($skipReasonText) { $skipReasonText } else { $null }
                    })
                }

                $totalPassed = @($jsonParsed.results | Where-Object { $_.passed -and -not $_.skipped }).Count
                $totalFailed = @($jsonParsed.results | Where-Object { -not $_.passed -and -not $_.skipped }).Count
                $totalSkipped = @($jsonParsed.results | Where-Object { $_.skipped }).Count
                Write-Host ""
                Write-Host "  TOTAL: $($jsonParsed.results.Count) checks  |  ✅ $totalPassed passed  |  ❌ $totalFailed failed  |  ⏭ $totalSkipped skipped" -ForegroundColor Gray
            }

            if ($validationExitCode -ne 0 -or $totalFailed -gt 0) {
                Write-Host ""
                Write-Host "❌ Validation found errors (exit code $validationExitCode)" -ForegroundColor Red
                $overallSuccess = $false
                if ($validationExitCode -ne 0 -and $totalFailed -eq 0) {
                    $null = $reportEntries.Add(@{
                        Step = 2; Name = "TypeScript Runner"; Status = "failed"
                        Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                        Errors = @("Node.js validation process exited with code $validationExitCode despite reporting no failed check. Full JSON and process output: $evidenceRunPath")
                    })
                }
            }
            else {
                Write-Host ""
                Write-Host "✅ All validations passed" -ForegroundColor Green
            }
        }
        catch {
            Write-Host ""
            Write-Host "❌ Validation failed: $($_.Exception.Message)" -ForegroundColor Red
            $overallSuccess = $false
            $null = $reportEntries.Add(@{
                Step = 2; Name = "TypeScript Runner"; Status = "failed"
                Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                Errors = @($_.Exception.Message)
            })
        }
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
        # Detection Schema exposes only the basename in its display name, so duplicate or
        # filter-sensitive names are skipped. KQL and Non-ASCII expose the full path and are
        # filtered by its encoded value to avoid matching same-named files elsewhere.

        function Build-DotnetTestFilter {
            param([System.IO.FileInfo[]]$Files, [switch]$UseEncodedPath)
            $parts = @()
            foreach ($f in $Files) {
                if ($UseEncodedPath) {
                    # KQL and Non-ASCII test cases include the full path as an argument.
                    $name = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($f.FullName))
                }
                else {
                    $name = $f.Name
                    if ($name.IndexOfAny([char[]]@('(', ')', '|', '&', '!')) -ge 0) {
                        throw "Cannot safely construct a dotnet test filter for filename '$name'."
                    }
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

        function Get-DotnetTestSkipReason {
            param(
                [int]$ExitCode,
                [hashtable]$Summary,
                [string[]]$OutputLines
            )
            if ($ExitCode -ne 0 -or $Summary.Total -gt 0) { return $null }
            $diagnostics = @($OutputLines | Where-Object {
                "$_" -match "No test is available|could not find dependent assembly|No tests were found"
            } | ForEach-Object { "$_".Trim() } | Select-Object -First 3)
            if ($diagnostics.Count -gt 0) {
                return "No tests executed: $($diagnostics -join ' | ')"
            }
            return "No tests executed: dotnet test did not report any test results"
        }

        # --- Detection Schema Validator ---
        $detectionProject = Join-Path $toolkitRoot ".script/tests/detectionTemplateSchemaValidation/DetectionTemplateSchemaValidation.Tests.csproj"
        if ($has31 -and (Test-Path $detectionProject)) {
            # Scope to solution's Analytic Rules only
            $detFiles = Get-SolutionContentFiles -SolPath $solutionPath -SubDirs @("Analytic Rules") -Extensions @("*.yaml")

            if ($detFiles.Count -gt 0) {
                # These tests expose only the basename as their filterable argument. If another
                # solution has a same-named rule, filtering by that name would execute it too.
                $allDetectionFiles = @(
                    Get-ChildItem (Join-Path $ContentRoot "Detections"), $solutionsDir -Recurse -Filter "*.yaml" -File |
                        Where-Object { $_.FullName -match '[\\/]Detections[\\/]' -or $_.FullName -match '[\\/]Solutions[\\/].*[\\/]Analytic Rules[\\/]' }
                )
                $collidingNames = @($detFiles | Where-Object {
                    $targetName = $_.Name
                    @($allDetectionFiles | Where-Object { $_.Name -eq $targetName }).Count -gt 1
                } | Select-Object -ExpandProperty Name -Unique)
                $filterUnsafeNames = @($detFiles | Where-Object {
                    $_.Name.IndexOfAny([char[]]@('(', ')', '|', '&', '!')) -ge 0
                } | Select-Object -ExpandProperty Name -Unique)
                if ($collidingNames.Count -gt 0 -or $filterUnsafeNames.Count -gt 0) {
                    $collisionDetail = "Cannot safely scope Detection Schema by basename; duplicate file name(s): $($collidingNames -join ', '); filter-sensitive file name(s): $($filterUnsafeNames -join ', ')"
                    Write-Host "  ⏭  Detection Schema validation skipped — $collisionDetail." -ForegroundColor Yellow
                    $null = $reportEntries.Add(@{
                        Step = 3; Name = "Detection Schema"; Status = "skipped"
                        Passed = 0; Failed = 0; Skipped = $detFiles.Count; FileCount = $detFiles.Count
                        Duration = [TimeSpan]::Zero; SkipReason = $collisionDetail
                    })
                }
                else {
                $detFilter = Build-DotnetTestFilter -Files $detFiles
                Write-Host "  🔍 Detection Schema Validation (scoped to $SolutionName — $($detFiles.Count) files)..." -ForegroundColor White
                $detSw = [System.Diagnostics.Stopwatch]::StartNew()
                try {
                    Push-Location $toolkitRoot
                    $previousContentRoot = $env:SENTINEL_VALIDATION_CONTENT_ROOT
                    $env:SENTINEL_VALIDATION_CONTENT_ROOT = $ContentRoot
                    $detOutput = & dotnet test $detectionProject --filter "$detFilter" -v q --nologo 2>&1
                    $detExitCode = $LASTEXITCODE
                    Pop-Location
                    if ($previousContentRoot) { $env:SENTINEL_VALIDATION_CONTENT_ROOT = $previousContentRoot }
                    else { Remove-Item Env:SENTINEL_VALIDATION_CONTENT_ROOT -ErrorAction SilentlyContinue }
                    $detSw.Stop()
                    $detLogPath = & $saveProcessOutput "detection-schema.dotnet.log" $detOutput

                    $detSummary = Parse-DotnetTestSummary -OutputLines ($detOutput | ForEach-Object { "$_" })
                    $detSkipReason = Get-DotnetTestSkipReason -ExitCode $detExitCode -Summary $detSummary -OutputLines ($detOutput | ForEach-Object { "$_" })

                    if ($detExitCode -ne 0) {
                        $failLines = $detOutput | Where-Object { $_ -match "Failed|Error|FAIL" }
                        $failLines | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
                        $summaryLine = $detOutput | Where-Object { $_ -match "^(Failed|Passed)!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Red }
                        Write-Host "  ❌ Detection Schema validation failed" -ForegroundColor Red
                        $overallSuccess = $false
                    }
                    elseif ($detSkipReason) {
                        Write-Host "  ⏭  Detection Schema validation skipped — $detSkipReason" -ForegroundColor Yellow
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
                        Status    = if ($detExitCode -ne 0) { "failed" } elseif ($detSkipReason) { "skipped" } else { "passed" }
                        Passed    = $detSummary.Passed
                        Failed    = $detSummary.Failed
                        Skipped   = $detSummary.Skipped
                        FileCount = $detFiles.Count
                        Duration  = $detSw.Elapsed
                        Errors    = $detErrors
                        OutputLog = $detLogPath
                        SkipReason = $detSkipReason
                    })
                }
                catch {
                    $detSw.Stop()
                    if ($null -ne $previousContentRoot -and $previousContentRoot) { $env:SENTINEL_VALIDATION_CONTENT_ROOT = $previousContentRoot }
                    else { Remove-Item Env:SENTINEL_VALIDATION_CONTENT_ROOT -ErrorAction SilentlyContinue }
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
            }
            else {
                $xdrDetCheckFiles = Get-SolutionContentFiles -SolPath $solutionPath -SubDirs @("XDR Detections") -Extensions @("*.yaml", "*.yml")
                $noArReason = if ($xdrDetCheckFiles.Count -gt 0) {
                    "No legacy Sentinel Analytic Rules found (.NET Detection Schema only supports Sentinel Analytic Rules; XDR Detections are validated by XDR Detection validator)"
                }
                else {
                    "No Analytic Rules found"
                }
                Write-Host "  ⏭  Detection Schema validation skipped — $noArReason." -ForegroundColor Yellow
                $null = $reportEntries.Add(@{
                    Step = 3; Name = "Detection Schema"; Status = "skipped"
                    Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = [TimeSpan]::Zero; SkipReason = $noArReason
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
        elseif (-not (Test-Path $detectionProject)) {
            Write-Host "  ⏭  Detection Schema validation skipped — toolkit test project not found: $detectionProject" -ForegroundColor Yellow
            $null = $reportEntries.Add(@{
                Step = 3; Name = "Detection Schema"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                Duration = [TimeSpan]::Zero; SkipReason = "Toolkit test project not found"
            })
        }

        Write-Host ""

        # --- Non-ASCII Validator (scoped to solution's YAML/JSON files) ---
        $nonAsciiProject = Join-Path $toolkitRoot ".script/tests/NonAsciiValidationsTests/NonAsciiValidations.Tests.csproj"
        if ($has31 -and (Test-Path $nonAsciiProject)) {
            # Scope to solution content files (same approach as Detection Schema)
            $naFiles = Get-SolutionContentFiles -SolPath $solutionPath `
                -SubDirs @("Analytic Rules", "Hunting Queries", "Parsers", "Data Connectors", "Playbooks", "Workbooks") `
                -Extensions @("*.yaml", "*.json")

            if ($naFiles.Count -gt 0) {
                $naFilter = Build-DotnetTestFilter -Files $naFiles -UseEncodedPath
                Write-Host "  🔍 Non-ASCII Validation (scoped to $SolutionName — $($naFiles.Count) files)..." -ForegroundColor White
                $naSw = [System.Diagnostics.Stopwatch]::StartNew()
                try {
                    Push-Location $toolkitRoot
                    $previousContentRoot = $env:SENTINEL_VALIDATION_CONTENT_ROOT
                    $env:SENTINEL_VALIDATION_CONTENT_ROOT = $ContentRoot
                    $naOutput = & dotnet test $nonAsciiProject --filter "$naFilter" -v q --nologo 2>&1
                    $naExitCode = $LASTEXITCODE
                    Pop-Location
                    if ($previousContentRoot) { $env:SENTINEL_VALIDATION_CONTENT_ROOT = $previousContentRoot }
                    else { Remove-Item Env:SENTINEL_VALIDATION_CONTENT_ROOT -ErrorAction SilentlyContinue }
                    $naSw.Stop()
                    $naLogPath = & $saveProcessOutput "non-ascii.dotnet.log" $naOutput

                    $naSummary = Parse-DotnetTestSummary -OutputLines ($naOutput | ForEach-Object { "$_" })
                    $naSkipReason = Get-DotnetTestSkipReason -ExitCode $naExitCode -Summary $naSummary -OutputLines ($naOutput | ForEach-Object { "$_" })

                    if ($naExitCode -ne 0) {
                        $failLines = $naOutput | Where-Object { $_ -match "Failed|Error|FAIL" }
                        $failLines | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
                        $summaryLine = $naOutput | Where-Object { $_ -match "^(Failed|Passed)!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Red }
                        Write-Host "  ❌ Non-ASCII validation failed" -ForegroundColor Red
                        $overallSuccess = $false
                    }
                    elseif ($naSkipReason) {
                        Write-Host "  ⏭  Non-ASCII validation skipped — $naSkipReason" -ForegroundColor Yellow
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
                        Status    = if ($naExitCode -ne 0) { "failed" } elseif ($naSkipReason) { "skipped" } else { "passed" }
                        Passed    = $naSummary.Passed
                        Failed    = $naSummary.Failed
                        Skipped   = $naSummary.Skipped
                        FileCount = $naFiles.Count
                        Duration  = $naSw.Elapsed
                        Errors    = $naErrors
                        OutputLog = $naLogPath
                        SkipReason = $naSkipReason
                    })
                }
                catch {
                    $naSw.Stop()
                    if ($null -ne $previousContentRoot -and $previousContentRoot) { $env:SENTINEL_VALIDATION_CONTENT_ROOT = $previousContentRoot }
                    else { Remove-Item Env:SENTINEL_VALIDATION_CONTENT_ROOT -ErrorAction SilentlyContinue }
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
        elseif (-not (Test-Path $nonAsciiProject)) {
            Write-Host "  ⏭  Non-ASCII validation skipped — toolkit test project not found: $nonAsciiProject" -ForegroundColor Yellow
            $null = $reportEntries.Add(@{
                Step = 3; Name = "Non-ASCII"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                Duration = [TimeSpan]::Zero; SkipReason = "Toolkit test project not found"
            })
        }

        Write-Host ""

        # --- KQL Validator (scoped to solution) ---
        $kqlProject = Join-Path $toolkitRoot ".script/tests/KqlvalidationsTests/Kqlvalidations.Tests.csproj"
        if ($has80 -and (Test-Path $kqlProject)) {
            # Collect all YAML/JSON content files from the solution for scoping
            $kqlFiles = Get-SolutionContentFiles -SolPath $solutionPath `
                -SubDirs @("Analytic Rules", "XDR Detections", "Hunting Queries", "Parsers", "Data Connectors") `
                -Extensions @("*.yaml", "*.yml", "*.json")

            if ($kqlFiles.Count -gt 0) {
                $kqlFilter = Build-DotnetTestFilter -Files $kqlFiles -UseEncodedPath
                Write-Host "  🔍 KQL Validation (scoped to $SolutionName — $($kqlFiles.Count) files)..." -ForegroundColor White

                # KQL's GitHubApiClient.Create() throws without GitHub App credentials.
                # Setting SYSTEM_PULLREQUEST_ISFORK=true bypasses credential checks and creates
                # an unauthenticated client. With no PRNUM set, it loads all files for discovery
                # but --filter ensures only the solution's tests execute.
                $previousForkFlag = $env:SYSTEM_PULLREQUEST_ISFORK
                $env:SYSTEM_PULLREQUEST_ISFORK = "true"

                $kqlSw = [System.Diagnostics.Stopwatch]::StartNew()
                try {
                    Push-Location $toolkitRoot
                    $previousContentRoot = $env:SENTINEL_VALIDATION_CONTENT_ROOT
                    $env:SENTINEL_VALIDATION_CONTENT_ROOT = $ContentRoot
                    $kqlOutput = & dotnet test $kqlProject --filter "$kqlFilter" -v q --nologo 2>&1
                    $kqlExitCode = $LASTEXITCODE
                    Pop-Location
                    if ($previousContentRoot) { $env:SENTINEL_VALIDATION_CONTENT_ROOT = $previousContentRoot }
                    else { Remove-Item Env:SENTINEL_VALIDATION_CONTENT_ROOT -ErrorAction SilentlyContinue }
                    $kqlSw.Stop()
                    $kqlLogPath = & $saveProcessOutput "kql.dotnet.log" $kqlOutput

                    $kqlSummary = Parse-DotnetTestSummary -OutputLines ($kqlOutput | ForEach-Object { "$_" })
                    $kqlSkipReason = Get-DotnetTestSkipReason -ExitCode $kqlExitCode -Summary $kqlSummary -OutputLines ($kqlOutput | ForEach-Object { "$_" })

                    if ($kqlExitCode -ne 0) {
                        $failLines = $kqlOutput | Where-Object { $_ -match "Failed|Error|FAIL" }
                        $failLines | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
                        $summaryLine = $kqlOutput | Where-Object { $_ -match "^(Failed|Passed)!" } | Select-Object -Last 1
                        if ($summaryLine) { Write-Host "     $summaryLine" -ForegroundColor Red }
                        Write-Host "  ❌ KQL validation failed" -ForegroundColor Red
                        $overallSuccess = $false
                    }
                    elseif ($kqlSkipReason) {
                        Write-Host "  ⏭  KQL validation skipped — $kqlSkipReason" -ForegroundColor Yellow
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
                        Status    = if ($kqlExitCode -ne 0) { "failed" } elseif ($kqlSkipReason) { "skipped" } else { "passed" }
                        Passed    = $kqlSummary.Passed
                        Failed    = $kqlSummary.Failed
                        Skipped   = $kqlSummary.Skipped
                        FileCount = $kqlFiles.Count
                        Duration  = $kqlSw.Elapsed
                        Errors    = $kqlErrors
                        OutputLog = $kqlLogPath
                        SkipReason = $kqlSkipReason
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
                    if ($null -ne $previousContentRoot -and $previousContentRoot) {
                        $env:SENTINEL_VALIDATION_CONTENT_ROOT = $previousContentRoot
                    }
                    else {
                        Remove-Item Env:SENTINEL_VALIDATION_CONTENT_ROOT -ErrorAction SilentlyContinue
                    }
                }
            }
            else {
                $xdrKqlCheckFiles = Get-SolutionContentFiles -SolPath $solutionPath -SubDirs @("XDR Workbooks") -Extensions @("*.json")
                $noKqlReason = if ($xdrKqlCheckFiles.Count -gt 0) {
                    "No Sentinel or XDR Detection KQL files found (.NET KQL validator does not support XDR Workbooks; validated via static XDR KQL validator)"
                }
                else {
                    "No content files found"
                }
                Write-Host "  ⏭  KQL validation skipped — $noKqlReason in $SolutionName." -ForegroundColor Yellow
                $null = $reportEntries.Add(@{
                    Step = 3; Name = "KQL"; Status = "skipped"
                    Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = [TimeSpan]::Zero; SkipReason = $noKqlReason
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
        elseif (-not (Test-Path $kqlProject)) {
            Write-Host "  ⏭  KQL validation skipped — toolkit test project not found: $kqlProject" -ForegroundColor Yellow
            $null = $reportEntries.Add(@{
                Step = 3; Name = "KQL"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
                Duration = [TimeSpan]::Zero; SkipReason = "Toolkit test project not found"
            })
        }

        Write-Host ""
    }

    $xdrLiveKqlFiles = Get-SolutionContentFiles -SolPath $solutionPath -SubDirs @("XDR Detections", "XDR Workbooks") -Extensions @("*.yaml", "*.yml", "*.json")
    if ($xdrLiveKqlFiles.Count -gt 0) {
        $xdrLiveSkipReason = "Live Advanced Hunting / Defender Workbook KQL validation requires an approved live workspace/tenant and is skipped in offline local validation"
        Write-Host "  ⏭  XDR KQL (Live / Advanced Hunting) skipped — $xdrLiveSkipReason ($($xdrLiveKqlFiles.Count) XDR file(s))." -ForegroundColor Yellow
        $null = $reportEntries.Add(@{
            Step = 3; Name = "XDR KQL (Live / Advanced Hunting)"; Status = "skipped"
            Passed = 0; Failed = 0; Skipped = $xdrLiveKqlFiles.Count; FileCount = $xdrLiveKqlFiles.Count
            Duration = [TimeSpan]::Zero; SkipReason = $xdrLiveSkipReason
        })
        Write-Host ""
    }

    # -----------------------------------------------------------------
    # ARM-TTK Validator (local — calls run-arm-ttk.ps1, same checks as entrypoint.ps1)
    # -----------------------------------------------------------------
    $packageDir = Join-Path $solutionPath "Package"
    if ($ArmValidationMethod -eq "lab-deployment") {
        Write-Host "  ⏳ ARM deployment validation pending; candidate is NOT accepted." -ForegroundColor Yellow
        $null = $reportEntries.Add(@{
            Step = 3; Name = "ARM-TTK"; Status = "skipped"
            Passed = 0; Failed = 0; Skipped = 1; FileCount = 0
            Duration = [TimeSpan]::Zero
            SkipReason = "SKIP (lab-deployment selected as ARM validation route); replaced only by pending approved lab deployment validation; not acceptance"
        })
    }
    elseif (Test-Path $packageDir) {
        $armTtkScript = Join-Path $toolkitRoot ".script/local-validation/run-arm-ttk.ps1"
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
                $armOutput = & pwsh -NoProfile -File $armTtkScript -SolutionPath $solutionPath -ToolkitRoot $toolkitRoot 2>&1
                $armExitCode = $LASTEXITCODE
                $armSw.Stop()
                $armLogPath = & $saveProcessOutput "arm-ttk.log" $armOutput

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
                        Duration = $armSw.Elapsed; SkipReason = "No templates in Package/"; OutputLog = $armLogPath
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
                        OutputLog = $armLogPath
                    })
                }
                else {
                    Write-Host "  ✅ ARM-TTK validation passed ($armPass tests)" -ForegroundColor Green
                    $null = $reportEntries.Add(@{
                        Step = 3; Name = "ARM-TTK"; Status = "passed"
                        Passed = $armPass; Failed = 0; Skipped = 0; FileCount = 0
                        Duration = $armSw.Elapsed; OutputLog = $armLogPath
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
    Write-Host "  ℹ️  Solution-scoped validators inspect current files under $solutionPath." -ForegroundColor Gray
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
    $fieldTypesScript = Join-Path $toolkitRoot ".script/package-automation/validateFieldTypes.ps1"
    if (Test-Path $fieldTypesScript) {
        Write-Host "  🔍 Field Types Validation..." -ForegroundColor White
        $ftSw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            Push-Location $toolkitRoot
            $ftOutput = & pwsh -NoProfile -File $fieldTypesScript `
                -runId "local-validation" `
                -pullRequestNumber 0 `
                -instrumentationKey "" `
                -baseFolderPath $ContentRoot `
                -SolutionPath $solutionPath 2>&1
            $ftExitCode = $LASTEXITCODE
            Pop-Location
            $ftSw.Stop()
            $ftLogPath = & $saveProcessOutput "field-types.log" $ftOutput

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
                    OutputLog = $ftLogPath
                })
            }
            elseif (($ftOutput | ForEach-Object { "$_" }) -match "no current Package/mainTemplate\.json") {
                Write-Host "  ⏭  Field Types validation skipped — the selected solution has no current Package/mainTemplate.json." -ForegroundColor Yellow
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Field Types"; Status = "skipped"
                    Passed = 0; Failed = 0; Skipped = 1; FileCount = 0
                    Duration = $ftSw.Elapsed; SkipReason = "No current Package/mainTemplate.json in the selected solution"
                    OutputLog = $ftLogPath
                })
            }
            else {
                Write-Host "  ✅ Field Types validation passed" -ForegroundColor Green
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Field Types"; Status = "passed"
                    Passed = 1; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = $ftSw.Elapsed; OutputLog = $ftLogPath
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
    $classicAIScript = Join-Path $toolkitRoot ".script/package-automation/validateClassicAppInsights.ps1"
    if (Test-Path $classicAIScript) {
        Write-Host "  🔍 Classic App Insights Validation..." -ForegroundColor White
        $caiSw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            Push-Location $toolkitRoot
            $caiOutput = & pwsh -NoProfile -File $classicAIScript `
                -runId "local-validation" `
                -pullRequestNumber 0 `
                -instrumentationKey "" `
                -baseFolderPath $ContentRoot `
                -SolutionPath $solutionPath 2>&1
            $caiExitCode = $LASTEXITCODE
            Pop-Location
            $caiSw.Stop()
            $caiLogPath = & $saveProcessOutput "classic-app-insights.log" $caiOutput

            $caiOutput | ForEach-Object {
                $line = "$_"
                if ($line.Trim()) { Write-Host "     $line" -ForegroundColor Gray }
            }

            if ($caiExitCode -ne 0) {
                Write-Host "  ❌ Classic App Insights validation failed" -ForegroundColor Red
                $overallSuccess = $false
                $caiErrors = @($caiOutput | Where-Object { "$_" -match "Error|FAIL|failed|classic|deprecated" } | ForEach-Object { "$_".Trim() })
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Classic App Insights (Solution)"; Status = "failed"
                    Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                    Duration = $caiSw.Elapsed; Errors = $caiErrors
                    OutputLog = $caiLogPath
                })
            }
            elseif (($caiOutput | ForEach-Object { "$_" }) -match "no current azuredeploy files found in the selected folder") {
                Write-Host "  ⏭  Classic App Insights validation skipped — no current azuredeploy files in the selected solution." -ForegroundColor Yellow
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Classic App Insights (Solution)"; Status = "skipped"
                    Passed = 0; Failed = 0; Skipped = 1; FileCount = 0
                    Duration = $caiSw.Elapsed; SkipReason = "No current azuredeploy files in the selected solution"
                    OutputLog = $caiLogPath
                })
            }
            else {
                Write-Host "  ✅ Classic App Insights validation passed" -ForegroundColor Green
                $null = $reportEntries.Add(@{
                    Step = 4; Name = "Classic App Insights (Solution)"; Status = "passed"
                    Passed = 1; Failed = 0; Skipped = 0; FileCount = 0
                    Duration = $caiSw.Elapsed; OutputLog = $caiLogPath
                })
            }
            $null = $reportEntries.Add(@{
                Step = 4; Name = "Classic App Insights (Standalone DataConnectors)"; Status = "skipped"
                Passed = 0; Failed = 0; Skipped = 1; FileCount = 0
                Duration = [TimeSpan]::Zero
                SkipReason = "Standalone DataConnectors are outside the selected solution folder"
            })
        }
        catch {
            $caiSw.Stop()
            Pop-Location -ErrorAction SilentlyContinue
            Write-Host "  ❌ Classic App Insights validation error: $($_.Exception.Message)" -ForegroundColor Red
            $overallSuccess = $false
            $null = $reportEntries.Add(@{
                Step = 4; Name = "Classic App Insights (Solution)"; Status = "failed"
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
    $hyperlinkScript = Join-Path $toolkitRoot ".script/package-automation/hyperlink-validation.ps1"
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
                Push-Location $toolkitRoot
                $hlOutput = & pwsh -NoProfile -File $hyperlinkScript `
                    -runId "local-validation" `
                    -pullRequestNumber 0 `
                    -instrumentationKey "" `
                    -baseFolderPath $ContentRoot `
                    -SolutionPath $solutionPath 2>&1
                $hlExitCode = $LASTEXITCODE
                Pop-Location
                $hlSw.Stop()
                $hlLogPath = & $saveProcessOutput "hyperlink-validation.log" $hlOutput

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
                        OutputLog = $hlLogPath
                    })
                }
                else {
                    Write-Host "  ✅ Hyperlink validation passed" -ForegroundColor Green
                    $null = $reportEntries.Add(@{
                        Step = 4; Name = "Hyperlink Validation"; Status = "passed"
                        Passed = 1; Failed = 0; Skipped = 0; FileCount = 0
                        Duration = $hlSw.Elapsed; OutputLog = $hlLogPath
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
    if ($trufflehogCmd -and $solutionPath) {
        Write-Host "  ⏭  TruffleHog secret scanning skipped — it scans repository history and cannot be constrained to one solution folder." -ForegroundColor Yellow
        $null = $reportEntries.Add(@{
            Step = 4; Name = "TruffleHog (Secrets)"; Status = "skipped"
            Passed = 0; Failed = 0; Skipped = 0; FileCount = 0
            Duration = [TimeSpan]::Zero; SkipReason = "Repository-history scan cannot be scoped to a solution folder"
        })
    }
    elseif ($trufflehogCmd) {
        Write-Host "  🔍 TruffleHog Secret Scanning..." -ForegroundColor White
        $thSw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $excludePathsFile = Join-Path $toolkitRoot ".script/SecretScanning/Excludepathlist"
            $thArgs = @("git", "file://$toolkitRoot", "--only-verified", "--fail")
            if (Test-Path $excludePathsFile) {
                $thArgs += @("--exclude-paths=$excludePathsFile")
            }

            Push-Location $toolkitRoot
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

if ($PackageReportPath -and $null -ne $validationEvidenceBefore) {
    try {
        $validationEvidenceAfter = Get-ValidationEvidenceSnapshot `
            -ToolkitRoot $toolkitRoot `
            -ContentRoot $ContentRoot `
            -SolutionPath $solutionPath `
            -PackageReportPath $PackageReportPath
        $validationBinding = Complete-ValidationEvidenceBinding `
            -Before $validationEvidenceBefore `
            -After $validationEvidenceAfter `
            -ValidationEntries @($reportEntries) `
            -PackagingSkipped ([bool]$SkipPackaging) `
            -ValidationSkipped ([bool]$SkipValidation) `
            -EvidenceRunPath $evidenceRunPath
        $validationBinding.armValidationMethod = $ArmValidationMethod
        $validationBinding.armValidationStatus = if ($ArmValidationMethod -eq "lab-deployment") { "pending" } else {
            if (@($reportEntries | Where-Object { $_.Name -eq "ARM-TTK" -and $_.Status -eq "passed" }).Count -eq 1) { "passed" } else { "not-passed" }
        }
        $validationBinding.packageLifecycleStatus = if ($ArmValidationMethod -eq "lab-deployment") { "candidate-generated" } else { "validated" }
        $validationBinding.packageAccepted = $false
        if ($ArmValidationMethod -eq "lab-deployment") { $validationBinding.workbookCapabilityVersion = 1 }
        $bindingReceipt = Write-ValidationEvidenceBinding `
            -EvidenceRunPath $evidenceRunPath `
            -Binding $validationBinding
        $reportMeta.ValidationBindingPath = $bindingReceipt.path
        $reportMeta.ValidationBindingSha256 = $bindingReceipt.sha256
        $reportMeta.ValidationBindingResult = $validationBinding.validationResult
        if ($validationBinding.validationResult -ne "PASSED") {
            $overallSuccess = $false
            $null = $reportEntries.Add(@{
                Step = 4; Name = "Validation Evidence Integrity"; Status = "failed"
                Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
                Errors = @($validationBinding.issues)
            })
        }
    }
    catch {
        $overallSuccess = $false
        $null = $reportEntries.Add(@{
            Step = 4; Name = "Validation Evidence Integrity"; Status = "failed"
            Passed = 0; Failed = 1; Skipped = 0; FileCount = 0
            Errors = @("Could not complete V3.1 validation evidence: $($_.Exception.Message)")
        })
    }
}
elseif ($PackageReportPath -and $validationEvidenceCaptureError) {
    $reportMeta.ValidationBindingResult = "FAILED"
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
    Add-Line "Toolkit root: $toolkitRoot"
    Add-Line "Content root: $ContentRoot"
    Add-Line "Evidence: $($Meta.EvidenceRunPath)"
    $typescriptReportPath = Join-Path $Meta.EvidenceRunPath "typescript-results.json"
    if (Test-Path $typescriptReportPath -PathType Leaf) {
        Add-Line "TypeScript JSON: $typescriptReportPath"
    }
    else {
        Add-Line "TypeScript JSON: not produced (validation skipped, compile failed, or runner failed before report creation)"
    }
    $typescriptOutputPaths = @(
        (Join-Path $Meta.EvidenceRunPath "typescript.stdout.log"),
        (Join-Path $Meta.EvidenceRunPath "typescript.stderr.log"),
        (Join-Path $Meta.EvidenceRunPath "typescript-compile.log")
    ) | Where-Object { Test-Path $_ -PathType Leaf }
    if ($typescriptOutputPaths.Count -gt 0) {
        Add-Line "TypeScript process output: $($typescriptOutputPaths -join ', ')"
    }
    Add-Line "Version: $versionStr"
    Add-Line "Date: $dateStr"
    Add-Line "Duration: $durationStr"
    Add-Line "ARM validation method: $ArmValidationMethod"
    Add-Line "ARM validation status: $(if ($ArmValidationMethod -eq 'lab-deployment') { 'pending' } else { 'see validator results' })"
    Add-Line "Package accepted: false"
    Add-Line "Result: $(if (-not $Success) { 'FAILED' } elseif ($ArmValidationMethod -eq 'lab-deployment') { 'CANDIDATE_GENERATED' } else { 'PASSED' })"
    if ($Meta.ValidationBindingPath) {
        Add-Line "Validation binding: $($Meta.ValidationBindingPath)"
        Add-Line "Validation binding SHA256: $($Meta.ValidationBindingSha256)"
        Add-Line "Validation binding result: $($Meta.ValidationBindingResult)"
    }
    elseif ($Meta.ValidationBindingResult) {
        Add-Line "Validation binding result: $($Meta.ValidationBindingResult)"
    }
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
            if ($e.SkipReason) {
                $cleanSkip = ($e.SkipReason -replace '\|', '\|' -replace '[\r\n]+', ' ').Trim()
                $detailParts += $cleanSkip
            }
            if ($e.OutputLog) { $detailParts += "full output: $($e.OutputLog)" }
            $detail = if ($detailParts.Count -gt 0) { (($detailParts -join ", ") -replace '[\r\n]+', ' ').Trim() } else { "-" }
            Add-Line "| $stepLabel | $($e.Name) | $status | $detail |"

            if ($e.Status -eq "failed" -and $e.Errors) {
                foreach ($err in $e.Errors) {
                    $cleanErr = $err -replace '\|', '\|' -replace '\r?\n', '<br>'
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
    $skippedValidators = @($allValidators | Where-Object { $_.Status -eq "skipped" })
    if ($skippedValidators.Count -gt 0) {
        Add-Line "⚠️ Skipped / Unsupported Checks ($($skippedValidators.Count)):"
        foreach ($sv in $skippedValidators) {
            $svReason = if ($sv.SkipReason) { ($sv.SkipReason -replace '[\r\n]+', ' ').Trim() } else { "Skipped" }
            Add-Line "- $($sv.Name): $svReason"
        }
        Add-Line ""
    }
    if ($Success -and $ArmValidationMethod -eq "lab-deployment") {
        Add-Line "**CANDIDATE GENERATED — NOT ACCEPTED**"
        Add-Line "All reported static checks completed; approved deployment and workbook contract readback remain pending."
    }
    elseif ($Success) {
        Add-Line "**BUILD SUCCESSFUL**"
    }
    else {
        Add-Line "**BUILD FAILED**"
    }
    Add-Line ""

    # --- Write report to stdout ---
    $reportPath = Join-Path $Meta.EvidenceRunPath "build-and-validate-report.md"
    $reportContent = "[REPORT_START]`n" + ($lines -join "`n") + "`n[REPORT_END]`n"
    [System.IO.File]::WriteAllText($reportPath, $reportContent, [System.Text.UTF8Encoding]::new($false))
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
