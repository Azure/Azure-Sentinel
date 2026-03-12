<#
.SYNOPSIS
Uses the existing scripts from the Tools folder, to get the new version number to build for the specified solution, but ensures that the noisy output is disabled, since the outputs aren't good for automation and this modularity also allows for automation too.

.DESCRIPTION
This script first obtains the required 5 parameters for the GetPackageVersion function and then returns the version number to use for the build. It does this with the output silenced.

.PARAMETER SolutionDataFolderPath
Specifies the path to the Data folder for the particular package you are attempting to test.

.OUTPUTS
The new version number for the build of the specified solution. It will be in the format of #.#.#

.EXAMPLE
PS ./Solutions/Tanium/ci/get-new-version.ps1 "./Solutions/Tanium/Data"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SolutionDataFolderPath
)

# Reject empty or whitespace-only (Mandatory only prevents omitted param)
if ([string]::IsNullOrWhiteSpace($SolutionDataFolderPath)) {
    Write-Error "SolutionDataFolderPath is required."
    exit 1
}

$currentPath = $PWD.Path
$repoRoot = $(git rev-parse --show-toplevel).ToString().Trim()

# Resolve path so it is valid from repo root when invoked from Task (cwd = ci)
$pathToUse = $SolutionDataFolderPath
if (-not [System.IO.Path]::IsPathRooted($SolutionDataFolderPath)) {
    $pathToUse = (Join-Path -Path $repoRoot -ChildPath ($SolutionDataFolderPath -replace '^\.\/', '' -replace '^\.\\', '')).Replace('\', '/')
}

# We must change dirs, since the Azure team wrote this script to run at the root
Set-Location $repoRoot

try {
    . "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1"
    . ".script/package-automation/catalogAPI.ps1"
    # cspell:disable-next-line
    . "Tools/Create-Azure-Sentinel-Solution/common/get-ccp-details.ps1"

    $defaultPackageVersion = "3.0.0"

    function GetOfferIdSilently($solutionDataFolderPath)
    {
        $solutionManifestFile = $(Get-ChildItem $solutionDataFolderPath)
        $solutionManifest = Get-Content -Raw $solutionManifestFile | Out-String | ConvertFrom-Json
        $companyName = $solutionManifest.Name

        $indexOfSolutions = $solutionDataFolderPath.IndexOf('Solutions')
        $solutionBasePath = $solutionDataFolderPath.Substring(0, $indexOfSolutions + 10)

        # Builds the path to the metadata file
        $metadataPath = $solutionBasePath + "$($companyName)/$($solutionManifest.Metadata)"
        $solutionMetaData = Get-Content -Raw $metadataPath | Out-String | ConvertFrom-Json
        return $solutionMetaData.offerId
    }

    function GetOfferDetailsSilently($offerId){
        $offerDetails = GetCatalogDetails $offerId
        return $offerDetails
    }

    function global:Write-Host() {}

    # Get the offerId value
    $offerId = GetOfferIdSilently $pathToUse

    # Get the offer details
    $offerDetails = GetOfferDetailsSilently $offerId
    if (-not $offerDetails) {
        Write-Error "Could not get offer details for offerId $offerId."
        exit 1
    }

    # Derive solution manifest file from Data folder (same convention as createSolutionV3.ps1)
    $excluded = @("parameters.json", "parameter.json", "system_generated_metadata.json", "testParameters.json")
    $solutionManifestItem = Get-ChildItem -Path $pathToUse -File | Where-Object { $_.Name -notin $excluded } | Select-Object -First 1
    if (-not $solutionManifestItem) {
        Write-Error "Solution manifest file not found in $pathToUse"
        exit 1
    }
    $solutionFile = $solutionManifestItem.FullName

    $contentToImport = Get-Content -Raw $solutionFile | Out-String | ConvertFrom-Json

    # Get the package version attribute
    $packageVersionAttribute = [bool]($contentToImport.PSobject.Properties.Name -match "version")

    # Get the user input package version
    $userInputPackageVersion = $contentToImport.version

    $packageVersion = GetPackageVersion $defaultPackageVersion $offerId $offerDetails $packageVersionAttribute $userInputPackageVersion

    Remove-Item Function:\Write-Host

    return $packageVersion
}
finally {
    Set-Location $currentPath
}
