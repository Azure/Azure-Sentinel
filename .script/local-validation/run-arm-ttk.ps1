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

    Test skips and error filters match entrypoint.ps1 exactly:
      - Skipped: "Template Should Not Contain Blanks", "URIs Should Be Properly Constructed"
      - Filtered: contentProductId and id errors in 'IDs Should Be Derived From ResourceIDs'

.PARAMETER SolutionPath
    Full path to the solution folder (e.g., C:\repo\Solutions\MySolution).
    Must contain a Package/ subfolder with mainTemplate.json.

.EXAMPLE
    ./run-arm-ttk.ps1 -SolutionPath "C:/sentinel/AzureSentinel/Solutions/CrowdStrike Falcon Endpoint Protection"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SolutionPath
)

$ErrorActionPreference = "Continue"

# --------------------------------------------------------------------------
# Resolve repo root
# --------------------------------------------------------------------------
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    $repoRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
}
$repoRoot = $repoRoot.Replace('\', '/')

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
# Shared configuration — mirrors entrypoint.ps1 exactly
# --------------------------------------------------------------------------
$skipTests = @("Template Should Not Contain Blanks", "URIs Should Be Properly Constructed")

$totalPass = 0
$totalFail = 0
$exitCode  = 0

# --------------------------------------------------------------------------
# Run on mainTemplate.json — mirrors entrypoint.ps1 logic exactly
# --------------------------------------------------------------------------
if ($hasMain) {
    Write-Host "Running ARM-TTK on mainTemplate.json..." -ForegroundColor Cyan

    try {
        $rawResults = Test-AzTemplate -TemplatePath $packageDir -File mainTemplate.json -Skip $skipTests

        # Filter out contentProductId/id false positives — same as entrypoint.ps1
        $filtered = New-Object System.Collections.ArrayList
        $hasContentProductIdError = $false

        foreach ($testInfo in $rawResults) {
            if ($testInfo.Name -eq 'IDs Should Be Derived From ResourceIDs' -and $testInfo.Errors.Count -gt 0) {
                foreach ($errorInfo in $testInfo.Errors) {
                    if ($errorInfo.Exception.Message -like '*"contentProductId"*' -or
                        $errorInfo.Exception.Message -like '*"id"*') {
                        $hasContentProductIdError = $true
                    }
                    else {
                        $null = $filtered.Add($testInfo)
                    }
                }
            }
            else {
                if ($null -ne $testInfo.Summary -and $hasContentProductIdError -eq $true) {
                    $testInfo.Summary.Fail = $testInfo.Summary.Fail - 1
                    $testInfo.Summary.Pass = $testInfo.Summary.Pass + 1
                }
                $null = $filtered.Add($testInfo)
            }
        }

        Write-Output $filtered

        # Extract summary
        $mainSummary = $filtered | Where-Object { $null -ne $_.Summary } | Select-Object -Last 1
        if ($mainSummary) {
            $totalPass += $mainSummary.Summary.Pass
            $totalFail += $mainSummary.Summary.Fail
        }

        if ($mainSummary -and $mainSummary.Summary.Fail -gt 0) {
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
        $uiResults = Test-AzTemplate -TemplatePath $packageDir -File createUiDefinition.json -Skip $skipTests

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
