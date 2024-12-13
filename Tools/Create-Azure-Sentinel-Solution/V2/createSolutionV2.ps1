Import-Module powershell-yaml

Write-Host 'It is recommended to use createSolutionV3.ps1 file for solution packaging'
$jsonConversionDepth = 50
$path = "$PSScriptRoot\input"
$mainTemplateArtifact = [PSCustomObject]@{
    name = "DefaultTemplate";
    type = "Template"
}

function handleEmptyInstructionProperties ($inputObj) {
    $outputObj = $inputObj |
    Get-Member -MemberType *Property |
    Select-Object -ExpandProperty Name |
    Sort-Object |
    ForEach-Object -Begin { $obj = New-Object PSObject } {
        if (($null -eq $inputObj.$_) -or ($inputObj.$_ -eq "") -or ($inputObj.$_.Count -eq 0)) {
            Write-Host "Removing empty property $_"
        }
        else {
            $obj | Add-Member -memberType NoteProperty -Name $_ -Value $inputObj.$_
        }
    } { $obj }
    $outputObj
}
function removePropertiesRecursively ($resourceObj, $isWorkbook = $false) {
    foreach ($prop in $resourceObj.PsObject.Properties) {
        $key = $prop.Name
        $val = $prop.Value
        if ($null -eq $val) {
            if ($isWorkbook)
            {
                $resourceObj.$key = ''
            }
            else
            {
                $resourceObj.$key = "[variables('blanks')]";
                if (!$baseMainTemplate.variables.blanks) {
                    $baseMainTemplate.variables | Add-Member -NotePropertyName "blanks" -NotePropertyValue "[replace('b', 'b', '')]"
                }
            }
        }
        elseif ($val -is [System.Object[]]) {
            if ($val.Count -eq 0) {
                if ($isWorkbook)
                {
                    $resourceObj.$key = @()
                }
                else
                {
                    #$resourceObj.PsObject.Properties.Remove($key)
                    $resourceObj.$key = "[variables('TemplateEmptyArray')]";
                    if (!$baseMainTemplate.variables.TemplateEmptyArray) {
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "TemplateEmptyArray" -NotePropertyValue "[json('[]')]"
                    }
                }
            }
            else {
                foreach ($item in $val) {
                    $itemIndex = $val.IndexOf($item)
                    $resourceObj.$key[$itemIndex] = $(removePropertiesRecursively $val[$itemIndex] $isWorkbook)
                }
            }
        }
        else {
            if ($val -is [PSCustomObject]) {
                if ($($val.PsObject.Properties).Count -eq 0) {
                    $resourceObj.PsObject.Properties.Remove($key)
                }
                else {
                    $resourceObj.$key = $(removePropertiesRecursively $val $isWorkbook)
                    if ($($resourceObj.$key.PsObject.Properties).Count -eq 0) {
                        $resourceObj.PsObject.Properties.Remove($key)
                    }
                }
            }
        }
    }
    $resourceObj
}

function queryResourceExists () {
    foreach ($resource in $baseMainTemplate.resources) {
        if ($resource.type -eq "Microsoft.OperationalInsights/workspaces") {
            return $true
        }
    }
    return $false
}

function getQueryResourceLocation () {
    for ($i = 0; $i -lt $baseMainTemplate.resources.Length; $i++) {
        if ($baseMainTemplate.resources[$i].type -eq "Microsoft.OperationalInsights/workspaces") {
            return $i
        }
    }
}

function getParserDetails($solutionName)
{
    $API = 'https://catalogapi.azure.com/offers?api-version=2018-08-01-beta&$filter=categoryIds%2Fany(cat%3A%20cat%20eq%20%27AzureSentinelSolution%27)%20or%20keywords%2Fany(key%3A%20contains(key%2C%27f1de974b-f438-4719-b423-8bf704ba2aef%27))'
    $SolutionDataItems = $(Invoke-WebRequest -URI $API | ConvertFrom-Json).items
    $parserResourceType = [PSObject]@{
        templateSpecParserType = "Microsoft.OperationalInsights/workspaces/savedSearches"
        workspaceType = "Microsoft.OperationalInsights/workspaces"
        normalParserType = "savedSearches"
    }
    $variableExpressionRegex = "\[\s?variables\(\'_([\w\W]+)\'\)\s?\]"
    $parserDisplayDetails = New-Object PSObject
    $parserDisplayDetails | Add-Member -NotePropertyName "functionAlias" -NotePropertyValue $(getFileNameFromPath $file)
    $parserDisplayDetails | Add-Member -NotePropertyName "displayName" -NotePropertyValue "$($fileName)"
    $parserDisplayDetails | Add-Member -NotePropertyName "name" -NotePropertyValue "$($fileName)"

    $currentSolution = $SolutionDataItems | Where-Object { $_.legacyId -eq $solutionName }
    if($currentSolution.length -gt 0)
    {
        $templateUrl = ($currentSolution.plans[0].artifacts | Where-Object { (($_.name -eq $mainTemplateArtifact.name) -and ($_.type -eq $mainTemplateArtifact.type)) }).uri
        $templateContent = $(Invoke-WebRequest -URI $templateUrl) | ConvertFrom-Json
        if ($templateContent.resources -and $templateContent.variables) {
            $templateVariables = $templateContent.variables
            $parserTemplate = $templateContent.resources | Where-Object { $_.type -eq $parserResourceType.templateSpecParserType -or $_.type -eq $parserResourceType.workspaceType }

            if ($null -ne $parserTemplate) {
                if($null -ne $parserTemplate.resources)
                {
                    $parserTemplate = $parserTemplate.resources | Where-Object {$_.properties.category -eq "Samples" -and $_.type -eq $parserResourceType.normalParserType }
                }

                $parserTemplate = $parserTemplate | Where-Object {$_.properties.functionAlias -eq $(getFileNameFromPath $file)}

                if ($null -ne $parserTemplate) {
                    $parserDisplayDetails.functionAlias = $parserTemplate.properties.functionAlias;
                    $parserDisplayDetails.displayName = $parserTemplate.properties.displayName;
                    $parserDisplayDetails.name = $parserTemplate.name.split('/')[-1];

                    $suppressedOutput = $parserDisplayDetails.displayName -match $variableExpressionRegex
                    if ($suppressedOutput -and $matches[1]) {
                        $parserDisplayDetails.displayName = $templateVariables.$($matches[1])
                    }

                    $suppressedOutput = $parserDisplayDetails.name -match $variableExpressionRegex
                    if ($suppressedOutput -and $matches[1]) {
                        $parserDisplayDetails.name = $templateVariables.$($matches[1])
                    }
                }
            }
        }
    }

    return $parserDisplayDetails;
}

