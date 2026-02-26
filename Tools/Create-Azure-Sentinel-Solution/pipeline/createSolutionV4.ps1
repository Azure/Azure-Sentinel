param (
    [Parameter(Mandatory = $true)]
    [string]$pipelineBasePath,
    [Parameter(Mandatory = $true)]
    [string]$pipelineSolutionName,
    [Parameter(Mandatory = $true)]
    $pipelineDataFileRawContent,
    [Parameter(Mandatory = $true)]
    [string]$dataFileName,
    [Parameter(Mandatory = $true)]
    [string]$dataConnectorFolderName,
    [Parameter(Mandatory = $true)]
    [string]$dataFolderActualName,
    [Parameter(Mandatory = $true)]
    [string]$instrumentationKey,
    [Parameter(Mandatory = $true)]
    [string]$pullRequestNumber,
    [Parameter(Mandatory = $true)]
    [string]$runId,
    [Parameter(Mandatory = $true)]
    [string]$calculatedPackageVersion,
    [Parameter(Mandatory = $true)]
    [string]$defaultPackageVersion,
    [bool]$isWatchListInsideOfWorkbooksFolder = $false
)

. ./Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1
. ./Tools/Create-Azure-Sentinel-Solution/common/get-ccp-details.ps1

# Add a helper to normalize folder case for summary rules
function Normalize-SummaryRulesFolderCase {
    param(
        [Parameter(Mandatory = $true)]
        [string]$path
    )
    # Replace any case variant of 'Summary Rules' with the actual folder name as in the repo
    $path = $path -replace '(?i)summary rules', 'Summary Rules'
    $path = $path -replace '(?i)summaryrules', 'SummaryRules'
    return $path
}

