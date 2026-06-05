# cspell: words maintemplate.json

<#
.SYNOPSIS
Allows the ability to set a version for each data connector. This differs from the build functionality in the Tools scripts, because those scripts enforce that all data connectors use the same version. This prevents us from using semantic versioning properly.

.DESCRIPTION
Iterates over each data connector listed in the solution manifest (Data/Solution_*.json "Data Connectors" array).
For each connector:
  - Finds a version from the connector folder (version.txt or Version.json), or falls back to the solution manifest.
  - Adds a variable dataConnectorCCPVersion_<ContentId> in mainTemplate.json with that version.
  - Replaces every reference to dataConnectorCCPVersion that belongs to that connector with the new variable.
After all connectors are updated, removes the single dataConnectorCCPVersion variable. The script then overwrites mainTemplate.json inside Package/<BuildVersion>.zip with the updated file so the package folder and the zip always match.

Version fallback (when a connector has no version.txt or Version.json in its folder):
  - Use DataConnectorCCFVersion from the solution manifest (Solution_*.json), else
  - Use Version from the solution manifest.
  - If neither property exists in the manifest, the script throws.

.PARAMETER SolutionDataFolderPath
Specifies the path to the Data folder for the solution you are updating (e.g. Solutions/Tanium/Data or ./Solutions/Tanium/Data).

.PARAMETER BuildVersion
Required. The build version to update. It identifies the package zip (Package/<BuildVersion>.zip).
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SolutionDataFolderPath,
    [Parameter(Mandatory = $true)]
    [string]$BuildVersion
)

$ErrorActionPreference = 'Stop'

$scriptDirectory = $PSScriptRoot
if (-not $scriptDirectory) { $scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDirectory 'validation-functions.ps1')

<#
.SYNOPSIS
Maps the connector index (which is a 1-based index used by the build tool to create the maintemplate.json file) to the logical name of the connector in the solution. It also validates the count of connector variables in the maintemplate.json matches the manifest's count of connectors.
.OUTPUTS
PSCustomObject with List (hashtable) using the 1-based index as the key and the connector Id (string) as the value and Count (int).
#>
function Get-ConnectorIdByIndex {
    param(
        [object]$MainTemplate,
        [array]$ConnectorPaths
    )
    $connectorIdByIndex = @{}
    foreach ($key in $MainTemplate.variables.PSObject.Properties.Name) {
        if ($key -match '^_dataConnectorContentIdConnectorDefinition(\d+)$') {
            $index = [int]$Matches[1]
            $connectorIdByIndex[$index] = $MainTemplate.variables.$key
        }
    }
    $maxIndex = ($connectorIdByIndex.Keys | Measure-Object -Maximum).Maximum
    $connectorCount = $ConnectorPaths.Count
    if ($maxIndex -ne $connectorCount) {
        Write-Error "Connector count in manifest ($connectorCount) does not match variables in mainTemplate (max index $maxIndex)."
        exit 1
    }
    [PSCustomObject]@{ List = $connectorIdByIndex; Count = $connectorCount }
}

<#
.SYNOPSIS
Identifies the version to use for each connector from version.txt or Version.json in its folder, or uses the manifest version as a fallback.
.OUTPUTS
Hashtable using the connector id (string) as the key and the version as the value.
#>
function Get-ConnectorVersionMap {
    param(
        [array]$ConnectorPaths,
        [string]$DataConnectorsFolder,
        [hashtable]$ConnectorIdByIndex,
        [string]$ManifestFallbackVersion
    )
    $versionMap = @{}
    for ($index = 0; $index -lt $ConnectorPaths.Count; $index++) {
        $connectorPath = $ConnectorPaths[$index]
        $pathParts = $connectorPath -split '/'
        if ($pathParts.Count -lt 3) {
            Write-Error "Unexpected Data Connector path: $connectorPath"
            exit 1
        }
        $folderName = $pathParts[1]
        $connectorFolder = Join-Path $DataConnectorsFolder $folderName
        $contentId = $ConnectorIdByIndex[$index + 1]

        $version = $null
        $versionFile = Join-Path $connectorFolder 'version.txt'
        $versionJsonFile = Join-Path $connectorFolder 'Version.json'
        if (Test-Path $versionFile) {
            $version = (Get-Content -Raw $versionFile).Trim()
        } elseif (Test-Path $versionJsonFile) {
            try {
                $versionJson = Get-Content -Raw $versionJsonFile | ConvertFrom-Json
                $version = $versionJson.version
            } catch {
                Write-Error "Invalid Version.json in $connectorFolder : $_"
                exit 1
            }
        }
        if ([string]::IsNullOrWhiteSpace($version)) {
            $version = $ManifestFallbackVersion
        }
        $versionMap[$contentId] = $version
    }
    $versionMap
}

