<#
.SYNOPSIS
This is a script that uses the same logic that the Tools in this repo use to validate the JSON files. However, unlike the original it does not output any noise, so that if the script fails we know it's because the JSON isn't valid. This is much better for automation. 

.DESCRIPTION
This script validates that all JSON files are valid. Then it will throw an error if any failures are found.

This script installs the arm-ttk validator. Then runs it against the specified Solution in this repo. Then it will throw an error if any failures are found.

.EXAMPLE
PS ./Solutions/Tanium/ci/run-json-validation.ps1
#>


$repoRoot = $(git rev-parse --show-toplevel)
$commonFunctionsFilePath = $repoRoot + "/Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1"

. $commonFunctionsFilePath # load common functions

$packageFolderPath = "../Package/*.json"

if ((Test-Path -Path "$packageFolderPath")) {
    [array]$packageFolderFiles = Get-ChildItem "$packageFolderPath" -Recurse | Select-Object -expand fullname

    $count = 0
    foreach ($filePath in $packageFolderFiles) {
        $isValid = Get-Content "$filePath" -Raw | Test-Json -ErrorAction SilentlyContinue
        if (!$isValid) {
            $count++
        }
    }

    if ($count -gt 0) {
        Write-Host "Failed JSON validation with $count failure(s)."
        exit 1
    }
    
} else {
    Write-Host "Check solution folder path provided. $packageFolderPath does not exist."
    exit 1
}