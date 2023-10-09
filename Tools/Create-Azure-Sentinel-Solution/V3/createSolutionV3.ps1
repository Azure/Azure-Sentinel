Write-Host '=======Starting Package Creation using V3 tool========='
$path = Read-Host "Enter solution data file path "
$defaultPackageVersion = "3.0.0" # for templateSpec this will be 2.0.0
Write-Host "Path $path, DefaultPackageVersion is $defaultPackageVersion"

if ($path.length -eq 0)
{
    # path is not provided so check first file from input folder
    $path = "$PSScriptRoot\input"

    $inputFile = $(Get-ChildItem $path)
    if ($inputFile.Count -gt 0)
    {
        $inputFile = $inputFile[0]
        $inputJsonPath = Join-Path -Path $path -ChildPath "$($inputFile.Name)"

        $contentToImport = Get-Content -Raw $inputJsonPath | Out-String | ConvertFrom-Json
        # BELOW LINE MAKES USE OF BASEPATH FROM DATA FILE AND ADDS DATA FOLDER NAME.
        $path = $contentToImport.BasePath + "/Data"
    }
    else {
        Write-Host "Path is not specified and also input folder doesnt have input file. Please make sure to have path specified or add file in side of V3/input folder!"
    }
}

$path = $path.Replace('\', '/')
$indexOfSolutions = $path.IndexOf('Solutions')

if ($indexOfSolutions -le 0) {
    Write-Host "Please provide data folder path from Solutions folder!"
    exit 1
}
else {
    $hasDataFolder = $path -like '*/data'
    if ($hasDataFolder) {
        # DATA FOLDER PRESENT
        $dataFolderIndex = $path.IndexOf("/data", [StringComparison]"CurrentCultureIgnoreCase")

        if ($dataFolderIndex -le 0) {
            Write-Host "Given path is not from Solutions data folders. Please provide data file path from Solution"
            exit 1
        }
        else {
            $dataFolderName = $path.Substring($dataFolderIndex + 1)
            $solutionName = $path.Substring($indexOfSolutions + 10, $dataFolderIndex - ($indexOfSolutions + 10))
            $solutionFolderBasePath = $path.Substring(0, $dataFolderIndex)

            # GET DATA FOLDER FILE NAME
            $excluded = @("parameters.json", "parameter.json", "system_generated_metadata.json")
            $dataFileName = Get-ChildItem -Path "$solutionFolderBasePath\$dataFolderName\" -recurse -exclude $excluded | ForEach-Object -Process { [System.IO.Path]::GetFileName($_) }

            if ($dataFileName.Length -le 0) {
                Write-Host "Data File not present in given folder path!"
                exit 1
            }
        }
    }
    else {
        Write-Host "Data File not present in given folder path!"
        exit 1
    }
}

$solutionBasePath = $path.Substring(0, $indexOfSolutions + 10)
$repositoryBasePath = $path.Substring(0, $indexOfSolutions)
Write-Host "SolutionBasePath is $solutionBasePath, Solution Name $solutionName" 

$isPipelineRun = $false

. "$repositoryBasePath/Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1" # load common functions
. "$repositoryBasePath.script/package-automation/catelogAPI.ps1"

try {
    foreach ($inputFile in $(Get-ChildItem -Path "$solutionFolderBasePath\$dataFolderName\$dataFileName")) {
        #$inputJsonPath = Join-Path -Path $path -ChildPath "$($inputFile.Name)"
        $contentToImport = Get-Content -Raw $inputFile | Out-String | ConvertFrom-Json

        $basePath = $(if ($solutionBasePath) { $solutionBasePath } else { "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/" })
        $metadataAuthor = $contentToImport.Author.Split(" - ");
        if ($null -ne $metadataAuthor[1]) {
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "email" -NotePropertyValue $($metadataAuthor[1])
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_email" -NotePropertyValue "[variables('email')]"
        }

        $solutionName = $contentToImport.Name
        #$metadataPath = "$PSScriptRoot/../../../Solutions/$($contentToImport.Name)/$($contentToImport.Metadata)"
        $metadataPath = $solutionBasePath + "$($contentToImport.Name)/$($contentToImport.Metadata)"

        $baseMetadata = Get-Content -Raw $metadataPath | Out-String | ConvertFrom-Json
        if ($null -eq $baseMetadata) {
            Write-Host "Please verify if the given path is correct and/or Solution folder name and Data file Name attribute value is correct!"
            exit 1
        }

        #================START: IDENTIFY PACKAGE VERSION=============
        $solutionOfferId = $baseMetadata.offerId
        $offerId = "$solutionOfferId"
        $offerDetails = GetCatelogDetails $offerId
        $userInputPackageVersion = $contentToImport.version
        $packageVersion = GetPackageVersion $defaultPackageVersion $offerId $offerDetails $true $userInputPackageVersion
        if ($packageVersion -ne $contentToImport.version) {
            $contentToImport.PSObject.Properties.Remove('version')
            $contentToImport | Add-Member -MemberType NoteProperty -Name 'version' -Value $packageVersion 
            Write-Host "Package version updated to $packageVersion"
        }

        $TemplateSpecAttribute = [bool]($contentToImport.PSobject.Properties.Name -match "TemplateSpec")
        if (!$TemplateSpecAttribute) {
            $contentToImport | Add-Member -MemberType NoteProperty -Name 'TemplateSpec' -Value $true
        }

        $major = $contentToImport.version.split(".")[0]
        if ($TemplateSpecAttribute -and $contentToImport.TemplateSpec -eq $false -and $major -gt 1) {
            $contentToImport.PSObject.Properties.Remove('TemplateSpec')
            $contentToImport | Add-Member -MemberType NoteProperty -Name 'TemplateSpec' -Value $true
        }
        #================START: IDENTIFY PACKAGE VERSION=============

        Write-Host "Package version identified is $packageVersion"

        if ($major -ge 3) {
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionName" -NotePropertyValue $solutionName
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionVersion" -NotePropertyValue $contentToImport.version
        }

        $metadataAuthor = $contentToImport.Author.Split(" - ");

        $global:solutionId = $baseMetadata.publisherId + "." + $baseMetadata.offerId
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "solutionId" -NotePropertyValue $global:solutionId
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionId" -NotePropertyValue "[variables('solutionId')]"
        
        # VERIFY IF IT IS A CONTENTSPEC OR CONTENTPACKAGE RESOURCE TYPE BY VERIFYING VERSION FROM  DATA FILE
        $contentResourceDetails = returnContentResources($contentToImport.Version)
        if ($null -eq $contentResourceDetails) {
            Write-Host "Not able to identify content resource details based on Version. Please verify if Version in data input file is correct!"
            exit 1;
        }

        foreach ($objectProperties in $contentToImport.PsObject.Properties) {
            if ($objectProperties.Value -is [System.Array]) {
                foreach ($file in $objectProperties.Value) {
                    $file = $file.Replace("$basePath/", "").Replace("Solutions/", "").Replace("$solutionName/", "") 
                    $finalPath = $basePath + $solutionName + "/" + $file
                    $rawData = $null
                    try {
                        Write-Host "Downloading $finalPath"
                        $rawData = (New-Object System.Net.WebClient).DownloadString($finalPath)
                    }
                    catch {
                        Write-Host "Failed to download $finalPath -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
                        break;
                    }

                    try {
                        $json = ConvertFrom-Json $rawData -ErrorAction Stop; # Determine whether content is JSON or YAML
                        $validJson = $true;
                    }
                    catch {
                        $validJson = $false;
                    }
                    
                    if ($validJson) {
                        # If valid JSON, must be Workbook or Playbook
                        $objectKeyLowercase = $objectProperties.Name.ToLower()
                        if ($objectKeyLowercase -eq "workbooks") {
                            GetWorkbookDataMetadata -file $file -isPipelineRun $isPipelineRun -contentResourceDetails $contentResourceDetails -baseFolderPath $repositoryBasePath -contentToImport $contentToImport
                        }
                        elseif ($objectKeyLowercase -eq "playbooks") {
                            GetPlaybookDataMetadata -file $file -contentToImport $contentToImport -contentResourceDetails $contentResourceDetails -json $json -isPipelineRun $isPipelineRun
                        }
                        elseif ($objectKeyLowercase -eq "data connectors" -or $objectKeyLowercase -eq "dataconnectors") {
                            GetDataConnectorMetadata -file $file -contentResourceDetails $contentResourceDetails
                        }
                        elseif ($objectKeyLowercase -eq "savedsearches") {
                            GenerateSavedSearches -json $json -contentResourceDetails $contentResourceDetails
                        }
                        elseif ($objectKeyLowercase -eq "watchlists") {
                            $watchListFileName = Get-ChildItem $finalPath

                            GenerateWatchList -json $json -isPipelineRun $isPipelineRun -watchListFileName $watchListFileName.BaseName
                        }
                    }
                    else {
                        if ($file -match "(\.yaml)$" -and $objectProperties.Name.ToLower() -ne "parsers") {
                            $objectKeyLowercase = $objectProperties.Name.ToLower()
                            if ($objectKeyLowercase -eq "hunting queries") {
                                GetHuntingDataMetadata -file $file -rawData $rawData -contentResourceDetails $contentResourceDetails
                            }
                            else {
                                GenerateAlertRule -file $file -contentResourceDetails $contentResourceDetails
                            }
                        }
                        else {
                            GenerateParsersList -file $file -contentToImport $contentToImport -contentResourceDetails $contentResourceDetails
                        }
                    }
                }
            }
            elseif ($objectProperties.Name.ToLower() -eq "metadata") {
                try {
                    $finalPath = $metadataPath
                    $rawData = $null
                    try {
                        Write-Host "Downloading $finalPath"
                        $rawData = (New-Object System.Net.WebClient).DownloadString($finalPath)
                    }
                    catch {
                        Write-Host "Failed to download $finalPath -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
                        break;
                    }
                        
                    try {
                        $json = ConvertFrom-Json $rawData -ErrorAction Stop; # Determine whether content is JSON or YAML
                        $validJson = $true;
                    }
                    catch {
                        $validJson = $false;
                    }
                    
                    if ($validJson -and $json) {
                        PrepareSolutionMetadata -solutionMetadataRawContent $json -contentResourceDetails $contentResourceDetails -defaultPackageVersion $defaultPackageVersion
                    }
                    else {
                        Write-Host "Failed to load Metadata file $file -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
                    }
                }
                catch {
                    Write-Host "Failed to load Metadata file $file -- Please ensure that the SolutionMetadata file exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
                    break;
                }
            }
        }
        
        $global:analyticRuleCounter -= 1
		$global:workbookCounter -= 1
		$global:playbookCounter -= 1
		$global:connectorCounter -= 1
		$global:parserCounter -= 1
		$global:huntingQueryCounter -= 1
		$global:watchlistCounter -= 1
		updateDescriptionCount $global:connectorCounter                                "**Data Connectors:** "                     "{{DataConnectorCount}}"            $(checkResourceCounts $global:parserCounter, $global:analyticRuleCounter, $global:workbookCounter, $global:playbookCounter, $global:huntingQueryCounter, $global:watchlistCounter)
		updateDescriptionCount $global:parserCounter                                   "**Parsers:** "                             "{{ParserCount}}"                   $(checkResourceCounts $global:analyticRuleCounter, $global:workbookCounter, $global:playbookCounter, $global:huntingQueryCounter, $global:watchlistCounter)
		updateDescriptionCount $global:workbookCounter                                 "**Workbooks:** "                           "{{WorkbookCount}}"                 $(checkResourceCounts $global:analyticRuleCounter, $global:playbookCounter, $global:huntingQueryCounter, $global:watchlistCounter)
		updateDescriptionCount $global:analyticRuleCounter                             "**Analytic Rules:** "                      "{{AnalyticRuleCount}}"             $(checkResourceCounts $global:playbookCounter, $global:huntingQueryCounter, $global:watchlistCounter)
		updateDescriptionCount $global:huntingQueryCounter                             "**Hunting Queries:** "                     "{{HuntingQueryCount}}"             $(checkResourceCounts $global:playbookCounter, $global:watchlistCounter)
		updateDescriptionCount $global:watchlistCounter                                "**Watchlists:** "                          "{{WatchlistCount}}"                $(checkResourceCounts @($global:playbookCounter))
		updateDescriptionCount $global:customConnectorsList.Count                      "**Custom Azure Logic Apps Connectors:** "  "{{LogicAppCustomConnectorCount}}"  $(checkResourceCounts @($global:playbookCounter))
		updateDescriptionCount $global:functionAppList.Count                           "**Function Apps:** "                       "{{FunctionAppsCount}}"             $(checkResourceCounts @($global:playbookCounter))
        updateDescriptionCount ($global:playbookCounter - $global:customConnectorsList.Count - $global:functionAppList.Count)  "**Playbooks:** "   "{{PlaybookCount}}"       $false

        GeneratePackage -solutionName $solutionName -contentToImport $contentToImport -calculatedBuildPipelinePackageVersion $contentToImport.Version;
        RunArmTtkOnPackage -solutionName $solutionName -isPipelineRun $false;
    }
}
catch {
    Write-Host "Error occured in catch of createSolutionV3 file Error details are $_"
}