param ($solutionName, $pullRequestNumber, $runId, $instrumentationKey, $defaultPackageVersion, $solutionOfferId, $inputBaseFolderPath, $isNewSolution)
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1
. ./.script/package-automation/catelogAPI.ps1

function ErrorOutput {
    Write-Host "Package creation process failed!"
    Write-Output "isCreatePackage=$false" >> $env:GITHUB_OUTPUT
    Write-Output "packageCreationPath=''" >> $env:GITHUB_OUTPUT
    Write-Output "blobName=''" >> $env:GITHUB_OUTPUT
    #exit 1
}

try {
    Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for Package-generator started for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId' = "$runId"; 'SolutionName' = "$solutionName"; 'PullRequestNumber' = "$pullRequestNumber"; 'EventName' = "Package Generator"; 'SolutionOfferId' = "$solutionOfferId"; }
    if ($null -eq $solutionName -or $solutionName -eq '') { 
        Write-Host "::error::Solution name not found" 
        ErrorOutput
    }

    function GetGivenFilesPathNames {
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)] 
            [System.Array] $givenInputFiles
        )
        $resultList = @()
        foreach ($item in $givenInputFiles) {
            $getFileNameLastIndex = $item.LastIndexOf('/')
            if ($getFileNameLastIndex -gt 0) {
                $resultList += $item.substring($getFileNameLastIndex + 1)
            }
        }
        return $resultList;
    }

    function GetValidDataConnectorFileNames { 
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array] $dataConnectorFiles
        )
        $newDataConnectorFilesWithoutExcludedFiles = @()
        foreach ($item in $dataConnectorFiles) {
            $hostFileExist = $item -match ([regex]::Escape("host.json"))
            $proxiesFileExist = $item -match ([regex]::Escape("proxies.json"))
            $azureDeployFileExist = $item -match ([regex]::Escape("azureDeploy"))
            $functionFileExist = $item -match ([regex]::Escape("function.json"))
            $textFileExist = $item -match ([regex]::Escape(".txt"))
            $zipFileExist = $item -match ([regex]::Escape(".zip"))
            $pythonFileExist = $item -match ([regex]::Escape(".py"))
            $jsonFile = $item -match ([regex]::Escape(".json"))

            if ($hostFileExist -or $proxiesFileExist -or $azureDeployFileExist -or $functionFileExist -or $textFileExist -or $zipFileExist -or $pythonFileExist) 
            { }
            else { 
                if ($jsonFile) {
                    $newDataConnectorFilesWithoutExcludedFiles += $item
                }
            }
        }
        return $newDataConnectorFilesWithoutExcludedFiles;
    }

    function GetValidWatchlistFileNames { 
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array] $watchlistFiles
        )
        $newWatchlistFiles = @()
        foreach ($item in $watchlistFiles) {
            $jsonFile = $item -match ([regex]::Escape(".json"))
            if ($jsonFile) {
                $newWatchlistFiles += $item
            }
        }

        return $newWatchlistFiles;
    }

    function IgnoreParameterFileInDataFolder { 
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)] 
            [System.Array] $datafolderFiles
        )
        $newDataFolderFilesWithoutExcludedFiles = @()
        foreach ($item in $datafolderFiles) {
            $paramterFileExist = $item -match ([regex]::Escape("parameters.json"))
            $paramtersFileExist = $item -match ([regex]::Escape("parameter.json"))
            $systemGeneratedFileExist = $item -match ([regex]::Escape("system_generated_metadata.json"))
            $testParametersFileExist = $item -match ([regex]::Escape("testParameters.json"))
            if ($paramterFileExist -or $paramtersFileExist -or $systemGeneratedFileExist -or $testParametersFileExist) 
            { } 
            else { 
                $newDataFolderFilesWithoutExcludedFiles += $item 
            } 
        }
        return $newDataFolderFilesWithoutExcludedFiles;
    }

    function GetPlaybooksJsonFileNames($playbookFiles) {
        $playbookFiles = $playbookFiles -match ([regex]::Escape(".json"))
    
        if ($playbookFiles.Count -gt 0) {
            $playbookFiles = $playbookFiles | Where-Object { $_ -notlike '*swagger*' -and $_ -notlike '*gov*' -and $_ -notlike '*function.json' -and $_ -notlike '*host.json' }
        }
    
        return $playbookFiles;
    }

    function GetValidFunctionAppConnectorFileNames { 
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array] $files
        )
        $newFilesWithoutExcludedFiles = @()
        foreach ($item in $files) {
            $hostFileExist = $item -match ([regex]::Escape("host.json"))
            $proxiesFileExist = $item -match ([regex]::Escape("proxies.json"))
            $functionFileExist = $item -match ([regex]::Escape("function.json"))
            $textFileExist = $item -match ([regex]::Escape(".txt"))
            $zipFileExist = $item -match ([regex]::Escape(".zip"))
            $pythonFileExist = $item -match ([regex]::Escape(".py"))
            $jsonFile = $item -match ([regex]::Escape(".json"))
            if ($hostFileExist -or $proxiesFileExist -or $functionFileExist -or $textFileExist -or $zipFileExist -or $pythonFileExist)
            { }
            else { 
                if ($jsonFile) {
                    $newFilesWithoutExcludedFiles += $item
                }
            }
        }
        return $newFilesWithoutExcludedFiles;
    }

    function GetWorkbooksJsonFileNames { 
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)] 
            [System.Array] $workbookFiles
        )
        $newWorkbookFilesWithoutExcludedFiles = @()
        $newWorkbookFilesWithoutExcludedFiles = $workbookFiles -match ([regex]::Escape(".json"))
        return $newWorkbookFilesWithoutExcludedFiles;
    }

    function GetOnlyFileNames {
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array] $filePaths,
            [Parameter(Mandatory = $true, Position = 1)]
            [System.String] $folderNameWithSlash
        )
        $newFiles = @()
        foreach ($item in $filePaths) {
            $indexOfFiles = $item.IndexOf($folderNameWithSlash); # $item.IndexOf("Workbooks/")
            $lengthOfFolder = $folderNameWithSlash.Length
            if ($indexOfFiles -gt 0) {
                # REPLACE ALL INITIAL FILE PATHS JUST GET THE FILE NAME
                $fileName = $item.Substring($indexOfFiles + $lengthOfFolder);
                $newFiles += $fileName
            }
            else {
                $newFiles += $item
            }
        }
        return $newFiles;
    }

    $solutionFolderPath = 'Solutions/' + $solutionName + "/"
    $filesList = git ls-files | Where-Object { $_ -like "$solutionFolderPath*" }
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

    $dataFolderFile = IgnoreParameterFileInDataFolder($dataFolderFiles)
    $solutionDataFolder = $solutionFolderPath + "$dataFolderActualName/"
    Write-Host "solutionDataFolder is $solutionDataFolder"

    $baseFolderPath = $inputBaseFolderPath #'/home/runner/work/packagingrepo/packagingrepo/'
    $dataFilePath = $baseFolderPath + $solutionDataFolder + $dataFolderFile
    $dataFileLink = "https://github.com/Azure/Azure-Sentinel/master/Solutions/$solutionName/$dataFolderActualName/$dataFolderFile"

    Write-Output "dataFileLink=$dataFileLink" >> $env:GITHUB_OUTPUT
    Write-Host "Data File Path $dataFilePath"

    $dataFileContentObject = Get-Content "$dataFilePath" | ConvertFrom-Json
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
    $Is1PconnectorAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Is1Pconnector")
    $logoAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Logo")
    $basePathAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "BasePath")
    $packageVersionAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Version")

    $hasAllRequiredDataFileAttributes = ($nameAttribute -and $authorAttribute -and $descriptionAttribute)

    Write-Host "hasAllRequiredDataFileAttributes $hasAllRequiredDataFileAttributes"
    if (!$hasAllRequiredDataFileAttributes) {
        Write-Host "::error::Required properties missing in data input file. Please make sure that key values pairs for attributes: Name, Author and Description are present in data file." 
        exit 0 
    }

    # =============START: DETAILS TO IDENTIFY VERSION FROM CATELOG API=========
    $customProperties = @{ 'RunId' = "$runId"; 'SolutionName' = "$solutionName"; 'PullRequestNumber' = "$pullRequestNumber"; 'EventName' = "Package Generator"; 'SolutionOfferId' = "$solutionOfferId"; }

    $offerId = "$solutionOfferId"
    $offerDetails = GetCatelogDetails $offerId
    Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Offer details in Package-generator for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties

    $userInputPackageVersion = ''
    if ($packageVersionAttribute) {
        $userInputPackageVersion = $dataFileContentObject.version
    }
    $packageVersion = GetPackageVersion $defaultPackageVersion $offerId $offerDetails $packageVersionAttribute $userInputPackageVersion

    Write-Host "Package version identified is $packageVersion"
    # =============END: DETAILS TO IDENTIFY VERSION FROM CATELOG API=========
    if (!$packageVersionAttribute) {
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'Version' -Value "$packageVersion"
    }
    else {
        if ($dataFileContentObject.Version -ne "$packageVersion") {
            $dataFileContentObject.PSObject.Properties.Remove('Version')
            $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'Version' -Value "$packageVersion"
        }
    }
    
    if (!$TemplateSpecAttribute) {
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'TemplateSpec' -Value $true 
    }

    if (!$is1PconnectorAttribute) {
        $dataFileContentObject | Add-Member -MemberType NoteProperty -Name 'Is1Pconnector' -Value $false 
    }

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

    $parserFolderResult = $filesList -match ([regex]::Escape($solutionParsersFolder)) | ForEach-Object { $_.replace($solutionParsersFolder, '', 'OrdinalIgnoreCase') }
    $dataConnectorsFolderResult = $filesList -match ([regex]::Escape($solutionDataConnectorsFolder)) | ForEach-Object { $_.replace( $solutionDataConnectorsFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataConnectorsFolderResult) {
        $dataConnectorsFolderResult = GetValidDataConnectorFileNames($dataConnectorsFolderResult)
    }

    $dataConnectorsWithSpaceFolderResult = $filesList -match ([regex]::Escape($solutionDataConnectorsWithSpaceFolder)) | ForEach-Object { $_.replace($solutionDataConnectorsWithSpaceFolder, '', 'OrdinalIgnoreCase') }
    if ($null -ne $dataConnectorsWithSpaceFolderResult) {
        $dataConnectorsWithSpaceFolderResult = GetValidDataConnectorFileNames($dataConnectorsWithSpaceFolderResult)
    }

    $playbooksFolderResult = $filesList -match ([regex]::Escape($solutionPlaybooksFolder))
    if ($null -ne $playbooksFolderResult) {
        $playbooksFolderResult = GetPlaybooksJsonFileNames($playbooksFolderResult)
    }

    $workbooksFolderResult = $filesList -match ([regex]::Escape($solutionWorkbooksFolder)) | ForEach-Object { $_.replace($solutionWorkbooksFolder, '', 'OrdinalIgnoreCase') }
    $huntingQueriesFolderResult = $filesList -match ([regex]::Escape($solutionHuntingQueriesFolder)) | ForEach-Object { $_.replace( $solutionHuntingQueriesFolder, '', 'OrdinalIgnoreCase') }
    $analyticRulesFolderResult = $filesList -match ([regex]::Escape($solutionAnalyticRulesFolder)) | ForEach-Object { $_.replace($solutionAnalyticRulesFolder, '', 'OrdinalIgnoreCase') }

    $watchlistsFolderResult = $filesList -match ([regex]::Escape($solutionWatchlistsFolder)) | ForEach-Object { $_.replace($solutionWatchlistsFolder, '', 'OrdinalIgnoreCase') }
    $watchlistInWorkbooksFolderResult = $filesList -match ([regex]::Escape($solutionWatchlistInWorkbookFolder)) | ForEach-Object { $_.replace($solutionWatchlistInWorkbookFolder, '', 'OrdinalIgnoreCase') }

    if ($null -ne $watchlistsFolderResult) {
        $watchlistsFolderResult = GetValidWatchlistFileNames($watchlistsFolderResult)
    }

    if ($null -ne $watchlistInWorkbooksFolderResult) {
        $watchlistInWorkbooksFolderResult = GetValidWatchlistFileNames($watchlistInWorkbooksFolderResult)
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

    $dataConnectorFolderName = 'Data Connectors'
    if ($dataConnectorsFolderResultLength -gt 0) {
        $dataConnectorFolderName = 'DataConnectors'
        $newDataConnectorFiles = @()
        $newDataConnectorFiles = GetOnlyFileNames -filePaths $dataConnectorsFolderResult -folderNameWithSlash "DataConnectors/"

        $dataConnectorFilesResultArray = GetValidDataConnectorFileNames($newDataConnectorFiles) | ConvertTo-Json -AsArray
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
    elseif ($dataConnectorsWithSpaceFolderResultLength -gt 0) {
        $newDataConnectorFiles = @()
        $dataConnectorDataPaths = $dataFileContentObject."Data Connectors"
        Write-Host "dataConnectorDataPaths is $dataConnectorDataPaths"
        if ($null -eq $dataConnectorDataPaths -or $dataConnectorDataPaths -eq '') {
            $newDataConnectorFiles = GetOnlyFileNames -filePaths $dataConnectorsWithSpaceFolderResult -folderNameWithSlash "Data Connectors/"
        }
        else {
            $newDataConnectorFiles = GetOnlyFileNames -filePaths $dataConnectorDataPaths -folderNameWithSlash "Data Connectors/"
        }
        
        $dataConnectorFilesWithSpaceFolderResultArray = GetValidDataConnectorFileNames($newDataConnectorFiles) | ConvertTo-Json -AsArray
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
            $dataFileDataConnectorList = GetGivenFilesPathNames($dataFileContentObject.DataConnectors) | ConvertTo-Json -AsArray
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
                $dataFileparsersList = GetGivenFilesPathNames($dataFileContentObject.parsers) | ConvertTo-Json -AsArray
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
    
        $playbooksFolderHasFunctionAppsInPlaybooksFolder = $filesList -like "Solutions/$solutionName/Playbooks/*FunctionApp*"
        if ($playbooksFolderHasFunctionAppsInPlaybooksFolder -ne $false -and $playbooksFolderHasFunctionAppsInPlaybooksFolder.Count -gt 0) {
            $playbooksFunctionAppFiles += GetPlaybooksJsonFileNames($playbooksFolderHasFunctionAppsInPlaybooksFolder)
    
            if ($playbooksFunctionAppFiles -gt 0)
            {
                $playbooksFunctionAppFiles = $playbooksFunctionAppFiles | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
            }
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
    
            if ($playbooksFolderHasFunctionAppsInSolutionsFolder -gt 0 -and $filteredPlaybookFunctionApps -gt 0)
            {
                $playbooksFolderHasFunctionAppsInSolutionsFolder = @()
                $playbooksFolderHasFunctionAppsInSolutionsFolder += $filteredPlaybookFunctionApps
    
                $playbooksFunctionAppFilesInSolutionsFolder = GetPlaybooksJsonFileNames($playbooksFolderHasFunctionAppsInSolutionsFolder)
    
                if ($playbooksFunctionAppFilesInSolutionsFolder.Count -gt 0)
                {
                    $filteredPlaybooksFunctionAppFiles = $playbooksFunctionAppFilesInSolutionsFolder | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }

                    if ($filteredPlaybooksFunctionAppFiles.Count -gt 0)
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
    
        $linkedTemplate = @()
        foreach ($item in $playbooksFolderResult)
        {
            $filePath = $baseFolderPath + $item
            $fileContentObj = Get-Content "$filePath" | ConvertFrom-Json
            if ($null -ne $fileContentObj) {
                foreach ($resource in $fileContentObj.resources) {
                    if ($resource.type -eq "Microsoft.Resources/deployments") {
                        # ignore individual file of azure deploy inside of playbooks folder
                        $linkedTemplate += $item
                        break;
                    }
                }
            }
        }
    
        if ($linkedTemplate.Count -gt 0)
        {
            $playbooksFolderResult = $playbooksFolderResult | Where-Object { $_ -notlike "*$linkedTemplate" } 
        }
    
        $playbooksFolderResult = $playbooksFolderResult | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
    
        #======================================
        #check if folder with *Connector Name present inside of Solutions folder or in playbooks folder eg: Check Point or Cisco ISE solution 
        $filterPath = "$solutionFolderPath" + "*Connector/*"
        $playbooksDynamicCustomConnector = $filesList -like ($filterPath) | Where-Object {$_ -notlike '*/Data Connectors/*'} | Where-Object {$_ -notlike '*/DataConnectors/*'}
    
        if ($playbooksDynamicCustomConnector -ne $false -and $playbooksDynamicCustomConnector.Count -gt 0)
        {
            # it has custom connector playbooks 
            $playbooksDynamicCustomConnector = GetPlaybooksJsonFileNames($playbooksDynamicCustomConnector)
    
            if ($playbooksDynamicCustomConnector -gt 0)
            {
                $linkedTemplate = @()
                # CHECK IF WE HAVE ANY TEMPLATELINK AND IF YES THEN SKIP IT
                foreach ($item in $playbooksDynamicCustomConnector)
                {
                    $filePath = $baseFolderPath + $item
                    $fileContentObj = Get-Content "$filePath" | ConvertFrom-Json
                    if ($null -ne $fileContentObj) {
                        foreach ($resource in $fileContentObj.resources) {
                            if ($resource.type -eq "Microsoft.Resources/deployments") {
                                # ignore individual file of azure deploy inside of playbooks folder
                                $linkedTemplate += $item
                                break;
                            }
                        }
                    }
                }
    
                if ($linkedTemplate.Count -gt 0)
                {
                    #REMOVE LINKED TEMPLATE
                    $playbooksDynamicCustomConnector = $playbooksDynamicCustomConnector | Where-Object { $_ -notlike "*$linkedTemplate" }
                }
            }
        }
        $playbooksFinalDynamicCustomConnectorCount = $playbooksDynamicCustomConnector.Count
    
        #check if custom connector folder is present in root of solutions folder
        $playbookCustomConnectorFolderInRoot = "$solutionFolderPath" + "CustomConnector/"
        $playbookCustomConnectorFolderInRootFiles = $filesList -match ([regex]::Escape($playbookCustomConnectorFolderInRoot)) | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
    
        if ($playbookCustomConnectorFolderInRootFiles.Count -gt 0) {
            # BELOW LINE IS TO JUST GET JSON FILES AND EXCLUDE OTHER TYPE OF FILES.
            $playbookCustomConnectorFolderInRootFiles = GetPlaybooksJsonFileNames($playbookCustomConnectorFolderInRootFiles)
        }
        $playbookCustomConnectorFolderInRootCount = $playbookCustomConnectorFolderInRootFiles.Count
    
        #check if custom connector folder is present in solutions playbook folder
        $playbookCustomConnectorFolderInSolution = "$solutionFolderPath" + "Playbooks/CustomConnector/"
        $playbookCustomConnectorFolderInSolutionFiles = $filesList -match ([regex]::Escape($playbookCustomConnectorFolderInSolution)) | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
        if ($playbookCustomConnectorFolderInSolutionFiles.Count -gt 0) {
            # BELOW LINE IS TO JUST GET JSON FILES AND EXCLUDE OTHER TYPE OF FILES.
            $playbookCustomConnectorFolderInSolutionFiles = GetPlaybooksJsonFileNames($playbookCustomConnectorFolderInSolutionFiles)
        }
        $playbookCustomConnectorFolderInSolutionCount = $playbookCustomConnectorFolderInSolutionFiles.Count
    
        #check if connector folder is present in root of solutions folder
        $playbookConnectorFolderInRoot = "$solutionFolderPath" + "Connector/"
        $playbookConnectorFolderInRootFiles = $filesList -match ([regex]::Escape($playbookConnectorFolderInRoot)) | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
        if ($playbookConnectorFolderInRootFiles.Count -gt 0) {
            # BELOW LINE IS TO JUST GET JSON FILES AND EXCLUDE OTHER TYPE OF FILES.
            $playbookConnectorFolderInRootFiles = GetPlaybooksJsonFileNames($playbookConnectorFolderInRootFiles)
        }
        $playbookConnectorFolderInRootCount = $playbookConnectorFolderInRootFiles.Count
    
        #check if connector folder is present in solutions playbook folder
        $playbookConnectorFolderInSolution = "$solutionFolderPath" + "Playbooks/Connector/"
        $playbookConnectorFolderInSolutionFiles = $filesList -match ([regex]::Escape($playbookConnectorFolderInSolution)) | ForEach-Object { $_.replace("$solutionFolderPath", '', 'OrdinalIgnoreCase') }
        if ($playbookConnectorFolderInSolutionFiles.Count -gt 0) {
            # BELOW LINE IS TO JUST GET JSON FILES AND EXCLUDE OTHER TYPE OF FILES.
            $playbookConnectorFolderInSolutionFiles = GetPlaybooksJsonFileNames($playbookConnectorFolderInSolutionFiles)
        }
        $playbookConnectorFolderInSolutionCount = $playbookConnectorFolderInSolutionFiles.Count
    
        $formulatePlaybooksList = @();
        $hasCustomPlaybook = $false;
    
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
                    $playbookCustomConnectorFolderInRootFilesFirstFile = GetPlaybooksJsonFileNames($playbookCustomConnectorFolderInRootFiles) | Select-Object -first 1
                    $formulatePlaybooksList += "$playbookCustomConnectorFolderInRootFilesFirstFile"
                }
            }
            elseif ($playbookConnectorFolderInRootCount -gt 0) {
                # ADD CUSTOM PLAYBOOK FIRST AND THEN ADD OTHER PLAYBOOK FILES - WITHIN SOLUTION FOLDER, BUT OUTSIDE OF PLAYBOOKS FOLDER IN Connector
                if ($playbookConnectorFolderInRootCount -eq 1) {
                    $formulatePlaybooksList += "$playbookConnectorFolderInRootFiles"
                }
                else {
                    $playbookConnectorFolderInRootFilesFirstFile = GetPlaybooksJsonFileNames($playbookConnectorFolderInRootFiles) | Select-Object -first 1
                    $formulatePlaybooksList += $playbookConnectorFolderInRootFilesFirstFile
                }
            }
            elseif ($playbookCustomConnectorFolderInSolutionCount -gt 0) {
                # ADD CUSTOM PLAYBOOK FIRST AND THEN ADD OTHER PLAYBOOK FILES - WITHIN SOLUTION FOLDER, BUT INSIDE OF PLAYBOOKS FOLDER IN CustomConnector
                if ($playbookCustomConnectorFolderInSolutionCount -eq 1) {
                    $formulatePlaybooksList += "$playbookCustomConnectorFolderInSolutionFiles"
                }
                else {
                    $playbookCustomConnectorFolderInSolutionFilesFirstFile = GetPlaybooksJsonFileNames($playbookCustomConnectorFolderInSolutionFiles) | Select-Object -first 1
                    $formulatePlaybooksList += $playbookCustomConnectorFolderInSolutionFilesFirstFile
                }
            }
            elseif ($playbookConnectorFolderInSolutionCount -gt 0) {
                if ($playbookConnectorFolderInSolutionCount -eq 1) {
                    $formulatePlaybooksList += "$playbookConnectorFolderInSolutionFiles"
                }
                else {
                    $playbookConnectorFolderInSolutionFilesFirstFile = GetPlaybooksJsonFileNames($playbookConnectorFolderInSolutionFiles) | Select-Object -first 1
                    $formulatePlaybooksList += $playbookConnectorFolderInSolutionFilesFirstFile
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

        $workbookFiles = GetWorkbooksJsonFileNames($workbooksFolderResult)

        $workbooksFolderResultArray = $workbookFiles | ConvertTo-Json -AsArray

        if (!$workbooksArrayAttributeExist) {
            $dataFileContentObject | ForEach-Object {
                $_ | Add-Member -MemberType NoteProperty -Name 'Workbooks' -Value $workbooksFolderResultArray -PassThru
            }
        } 
        else {
            if ($dataFileContentObject.Workbooks.Count -gt 0) {
                $newWorkbookFiles = @()
                $newWorkbookFiles = GetOnlyFileNames -filePaths $dataFileContentObject.Workbooks -folderNameWithSlash "Workbooks/"

                $dataFileworkbooksList = GetWorkbooksJsonFileNames($newWorkbookFiles) | ConvertTo-Json -AsArray
                $dataFileContentObject.PSObject.Properties.Remove('Workbooks')
                $datafilecontentobject | foreach-object {
                    $_ | add-member -membertype noteproperty -name 'Workbooks' -value $dataFileworkbooksList -passthru
                }
            }
            else { $dataFileContentObject.PSObject.Properties.Remove('Workbooks') }
        }
    }

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
                $dataFileanalyticRulesList = GetGivenFilesPathNames($dataFileContentObject.'Analytic Rules') | ConvertTo-Json -AsArray
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
                $dataFilehuntingList = GetGivenFilesPathNames($dataFileContentObject.'Hunting Queries') | ConvertTo-Json -AsArray
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
            else {
                if ($dataFileContentObject.Watchlists.Count -gt 0) {
                    $dataFileWatchListList = GetValidWatchlistFileNames($watchlistFolderResultArray)
                    $dataFileContentObject.PSObject.Properties.Remove('Watchlists')
                    $datafilecontentobject | foreach-object {
                        $_ | add-member -membertype noteproperty -name 'Watchlists' -value $dataFileWatchListList -passthru
                    }
                }
                else { 
                    $dataFileContentObject.PSObject.Properties.Remove('Watchlists') 
                }
            }
        }
    }
    #===================End: Watchlist code================

    $jsonDataFile = $dataFileContentObject | ConvertTo-Json
    $jsonDataFile.replace("'", "''") # replace single quote with double
    Write-Host "Calculated Json data file $jsonDataFile"

    # UPDATE DATA FILE WITH NEW JSON CONTENT
    Write-Host "Updating data input file $dataFolderFile"
    Set-Content -Path $dataFilePath -Value $jsonDataFile

    foreach ($property in $dataFileContentObject.PSObject.Properties) {
        if ($property.Name.ToLower() -eq 'watchlists' -or 
            $property.Name.ToLower() -eq 'watchlist' -or 
            $property.Name -eq 'Hunting Queries' -or 
            $property.Name -eq 'Analytic Rules' -or 
            $property.Name.ToLower() -eq 'playbooks' -or 
            $property.Name.ToLower() -eq 'workbooks' -or 
            $property.Name.ToLower() -eq 'parsers' -or 
            $property.Name.ToLower() -eq 'dataconnectors' -or 
            $property.Name.ToLower() -eq 'data connectors') {
            $gg = $property.Value.GetType()
            $pp = $property.Name
            Write-Host "type is $gg , $pp"
            if ($property.Value.GetType().FullName -eq 'System.String') {
                $customProperties[$property.Name] = $property.Value | ConvertFrom-Json
            }
            else {
                $customProperties[$property.Name] = $property.Value
            }
        }
    }

    Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Package-generator : Data Input File Prepared dynamic, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
    Write-Host "Now going to execute createSolutionV4 file"

    ./Tools/Create-Azure-Sentinel-Solution/pipeline/createSolutionV4.ps1 $baseFolderPath $solutionName $dataFileContentObject $dataFolderFile $dataConnectorFolderName $dataFolderActualName $instrumentationKey $pullRequestNumber $runId $packageVersion $defaultPackageVersion $isWatchListInsideOfWorkbooksFolder

    $packageCreationPath = "" + $baseFolderPath + "Solutions/" + $solutionName + "/Package/"
    $allFilesInCreatedPackage = Get-ChildItem $packageCreationPath 
    $allFilesInCreatedPackageCount = $allFilesInCreatedPackage.Count
    $blobName = "" + $solutionName + "_" + $pullRequestNumber + "_" + $packageVersion
    Write-Host "Blob name is $blobName"
    Write-Host "Package Files List are : $allFilesInCreatedPackage"
    Write-Host "Package Files Count $allFilesInCreatedPackageCount"

    Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Package-generator : Total Files created in package : $allFilesInCreatedPackageCount with file names : $allFilesInCreatedPackage , Job Run Id : $runId" -Severity Information -CustomProperties $customProperties

    $solutionBaseFolderPath = "Solutions/" + $solutionName + "/Package"

    if ($allFilesInCreatedPackageCount -gt 0) {
        Write-Output "isCreatePackage=$true" >> $env:GITHUB_OUTPUT
        Write-Output "solutionBaseFolderPath=$solutionBaseFolderPath" >> $env:GITHUB_OUTPUT
        Write-Output "packageCreationPath=$packageCreationPath" >> $env:GITHUB_OUTPUT
        Write-Output "packageVersion=$packageVersion" >> $env:GITHUB_OUTPUT
        Write-Output "blobName=$blobName" >> $env:GITHUB_OUTPUT
        Write-Output "dataFileLink=$dataFileLink" >> $env:GITHUB_OUTPUT
        Write-Output "dataFolderPath=$dataFolderPath" >> $env:GITHUB_OUTPUT
        Write-Output "dataInputFileName=$dataFolderFile" >> $env:GITHUB_OUTPUT 

        Write-Host "Package created successfully!"
    }
    else {
        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Package-generator : Total Files created in package : 0, Job Run Id : $runId" -Severity Warning -CustomProperties $customProperties

        Write-Output "::error::Package creation for Solution '$solutionName' Failed with an error" 
        ErrorOutput
    }
}
catch {
    $errorDetails = $_
    $errorInfo = $_.Exception
    Write-Output "Error Details $errorDetails , Error Info $errorInfo"
    
    Write-Host "Package-generator: Error occured in catch block!"
    Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId' = "$runId"; 'SolutionName' = "$solutionName"; 'PullRequestNumber' = "$pullRequestNumber"; 'ErrorDetails' = "Package-generator : Error occured in catch block: $_"; 'EventName' = "Package Generator"; 'SolutionOfferId' = "$solutionOfferId"; }
    ErrorOutput
}
