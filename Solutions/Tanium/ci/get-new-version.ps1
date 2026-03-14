<#
.SYNOPSIS
Uses the existing scripts from the Tools folder, to get the new version number to build for the specified solution, but ensures that the noisy output is disabled, since the outputs aren't good for automation and this modularity also allows for automation too.

.DESCRIPTION
This script first obtains the required 5 parameters for the GetPackageVersion function and then returns the version number to use for the build. It does this with the output silenced.

.PARAMETER SolutionDataFolderPath
Specifies the path to the Data folder for the particular package you are attempting to test.

.PARAMETER VersionBump
Optional. When provided, uses local version mode: reads the version from the solution data file and returns the version incremented by this bump type (major, minor, or patch). If not provided, uses catalog mode and returns the version from the Microsoft catalog (same as createSolutionV3).

.OUTPUTS
The new version number for the build of the specified solution. It will be in the format of #.#.#

.EXAMPLE
PS ./Solutions/Tanium/ci/get-new-version.ps1 "./Solutions/Tanium/Data"

.EXAMPLE
PS ./Solutions/Tanium/ci/get-new-version.ps1 "./Solutions/Tanium/Data" -VersionBump minor
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SolutionDataFolderPath,
    [Parameter(Mandatory = $false)]
    [ValidateSet("major", "minor", "patch")]
    [string]$VersionBump
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
    $defaultPackageVersion = "3.0.0"

    # Matches createSolutionV3.ps1 GetIncrementedVersion (for local version mode)
    function GetIncrementedVersion($version, $bumpType = "patch") {
        if ([string]::IsNullOrWhiteSpace($version)) {
            $version = "1.0.0"
        }
        $versionParts = $version.split(".")
        if ($versionParts.Length -lt 3) {
            while ($versionParts.Length -lt 3) {
                $versionParts += "0"
            }
        }
        $major = $versionParts[0].Trim()
        $minor = $versionParts[1].Trim()
        $patch = $versionParts[2].Trim()
        try {
            [int]$majorInt = [Convert]::ToInt32($major)
            [int]$minorInt = [Convert]::ToInt32($minor)
            [int]$patchInt = [Convert]::ToInt32($patch)
        }
        catch {
            $majorInt = 1
            $minorInt = 0
            $patchInt = 0
        }
        switch ($bumpType.ToLower().Trim()) {
            "major" { $majorInt += 1; $minorInt = 0; $patchInt = 0 }
            "minor" { $minorInt += 1; $patchInt = 0 }
            "patch" { $patchInt += 1 }
            default { $patchInt += 1 }
        }
        return "$majorInt.$minorInt.$patchInt"
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
    $packageVersionAttribute = [bool]($contentToImport.PSobject.Properties.Name -match "version")
    $userInputPackageVersion = $contentToImport.version

    if ($PSBoundParameters.ContainsKey('VersionBump')) {
        # Local mode: same logic as createSolutionV3 GetLocalPackageVersion (without file updates)
        if ($packageVersionAttribute -and $null -ne $userInputPackageVersion -and $userInputPackageVersion -ne '') {
            $versionParts = $userInputPackageVersion.split(".")
            if ($versionParts.Length -lt 3) {
                return $defaultPackageVersion
            }
            try {
                [int]$null = $versionParts[0]
                [int]$null = $versionParts[1]
                [int]$null = $versionParts[2]
            }
            catch {
                return $defaultPackageVersion
            }
            $packageVersion = GetIncrementedVersion $userInputPackageVersion $VersionBump
        }
        else {
            $packageVersion = $defaultPackageVersion
        }
        return $packageVersion
    }

    # Catalog mode: use Microsoft catalog for version
    . "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1"
    . ".script/package-automation/catalogAPI.ps1"
    # cspell:disable-next-line
    . "Tools/Create-Azure-Sentinel-Solution/common/get-ccp-details.ps1"

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

    $packageVersion = GetPackageVersion $defaultPackageVersion $offerId $offerDetails $packageVersionAttribute $userInputPackageVersion

    Remove-Item Function:\Write-Host

    return $packageVersion
}
finally {
    Set-Location $currentPath
}
