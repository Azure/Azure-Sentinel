#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run ARM-TTK validation on a Sentinel solution package.
    Same checks and error filters as .github/actions/entrypoint.ps1.

.DESCRIPTION
    Validates mainTemplate.json and createUiDefinition.json in the solution's Package/ folder
    using Test-AzTemplate from the ARM-TTK module.

    The ARM-TTK module is auto-installed on first run by cloning from GitHub into .arm-ttk/
    at the repository root.

    Tests and exemptions match entrypoint.ps1 exactly because both dot-source
    .script/package-automation/arm-ttk-sentinel-filters.ps1:
      - No ARM-TTK tests are skipped.
      - 'IDs Should Be Derived From ResourceIDs': only exact Sentinel content identifier
        properties and customDetails *Id column names are exempt.
      - 'Template Should Not Contain Blanks': blanks are allowed only inside workbook
        payloads (classic serializedData and Defender workbook properties.content).

.PARAMETER SolutionPath
    Full path to the solution folder (e.g., C:\repo\Solutions\MySolution).
    Must contain a Package/ subfolder with mainTemplate.json.

.PARAMETER ToolkitRoot
    Checkout containing the ARM-TTK helper module and .gitignore. Defaults to the
    toolkit checkout containing this script, independently of SolutionPath.

.EXAMPLE
    ./run-arm-ttk.ps1 -SolutionPath "C:/sentinel/AzureSentinel/Solutions/CrowdStrike Falcon Endpoint Protection"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SolutionPath,

    [string]$ToolkitRoot
)

$ErrorActionPreference = "Continue"

# --------------------------------------------------------------------------
# Resolve repo root
# --------------------------------------------------------------------------
$repoRoot = if ($ToolkitRoot) {
    [System.IO.Path]::GetFullPath($ToolkitRoot)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../.."))
}
if (-not (Test-Path (Join-Path $repoRoot ".script/local-validation/run-arm-ttk.ps1") -PathType Leaf)) {
    Write-Host "ARM-TTK: Invalid toolkit root: $repoRoot" -ForegroundColor Red
    Write-Host "ARM-TTK-SUMMARY: Pass=0 Fail=1 Total=1 Error=true"
    exit 2
}

# --------------------------------------------------------------------------
# Locate Package folder
# --------------------------------------------------------------------------
$packageDir = Join-Path $SolutionPath "Package"
if (-not (Test-Path $packageDir)) {
    Write-Host "ARM-TTK: Package/ folder not found — skipping." -ForegroundColor Yellow
    Write-Host "ARM-TTK-SUMMARY: Pass=0 Fail=0 Total=0 Skipped=true"
    exit 0
}

$mainTemplate = Join-Path $packageDir "mainTemplate.json"
$createUiDef  = Join-Path $packageDir "createUiDefinition.json"

$hasMain     = Test-Path $mainTemplate
$hasCreateUi = Test-Path $createUiDef

if (-not $hasMain -and -not $hasCreateUi) {
    Write-Host "ARM-TTK: No mainTemplate.json or createUiDefinition.json found — skipping." -ForegroundColor Yellow
    Write-Host "ARM-TTK-SUMMARY: Pass=0 Fail=0 Total=0 Skipped=true"
    exit 0
}

# --------------------------------------------------------------------------
# Ensure ARM-TTK module is available
# --------------------------------------------------------------------------
$armTtkModule = Get-Module -ListAvailable arm-ttk -ErrorAction SilentlyContinue

if (-not $armTtkModule) {
    # Check local clone
    $localClonePath = Join-Path $repoRoot ".arm-ttk"
    $localPsd1 = Join-Path $localClonePath "arm-ttk/arm-ttk.psd1"

    if (-not (Test-Path $localPsd1)) {
        Write-Host "ARM-TTK module not found — cloning from GitHub..." -ForegroundColor Yellow
        git clone --depth 1 https://github.com/Azure/arm-ttk.git "$localClonePath" 2>&1 | Write-Host

        if (-not (Test-Path $localPsd1)) {
            Write-Host "ARM-TTK: Failed to clone arm-ttk repository." -ForegroundColor Red
            Write-Host "ARM-TTK-SUMMARY: Pass=0 Fail=0 Total=0 Error=true"
            exit 1
        }

        # Add .arm-ttk/ to .gitignore if not already present
        $gitignorePath = Join-Path $repoRoot ".gitignore"
        if (Test-Path $gitignorePath) {
            $gitignoreContent = Get-Content $gitignorePath -Raw
            if ($gitignoreContent -notmatch '(?m)^\.arm-ttk/?') {
                Add-Content $gitignorePath -Value "`n# ARM-TTK local clone (auto-installed)`n.arm-ttk/" -Encoding UTF8
                Write-Host "Added .arm-ttk/ to .gitignore" -ForegroundColor Gray
            }
        }
    }

    Import-Module $localPsd1 -Force
}
else {
    Import-Module arm-ttk -Force
}

