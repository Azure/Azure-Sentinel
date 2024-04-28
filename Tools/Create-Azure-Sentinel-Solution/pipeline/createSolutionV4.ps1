# this is only for build pipeline not for local use
param ($pipelineBasePath, $pipelineSolutionName, $pipelineDataFileRawContent, $dataFileName, $dataConnectorFolderName, $dataFolderActualName, $instrumentationKey, $pullRequestNumber, $runId, $calculatedPackageVersion, $defaultPackageVersion, $isWatchListInsideOfWorkbooksFolder = $false)
. ./Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1 # load common functions
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1 # load log analytics functions
. ./Tools/Create-Azure-Sentinel-Solution/common/get-ccp-details.ps1 # load ccp functions

try 
{
	$isPipelineRun = $true
	Write-Host "Running for Build Pipeline"
	Write-Host "Data File Content is $pipelineDataFileRawContent"

	$customProperties = @{ 'SolutionName'="$pipelineSolutionName"; 'DataFileName'="$dataFileName"; 'RunId'="$runId"; 'PullRequestNumber'="$pullRequestNumber" }
	Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "CreateSolutionV4" -CustomProperties $customProperties
	Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CreateSolutionV4: Starting execution for Solution $pipelineSolutionName." -Severity Information -CustomProperties $customProperties

	$path = ("" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/" + $dataFolderActualName + "/" + $dataFileName + "")
	$solutionFolderBasePath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName;
	
	foreach ($inputFile in $(Get-ChildItem $path)) {
		$contentToImport = $pipelineDataFileRawContent
		$basePath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/"

		$solutionName = $pipelineSolutionName 
		$baseMetadata = $pipelineDataFileRawContent
		$metadataCounter = 0
		$global:solutionId = $baseMetadata.publisherId + "." + $baseMetadata.offerId
		$global:baseMainTemplate.variables | Add-Member -NotePropertyName "solutionId" -NotePropertyValue "$global:solutionId"
		$global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionId" -NotePropertyValue "[variables('solutionId')]"
		
		$metadataAuthor = $contentToImport.Author.Split(" - ");
		if($null -ne $metadataAuthor[1])
		{
			$global:baseMainTemplate.variables | Add-Member -NotePropertyName "email" -NotePropertyValue $($metadataAuthor[1])
			$global:baseMainTemplate.variables | Add-Member -NotePropertyName "_email" -NotePropertyValue "[variables('email')]"
		}

		$major = $contentToImport.version.split(".")[0]
		if ($major -ge 3)
		{
			$global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionName" -NotePropertyValue $solutionName
			$global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionVersion" -NotePropertyValue $contentToImport.version
		}

		Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CreateSolutionV4: Inside of Powershell Foreach for Solution $pipelineSolutionName." -Severity Information -CustomProperties $customProperties

		# VERIFY IF IT IS A CONTENTSPEC OR CONTENTPACKAGE RESOURCE TYPE BY VERIFYING VERSION FROM  DATA FILE
		$contentResourceDetails = returnContentResources($calculatedPackageVersion) #($contentToImport.Version)
		if ($null -eq $contentResourceDetails)
		{
			Write-Host "Not able to identify content resource details based on Version. Please verify if Version in data input file is correct!"
			return;
		}

		$ccpDict = @();
		$ccpTablesFilePaths = @()
		$ccpTablesCounter = 1; 
    $isCCPConnector = $false;
		foreach ($objectProperties in $contentToImport.PsObject.Properties) 
		{
			# Access the value of the property
				if ($objectProperties.Name.ToLower() -eq "name" -or 
					$objectProperties.Name.ToLower() -eq "author" -or
					$objectProperties.Name.ToLower() -eq "logo" -or
					$objectProperties.Name.ToLower() -eq "description" -or
					$objectProperties.Name.ToLower() -eq "basepath" -or
					$objectProperties.Name.ToLower() -eq "version" -or
					$objectProperties.Name.ToLower() -eq "metadata" -or
					$objectProperties.Name.ToLower() -eq "templatespec" -or
					$objectProperties.Name.ToLower() -eq "is1pconnector" -or
					$objectProperties.Name.ToLower() -eq "createpackage")
				{
					continue;
				}
				elseif (
				$objectProperties.Name.ToLower() -eq "parsers" -or
				$objectProperties.Name.ToLower() -eq "data connectors" -or
				$objectProperties.Name.ToLower() -eq "dataconnectors" -or
				$objectProperties.Name.ToLower() -eq "playbooks" -or
				$objectProperties.Name.ToLower() -eq "workbooks" -or
				$objectProperties.Name.ToLower() -eq "analytic rules" -or
				$objectProperties.Name.ToLower() -eq "hunting queries" -or
				$objectProperties.Name.ToLower() -eq "watchlists")
				{
					$currentRunningPropertyName = $objectProperties.Name.ToLower()
					$propertyValue = $objectProperties.Value
					Write-Host "currentRunningPropertyName $currentRunningPropertyName , property Value is $propertyValue"
					$customProperties = @{ 'SolutionName'="$pipelineSolutionName";'DataFileName'="$dataFileName"; 'RunId'="$runId"; 'PullRequestNumber'="$pullRequestNumber"; 'CurrentRunningPropertyName'="$currentRunningPropertyName"; 'CurrentRunningPropertyValue'="$propertyValue"}

					Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CreateSolutionV4: For Solution $pipelineSolutionName, currentRunningPropertyName is $currentRunningPropertyName" -Severity Information -CustomProperties $customProperties

					if ($propertyValue.GetType().FullName -eq "System.String")
					{
						try {
							$filesList = $propertyValue | ConvertFrom-Json
						}
						catch {
							$filesList = $propertyValue
						}
					}
					else 
					{
						$filesList = $propertyValue
					}

					# =============start: ccp connector code===============
					$solutionBasePath = ($pipelineBasePath + "/Solutions/").Replace("//", "/");

					$solutionMetadataPath = $solutionBasePath + "$($pipelineDataFileRawContent.Name)/$($pipelineDataFileRawContent.Metadata)"
					$solutionBaseMetadata = Get-Content -Raw $solutionMetadataPath | Out-String | ConvertFrom-Json
					if ($null -eq $solutionBaseMetadata) {
							Write-Host "Please verify if the given path $solutionMetadataPath is correct and/or Solution folder name and Data file Name attribute value is correct!"
							exit 1
					}

					if ($isCCPConnector -eq $false) {            
            [array]$ccpDict = Get-CCP-Dict -dataFileMetadata $pipelineDataFileRawContent -baseFolderPath $solutionBasePath -solutionName $solutionName -DCFolderName $dataConnectorFolderName

            if ($null -ne $ccpDict -and $ccpDict.count -gt 0) {
							$isCCPConnector = $true
							[array]$ccpTablesFilePaths = GetCCPTableFilePaths -existingCCPDict $ccpDict -baseFolderPath $solutionBasePath -solutionName $solutionName -DCFolderName $dataConnectorFolderName
						}
					}
					Write-Host "isCCPConnector $isCCPConnector"
					$ccpConnectorCodeExecutionCounter = 1;
					# =============end: ccp connector code===============

					foreach ($file in $filesList) 
					{
						$fileExtension = $file -split '\.' | Select-Object -Last 1
						Write-Host "Current file is $file, File extension is $fileExtension"

						if ($objectProperties.Name.ToLower() -eq "parsers") {
							$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/Parsers/" + $file.Replace("Parsers/", "")
						} elseif ($objectProperties.Name.ToLower() -eq "data connectors" -or $objectProperties.Name.ToLower() -eq "dataconnectors")
						{
							$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/" + $dataConnectorFolderName+ "/" + $file.Replace("$dataConnectorFolderName/", "")
						}
						elseif ($objectProperties.Name.ToLower() -eq "playbooks") {
							if ($file.Contains("Solutions/$solutionName/"))
							{
								$file = $file.replace("Solutions/$solutionName/", '')
							}
							$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/" + $file

							#$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/Playbooks/" + $file
						}
						elseif ($objectProperties.Name.ToLower() -eq "workbooks") {
							$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/Workbooks/" + $file.Replace("Workbooks/", "")
						}
						elseif ($objectProperties.Name.ToLower() -eq "analytic rules") {
							$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/Analytic Rules/" + $file.Replace("Analytic Rules/", "")
						}
						elseif ($objectProperties.Name.ToLower() -eq "hunting queries") {
							$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/Hunting Queries/" + $file.Replace("Hunting Queries/", "")
						}
						elseif ($objectProperties.Name.ToLower() -eq "watchlists") {
							if ($isWatchListInsideOfWorkbooksFolder)
							{
								$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/Workbooks/Watchlists/" + $file.Replace("Watchlists/", "")
							}
							else {
								$finalPath = "" + $pipelineBasePath + "Solutions/" + $pipelineSolutionName + "/Watchlists/" + $file.Replace("Watchlists/", "")
							}
						}
						
						$finalPath = $finalPath.Replace("//", "/")
						Write-Host "Final Path is $finalPath"
						$rawData = $null
						Send-AppInsightsTraceTelemetry -InstrumentationKey "$instrumentationKey" -Message "CreateSolutionV4: For Solution $pipelineSolutionName, Current file path is $finalPath" -Severity Information -CustomProperties $customProperties

						try {
							Write-Host "Downloading $finalPath"

							$isFilePathPresent = Test-Path -Path "$finalPath"
							Write-Host "Is $finalPath file path present $isFilePathPresent"
							if ($isFilePathPresent) {
								$rawData = (New-Object System.Net.WebClient).DownloadString($finalPath)
							}
							else {
								if ($fileExtension -eq "json" -or $fileExtension -eq "JSON") {
									Write-Host "FinalPath $finalPath not found!"
									if ($fileExtension -eq "json") {
										$finalPath = $finalPath.Replace(".json", ".JSON")
									} else {
										$finalPath = $finalPath.Replace(".JSON", ".json")
									}
									Write-Host "Updated FinalPath is $finalPath"
									$rawData = (New-Object System.Net.WebClient).DownloadString($finalPath)
								}
							}
						}
						catch {
							Write-Host "Failed to download $finalPath -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
							Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; 'ErrorDetails'="CreateSolutionV4 : Error occured in catch block: $_"; 'EventName'="CreateSolutionV4" }
							exit 1;
						}

						try {
							$json = ConvertFrom-Json $rawData -ErrorAction Stop; # Determine whether content is JSON or YAML
							$validJson = $true;
						}
						catch {
							$validJson = $false;
						}
						
						if ($validJson) 
						{
							# If valid JSON, must be Workbook or Playbook
							$objectKeyLowercase = $objectProperties.Name.ToLower()
							if ($objectKeyLowercase -eq "workbooks") {
								GetWorkbookDataMetadata -file $file -isPipelineRun $isPipelineRun -contentResourceDetails $contentResourceDetails -baseFolderPath $pipelineBasePath -contentToImport $contentToImport
							}
							elseif ($objectKeyLowercase -eq "playbooks") {
								GetPlaybookDataMetadata -file $file -contentToImport $contentToImport -contentResourceDetails $contentResourceDetails -json $json -isPipelineRun $true
							}
							elseif ($objectKeyLowercase -eq "data connectors" -or $objectKeyLowercase -eq "dataconnectors") {

								if ($ccpDict.Count -gt 0) {
									$isCCPConnectorFile = $false;
									foreach($item in $ccpDict) {
											if ($item.DCDefinitionFullPath -eq $finalPath) {
													$isCCPConnectorFile = $true
													break;
											}
									}

									if ($isCCPConnectorFile -and $ccpConnectorCodeExecutionCounter -eq 1) {
											# current file is a ccp connector
											GetDataConnectorMetadata -file $file -contentResourceDetails $contentResourceDetails -dataFileMetadata $pipelineDataFileRawContent -solutionFileMetadata $solutionBaseMetadata -dcFolderName $dataConnectorFolderName -ccpDict $ccpDict -solutionBasePath $solutionBasePath -solutionName $solutionName -ccpTables $ccpTablesFilePaths -ccpTablesCounter $ccpTablesCounter
									} 
									elseif ($isCCPConnectorFile -and $ccpConnectorCodeExecutionCounter -gt 1) {
										continue;
									}
									else {
											# current file is a normal connector
											GetDataConnectorMetadata -file $file -contentResourceDetails $contentResourceDetails -dataFileMetadata $pipelineDataFileRawContent -solutionFileMetadata $solutionBaseMetadata -dcFolderName $dataConnectorFolderName -ccpDict $null -solutionBasePath $solutionBasePath -solutionName $solutionName -ccpTables $null -ccpTablesCounter $ccpTablesCounter
									}
								}
								else {
									GetDataConnectorMetadata -file $file -contentResourceDetails $contentResourceDetails -dataFileMetadata $pipelineDataFileRawContent -solutionFileMetadata $solutionBaseMetadata -dcFolderName $dataConnectorFolderName -ccpDict $null -solutionBasePath $solutionBasePath -solutionName $solutionName -ccpTables $null -ccpTablesCounter $ccpTablesCounter
								}
							}
							elseif ($objectKeyLowercase -eq "savedsearches") {
								GenerateSavedSearches -json $json -contentResourceDetails $contentResourceDetails
							}
							elseif ($objectKeyLowercase -eq "watchlists") {
								$watchListFileName = Get-ChildItem $finalPath

								GenerateWatchList -json $json -isPipelineRun $isPipelineRun -watchListFileName $watchListFileName.BaseName
							}
						}
						else
						{
							if ($file -match "(\.yaml)$" -and $objectKeyLowercase -ne "parsers" -and $currentRunningPropertyName -ne "parsers") {
								$objectKeyLowercase = $objectProperties.Name.ToLower()
								if ($objectKeyLowercase -eq "hunting queries") {
									GetHuntingDataMetadata -file $file -rawData $rawData -contentResourceDetails $contentResourceDetails
								}
								else {
									GenerateAlertRule -file $file -contentResourceDetails $contentResourceDetails
								}
							}
							else 
							{
								GenerateParsersList -file $file -contentToImport $contentToImport -contentResourceDetails $contentResourceDetails
							}
						}
						
					} # end of for each look 'foreach ($file in $filesList)'
				}
		}

		foreach($objectProperties in $contentToImport.PsObject.Properties)
		{
			if (($objectProperties.Name.ToLower() -eq "publisherid" -or 
				$objectProperties.Name.ToLower() -eq "offerid" -or
				$objectProperties.Name.ToLower() -eq "firstpublishdate" -or
				$objectProperties.Name.ToLower() -eq "providers" -or
				$objectProperties.Name.ToLower() -eq "categories" -or
				$objectProperties.Name.ToLower() -eq "support" -or
				$objectProperties.Name.ToLower() -eq "metadata")) 
			{
				if ($metadataCounter -eq 1)
				{
					break;
				}

				$metadataCounter = 1
				$rawData = $null
				$json = $pipelineDataFileRawContent
				$validJson = $true;

				PrepareSolutionMetadata -solutionMetadataRawContent $json -contentResourceDetails $contentResourceDetails -defaultPackageVersion $defaultPackageVersion
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
        updateDescriptionCount ($global:playbookCounter - $global:customConnectorsList.Count - $global:functionAppList.Count)  "**Playbooks:** "  "{{PlaybookCount}}"  $false

		GeneratePackage -solutionName $solutionName -contentToImport $contentToImport -calculatedBuildPipelinePackageVersion $calculatedPackageVersion;
		Write-Host "Package Generated Successfully!!"

		# check if mainTemplate and createUiDefinition json files are valid or not
		$solutionFolderBasePath = ($pipelineBasePath + "/" + "Solutions/" + $pipelineSolutionName).Replace("//", "/")
		CheckJsonIsValid($solutionFolderBasePath)
	}
}
catch {
	$errorDetails = $_ | Out-String
	Write-Host "Error from catch $errorDetails"
	Send-AppInsightsEventTelemetry -InstrumentationKey '703081d3-c4b5-4e6f-bd89-5c613618f0bf' -Exception $_.Exception -CustomProperties @{ 'CustomExceptionProperty3'='abc'; 'CustomExceptionProperty4'='xyz' }
	Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'SolutionName'='$pipelineSolutionName'; 'DataFileName'='$dataFileName'; 'EventName'="CreateSolutionV4" }
}
