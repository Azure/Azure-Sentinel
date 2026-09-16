param(
    [string]$SolutionDataFolderPath = $null,
    [ValidateSet("catalog", "local")]
    [string]$VersionMode = "catalog",
    [ValidateSet("none", "patch", "minor", "major")]
    [string]$VersionBump = "patch"
)

$localImplementation = Join-Path $PSScriptRoot "..\common\createSolutionLocal.ps1"
& $localImplementation `
    -SolutionDataFolderPath $SolutionDataFolderPath `
    -VersionMode $VersionMode `
    -VersionBump $VersionBump `
    -EntryPointName "V3" `
    -DefaultInputPath (Join-Path $PSScriptRoot "input") `
    -IncludeXdrDetections $false