# --------------------------------------------------------------------------
# Shared configuration — same file dot-sourced by entrypoint.ps1
# --------------------------------------------------------------------------
$sharedFilters = Join-Path $repoRoot ".script/package-automation/arm-ttk-sentinel-filters.ps1"
if (-not (Test-Path $sharedFilters -PathType Leaf)) {
    Write-Host "ARM-TTK: Shared filter script not found: $sharedFilters" -ForegroundColor Red
    Write-Host "ARM-TTK-SUMMARY: Pass=0 Fail=1 Total=1 Error=true"
    exit 2
}
. $sharedFilters

$totalPass = 0
$totalFail = 0
$exitCode  = 0

# --------------------------------------------------------------------------
# Run on mainTemplate.json — mirrors entrypoint.ps1 logic exactly
# --------------------------------------------------------------------------
if ($hasMain) {
    Write-Host "Running ARM-TTK on mainTemplate.json..." -ForegroundColor Cyan

    try {
        $mainTemplateText = Get-Content -Raw $mainTemplate
        $testParameter = Get-SentinelArmTtkTestParameter -TemplateText $mainTemplateText
        $rawResults = Test-AzTemplate -TemplatePath $packageDir -File mainTemplate.json -TestParameter $testParameter
        $resolved = Resolve-SentinelArmTtkMainTemplateResults -Results @($rawResults)

        Write-Output $resolved.Results
        Write-Host "MainTemplate.json ARM-TTK: Pass=$($resolved.Pass) Fail=$($resolved.Fail) ExemptedIdErrors=$($resolved.ExemptedErrors)"

        $totalPass += $resolved.Pass
        $totalFail += $resolved.Fail

        if ($resolved.Fail -gt 0) {
            Write-Host "Please review and rectify the 'MainTemplate.json' file as some of the ARM-TTK tests did not pass!" -ForegroundColor Red
            $exitCode = 1
        }
        else {
            Write-Host "All tests passed for the 'MainTemplate.json' file!" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "ARM-TTK error on mainTemplate.json: $($_.Exception.Message)" -ForegroundColor Red
        $totalFail++
        $exitCode = 1
    }

    Write-Host ""
}

# --------------------------------------------------------------------------
# Run on createUiDefinition.json — mirrors entrypoint.ps1 logic exactly
# --------------------------------------------------------------------------
if ($hasCreateUi) {
    Write-Host "Running ARM-TTK on createUiDefinition.json..." -ForegroundColor Cyan

    try {
        $uiResults = Test-AzTemplate -TemplatePath $packageDir -File createUiDefinition.json

        $uiPassed = $uiResults | Where-Object { -not $_.Failed }
        Write-Output $uiPassed

        $uiFailures = $uiResults | Where-Object { -not $_.Passed }
        $uiSummary  = $uiResults | Where-Object { $null -ne $_.Summary } | Select-Object -Last 1

        if ($uiSummary) {
            $totalPass += $uiSummary.Summary.Pass
            $totalFail += $uiSummary.Summary.Fail
        }

        if ($uiFailures) {
            Write-Host "Please review and rectify the 'CreateUiDefinition.json' file as some of the ARM-TTK tests did not pass!" -ForegroundColor Red
            $exitCode = 1
        }
        else {
            Write-Host "All tests passed for the 'CreateUiDefinition.json' file!" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "ARM-TTK error on createUiDefinition.json: $($_.Exception.Message)" -ForegroundColor Red
        $totalFail++
        $exitCode = 1
    }

    Write-Host ""
}

# --------------------------------------------------------------------------
# Parseable summary line (always output last)
# --------------------------------------------------------------------------
$total = $totalPass + $totalFail
Write-Host "ARM-TTK-SUMMARY: Pass=$totalPass Fail=$totalFail Total=$total"

exit $exitCode
