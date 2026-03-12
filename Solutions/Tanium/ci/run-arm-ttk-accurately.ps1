<#
.SYNOPSIS
Runs the arm-ttk validation against a specific solution, to ensure they will pass marketplace validations. This is a simplified version of ./Tools/Create-Azure-Sentinel-Solution/arm-ttk/run-arm-ttk-in-automation.ps1 which outputs the results and isn't good for automation. Additionally there is a known false positive regarding the "IDs Should Be Derived From ResourceIDs" noted here: https://github.com/Azure/Azure-Sentinel/blob/acb08c1c6e1dde30a891d5314fe47d6511e92175/Tools/Create-Azure-Sentinel-Solution/V3/README.md#ids-should-be-derived-from-resourceids

This script will filter out that particular failure.

.DESCRIPTION
This script runs the arm-ttk PowerShell module to validate the ARM templates in the specified solution. Then it will throw an error if any failures are found.

.PARAMETER SolutionName
Specifies the name of the folder found in the `./Solutions` folder that should be tested.

.EXAMPLE
PS ./Solutions/Tanium/ci/run-arm-ttk-accurately.ps1 "Tanium"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SolutionName
)

$repoRoot = $(git rev-parse --show-toplevel).ToString().Trim()
$root = "$repoRoot/Solutions"

if (!$(Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)) {
    Write-Error "You must install the arm-ttk module for PowerShell"
    exit 1
}

# Resolve the solution's Package folder (where mainTemplate.json lives)
$packagePath = Join-Path -Path $root -ChildPath "$SolutionName/Package"
if (-not (Test-Path -Path $packagePath -PathType Container)) {
    Write-Error "Package folder not found: $packagePath"
    exit 1
}
$solution = Get-Item -Path $packagePath

$testFailures = @()

# Conduct an initial run using the tool and suppress results,
#  due to race condition which may cause faulty result formatting
$results = @(Test-AzTemplate -TemplatePath "$root/Templates")


$results = @(Test-AzTemplate -TemplatePath $solution.FullName)
$testFailures = $results | Where-Object { -not $_.Passed }

# Filter out the known false positive
$testFailures = $testFailures | Where-Object { $_.Group -ne "IDs Should Be Derived From ResourceIDs" }

# finally exit with non-zero code on errors (use @() so count works for both single object and array)
$failureCount = @($testFailures).Count
if ($failureCount -gt 0) {
    Write-Error "Failed arm-ttk with $failureCount failure(s)."
    exit 1
}