try {
    $isPipelineRun = $true
    Write-Host "Running for Build Pipeline"
    Write-Host "Data File Content is $pipelineDataFileRawContent"

    $path = Join-Path -Path $pipelineBasePath -ChildPath "Solutions/$pipelineSolutionName/$dataFolderActualName/$dataFileName"
    $solutionFolderBasePath = Join-Path -Path $pipelineBasePath -ChildPath "Solutions/$pipelineSolutionName"

    foreach ($inputFile in Get-ChildItem $path) {
        $contentToImport = $pipelineDataFileRawContent
        $basePath = Join-Path -Path $pipelineBasePath -ChildPath "Solutions/$pipelineSolutionName/"
        $solutionName = $pipelineSolutionName
        $baseMetadata = $pipelineDataFileRawContent
        $metadataCounter = 0
        $global:solutionId = $baseMetadata.publisherId + "." + $baseMetadata.offerId
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "solutionId" -NotePropertyValue "$global:solutionId"
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionId" -NotePropertyValue "[variables('solutionId')]"

        $metadataAuthor = $contentToImport.Author -split " - "
        if ($null -ne $metadataAuthor[1]) {
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "email" -NotePropertyValue $($metadataAuthor[1])
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_email" -NotePropertyValue "[variables('email')]"
        }

        $major = $contentToImport.version -split '\.' | Select-Object -First 1
        if ($major -ge 3) {
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionName" -NotePropertyValue $solutionName
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionVersion" -NotePropertyValue $contentToImport.version
        }
        
        Write-Host "Package version identified is $calculatedPackageVersion"
        $contentResourceDetails = returnContentResources $calculatedPackageVersion
        if ($null -eq $contentResourceDetails) {
            Write-Error "Not able to identify content resource details based on Version. Please verify if Version in data input file is correct!"
            return
        }

        $ccpDict = @()
        $ccpTablesFilePaths = @()
        $ccpTablesCounter = 1
        $isCCPConnector = $false
        foreach ($objectProperties in $contentToImport.PSObject.Properties) {
            $objectKeyLowercase = $objectProperties.Name.ToLower()
            if ($objectKeyLowercase -in @('name','author','logo','description','basepath','version','metadata','templatespec','is1pconnector','createpackage','dependentdomainsolutionids')) {
                continue
            }
            elseif ($objectKeyLowercase -in @('parsers','data connectors','dataconnectors','playbooks','workbooks','analytic rules','hunting queries','watchlists', 'summary rules', 'summaryrules')) {
                $currentRunningPropertyName = $objectKeyLowercase
                $propertyValue = $objectProperties.Value
                Write-Host "currentRunningPropertyName $currentRunningPropertyName , property Value is $propertyValue"

                if ($propertyValue -is [string]) {
                    try { $filesList = $propertyValue | ConvertFrom-Json } catch { $filesList = $propertyValue }
                } else {
                    $filesList = $propertyValue 
                }

                $solutionBasePath = (Join-Path $pipelineBasePath 'Solutions/')
                $solutionMetadataPath = Join-Path $solutionBasePath "$($pipelineDataFileRawContent.Name)/$($pipelineDataFileRawContent.Metadata)"
                $solutionBaseMetadata = Get-Content -Raw $solutionMetadataPath | Out-String | ConvertFrom-Json

                if ($null -eq $solutionBaseMetadata) {
                    Write-Error "Please verify if the given path $solutionMetadataPath is correct and/or Solution folder name and Data file Name attribute value is correct!"
                    exit 1
                }

                if (-not $isCCPConnector -and ($dataFileContentObject.'Data Connectors'.Count -gt 0 -or $dataFileContentObject.'DataConnectors'.Count -gt 0)) {
                    [array]$ccpDict = Get-CCP-Dict -dataFileMetadata $pipelineDataFileRawContent -baseFolderPath $solutionBasePath -solutionName $solutionName -DCFolderName $dataConnectorFolderName

                    if ($null -ne $ccpDict -and $ccpDict.Count -gt 0) {
                        $isCCPConnector = $true
                        [array]$ccpTablesFilePaths = GetCCPTableFilePaths -existingCCPDict $ccpDict -baseFolderPath $solutionBasePath -solutionName $solutionName -DCFolderName $dataConnectorFolderName
                    }
                }

                Write-Host "isCCPConnector $isCCPConnector"
                $ccpConnectorCodeExecutionCounter = 1
                foreach ($file in $filesList) {
                    $fileExtension = $file -split '\.' | Select-Object -Last 1
                    Write-Host "Current file is $file, File extension is $fileExtension"
                    switch ($objectKeyLowercase) {
                        'parsers' 
                        { 
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/Parsers/"; 
                            $finalPath += $file.Replace('Parsers/', '') 
                        }
                        'data connectors' 
                        { 
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/$dataConnectorFolderName/"; 
                            $finalPath += $file.Replace("$dataConnectorFolderName/", '') 
                        }
                        'dataconnectors' 
                        { 
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/$dataConnectorFolderName/"; 
                            $finalPath += $file.Replace("$dataConnectorFolderName/", '') 
                        }
                        'playbooks' {
                            if ($file -like "Solutions/$solutionName/*") { $file = $file.Replace("Solutions/$solutionName/", '') }
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/"; $finalPath += $file
                        }
                        'workbooks' 
                        { 
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/Workbooks/"; 
                            $finalPath += $file.Replace('Workbooks/', '') 
                        }
                        'analytic rules' 
                        {
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/Analytic Rules/"; 
                            $finalPath += $file.Replace("Solutions/$pipelineSolutionName/", "").Replace('Analytic Rules/', '') 
                        }
                        'hunting queries' 
                        { 
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/Hunting Queries/"; 
                            $finalPath += $file.Replace("Solutions/$pipelineSolutionName/", "").Replace('Hunting Queries/', '') 
                        }
                        'watchlists' {
                            if ($isWatchListInsideOfWorkbooksFolder) {
                                $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/Workbooks/Watchlists/"; $finalPath += $file.Replace("Solutions/$pipelineSolutionName/", "").Replace('Watchlists/', '')
                            } else {
                                $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/Watchlists/"; $finalPath += $file.Replace("Solutions/$pipelineSolutionName/", "").Replace('Watchlists/', '')
                            }
                        }
                        'summary rules' {
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/Summary Rules/"; $finalPath += $file.Replace('Summary Rules/', '')
                        }
                        'summaryrules' {
                            $finalPath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName/SummaryRules/"; $finalPath += $file.Replace('SummaryRules/', '')
                        }
                        default { $finalPath = '' }
                    }

                    # In the file processing loop, before using $finalPath, normalize the folder case
                    $finalPath = Normalize-SummaryRulesFolderCase $finalPath

                    $finalPath = $finalPath.Replace('//', '/')
                    Write-Host "Final Path is $finalPath"
                    $rawData = $null
                    try {
                        Write-Host "Downloading $finalPath"
                        # Case-insensitive file existence check for cross-platform compatibility
                        $parentDir = Split-Path -Path $finalPath -Parent
                        $fileName = [System.IO.Path]::GetFileName($finalPath)
                        $actualFile = Get-ChildItem -Path $parentDir -Filter "*" | Where-Object { $_.Name -ieq $fileName }
                        if ($null -ne $actualFile) {
                            Write-Host "Found file: $($actualFile.FullName)"
                            $rawData = Get-Content -Raw $actualFile.FullName
                        } else {
                            Write-Error "File not found (case-insensitive) for $finalPath"
                            exit 1
                        }
                    } catch {
                        Write-Error "Failed to read $finalPath -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))"
                        exit 1
                    }
                    try {
                        $json = ConvertFrom-Json $rawData -ErrorAction Stop
                        $validJson = $true
                    } catch {
                        $validJson = $false
                    }
                    if ($validJson) {
                        switch ($objectKeyLowercase) {
                            'workbooks' { GetWorkbookDataMetadata -file $file -isPipelineRun $isPipelineRun -contentResourceDetails $contentResourceDetails -baseFolderPath $pipelineBasePath -contentToImport $contentToImport }
                            'playbooks' { GetPlaybookDataMetadata -file $file -contentToImport $contentToImport -contentResourceDetails $contentResourceDetails -json $json -isPipelineRun $true }
                            'data connectors' {
                                $isCCPConnectorFile = $false
                                foreach ($item in $ccpDict) {
                                    if ($item.DCDefinitionFullPath -eq $finalPath) { $isCCPConnectorFile = $true; break }
                                }
                                if ($isCCPConnectorFile -and $ccpConnectorCodeExecutionCounter -eq 1) {
                                    GetDataConnectorMetadata -file $file -contentResourceDetails $contentResourceDetails -dataFileMetadata $pipelineDataFileRawContent -solutionFileMetadata $solutionBaseMetadata -dcFolderName $dataConnectorFolderName -ccpDict $ccpDict -solutionBasePath $solutionBasePath -solutionName $solutionName -ccpTables $ccpTablesFilePaths -ccpTablesCounter $ccpTablesCounter
                                    $ccpConnectorCodeExecutionCounter += 1
                                } elseif ($isCCPConnectorFile) {
                                    continue
                                } else {
                                    GetDataConnectorMetadata -file $file -contentResourceDetails $contentResourceDetails -dataFileMetadata $pipelineDataFileRawContent -solutionFileMetadata $solutionBaseMetadata -dcFolderName $dataConnectorFolderName -ccpDict $null -solutionBasePath $solutionBasePath -solutionName $solutionName -ccpTables $null -ccpTablesCounter $ccpTablesCounter
                                }
                            }
                            'dataconnectors' {
                                $isCCPConnectorFile = $false
                                foreach ($item in $ccpDict) {
                                    if ($item.DCDefinitionFullPath -eq $finalPath) { $isCCPConnectorFile = $true; break }
                                }
                                if ($isCCPConnectorFile -and $ccpConnectorCodeExecutionCounter -eq 1) {
                                    GetDataConnectorMetadata -file $file -contentResourceDetails $contentResourceDetails -dataFileMetadata $pipelineDataFileRawContent -solutionFileMetadata $solutionBaseMetadata -dcFolderName $dataConnectorFolderName -ccpDict $ccpDict -solutionBasePath $solutionBasePath -solutionName $solutionName -ccpTables $ccpTablesFilePaths -ccpTablesCounter $ccpTablesCounter
                                    $ccpConnectorCodeExecutionCounter += 1
                                } elseif ($isCCPConnectorFile) {
                                    continue
                                } else {
                                    GetDataConnectorMetadata -file $file -contentResourceDetails $contentResourceDetails -dataFileMetadata $pipelineDataFileRawContent -solutionFileMetadata $solutionBaseMetadata -dcFolderName $dataConnectorFolderName -ccpDict $null -solutionBasePath $solutionBasePath -solutionName $solutionName -ccpTables $null -ccpTablesCounter $ccpTablesCounter
                                }
                            }
                            'savedsearches' { GenerateSavedSearches -json $json -contentResourceDetails $contentResourceDetails }
                            'watchlists' {
                                $watchListFileName = Get-ChildItem $finalPath
                                GenerateWatchList -json $json -isPipelineRun $isPipelineRun -watchListFileName $watchListFileName.BaseName
                            }
                            'summary rules' {
                                $summaryRuleFilePath = $repositoryBasePath + "Tools/Create-Azure-Sentinel-Solution/common/summaryRules.ps1"
                                . $summaryRuleFilePath
                                GenerateSummaryRules -solutionName $solutionName -file $finalPath -rawData $rawData -contentResourceDetails $contentResourceDetails
                            }
                            'summaryrules' {
                                $summaryRuleFilePath = $repositoryBasePath + "Tools/Create-Azure-Sentinel-Solution/common/summaryRules.ps1"
                                . $summaryRuleFilePath
                                GenerateSummaryRules -solutionName $solutionName -file $finalPath -rawData $rawData -contentResourceDetails $contentResourceDetails
                            }
                            default {
                                if ($file -match '(\.yaml)$' -and $objectKeyLowercase -ne 'parsers' -and $currentRunningPropertyName -ne 'parsers') {
                                    if ($objectKeyLowercase -eq 'hunting queries') {
                                        GetHuntingDataMetadata -file $file -rawData $rawData -contentResourceDetails $contentResourceDetails
                                    } elseif ($objectKeyLowercase -eq "summary rules" -or $objectKeyLowercase -eq "summaryrules") {
                                        $summaryRuleFilePath = $repositoryBasePath + "Tools/Create-Azure-Sentinel-Solution/common/summaryRules.ps1"
                                        . $summaryRuleFilePath
                                        GenerateSummaryRules -solutionName $solutionName -file $file -rawData $rawData -contentResourceDetails $contentResourceDetails
                                    } else {
                                        GenerateAlertRule -file $file -contentResourceDetails $contentResourceDetails
                                    }
                                } else {
                                    GenerateParsersList -file $file -contentToImport $contentToImport -contentResourceDetails $contentResourceDetails
                                }
                            }
                        }
                    } else {
                        if ($file -match '(\.yaml)$' -and $objectKeyLowercase -ne 'parsers' -and $currentRunningPropertyName -ne 'parsers') {
                            if ($objectKeyLowercase -eq 'hunting queries') {
                                GetHuntingDataMetadata -file $file -rawData $rawData -contentResourceDetails $contentResourceDetails
                            } elseif ($objectKeyLowercase -eq "summary rules" -or $objectKeyLowercase -eq "summaryrules") {
                                $summaryRuleFilePath = $repositoryBasePath + "Tools/Create-Azure-Sentinel-Solution/common/summaryRules.ps1"
                                . $summaryRuleFilePath
                                GenerateSummaryRules -solutionName $solutionName -file $file -rawData $rawData -contentResourceDetails $contentResourceDetails
                            } else {
                                GenerateAlertRule -file $file -contentResourceDetails $contentResourceDetails
                            }
                        } else {
                            GenerateParsersList -file $file -contentToImport $contentToImport -contentResourceDetails $contentResourceDetails
                        }
                    }
                }
            }
        }
        foreach ($objectProperties in $contentToImport.PSObject.Properties) {
            $objectKeyLowercase = $objectProperties.Name.ToLower()
            if ($objectKeyLowercase -in @('publisherid','offerid','firstpublishdate','providers','categories','support','metadata')) {
                if ($metadataCounter -eq 1) { break }
                $metadataCounter = 1
                $rawData = $null
                $json = $pipelineDataFileRawContent
                $validJson = $true
                PrepareSolutionMetadata -solutionMetadataRawContent $json -contentResourceDetails $contentResourceDetails -defaultPackageVersion $defaultPackageVersion
            }
        }
        $global:analyticRuleCounter--
        $global:workbookCounter--
        $global:playbookCounter--
        $global:connectorCounter--
        $global:parserCounter--
        $global:huntingQueryCounter--
        $global:watchlistCounter--
        $global:summaryRuleCounter--

        updateDescriptionCount $global:connectorCounter                                "**Data Connectors:** "                     "{{DataConnectorCount}}"            $(checkResourceCounts $global:parserCounter, $global:analyticRuleCounter, $global:workbookCounter, $global:playbookCounter, $global:huntingQueryCounter, $global:watchlistCounter, $global:summaryRuleCounter)
        updateDescriptionCount $global:parserCounter                                   "**Parsers:** "                             "{{ParserCount}}"                   $(checkResourceCounts $global:analyticRuleCounter, $global:workbookCounter, $global:playbookCounter, $global:huntingQueryCounter, $global:watchlistCounter, $global:summaryRuleCounter)
        updateDescriptionCount $global:workbookCounter                                 "**Workbooks:** "                           "{{WorkbookCount}}"                 $(checkResourceCounts $global:analyticRuleCounter, $global:playbookCounter, $global:huntingQueryCounter, $global:watchlistCounter, $global:summaryRuleCounter)
        updateDescriptionCount $global:analyticRuleCounter                             "**Analytic Rules:** "                      "{{AnalyticRuleCount}}"             $(checkResourceCounts $global:playbookCounter, $global:huntingQueryCounter, $global:watchlistCounter, $global:summaryRuleCounter)
        updateDescriptionCount $global:huntingQueryCounter                             "**Hunting Queries:** "                     "{{HuntingQueryCount}}"             $(checkResourceCounts $global:playbookCounter, $global:watchlistCounter, $global:summaryRuleCounter)
        updateDescriptionCount $global:watchlistCounter                                "**Watchlists:** "                          "{{WatchlistCount}}"                $(checkResourceCounts $global:playbookCounter, $global:summaryRuleCounter)
        updateDescriptionCount $global:summaryRuleCounter                           "**Summary Rules:** "                       "{{SummaryRuleCount}}"             $(checkResourceCounts @($global:playbookCounter))
        updateDescriptionCount $global:customConnectorsList.Count                      "**Custom Azure Logic Apps Connectors:** "  "{{LogicAppCustomConnectorCount}}"  $(checkResourceCounts @($global:playbookCounter))
        updateDescriptionCount $global:functionAppList.Count                           "**Function Apps:** "                       "{{FunctionAppsCount}}"             $(checkResourceCounts @($global:playbookCounter))
        updateDescriptionCount ($global:playbookCounter - $global:customConnectorsList.Count - $global:functionAppList.Count)  "**Playbooks:** "  "{{PlaybookCount}}"  $false
        GeneratePackage -solutionName $solutionName -contentToImport $contentToImport -calculatedBuildPipelinePackageVersion $calculatedPackageVersion
        Write-Host "Package Generated Successfully!!"
        $solutionFolderBasePath = Join-Path $pipelineBasePath "Solutions/$pipelineSolutionName"
        CheckJsonIsValid $solutionFolderBasePath
    }
} catch {
    $errorDetails = $_ | Out-String
    Write-Error "Error occured in createSolutionV4 file. Error Details : $errorDetails"
}
