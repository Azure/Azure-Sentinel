param(
    [string]$SolutionDataFolderPath = $null
)

$repositoryBasePath = $SolutionDataFolderPath.Substring(0, $indexOfSolutions)
$commonFunctionsFilePath = $repositoryBasePath + "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1"
$catalogAPIFilePath = $repositoryBasePath + ".script/package-automation/catalogAPI.ps1"
# cspell:disable-next-line
$getccpDetailsFilePath = $repositoryBasePath + "Tools/Create-Azure-Sentinel-Solution/common/get-ccp-details.ps1"

. $commonFunctionsFilePath # load common functions
. $catalogAPIFilePath # load catalog api functions
# cspell:disable-next-line
. $getccpDetailsFilePath # load ccp functions


function GetOfferId($solutionDataFolderPath)
{
    $solutionManifestFile = $(Get-ChildItem $solutionDataFolderPath)
    $solutionManifest = Get-Content -Raw $solutionManifestFile | Out-String | ConvertFrom-Json
    $companyName = $solutionManifest.Name

    $indexOfSolutions = $SolutionDataFolderPath.IndexOf('Solutions')
    $solutionBasePath = $SolutionDataFolderPath.Substring(0, $indexOfSolutions + 10)

    # Builds the path to the metadata file
    $metadataPath = $solutionBasePath + "$($companyName)/$($solutionManifest.Metadata)"
    $solutionMetaData = Get-Content -Raw $metadataPath | Out-String | ConvertFrom-Json
    return $solutionMetaData.offerId
}

function global:Write-Host() {}

$offerId = GetOfferId $SolutionDataFolderPath
$offerDetails = GetCatalogDetails $offerId

$mainTemplateDetails = $offerDetails.plans.artifacts | Where-Object {$_.type -eq "Template" -and $_.name -eq "DefaultTemplate"}
$mainTemplateUri = $mainTemplateDetails.uri

$offerMetadataVersion = GetOfferVersion $offerId $mainTemplateUri 
Remove-Item Function:\Write-Host
return $offerMetadataVersion

# $userInputPackageVersion = $contentToImport.version
# $packageVersion = GetPackageVersion $defaultPackageVersion $offerId $offerDetails $true $userInputPackageVersion