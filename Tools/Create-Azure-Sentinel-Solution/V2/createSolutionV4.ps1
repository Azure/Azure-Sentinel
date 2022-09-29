param ($pipelineBasePath, $pipelineSolutionName, $pipelineDataFileRawContent, $pipelineParserRawContent, $dataFileName)

$jsonConversionDepth = 50
#$path = "$pipelineBasePath" + "\Solutions\" + "$pipelineSolutionName" + "\data\" + "$dataFileName"

$path = "\home\runner\work\SentinelCAT\SentinelCAT\Solutions\Alibaba Cloud\Data\Solution_Alibaba_Cloud.json"
Write-Host "path in createSolutionV4 file : $path"
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
function removePropertiesRecursively ($resourceObj) {
    foreach ($prop in $resourceObj.PsObject.Properties) {
        $key = $prop.Name
        $val = $prop.Value
        if ($null -eq $val) {
            $resourceObj.PsObject.Properties.Remove($key)
        }
        elseif ($val -is [System.Object[]]) {
            if ($val.Count -eq 0) {
                $resourceObj.PsObject.Properties.Remove($key)
            }
            else {
                foreach ($item in $val) {
                    $itemIndex = $val.IndexOf($item)
                    $resourceObj.$key[$itemIndex] = $(removePropertiesRecursively $val[$itemIndex])
                }
            }
        }
        else {
            if ($val -is [PSCustomObject]) {
                if ($($val.PsObject.Properties).Count -eq 0) {
                    $resourceObj.PsObject.Properties.Remove($key)
                }
                else {
                    $resourceObj.$key = $(removePropertiesRecursively $val)
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

    Write-Host "input file: $inputFile"
    $typeoffile = $inputFile.GetType()
    $inputFileString = $inputFile.ToString()
    $inputFileBasename = $inputFile.BaseName
    Write-Host "Type of input file: $typeoffile, Basefilpath: $inputFileBasename , inputFileString: $inputFileString"
    #$inputJsonPath = Join-Path -Path $path -ChildPath "$($inputFile.Name)"
    $dataFileIndex = $inputFileString.indexOf("Data")
    $parserFileIndex = $inputFileString.indexOf("Parsers")

    if ($dataFileIndex -gt 0)
    {
        #$inputJsonPath = Join-Path -Path "$pipelineBasePath" -ChildPath "$pipelineSolutionName" | Join-Path -ChildPath "data" | Join-Path -ChildPath "$($inputFile.Name)"
        #$inputJsonPath = "$pipelineBasePath" + "\Solutions" + "$pipelineSolutionName" + "\data\" + "$dataFileName"
        $inputJsonPath = "\home\runner\work\SentinelCAT\SentinelCAT\Solutions\Alibaba Cloud\Data\Solution_Alibaba_Cloud.json"
        Write-Host "data folder: $inputJsonPath"
        $contentToImport = $pipelineDataFileRawContent
    }
    elseif ($parserFileIndex -gt 0) {
        #$inputJsonPath = Join-Path -Path "$pipelineBasePath" -ChildPath "$pipelineSolutionName" | Join-Path -ChildPath "data" | Join-Path -ChildPath "$($inputFile.Name)"
        #$inputJsonPath = "$pipelineBasePath" + "\Solutions\" + "$pipelineSolutionName" + "\Parsers\AliCloud.txt"
        $inputJsonPath = "\home\runner\work\SentinelCAT\SentinelCAT\Solutions\Alibaba Cloud\Parsers\AliCloud.txt"
        Write-Host "parser folder: $inputJsonPath"
        $contentToImport = $pipelineParserRawContent
    }

    #$inputJsonPath = Join-Path -Path $pipelineBasePath -ChildPath "$($inputFile.Name)"
    Write-Host "line 162, inputjsonpath: $inputJsonPath"
    Write-Host "line 163, path: $path , filename:  $($inputFile.Name)"
    $contentToImport = Get-Content -Raw $inputJsonPath | Out-String | ConvertFrom-Json
    Write-Host "line 165 Content to import: $contentToImport"
    $ss = $contentToImport.BasePath
    Write-Host "line 167: content to import base path: $ss"
    $basePath = $(if ($contentToImport.BasePath) { $contentToImport.BasePath + "/" } else { "https://raw.githubusercontent.com/Tichandr/SentinelCAT/test7/" })
    Write-Host "line 169 BasePath : $basePath"
    # Content Counters - (for adding numbering to each item)
    # $analyticRuleCounter = 1
    #$connectorCounter = 1
    # $workbookCounter = 1
    # $playbookCounter = 1
    $parserCounter = 1
    # $savedSearchCounter = 1
    # $huntingQueryCounter = 1
    $watchlistCounter = 1

    # Convenience Variables
    $solutionName = $contentToImport.Name
    Write-Host "line 182 Solution name : $solutionName" 

    # Base JSON Object Paths
    $baseMainTemplatePath = "$PSScriptRoot/templating/baseMainTemplate.json"
    $baseCreateUiDefinitionPath = "$PSScriptRoot/templating/baseCreateUiDefinition.json"
    $metadataPath = "$PSScriptRoot/../../../Solutions/$($contentToImport.Name)/$($contentToImport.Metadata)"
    Write-Host " line 188 baseMainTemplatePath: $baseMainTemplatePath"
    Write-Host "baseCreateUiDefinitionPath: $baseCreateUiDefinitionPath"
    Write-Host "MetadataPath: $metadataPath"

    # Base JSON Objects
    $baseMainTemplate = Get-Content -Raw $baseMainTemplatePath | Out-String | ConvertFrom-Json
    $baseCreateUiDefinition = Get-Content -Raw $baseCreateUiDefinitionPath | Out-String | ConvertFrom-Json
    $baseMetadata = Get-Content -Raw $metadataPath | Out-String | ConvertFrom-Json

    $DependencyCriteria = @();
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
        Write-Host "line 174 object properties:  $objectProperties"

        # Access the value of the property
        if ($objectProperties.Value -is [System.Array]) {
            $aa = $objectProperties.Value
            Write-Host "line 178 object properties:  $aa"
            foreach ($file in $objectProperties.Value) {
                Write-Host "line 181 foreach: Base path: $basePath , File path: $file"
                $finalPath = $basePath + $file
                Write-Host "line 183 foreach:  $finalPath"
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
                    $objectKeyLowercase = $objectProperties.Name.ToLower()
                    if ($objectKeyLowercase -eq "savedsearches") {
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
                }
                else {
                    if ($file -match "(\.yaml)$") {
                        $objectKeyLowercase = $objectProperties.Name.ToLower()
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
                                apiVersion = "2021-05-01";
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
                                    "[variables('_parserName$parserCounter')]"
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
                                apiVersion = "2021-05-01";
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
    updateDescriptionCount $parserCounter                                   "**Parsers:** "                             "{{ParserCount}}"                   $(checkResourceCounts $analyticRuleCounter, $workbookCounter, $playbookCounter, $huntingQueryCounter, $watchlistCounter)

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
    Write-Host "repoRoot: $repoRoot"
    $solutionFolderName = $solutionName
    $solutionFolder = "$repoRoot/Solutions/$solutionFolderName"

    if (!(Test-Path -Path $solutionFolder)) {
        New-Item -ItemType Directory $solutionFolder
    }
    $solutionFolder = "$solutionFolder/Package"
    Write-Host "line 567 solutionFolder $solutionFolder"

    if (!(Test-Path -Path $solutionFolder)) {
        New-Item -ItemType Directory $solutionFolder
    }
    $mainTemplateOutputPath = "$solutionFolder/mainTemplate.json"
    Write-Host "line 571 mainTemplateOutputPath $mainTemplateOutputPath"
    #$createUiDefinitionOutputPath = "$solutionFolder/createUiDefinition.json"

    try {
        $baseMainTemplate | ConvertTo-Json -Depth $jsonConversionDepth | Out-File $mainTemplateOutputPath -Encoding utf8
        Write-Host "line 579 baseMainTemplate $baseMainTemplate"
    }
    catch {
        Write-Host "Failed to write output file $mainTemplateOutputPath" -ForegroundColor Red
        break;
    }

    Write-Host "At line 586"
    $zipPackageName = "$(if($contentToImport.Version){$contentToImport.Version}else{"newSolutionPackage"}).zip"
    Write-Host "zip package name: $zipPackageName"
    Compress-Archive -Path "$solutionFolder/*" -DestinationPath "$solutionFolder/$zipPackageName" -Force

    #downloading and running arm-ttk on generated solution
    # $armTtkFolder = "$PSScriptRoot/../arm-ttk"
    # Write-Host "armTtkFolder : $armTtkFolder"

    # if (!$(Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)) {
    #     Write-Host "at line 586"
    #     Write-Output "Missing arm-ttk validations. Downloading module..."
    #     Invoke-Expression "$armTtkFolder/download-arm-ttk.ps1"
    # }
    # Write-Host "at line 590"
    # Invoke-Expression "$armTtkFolder/run-arm-ttk-in-automation.ps1 '$solutionName'"
}
