<#
.SYNOPSIS
Uses the existing scripts from the Tools folder, to get the currently published version of the specified solution, but ensures that the noisy output is disabled, since the outputs aren't good for automation and this modularity also allows for automation too.

.DESCRIPTION
This script first obtains the required 4 parameter for the GetOfferVersion function and then returns the offer version value. It does this with the output silenced.

.PARAMETER SolutionDataFolderPath
Specifies the path to the Data folder for the particular package you are attempting to test.

.OUTPUTS
The currently published version of the specified solution. It will be in the format of #.#.#

.EXAMPLE
PS ./Solutions/Tanium/ci/get-published-version.ps1 "./Solutions/Tanium/Data"
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
    . "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1" # load common functions
    . ".script/package-automation/catalogAPI.ps1" # load catalog api functions
    # cspell:disable-next-line
    . "Tools/Create-Azure-Sentinel-Solution/common/get-ccp-details.ps1" # load ccp functions

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

    $mainTemplateDetails = $offerDetails.plans.artifacts | Where-Object {$_.type -eq "Template" -and $_.name -eq "DefaultTemplate"}
    $mainTemplateUri = $mainTemplateDetails.uri
    if (-not $mainTemplateDetails -or -not $mainTemplateUri) {
        Write-Error "Offer details do not contain a DefaultTemplate artifact; cannot get published version."
        exit 1
    }

    $offerMetadataVersion = GetOfferVersion $offerId $mainTemplateUri

    Remove-Item Function:\Write-Host

    return $offerMetadataVersion
}
finally {
    Set-Location $currentPath
}