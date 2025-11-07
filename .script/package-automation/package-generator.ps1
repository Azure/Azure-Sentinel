param (
    $solutionName, 
    $pullRequestNumber, 
    $runId, 
    $instrumentationKey, 
    $defaultPackageVersion, 
    $solutionOfferId, 
    $inputBaseFolderPath, 
    $isNewSolution = $false,
    $isPRMerged = $false
)

. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1
. ./.script/package-automation/catalogAPI.ps1

function ErrorOutput {
    Write-Host "Package creation process failed!"
    Write-Output "isCreatePackage=$false" >> $env:GITHUB_OUTPUT
    Write-Output "packageCreationPath=''" >> $env:GITHUB_OUTPUT
    Write-Output "blobName=''" >> $env:GITHUB_OUTPUT
    exit 1
}

    if ($null -eq $solutionName -or $solutionName -eq '') { 
        Write-Host "::error::Solution name not found" 
        ErrorOutput
    }

    function Remove-ParameterFilesFromDataFolder {
        [CmdletBinding()]
        Param(
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array]$DatafolderFiles
        )
        $Result = @()
        foreach ($Item in $DatafolderFiles) {
            if ($Item -notmatch 'parameters\.json' -and
                $Item -notmatch 'parameter\.json' -and
                $Item -notmatch 'system_generated_metadata\.json' -and
                $Item -notmatch 'testParameters\.json') {
                $Result += $Item
            }
        }
        return $Result
    }

    function Get-ValidFileNames {
        [CmdletBinding()]
        Param(
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array]$filesList
        )
        $Result = @()
        foreach ($Item in $filesList) {
            # Exclude files that are not valid data connector JSONs
            if ($Item -match '\.json$' -and
                $Item -notmatch 'host\.json$' -and
                $Item -notmatch 'proxies\.json$' -and
                $Item -notmatch 'azureDeploy' -and
                $Item -notmatch 'function\.json$' -and
                $Item -notmatch '\.txt$' -and
                $Item -notmatch '\.zip$' -and
                $Item -notmatch '\.py$') {
                $Result += $Item
            }
        }
        return $Result
    }

    function Get-ValidFileNamesByExtension {
    [CmdletBinding()]
        Param(
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array]$filesList,
            [Parameter(Mandatory = $true, Position = 1)]
            [string]$extension # e.g. '.yaml' or '.json'
        )
        $Result = @()
        foreach ($Item in $filesList) {
            if ($Item -match ([regex]::Escape($extension) + '$')) {
                $Result += $Item
            }
        }
        return $Result
    }

    function Get-PlaybooksJsonFileNames {
        [CmdletBinding()]
        Param(
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array]$PlaybookFiles
        )
        $Result = $PlaybookFiles | Where-Object {
            $_ -match '\.json$' -and
            $_ -notlike '*swagger*' -and
            $_ -notlike '*function.json' -and
            $_ -notlike '*host.json'
        }
        return $Result
    }

    function Get-OnlyFileNames {
        [CmdletBinding()]
        Param(
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array]$FilePaths,
            [Parameter(Mandatory = $true, Position = 1)]
            [System.String]$FolderNameWithSlash
        )
        $Result = @()
        foreach ($Item in $FilePaths) {
            $Index = $Item.IndexOf($FolderNameWithSlash)
            #$Length = $FolderNameWithSlash.Length
            if ($Index -gt 0) {
                #$Result += $Item.Substring($Index + $Length)
                $Result += $Item.Substring($Index)
            } else {
                $Result += $Item
            }
        }
        return $Result
    }

    function Remove-LinkedTemplates {
        [CmdletBinding()]
        Param(
            [Parameter(Mandatory = $true)]
            [array]$PlaybookFiles,
            [string]$BaseFolderPath
        )
        $filtered = @()
        foreach ($item in $PlaybookFiles) {
            $filePath = $BaseFolderPath + $item
            if (Test-Path $filePath) {
                $fileContentObj = Get-Content "$filePath" | ConvertFrom-Json
                if ($null -ne $fileContentObj) {
                    $hasLinked = $false
                    foreach ($resource in $fileContentObj.resources) {
                        if ($resource.type -eq "Microsoft.Resources/deployments") {
                            $hasLinked = $true
                            break
                        }
                    }
                    if (-not $hasLinked) { $filtered += $item }
                } else {
                    $filtered += $item
                }
            } else {
                $filtered += $item
            }
        }
        return $filtered
    }

    function Get-WorkbooksJsonFileNames { 
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)] 
            [System.Array] $workbookFiles
        )
        $newWorkbookFilesWithoutExcludedFiles = @()
        $newWorkbookFilesWithoutExcludedFiles = $workbookFiles -match ([regex]::Escape(".json"))
        return $newWorkbookFilesWithoutExcludedFiles;
    }

function Normalize-FilePathSpaces {
    param(
        [Parameter(Mandatory = $true)]
        [string]$filePath
    )
    return $filePath -replace '%20', ' '
}

function Normalize-SummaryRulesPaths {
    param(
        [Parameter(Mandatory = $true)]
        [array]$SummaryRulesArray
    )
    $normalized = @()
    foreach ($item in $SummaryRulesArray) {
        $item = Normalize-FilePathSpaces $item
        if ($item -like "Summary Rules/*") {
            $normalized += $item -replace "^Summary Rules/", "SummaryRules/"
        } elseif ($item -like "SummaryRules/*") {
            $normalized += $item
        } else {
            $normalized += $item
        }
    }
    return $normalized
}

