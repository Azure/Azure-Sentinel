# Script to run arm-ttk against a specific solution,
#  to ensure they will pass marketplace validations
# This is a simplified version of run-arm-ttk.ps1 which outputs the results as is,
#  without accounting for ADO Unit Test Formatting.

param(
    [Parameter(Mandatory = $false)]
    [string]$SolutionName
)

# Paths
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../../.."))
$root="$repoRoot/Solutions"
$tmp = Join-Path (Split-Path -Parent $PSScriptRoot) "tmp"
$moduleManifest = Join-Path (Join-Path $tmp "arm-ttk") "arm-ttk.psd1"

if(!$(Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)){
    Import-Module $moduleManifest
}

# Run 'Test-AzTemplate' from the arm-ttk for given solution package
$solutions = Get-ChildItem $root -Directory
if($SolutionName){
    $solutions = Get-Item "$root/$SolutionName/Package"
}
$fails = @()
$skip = "poc","template", "automation"

# Conduct an initial run using the tool and suppress results,
#  due to race condition which may cause faulty result formatting
try {
    $initialRun = @(Test-AzTemplate -TemplatePath "$root/Templates" -ErrorAction SilentlyContinue *>$null)
}
catch {
}
finally {
    $global:LASTEXITCODE = 0
}

foreach ($dir in $solutions) {
    $name = $dir.Name
    # Skip the example solutions
    if($skip.Contains($name)){
        continue
    }

    $results = @(Test-AzTemplate -TemplatePath $dir.FullName)
    $filteredResults = New-Object System.Collections.ArrayList
    $filteredIdTestCount = 0

    foreach ($testInfo in $results) {
        $testInfo.PSObject.Properties.Remove('TestInput')
        $testInfo.PSObject.Properties.Remove('File')

        if ($testInfo.Name -eq 'IDs Should Be Derived From ResourceIDs' -and $testInfo.Errors.Count -gt 0) {
            $hasUnfilteredIdError = $false
            $hasExemptIdError = $false
            foreach ($errorInfo in $testInfo.Errors) {
                if ($errorInfo.Exception.Message -like '*"contentProductId"*' -or
                    $errorInfo.Exception.Message -like '*"id"*' -or
                    $errorInfo.Exception.Message -like '*"packageId"*' -or
                    $errorInfo.Exception.Message -like '*"fromTemplateId"*') {
                    $hasExemptIdError = $true
                }
                else {
                    $hasUnfilteredIdError = $true
                }
            }
            if ($hasUnfilteredIdError) {
                $null = $filteredResults.Add($testInfo)
            }
            elseif ($hasExemptIdError) {
                $filteredIdTestCount++
            }
        }
        else {
            if ($null -ne $testInfo.Summary -and $filteredIdTestCount -gt 0) {
                $testInfo.Summary.Fail = [Math]::Max(0, $testInfo.Summary.Fail - $filteredIdTestCount)
                $testInfo.Summary.Pass = $testInfo.Summary.Pass + $filteredIdTestCount
            }
            $null = $filteredResults.Add($testInfo)
        }
    }

    $filteredResults

    if ($filteredResults | Where-Object {$_.Errors}) {
        Write-Host "Failed arm-ttk (Test-AzTemplate): $name"
        $fails += $name
    }
}

# finally exit with non-zero code on errors
if($fails.Length -gt 0){
    $message = $fails -join ", "
    Write-Host "Failed arm-ttk (Test-AzTemplate) on solutions: $message"
    exit 1
}