<#
.SYNOPSIS
Replaces dataConnectorCCPVersion references with per-connector variables, updates variables block, and writes mainTemplate.json.
#>
function Update-MainTemplateWithPerConnectorVersions {
    param(
        [string]$MainTemplateRaw,
        [hashtable]$ConnectorIdByIndex,
        [hashtable]$VersionMap,
        [int]$Count,
        [string]$MainTemplatePath
    )
    $literalPattern = "[variables('dataConnectorCCPVersion')]"
    $backRefPattern = "_dataConnectorContentId(?:ConnectorDefinition|Connections)(\d+)"
    $patternMatches = [regex]::Matches($MainTemplateRaw, [regex]::Escape($literalPattern))
    $replacements = @()
    foreach ($match in $patternMatches) {
        $before = $MainTemplateRaw.Substring(0, $match.Index)
        $backMatches = [regex]::Matches($before, $backRefPattern)
        $index = 1
        if ($backMatches.Count -gt 0) {
            $last = $backMatches[$backMatches.Count - 1]
            $index = [int]$last.Groups[1].Value
        }
        $contentId = $ConnectorIdByIndex[$index]
        $newText = "[variables('dataConnectorCCPVersion_$contentId')]"
        $replacements += [pscustomobject]@{ Index = $match.Index; Length = $match.Length; NewText = $newText }
    }
    $sortedReplacements = $replacements | Sort-Object -Property Index -Descending
    foreach ($replacement in $sortedReplacements) {
        $MainTemplateRaw = $MainTemplateRaw.Remove($replacement.Index, $replacement.Length).Insert($replacement.Index, $replacement.NewText)
    }

    $mainTemplate = $MainTemplateRaw | ConvertFrom-Json
    $templateVariables = $mainTemplate.variables
    $templateVariableNames = $templateVariables.PSObject.Properties.Name
    $insertAfter = $null
    foreach ($name in $templateVariableNames) {
        if ($name -eq 'dataConnectorCCPVersion') { $insertAfter = $name; break }
        if ($name -match '^dataConnectorTemplateNameConnections\d+$') { $insertAfter = $name }
    }
    if (-not $insertAfter) { $insertAfter = $templateVariableNames[-1] }

    $finalVariables = [ordered]@{}
    foreach ($name in $templateVariableNames) {
        $finalVariables[$name] = $templateVariables.$name
        if ($name -eq $insertAfter) {
            foreach ($index in (1..$Count)) {
                $contentId = $ConnectorIdByIndex[$index]
                $finalVariables["dataConnectorCCPVersion_$contentId"] = $VersionMap[$contentId]
            }
        }
    }
    $mainTemplate.variables = $finalVariables

    $json = $mainTemplate | ConvertTo-Json -Depth 100 -Compress:$false
    [System.IO.File]::WriteAllText($MainTemplatePath, $json, [System.Text.UTF8Encoding]::new($false))

    Write-Host "Per-connector versions set in mainTemplate.json:"
    foreach ($index in (1..$Count)) {
        $contentId = $ConnectorIdByIndex[$index]
        Write-Host "  dataConnectorCCPVersion_$contentId = $($VersionMap[$contentId])"
    }
}

<#
.SYNOPSIS
Overwrites mainTemplate.json inside the build zip so the package folder and zip match.
#>
function Update-ZipWithMainTemplate {
    param(
        [string]$ZipPath,
        [string]$MainTemplatePath
    )
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zipArchive = [System.IO.Compression.ZipFile]::Open($ZipPath, 'Update')
    try {
        $existingEntry = $zipArchive.GetEntry('mainTemplate.json')
        if ($existingEntry) { $existingEntry.Delete() }
        $newZipEntry = $zipArchive.CreateEntry('mainTemplate.json')
        $destinationStream = $newZipEntry.Open()
        try {
            $sourceStream = [System.IO.File]::OpenRead($MainTemplatePath)
            try {
                $sourceStream.CopyTo($destinationStream)
            } finally {
                $sourceStream.Close()
            }
        } finally {
            $destinationStream.Close()
        }
    } finally {
        $zipArchive.Dispose()
    }
    Write-Host "Updated mainTemplate.json in $ZipPath"
}

# ---------------------------------------------------------------------------
# Main: validate inputs, then apply per-connector versions and update zip
# ---------------------------------------------------------------------------
$solutionData = Resolve-SolutionDataPath -SolutionDataFolderPath $SolutionDataFolderPath
$zipPath = Assert-BuildZipExists -SolutionRoot $solutionData.SolutionRoot -BuildVersion $BuildVersion
$assertionResults = Assert-DataConnectorsManifestAndFolder -SolutionPath $solutionData.SolutionFilePath -SolutionRoot $solutionData.SolutionRoot

$mainTemplateRaw = Get-Content -Raw $assertionResults.MainTemplatePath
$mainTemplate = $mainTemplateRaw | ConvertFrom-Json

$connectors = Get-ConnectorIdByIndex -MainTemplate $mainTemplate -ConnectorPaths $assertionResults.ConnectorPaths
$versionMap = Get-ConnectorVersionMap -ConnectorPaths $assertionResults.ConnectorPaths -DataConnectorsFolder $assertionResults.DataConnectorsFolder -ConnectorIdByIndex $connectors.List -ManifestFallbackVersion $assertionResults.ManifestFallbackVersion

Update-MainTemplateWithPerConnectorVersions -MainTemplateRaw $mainTemplateRaw -ConnectorIdByIndex $connectors.List -VersionMap $versionMap -Count $connectors.Count -MainTemplatePath $assertionResults.MainTemplatePath
Update-ZipWithMainTemplate -ZipPath $zipPath -MainTemplatePath $assertionResults.MainTemplatePath
