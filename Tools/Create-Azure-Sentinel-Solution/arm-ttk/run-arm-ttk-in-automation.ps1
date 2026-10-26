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
. (Join-Path $repoRoot ".script/package-automation/arm-ttk-sentinel-filters.ps1")

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

    $templateText = (Get-ChildItem -LiteralPath $dir.FullName -Filter mainTemplate.json -Recurse |
        ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw }) -join "`n"
    $testParameter = Get-SentinelArmTtkTestParameter -TemplateText $templateText
    $results = @(Test-AzTemplate -TemplatePath $dir.FullName -TestParameter $testParameter)
    $resolved = Resolve-SentinelArmTtkMainTemplateResults -Results $results

    foreach ($testInfo in $resolved.Results) {
        $testInfo.PSObject.Properties.Remove('TestInput')
        $testInfo.PSObject.Properties.Remove('File')
    }

    $resolved.Results
    Write-Host "ARM-TTK: Pass=$($resolved.Pass) Fail=$($resolved.Fail) ExemptedIdErrors=$($resolved.ExemptedErrors)"

    if ($resolved.Fail -gt 0) {
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
