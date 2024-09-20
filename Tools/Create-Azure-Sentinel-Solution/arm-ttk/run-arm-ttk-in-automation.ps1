# Script to run arm-ttk against a specific solution,
#  to ensure they will pass marketplace validations
# This is a simplified version of run-arm-ttk.ps1 which outputs the results as is,
#  without accounting for ADO Unit Test Formatting.

# Paths
$repoRoot = $(git rev-parse --show-toplevel)
$root="$repoRoot/Solutions"
$tmp="$PSScriptRoot/tmp"
$solutionName=$args[0]

if(!$(Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)){
    Import-Module "$tmp/arm-ttk/arm-ttk.psd1"
}

# Run 'Test-AzTemplate' from the arm-ttk for given solution package
$solutions = Get-ChildItem $root -Directory
if($solutionName){
    $solutions = Get-Item "$root/$solutionName/Package"
}
$fails = @()
$skip = "poc","template", "automation"

# Conduct an initial run using the tool and suppress results,
#  due to race condition which may cause faulty result formatting
$initialRun = @(Test-AzTemplate -TemplatePath "$root/Templates")

foreach ($dir in $solutions) {
    $name = $dir.Name
    # Skip the example solutions
    if($skip.Contains($name)){
        continue
    }

    $results = @(Test-AzTemplate -TemplatePath $dir.FullName)
    $results

    if ($results | Where-Object {$_.Errors}) {
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
