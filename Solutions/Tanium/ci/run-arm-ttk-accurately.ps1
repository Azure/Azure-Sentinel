<#
.SYNOPSIS
Runs the arm-ttk validation against a specific solution, to ensure they will pass marketplace validations. This is a simplified version of ./Tools/Create-Azure-Sentinel-Solution/arm-ttk/run-arm-ttk-in-automation.ps1 which outputs the results and isn't good for automation.

Skips (aligned with .github/actions/entrypoint.ps1):
- "Template Should Not Contain Blanks" (blanks come from serialized workbook/playbook JSON; marketplace validation skips this).
- "URIs Should Be Properly Constructed".
- "IDs Should Be Derived From ResourceIDs" (known false positive; see Tools/Create-Azure-Sentinel-Solution/V3/README.md).

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

# Skip rules that the official marketplace validation skips (see .github/actions/entrypoint.ps1).
# "Template Should Not Contain Blanks" flags null/[] in serialized workbook/playbook JSON; fixing would require editing embedded JSON strings.
# "URIs Should Be Properly Constructed" is skipped there as well.
$skipRules = @("Template Should Not Contain Blanks", "URIs Should Be Properly Constructed")

# Conduct an initial run using the tool and suppress results,
#  due to race condition which may cause faulty result formatting
$results = @(Test-AzTemplate -TemplatePath "$root/Templates" -Skip $skipRules)

$results = @(Test-AzTemplate -TemplatePath $solution.FullName -Skip $skipRules)
$testFailures = $results | Where-Object { -not $_.Passed }

# Filter out the known false positive (property may be Group or Name depending on arm-ttk version)
$testFailures = $testFailures | Where-Object {
    ($_.Group -ne "IDs Should Be Derived From ResourceIDs") -and
    ($_.Name -ne "IDs Should Be Derived From ResourceIDs")
}

# finally exit with non-zero code on errors (use @() so count works for both single object and array)
$failureCount = @($testFailures).Count
if ($failureCount -gt 0) {
    Write-Error "Failed arm-ttk with $failureCount failure(s)."
    foreach ($failure in $testFailures) {
        $ruleName = if ($failure.Name) { $failure.Name } elseif ($failure.Group) { $failure.Group } else { $failure.RuleName }
        Write-Host ""
        Write-Host "--- Rule: $ruleName ---" -ForegroundColor Red
        $filePath = $failure.File
        if ($filePath -is [System.Collections.IDictionary]) {
            $filePath = if ($filePath.FullName) { $filePath.FullName } else { $filePath.Path }
        }
        if (-not $filePath) { $filePath = $failure.FileName }
        if ($filePath) { Write-Host "File: $filePath" }
        $messages = [System.Collections.ArrayList]::new()
        if ($failure.Errors -and $failure.Errors.Count -gt 0) {
            foreach ($err in $failure.Errors) {
                $msg = if ($err.Exception -and $err.Exception.Message) { $err.Exception.Message } else { [string]$err }
                if ($msg -and $messages -notcontains $msg) { [void]$messages.Add($msg) }
            }
        } elseif ($failure.Message) {
            [void]$messages.Add($failure.Message)
        }
        $maxMessages = 10
        $shown = 0
        foreach ($msg in $messages) {
            if ($shown -ge $maxMessages) {
                Write-Host "Message: ... and $($messages.Count - $maxMessages) more (total $($messages.Count) occurrences)" -ForegroundColor DarkGray
                break
            }
            Write-Host "Message: $msg"
            $shown++
        }
        if ($failure.Recommendation) { Write-Host "Recommendation: $($failure.Recommendation)" }
    }
    exit 1
}