foreach ($inputFile in $(Get-ChildItem $path)) {
    $inputJsonPath = Join-Path -Path $path -ChildPath "$($inputFile.Name)"

    $contentToImport = Get-Content -Raw $inputJsonPath | Out-String | ConvertFrom-Json
    $basePath = $(if ($contentToImport.BasePath) { $contentToImport.BasePath + "/" } else { "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/" })

    # Content Counters - (for adding numbering to each item)
    $analyticRuleCounter = 1
    $connectorCounter = 1
    $workbookCounter = 1
    $playbookCounter = 1
    $parserCounter = 1
    $savedSearchCounter = 1
    $huntingQueryCounter = 1
    $watchlistCounter = 1

    # Convenience Variables
    $solutionName = $contentToImport.Name


    # Base JSON Object Paths
    $baseMainTemplatePath = "$PSScriptRoot/templating/baseMainTemplate.json"
    $baseCreateUiDefinitionPath = "$PSScriptRoot/templating/baseCreateUiDefinition.json"
    $metadataPath = "$PSScriptRoot/../../../Solutions/$($contentToImport.Name)/$($contentToImport.Metadata)"

    $workbookMetadataPath = "$PSScriptRoot/../../../"
    # Base JSON Objects
    $baseMainTemplate = Get-Content -Raw $baseMainTemplatePath | Out-String | ConvertFrom-Json
    $baseCreateUiDefinition = Get-Content -Raw $baseCreateUiDefinitionPath | Out-String | ConvertFrom-Json
    $baseMetadata = Get-Content -Raw $metadataPath | Out-String | ConvertFrom-Json

    $DependencyCriteria = @();
    $customConnectorsList = @{};
    $functionAppList = @{};
    $metadataAuthor = $contentToImport.Author.Split(" - ");
    $solutionId = $baseMetadata.publisherId + "." + $baseMetadata.offerId
    $baseMainTemplate.variables | Add-Member -NotePropertyName "solutionId" -NotePropertyValue $solutionId
    $baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionId" -NotePropertyValue "[variables('solutionId')]"
    if($null -ne $metadataAuthor[1])
    {
        $baseMainTemplate.variables | Add-Member -NotePropertyName "email" -NotePropertyValue $($metadataAuthor[1])
        $baseMainTemplate.variables | Add-Member -NotePropertyName "_email" -NotePropertyValue "[variables('email')]"
    }

    foreach ($objectProperties in $contentToImport.PsObject.Properties) {
        # Access the value of the property
        if ($objectProperties.Value -is [System.Array]) {
            foreach ($file in $objectProperties.Value) {
                $finalPath = $basePath + $file
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
				#Replace the special characters in the solution name.
				function Replace-SpecialChars {
				param($InputString,$Type)
					if ($Type.ToLower() -eq 'solutionname') {
						$SpecialChars = '[#?\{\[\(\)\]\}]'
						$Replacement  = ' '
					}
					elseif ($Type.ToLower() -eq 'filename') {
						$SpecialChars = '[#?\{\[\(\)\]\}]'
						$Replacement  = ''
					}
					else {
						$SpecialChars = '[#?\{\[\(\)\]\}]'
						$Replacement  = ''
					}
				return $InputString -replace $SpecialChars,$Replacement
				}

                if ($validJson) {
                    # If valid JSON, must be Workbook or Playbook
                    $objectKeyLowercase = $objectProperties.Name.ToLower()
                    if ($objectKeyLowercase -eq "workbooks") {
                        Write-Host "Generating Workbook using $file"
						$solutionRename = Replace-SpecialChars -InputString $solutionName -Type 'solutionname'
                        $fileName = Split-Path $file -leafbase;
						$fileName = Replace-SpecialChars -InputString $fileName -Type 'filename'
                        $workbookKey = $fileName;
                        $fileName = $fileName + "Workbook";

                        if ($workbookCounter -eq 1) {
                            # Add workbook source variables
                            if (!$contentToImport.TemplateSpec){
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "workbook-source" -NotePropertyValue "[concat(resourceGroup().id, '/providers/Microsoft.OperationalInsights/workspaces/',parameters('workspace'))]"
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "_workbook-source" -NotePropertyValue "[variables('workbook-source')]"
                            };
							$baseWorkbookStep = [PSCustomObject] @{
                                name       = "workbooks";
                                label      = "Workbooks";
                                subLabel   = [PSCustomObject] @{
                                preValidation  = "Configure the workbooks";
                                postValidation = "Done";
                                };
                                bladeTitle = "Workbooks";
                                elements   = @(
                                    [PSCustomObject] @{
                                        name    = "workbooks-text";
                                        type    = "Microsoft.Common.TextBlock";
                                        options = [PSCustomObject] @{
                                            text =  $contentToImport.WorkbookBladeDescription ? $contentToImport.WorkbookBladeDescription : "This solution installs workbook(s) to help you gain insights into the telemetry collected in Microsoft Sentinel. After installing the solution, start using the workbook in Manage solution view.";
                                        }
                                    },
                                    [PSCustomObject] @{
                                        name    = "workbooks-link";
                                        type    = "Microsoft.Common.TextBlock";
                                        options = [PSCustomObject] @{
                                            link=  [PSCustomObject] @{
                                                label= "Learn more";
                                                uri= "https://docs.microsoft.com/azure/sentinel/tutorial-monitor-your-data"
                                              }
                                            }
										}
                                    )
                                }
                                $baseCreateUiDefinition.parameters.steps += $baseWorkbookStep
                            if(!$contentToImport.TemplateSpec)
                            {
                                #Add formattedTimeNow parameter since workbooks exist
                                $timeNowParameter = [PSCustomObject]@{
                                    type         = "string";
                                    defaultValue = "[utcNow('g')]";
                                    metadata     = [PSCustomObject]@{
                                        description = "Appended to workbook displayNames to make them unique";
                                    }
                                }
                                $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name "formattedTimeNow" -Value $timeNowParameter
                            }
                        }
						if($contentToImport.TemplateSpec) {
                            #Getting Workbook Metadata dependencies from Github
                            $workbookData = $null
                            $workbookFinalPath = $workbookMetadataPath + 'Workbooks/WorkbooksMetadata.json';
                            try {
                                Write-Host "Downloading $workbookFinalPath"
                                $workbookData = (New-Object System.Net.WebClient).DownloadString($workbookFinalPath)
                                $dependencies = $workbookData | ConvertFrom-Json | Where-Object {($_.templateRelativePath.split('.')[0].ToLower() -eq $workbookKey.ToLower())}
                                $WorkbookDependencyCriteria = @();
                            }
                            catch {
                                Write-Host "TemplateSpec Workbook Metadata Dependencies errors occurred: $($_.Exception.Message)" -ForegroundColor Red
                                break;
                            }

                            if($dependencies.source -and $dependencies.source.kind -and ($dependencies.source.kind -eq "Community" -or $dependencies.source.kind -eq "Standalone"))
                            {
                                throw "The file $fileName has metadata with source -> kind = Community | Standalone. Please remove it so that it can be packaged as a solution."
                            }
						}
						$workbookUIParameter = [PSCustomObject] @{ name = "workbook$workbookCounter"; type = "Microsoft.Common.Section"; label = $dependencies.title; elements = @( [PSCustomObject] @{ name = "workbook$workbookCounter-text"; type = "Microsoft.Common.TextBlock"; options = @{ text = $dependencies.description; } } ) }
                        $baseCreateUiDefinition.parameters.steps[$baseCreateUiDefinition.parameters.steps.Count - 1].elements += $workbookUIParameter

                        try {
                            $data = $rawData
                            # Serialize workbook data
                            $serializedData = $data |  ConvertFrom-Json -Depth $jsonConversionDepth
                            # Remove empty braces
                            $serializedData = $(removePropertiesRecursively $serializedData $true) | ConvertTo-Json -Compress -Depth $jsonConversionDepth | Out-String
                        }
                        catch {
                            Write-Host "Failed to serialize $file" -ForegroundColor Red
                            break;
                        }
                        $workbookDescriptionText = $(if ($contentToImport.WorkbookDescription -and $contentToImport.WorkbookDescription -is [System.Array]) { $contentToImport.WorkbookDescription[$workbookCounter - 1] } elseif ($contentToImport.WorkbookDescription -and $contentToImport.WorkbookDescription -is [System.String]) { $contentToImport.WorkbookDescription } else { "" })
                        #creating parameters in mainTemplate
                        $workbookIDParameterName = "workbook$workbookCounter-id"
                        $workbookNameParameterName = "workbook$workbookCounter-name"
                        $workbookIDParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the workbook" }; }


                        if(!$contentToImport.TemplateSpec)
                        {
                            $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $workbookIDParameterName -Value $workbookIDParameter
                        }

                        # Create Workbook Resource Object
                        $newWorkbook = [PSCustomObject]@{
                            type       = "Microsoft.Insights/workbooks";
                            name       = "[parameters('workbook$workbookCounter-id')]";
                            location   = "[parameters('workspace-location')]";
                            kind       = "shared";
                            apiVersion = "2021-08-01";
                            metadata   = [PSCustomObject]@{};
                            properties = [PSCustomObject] @{
                                displayName    = $contentToImport.Workbooks ? "[parameters('workbook$workbookCounter-name')]" : "[concat(parameters('workbook$workbookCounter-name'), ' - ', parameters('formattedTimeNow'))]";
                                serializedData = $serializedData;
                                version        = "1.0";
                                sourceId       = $contentToImport.TemplateSpec? "[variables('workspaceResourceId')]" : "[variables('_workbook-source')]";
                                category       = "sentinel"
                            }
                        }

                        if($contentToImport.TemplateSpec) {
                            #Getting Workbook Metadata dependencies from Github
                            $workbookData = $null
                            $workbookFinalPath = $workbookMetadataPath + 'Workbooks/WorkbooksMetadata.json';
                            try {
                                Write-Host "Downloading $workbookFinalPath"
                                $workbookData = (New-Object System.Net.WebClient).DownloadString($workbookFinalPath)
                                $dependencies = $workbookData | ConvertFrom-Json | Where-Object {($_.templateRelativePath.split('.')[0].ToLower() -eq $workbookKey.ToLower())}
                                $WorkbookDependencyCriteria = @();
                                foreach($dataTypesDependencies in $dependencies.dataTypesDependencies)
                                {
                                    $dataTypeObject = New-Object PSObject
                                    $dataTypeObject | Add-Member -MemberType NoteProperty -Name "contentId" -Value "$dataTypesDependencies"
                                    $dataTypeObject | Add-Member -MemberType NoteProperty -Name "kind" -Value "DataType"
                                    $WorkbookDependencyCriteria += $dataTypeObject
                                }
                                foreach($dataConnectorsDependencies in $dependencies.dataConnectorsDependencies)
                                {
                                    $dataConnectorObject = New-Object PSObject
                                    $dataConnectorObject | Add-Member -MemberType NoteProperty -Name "contentId" -Value "$dataConnectorsDependencies"
                                    $dataConnectorObject | Add-Member -MemberType NoteProperty -Name "kind" -Value "DataConnector"
                                    $WorkbookDependencyCriteria += $dataConnectorObject
                                }
                                if($null -ne $dataConnectorObject -or $null -ne $dataTypeObject){
                                $workbookDependencies = [PSCustomObject]@{
                                    operator = "AND";
                                };
                            }

                                if($WorkbookDependencyCriteria.Count -gt 0)
                                {
                                    $workbookDependencies | Add-Member -NotePropertyName "criteria" -NotePropertyValue $WorkbookDependencyCriteria                 
                                }

                                $newWorkbook.metadata | Add-Member -MemberType NoteProperty -Name "description" -Value "$($dependencies.description)"
                            }
                            catch {
                                Write-Host "TemplateSpec Workbook Metadata Dependencies errors occurred: $($_.Exception.Message)" -ForegroundColor Red
                                break;
                            }

                            $workbookNameParameter = [PSCustomObject] @{ type = "string"; defaultValue = $dependencies.title; minLength = 1; metadata = [PSCustomObject] @{ description = "Name for the workbook" }; }
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "workbookVersion$workbookCounter" -NotePropertyValue "$($dependencies.version)"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "workbookContentId$workbookCounter" -NotePropertyValue "$($dependencies.workbookKey)"
                            $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $workbookNameParameterName -Value $workbookNameParameter
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "workbookId$workbookCounter" -NotePropertyValue "[resourceId('Microsoft.Insights/workbooks', variables('workbookContentId$workbookCounter'))]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "workbookTemplateSpecName$workbookCounter" -NotePropertyValue "[concat(parameters('workspace'),'-wb-',uniquestring(variables('_workbookContentId$workbookCounter')))]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_workbookContentId$workbookCounter" -NotePropertyValue "[variables('workbookContentId$workbookCounter')]"
                            $DependencyCriteria += [PSCustomObject]@{
                                kind      = "Workbook";
                                contentId = "[variables('_workbookContentId$workbookCounter')]";
                                version   = "[variables('workbookVersion$workbookCounter')]";
                            };

                            # Add workspace resource ID if not available
                            if (!$baseMainTemplate.variables.workspaceResourceId) {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                            }

                            # Add base templateSpec
                            $baseWorkbookTemplateSpec = [PSCustomObject]@{
                                type       = "Microsoft.Resources/templateSpecs";
                                apiVersion = "2022-02-01";
                                name       = "[variables('workbookTemplateSpecName$workbookCounter')]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "Workbook";
                                };
                                properties = [PSCustomObject]@{
                                    description = "$($solutionName) Workbook with template";
                                    displayName = "$($solutionName) workbook template";
                                }
                            }
                            $newWorkbook.name = "[variables('workbookContentId$workbookCounter')]"
                            $baseMainTemplate.resources += $baseWorkbookTemplateSpec
                            $author = $contentToImport.Author.Split(" - ");
                            $authorDetails = [PSCustomObject]@{
                                name  = $author[0];
                            };
                            if($null -ne $author[1])
                            {
                                $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
                            }
                            $workbookMetadata = [PSCustomObject]@{
                                type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                                apiVersion = "2022-01-01-preview";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('Workbook-', last(split(variables('workbookId$workbookCounter'),'/'))))]";
                                properties = [PSCustomObject]@{
                                    description = "$dependencies.description";
                                    parentId  = "[variables('workbookId$workbookCounter')]"
                                    contentId = "[variables('_workbookContentId$workbookCounter')]";
                                    kind      = "Workbook";
                                    version   = "[variables('workbookVersion$workbookCounter')]";
                                    source    = [PSCustomObject]@{
                                        kind     = "Solution";
                                        name     = $contentToImport.Name;
                                        sourceId = "[variables('_solutionId')]"
                                    };
                                    author    = $authorDetails;
                                    support   = $baseMetadata.support;
                                }
                            }
                            if($null -ne $workbookDependencies)
                            {
                                $workbookMetadata.properties | Add-Member -NotePropertyName "dependencies" -NotePropertyValue $workbookDependencies
                            }

                            if($workbookDescriptionText -ne "")
                            {
                                $workbookMetadata | Add-Member -NotePropertyName "description" -NotePropertyValue $workbookDescriptionText
                            }

                            # Add templateSpecs/versions resource to hold actual content
                            $workbookTemplateSpecContent = [PSCustomObject]@{
                                type       = "Microsoft.Resources/templateSpecs/versions";
                                apiVersion = "2022-02-01";
                                name       = "[concat(variables('workbookTemplateSpecName$workbookCounter'),'/',variables('workbookVersion$workbookCounter'))]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "Workbook";
                                };
                                dependsOn  = @(
                                    "[resourceId('Microsoft.Resources/templateSpecs', variables('workbookTemplateSpecName$workbookCounter'))]"
                                );
                                properties = [PSCustomObject]@{
                                    description  = "$($fileName) with template version $($contentToImport.Version)";
                                    mainTemplate = [PSCustomObject]@{
                                        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                        contentVersion = "[variables('workbookVersion$workbookCounter')]";
                                        parameters     = [PSCustomObject]@{};
                                        variables      = [PSCustomObject]@{};
                                        resources      = @(
                                            # workbook
                                            $newWorkbook,
                                            # Metadata
                                            $workbookMetadata
                                        )
                                    }
                                }
                            }

                            $baseMainTemplate.resources += $workbookTemplateSpecContent
                        }
                        else {
                            $baseMainTemplate.resources += $newWorkbook
                            if ($contentToImport.Metadata) {
                            $baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"
                            $DependencyCriteria += [PSCustomObject]@{
                                kind      = "Workbook";
                                contentId = "[variables('_$fileName')]";
                                version   = "[variables('workbookVersion$workbookCounter')]";
                            };
                        }
                        }
                        $workbookCounter += 1
                    }
                    elseif ($objectKeyLowercase -eq "playbooks") {
                        Write-Host "Generating Playbook using $file"
                        $playbookData = $json
                        $playbookName = $(if ($playbookData.parameters.PlaybookName) { $playbookData.parameters.PlaybookName.defaultValue }elseif ($playbookData.parameters."Playbook Name") { $playbookData.parameters."Playbook Name".defaultValue })

                        $fileName = Split-path -Parent $file | Split-Path -leaf
						if($fileName.ToLower() -eq "incident-trigger" -or $fileName.ToLower() -eq "alert-trigger" -or $fileName.ToLower() -eq "entity-trigger")
						{ 
						$parentPath = Split-Path $file -Parent; $fileName = (Split-Path $parentPath -Parent | Split-Path -leaf) + "-" + $fileName; 
						}

                        if($playbookData.metadata -and $playbookData.metadata.source -and $playbookData.metadata.source.kind -and ($playbookData.metadata.source.kind -eq "Community" -or $playbookData.metadata.source.kind -eq "Standalone"))
                        {
                            throw "The file $fileName has metadata with source -> kind = Community | Standalone. Please remove it so that it can be packaged as a solution."
                        }
						
                        if ($contentToImport.Metadata) {
                            $baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"
                        }

                        $IsLogicAppsCustomConnector = ($playbookData.resources | Where-Object {($_.type.ToLower() -eq "Microsoft.Web/customApis".ToLower())}) ? $true : $false;
                        $IsFunctionAppResource = ($playbookData.resources | Where-Object {($_.type.ToLower() -eq "Microsoft.Web/sites".ToLower())}) ? $true : $false;                        
                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ? "AzureFunction" : "Playbook";;
                            contentId = "[variables('_$fileName')]";
                            version   = "[variables('playbookVersion$playbookCounter')]";
                        };
                        if($fileName.ToLower() -match "FunctionApp"){
                            $functionAppsPlaybookId = $playbookData.parameters.FunctionAppName.defaultValue
                        }

                        if (!$playbookName) {
                            $playbookName = $fileName;
                        }

                        if ($playbookCounter -eq 1) {
                            # If a playbook exists, add CreateUIDefinition step before playbook elements while handling first playbook.
                            $playbookStep = [PSCustomObject] @{
                                name       = "playbooks";
                                label      = "Playbooks";
                                subLabel   = [PSCustomObject] @{
                                    preValidation  = "Configure the playbooks";
                                    postValidation = "Done";
                                };
                                bladeTitle = "Playbooks";
                                elements   = @(
                                    [PSCustomObject] @{
                                        name    = "playbooks-text";
                                        type    = "Microsoft.Common.TextBlock";
                                        options = [PSCustomObject] @{
                                            text = $contentToImport.PlaybooksBladeDescription ? $contentToImport.PlaybooksBladeDescription : "This solution installs the Playbook templates to help implement your Security Orchestration, Automation and Response (SOAR) operations. After installing the solution, these will be deployed under Playbook Templates in the Automation blade in Microsoft Sentinel. They can be configured and managed from the Manage solution view in Content Hub.";
                                        }
                                    },
                                    [PSCustomObject] @{
                                        name    = "playbooks-link";
                                        type    = "Microsoft.Common.TextBlock";
                                        options = [PSCustomObject] @{
                                            link = [PSCustomObject] @{
                                                label = "Learn more";
                                                uri   = "https://docs.microsoft.com/azure/sentinel/tutorial-respond-threats-playbook?WT.mc_id=Portal-Microsoft_Azure_CreateUIDef"
                                        }
                                    }
                                })
                            }
                            $baseCreateUiDefinition.parameters.steps += $playbookStep
                        }
                        $playbookDescriptionText = $(if ($contentToImport.PlaybookDescription -and $contentToImport.PlaybookDescription -is [System.Array]) { $contentToImport.PlaybookDescription[$playbookCounter - 1] } elseif ($contentToImport.PlaybookDescription -and $contentToImport.PlaybookDescription -is [System.String]) { $contentToImport.PlaybookDescription } else { "" })
                        $playbookElement = [PSCustomObject] @{
                            name     = "playbook$playbookCounter";
                            type     = "Microsoft.Common.Section";
                            label    = $playbookName;
                            elements = @(
                                [PSCustomObject] @{
                                    name    = "playbook$playbookCounter-text";
                                    type    = "Microsoft.Common.TextBlock";
                                    options = [PSCustomObject] @{ text = if ($playbookData.metadata -and $playbookData.metadata.comments) { $playbookData.metadata.comments } else { "This playbook ingests events from $solutionName into Log Analytics using the API." } }
                                }
                            )
                        }
                        $currentStepNum = $baseCreateUiDefinition.parameters.steps.Count - 1
                        #$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $playbookElement

                        foreach ($param in $playbookData.parameters.PsObject.Properties) {
                            $paramName = $param.Name
                            $defaultParamValue = $(if ($playbookData.parameters.$paramName.defaultValue) { $playbookData.parameters.$paramName.defaultValue } else { "" })
                            if ($param.Name.ToLower().contains("playbookname")) {
                                $playbookNameObject = [PSCustomObject] @{
                                    name         = $contentToImport.TemplateSpec ? $paramName : "playbook$playbookCounter-$paramName";
                                    type         = "Microsoft.Common.TextBox";
                                    label        = "Playbook Name";
                                    defaultValue = $defaultParamValue;
                                    toolTip      = "Resource name for the logic app playbook.  No spaces are allowed";
                                    constraints  = [PSCustomObject] @{
                                        required          = $true;
                                        regex             = "[a-z0-9A-Z]{1,256}$";
                                        validationMessage = "Please enter a playbook resource name"
                                    }
                                }
                                #$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookNameObject
                                if(!$contentToImport.TemplateSpec)
                                {
                                    $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                            defaultValue = $playbookName;
                                            type         = "string";
                                            minLength    = 1;
                                            metadata     = [PSCustomObject] @{ description = "Resource name for the logic app playbook.  No spaces are allowed"; }
                                        })
                                }
                            }
                            elseif ($param.Name.ToLower().contains("username")) {
                                $playbookUsernameObject = [PSCustomObject] @{
                                    name         = $contentToImport.TemplateSpec ? $paramName : "playbook$playbookCounter-$paramName";
                                    type         = "Microsoft.Common.TextBox";
                                    label        = "$solutionName Username";
                                    defaultValue = $defaultParamValue;
                                    toolTip      = "Username to connect to $solutionName API";
                                    constraints  = [PSCustomObject] @{
                                        required          = $true;
                                        regex             = "[a-z0-9A-Z]{1,256}$";
                                        validationMessage = "Please enter a playbook username";
                                    }
                                }
                                #$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookUsernameObject
                                if(!$contentToImport.TemplateSpec){
                                $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        defaultValue = $defaultParamValue;
                                        type         = "string";
                                        minLength    = 1;
                                        metadata     = [PSCustomObject] @{ description = "Username to connect to $solutionName API" }
                                    })
                                }
                            }
                            elseif ($param.Name.ToLower().contains("password")) {
                                $playbookPasswordObject = [PSCustomObject] @{
                                    name        = $contentToImport.TemplateSpec ? $paramName : "playbook$playbookCounter-$paramName";
                                    type        = "Microsoft.Common.PasswordBox";
                                    label       = [PSCustomObject] @{ password = $defaultParamValue; };
                                    toolTip     = "Password to connect to $solutionName API";
                                    constraints = [PSCustomObject] @{ required = $true; };
                                    options     = [PSCustomObject] @{ hideConfirmation = $false; };
                                }
                                #$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookPasswordObject
                                if(!$contentToImport.TemplateSpec){
                                $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        type      = "securestring";
                                        minLength = 1;
                                        metadata  = [PSCustomObject] @{ description = "Password to connect to $solutionName API"; }
                                    })
                                }
                            }
                            elseif ($param.Name.ToLower().contains("apikey")) {
                                $playbookPasswordObject = [PSCustomObject] @{
                                    name        = $contentToImport.TemplateSpec ? $paramName : "playbook$playbookCounter-$paramName";
                                    type        = "Microsoft.Common.PasswordBox";
                                    label       = [PSCustomObject] @{password = "ApiKey" };
                                    toolTip     = "ApiKey to connect to $solutionName API";
                                    constraints = [PSCustomObject] @{ required = $true; };
                                    options     = [PSCustomObject] @{ hideConfirmation = $true; };
                                }
                                #$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookPasswordObject
                                if(!$contentToImport.TemplateSpec)
                                {
                                    $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                            type      = "securestring";
                                            minLength = 1;
                                            metadata  = [PSCustomObject] @{ description = "ApiKey to connect to $solutionName API"; }
                                        })
                                }
                            }
                            else {
                                function PascalSplit ($pascalStr) {
                                    foreach ($piece in $pascalStr) {
                                        if ($piece -is [array]) {
                                            foreach ($subPiece in $piece) { PascalSplit $subPiece }
                                        }
                                        else {
                                            ($piece.ToString() -creplace '[A-Z]', ' $&').Trim().Split($null)
                                        }
                                    }
                                }

                                $playbookParamObject = $(
                                    if ($playbookData.parameters.$paramName.allowedValues) {
                                        [PSCustomObject] @{
                                            name         = $contentToImport.TemplateSpec ? $paramName : "playbook$playbookCounter-$paramName";
                                            type         = "Microsoft.Common.DropDown";
                                            label        = "$(PascalSplit $paramName)";
                                            placeholder  = "$($playbookData.parameters.$paramName.allowedValues[0])";
                                            defaultValue = "$($playbookData.parameters.$paramName.allowedValues[0])";
                                            toolTip      = "Please enter $(if($paramName.IndexOf("-") -ne -1){$paramName}else{PascalSplit $paramName})";
                                            constraints  = [PSCustomObject] @{
                                                allowedValues = $playbookData.parameters.$paramName.allowedValues | ForEach-Object {
                                                    [PSCustomObject] @{
                                                        label = $_;
                                                        value = $_;
                                                    }
                                                }
                                                required      = $true;
                                            }
                                            visible      = $true;
                                        }
                                    }
                                    else {
                                        [PSCustomObject] @{
                                            name         = $contentToImport.TemplateSpec ? $paramName : "playbook$playbookCounter-$paramName";
                                            type         = "Microsoft.Common.TextBox";
                                            label        = "$(PascalSplit $paramName)";
                                            defaultValue = $defaultParamValue;
                                            toolTip      = "Please enter $(if($paramName.IndexOf("-") -ne -1){$paramName}else{PascalSplit $paramName})";
                                            constraints  = [PSCustomObject] @{
                                                required          = $true;
                                                regex             = "[a-z0-9A-Z]{1,256}$";
                                                validationMessage = "Please enter the $(PascalSplit $paramName)"
                                            }
                                        }
                                    }
                                )
                                #$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookParamObject
                                $defaultValue = $(if ($defaultParamValue) { $defaultParamValue } else { "" })
                                if(!$contentToImport.TemplateSpec){
                                $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        defaultValue = $defaultValue;
                                        type         = "string";
                                        minLength    = 1;
                                    })
                                }
                            }
                            if(!$contentToImport.TemplateSpec){
                                $baseCreateUiDefinition.parameters.outputs | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue "[steps('playbooks').playbook$playbookCounter.playbook$playbookCounter-$paramName]"
                            }
                        }

                        foreach ($playbookVariable in $playbookData.variables.PsObject.Properties) {
                            $variableName = $playbookVariable.Name
                            $variableValue = $playbookVariable.Value
                            if ($variableValue -is [System.String]) {
                                $variableValue = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" $variableValue $playbookCounter)
                            }
                            if($contentToImport.TemplateSpec -and $variableName.ToLower().Contains("connection"))
                            {
                                $variableValue = "[" + $variableValue ;
                            }
                            if (!$contentToImport.TemplateSpec -and $variableName.ToLower().contains("apikey")) {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "playbook-$variableName" -NotePropertyValue "[$variableValue]"
                            }
                            elseif (!$contentToImport.TemplateSpec) {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "playbook$playbookCounter-$variableName" -NotePropertyValue $variableValue
                            }
                        }

                        $azureManagementUrlExists = $false
                        $azureManagementUrl = "management.azure.com"

                        function replaceQuotes ($inputStr) {
                            $baseStr = $resourceObj.$key
                            $outputStr = $baseStr.Replace("`"", "\`"")
                            $outputStr
                        }

                        function removeBlanksRecursively($resourceObj) {
                            if ($resourceObj.GetType() -ne [System.DateTime]) {
                                foreach ($prop in $resourceObj.PsObject.Properties) {
                                    $key = $prop.Name
                                    if ($prop.Value -is [System.String]) {
                                        #Write-Host "its a string $resourceObj.$key"
                                        if($resourceObj.$key -eq "")
                                        {
                                            $resourceObj.$key = "[variables('blanks')]";
                                            if (!$baseMainTemplate.variables.blanks) {
                                    $baseMainTemplate.variables | Add-Member -NotePropertyName "blanks" -NotePropertyValue "[replace('b', 'b', '')]"
                                }
                                        }
                                    }
                                    elseif ($prop.Value -is [System.Array]) {
                                        foreach ($item in $prop.Value) {
                                            $itemIndex = $prop.Value.IndexOf($item)
                                            if ($null -ne $itemIndex) {
                                                if ($item -is [System.String]) {
                                                    $resourceObj.$key[$itemIndex] = $item
                                                }
                                                elseif ($item -is [System.Management.Automation.PSCustomObject]) {
                                                    $resourceObj.$key[$itemIndex] = $(removeBlanksRecursively $item)
                                                }
                                            }
                                        }
                                    }
                                    else {
                                        if (($prop.Value -isnot [System.Int32]) -and ($prop.Value -isnot [System.Int64])) {
                                            $resourceObj.$key = $(removeBlanksRecursively $resourceObj.$key)
                                        }
                                    }
                                }
                            }
                            $resourceObj
                        }

                        function addInternalSuffixRecursively($resourceObj) {
                            if ($resourceObj.GetType() -ne [System.DateTime]) {
                                foreach ($prop in $resourceObj.PsObject.Properties) {
                                    $key = $prop.Name
                                    if ($prop.Value -is [System.String]) {
                                        $resourceObj.$key = $resourceObj.$key.Replace("resourceGroup().location", "variables('workspace-location-inline')")
                                        if ($key -eq "operationId") {
                                            $playbookData.variables | Add-Member -NotePropertyName "operationId-$($resourceobj.$key)" -NotePropertyValue $($resourceobj.$key)
                                            $playbookData.variables | Add-Member -NotePropertyName "_operationId-$($resourceobj.$key)" -NotePropertyValue "[variables('operationId-$($resourceobj.$key)')]"
                                            $resourceObj.$key = "[variables('_operationId-$($resourceobj.$key)')]"
                                        }
                                        if($contentToImport.TemplateSpec -and ($resourceObj.$key.StartsWith("[")) -and ($resourceObj.$key -ne "[variables('TemplateEmptyArray')]"))
                                        {
                                            $resourceObj.$key = "[" + $resourceObj.$key;
                                        }
                                    }
                                    elseif ($prop.Value -is [System.Array]) {
                                        foreach ($item in $prop.Value) {
                                            $itemIndex = $prop.Value.IndexOf($item)
                                            if ($null -ne $itemIndex) {
                                                if ($item -is [System.String]) {
                                                    $item = $item.Replace("resourceGroup().location", "variables('workspace-location-inline')")
                                                    if($contentToImport.TemplateSpec -and ($item.StartsWith("[")))
                                                    {
                                                        $item = "[" + $item;
                                                    }
                                                    $resourceObj.$key[$itemIndex] = $item
                                                }
                                                elseif ($item -is [System.Management.Automation.PSCustomObject]) {
                                                    $resourceObj.$key[$itemIndex] = $(addInternalSuffixRecursively $item)
                                                }
                                            }
                                        }
                                    }
                                    else {
                                        if (($prop.Value -isnot [System.Int32]) -and ($prop.Value -isnot [System.Int64])) {
                                            $resourceObj.$key = $(addInternalSuffixRecursively $resourceObj.$key)
                                        }
                                    }
                                }
                            }
                            $resourceObj
                        }

                        function replaceVarsRecursively ($resourceObj) {
                            if ($resourceObj.GetType() -ne [System.DateTime]) {
                                foreach ($prop in $resourceObj.PsObject.Properties) {
                                    $key = $prop.Name
                                    if ($prop.Value -is [System.String]) {
                                        $resourceObj.$key = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" "$(replaceQuotes $resourceObj.$key)" $playbookCounter)
                                        if($contentToImport.TemplateSpec -and ($resourceObj.$key.StartsWith("[") -and $resourceObj.$key.Contains("parameters(") -and !$resourceObj.$key.contains("parameters('workspace-location')")))
                                        {
                                            $resourceObj.$key = "[" + $resourceObj.$key;
                                        }
                                        if ($resourceObj.$key.StartsWith("[") -and $resourceObj.$key[$resourceObj.$key.Length - 1] -eq "]") {
                                            $resourceObj.$key = $(node "$PSScriptRoot/templating/replacePlaybookVarNames.js" "$(replaceQuotes $resourceObj.$key)" $playbookCounter)
                                        }
                                        $resourceObj.$key = $(node "$PSScriptRoot/templating/replaceLocationValue.js" "$(replaceQuotes $resourceObj.$key)" $playbookCounter)
                                        if ($resourceObj.$key.IndexOf($azureManagementUrl)) {
                                            $resourceObj.$key = $resourceObj.$key.Replace($azureManagementUrl, "@{variables('azureManagementUrl')}")
                                            $azureManagementUrlExists = $true
                                        }
                                        if ($key -eq "operationId") {
                                            $baseMainTemplate.variables | Add-Member -NotePropertyName "operationId-$($resourceobj.$key)" -NotePropertyValue $($resourceobj.$key)
                                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_operationId-$($resourceobj.$key)" -NotePropertyValue "[variables('operationId-$($resourceobj.$key)')]"
                                            $resourceObj.$key = "[variables('_operationId-$($resourceobj.$key)')]"
                                        }
                                    }
                                    elseif ($prop.Value -is [System.Array]) {
                                        foreach ($item in $prop.Value) {
                                            $itemIndex = $prop.Value.IndexOf($item)
                                            if ($null -ne $itemIndex) {
                                                if ($item -is [System.String]) {
                                                    $item = $(node "$PSScriptRoot/templating/replaceLocationValue.js" $item $playbookCounter)
                                                    $item = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" $item $playbookCounter)
                                                    if($contentToImport.TemplateSpec -and ($item.StartsWith("[") -and $item.Contains("parameters(") -and !$item.contains("parameters('workspace-location')")))
                                                    {
                                                        $item = "[" + $item;
                                                    }
                                                    if ($item.StartsWith("[") -and $item[$item.Length - 1] -eq "]") {
                                                        $item = $(node "$PSScriptRoot/templating/replacePlaybookVarNames.js" $item $playbookCounter)
                                                    }
                                                    $resourceObj.$key[$itemIndex] = $item
                                                }
                                                elseif ($item -is [System.Management.Automation.PSCustomObject]) {
                                                    $resourceObj.$key[$itemIndex] = $(replaceVarsRecursively $item)
                                                }
                                            }
                                        }
                                    }
                                    else {
                                        if (($prop.Value -isnot [System.Int32]) -and ($prop.Value -isnot [System.Int64])) {
                                            $resourceObj.$key = $(replaceVarsRecursively $resourceObj.$key)
                                        }
                                    }
                                }
                            }
                            $resourceObj
                        }
                        $connectionCounter = 1
                        function getConnectionVariableName($connectionVariable) {
                            foreach ($templateVar in $($baseMainTemplate.variables).PSObject.Properties) {
                                if ($templateVar.Value -eq $connectionVariable) {
                                    return $templateVar.Name
                                }
                            }
                            return $false
                        }

                        $playbookDependencies = @();
                        $playbookResources = @();
                        $playbookVersion = '1.0';
                        $logicAppsPlaybookId = '';
                        $customConnectorContentId = '';
                        $FunctionResource = @();
                        foreach ($playbookResource in $playbookData.resources) {
                            if ($playbookResource.type -eq "Microsoft.Web/connections") {
                                if ($playbookResource.properties -and $playbookResource.properties.api -and $playbookResource.properties.api.id) {
                                    if ($playbookResource.properties.api.id.Contains("/providers/Microsoft.Web/customApis/")) {
                                        $splits = $playbookResource.properties.api.id.Split(',');
                                        $connectionKey = $splits[-1].Trim().Replace("parameters('","").Replace("'","").Replace(")","").Replace("]","");

                                        foreach ($templateVar in $($playbookData.parameters).PSObject.Properties) {
                                            if ($templateVar.Name -eq $connectionKey) {
                                                $playbookDependencies += [PSCustomObject] @{
                                                    kind = "LogicAppsCustomConnector";
                                                    contentId = $customConnectorsList[$templateVar.Value.defaultValue].id;
                                                    version = $customConnectorsList[$templateVar.Value.defaultValue].version;
                                                }
                                            }
                                        }
                                    }

                                    $connectionVar = $playbookResource.properties.api.id
                                    $connectionVar = $connectionVar.Replace("resourceGroup().location", "variables('workspace-location-inline')")
                                    $variableReferenceString = "[variables"
                                    $varName = ""
                                    if ($connectionVar.StartsWith($variableReferenceString)) {
                                        # Get value of variable
                                        $varName = $($connectionVar.Split("'"))[1]
                                        # Handle variable reference pairs
                                        if ($playbookData.variables.$varName.StartsWith($variableReferenceString)) {
                                            $varName = $($playbookData.variables.$varName.Split("'"))[1]
                                        }
                                        $connectionVar = $playbookData.variables.$varName
                                        $connectionVar = $connectionVar.Replace("resourceGroup().location", "variables('workspace-location-inline')")

                                    }
                                    $foundConnection = getConnectionVariableName $connectionVar
                                    if ($foundConnection) {
                                        $playbookResource.properties.api.id = "[variables('_$foundConnection')]"
                                    }
                                    else {
                                        $playbookData.variables | Add-Member -NotePropertyName "connection-$connectionCounter" -NotePropertyValue $connectionVar
                                        $playbookData.variables | Add-Member -NotePropertyName "_connection-$connectionCounter" -NotePropertyValue "[variables('connection-$connectionCounter')]"
                                        $playbookResource.properties.api.id = "[variables('_connection-$connectionCounter')]"
                                    }
                                    if(($playbookResource.properties.parameterValues) -and ($null -ne $baseMainTemplate.variables.'playbook-ApiKey')) {
                                        $playbookResource.properties.parameterValues.api_key = "[variables('playbook-ApiKey')]"
                                    }
                                }
                            }
                            elseif ($contentToImport.TemplateSpec -and $playbookResource.type -eq "Microsoft.Logic/workflows") {
                                if($null -eq $playbookResource.tags)
                                {
                                    $playbookResource | Add-Member -NotePropertyName "tags" -NotePropertyValue ([PSCustomObject]@{});
                                }
                                $playbookResource.tags | Add-Member -NotePropertyName "hidden-SentinelWorkspaceId" -NotePropertyValue "[variables('workspaceResourceId')]";
                                $playbookVersion = $playbookResource.tags.'hidden-SentinelTemplateVersion' ? $playbookResource.tags.'hidden-SentinelTemplateVersion' : $playbookVersion;
                            }  elseif ($contentToImport.TemplateSpec -and $playbookResource.type -eq "Microsoft.Web/customApis") {
                                $logicAppsPlaybookId = $playbookResource.name.Replace("parameters('","").Replace("'","").Replace(")","").Replace("]","").Replace("[","");
                                $customConnectorContentId = $playbookData.parameters.$logicAppsPlaybookId.defaultValue
                                Write-Host $customConnectorContentId;
                                Write-Host $logicAppsPlaybookId;
                            }

                            $playbookResource =  $playbookResource
                            $playbookResource = $(removePropertiesRecursively $playbookResource $false)
                            $playbookResource =  $(addInternalSuffixRecursively $playbookResource)
                            $playbookResource =  $(removeBlanksRecursively $playbookResource)
                            $playbookResources += $playbookResource;
                            $connectionCounter += 1
                        }
                        if(!$IsFunctionAppResource -and $rawData -like '*Microsoft.Web/sites*' )
                            {
                            if ($null -ne $playbookData -and $null -ne $playbookData.parameters){
                                        foreach($param in $playbookData.parameters.PsObject.Properties)
                                        {
                                            if($param.Value -match "defaultValue" -and $functionAppList.ContainsKey($param.Value.defaultValue))
                                            {
                                                $playbookDependencies += [PSCustomObject] @{
                                                        kind = "AzureFunction";
                                                        contentId = $functionAppList[$param.Value.defaultValue].id;
                                                        version = $functionAppList[$param.Value.defaultValue].version;
                                                }
                                            }
                                        }                                                                            
                        
                        }
                        }


                        if($contentToImport.TemplateSpec)
                        {
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "playbookVersion$playbookCounter" -NotePropertyValue $playbookVersion
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "playbookContentId$playbookCounter" -NotePropertyValue $fileName
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_playbookContentId$playbookCounter" -NotePropertyValue "[variables('playbookContentId$playbookCounter')]"

                            if (!$IsLogicAppsCustomConnector -and !$IsFunctionAppResource) {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "playbookId$playbookCounter" -NotePropertyValue "[resourceId('Microsoft.Logic/workflows', variables('playbookContentId$playbookCounter'))]"
                            }

                            $baseMainTemplate.variables | Add-Member -NotePropertyName "playbookTemplateSpecName$playbookCounter" -NotePropertyValue ($IsLogicAppsCustomConnector ? 
                            "[concat(parameters('workspace'),'-lc-',uniquestring(variables('_playbookContentId$playbookCounter')))]" : 
                            $IsFunctionAppResource ? "[concat(parameters('workspace'),'-fa-',uniquestring(variables('_playbookContentId$playbookCounter')))]" :
                            "[concat(parameters('workspace'),'-pl-',uniquestring(variables('_playbookContentId$playbookCounter')))]")

                            # Add workspace resource ID if not available
                            if (!$baseMainTemplate.variables.workspaceResourceId) {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                            }
                            # Add base templateSpec
                            $basePlaybookTemplateSpec = [PSCustomObject]@{
                                type       = "Microsoft.Resources/templateSpecs";
                                apiVersion = "2022-02-01";
                                name       = "[variables('playbookTemplateSpecName$playbookCounter')]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" 
                                        : $IsFunctionAppResource ? "AzureFunction" : "Playbook";
                                };
                                properties = [PSCustomObject]@{
                                    description = $IsLogicAppsCustomConnector -or $IsFunctionAppResource ? $playbookName : "$($playbookName) playbook";
                                    displayName = $IsLogicAppsCustomConnector -or $IsFunctionAppResource ? $playbookName : "$($playbookName) playbook";
                                }
                            }

                            $baseMainTemplate.resources += $basePlaybookTemplateSpec
                            $author = $contentToImport.Author.Split(" - ");
                            $authorDetails = [PSCustomObject]@{
                                name  = $author[0];
                            };
                            if($null -ne $author[1])
                            {
                                $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
                            }
                            if ($IsLogicAppsCustomConnector) {
                                $customConnectorsList.add($customConnectorContentId, @{ id="[variables('_$filename')]"; version="[variables('playbookVersion$playbookCounter')]"});
                            }
                            if ($IsFunctionAppResource) {
                                $functionAppList.add($functionAppsPlaybookId, @{ id="[variables('_$filename')]"; version="[variables('playbookVersion$playbookCounter')]"});
                            }

                            Write-Host $playbookDependencies
                            $playbookMetadata = [PSCustomObject]@{
                                type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                                apiVersion = "2022-01-01-preview";
                                name       = $IsLogicAppsCustomConnector ? "[[concat(variables('workspace-name'),'/Microsoft.SecurityInsights/',concat('LogicAppsCustomConnector-', last(split(variables('playbookId$playbookCounter'),'/'))))]" : 
                                $IsFunctionAppResource ? "[[concat(variables('workspace-name'),'/Microsoft.SecurityInsights/',concat('AzureFunction-', last(split(variables('playbookId$playbookCounter'),'/'))))]" :
                                "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('Playbook-', last(split(variables('playbookId$playbookCounter'),'/'))))]";
                                properties = [PSCustomObject]@{
                                    parentId  = $IsLogicAppsCustomConnector -or $IsFunctionAppResource ? "[[variables('playbookId$playbookCounter')]" : "[variables('playbookId$playbookCounter')]"
                                    contentId = "[variables('_playbookContentId$playbookCounter')]";
                                    kind      = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ?
                                    "AzureFunction" : "Playbook";
                                    version   = "[variables('playbookVersion$playbookCounter')]";
                                    source    = [PSCustomObject]@{
                                        kind     = "Solution";
                                        name     = $contentToImport.Name;
                                        sourceId = "[variables('_solutionId')]"
                                    };
                                    author    = $authorDetails;
                                    support   = $baseMetadata.support;
                                }
                            }

                            if ($playbookDependencies) {
                                $criteria = [PSCustomObject]@{
                                    criteria = $playbookDependencies
                                };
                                $playbookMetadata.properties | Add-Member -NotePropertyName "dependencies" -NotePropertyValue $criteria
                            }

                            $playbookVariables = [PSCustomObject]@{};
                            foreach($var in $playbookData.variables.PsObject.Properties)
                            {
                                $playbookVariables | Add-Member -NotePropertyName $var.Name -NotePropertyValue $(($contentToImport.TemplateSpec -and $var.Value.StartsWith("[")) ? "[" + $var.Value : $var.Value);
                            }

                            $playbookVariables | Add-Member -NotePropertyName "workspace-location-inline" -NotePropertyValue "[concat('[resourceGroup().locatio', 'n]')]";
                            if ($IsLogicAppsCustomConnector) {
                                $playbookVariables | Add-Member -NotePropertyName "playbookContentId$playbookCounter" -NotePropertyValue $fileName;
                                $playbookVariables | Add-Member -NotePropertyName "playbookId$playbookCounter" -NotePropertyValue "[[resourceId('Microsoft.Web/customApis', parameters('$logicAppsPlaybookId'))]"
                            }

                            if ($IsFunctionAppResource) {
                                $playbookVariables | Add-Member -NotePropertyName "playbookContentId$playbookCounter" -NotePropertyValue $fileName;
                                $playbookVariables | Add-Member -NotePropertyName "playbookId$playbookCounter" -NotePropertyValue "[[resourceId('Microsoft.Logic/workflows', variables('playbookContentId$playbookCounter'))]"
                            }

                            $playbookVariables | Add-Member -NotePropertyName "workspace-name" -NotePropertyValue "[parameters('workspace')]"
                            $playbookVariables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[[resourceId('microsoft.OperationalInsights/Workspaces', variables('workspace-name'))]"
                            $playbookResources = $playbookResources + $playbookMetadata;

                            $playbookMetadata = [PSCustomObject]@{};
                            foreach($var in $playbookData.metadata.PsObject.Properties)
                            {
                                $playbookMetadata | Add-Member -NotePropertyName $var.Name -NotePropertyValue $var.Value;
                            }

                            # Add templateSpecs/versions resource to hold actual content
                            $playbookTemplateSpecContent = [PSCustomObject]@{
                                type       = "Microsoft.Resources/templateSpecs/versions";
                                apiVersion = "2022-02-01";
                                name       = "[concat(variables('playbookTemplateSpecName$playbookCounter'),'/',variables('playbookVersion$playbookCounter'))]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ? "AzureFunction" : "Playbook";
                                };
                                dependsOn  = @(
                                    "[resourceId('Microsoft.Resources/templateSpecs', variables('playbookTemplateSpecName$playbookCounter'))]"
                                );
                                properties = [PSCustomObject]@{
                                    description  = "$($playbookName) Playbook with template version $($contentToImport.Version)";
                                    mainTemplate = [PSCustomObject]@{
                                        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                        contentVersion = "[variables('playbookVersion$playbookCounter')]";
                                        parameters     = $playbookData.parameters;
                                        variables      = $playbookVariables;
                                        resources      = $playbookResources;
                                    }
                                }
                            }

                            if (@($playbookMetadata.PsObject.Properties).Count -gt 0) {
                                Write-Host "creating metadata for playbook"
                                $playbookTemplateSpecContent.properties.mainTemplate | Add-Member -NotePropertyName "metadata" -NotePropertyValue ([PSCustomObject]@{});
                                foreach($var in $playbookMetadata.PsObject.Properties) {
                                    if ($var.Name -ne "author" -and $var.Name -ne "support" -and $var.Name -ne "prerequisitesDeployTemplateFile") {
                                        $playbookTemplateSpecContent.properties.mainTemplate.metadata | Add-Member -NotePropertyName $var.Name -NotePropertyValue $var.Value;
                                    }
                                }
                                if (!$playbookTemplateSpecContent.properties.mainTemplate.metadata.'lastUpdateTime') {
                                    $playbookTemplateSpecContent.properties.mainTemplate.metadata | Add-Member -NotePropertyName "lastUpdateTime" -NotePropertyValue (get-date -format "yyyy-MM-ddTHH:mm:ss.fffZ");
                                }
                            }
                            if (!$playbookMetadata.releaseNotes -and $playbookTemplateSpecContent.properties.mainTemplate.metadata) {
                                Write-Host "adding default release notes"
                                $releaseNotes = [PSCustomObject]@{
                                    version = $playbookVersion;
                                    title      = "[variables('blanks')]";
                                    notes      = @("Initial version");
                                }
                                $playbookTemplateSpecContent.properties.mainTemplate.metadata | Add-Member -NotePropertyName 'releaseNotes' -NotePropertyValue $releaseNotes;
                                if (!$baseMainTemplate.variables.blanks) {
                                    $baseMainTemplate.variables | Add-Member -NotePropertyName "blanks" -NotePropertyValue "[replace('b', 'b', '')]"
                                }
                            }

                            if ($null -ne $playbookTemplateSpecContent.properties.mainTemplate.metadata.entities -and
                                $playbookTemplateSpecContent.properties.mainTemplate.metadata.entities.count -le 0)
                            {
                                $playbookTemplateSpecContent.properties.mainTemplate.metadata.PSObject.Properties.Remove("entities");
                            }

                            if ($null -ne $playbookTemplateSpecContent.properties.mainTemplate.metadata.tags -and
                                $playbookTemplateSpecContent.properties.mainTemplate.metadata.tags.count -le 0)
                            {
                                $playbookTemplateSpecContent.properties.mainTemplate.metadata.PSObject.Properties.Remove("tags");
                            }

                            if ($null -ne $playbookTemplateSpecContent.properties.mainTemplate.metadata.prerequisites -and
                            [string]::IsNullOrWhitespace($playbookTemplateSpecContent.properties.mainTemplate.metadata.prerequisites))
                            {
                                $playbookTemplateSpecContent.properties.mainTemplate.metadata.PSObject.Properties.Remove("prerequisites");
                            }
                            $baseMainTemplate.resources += $playbookTemplateSpecContent;
                        }
                        else
                        {
                            $baseMainTemplate.resources += $playbookResources;
                        }

                        if ($azureManagementUrlExists) {
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "azureManagementUrl" -NotePropertyValue $azureManagementUrl
                        }

                        $playbookCounter += 1
                    }
                    elseif ($objectKeyLowercase -eq "data connectors") {
                        Write-Host "Generating Data Connector using $file"
                        try {
                            $ccpPollingConfig = [PSCustomObject] @{}
                            $ccpConnector = $false
                            $connectorData = ConvertFrom-Json $rawData
                            # If both ID and Title exist, is standard GenericUI data connector
                            if ($connectorData.resources -and
                            $connectorData.resources[0] -and
                            $connectorData.resources[0].properties -and
                            $connectorData.resources[0].properties.connectorUiConfig -and
                            $connectorData.resources[0].properties.pollingConfig) {
                                $ccpPollingConfig = $connectorData.resources[0].properties.pollingConfig
                                $ccpConnector = $true
                                $templateSpecConnectorData = $connectorData.resources[0].properties.connectorUiConfig
                            }
                            else
                            {
                                $ccpPollingConfig = $null
                                $ccpConnector = $false
                                $templateSpecConnectorData = $connectorData
                            }
                        }
                        catch {
                            Write-Host "Failed to deserialize $file" -ForegroundColor Red
                            break;
                        }
                        # $connectorNameParamObj = [PSCustomObject] @{
                        #     type         = "string";
                        #      defaultValue = $(New-Guid).Guid
                        # }
                        #  $connectorId = $connectorData.id + 'Connector';
                        # if ($contentToImport.Metadata -and !$contentToImport.TemplateSpec) {
                        #     $baseMainTemplate.variables | Add-Member -NotePropertyName $connectorId -NotePropertyValue $connectorId
                        #     $baseMainTemplate.variables | Add-Member -NotePropertyName "_$connectorId" -NotePropertyValue "[variables('$connectorId')]"
                        # }
                        #  if (!$contentToImport.TemplateSpec){
                        #     $baseMainTemplate.parameters | Add-Member -NotePropertyName "connector$connectorCounter-name" -NotePropertyValue $connectorNameParamObj
                        #     $baseMainTemplate.variables | Add-Member -NotePropertyName "connector$connectorCounter-source" -NotePropertyValue "[concat('/subscriptions/',subscription().subscriptionId,'/resourceGroups/',resourceGroup().name,'/providers/Microsoft.OperationalInsights/workspaces/',parameters('workspace'),'/providers/Microsoft.SecurityInsights/dataConnectors/',parameters('connector$connectorCounter-name'))]"
                        #     $baseMainTemplate.variables | Add-Member -NotePropertyName "_connector$connectorCounter-source" -NotePropertyValue "[variables('connector$connectorCounter-source')]"
                        #  };
                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = "DataConnector";
                            contentId = if ($contentToImport.TemplateSpec){"[variables('_dataConnectorContentId$connectorCounter')]"}else{"[variables('_$connectorId')]"};
                            version   = if ($contentToImport.TemplateSpec){"[variables('dataConnectorVersion$connectorCounter')]"}else{$contentToImport.Version};
                        };
                        foreach ($step in $templateSpecConnectorData.instructionSteps) {
                            # Remove empty properties from each instructionStep
                            $stepIndex = $templateSpecConnectorData.instructionSteps.IndexOf($step)
                            $templateSpecConnectorData.instructionSteps[$stepIndex] = handleEmptyInstructionProperties $step
                        }

                        if ($contentToImport.TemplateSpec) {
                            $connectorName = $contentToImport.Name
                            # Add workspace resource ID if not available
                            if (!$baseMainTemplate.variables.workspaceResourceId) {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                            }
                            # If both ID and Title exist, is standard GenericUI data connector
                            if ($templateSpecConnectorData.id -and $templateSpecConnectorData.title) {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "uiConfigId$connectorCounter" -NotePropertyValue $templateSpecConnectorData.id
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "_uiConfigId$connectorCounter" -NotePropertyValue "[variables('uiConfigId$connectorCounter')]"
                            }
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorContentId$connectorCounter" -NotePropertyValue $templateSpecConnectorData.id
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$connectorCounter" -NotePropertyValue "[variables('dataConnectorContentId$connectorCounter')]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorId$connectorCounter" -NotePropertyValue "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/dataConnectors', variables('_dataConnectorContentId$connectorCounter'))]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorId$connectorCounter" -NotePropertyValue "[variables('dataConnectorId$connectorCounter')]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorTemplateSpecName$connectorCounter" -NotePropertyValue "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentId$connectorCounter')))]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$connectorCounter" -NotePropertyValue (($null -ne $templateSpecConnectorData.metadata) ? "$($templateSpecConnectorData.metadata.version)" : "1.0.0")
                            if (!$contentToImport.TemplateSpec){
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "parentId" -NotePropertyValue $solutionId
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "_parentId" -NotePropertyValue "[variables('parentId')]"
                             };

                            # Add base templateSpec
                            $baseDataConnectorTemplateSpec = [PSCustomObject]@{
                                type       = "Microsoft.Resources/templateSpecs";
                                apiVersion = "2022-02-01";
                                name       = "[variables('dataConnectorTemplateSpecName$connectorCounter')]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "DataConnector";
                                };
                                properties = [PSCustomObject]@{
                                    description = "$($connectorName) data connector with template";
                                    displayName = "$($connectorName) template";
                                }
                            }
                            $baseMainTemplate.resources += $baseDataConnectorTemplateSpec

                            if(!$contentToImport.Is1PConnector)
                            {
                                $existingFunctionApp = $false;
                                $instructionArray = $templateSpecConnectorData.instructionSteps
                                ($instructionArray | ForEach {if($_.description -and $_.description.IndexOf('[Deploy To Azure]') -gt 0){$existingFunctionApp = $true;}})

                                if ($existingFunctionApp -eq $false)
                                {
                                    # check if only instructions object is present without any description
                                    foreach ($item in $instructionArray) 
                                    {
                                        if ($null -eq $item.description -and $item.instructions.Count -gt 0)
                                        {
                                            foreach ($instructionItem in $item.instructions)
                                            {
                                                $parameterCount = $instructionItem.parameters.Count -gt 0
                                                $parameterInstructionStepsCount = $instructionItem.parameters.instructionSteps.Count -gt 0

                                                if ($parameterCount -and $parameterInstructionStepsCount)
                                                {
                                                    foreach ($desc in $instructionItem.parameters.instructionSteps)
                                                    {
                                                        if ($desc.description && $desc.description.IndexOf('Deploy To Azure') -gt 0)
                                                        {
                                                            $existingFunctionApp = $true
                                                            break
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                if($existingFunctionApp)
                                {
                                    $templateSpecConnectorData.title = ($templateSpecConnectorData.title.Contains("using Azure Functions")) ? $templateSpecConnectorData.title : $templateSpecConnectorData.title + " (using Azure Functions)"
                                    #$templateSpecConnectorData.title = $templateSpecConnectorData.title + " (using Azure Functions)";
                                }
                            }
                            # Data Connector Content -- *Assumes GenericUI
                            if($contentToImport.Is1PConnector)
                            {
                                $1pconnectorData = $templateSpecConnectorData
                                $1pconnectorData = $1pconnectorData | Select-Object -Property id,title,publisher,descriptionMarkdown, graphQueries, connectivityCriterias,dataTypes
                            }
                            $templateSpecConnectorUiConfig = ($contentToImport.Is1PConnector -eq $true) ? $1pconnectorData : $templateSpecConnectorData
                            $templateSpecConnectorUiConfig.id = "[variables('_uiConfigId$connectorCounter')]"
                            if($contentToImport.Is1PConnector -eq $false)
                            {
                                $templateSpecConnectorUiConfig.availability.isPreview =  ($templateSpecConnectorUiConfig.availability.isPreview -eq $true) ? $false : $templateSpecConnectorUiConfig.availability.isPreview
                            }
                            $dataConnectorContent = [PSCustomObject]@{
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$connectorCounter'))]";
                                apiVersion = "2021-03-01-preview";
                                type       = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors";
                                location   = "[parameters('workspace-location')]";
                                kind       = ($contentToImport.Is1PConnector -eq $true) ? "StaticUI" : (($ccpConnector -eq $true) ? $connectorData.resources[0].kind : "GenericUI");
                                properties = [PSCustomObject]@{
                                    connectorUiConfig = $templateSpecConnectorUiConfig
                                }
                            }
                            if($null -ne $ccpPollingConfig)
                            {
                                $dataConnectorContent.properties | Add-Member -NotePropertyName "pollingConfig" -NotePropertyValue $ccpPollingConfig
                            }
                            $author = $contentToImport.Author.Split(" - ");
                            $authorDetails = [PSCustomObject]@{
                                name  = $author[0];
                            };
                            if($null -ne $author[1])
                            {
                                $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
                            }
                            $dataConnectorMetadata = [PSCustomObject]@{
                                type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                                apiVersion = "2022-01-01-preview";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('DataConnector-', last(split(variables('_dataConnectorId$connectorCounter'),'/'))))]";
                                properties = [PSCustomObject]@{
                                    parentId  = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/dataConnectors', variables('_dataConnectorContentId$connectorCounter'))]";
                                    contentId = "[variables('_dataConnectorContentId$connectorCounter')]";
                                    kind      = "DataConnector";
                                    version   = "[variables('dataConnectorVersion$connectorCounter')]";
                                    source    = [PSCustomObject]@{
                                        kind     = "Solution";
                                        name     = $contentToImport.Name;
                                        sourceId = "[variables('_solutionId')]"
                                    };
                                    author    = $authorDetails;
                                    support   = $baseMetadata.support
                                }
                            }
                            # Add templateSpecs/versions resource to hold actual content
                            $dataConnectorTemplateSpecContent = [PSCustomObject]@{
                                type       = "Microsoft.Resources/templateSpecs/versions";
                                apiVersion = "2022-02-01";
                                name       = "[concat(variables('dataConnectorTemplateSpecName$connectorCounter'),'/',variables('dataConnectorVersion$connectorCounter'))]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "DataConnector";
                                };
                                dependsOn  = @(
                                    "[resourceId('Microsoft.Resources/templateSpecs', variables('dataConnectorTemplateSpecName$connectorCounter'))]"
                                );
                                properties = [PSCustomObject]@{
                                    description  = "$($connectorName) data connector with template version $($contentToImport.Version)";
                                    mainTemplate = [PSCustomObject]@{
                                        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                        contentVersion = "[variables('dataConnectorVersion$connectorCounter')]";
                                        parameters     = [PSCustomObject]@{};
                                        variables      = [PSCustomObject]@{};
                                        resources      = @(
                                            # Data Connector
                                            $dataConnectorContent,
                                            # Metadata
                                            $dataConnectorMetadata
                                        )
                                    }
                                }
                            }
                            $baseMainTemplate.resources += $dataConnectorTemplateSpecContent

                            # Add content-metadata item, in addition to template spec metadata item
                            $dataConnectorActiveContentMetadata = [PSCustomObject]@{
                                type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                                apiVersion = "2022-01-01-preview";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('DataConnector-', last(split(variables('_dataConnectorId$connectorCounter'),'/'))))]";
                                dependsOn  = @("[variables('_dataConnectorId$connectorCounter')]");
                                location   = "[parameters('workspace-location')]";
                                properties = [PSCustomObject]@{
                                    parentId  = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/dataConnectors', variables('_dataConnectorContentId$connectorCounter'))]";
                                    contentId = "[variables('_dataConnectorContentId$connectorCounter')]";
                                    kind      = "DataConnector";
                                    version   = "[variables('dataConnectorVersion$connectorCounter')]";
                                    source    = [PSCustomObject]@{
                                        kind     = "Solution";
                                        name     = $contentToImport.Name;
                                        sourceId = "[variables('_solutionId')]"
                                    };
                                    author    = $authorDetails;
                                    support   = $baseMetadata.support
                                }
                            }
                            $baseMainTemplate.resources += $dataConnectorActiveContentMetadata
                        }
                        $connectorObj = [PSCustomObject]@{}
                        # If direct title is available, assume standard connector format
                        if ($connectorData.title) {
                            $standardConnectorUiConfig = [PSCustomObject]@{
                                title                 = $connectorData.title;
                                publisher             = $connectorData.publisher;
                                descriptionMarkdown   = $connectorData.descriptionMarkdown;
                                graphQueries          = $connectorData.graphQueries;
                                dataTypes             = $connectorData.dataTypes;
                                connectivityCriterias = $connectorData.connectivityCriterias;
                            }

                            if(!$contentToImport.Is1PConnector)
                            {
                                $standardConnectorUiConfig | Add-Member -NotePropertyName "sampleQueries" -NotePropertyValue $connectorData.sampleQueries;
                                $standardConnectorUiConfig | Add-Member -NotePropertyName "availability" -NotePropertyValue $connectorData.availability;
                                $standardConnectorUiConfig | Add-Member -NotePropertyName "permissions" -NotePropertyValue $connectorData.permissions;
                                $standardConnectorUiConfig | Add-Member -NotePropertyName "instructionSteps" -NotePropertyValue $connectorData.instructionSteps;
                            }

                            if($contentToImport.TemplateSpec){
                                $standardConnectorUiConfig | Add-Member -NotePropertyName "id" -NotePropertyValue "[variables('_uiConfigId$connectorCounter')]"

                            }

                            $connectorObj = [PSCustomObject]@{
                                name       = if ($contentToImport.TemplateSpec) { "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$connectorCounter'))]" }else { "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('connector$connectorCounter-name'))]" }
                                apiVersion = "2021-03-01-preview";
                                type       = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors";
                                location   = "[parameters('workspace-location')]";
                                kind       = ($contentToImport.Is1PConnector -eq $true) ? "StaticUI" : "GenericUI";
                                properties = [PSCustomObject]@{
                                    connectorUiConfig = $standardConnectorUiConfig
                                }
                            }

                            if(!$contentToImport.TemplateSpec)
                            {
                                $connectorObj | Add-Member -NotePropertyName "id" -NotePropertyValue "[variables('_connector$connectorCounter-source')]";
                            }
                        }
                        # This section is for CCP connectors
                        elseif ($connectorData.resources -and
                            $connectorData.resources[0] -and
                            $connectorData.resources[0].properties -and
                            $connectorData.resources[0].properties.connectorUiConfig -and
                            $connectorData.resources[0].properties.pollingConfig) {
                            # Else check if Polling connector
                            $connectorData = $connectorData.resources[0]
                            $connectorUiConfig = $connectorData.properties.connectorUiConfig
                            # $connectorUiConfig.PSObject.Properties.Remove('id')
                            $connectorUiConfig.id = if ($contentToImport.TemplateSpec) { "[variables('_uiConfigId$connectorCounter')]" }else { "[variables('_connector$connectorCounter-source')]" };

                            $connectorObj = [PSCustomObject]@{
                                # id         = if ($contentToImport.TemplateSpec) { "[variables('_uiConfigId$connectorCounter')]" }else { "[variables('_connector$connectorCounter-source')]" };
                                name       = if ($contentToImport.TemplateSpec) { "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$connectorCounter'))]" }else { "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('connector$connectorCounter-name'))]" }
                                apiVersion = "2021-03-01-preview";
                                type       = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors";
                                location   = "[parameters('workspace-location')]";
                                kind       = $connectorData.kind;
                                properties = [PSCustomObject]@{
                                    connectorUiConfig = $connectorUiConfig;
                                    pollingConfig     = $connectorData.properties.pollingConfig;
                                }
                            }
                        }
                        if ($connectorData.additionalRequirementBanner) {
                            $connectorObj.properties.connectorUiConfig | Add-Member -NotePropertyName "additionalRequirementBanner" -NotePropertyValue $connectorData.additionalRequirementBanner
                        }

                        $baseMainTemplate.resources += $connectorObj

                        $syslog = "Syslog"
                        $commonSecurityLog = "CommonSecurityLog"
                        function getConnectorDataTypes($dataTypesArray) {
                            $typeResult = "custom log"
                            foreach ($dataType in $dataTypesArray) {
                                if ($dataType.name.IndexOf($syslog) -ne -1) {
                                    $typeResult = $syslog
                                }
                                elseif ($dataType.name.IndexOf($commonSecurityLog) -ne -1) {
                                    $typeResult = $commonSecurityLog
                                }
                            }
                            return $typeResult
                        }
                        function getAllDataTypeNames($dataTypesArray) {
                            $typeResult = @()
                            foreach ($dataType in $dataTypesArray) {
                                $typeResult += $dataType.name
                            }
                            return $typeResult
                        }
                        $connectorDataType = $(getConnectorDataTypes $connectorData.dataTypes)
                        $isParserAvailable = $($contentToImport.Parsers -and ($contentToImport.Parsers.Count -gt 0))
                        $connectorDescriptionText = "This Solution installs the data connector for $solutionName. You can get $solutionName $connectorDataType data in your Microsoft Sentinel workspace. After installing the solution, configure and enable this data connector by following guidance in Manage solution view."
                        $parserText = "The Solution installs a parser that transforms the ingested data into Microsoft Sentinel normalized format. The normalized format enables better correlation of different types of data from different data sources to drive end-to-end outcomes seamlessly in security monitoring, hunting, incident investigation and response scenarios in Microsoft Sentinel."

                        $baseDataConnectorStep = [PSCustomObject] @{
                            name       = "dataconnectors";
                            label      = "Data Connectors";
                            bladeTitle = "Data Connectors";
                            elements   = @();
                        }
                        $baseDataConnectorTextElement = [PSCustomObject] @{
                            name    = "dataconnectors$connectorCounter-text";
                            type    = "Microsoft.Common.TextBlock";
                            options = [PSCustomObject] @{
                                text = $connectorDescriptionText;
                            }
                        }
                        if ($connectorCounter -eq 1) {
                            $baseCreateUiDefinition.parameters.steps += $baseDataConnectorStep
                        }
                        $currentStepNum = $baseCreateUiDefinition.parameters.steps.Count - 1
                        $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $baseDataConnectorTextElement
                        if ($connectorCounter -eq $contentToImport."Data Connectors".Count) {
                            $parserTextElement = [PSCustomObject] @{
                                name    = "dataconnectors-parser-text";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject] @{
                                    text = $parserText;
                                }
                            }
                            $connectDataSourcesLink = [PSCustomObject] @{
                                name    = "dataconnectors-link2";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject] @{
                                    link = [PSCustomObject] @{
                                        label = "Learn more about connecting data sources";
                                        uri   = "https://docs.microsoft.com/azure/sentinel/connect-data-sources";
                                    }
                                }
                            }
                            if ($isParserAvailable) {
                                $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $parserTextElement
                            }
                            $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $connectDataSourcesLink
                        }

                        # Update Connector Counter
                        $connectorCounter += 1
                    }
                    elseif ($objectKeyLowercase -eq "savedsearches") {
                        $isStandardTemplate = $false
                        $searchData = $json # Assume input is basic array of SavedSearches to start
                        # Check if SavedSearch input file uses direct structure given by export
                        if ($searchData -isnot [System.Array] -and $searchData.value) {
                            $searchData = $searchData.value
                        }
                        # Check if SavedSearch input file uses standard template structure
                        if ($searchData -isnot [System.Array] -and $searchData.resources) {
                            $isStandardTemplate = $true
                            $searchData = $searchData.resources
                        }
                        if ($searchData -is [System.Array] -and !$isStandardTemplate) {
                            foreach ($search in $searchData) {
                                $savedSearchIdParameterName = "savedsearch$savedSearchCounter-id"
                                $savedSearchIdParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the watchlist" }; }
                                $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $savedSearchIdParameterName -Value $savedSearchIdParameter

                                $savedSearchResource = [PSCustomObject]@{
                                    type       = "Microsoft.OperationalInsights/workspaces/savedSearches";
                                    apiVersion = "2020-08-01";
                                    name       = "[concat(parameters('workspace'),'/',parameters('$savedSearchIdParameterName'))]";
                                    properties = [PSCustomObject]@{
                                        category      = $search.properties.category;
                                        displayName   = $search.properties.displayName;
                                        query         = $search.properties.query;
                                        functionAlias = $search.properties.functionAlias;
                                        version       = $search.properties.version;
                                    };
                                }
                                $baseMainTemplate.resources += $savedSearchResource
                                $savedSearchCounter++
                            }
                        }
                        elseif ($isStandardTemplate) {
                            $baseMainTemplate.resources += $searchData
                        }
                    }
                    elseif ($objectKeyLowercase -eq "watchlists") {
                        $watchlistData = $json.resources[0]

                        $watchlistName = $watchlistData.properties.displayName;
                        if ($contentToImport.Metadata) {
                            $baseMainTemplate.variables | Add-Member -NotePropertyName $watchlistName -NotePropertyValue $watchlistName
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_$watchlistName" -NotePropertyValue "[variables('$watchlistName')]"
                        }

                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = "Watchlist";
                            contentId = "[variables('_$watchlistName')]";
                            version   = $contentToImport.Version;
                        };

                        #Handle CreateUiDefinition Base Step
                        if ($watchlistCounter -eq 1) {
                            $baseWatchlistStep = [PSCustomObject]@{
                                name       = "watchlists";
                                label      = "Watchlists";
                                subLabel   = [PSCustomObject]@{
                                    preValidation  = "Configure the watchlists";
                                    postValidation = "Done";
                                }
                                bladeTitle = "Watchlists";
                                elements   = @(
                                    [PSCustomObject]@{
                                        name    = "watchlists-text";
                                        type    = "Microsoft.Common.TextBlock";
                                        options = [PSCustomObject]@{
                                            text = "Microsoft Sentinel watchlists enable the collection of data from external data sources for correlation with the events in your Microsoft Sentinel environment. Once created, you can use watchlists in your search, detection rules, threat hunting, and response playbooks. Watchlists are stored in your Microsoft Sentinel workspace as name-value pairs and are cached for optimal query performance and low latency. Once deployment is successful, the installed watchlists will be available in the Watchlists blade under 'My Watchlists'.";
                                            link = [PSCustomObject]@{
                                                label = "Learn more";
                                                uri   = "https://aka.ms/sentinelwatchlists";
                                            }
                                        }
                                    }
                                )
                            }
                            $baseCreateUiDefinition.parameters.steps += $baseWatchlistStep
                        }

                        #Handle CreateUiDefinition Step Sub-Element
                        $watchlistDescriptionText = $(if ($contentToImport.WatchlistDescription -and $contentToImport.WatchlistDescription -is [System.Array]) { $contentToImport.WatchlistDescription[$watchlistCounter - 1] } elseif ($contentToImport.WatchlistDescription -and $contentToImport.WatchlistDescription -is [System.String]) { $contentToImport.WatchlistDescription } else { $watchlistData.properties.description })
                        $currentStepNum = $baseCreateUiDefinition.parameters.steps.Count - 1
                        $watchlistStepElement = [PSCustomObject]@{
                            name     = "watchlist$watchlistCounter";
                            type     = "Microsoft.Common.Section";
                            label    = $watchlistData.properties.displayName;
                            elements = @(
                                [PSCustomObject]@{
                                    name    = "watchlist$watchlistCounter-text";
                                    type    = "Microsoft.Common.TextBlock";
                                    options = [PSCustomObject]@{
                                        text = $watchlistDescriptionText
                                    }
                                }
                            )
                        }
                        $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $watchlistStepElement

                        # Add Watchlist ID to MainTemplate parameters
                        $watchlistIdParameterName = "watchlist$watchlistCounter-id"
                        $watchlistIdParameter = [PSCustomObject] @{ type = "string"; defaultValue = "$($watchlistData.properties.watchlistAlias)"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the watchlist" }; }
                        $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $watchlistIdParameterName -Value $watchlistIdParameter

                        # Replace watchlist resource id
                        $watchlistData.name = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('watchlist$watchlistCounter-id'))]"

                        # Handle MainTemplate Resource
                        $baseMainTemplate.resources += $watchlistData #Assume 1 watchlist per template

                        # Update Watchlist Counter
                        $watchlistCounter += 1
                    }
                }
                else {
                    if ($file -match "(\.yaml)$") {
                        $objectKeyLowercase = $objectProperties.Name.ToLower()
                        if ($objectKeyLowercase -eq "hunting queries") {
                            Write-Host "Generating Hunting Query using $file"
                            $content = ''
                            foreach ($line in $rawData) {
                                $content = $content + "`n" + $line
                            }
                            try {
                                $yaml = ConvertFrom-YAML $content
                            }
                            catch {
                                Write-Host "Failed to deserialize $file" -ForegroundColor Red
                                break;
                            }

                            $fileName = Split-Path $file -leafbase;
                            $fileName = $fileName + "_HuntingQueries";
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQueryVersion$huntingQueryCounter" -NotePropertyValue (($null -ne $yaml.version) ? "$($yaml.version)" : "1.0.0")
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQuerycontentId$huntingQueryCounter" -NotePropertyValue $yaml.id
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_huntingQuerycontentId$huntingQueryCounter" -NotePropertyValue "[variables('huntingQuerycontentId$huntingQueryCounter')]"
                            $DependencyCriteria += [PSCustomObject]@{
                                kind      = "HuntingQuery";
                                contentId = "[variables('_huntingQuerycontentId$huntingQueryCounter')]";
                                version   = "[variables('huntingQueryVersion$huntingQueryCounter')]";
                            };

                            if ($huntingQueryCounter -eq 1) {
                                if (!$(queryResourceExists) -and !$contentToImport.TemplateSpec) {
                                    $baseHuntingQueryResource = [PSCustomObject] @{
                                        type       = "Microsoft.OperationalInsights/workspaces";
                                        apiVersion = "2021-06-01";
                                        name       = "[parameters('workspace')]";
                                        location   = "[parameters('workspace-location')]";
                                        resources  = @()
                                    }
                                    $baseMainTemplate.resources += $baseHuntingQueryResource
                                }
                                if (!$contentToImport.TemplateSpec -and $null -eq $baseMainTemplate.variables.'workspace-dependency') {
                                    #Add parser dependency variable once to ensure validation passes.
                                    $baseMainTemplate.variables | Add-Member -MemberType NoteProperty -Name "workspace-dependency" -Value "[concat('Microsoft.OperationalInsights/workspaces/', parameters('workspace'))]"
                                }
                                $huntingQueryBaseStep = [PSCustomObject] @{
                                    name       = "huntingqueries";
                                    label      = "Hunting Queries";
                                    bladeTitle = "Hunting Queries";
                                    elements   = @(
                                        [PSCustomObject] @{
                                            name    = "huntingqueries-text";
                                            type    = "Microsoft.Common.TextBlock";
                                            options = [PSCustomObject] @{
                                                    text = $contentToImport.HuntingQueryBladeDescription ? $contentToImport.HuntingQueryBladeDescription : "This solution installs the following hunting queries. After installing the solution, run these hunting queries to hunt for threats in Manage solution view. ";
                                                }
                                            },
                                            [PSCustomObject] @{
                                                name    = "huntingqueries-link";
                                                type    = "Microsoft.Common.TextBlock";
                                                options = [PSCustomObject] @{
                                                    link = [PSCustomObject] @{
                                                        label = "Learn more";
                                                        uri   = "https://docs.microsoft.com/azure/sentinel/hunting"
                                                    }
                                                }
                                            })
                                }
                                $baseCreateUiDefinition.parameters.steps += $huntingQueryBaseStep
                            }

                            if($yaml.metadata -and $yaml.metadata.source -and $yaml.metadata.source.kind -and ($yaml.metadata.source.kind -eq "Community" -or $yaml.metadata.source.kind -eq "Standalone"))
                            {
                                throw "The file $fileName has metadata with source -> kind = Community | Standalone. Please remove it so that it can be packaged as a solution."
                            }

                            $huntingQueryObj = [PSCustomObject] @{
                                type       = $contentToImport.TemplateSpec ? "Microsoft.OperationalInsights/savedSearches" : "savedSearches";
                                apiVersion = "2020-08-01";
                                name       = $contentToImport.TemplateSpec ? "$($solutionName.Replace(' ', '_'))_Hunting_Query_$huntingQueryCounter" : "$solutionName Hunting Query $huntingQueryCounter";
                                location   = "[parameters('workspace-location')]";
                                properties = [PSCustomObject] @{
                                    eTag        = "*";
                                    displayName = $yaml.name;
                                    category    = "Hunting Queries";
                                    query       = $yaml.query;
                                    version     = $contentToImport.TemplateSpec ? 2 : 1;
                                    tags        = @();
                                }
                            }

                            $huntingQueryDescription = ""
                            if ($yaml.description) {
                                $huntingQueryDescription = $yaml.description.Trim();
                                if($huntingQueryDescription.StartsWith("'"))
                                {
                                    $huntingQueryDescription = $huntingQueryDescription.substring(1, $huntingQueryDescription.length-1)
                                }

                                if($huntingQueryDescription.EndsWith("'"))
                                {
                                    $huntingQueryDescription = $huntingQueryDescription.substring(0, $huntingQueryDescription.length-1)
                                }

                                $descriptionObj = [PSCustomObject]@{
                                    name  = "description";
                                    value = $huntingQueryDescription
                                }
                                $huntingQueryObj.properties.tags += $descriptionObj
                                $huntingQueryDescription = "$huntingQueryDescription "
                            }
                            if ($yaml.tactics -and $yaml.tactics.Count -gt 0) {
                                $tacticsObj = [PSCustomObject]@{
                                    name  = "tactics";
                                    value = $yaml.tactics -join ","
                                }
                                if ($tacticsObj.value.ToString() -match ' ') {
                                    $tacticsObj.value = $tacticsObj.value -replace ' ', ''
                                }
                                $huntingQueryObj.properties.tags += $tacticsObj
                            }

                            if ($yaml.relevantTechniques -and $yaml.relevantTechniques.Count -gt 0) {
                                $relevantTechniquesObj = [PSCustomObject]@{
                                    name  = "techniques";
                                    value = $yaml.relevantTechniques -join ","
                                }
                                if ($relevantTechniquesObj.value.ToString() -match ' ') {
                                    $relevantTechniquesObj.value = $relevantTechniquesObj.value -replace ' ', ''
                                }
                                $huntingQueryObj.properties.tags += $relevantTechniquesObj
                            }

                            if($contentToImport.TemplateSpec) {

                                $baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQueryId$huntingQueryCounter" -NotePropertyValue "[resourceId('Microsoft.OperationalInsights/savedSearches', variables('_huntingQuerycontentId$huntingQueryCounter'))]"
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQueryTemplateSpecName$huntingQueryCounter" -NotePropertyValue "[concat(parameters('workspace'),'-hq-',uniquestring(variables('_huntingQuerycontentId$huntingQueryCounter')))]"
                                if (!$baseMainTemplate.variables.workspaceResourceId) {
                                    $baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                                }

                                $baseHuntingQueryTemplateSpec = [PSCustomObject]@{
                                    type       = "Microsoft.Resources/templateSpecs";
                                    apiVersion = "2022-02-01";
                                    name       = "[variables('huntingQueryTemplateSpecName$huntingQueryCounter')]";
                                    location   = "[parameters('workspace-location')]";
                                    tags       = [PSCustomObject]@{
                                        "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                        "hidden-sentinelContentType" = "HuntingQuery";
                                    };
                                    properties = [PSCustomObject]@{
                                        description = "$($solutionName) Hunting Query $huntingQueryCounter with template";
                                        displayName = "$($solutionName) Hunting Query template";
                                    }
                                }
                                if($baseHuntingQueryTemplateSpec.properties.displayName.length -ge 64){
                                    $baseHuntingQueryTemplateSpec.properties.displayName = "$($solutionName) HQ template";
                                }

                                $baseMainTemplate.resources += $baseHuntingQueryTemplateSpec
                                $author = $contentToImport.Author.Split(" - ");
                                $authorDetails = [PSCustomObject]@{
                                    name  = $author[0];
                                };
                                if($null -ne $author[1])
                                {
                                     $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
                                }

                                $huntingQueryMetadata = [PSCustomObject]@{
                                    type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                                    apiVersion = "2022-01-01-preview";
                                    name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('HuntingQuery-', last(split(variables('huntingQueryId$huntingQueryCounter'),'/'))))]";
                                    properties = [PSCustomObject]@{
                                        description = "$($solutionName) Hunting Query $huntingQueryCounter";
                                        parentId  = "[variables('huntingQueryId$huntingQueryCounter')]";
                                        contentId = "[variables('_huntingQuerycontentId$huntingQueryCounter')]";
                                        kind      = "HuntingQuery";
                                        version   = "[variables('huntingQueryVersion$huntingQueryCounter')]";
                                        source    = [PSCustomObject]@{
                                            kind     = "Solution";
                                            name     = $contentToImport.Name;
                                            sourceId = "[variables('_solutionId')]"
                                        };
                                        author    = $authorDetails;
                                        support   = $baseMetadata.support
                                    }
                                }

                                 # Add templateSpecs/versions resource to hold actual content
                                $huntingQueryTemplateSpecContent = [PSCustomObject]@{
                                    type       = "Microsoft.Resources/templateSpecs/versions";
                                    apiVersion = "2022-02-01";
                                    name       = "[concat(variables('huntingQueryTemplateSpecName$huntingQueryCounter'),'/',variables('huntingQueryVersion$huntingQueryCounter'))]";
                                    location   = "[parameters('workspace-location')]";
                                    tags       = [PSCustomObject]@{
                                        "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                        "hidden-sentinelContentType" = "HuntingQuery";
                                    };
                                    dependsOn  = @(
                                        "[resourceId('Microsoft.Resources/templateSpecs', variables('huntingQueryTemplateSpecName$huntingQueryCounter'))]"
                                    );
                                    properties = [PSCustomObject]@{
                                        description  = "$($fileName) Hunting Query with template version $($contentToImport.Version)";
                                        mainTemplate = [PSCustomObject]@{
                                            '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                            contentVersion = "[variables('huntingQueryVersion$huntingQueryCounter')]";
                                            parameters     = [PSCustomObject]@{};
                                            variables      = [PSCustomObject]@{};
                                            resources      = @(
                                                # workbook
                                                $huntingQueryObj,
                                                # Metadata
                                                $huntingQueryMetadata
                                            )
                                        }
                                    }
                                }
                                $baseMainTemplate.resources += $huntingQueryTemplateSpecContent
                            }
                            else{
                                if(!$contentToImport.TemplateSpec)
                                {
                                    $dependsOn  = @(
                                        "[variables('workspace-dependency')]"
                                    );

                                    $huntingQueryObj | Add-Member -NotePropertyName "dependsOn" -NotePropertyValue $dependsOn
                                }
                                $baseMainTemplate.resources[$(getQueryResourceLocation)].resources += $huntingQueryObj
                            }
                            $dependencyDescription = ""
                            if ($yaml.requiredDataConnectors) {
                                # $dependencyDescription = "It depends on the $($yaml.requiredDataConnectors.connectorId) data connector and $($($yaml.requiredDataConnectors.dataTypes)) data type and $($yaml.requiredDataConnectors.connectorId) parser."
                                $dependencyDescription = "This hunting query depends on $($yaml.requiredDataConnectors.connectorId) data connector ($($($yaml.requiredDataConnectors.dataTypes)) Parser or Table)"
                            }
                            $huntingQueryElement = [PSCustomObject]@{
                                name     = "huntingquery$huntingQueryCounter";
                                type     = "Microsoft.Common.Section";
                                label    = $yaml.name;
                                elements = @()
                            }
                            $huntingQueryElementDescription = [PSCustomObject]@{
                                name    = "huntingquery$huntingQueryCounter-text";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject]@{
                                    text = "$($huntingQueryDescription)$dependencyDescription";
                                }
                            }
                            if ($huntingQueryDescription -or $dependencyDescription) {
                                $huntingQueryElement.elements += $huntingQueryElementDescription
                            }
                            $baseCreateUiDefinition.parameters.steps[$baseCreateUiDefinition.parameters.steps.Count - 1].elements += $huntingQueryElement

                            # Update HuntingQuery Counter
                            $huntingQueryCounter += 1
                        }
                        else {
                            # If yaml and not hunting query, process as Alert Rule
                            Write-Host "Generating Alert Rule using $file"
                            if ($analyticRuleCounter -eq 1) {
                                $baseAnalyticRuleStep = [PSCustomObject] @{
                                    name       = "analytics";
                                    label      = "Analytics";
                                    subLabel   = [PSCustomObject] @{
                                        preValidation  = "Configure the analytics";
                                        postValidation = "Done";
                                    };
                                    bladeTitle = "Analytics";
                                    elements   = @(
                                        [PSCustomObject] @{
                                            name    = "analytics-text";
                                            type    = "Microsoft.Common.TextBlock";
                                            options = [PSCustomObject] @{
                                                text = $contentToImport.AnalyticalRuleBladeDescription ? $contentToImport.AnalyticalRuleBladeDescription : "This solution installs the following analytic rule templates. After installing the solution, create and enable analytic rules in Manage solution view.";
                                            }
                                        },
                                        [PSCustomObject] @{
                                            name    = "analytics-link";
                                            type    = "Microsoft.Common.TextBlock";
                                            options = [PSCustomObject] @{
                                                link = [PSCustomObject] @{
                                                    label = "Learn more";
                                                    uri   = "https://docs.microsoft.com/azure/sentinel/tutorial-detect-threats-custom?WT.mc_id=Portal-Microsoft_Azure_CreateUIDef";
                                                }
                                            }
                                        }
                                    )
                                }
                                $baseCreateUiDefinition.parameters.steps += $baseAnalyticRuleStep
                            }
                            $yamlPropertiesToCopyFrom = "name", "severity", "triggerThreshold", "query"
                            $yamlPropertiesToCopyTo = "displayName", "severity", "triggerThreshold", "query"
                            $alertRuleParameterName = "analytic$analyticRuleCounter-id"
                            $alertRule = [PSCustomObject] @{ description = ""; displayName = ""; enabled = $false; query = ""; queryFrequency = ""; queryPeriod = ""; severity = ""; suppressionDuration = ""; suppressionEnabled = $false; triggerOperator = ""; triggerThreshold = 0; }
                            $alertRuleParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the scheduled alert rule" }; }
                            $content = ''

                            $fileName = Split-Path $file -leafbase;
                            $fileName = $fileName + "_AnalyticalRules";
                            foreach ($line in $rawData) {
                                $content = $content + "`n" + $line
                            }
                            try {
                                $yaml = ConvertFrom-YAML $content # Convert YAML to PSObject
                            }
                            catch {
                                Write-Host "Failed to deserialize $file" -ForegroundColor Red
                                break;
                            }

                            if($yaml.metadata -and $yaml.metadata.source -and $yaml.metadata.source.kind -and ($yaml.metadata.source.kind -eq "Community" -or $yaml.metadata.source.kind -eq "Standalone"))
                            {
                                throw "The file $fileName has metadata with source -> kind = Community | Standalone. Please remove it so that it can be packaged as a solution."
                            }

                            $baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRuleVersion$analyticRuleCounter" -NotePropertyValue (($null -ne $yaml.version) ? "$($yaml.version)" : "1.0.0")
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRulecontentId$analyticRuleCounter" -NotePropertyValue "$($yaml.id)"
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "_analyticRulecontentId$analyticRuleCounter" -NotePropertyValue "[variables('analyticRulecontentId$analyticRuleCounter')]"
                            $DependencyCriteria += [PSCustomObject]@{
                                kind      = "AnalyticsRule";
                                contentId = "[variables('analyticRulecontentId$analyticRuleCounter')]";
                                #post bug bash ,remove this below comments!
                                version   = "[variables('analyticRuleVersion$analyticRuleCounter')]";
                            };
                            # Copy all directly transposable properties
                            foreach ($yamlProperty in $yamlPropertiesToCopyFrom) {
                                $index = $yamlPropertiesToCopyFrom.IndexOf($yamlProperty)
                                $alertRule.$($yamlPropertiesToCopyTo[$index]) = $yaml.$yamlProperty
                            }

                            if($contentToImport.TemplateSpec)
                            {
                                $alertRule | Add-Member -NotePropertyName status -NotePropertyValue ($yaml.status ? $yaml.status : "Available") # Add requiredDataConnectors property if exists
                            }
                            

                            if($yaml.requiredDataConnectors -and $yaml.requiredDataConnectors.count -gt 0)
                            {
                                $alertRule | Add-Member -NotePropertyName requiredDataConnectors -NotePropertyValue $yaml.requiredDataConnectors # Add requiredDataConnectors property if exists
                                for($i=0; $i -lt $yaml.requiredDataConnectors.connectorId.count; $i++)
                                {
                                    $alertRule.requiredDataConnectors[$i].connectorId = ($yaml.requiredDataConnectors[$i].connectorId.GetType().Name -is [object]) ? ($yaml.requiredDataConnectors[$i].connectorId -join ',') : $yaml.requiredDataConnectors[$i].connectorId;
                                }
                            }
                            else
                            {
                                $alertRule | Add-Member -NotePropertyName requiredDataConnectors -NotePropertyValue "[variables('TemplateEmptyArray')]";
                                    if (!$baseMainTemplate.variables.TemplateEmptyArray) {                                        
                                        $baseMainTemplate.variables | Add-Member -NotePropertyName "TemplateEmptyArray" -NotePropertyValue "[json('[]')]"
                                        }
                            }

                            if (!$yaml.severity) {
                                $alertRule.severity = "Medium"
                            }

                            # Content Modifications
                            $triggerOperators = [PSCustomObject] @{ gt = "GreaterThan" ; lt = "LessThan" ; eq = "Equal" ; ne = "NotEqual"; GreaterThan = "GreaterThan" ; LessThan = "LessThan" ; Equal = "Equal" ; NotEqual = "NotEqual" }
                            $alertRule.triggerOperator = $triggerOperators.$($yaml.triggerOperator)
                            if ($yaml.tactics -and ($yaml.tactics.Count -gt 0) ) {
                                if ($yaml.tactics -match ' ') {
                                    $yaml.tactics = $yaml.tactics -replace ' ', ''
                                }
                                $alertRule | Add-Member -NotePropertyName tactics -NotePropertyValue $yaml.tactics # Add Tactics property if exists
                            }
                            if ($yaml.relevantTechniques -and ($yaml.relevantTechniques.Count -gt 0) ) {
                                if ($yaml.relevantTechniques -match ' ') {
                                    $yaml.relevantTechniques = $yaml.relevantTechniques -replace ' ', ''
                                }
                                $alertRule | Add-Member -NotePropertyName techniques -NotePropertyValue ([array]($yaml.relevantTechniques | ForEach-Object { ($_ -split "\.")[0] })) # Add relevantTechniques property if exists
                            }
                           
                            $alertRule.description = $yaml.description.TrimEnd() #remove newlines at the end of the string if there are any.
                            if ($alertRule.description.StartsWith("'") -or $alertRule.description.StartsWith('"')) {
                                # Remove surrounding single-quotes (') from YAML block literal string, in case the string starts with a single quote in Yaml.
                                # This block is for backwards compatibility as YAML doesn't require having strings quotes by single (or double) quotes
                                $alertRule.description = $alertRule.description.substring(1, $alertRule.description.length - 2)
                            }

                            # Check whether Day or Hour/Minut format need be used
                            function checkISO8601Format($field) {
                                if ($field.IndexOf("D") -ne -1) {
                                    return "P$field"
                                }
                                else {
                                    "PT$field"
                                }
                            }
                            function Remove-EmptyArrays($Object) {
                                (@($Object).GetEnumerator() | ? {
                                    if($_.GetType().fullname -eq "System.Collections.Hashtable"){
                                        -not $_.Values
                                    }
                                    else
                                    {
                                      -not $_.Value
                                    }
                                }) |
                                % {
                                    $Object.Remove($_.Name)
                                }
                                return $Object;
                            }
                            if($yaml.kind.ToUpper() -eq "Scheduled")
                            {
                                $alertRule.queryFrequency =  $(checkISO8601Format $yaml.queryFrequency.ToUpper())
                                $alertRule.queryPeriod = $(checkISO8601Format $yaml.queryPeriod.ToUpper())
                            }
                            else {
                                $alertRule.PSObject.Properties.Remove('queryFrequency');
                                $alertRule.PSObject.Properties.Remove('queryPeriod');
                                $alertRule.PSObject.Properties.Remove('triggerOperator');
                                $alertRule.PSObject.Properties.Remove('triggerThreshold');
                            }
                            $alertRule.suppressionDuration = "PT1H"
                            # Handle optional fields
                            foreach ($yamlField in @("entityMappings", "eventGroupingSettings", "customDetails", "alertDetailsOverride", "incidentConfiguration", "sentinelEntitiesMappings")) {
                                if ($yaml.$yamlField) {
                                    $alertRule | Add-Member -MemberType NoteProperty -Name $yamlField -Value $(Remove-EmptyArrays $yaml.$yamlField)

                                    if($yamlField -eq "entityMappings" -and $yaml.$yamlField.length -lt 2)
                                    {
                                        $alertRule.entityMappings = @($alertRule.entityMappings);
                                    }
                                }
                            }
                            # Create Alert Rule Resource Object
                            $newAnalyticRule = [PSCustomObject]@{
                                type       = $contentToImport.TemplateSpec ? "Microsoft.SecurityInsights/AlertRuleTemplates" : "Microsoft.OperationalInsights/workspaces/providers/alertRules";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('analytic$analyticRuleCounter-id'))]";
                                apiVersion = "2022-04-01-preview";
                                kind       =  "$($yaml.kind)";
                                location   = "[parameters('workspace-location')]";
                                properties = $alertRule;
                            }

                            if($contentToImport.TemplateSpec) {

                                $baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRuleId$analyticRuleCounter" -NotePropertyValue "[resourceId('Microsoft.SecurityInsights/AlertRuleTemplates', variables('analyticRulecontentId$analyticRuleCounter'))]"
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRuleTemplateSpecName$analyticRuleCounter" -NotePropertyValue "[concat(parameters('workspace'),'-ar-',uniquestring(variables('_analyticRulecontentId$analyticRuleCounter')))]"
                                if (!$baseMainTemplate.variables.workspaceResourceId) {
                                    $baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                                }

                                $baseAnalyticRuleTemplateSpec = [PSCustomObject]@{
                                    type       = "Microsoft.Resources/templateSpecs";
                                    apiVersion = "2022-02-01";
                                    name       = "[variables('analyticRuleTemplateSpecName$analyticRuleCounter')]";
                                    location   = "[parameters('workspace-location')]";
                                    tags       = [PSCustomObject]@{
                                        "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                        "hidden-sentinelContentType" = "AnalyticsRule";
                                    };
                                    properties = [PSCustomObject]@{
                                        description = "$($solutionName) Analytics Rule $analyticRuleCounter with template";
                                        displayName = "$($solutionName) Analytics Rule template";
                                    }
                                }
                                if($baseAnalyticRuleTemplateSpec.properties.displayName.length -ge 64){
                                    $baseAnalyticRuleTemplateSpec.properties.displayName = "$($solutionName) AR template";
                                }

                                $newAnalyticRule.name = "[variables('AnalyticRulecontentId$analyticRuleCounter')]"
                                $baseMainTemplate.resources += $baseAnalyticRuleTemplateSpec
                                $author = $contentToImport.Author.Split(" - ");
                                $authorDetails = [PSCustomObject]@{
                                    name  = $author[0];
                                };
                                if($null -ne $author[1])
                                {
                                     $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
                                }

                                $analyticRuleMetadata = [PSCustomObject]@{
                                    type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                                    apiVersion = "2022-01-01-preview";
                                    name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('AnalyticsRule-', last(split(variables('analyticRuleId$analyticRuleCounter'),'/'))))]";
                                    properties = [PSCustomObject]@{
                                        description = "$($solutionName) Analytics Rule $analyticRuleCounter";
                                        parentId  = "[variables('analyticRuleId$analyticRuleCounter')]";
                                        contentId = "[variables('_analyticRulecontentId$analyticRuleCounter')]";
                                        kind      = "AnalyticsRule";
                                        # Need to remove the below assigned property for the yaml version after bug bash
                                        version   = "[variables('analyticRuleVersion$analyticRuleCounter')]";
                                        source    = [PSCustomObject]@{
                                            kind     = "Solution";
                                            name     = $contentToImport.Name;
                                            sourceId = "[variables('_solutionId')]"
                                        };
                                        author    = $authorDetails;
                                        support   = $baseMetadata.support
                                    }
                                }

                                 # Add templateSpecs/versions resource to hold actual content
                                $analyticRuleTemplateSpecContent = [PSCustomObject]@{
                                    type       = "Microsoft.Resources/templateSpecs/versions";
                                    apiVersion = "2022-02-01";
                                    name       = "[concat(variables('analyticRuleTemplateSpecName$analyticRuleCounter'),'/',variables('analyticRuleVersion$analyticRuleCounter'))]";
                                    location   = "[parameters('workspace-location')]";
                                    tags       = [PSCustomObject]@{
                                        "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                        "hidden-sentinelContentType" = "AnalyticsRule";
                                    };
                                    dependsOn  = @(
                                        "[resourceId('Microsoft.Resources/templateSpecs', variables('analyticRuleTemplateSpecName$analyticRuleCounter'))]"
                                    );
                                    properties = [PSCustomObject]@{
                                        description  = "$($fileName) Analytics Rule with template version $($contentToImport.Version)";
                                        mainTemplate = [PSCustomObject]@{
                                            '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                            contentVersion = "[variables('analyticRuleVersion$analyticRuleCounter')]";
                                            parameters     = [PSCustomObject]@{};
                                            variables      = [PSCustomObject]@{};
                                            resources      = @(
                                                # Analytics Rule
                                                $newAnalyticRule,
                                                # Metadata
                                                $analyticRuleMetadata
                                            )
                                        }
                                    }
                                }
                                $baseMainTemplate.resources += $analyticRuleTemplateSpecContent
                            }
                            else {
                                # Add Resource and Parameters to Template
                                $baseMainTemplate.resources += $newAnalyticRule
                            }

                            if(!$contentToImport.TemplateSpec)
                            {
                                $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $alertRuleParameterName -Value $alertRuleParameter
                            }
                            $alertRuleUIParameter = [PSCustomObject] @{ name = "analytic$analyticRuleCounter"; type = "Microsoft.Common.Section"; label = $alertRule.displayName; elements = @( [PSCustomObject] @{ name = "analytic$analyticRuleCounter-text"; type = "Microsoft.Common.TextBlock"; options = @{ text = $alertRule.description; } } ) }
                            $baseCreateUiDefinition.parameters.steps[$baseCreateUiDefinition.parameters.steps.Count - 1].elements += $alertRuleUIParameter

                            # Update Counter
                            $analyticRuleCounter += 1
                        }
                    }
                    else {
                        # Assume file is Parser due to parsers having inconsistent types. (.txt, .kql, or none)
                        Write-Host "Generating Data Parser using $file"
                        if ($parserCounter -eq 1 -and $null -eq $baseMainTemplate.variables.'workspace-dependency' -and !$contentToImport.TemplateSpec) {
                            # Add parser dependency variable once to ensure validation passes.
                            $baseMainTemplate.variables | Add-Member -MemberType NoteProperty -Name "workspace-dependency" -Value "[concat('Microsoft.OperationalInsights/workspaces/', parameters('workspace'))]"
                        }

                        $fileName = Split-Path $file -leafbase;

                        function getFileNameFromPath ($inputFilePath) {
                            # Split out path
                            $output = $inputFilePath.Split("/")
                            $output = $output[$output.Length - 1]

                            # Split out file type
                            $output = $output.Split(".")[0]
                            return $output
                        }
                        $content = ''
                        $rawData = $rawData.Split("`n")
                        foreach ($line in $rawData) {
                            # Remove comment lines before condensing query
                            if (!$line.StartsWith("//")) {
                                $content = $content + "`n" + $line
                            }
                        }

                        # Use File Name as Parser Name
                        $functionAlias = getFileNameFromPath $file
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "parserVersion$parserCounter" -NotePropertyValue "1.0.0"
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "parserContentId$parserCounter" -NotePropertyValue "$($functionAlias)-Parser"
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "_parserContentId$parserCounter" -NotePropertyValue "[variables('parserContentId$parserCounter')]"
                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = "Parser";
                            contentId = "[variables('_parserContentId$parserCounter')]";
                            version   = "[variables('parserVersion$parserCounter')]";
                        };

                        if($contentToImport.TemplateSpec) {
                            $displayDetails = getParserDetails $solutionId

                            $baseMainTemplate.variables | Add-Member -NotePropertyName "parserName$parserCounter" -NotePropertyValue "$($displayDetails.name)"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_parserName$parserCounter" -NotePropertyValue "[concat(parameters('workspace'),'/',variables('parserName$parserCounter'))]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "parserId$parserCounter" -NotePropertyValue "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', parameters('workspace'), variables('parserName$parserCounter'))]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_parserId$parserCounter" -NotePropertyValue "[variables('parserId$parserCounter')]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "parserTemplateSpecName$parserCounter" -NotePropertyValue "[concat(parameters('workspace'),'-pr-',uniquestring(variables('_parserContentId$parserCounter')))]"
                            # Add workspace resource ID if not available
                            if (!$baseMainTemplate.variables.workspaceResourceId) {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                            }
                            # Add base templateSpec
                            $baseParserTemplateSpec = [PSCustomObject]@{
                                type       = "Microsoft.Resources/templateSpecs";
                                apiVersion = "2022-02-01";
                                name       = "[variables('parserTemplateSpecName$parserCounter')]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "Parser";
                                };
                                properties = [PSCustomObject]@{
                                    description = "$($fileName) Data Parser with template";
                                    displayName = "$($fileName) Data Parser template";
                                }
                            }
                            $baseMainTemplate.resources += $baseParserTemplateSpec

                            # Parser Content
                            $parserContent = [PSCustomObject]@{
                                name       = "[variables('_parserName$parserCounter')]";
                                apiVersion = "2020-08-01";
                                type       = "Microsoft.OperationalInsights/workspaces/savedSearches";
                                location   = "[parameters('workspace-location')]";
                                properties = [PSCustomObject]@{
                                    eTag          = "*"
                                    displayName   = "$($displayDetails.displayName)"
                                    category      = "Samples"
                                    functionAlias = "$($displayDetails.functionAlias)"
                                    query         = "$content"
                                    version       = 1
                                    tags          = @([PSCustomObject]@{
                                        "name"  = "description"
                                        "value" = "$($displayDetails.displayName)"
                                        };
                                    )
                                }
                            }

                            $author = $contentToImport.Author.Split(" - ");
                            $authorDetails = [PSCustomObject]@{
                                name  = $author[0];
                            };
                            if($null -ne $author[1])
                            {
                                 $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
                            }
                            $parserMetadata = [PSCustomObject]@{
                                type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                                apiVersion = "2022-01-01-preview";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('Parser-', last(split(variables('_parserId$parserCounter'),'/'))))]";
                                dependsOn  =  @(
                                    "[variables('_parserId$parserCounter')]"
                                );
                                properties = [PSCustomObject]@{
                                    parentId  = "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', parameters('workspace'), variables('parserName$parserCounter'))]"
                                    contentId = "[variables('_parserContentId$parserCounter')]";
                                    kind      = "Parser";
                                    version   = "[variables('parserVersion$parserCounter')]";
                                    source    = [PSCustomObject]@{
                                        name     = $contentToImport.Name;
                                        kind     = "Solution";
                                        sourceId = "[variables('_solutionId')]"
                                    };
                                    author    = $authorDetails;
                                    support   = $baseMetadata.support
                                }
                            }

                            # Add templateSpecs/versions resource to hold actual content
                            $parserTemplateSpecContent = [PSCustomObject]@{
                                type       = "Microsoft.Resources/templateSpecs/versions";
                                apiVersion = "2022-02-01";
                                name       = "[concat(variables('parserTemplateSpecName$parserCounter'),'/',variables('parserVersion$parserCounter'))]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "Parser";
                                };
                                dependsOn  = @(
                                    "[resourceId('Microsoft.Resources/templateSpecs', variables('parserTemplateSpecName$parserCounter'))]"
                                );
                                properties = [PSCustomObject]@{
                                    description  = "$($fileName) Data Parser with template version $($contentToImport.Version)";
                                    mainTemplate = [PSCustomObject]@{
                                        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                        contentVersion = "[variables('parserVersion$parserCounter')]";
                                        parameters     = [PSCustomObject]@{};
                                        variables      = [PSCustomObject]@{};
                                        resources      = @(
                                            # Parser
                                            $parserContent,
                                            # Metadata
                                            $parserMetadata
                                        )
                                    }
                                }
                            }
                            $baseMainTemplate.resources += $parserTemplateSpecContent

                            $parserObj = [PSCustomObject] @{
                                type       = "Microsoft.OperationalInsights/workspaces/savedSearches";
                                apiVersion = "2021-06-01";
                                name       = "[variables('_parserName$parserCounter')]";
                                location   = "[parameters('workspace-location')]";
                                properties = [PSCustomObject] @{
                                    eTag          = "*";
                                    displayName   = "$($displayDetails.displayName)";
                                    category      = "Samples";
                                    functionAlias = "$($displayDetails.functionAlias)";
                                    query         = $content;
                                    version       = 1;
                                }
                            }
                            $baseMainTemplate.resources += $parserObj

                            $parserMetadata = [PSCustomObject]@{
                                type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                                apiVersion = "2022-01-01-preview";
                                location   = "[parameters('workspace-location')]";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('Parser-', last(split(variables('_parserId$parserCounter'),'/'))))]";
                                dependsOn  =  @(
                                    "[variables('_parserId$parserCounter')]"
                                );
                                properties = [PSCustomObject]@{
                                    parentId  = "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', parameters('workspace'), variables('parserName$parserCounter'))]"
                                    contentId = "[variables('_parserContentId$parserCounter')]";
                                    kind      = "Parser";
                                    version   = "[variables('parserVersion$parserCounter')]";
                                    source    = [PSCustomObject]@{
                                        kind     = "Solution";
                                        name     = $contentToImport.Name;
                                        sourceId = "[variables('_solutionId')]"
                                    };
                                    author    = $authorDetails;
                                    support   = $baseMetadata.support
                                }
                            }

                            $baseMainTemplate.resources += $parserMetadata
                        }
                        else {
                            if ($parserCounter -eq 1 -and $(queryResourceExists) -and !$contentToImport.TemplateSpec) {
                                $baseParserResource = [PSCustomObject] @{
                                    type       = "Microsoft.OperationalInsights/workspaces";
                                    apiVersion = "2020-08-01";
                                    name       = "[parameters('workspace')]";
                                    location   = "[parameters('workspace-location')]";
                                    resources  = @(

                                    )
                                }
                                $baseMainTemplate.resources += $baseParserResource
                            }
                            $parserObj = [PSCustomObject] @{
                                type       = "savedSearches";
                                apiVersion = "2020-08-01";
                                name       = "$solutionName Data Parser";
                                dependsOn  = @(
                                    "[variables('workspace-dependency')]"
                                );
                                properties = [PSCustomObject] @{
                                    eTag          = "*";
                                    displayName   = "$solutionName Data Parser";
                                    category      = "Samples";
                                    functionAlias = "$functionAlias";
                                    query         = $content;
                                    version       = 1;
                                }
                            }
                            $baseMainTemplate.resources[$(getQueryResourceLocation)].resources += $parserObj
                        }
                        # Update Parser Counter
                        $parserCounter += 1
                    }
                }
            }
        }
        elseif ($objectProperties.Name.ToLower() -eq "metadata") {
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
                # Create Metadata Resource Object
                if ($json.support) {
                    $support = $json.support;
                }
                if ($json.categories) {
                    $categories = $json.categories;
                }


                $Author = $contentToImport.Author.Split(" - ");

                $newMetadata = [PSCustomObject]@{
                    type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                    apiVersion = "2022-01-01-preview";
                    location   = "[parameters('workspace-location')]";
                    properties = [PSCustomObject] @{
                        version = $contentToImport.Version;
                        kind    = "Solution";
                    };
                };

                if($contentToImport.TemplateSpec)
                {
                    $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "2.0.0";
                }

                $source = [PSCustomObject]@{
                    kind = "Solution";
                    name = "$solutionName";
                };
                $authorDetails = [PSCustomObject]@{
                    name  = $Author[0];
                };
                if($null -ne $Author[1])
                {
                     $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
                }
                if ($solutionId) {
                    $newMetadata | Add-Member -Name 'name' -Type NoteProperty -Value "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', variables('_solutionId'))]";
                    $newMetadata.Properties | Add-Member -Name 'contentId' -Type NoteProperty -Value "[variables('_solutionId')]";
                    $newMetadata.Properties | Add-Member -Name 'parentId' -Type NoteProperty -Value "[variables('_solutionId')]";

                    $source | Add-Member -Name 'sourceId' -Type NoteProperty -value "[variables('_solutionId')]";
                    $newMetadata.Properties | Add-Member -Name 'source' -Type NoteProperty -value $source;
                }

                $newMetadata.Properties | Add-Member -Name 'author' -Type NoteProperty -value $authorDetails

                $supportDetails = New-Object psobject;

                if ($support -and $support.psobject.properties["name"] -and $support.psobject.properties["name"].value) {
                    $supportDetails | Add-Member -Name 'name' -Type NoteProperty -value $support.psobject.properties["name"].value;
                }

                if ($support -and $support.psobject.properties["email"] -and $support.psobject.properties["email"].value) {
                    $supportDetails | Add-Member -Name 'email' -Type NoteProperty -value $support.psobject.properties["email"].value;
                }

                if ($support -and $support.psobject.properties["tier"] -and $support.psobject.properties["tier"].value) {
                    $supportDetails | Add-Member -Name 'tier' -Type NoteProperty -value $support.psobject.properties["tier"].value;
                }

                if ($support -and $support.psobject.properties["link"] -and $support.psobject.properties["link"].value) {
                    $supportDetails | Add-Member -Name 'link' -Type NoteProperty -value $support.psobject.properties["link"].value;
                }

                if ($support.psobject.properties["name"] -or $support.psobject.properties["email"] -or $support.psobject.properties["tier"] -or $support.psobject.properties["link"]) {
                    $newMetadata.Properties | Add-Member -Name 'support' -Type NoteProperty -value $supportDetails;
                }

                $dependencies = [PSCustomObject]@{
                    operator = "AND";
                    criteria = $DependencyCriteria;
                };

                $newMetadata.properties | Add-Member -Name 'dependencies' -Type NoteProperty -Value $dependencies;

                if ($json.firstPublishDate -and $json.firstPublishDate -ne "") {
                    $newMetadata.Properties | Add-Member -Name 'firstPublishDate' -Type NoteProperty -value $json.firstPublishDate;
                }

                if ($json.lastPublishDate -and $json.lastPublishDate -ne "") {
                    $newMetadata.Properties | Add-Member -Name 'lastPublishDate' -Type NoteProperty -value $json.lastPublishDate;
                }

                if ($json.providers -and $json.providers -ne "") {
                    $newMetadata.Properties | Add-Member -Name 'providers' -Type NoteProperty -value $json.providers;
                }
                $categoriesDetails = New-Object psobject;
                if ($categories -and $categories.psobject.properties['domains'] -and $categories.psobject.properties["domains"].Value.Length -gt 0) {
                    $categoriesDetails | Add-Member -Name 'domains' -Type NoteProperty -Value $categories.psobject.properties["domains"].Value;
                    $newMetadata.properties | Add-Member -Name 'categories' -Type NoteProperty -Value $categoriesDetails;
                }

                if ($categories -and $categories.psobject.properties['verticals'] -and $categories.psobject.properties["verticals"].Value.Length -gt 0) {
                    $categoriesDetails | Add-Member -Name 'verticals' -Type NoteProperty -Value $categories.psobject.properties["verticals"].value;
                    $newMetadata.properties | Add-Member -Name 'categories' -Type NoteProperty -Value $categoriesDetails;
                }
                $baseMainTemplate.resources += $newMetadata;
            }
            else {
                Write-Host "Failed to load Metadata file $file -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
            }
        }
    }


    # Update CreateUiDefinition Description with Content Counts
    function updateDescriptionCount($counter, $emplaceString, $replaceString, $countStringCondition) {
        if ($counter -gt 0) {
            $ruleCountSubstring = "$emplaceString$counter"
            $ruleCountString = $(if ($countStringCondition) { "$ruleCountSubstring, " } else { $ruleCountSubstring })
            $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace $replaceString, $ruleCountString
        }
        else {
            $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace $replaceString, ""
        }
    }
    function checkResourceCounts ($countList) {
        if ($countList -isnot [System.Array]) { return $false }
        else {
            foreach ($count in $countList) { if ($count -gt 0) { return $true } }
            return $false
        }
    }
    if ($contentToImport.Description) {
        $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace "{{SolutionDescription}}", $contentToImport.Description
    }
    else {
        $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace "{{SolutionDescription}}", ""
    }

    $analyticRuleCounter -= 1
    $workbookCounter -= 1
    $playbookCounter -= 1
    $connectorCounter -= 1
    $parserCounter -= 1
    $huntingQueryCounter -= 1
    $watchlistCounter -= 1
    updateDescriptionCount $connectorCounter                                "**Data Connectors:** "                     "{{DataConnectorCount}}"            $(checkResourceCounts $parserCounter, $analyticRuleCounter, $workbookCounter, $playbookCounter, $huntingQueryCounter, $watchlistCounter)
    updateDescriptionCount $parserCounter                                   "**Parsers:** "                             "{{ParserCount}}"                   $(checkResourceCounts $analyticRuleCounter, $workbookCounter, $playbookCounter, $huntingQueryCounter, $watchlistCounter)
    updateDescriptionCount $workbookCounter                                 "**Workbooks:** "                           "{{WorkbookCount}}"                 $(checkResourceCounts $analyticRuleCounter, $playbookCounter, $huntingQueryCounter, $watchlistCounter)
    updateDescriptionCount $analyticRuleCounter                             "**Analytic Rules:** "                      "{{AnalyticRuleCount}}"             $(checkResourceCounts $playbookCounter, $huntingQueryCounter, $watchlistCounter)
    updateDescriptionCount $huntingQueryCounter                             "**Hunting Queries:** "                     "{{HuntingQueryCount}}"             $(checkResourceCounts $playbookCounter, $watchlistCounter)
    updateDescriptionCount $watchlistCounter                                "**Watchlists:** "                          "{{WatchlistCount}}"                $(checkResourceCounts @($playbookCounter))
    updateDescriptionCount $customConnectorsList.Count                      "**Custom Azure Logic Apps Connectors:** "  "{{LogicAppCustomConnectorCount}}"  $(checkResourceCounts @($playbookCounter))
    updateDescriptionCount ($playbookCounter - $customConnectorsList.Count) "**Playbooks:** "                           "{{PlaybookCount}}"                   $false

    # Update Logo in CreateUiDefinition Description
    if ($contentToImport.Logo) {
        $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace "{{Logo}}", $contentToImport.Logo
    }
    else {
        $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace "{{Logo}}\n\n", ""
    }

    # Update Metadata in MainTemplate
    $baseMainTemplate.metadata.author = $(if ($contentToImport.Author) { $contentToImport.Author } else { "" })
    $baseMainTemplate.metadata.comments = $baseMainTemplate.metadata.comments -replace "{{SolutionName}}", $solutionName

    $repoRoot = $(git rev-parse --show-toplevel)
    $solutionFolderName = $solutionName
    $solutionFolder = "$repoRoot/Solutions/$solutionFolderName"
    if (!(Test-Path -Path $solutionFolder)) {
        New-Item -ItemType Directory $solutionFolder
    }
    $solutionFolder = "$solutionFolder/Package"
    if (!(Test-Path -Path $solutionFolder)) {
        New-Item -ItemType Directory $solutionFolder
    }
    $mainTemplateOutputPath = "$solutionFolder/mainTemplate.json"
    $createUiDefinitionOutputPath = "$solutionFolder/createUiDefinition.json"

    try {
        $baseMainTemplate | ConvertTo-Json -Depth $jsonConversionDepth | Out-File $mainTemplateOutputPath -Encoding utf8
    }
    catch {
        Write-Host "Failed to write output file $mainTemplateOutputPath" -ForegroundColor Red
        break;
    }
    try {
        # Sort UI Steps before writing to file
        $createUiDefinitionOrder = "dataconnectors", "parsers", "workbooks", "analytics", "huntingqueries", "watchlists", "playbooks"
        $baseCreateUiDefinition.parameters.steps = $baseCreateUiDefinition.parameters.steps | Sort-Object { $createUiDefinitionOrder.IndexOf($_.name) }
        # Ensure single-step UI Definitions have proper type for steps
        if ($($baseCreateUiDefinition.parameters.steps).GetType() -ne [System.Object[]]) {
            $baseCreateUiDefinition.parameters.steps = @($baseCreateUiDefinition.parameters.steps)
        }
        $baseCreateUiDefinition | ConvertTo-Json -Depth $jsonConversionDepth | Out-File $createUiDefinitionOutputPath -Encoding utf8
    }
    catch {
        Write-Host "Failed to write output file $createUiDefinitionOutputPath" -ForegroundColor Red
        break;
    }
    $zipPackageName = "$(if($contentToImport.Version){$contentToImport.Version}else{"newSolutionPackage"}).zip"
    Compress-Archive -Path "$solutionFolder/*" -DestinationPath "$solutionFolder/$zipPackageName" -Force

    #downloading and running arm-ttk on generated solution
    $armTtkFolder = "$PSScriptRoot/../arm-ttk"
    if (!$(Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)) {
        Write-Output "Missing arm-ttk validations. Downloading module..."
        Invoke-Expression "$armTtkFolder/download-arm-ttk.ps1"
    }
    Invoke-Expression ". '$armTtkFolder/run-arm-ttk-in-automation.ps1' '$solutionName'"
}