try 
{
    $solutionFolderPath = 'Solutions/' + $solutionName + "/"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "::error::Failed to fetch origin/master"
        Write-Output "isCreatePackage=$false" >> $env:GITHUB_OUTPUT
        exit 1
    }

    $base = git merge-base HEAD origin/master
    if ($LASTEXITCODE -ne 0) {
        Write-Host "::error::Failed to get merge-base with origin/master"
        Write-Output "isCreatePackage=$false" >> $env:GITHUB_OUTPUT
        exit 1
    }

    $head = git rev-parse HEAD
    if ($LASTEXITCODE -ne 0) {
        Write-Host "::error::Failed to get HEAD commit"
        Write-Output "isCreatePackage=$false" >> $env:GITHUB_OUTPUT
        exit 1
    }

    if ($base -eq $head -and $isPRMerged -eq $false) {
        Write-Host "PR branch is up to date with master. Skipping package generation."
        Write-Output "isCreatePackage=$false" >> $env:GITHUB_OUTPUT
        exit 0
    }

    if ($isPRMerged) {
        Write-Host "PR branch is merged with master."
        $changedFiles = $(git diff --name-only HEAD^ HEAD)
        if ([string]::IsNullOrWhiteSpace($changedFiles)) {
            Write-Host "No files changed in the last commit. Skipping package generation." -ForegroundColor Yellow
            Write-Output "isCreatePackage=$false" >> $env:GITHUB_OUTPUT
            exit 0
        }
    }

    $filesList = git ls-files | Where-Object { $_ -like "$solutionFolderPath*" }

    #SOLUTION FOLDERS
    $solutionParsersFolder = $solutionFolderPath + 'Parsers/'
    $solutionDataConnectorsFolder = $solutionFolderPath + 'DataConnectors/'
    $solutionDataConnectorsWithSpaceFolder = $solutionFolderPath + 'Data Connectors/'
    $solutionWorkbooksFolder = $solutionFolderPath + 'Workbooks/'
    $solutionPlaybooksFolder = $solutionFolderPath + 'Playbooks/'
    $solutionHuntingQueriesFolder = $solutionFolderPath + 'Hunting Queries/'
    $solutionAnalyticRulesFolder = $solutionFolderPath + 'Analytic Rules/'
    $solutionWatchlistsFolder = $solutionFolderPath + 'Watchlists/'
    $solutionWatchlistInWorkbookFolder = $solutionFolderPath + 'Workbooks/Watchlist/'
    $solutionSummaryRulesFolder = $solutionFolderPath + 'SummaryRules/'
    $solutionSummaryRulesWithSpaceFolder = $solutionFolderPath + 'Summary Rules/'

    # Filter result variables by $dataFileContentObject arrays if present, else set to empty
    $parserFolderResult = $filesList -match ([regex]::Escape($solutionParsersFolder)) | ForEach-Object { $_.replace($solutionParsersFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataFileContentObject.Parsers -and $dataFileContentObject.Parsers.Count -gt 0) {
        $parserFolderResult = $parserFolderResult | Where-Object { $dataFileContentObject.Parsers -contains $_ }
    } else {
        $parserFolderResult = @()
    }

    $dataConnectorsFolderResult = $filesList -match ([regex]::Escape($solutionDataConnectorsFolder)) | ForEach-Object { $_.replace($solutionDataConnectorsFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataFileContentObject.DataConnectors -and $dataFileContentObject.DataConnectors.Count -gt 0) {
        $dataConnectorsFolderResult = $dataConnectorsFolderResult | Where-Object { $dataFileContentObject.DataConnectors -contains $_ }
    } else {
        $dataConnectorsFolderResult = @()
    }

    $dataConnectorsWithSpaceFolderResult = $filesList -match ([regex]::Escape($solutionDataConnectorsWithSpaceFolder)) | ForEach-Object { $_.replace($solutionDataConnectorsWithSpaceFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataFileContentObject.'Data Connectors' -and $dataFileContentObject.'Data Connectors'.Count -gt 0 -and $null -ne $dataConnectorsWithSpaceFolderResult -and $dataConnectorsWithSpaceFolderResult.Count -gt 0) {
        $dataConnectorsWithSpaceFolderResult = $dataConnectorsWithSpaceFolderResult | Where-Object { $dataFileContentObject.'Data Connectors' -contains $_ }
    } else {
        $dataConnectorsWithSpaceFolderResult = @()
    }

    $playbooksFolderResult = $filesList -match ([regex]::Escape($solutionPlaybooksFolder))
    if ($null -ne $dataFileContentObject.Playbooks -and $dataFileContentObject.Playbooks.Count -gt 0) {
        $playbooksFolderResult = $playbooksFolderResult | Where-Object { $dataFileContentObject.Playbooks -contains $_ }
    } else {
        $playbooksFolderResult = @()
    }

    $workbooksFolderResult = $filesList -match ([regex]::Escape($solutionWorkbooksFolder)) | ForEach-Object { $_.replace($solutionWorkbooksFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataFileContentObject.Workbooks -and $dataFileContentObject.Workbooks.Count -gt 0) {
        $workbooksFolderResult = $workbooksFolderResult | Where-Object { $dataFileContentObject.Workbooks -contains $_ }
    } else {
        $workbooksFolderResult = @()
    }

    $huntingQueriesFolderResult = $filesList -match ([regex]::Escape($solutionHuntingQueriesFolder)) | ForEach-Object { $_.replace( $solutionHuntingQueriesFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataFileContentObject.'Hunting Queries' -and $dataFileContentObject.'Hunting Queries'.Count -gt 0) {
        $huntingQueriesFolderResult = $huntingQueriesFolderResult | Where-Object { $dataFileContentObject.'Hunting Queries' -contains $_ }
    } else {
        $huntingQueriesFolderResult = @()
    }

    $analyticRulesFolderResult = $filesList -match ([regex]::Escape($solutionAnalyticRulesFolder)) | ForEach-Object { $_.replace($solutionAnalyticRulesFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataFileContentObject.'Analytic Rules' -and $dataFileContentObject.'Analytic Rules'.Count -gt 0) {
        $analyticRulesFolderResult = $analyticRulesFolderResult | Where-Object { $dataFileContentObject.'Analytic Rules' -contains $_ }
    } else {
        $analyticRulesFolderResult = @()
    }

    $watchlistsFolderResult = $filesList -match ([regex]::Escape($solutionWatchlistsFolder)) | ForEach-Object { $_.replace($solutionWatchlistsFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataFileContentObject.Watchlists -and $dataFileContentObject.Watchlists.Count -gt 0) {
        $watchlistsFolderResult = $watchlistsFolderResult | Where-Object { $dataFileContentObject.Watchlists -contains $_ }
    } else {
        $watchlistsFolderResult = @()
    }

    $watchlistInWorkbooksFolderResult = $filesList -match ([regex]::Escape($solutionWatchlistInWorkbookFolder)) | ForEach-Object { $_.replace($solutionWatchlistInWorkbookFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataFileContentObject.'WatchlistInWorkbook' -and $dataFileContentObject.'WatchlistInWorkbook'.Count -gt 0) {
        $watchlistInWorkbooksFolderResult = $watchlistInWorkbooksFolderResult | Where-Object { $dataFileContentObject.'WatchlistInWorkbook' -contains $_ }
    } else {
        $watchlistInWorkbooksFolderResult = @()
    }

    $dataFolderFiles = $filesList | Where-Object { $_ -like "*/Data/*" } | Where-Object { $_ -notlike '*system_generated_metadata.json' } | Where-Object { $_ -notlike '*testParameters.json' }
    if ($dataFolderFiles.Count -gt 0) {
        $selectFirstdataFolderFile = $dataFolderFiles | Select-Object -first 1
        $filteredString = $selectFirstdataFolderFile.Replace("$solutionFolderPath", '', 'OrdinalIgnoreCase')
        $nextSlashIndex = $filteredString.IndexOf('/')
        $dataFolderActualName = $filteredString.Substring(0, $nextSlashIndex)
        $replaceInitialPath = "$solutionFolderPath" + "$dataFolderActualName/"
        $dataFolderFiles = $dataFolderFiles.Replace("$replaceInitialPath", '', 'OrdinalIgnoreCase')
    }
    else {
        Write-Host "Data Folder not present!"
        ErrorOutput
    }

    $dataFolderFile = Remove-ParameterFilesFromDataFolder($dataFolderFiles)
    $solutionDataFolder = $solutionFolderPath + "$dataFolderActualName/"
    Write-Host "solutionDataFolder is $solutionDataFolder"

    $baseFolderPath = $inputBaseFolderPath #'/home/runner/work/packagingrepo/packagingrepo/'
    $dataFilePath = $baseFolderPath + $solutionDataFolder + $dataFolderFile
    $dataFileLink = "https://github.com/Azure/Azure-Sentinel/master/Solutions/$solutionName/$dataFolderActualName/$dataFolderFile"

    Write-Output "dataFileLink=$dataFileLink" >> $env:GITHUB_OUTPUT
    Write-Host "Data File Path $dataFilePath"

    # Use Test-Path before file operations
    if (-not (Test-Path $dataFilePath)) {
        Write-Error "Data file not found: $dataFilePath"
        exit 1
    }
    $dataFileContentObject = Get-Content "$dataFilePath" | ConvertFrom-Json
    if ($null -eq $dataFileContentObject) {
        Write-Error "Data file content is invalid."
        exit 1
    }
    $dataFileContentObject = $null -eq $dataFileContentObject[0] ? $dataFileContentObject[1] : $dataFileContentObject[0]

    $dataFolderPath = $baseFolderPath + $solutionDataFolder
    $jsonDataFileInput = $dataFileContentObject | ConvertTo-Json
    # CREATE SYSTEM GENERATED DATA FILE
    $dataFilePath = $baseFolderPath + $solutionDataFolder + 'system_generated_metadata.json'

    Set-Content -Path "$dataFilePath" -Value $jsonDataFileInput
    Write-Output "dataFolderPath=$dataFolderPath" >> $env:GITHUB_OUTPUT
    Write-Host "dataFolderPath is $dataFolderPath"

    $hasCreatePackageAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match ([regex]::Escape("createPackage")))
    $isCreatePackageSetToTrue = $dataFileContentObject.createPackage
    if ($hasCreatePackageAttribute -eq $true -and $isCreatePackageSetToTrue -eq $false) {
        Write-Host "::warning::Skipping Package Creation for Solution '$solutionName', as Data File has attribute 'createPackage' set to False!"
        $setIsCreatePackage = $false
        Write-Output "isCreatePackage=$setIsCreatePackage" >> $env:GITHUB_OUTPUT
        ErrorOutput
    }

    #Required Fields
    $nameAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Name")
    $authorAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Author")
    $descriptionAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Description")

    #Optional Fields
    $TemplateSpecAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "TemplateSpec")
    #$Is1PconnectorAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Is1Pconnector")
    $logoAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Logo")
    $basePathAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "BasePath")
    $packageVersionAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Version")

    $hasAllRequiredDataFileAttributes = ($nameAttribute -and $authorAttribute -and $descriptionAttribute)

    Write-Host "hasAllRequiredDataFileAttributes $hasAllRequiredDataFileAttributes"
    if (!$hasAllRequiredDataFileAttributes) {
        Write-Host "::error::Required properties missing in data input file. Please make sure that key values pairs for attributes: Name, Author and Description are present in data file." 
        exit 0 
    }

    # =============START: DETAILS TO IDENTIFY VERSION FROM CATALOG API=========
    $offerId = "$solutionOfferId"
    $offerDetails = GetCatalogDetails $offerId

    $userInputPackageVersion = ''
    if ($packageVersionAttribute) {
        $userInputPackageVersion = $dataFileContentObject.version
    }
    $packageVersion = GetPackageVersion $defaultPackageVersion $offerId $offerDetails $packageVersionAttribute $userInputPackageVersion

    Write-Host "Package version identified is $packageVersion"
    # =============END: DETAILS TO IDENTIFY VERSION FROM CATALOG API=========
    if (!$packageVersionAttribute) {
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'Version' -Value "$packageVersion"
    }
    else {
        if ($dataFileContentObject.Version -ne "$packageVersion") {
            $dataFileContentObject.PSObject.Properties.Remove('Version')
            $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'Version' -Value "$packageVersion"
            Write-Host "Package version updated to $packageVersion"
        }
    }
    
    if (!$TemplateSpecAttribute) {
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'TemplateSpec' -Value $true 
    }

    # if (!$is1PconnectorAttribute) {
    #     $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'Is1Pconnector' -Value $false 
    # }

    if (!$logoAttribute) {
        $logoAttributeValue = '<img src=\"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/Azure_Sentinel.svg\" width=\"75px\" height=\"75px\">'
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'Logo' -Value "$logoAttributeValue"
    }

    if (!$basePathAttribute) {
        $basePathAttributeValue = $baseFolderPath + $solutionFolderPath
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'BasePath' -Value "$basePathAttributeValue"
    }

    # ATTRIBUTES FROM DATA FILE IF CONSOLIDATED DATA FILE AND SOLUTIONMETADATA FILE
    $publisherIdAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "publisherId")
    $offerIdAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "offerId")
    $firstPublishDateAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "firstPublishDate")
    $providersAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "providers")
    $categoriesAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "categories")
    $supportAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "support")

    #CHECK IF ALL PROPERTIES ARE MISSING IN DATA FILE
    $hasAllSolutionMetadataAttributeInDataFile = ($publisherIdAttribute -or $offerIdAttribute -or $firstPublishDateAttribute -or
        $providersAttribute -or $categoriesAttribute)
    $isContentInSolutionMetadataFile = $false

    if (!$hasAllSolutionMetadataAttributeInDataFile) {
        #GET DATA FROM SOLUTIONMETADATA.JSON FILE
        try {
            $solutionMetadataFilePresent = $filesList -match ([regex]::Escape("SolutionMetadata.json"))
        }
        catch {
            Write-Host "SolutionMetadata file not present so check if any file is present that contains SolutionMetadata file in the Solutions respective folder!"
            $solutionMetadataFilePresent = filesList | Where-Object { $_ -like "Solutions/*SolutionMetadata.json" }
        }
        $solutionMetadataFilePresent = $solutionMetadataFilePresent.replace($solutionFolderPath, "")
        $solutionMetadataFilePath = $baseFolderPath + $solutionFolderPath + $solutionMetadataFilePresent
        $solutionMetadataFileContentObject = Get-Content $solutionMetadataFilePath | ConvertFrom-Json
        if ($null -eq $solutionMetadataFileContentObject) { 
            Write-Host "::error::SolutionMetadata.json file not found." 
            exit 0
        }

        $isContentInSolutionMetadataFile = $true
        $publisherIdAttribute = [bool]($solutionMetadataFileContentObject.PSobject.Properties.name -match "publisherId")
        $offerIdAttribute = [bool]($solutionMetadataFileContentObject.PSobject.Properties.name -match "offerId")
        $firstPublishDateAttribute = [bool]($solutionMetadataFileContentObject.PSobject.Properties.name -match "firstPublishDate")
        $providersAttribute = [bool]($solutionMetadataFileContentObject.PSobject.Properties.name -match "providers")
        $categoriesAttribute = [bool]($solutionMetadataFileContentObject.PSobject.Properties.name -match "categories")
        $supportAttributeSolutionMetadata = [bool]($solutionMetadataFileContentObject.PSobject.Properties.name -match "support")
        $hasAllSolutionMetadataAttributeInDataFile = ($publisherIdAttribute -and $offerIdAttribute -and $firstPublishDateAttribute -and
            $providersAttribute -and $categoriesAttribute)
        if (!$hasAllSolutionMetadataAttributeInDataFile) {
            Write-Host "::error::Required properties are missing. You can either create a new file with name 'SolutionMetadata.json' inside of Solution '$solutionName' folder and add all required attributes: publisherId, offerId, providers and categories  OR add all required properties in Data input file" 
            exit 0
        }
    }

    if ($isContentInSolutionMetadataFile) {
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'publisherId' -Value $solutionMetadataFileContentObject.publisherId
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'offerId' -Value $solutionMetadataFileContentObject.offerId
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'providers' -Value $solutionMetadataFileContentObject.providers
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'categories' -Value $solutionMetadataFileContentObject.categories
        if ($solutionMetadataFileContentObject.firstPublishDate -and $solutionMetadataFileContentObject.firstPublishDate -ne "") {
            $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'firstPublishDate' -Value $solutionMetadataFileContentObject.firstPublishDate
        }
        
        if ($solutionMetadataFileContentObject.lastPublishDate -and $solutionMetadataFileContentObject.lastPublishDate -ne "") {
            $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'lastPublishDate' -Value $solutionMetadataFileContentObject.lastPublishDate
        }
    }

    if (!$supportAttributeSolutionMetadata -and !$supportAttribute) {
        $supportAttributeValue = "{
            `n    `"name`" : `"Microsoft Corporation`",
            `n    `"email`" : `"support@microsoft.com`",
            `n    `"tier`" : `"Microsoft`",
            `n    `"link`" : `"https://support.microsoft.com`"
            `n}"
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'support' -Value $supportAttributeValue
    } 
    elseif ($supportAttributeSolutionMetadata) {
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'support' -Value $solutionMetadataFileContentObject.support
    }

    $parserFolderResult = $filesList -match ([regex]::Escape($solutionParsersFolder)) | ForEach-Object { $_.replace($solutionParsersFolder, '', 'OrdinalIgnoreCase') }
    $dataConnectorsFolderResult = $filesList -match ([regex]::Escape($solutionDataConnectorsFolder)) | ForEach-Object { $_.replace( $solutionDataConnectorsFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataConnectorsFolderResult -and $null -ne $dataFileContentObject.'DataConnectors' -and $dataFileContentObject.'DataConnectors'.Count -gt 0) {
        $dataConnectorsFolderResult = Get-ValidFileNames($dataConnectorsFolderResult)
    }

    $dataConnectorsWithSpaceFolderResult = $filesList -match ([regex]::Escape($solutionDataConnectorsWithSpaceFolder)) | ForEach-Object { $_.replace($solutionDataConnectorsWithSpaceFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataConnectorsWithSpaceFolderResult -and $null -ne $dataFileContentObject.'Data Connectors' -and $dataFileContentObject.'Data Connectors'.Count -gt 0) {
        $dataConnectorsWithSpaceFolderResult = Get-ValidFileNames($dataConnectorsWithSpaceFolderResult)
    }

    $playbooksFolderResult = $filesList -match ([regex]::Escape($solutionPlaybooksFolder))
    # if ($null -ne $playbooksFolderResult -and $playbooksFolderResult.Count -gt 0) {
    #     $playbooksFolderResult = Get-PlaybooksJsonFileNames($playbooksFolderResult)
    # }

    if ($null -ne $dataFileContentObject.Playbooks -and $dataFileContentObject.Playbooks.Count -gt 0) {
        $playbooksFolderResult = $playbooksFolderResult | Where-Object { $dataFileContentObject.Playbooks -like "*$_*"  }
    } else {
        $playbooksFolderResult = @()
    }

    $workbooksFolderResult = $filesList -match ([regex]::Escape($solutionWorkbooksFolder)) | ForEach-Object { $_.replace($solutionWorkbooksFolder, '', 'OrdinalIgnoreCase') }

    # Filter workbooksFolderResult by dataFileContentObject.Workbooks if present
    if ($null -ne $dataFileContentObject.Workbooks -and $dataFileContentObject.Workbooks.Count -gt 0) {
        $workbooksFolderResult = $workbooksFolderResult | Where-Object { $dataFileContentObject.Workbooks -like "*$_*" }
    } else {
        $workbooksFolderResult = @()
    }

    $huntingQueriesFolderResult = $filesList -match ([regex]::Escape($solutionHuntingQueriesFolder)) | ForEach-Object { $_.replace( $solutionHuntingQueriesFolder, '', 'OrdinalIgnoreCase') }

    # Filter analyticRulesFolderResult by dataFileContentObject.'Analytic Rules' if present
    if ($null -ne $dataFileContentObject.'Hunting Queries' -and $dataFileContentObject.'Hunting Queries'.Count -gt 0) {
        $huntingQueriesFolderResult = $huntingQueriesFolderResult | Where-Object { $dataFileContentObject.'Hunting Queries' -like "*$_*"  }
    } else {
        $huntingQueriesFolderResult = @()
    }

    $analyticRulesFolderResult = $filesList -match ([regex]::Escape($solutionAnalyticRulesFolder)) | ForEach-Object { $_.replace($solutionAnalyticRulesFolder, '', 'OrdinalIgnoreCase') }

    # Filter analyticRulesFolderResult by dataFileContentObject.'Analytic Rules' if present
    if ($null -ne $dataFileContentObject.'Analytic Rules' -and $dataFileContentObject.'Analytic Rules'.Count -gt 0) {
        $analyticRulesFolderResult = $analyticRulesFolderResult | Where-Object { $dataFileContentObject.'Analytic Rules' -like "*$_*"  }
    } else {
        $analyticRulesFolderResult = @()
    }

    $watchlistsFolderResult = $filesList -match ([regex]::Escape($solutionWatchlistsFolder)) | ForEach-Object { $_.replace($solutionWatchlistsFolder, '', 'OrdinalIgnoreCase') }
    $watchlistInWorkbooksFolderResult = $filesList -match ([regex]::Escape($solutionWatchlistInWorkbookFolder)) | ForEach-Object { $_.replace($solutionWatchlistInWorkbookFolder, '', 'OrdinalIgnoreCase') }

    if ($null -ne $dataFileContentObject.Watchlists -and $dataFileContentObject.Watchlists.Count -gt 0) {
        $watchlistsFolderResult = $watchlistsFolderResult | Where-Object { $dataFileContentObject.Watchlists -like "*$_*"  }
    } else {
        $watchlistsFolderResult = @()
    }

    if ($null -ne $dataFileContentObject.Watchlists -and $dataFileContentObject.Watchlists.Count -gt 0) {
        $watchlistInWorkbooksFolderResult = $watchlistInWorkbooksFolderResult | Where-Object { $dataFileContentObject.Watchlists -like "*$_*" }
    } else {
        $watchlistInWorkbooksFolderResult = @()
    }

    if ($null -ne $watchlistsFolderResult -and $watchlistsFolderResult.Count -gt 0) {
        $watchlistsFolderResult = Get-ValidFileNamesByExtension $watchlistsFolderResult ".json"
    }

    if ($null -ne $watchlistInWorkbooksFolderResult -and $watchlistInWorkbooksFolderResult.Count -gt 0) {
        $watchlistInWorkbooksFolderResult = Get-ValidFileNamesByExtension $watchlistInWorkbooksFolderResult ".json"
    }

    #COUNT NUMBER OF FILES IN EACH FOLDER
    $parserFolderResultLength = $parserFolderResult.Count
    $dataConnectorsFolderResultLength = $dataConnectorsFolderResult.Count
    $dataConnectorsWithSpaceFolderResultLength = $dataConnectorsWithSpaceFolderResult.Count
    $playbooksFolderResultLength = $playbooksFolderResult.Count
    $workbooksFolderResultLength = $workbooksFolderResult.Count
    $huntingQueriesFolderResultLength = $huntingQueriesFolderResult.Count
    $analyticRulesFolderResultLength = $analyticRulesFolderResult.Count

    $watchlistsFolderResultLength = $watchlistsFolderResult.Count
    $watchlistInWorkbookFolderLength = $watchlistInWorkbooksFolderResult.Count

    Write-Host "ParserFolderResultLength: $parserFolderResultLength"
    Write-Host "dataConnectorsFolderResultLength: $dataConnectorsFolderResultLength"
    Write-Host "dataConnectorsWithSpaceFolderResultLength: $dataConnectorsWithSpaceFolderResultLength"
    Write-Host "playbooksFolderResultLength: $playbooksFolderResultLength"
    Write-Host "workbooksFolderResultLength: $workbooksFolderResultLength"
    Write-Host "huntingQueriesFolderResultLength: $huntingQueriesFolderResultLength"
    Write-Host "analyticRulesFolderResultLength: $analyticRulesFolderResultLength"
    Write-Host "watchlistsFolderResultLength: $watchlistsFolderResultLength"
    Write-Host "watchlistInWorkbookFolderLength: $watchlistInWorkbookFolderLength"

    $dataConnectorFolderName = 'Data Connectors'
    if ($dataConnectorsFolderResultLength -gt 0 -and $dataFileContentObject.'DataConnectors'.Count -gt 0) {
        $dataConnectorFolderName = 'DataConnectors'
        $newDataConnectorFiles = @()
        $newDataConnectorFiles = Get-OnlyFileNames -filePaths $dataConnectorsFolderResult -folderNameWithSlash "DataConnectors/"
        $dataConnectorFilesResultArray = (Get-ValidFileNamesByExtension $newDataConnectorFiles ".json") | ConvertTo-Json -AsArray
        $dataConnectoryWithoutSpaceArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("DataConnectors")))
        if (!$dataConnectoryWithoutSpaceArrayAttributeExist) {
            $dataFileContentObject.PSObject.Properties.Remove('Data Connectors')
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'Data Connectors' -Value $dataConnectorFilesResultArray -PassThru
            }
        }
        else {
            $dataFileContentObject.PSObject.Properties.Remove('DataConnectors')
            $datafilecontentobject | foreach-object {
                $_ | add-member -membertype noteproperty -name 'DataConnectors' -value $dataConnectorFilesResultArray -passthru
            }
        }
    }
    elseif ($dataConnectorsWithSpaceFolderResultLength -gt 0 -and $dataFileContentObject.'Data Connectors'.Count -gt 0) {
        $newDataConnectorFiles = @()
        $dataConnectorDataPaths = $dataFileContentObject."Data Connectors"
        Write-Host "dataConnectorDataPaths is $dataConnectorDataPaths"
        if ($null -eq $dataConnectorDataPaths -or $dataConnectorDataPaths -eq '') {
            $newDataConnectorFiles = Get-OnlyFileNames -filePaths $dataConnectorsWithSpaceFolderResult -folderNameWithSlash "Data Connectors/"
        }
        else {
            $newDataConnectorFiles = Get-OnlyFileNames -filePaths $dataConnectorDataPaths -folderNameWithSlash "Data Connectors/"
        }

        $dataConnectorFilesWithSpaceFolderResultArray = (Get-ValidFileNamesByExtension $newDataConnectorFiles ".json") | ConvertTo-Json -AsArray
        $dataConnectoryArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("Data Connectors")))

        if (!$dataConnectoryArrayAttributeExist) {
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'Data Connectors' -Value $dataConnectorFilesWithSpaceFolderResultArray -PassThru
            }
        }
        else {
            $dataFileContentObject.PSObject.Properties.Remove('Data Connectors')
            $datafilecontentobject | foreach-object {
                $_ | add-member -membertype noteproperty -name 'Data Connectors' -value $dataConnectorFilesWithSpaceFolderResultArray -passthru
            }
        }
    }

    if ($dataConnectoryArrayAttributeExist) {
        if ($dataFileContentObject.DataConnectors.Count -gt 0) {
            $dataFileDataConnectorList = (Get-ValidFileNamesByExtension $dataFileContentObject.DataConnectors ".json") | ConvertTo-Json -AsArray
            $dataFileContentObject.PSObject.Properties.Remove('Data Connectors')
            $datafilecontentobject | foreach-object {
                $_ | add-member -membertype noteproperty -name 'Data Connectors' -value $dataFileDataConnectorList -passthru
            }
        }
    }

    if ($parserFolderResultLength -gt 0) {
        $parserFolderResultArray = $parserFolderResult | ConvertTo-Json -AsArray
        $parsersArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("Parsers")))
        if (!$parsersArrayAttributeExist) {
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'Parsers' -Value $parserFolderResultArray -PassThru
            }
        } 
        else {
            if ($dataFileContentObject.Parsers.Count -gt 0) {
                $dataFileparsersList = (Get-ValidFileNamesByExtension $dataFileContentObject.parsers ".yaml") | ConvertTo-Json -AsArray
                $dataFileContentObject.PSObject.Properties.Remove('Parsers')
                $datafilecontentobject | foreach-object {
                    $_ | add-member -membertype noteproperty -name 'Parsers' -value $dataFileparsersList -passthru
                }
            } 
            else { 
                $dataFileContentObject.PSObject.Properties.Remove('Parsers') 
            }
        }
    }

    # ===============Start of new: Playbooks Code ============
    if ($playbooksFolderResultLength -gt 0) {

        #===============START : PLAYBOOKS FUNCTION APP FILES=============
        # check if functionapp folder files are present in solution for playbooks
        $playbooksFunctionAppFiles = @()
        if ($playbooksFolderHasFunctionAppsInPlaybooksFolder -and $playbooksFolderHasFunctionAppsInPlaybooksFolder.Count -gt 0) {
            $playbooksFunctionAppFiles += Get-PlaybooksJsonFileNames($playbooksFolderHasFunctionAppsInPlaybooksFolder)
        }
    
        $playbooksFolderHasFunctionAppsInSolutionsFolder = $filesList -like "Solutions/$solutionName/*FunctionApp*"
    
        if ($playbooksFolderHasFunctionAppsInSolutionsFolder -ne $false -and $playbooksFolderHasFunctionAppsInSolutionsFolder.Count -gt 0) {
            # REMOVE DATA CONNECTOR FOLDERS IF ANY
            $filteredPlaybookFunctionApps = @()
            foreach($item in $playbooksFolderHasFunctionAppsInSolutionsFolder)
            {
                if ($item -like '*Data Connectors*' -or $item -like '*DataConnectors*')
                { }
                else {
                    $filteredPlaybookFunctionApps += "$item"
                }
            }
    
            if ($filteredPlaybookFunctionApps -and $filteredPlaybookFunctionApps.Count -gt 0)
            {
                $playbooksFolderHasFunctionAppsInSolutionsFolder = @()
                $playbooksFolderHasFunctionAppsInSolutionsFolder += $filteredPlaybookFunctionApps
                $playbooksFunctionAppFilesInSolutionsFolder = Get-PlaybooksJsonFileNames($playbooksFolderHasFunctionAppsInSolutionsFolder)
                if ($playbooksFunctionAppFilesInSolutionsFolder -and $playbooksFunctionAppFilesInSolutionsFolder.Count -gt 0)
                {
                    $filteredPlaybooksFunctionAppFiles = $playbooksFunctionAppFilesInSolutionsFolder | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
                    if ($filteredPlaybooksFunctionAppFiles -and $filteredPlaybooksFunctionAppFiles.Count -gt 0)
                    {
                        foreach($item in $filteredPlaybooksFunctionAppFiles)
                        {
                            if ($playbooksFunctionAppFiles -notcontains $item)
                            {
                                $playbooksFunctionAppFiles += $item
                            }
                        }
                    }
                }
            }
        }
    
        #===============END : PLAYBOOKS FUNCTION APP FILES=============
    
        # check if folder with Connector Name present inside of Playbooks folder eg: AzureFirewall
        $customConnectorPath = "$solutionPlaybooksFolder" + "Connector"
        $playbooksFolderHasConnectorNames = $playbooksFolderResult -match "$customConnectorPath"
        $playbooksFolderHasConnectorList = @()
    
        if ($playbooksFolderHasConnectorNames -ne $false -and $playbooksFolderHasConnectorNames.Count -gt 0) {
            # it has custom playbooks 
            $playbooksFolderHasConnectorList = $playbooksFolderHasConnectorNames | Where-Object { $_ -notlike '*azuredeploy.json' }
    
            if ($playbooksFolderHasConnectorList.Count -gt 0) {
                $playbooksFolderResult = $playbooksFolderResult | Where-Object { (-not($_ -match $playbooksFolderHasConnectorList )) }
            }
        }
    
        #for cisco umbrella
        # check if individual file exist inside of playbooks folder and check content if "resources" section has "type" = "Microsoft.Resources/deployments"
        #if it has Microsoft.Resources/deployments type then we should skip this file
    
        # Helper function to filter out playbooks with Microsoft.Resources/deployments
        function Remove-LinkedTemplates {
            param(
                [Parameter(Mandatory = $true)]
                [array]$PlaybookFiles,
                [string]$BaseFolderPath
            )
            $filtered = @()
            foreach ($item in $PlaybookFiles) {
                $filePath = $BaseFolderPath + $item
                if (Test-Path $filePath) {
                    $fileContentObj = Get-Content "$filePath" | ConvertFrom-Json
                    if ($null -ne $fileContentObj) {
                        $hasLinked = $false
                        foreach ($resource in $fileContentObj.resources) {
                            if ($resource.type -eq "Microsoft.Resources/deployments") {
                                $hasLinked = $true
                                break
                            }
                        }
                        if (-not $hasLinked) { $filtered += $item }
                    } else {
                        $filtered += $item
                    }
                } else {
                    $filtered += $item
                }
            }
            return $filtered
        }

        # Remove linked templates from playbooksFolderResult
        $playbooksFolderResult = Remove-LinkedTemplates -PlaybookFiles $playbooksFolderResult -BaseFolderPath $baseFolderPath
        $playbooksFolderResult = $playbooksFolderResult | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }

        # Find dynamic custom connectors (excluding Data Connectors)
        $filterPath = "$solutionFolderPath*Connector/*"
        $playbooksDynamicCustomConnector = $filesList -like $filterPath | Where-Object { $_ -notlike '*/Data Connectors/*' -and $_ -notlike '*/DataConnectors/*' }
        if ($playbooksDynamicCustomConnector -and $playbooksDynamicCustomConnector.Count -gt 0) {
            $playbooksDynamicCustomConnector = Get-PlaybooksJsonFileNames($playbooksDynamicCustomConnector)
            $playbooksDynamicCustomConnector = Remove-LinkedTemplates -PlaybookFiles $playbooksDynamicCustomConnector -BaseFolderPath $baseFolderPath
        }
        $playbooksFinalDynamicCustomConnectorCount = $playbooksDynamicCustomConnector.Count
    
        #check if custom connector folder is present in root of solutions folder
        $playbookCustomConnectorFolderInRoot = "$solutionFolderPath" + "CustomConnector/"
        $playbookCustomConnectorFolderInRootFiles = $filesList -match ([regex]::Escape($playbookCustomConnectorFolderInRoot)) | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
    
        if ($playbookCustomConnectorFolderInRootFiles.Count -gt 0) {
            # BELOW LINE IS TO JUST GET JSON FILES AND EXCLUDE OTHER TYPE OF FILES.
            $playbookCustomConnectorFolderInRootFiles = Get-PlaybooksJsonFileNames($playbookCustomConnectorFolderInRootFiles)
        }
        $playbookCustomConnectorFolderInRootCount = $playbookCustomConnectorFolderInRootFiles.Count
    
        #check if custom connector folder is present in solutions playbook folder
        $playbookCustomConnectorFolderInSolution = "$solutionFolderPath" + "Playbooks/CustomConnector/"
        $playbookCustomConnectorFolderInSolutionFiles = $filesList -match ([regex]::Escape($playbookCustomConnectorFolderInSolution)) | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
        if ($playbookCustomConnectorFolderInSolutionFiles.Count -gt 0) {
            # BELOW LINE IS TO JUST GET JSON FILES AND EXCLUDE OTHER TYPE OF FILES.
            $playbookCustomConnectorFolderInSolutionFiles = Get-PlaybooksJsonFileNames($playbookCustomConnectorFolderInSolutionFiles)
        }
        $playbookCustomConnectorFolderInSolutionCount = $playbookCustomConnectorFolderInSolutionFiles.Count
    
        #check if connector folder is present in root of solutions folder
        $playbookConnectorFolderInRoot = "$solutionFolderPath" + "Connector/"
        $playbookConnectorFolderInRootFiles = $filesList -match ([regex]::Escape($playbookConnectorFolderInRoot)) | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
        if ($playbookConnectorFolderInRootFiles.Count -gt 0) {
            # BELOW LINE IS TO JUST GET JSON FILES AND EXCLUDE OTHER TYPE OF FILES.
            $playbookConnectorFolderInRootFiles = Get-PlaybooksJsonFileNames($playbookConnectorFolderInRootFiles)
        }
        $playbookConnectorFolderInRootCount = $playbookConnectorFolderInRootFiles.Count
    
        #check if connector folder is present in solutions playbook folder
        $playbookConnectorFolderInSolution = "$solutionFolderPath" + "Playbooks/Connector/"
        $playbookConnectorFolderInSolutionFiles = $filesList -match ([regex]::Escape($playbookConnectorFolderInSolution)) | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
        if ($playbookConnectorFolderInSolutionFiles.Count -gt 0) {
            # BELOW LINE IS TO JUST GET JSON FILES AND EXCLUDE OTHER TYPE OF FILES.
            $playbookConnectorFolderInSolutionFiles = Get-PlaybooksJsonFileNames($playbookConnectorFolderInSolutionFiles)
        }
        $playbookConnectorFolderInSolutionCount = $playbookConnectorFolderInSolutionFiles.Count
    
        $formulatePlaybooksList = @();
    
        # IDENTIFY THE NAME OF FIRST CUSTOM CONNECTOR SO THAT WE CAN COMPARE IT WITH THE LIST OF FILE NAMES OF PLAYBOOKS IF INPUT HAS PLAYBOOKS ARRAY SPECIFIED
        if ($playbookCustomConnectorFolderInRootCount -le 0 -and 
        $playbookCustomConnectorFolderInSolutionCount -le 0 -and 
        $playbookConnectorFolderInRootCount -le 0 -and 
        $playbookConnectorFolderInSolutionCount -le 0 -and 
        $playbooksFinalDynamicCustomConnectorCount -le 0) {
            #THIS MEANS WE DONT HAVE CUSTOM CONNECTOR FOR PLAYBOOKS IN ANY WAY
            $formulatePlaybooksList = $playbooksFolderResult
        }
        else {
            # if we have custom connector then we do below
            $hasCustomPlaybook = $true;
            $allPlaybookFiles = $playbooksFolderResult
            if ($playbookCustomConnectorFolderInRootCount -gt 0) {
                # ADD CUSTOM PLAYBOOK FIRST AND THEN ADD OTHER PLAYBOOK FILES - WITHIN SOLUTION FOLDER, BUT OUTSIDE OF PLAYBOOKS FOLDER IN CustomConnector
                if ($playbookCustomConnectorFolderInRootCount -eq 1) {
                    $formulatePlaybooksList += "$playbookCustomConnectorFolderInRootFiles"
                }
                else {
                    if ($playbookCustomConnectorFolderInRootFiles.Count -gt 0) {
                        $playbookCustomConnectorFolderInRootFilesFirstFile = Get-PlaybooksJsonFileNames($playbookCustomConnectorFolderInRootFiles) | Select-Object -first 1
                        $formulatePlaybooksList += "$playbookCustomConnectorFolderInRootFilesFirstFile"
                    }
                }
            }
            elseif ($playbookConnectorFolderInRootCount -gt 0) {
                # ADD CUSTOM PLAYBOOK FIRST AND THEN ADD OTHER PLAYBOOK FILES - WITHIN SOLUTION FOLDER, BUT OUTSIDE OF PLAYBOOKS FOLDER IN Connector
                if ($playbookConnectorFolderInRootCount -eq 1) {
                    $formulatePlaybooksList += "$playbookConnectorFolderInRootFiles"
                }
                else {
                    if ($playbookConnectorFolderInRootFiles.Count -gt 0) {
                        $playbookConnectorFolderInRootFilesFirstFile = Get-PlaybooksJsonFileNames($playbookConnectorFolderInRootFiles) | Select-Object -first 1
                        $formulatePlaybooksList += "$playbookConnectorFolderInRootFilesFirstFile"
                    }
                }
            }
            elseif ($playbookCustomConnectorFolderInSolutionCount -gt 0) {
                # ADD CUSTOM PLAYBOOK FIRST AND THEN ADD OTHER PLAYBOOK FILES - WITHIN SOLUTION FOLDER, BUT INSIDE OF PLAYBOOKS FOLDER IN CustomConnector
                if ($playbookCustomConnectorFolderInSolutionCount -eq 1) {
                    $formulatePlaybooksList += "$playbookCustomConnectorFolderInSolutionFiles"
                }
                else {
                    if ($playbookCustomConnectorFolderInSolutionFiles.Count -gt 0) {
                        $playbookCustomConnectorFolderInSolutionFilesFirstFile = Get-PlaybooksJsonFileNames($playbookCustomConnectorFolderInSolutionFiles) | Select-Object -first 1
                        $formulatePlaybooksList += $playbookCustomConnectorFolderInSolutionFilesFirstFile
                    }
                }
            }
            elseif ($playbookConnectorFolderInSolutionCount -gt 0) {
                if ($playbookConnectorFolderInSolutionCount -eq 1) {
                    $formulatePlaybooksList += "$playbookConnectorFolderInSolutionFiles"
                }
                else {
                    if ($playbookConnectorFolderInSolutionFiles.Count -gt 0) {
                        $playbookConnectorFolderInSolutionFilesFirstFile = Get-PlaybooksJsonFileNames($playbookConnectorFolderInSolutionFiles) | Select-Object -first 1
                        $formulatePlaybooksList += "$playbookConnectorFolderInSolutionFilesFirstFile"
                    }
                }
            }
            elseif ($playbooksFinalDynamicCustomConnectorCount -gt 0) {
                foreach($item in $playbooksDynamicCustomConnector)
                {
                    $formulatePlaybooksList += "$item"
                }
                #$formulatePlaybooksList += "$playbooksDynamicCustomConnector"
            }
    
            # ADD REMAINING PLAYBOOKS
            foreach($item in $allPlaybookFiles)
            {
                $hasMatchingPlaybook = $formulatePlaybooksList -match $item
                if (!$hasMatchingPlaybook)
                {
                    # ADD ONLY WHEN SAME FILES ARE NOT PRESENT I.E IGNORE ALREADY ADDED CUSTOM PLAYBOOK 
                    $formulatePlaybooksList += $item
                }
            }
        }
    
        $playbooksArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("Playbooks")))
    
        $playbooksFinalList = @()
        # if functionapp files are there then we add it first and then rest files
        if ($playbooksFunctionAppFiles.Count -gt 0)
        {
            # ADD FUNCTION APP LIST FIRST
            foreach($item in $playbooksFunctionAppFiles)
            {
                $playbooksFinalList += $item.Replace("$solutionFolderPath", '')
            }
    
            # ADD REMAINING PLAYBOOKS
            foreach ($fl in $formulatePlaybooksList)
            {
                if ($playbooksFinalList -notcontains $fl)
                {
                    $playbooksFinalList += $fl.Replace("$solutionFolderPath", '')
                }
            }
        }
        else 
        {
            foreach ($fl in $formulatePlaybooksList)
            {
                if ($playbooksFinalList -notcontains $fl)
                {
                    $playbooksFinalList += $fl.Replace("$solutionFolderPath", '')
                }
            }
        }
    
        if (!$playbooksArrayAttributeExist) {
            # IF OBJECT IS NOT PRESENT IN DATA FILE THEN WE ADD IT DYNAMICALLY
            $playbooksFinalListJson = $playbooksFinalList | ConvertTo-Json
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'Playbooks' -Value $playbooksFinalList -PassThru
            }
        }
        else {
            # IF ATTRIBUTE IN DATA FILE IS PRESENT THEN WE VERIFY FILES
            if ($dataFileContentObject.Playbooks.Count -gt 0) {
                $dataFileContentObject.PSObject.Properties.Remove('Playbooks')
                $playbooksFinalListJson = $playbooksFinalList | ConvertTo-Json
                $datafilecontentobject | foreach-object {
                    $_ | add-member -membertype noteproperty -name 'Playbooks' -value $playbooksFinalList -passthru
                }
            }
            else {
                # REMOVE THIS TAG AS USER HAS EXPLICITLY SPECIFIED EMPTY PLAYBOOK ARRAY
                $dataFileContentObject.PSObject.Properties.Remove('Playbooks')
            }
        }
    
        Write-Host "Final Playbook List Json is $playbooksFinalListJson"
    }

    # ===============end of new: Playbooks Code ============

    if ($workbooksFolderResultLength -gt 0) {
        $workbooksArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("Workbooks")))

        $workbookFiles = Get-WorkbooksJsonFileNames($workbooksFolderResult)

        $workbooksFolderResultArray = $workbookFiles | ConvertTo-Json -AsArray

        if (!$workbooksArrayAttributeExist) {
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'Workbooks' -Value $workbooksFolderResultArray -PassThru
            }
        } 
        else {
            if ($dataFileContentObject.Workbooks.Count -gt 0) {
                $newWorkbookFiles = @()
                $newWorkbookFiles = Get-OnlyFileNames -filePaths $dataFileContentObject.Workbooks -folderNameWithSlash "Workbooks/"

                $dataFileworkbooksList = Get-WorkbooksJsonFileNames($newWorkbookFiles) | ConvertTo-Json -AsArray
                $dataFileContentObject.PSObject.Properties.Remove('Workbooks')
                $datafilecontentobject | foreach-object {
                    $_ | add-member -membertype noteproperty -name 'Workbooks' -value $dataFileworkbooksList -passthru
                }
            }
            else { $dataFileContentObject.PSObject.Properties.Remove('Workbooks') }
        }
    }

    Write-Host "analyticRulesFolderResult $analyticRulesFolderResult, analyticRulesFolderResultLength $analyticRulesFolderResultLength, dataFileContentObject $dataFileContentObject"
    if ($analyticRulesFolderResultLength -gt 0) {
        $analyticRulesFolderResultArray = $analyticRulesFolderResult | ConvertTo-Json -AsArray
        $analyticRulesArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("Analytic Rules")))
        if (!$analyticRulesArrayAttributeExist) {
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'Analytic Rules' -Value $analyticRulesFolderResultArray -PassThru
            }
        } 
        else {
            if ($dataFileContentObject.'Analytic Rules'.Count -gt 0) {
                $dataFileanalyticRulesList = (Get-ValidFileNamesByExtension $dataFileContentObject.'Analytic Rules' ".yaml") | ConvertTo-Json -AsArray
                $dataFileContentObject.PSObject.Properties.Remove('Analytic Rules')
                $datafilecontentobject | foreach-object {
                    $_ | add-member -membertype noteproperty -name 'Analytic Rules' -value $dataFileanalyticRulesList -passthru
                }
            } 
            else { 
                $dataFileContentObject.PSObject.Properties.Remove('Analytic Rules') 
            }
        }
    }

    Write-Host "huntingQueriesFolderResult $huntingQueriesFolderResult, huntingQueriesFolderResultLength $huntingQueriesFolderResultLength, dataFileContentObject $dataFileContentObject"
    if ($huntingQueriesFolderResultLength -gt 0) {
        $huntingQueriesFolderResultArray = $huntingQueriesFolderResult | ConvertTo-Json -AsArray
        $huntingQueriesArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("Hunting Queries")))
        if (!$huntingQueriesArrayAttributeExist) {
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'Hunting Queries' -Value $huntingQueriesFolderResultArray -PassThru
            }
        } 
        else {
            if ($dataFileContentObject.'Hunting Queries'.Count -gt 0) {
                $dataFilehuntingList = (Get-ValidFileNamesByExtension $dataFileContentObject.'Hunting Queries' ".yaml") | ConvertTo-Json -AsArray
                $dataFileContentObject.PSObject.Properties.Remove('Hunting Queries')
                $datafilecontentobject | foreach-object {
                    $_ | add-member -membertype noteproperty -name 'Hunting Queries' -value $dataFilehuntingList -passthru
                }
            } 
            else {
                $dataFileContentObject.PSObject.Properties.Remove('Hunting Queries') 
            }
        }
    }

    #===================Start : Watchlist code================
    if ($watchlistInWorkbookFolderLength -gt 0 -or $watchlistsFolderResultLength -gt 0) {
        $isWatchListInsideOfWorkbooksFolder = $false
        # WATCHLIST FILES ARE INSIDE OF WORKBOOKS FOLDER OR THEY ARE IN THE ROOT OF THE SOLUTIONS FOLDER
        if ($watchlistInWorkbookFolderLength -gt 0) {
            $watchlistFolderResultArray = $watchlistInWorkbooksFolderResult | ConvertTo-Json -AsArray
            $isWatchListInsideOfWorkbooksFolder = $true
        }
        elseif ($watchlistsFolderResultLength -gt 0) {
            $watchlistFolderResultArray = $watchlistsFolderResult | ConvertTo-Json -AsArray
            $isWatchListInsideOfWorkbooksFolder = $false
        }

        if ($null -ne $watchlistFolderResultArray -ne $watchlistFolderResultArray -eq '') {
            $watchlistsArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("Watchlists")))
            if (!$watchlistsArrayAttributeExist) {
                $dataFileContentObject | ForEach-Object {
                    $_ | Add-Member -MemberType NoteProperty -Name 'Watchlists' -Value $watchlistFolderResultArray -PassThru
                }
            }
        }
    }
    #===================End: Watchlist code================

    # ===============Start of new: SummaryRules Code ============
    $summaryRulesFolderResult = $filesList -match ([regex]::Escape($solutionSummaryRulesFolder)) | ForEach-Object { $_.replace($solutionSummaryRulesFolder, '', 'OrdinalIgnoreCase') }
    $summaryRulesWithSpaceFolderResult = $filesList -match ([regex]::Escape($solutionSummaryRulesWithSpaceFolder)) | ForEach-Object { $_.replace($solutionSummaryRulesWithSpaceFolder, '', 'OrdinalIgnoreCase') }
    $summaryRulesFolderResultLength = $summaryRulesFolderResult.Count
    $summaryRulesWithSpaceFolderResultLength = $summaryRulesWithSpaceFolderResult.Count

    $summaryRulesArrayAttributeExist = [bool]($dataFileContentObject.PSobject.Properties.name -match ([regex]::Escape("SummaryRules")))
    if ($summaryRulesFolderResultLength -gt 0 -or $summaryRulesWithSpaceFolderResultLength -gt 0) {
        $allSummaryRules = @()
        if ($summaryRulesFolderResultLength -gt 0) {
            $allSummaryRules += $summaryRulesFolderResult
        }
        if ($summaryRulesWithSpaceFolderResultLength -gt 0) {
            $allSummaryRules += $summaryRulesWithSpaceFolderResult
        }
        $allSummaryRules = Normalize-SummaryRulesPaths $allSummaryRules
        $allSummaryRules = $allSummaryRules | Where-Object { $_ -ne '' }
        $allSummaryRulesArray = $allSummaryRules | ConvertTo-Json -AsArray
        if (!$summaryRulesArrayAttributeExist) {
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'SummaryRules' -Value $allSummaryRulesArray -PassThru
            }
        } else {
            if ($dataFileContentObject.SummaryRules.Count -gt 0) {
                $normalizedSummaryRules = Normalize-SummaryRulesPaths $dataFileContentObject.SummaryRules | ConvertTo-Json -AsArray
                $dataFileContentObject.PSObject.Properties.Remove('SummaryRules')
                $datafilecontentobject | foreach-object {
                    $_ | add-member -membertype noteproperty -name 'SummaryRules' -value $normalizedSummaryRules -passthru
                }
            } else {
                $dataFileContentObject.PSObject.Properties.Remove('SummaryRules')
            }
        }
    }

    $jsonDataFile = $dataFileContentObject | ConvertTo-Json
    $jsonDataFile.replace("'", "''") # replace single quote with double
    Write-Host "Calculated Json data file $jsonDataFile"

    # UPDATE DATA FILE WITH NEW JSON CONTENT
    Write-Host "Updating data input file $dataFolderFile"
    Set-Content -Path $dataFilePath -Value $jsonDataFile

    Write-Host "Now going to execute createSolutionV4 file"

    if ($null -eq $isWatchListInsideOfWorkbooksFolder -or $isWatchListInsideOfWorkbooksFolder -eq '') {
        $isWatchListInsideOfWorkbooksFolder = $false
    }

    ./Tools/Create-Azure-Sentinel-Solution/pipeline/createSolutionV4.ps1 $baseFolderPath $solutionName $dataFileContentObject $dataFolderFile $dataConnectorFolderName $dataFolderActualName $instrumentationKey $pullRequestNumber $runId $packageVersion $defaultPackageVersion $isWatchListInsideOfWorkbooksFolder

    $packageCreationPath = "" + $baseFolderPath + "Solutions/" + $solutionName + "/Package/"
    Write-Host "packageCreationPath $packageCreationPath"
    $zipPackagePath = $packageCreationPath + $packageVersion + ".zip"
    if (Test-Path -Path "$zipPackagePath") {
        $allFilesInCreatedPackage = Get-ChildItem "$zipPackagePath" 
        $allFilesInCreatedPackageCount = $allFilesInCreatedPackage.Count
    } else {
        $allFilesInCreatedPackageCount = 0
    }

    $blobName = "" + $solutionName + "_" + $pullRequestNumber + "_" + $packageVersion
    Write-Host "Blob name is $blobName"
    Write-Host "Package Files List are : $allFilesInCreatedPackage"
    Write-Host "Package Files Count $allFilesInCreatedPackageCount"

    $solutionBaseFolderPath = "Solutions/" + $solutionName + "/Package"

    if ($allFilesInCreatedPackageCount -gt 0) {
        $uploadPackagePath = $packageCreationPath + $packageVersion + ".zip"
        Write-Output "isCreatePackage=$true" >> $env:GITHUB_OUTPUT
        Write-Output "solutionBaseFolderPath=$solutionBaseFolderPath" >> $env:GITHUB_OUTPUT
        Write-Output "packageCreationPath=$packageCreationPath" >> $env:GITHUB_OUTPUT
        Write-Output "packageVersion=$packageVersion" >> $env:GITHUB_OUTPUT
        Write-Output "blobName=$blobName" >> $env:GITHUB_OUTPUT
        Write-Output "dataFileLink=$dataFileLink" >> $env:GITHUB_OUTPUT
        Write-Output "dataFolderPath=$dataFolderPath" >> $env:GITHUB_OUTPUT
        Write-Output "dataInputFileName=$dataFolderFile" >> $env:GITHUB_OUTPUT 
        Write-Output "uploadPackagePath=$uploadPackagePath" >> $env:GITHUB_OUTPUT

        Write-Host "Package created successfully!"
    }
    else {
        Write-Output "::error::Package creation for Solution '$solutionName' Failed with an error" 
        ErrorOutput
    }
}
catch {
    $errorDetails = $_
    $errorInfo = $_.Exception
    Write-Output "Error Details $errorDetails , Error Info $errorInfo"
    
    Write-Host "Package-generator: Error occured in catch block!"
    ErrorOutput
}