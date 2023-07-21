$jsonConversionDepth = 50
$mainTemplateArtifact = [PSCustomObject]@{
    name = "DefaultTemplate";
    type = "Template"
}

# Base JSON Object Paths
$baseMainTemplatePath = "$PSScriptRoot/templating/baseMainTemplate.json"
$baseCreateUiDefinitionPath = "$PSScriptRoot/templating/baseCreateUiDefinition.json"

$global:baseMainTemplate = Get-Content -Raw $baseMainTemplatePath | Out-String | ConvertFrom-Json
$global:baseCreateUiDefinition = Get-Content -Raw $baseCreateUiDefinitionPath | Out-String | ConvertFrom-Json

# Content Counters - (for adding numbering to each item)
$global:analyticRuleCounter = 1
$global:connectorCounter = 1
$global:workbookCounter = 1
$global:playbookCounter = 1
$global:parserCounter = 1
$global:savedSearchCounter = 1
$global:huntingQueryCounter = 1
$global:watchlistCounter = 1

$global:DependencyCriteria = @();
$global:customConnectorsList = @{};
$global:functionAppList = @{};
$ContentKindDict = [System.Collections.Generic.Dictionary[String,string]]::new()
$ContentKindDict.Add("AnalyticsRule", "ar")
$ContentKindDict.Add("AnalyticsRuleTemplate", "art")
$ContentKindDict.Add("DataConnector", "dc")
$ContentKindDict.Add("DataType", "dt")
$ContentKindDict.Add("HuntingQuery", "hq")
$ContentKindDict.Add("InvestigationQuery", "iq")
$ContentKindDict.Add("Parser", "pr")
$ContentKindDict.Add("Playbook", "pl")
$ContentKindDict.Add("PlaybookTemplate", "plt")
$ContentKindDict.Add("Workbook", "wb")
$ContentKindDict.Add("WorkbookTemplate", "wbt")
$ContentKindDict.Add("Watchlist", "wl")
$ContentKindDict.Add("WatchlistTemplate", "wlt")
$ContentKindDict.Add("Notebook", "nb")
$ContentKindDict.Add("Solution", "sl")
$ContentKindDict.Add("AzureFunction", "fa")
$ContentKindDict.Add("LogicAppsCustomConnector", "lc")
$ContentKindDict.Add("AutomationRule", "ar")
$ContentKindDict.Add("ResourcesDataConnector", "rdc")
$ContentKindDict.Add("Standalone", "sa")

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
                if (!$global:baseMainTemplate.variables.blanks) {
                    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "blanks" -NotePropertyValue "[replace('b', 'b', '')]"
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
                    $resourceObj.$key = "[variables('TemplateEmptyArray')]";
                    if (!$global:baseMainTemplate.variables.TemplateEmptyArray) {
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "TemplateEmptyArray" -NotePropertyValue "[json('[]')]"
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
    foreach ($resource in $global:baseMainTemplate.resources) {
        if ($resource.type -eq "Microsoft.OperationalInsights/workspaces") {
            return $true
        }
    }
    return $false
}

function getQueryResourceLocation () {
    for ($i = 0; $i -lt $global:baseMainTemplate.resources.Length; $i++) {
        if ($global:baseMainTemplate.resources[$i].type -eq "Microsoft.OperationalInsights/workspaces") {
            return $i
        }
    }
}

function getParserDetails($solutionName,$yaml,$isyaml)
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

    $functionAlias = ($isyaml -eq $true) ? $yaml.FunctionName : $(getFileNameFromPath $file)
    $displayName = ($isyaml -eq $true) ? "$($yaml.Function.Title)" : "$($fileName)"
    $name = ($isyaml -eq $true) ? "$($yaml.FunctionName)" : "$($fileName)"
    $parserDisplayDetails | Add-Member -NotePropertyName "functionAlias" -NotePropertyValue $functionAlias
    $parserDisplayDetails | Add-Member -NotePropertyName "displayName" -NotePropertyValue $displayName
    $parserDisplayDetails | Add-Member -NotePropertyName "name" -NotePropertyValue $name


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

function checkResourceCounts ($countList) {
    if ($countList -isnot [System.Array]) { return $false }
    else {
        foreach ($count in $countList) { if ($count -gt 0) { return $true } }
        return $false
    }
}

function updateDescriptionCount($counter, $emplaceString, $replaceString, $countStringCondition) {
    if ($counter -gt 0) {
        $ruleCountSubstring = "$emplaceString$counter"
        $ruleCountString = $(if ($countStringCondition) { "$ruleCountSubstring, " } else { $ruleCountSubstring })
        $global:baseCreateUiDefinition.parameters.config.basics.description = $global:baseCreateUiDefinition.parameters.config.basics.description -replace $replaceString, $ruleCountString
    }
    else {
        $global:baseCreateUiDefinition.parameters.config.basics.description = $global:baseCreateUiDefinition.parameters.config.basics.description -replace $replaceString, ""
    }
}

function GetContentSchemaVersion($defaultPackageVersion, $dataInputVersion)
{
    # DEPENDING OF VERSION WE SHOULD SET THE CONTENTSCHEMAVERSION
    if ($null -eq $defaultPackageVersion -or $null -eq $dataInputVersion)
    {
        # WHEN BOTH NULL
        $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "3.0.0";
    }
    elseif ($null -ne $defaultPackageVersion -and ($dataInputVersion -ne $defaultPackageVersion))
    {
        # WHEN ONE IS NULL  
        $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "2.0.0";
    }
    elseif ($null -eq $defaultPackageVersion -and $null -eq $dataInputVersion) {
        $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "3.0.0";
        Write-Host "contentSchemaVersion set is 3.0.0 as both defaultPackageVersion and version field are null"
    }
    elseif ($null -ne $defaultPackageVersion -and $null -eq $dataInputVersion) {
        $major = $defaultPackageVersion.split(".")[0]
        $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "$major.0.0";
        Write-Host "contentSchemaVersion set is $major inside of elseif where defaultPackageVersion is not null but input file version is null"
    }
    elseif ($null -eq $defaultPackageVersion -and $null -ne $dataInputVersion) {
        $inputMajor,$inputMinor,$inputBuild,$inputRevision = $dataInputVersion.split(".")
        $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "$inputMajor.0.0";
        Write-Host "contentSchemaVersion inputMajor set is $inputMajor inside of elseif where defaultPackageVersion is null but input file version is not null"
    }
    elseif ($null -ne $defaultPackageVersion -and $null -ne $dataInputVersion -and 
    $dataInputVersion -ne $defaultPackageVersion)
    {
        $inputMajor,$inputMinor,$inputBuild,$inputRevision = $dataInputVersion.split(".")
        $defaultMajor,$defaultMinor,$defaultBuild,$defaultRevision = $defaultPackageVersion.split(".")
            
        if ($inputMajor -gt $defaultMajor -or $inputMajor -eq $defaultMajor)
        {
            $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "$inputMajor.0.0";
        }
        elseif ($inputMajor -gt $defaultMajor)
        {
            $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "$defaultMajor.0.0";
        }
    }
    elseif ($defaultPackageVersion -eq $dataInputVersion)
    {
        # WHEN BOTH SAME
        if ($null -eq $defaultPackageVersion)
        {
            $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "3.0.0";
        }
        else {
            $major = $defaultPackageVersion.split(".")[0]
            $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "$major.0.0";
        }
    }
    else 
    {
        $newMetadata.Properties | Add-Member -Name 'contentSchemaVersion' -Type NoteProperty -Value "3.0.0";
    }

    return $newMetadata
}

function PrepareSolutionMetadata($solutionMetadataRawContent, $contentResourceDetails, $defaultPackageVersion = $null)
    {
        Write-Host "Inside of PrepareSolutionMetadata"
        $json = $solutionMetadataRawContent
        # Create Metadata Resource Object
        if ($json.support) {
            $support = $json.support;
        }
        if ($json.categories) {
            $categories = $json.categories;
        }
        
        $Author = $contentToImport.Author.Split(" - ");
        $newMetadata = [PSCustomObject]@{
            type       = $contentResourceDetails.metadata #"Microsoft.OperationalInsights/workspaces/providers/metadata";
            apiVersion = $contentResourceDetails.metadataApiVersion;
            location   = "[parameters('workspace-location')]";
            properties = [PSCustomObject] @{
                version = $contentToImport.Version;
                kind    = "Solution";
            };
        };
        
        if($contentToImport.TemplateSpec)
        {
            $hasVersionAttribute = [bool]($contentToImport.PSobject.Properties.name -match "Version")
            if ($hasVersionAttribute)
            {
                $newMetadata = GetContentSchemaVersion -defaultPackageVersion $defaultPackageVersion -dataInputVersion $contentToImport.Version
            }
            else {
                $newMetadata = GetContentSchemaVersion -defaultPackageVersion $defaultPackageVersion -dataInputVersion $contentToImport.Version
            }
        }

        if($contentResourceDetails.apiVersion -eq '3.0.0')
        {
            $newMetadata.Properties | Add-Member -Name 'displayName' -Type NoteProperty -Value $contentToImport.Name;
            $newMetadata.Properties | Add-Member -Name 'publisherDisplayName' -Type NoteProperty -Value $(If ($support.psobject.properties["tier"].value.tolower() -eq "microsoft") {"Microsoft Sentinel, $($support.psobject.properties["name"].value)"} Else {$($support.psobject.properties["name"].value)})
            $newMetadata.Properties | Add-Member -Name 'descriptionHtml' -Type NoteProperty -Value $contentToImport.Description;
            $newMetadata.Properties | Add-Member -Name 'contentKind' -Type NoteProperty -Value "Solution";

            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutioncontentProductId" -NotePropertyValue "[concat(take(variables('_solutionId'),50),'-','$($ContentKindDict.ContainsKey("Solution") ? $ContentKindDict["Solution"] : '')','-', uniqueString(concat(variables('_solutionId'),'-','Solution','-',variables('_solutionId'),'-', variables('_solutionVersion'))))]"
	    $newMetadata.Properties | Add-Member -Name 'contentProductId' -Type NoteProperty -Value "[variables('_solutioncontentProductId')]"
            $newMetadata.Properties | Add-Member -Name 'id' -Type NoteProperty -Value "[variables('_solutioncontentProductId')]"
            $newMetadata.Properties | Add-Member -Name 'icon' -Type NoteProperty -Value $contentToImport.Logo;
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
        if ($global:solutionId) 
        {
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
        
        if ($support.psobject.properties["name"] -or $support.psobject.properties["email"] -or $support.psobject.properties["tier"] -or $support.psobject.properties["link"]) 
        {
            $newMetadata.Properties | Add-Member -Name 'support' -Type NoteProperty -value $supportDetails;
        }

        $dependencies = [PSCustomObject]@{
            operator = "AND";
            criteria = $global:DependencyCriteria;
        };
        
        $newMetadata.properties | Add-Member -Name 'dependencies' -Type NoteProperty -Value $dependencies;
        
        if ($json.firstPublishDate -and $json.firstPublishDate -ne "") 
        {
            $newMetadata.Properties | Add-Member -Name 'firstPublishDate' -Type NoteProperty -value $json.firstPublishDate;
        }
                    
        if ($json.lastPublishDate -and $json.lastPublishDate -ne "") 
        {
            $newMetadata.Properties | Add-Member -Name 'lastPublishDate' -Type NoteProperty -value $json.lastPublishDate;
        }
        
        if ($json.providers -and $json.providers -ne "") 
        {
            $newMetadata.Properties | Add-Member -Name 'providers' -Type NoteProperty -value $json.providers;
        }
        $categoriesDetails = New-Object psobject;
        if ($categories -and $categories.psobject.properties['domains'] -and $categories.psobject.properties["domains"].Value.Length -gt 0) 
        {
            $categoriesDetails | Add-Member -Name 'domains' -Type NoteProperty -Value $categories.psobject.properties["domains"].Value;
            $newMetadata.properties | Add-Member -Name 'categories' -Type NoteProperty -Value $categoriesDetails;
        }
        
        if ($categories -and $categories.psobject.properties['verticals'] -and $categories.psobject.properties["verticals"].Value.Length -gt 0) 
        {
            $categoriesDetails | Add-Member -Name 'verticals' -Type NoteProperty -Value $categories.psobject.properties["verticals"].value;
            $newMetadata.properties | Add-Member -Name 'categories' -Type NoteProperty -Value $categoriesDetails;
        }
        $global:baseMainTemplate.resources += $newMetadata;
        ### Removing the Non-Sentinel Resources if there are any:
        $newobject = $global:baseMainTemplate.resources | ? {$_.type -in $contentResourceDetails.resources}
        $global:baseMainTemplate.resources = $newobject
    }

    function GetWorkbookDataMetadata($file, $isPipelineRun, $contentResourceDetails, $baseFolderPath, $contentToImport)
    {
        Write-Host "Generating Workbook using $file"
        $solutionRename = Replace-SpecialChars -InputString $solutionName -Type 'solutionname'
        $fileName = Split-Path $file -leafbase;

        $indexOfOpenBraces = $fileName.IndexOf('(')
        if ($indexOfOpenBraces -le 0)
        {
            $fileName = Replace-SpecialChars -InputString $fileName -Type 'filename'
        }
        $workbookKey = $fileName;
        $fileName = $fileName + "Workbook";

                        if ($global:workbookCounter -eq 1) {
                            # Add workbook source variables
                            if (!$contentToImport.TemplateSpec){
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workbook-source" -NotePropertyValue "[concat(resourceGroup().id, '/providers/Microsoft.OperationalInsights/workspaces/',parameters('workspace'))]"
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_workbook-source" -NotePropertyValue "[variables('workbook-source')]"
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

                            $global:baseCreateUiDefinition.parameters.steps += $baseWorkbookStep
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
                                $global:baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name "formattedTimeNow" -Value $timeNowParameter
                            }
                        }

                        $workbookFinalPath = $baseFolderPath + 'Tools/Create-Azure-Sentinel-Solution/V2/WorkbookMetadata/WorkbooksMetadata.json';  
                        
                        # BELOW IS THE NEW CODE ADDED FROM AZURE SENTINEL REPO
                        if($contentToImport.TemplateSpec) {
                            #Getting Workbook Metadata dependencies from Github
                            $workbookData = $null
                            #$workbookFinalPath = $workbookMetadataPath + 'Tools/Create-Azure-Sentinel-Solution/V2/WorkbookMetadata/WorkbooksMetadata.json';
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
						$workbookUIParameter = [PSCustomObject] @{ name = "workbook$global:workbookCounter"; type = "Microsoft.Common.Section"; label = $dependencies.title; elements = @( [PSCustomObject] @{ name = "workbook$global:workbookCounter-text"; type = "Microsoft.Common.TextBlock"; options = @{ text = $dependencies.description; } } ) }
                        $global:baseCreateUiDefinition.parameters.steps[$global:baseCreateUiDefinition.parameters.steps.Count - 1].elements += $workbookUIParameter

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
                        $workbookDescriptionText = $(if ($contentToImport.WorkbookDescription -and $contentToImport.WorkbookDescription -is [System.Array]) { $contentToImport.WorkbookDescription[$global:workbookCounter - 1] } elseif ($contentToImport.WorkbookDescription -and $contentToImport.WorkbookDescription -is [System.String]) { $contentToImport.WorkbookDescription } else { "" })
                        #creating parameters in mainTemplate
                        $workbookIDParameterName = "workbook$global:workbookCounter-id"
                        $workbookNameParameterName = "workbook$global:workbookCounter-name"

                        $workbookIDParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the workbook" }; }

                        if(!$contentToImport.TemplateSpec)
                        {
                            $global:baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $workbookIDParameterName -Value $workbookIDParameter
                        }

                        # Create Workbook Resource Object
                        $newWorkbook = [PSCustomObject]@{
                            type       = "Microsoft.Insights/workbooks";
                            name       = "[parameters('workbook$global:workbookCounter-id')]";
                            location   = "[parameters('workspace-location')]";
                            kind       = "shared";
                            apiVersion = $contentResourceDetails.insightsWorkbookApiVersion; #"2021-08-01";
                            metadata   = [PSCustomObject]@{};
                            properties = [PSCustomObject] @{
                                displayName    = $contentToImport.Workbooks ? "[parameters('workbook$global:workbookCounter-name')]" : "[concat(parameters('workbook$global:workbookCounter-name'), ' - ', parameters('formattedTimeNow'))]";
                                serializedData = $serializedData;
                                version        = "1.0";
                                sourceId       = $contentToImport.TemplateSpec? "[variables('workspaceResourceId')]" : "[variables('_workbook-source')]";
                                category       = "sentinel"
                            }
                        }

                        if($contentToImport.TemplateSpec) {
                            #Getting Workbook Metadata dependencies from Github
                            $workbookData = $null

                            try {
                                Write-Host "Downloading $workbookFinalPath"
                                $workbookData = (New-Object System.Net.WebClient).DownloadString($workbookFinalPath)
                                $dependencies = $workbookData | ConvertFrom-Json | Where-Object {
                                    $indexOfOpenBraces = $_.templateRelativePath.contains('(')
                                    if ($indexOfOpenBraces)
                                    {
                                        $lastIndexOfDot = $_.templateRelativePath.LastIndexOf('.')
                                        if($lastIndexOfDot -gt 0)
                                        {
                                            $value = $_.templateRelativePath.substring(0, $lastIndexOfDot)
                                            if ($value.ToLower() -eq $workbookKey.ToLower())
                                            {
                                                return $_;
                                            }
                                        }
                                    }
                                    else {
                                        if($_.templateRelativePath.split('.')[0].ToLower() -eq $workbookKey.ToLower())
                                        {
                                            return $_;
                                        }
                                    }
                                }
                                
                                if ($dependencies.Count -gt 0)
                                {
                                    $dependencies = $dependencies[0]
                                }
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
                                        #criteria = $WorkbookDependencyCriteria;
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
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workbookVersion$global:workbookCounter" -NotePropertyValue "$($dependencies.version)"
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workbookContentId$global:workbookCounter" -NotePropertyValue "$($dependencies.workbookKey)"
                            $global:baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $workbookNameParameterName -Value $workbookNameParameter
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workbookId$global:workbookCounter" -NotePropertyValue "[resourceId('Microsoft.Insights/workbooks', variables('workbookContentId$global:workbookCounter'))]"

                            if ($contentResourceDetails.apiVersion -eq '3.0.0')
                            {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workbookTemplateSpecName$global:workbookCounter" -NotePropertyValue "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(concat(parameters('workspace'),'-wb-',uniquestring(variables('_workbookContentId$global:workbookCounter'))),variables('workbookVersion$global:workbookCounter')))]"
                            }
                            else 
                            {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workbookTemplateSpecName$global:workbookCounter" -NotePropertyValue "[concat(parameters('workspace'),'-wb-',uniquestring(variables('_workbookContentId$global:workbookCounter')))]"
                            }

                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_workbookContentId$global:workbookCounter" -NotePropertyValue "[variables('workbookContentId$global:workbookCounter')]"
                            $global:DependencyCriteria += [PSCustomObject]@{
                                kind      = "Workbook";
                                contentId = "[variables('_workbookContentId$global:workbookCounter')]";
                                version   = "[variables('workbookVersion$global:workbookCounter')]";
                            };

                            # Add workspace resource ID if not available
                            if (!$global:baseMainTemplate.variables.workspaceResourceId) {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                            }

                            if ($contentResourceDetails.contentSchemaVersion -ne '3.0.0')
                            {
                                # Add base templateSpec
                                $baseWorkbookTemplateSpec = [PSCustomObject]@{
                                    type       = $contentResourceDetails.resourcetype;  # "Microsoft.Resources/templateSpecs";
                                    apiVersion = $contentResourceDetails.templateSpecsApiVersion; # "2022-02-01";
                                    name       = "[variables('workbookTemplateSpecName$global:workbookCounter')]";
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
                                $global:baseMainTemplate.resources += $baseWorkbookTemplateSpec
                            }

                            $newWorkbook.name = "[variables('workbookContentId$global:workbookCounter')]"
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
                                apiVersion = $contentResourceDetails.commonResourceMetadataApiVersion; #"2022-01-01-preview";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('Workbook-', last(split(variables('workbookId$global:workbookCounter'),'/'))))]";
                                properties = [PSCustomObject]@{
                                    description = "$dependencies.description";
                                    parentId  = "[variables('workbookId$global:workbookCounter')]"
                                    contentId = "[variables('_workbookContentId$global:workbookCounter')]";
                                    kind      = "Workbook";
                                    version   = "[variables('workbookVersion$global:workbookCounter')]";
                                    source    = [PSCustomObject]@{
                                        kind     = "Solution";
                                        name     = $contentToImport.Name;
                                        sourceId = "[variables('_solutionId')]"
                                    };
                                    author    = $authorDetails;
                                    support   = $baseMetadata.support;
                                    #dependencies = $workbookDependencies;
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
                                type       = $contentResourceDetails.subtype; # "Microsoft.Resources/templateSpecs/versions";
                                apiVersion = $contentResourceDetails.templateSpecsVersionApiVersion;
                                name       = $contentResourceDetails.apiVersion -eq '3.0.0' ? "[variables('workbookTemplateSpecName$global:workbookCounter')]" : "[concat(variables('workbookTemplateSpecName$global:workbookCounter'),'/',variables('workbookVersion$global:workbookCounter'))]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "Workbook";
                                };

                                dependsOn  = $contentResourceDetails.apiVersion -eq '3.0.0' ? @(
                                "$($contentResourceDetails.dependsOn)") : @(
                                    "$($contentResourceDetails.dependsOn), variables('workbookTemplateSpecName$global:workbookCounter'))]"
                                );
                                properties = [PSCustomObject]@{
                                    description  = "$($fileName) Workbook with template version $($contentToImport.Version)";
                                    mainTemplate = [PSCustomObject]@{
                                        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                        contentVersion = "[variables('workbookVersion$global:workbookCounter')]";
                                        parameters     = [PSCustomObject]@{};
                                        variables      = [PSCustomObject]@{};
                                        resources      = @(
                                            # workbook
                                            $newWorkbook,
                                            # Metadata
                                            $workbookMetadata
                                        )
                                    };
                                }
                            }

                            if ($contentResourceDetails.apiVersion -eq '3.0.0')
                            {
                                $workbookTemplateSpecContent = SetContentTemplateDefaultValuesToProperties -templateSpecResourceObj $workbookTemplateSpecContent
                                $workbookTemplateSpecContent.properties.contentId = "[variables('_workbookContentId$global:workbookCounter')]"
                                $workbookTemplateSpecContent.properties.contentKind = "Workbook"
                                $workbookTemplateSpecContent.properties.displayName = "[parameters('workbook$global:workbookCounter-name')]"

                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_workbookcontentProductId$global:workbookCounter" -NotePropertyValue "[concat(take(variables('_solutionId'),50),'-','wb','-', uniqueString(concat(variables('_solutionId'),'-','Workbook','-',variables('_workbookContentId$global:workbookCounter'),'-', variables('workbookVersion$global:workbookCounter'))))]"
				$workbookTemplateSpecContent.properties.contentProductId = "[variables('_workbookcontentProductId$global:workbookCounter')]"                                
                                $workbookTemplateSpecContent.properties.id = "[variables('_workbookcontentProductId$global:workbookCounter')]"
                                $workbookTemplateSpecContent.properties.version = "[variables('workbookVersion$global:workbookCounter')]"
                                $workbookTemplateSpecContent.PSObject.Properties.Remove('tags')
                            }
                            $global:baseMainTemplate.resources += $workbookTemplateSpecContent
                        }
                        else 
                        {
                            $major = $contentToImport.version.split(".")[0]
                            #if ($contentToImport.version -ne '3.0.0' )
                            if ($major -ne 3)
                            {
                                $global:baseMainTemplate.resources += $newWorkbook
                                if ($contentToImport.Metadata -or $isPipelineRun)
                                {
                                    $global:baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                                    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"
                                    $global:DependencyCriteria += [PSCustomObject]@{
                                        kind      = "Workbook";
                                        contentId = "[variables('_$fileName')]";
                                        version   = "[variables('workbookVersion$global:workbookCounter')]";
                                    };
                                }
                            }
                        }
                        $global:workbookCounter += 1
    }

    function GetPlaybookDataMetadata($file, $contentToImport, $contentResourceDetails, $json, $isPipelineRun)
    {
        Write-Host "Generating Playbook using $file"
                    $playbookData = $json
                    $playbookName = $(if ($playbookData.parameters.PlaybookName) { $playbookData.parameters.PlaybookName.defaultValue }elseif ($playbookData.parameters."Playbook Name") { $playbookData.parameters."Playbook Name".defaultValue })

                    $fileName = Split-path -Parent $file | Split-Path -leaf
                    if($fileName.ToLower() -eq "incident-trigger" -or $fileName.ToLower() -eq "alert-trigger" -or $fileName.ToLower() -eq "entity-trigger")
                    { 
                        $parentPath = Split-Path $file -Parent; 
                        $fileName = (Split-Path $parentPath -Parent | Split-Path -leaf) + "-" + $fileName; 
                    }
                    
                    if($playbookData.metadata -and $playbookData.metadata.source -and $playbookData.metadata.source.kind -and ($playbookData.metadata.source.kind -eq "Community" -or $playbookData.metadata.source.kind -eq "Standalone"))
                    {
                        throw "The file $fileName has metadata with source -> kind = Community | Standalone. Please remove it so that it can be packaged as a solution."
                    }

                    if ($contentToImport.Metadata -or $isPipelineRun) {
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"
                    }

                    $IsLogicAppsCustomConnector = ($playbookData.resources | Where-Object {($_.type.ToLower() -eq "Microsoft.Web/customApis".ToLower())}) ? $true : $false;
                    $IsFunctionAppResource = ($playbookData.resources | Where-Object {($_.type.ToLower() -eq "Microsoft.Web/sites".ToLower())}) ? $true : $false;  

                    $global:DependencyCriteria += [PSCustomObject]@{
                        kind      = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ? "AzureFunction" : "Playbook";
                        contentId = "[variables('_$fileName')]";
                        version   = "[variables('playbookVersion$global:playbookCounter')]";
                    };

                    if($fileName.ToLower() -match "FunctionApp")
                    {
                        $functionAppsPlaybookId = $playbookData.parameters.FunctionAppName.defaultValue

                        # keeping this for furture use
                        # if ($null -eq $functionAppsPlaybookId)
                        # {
                        #     $suffix = 'fa'
                        #     if (!$playbookName) {
                        #         $functionAppMessage = "FunctionAppname not found in FunctionApp file $fileName so setting default value to '" + $fileName + "fa'"
                        #         Write-Host "$functionAppMessage"
                        #         $functionAppsPlaybookId = $fileName + $suffix
                        #     }
                        #     else {
                        #         $functionAppMessage = "FunctionAppname not found in FunctionApp file $fileName so setting default value to '" + $playbookName + "fa'"
                        #         Write-Host "$functionAppMessage"
                        #         $functionAppsPlaybookId = $playbookName + $suffix
                        #     }
                        # }
                    }

                    if (!$playbookName) {
                        $playbookName = $fileName;
                    }

                    if ($global:playbookCounter -eq 1) {
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
                        $global:baseCreateUiDefinition.parameters.steps += $playbookStep
                    }
                    $playbookDescriptionText = $(if ($contentToImport.PlaybookDescription -and $contentToImport.PlaybookDescription -is [System.Array]) { $contentToImport.PlaybookDescription[$global:playbookCounter - 1] } elseif ($contentToImport.PlaybookDescription -and $contentToImport.PlaybookDescription -is [System.String]) { $contentToImport.PlaybookDescription } else { "" })
                    $playbookElement = [PSCustomObject] @{
                        name     = "playbook$global:playbookCounter";
                        type     = "Microsoft.Common.Section";
                        label    = $playbookName;
                        elements = @(
                            [PSCustomObject] @{
                                name    = "playbook$global:playbookCounter-text";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject] @{ text = if ($playbookData.metadata -and $playbookData.metadata.comments) { $playbookData.metadata.comments } else { "This playbook ingests events from $solutionName into Log Analytics using the API." } }
                            }
                        )
                    }
                    $currentStepNum = $global:baseCreateUiDefinition.parameters.steps.Count - 1

                    foreach ($param in $playbookData.parameters.PsObject.Properties) {
                        $paramName = $param.Name
                        $defaultParamValue = $(if ($playbookData.parameters.$paramName.defaultValue) { $playbookData.parameters.$paramName.defaultValue } else { "" })
                        if ($param.Name.ToLower().contains("playbookname")) {
                            $playbookNameObject = [PSCustomObject] @{
                                name         = $contentToImport.TemplateSpec ? $paramName : "playbook$global:playbookCounter-$paramName";
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

                            if(!$contentToImport.TemplateSpec)
                            {
                                $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$global:playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        defaultValue = $playbookName;
                                        type         = "string";
                                        minLength    = 1;
                                        metadata     = [PSCustomObject] @{ description = "Resource name for the logic app playbook.  No spaces are allowed"; }
                                    })
                            }
                        }
                        elseif ($param.Name.ToLower().contains("username")) {
                            $playbookUsernameObject = [PSCustomObject] @{
                                name         = $contentToImport.TemplateSpec ? $paramName : "playbook$global:playbookCounter-$paramName";
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

                            if(!$contentToImport.TemplateSpec){
                            $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$global:playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                    defaultValue = $defaultParamValue;
                                    type         = "string";
                                    minLength    = 1;
                                    metadata     = [PSCustomObject] @{ description = "Username to connect to $solutionName API" }
                                })
                            }
                        }
                        elseif ($param.Name.ToLower().contains("password")) {
                            $playbookPasswordObject = [PSCustomObject] @{
                                name        = $contentToImport.TemplateSpec ? $paramName : "playbook$global:playbookCounter-$paramName";
                                type        = "Microsoft.Common.PasswordBox";
                                label       = [PSCustomObject] @{ password = $defaultParamValue; };
                                toolTip     = "Password to connect to $solutionName API";
                                constraints = [PSCustomObject] @{ required = $true; };
                                options     = [PSCustomObject] @{ hideConfirmation = $false; };
                            }

                            if(!$contentToImport.TemplateSpec){
                            $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$global:playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                    type      = "securestring";
                                    minLength = 1;
                                    metadata  = [PSCustomObject] @{ description = "Password to connect to $solutionName API"; }
                                })
                            }
                        }
                        elseif ($param.Name.ToLower().contains("apikey")) {
                            $playbookPasswordObject = [PSCustomObject] @{
                                name        = $contentToImport.TemplateSpec ? $paramName : "playbook$global:playbookCounter-$paramName";
                                type        = "Microsoft.Common.PasswordBox";
                                label       = [PSCustomObject] @{password = "ApiKey" };
                                toolTip     = "ApiKey to connect to $solutionName API";
                                constraints = [PSCustomObject] @{ required = $true; };
                                options     = [PSCustomObject] @{ hideConfirmation = $true; };
                            }

                            if(!$contentToImport.TemplateSpec)
                            {
                                $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$global:playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
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
                                        name         = $contentToImport.TemplateSpec ? $paramName : "playbook$global:playbookCounter-$paramName";
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
                                        name         = $contentToImport.TemplateSpec ? $paramName : "playbook$global:playbookCounter-$paramName";
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

                            $defaultValue = $(if ($defaultParamValue) { $defaultParamValue } else { "" })
                            if(!$contentToImport.TemplateSpec){
                            $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$global:playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                    defaultValue = $defaultValue;
                                    type         = "string";
                                    minLength    = 1;
                                })
                            }
                        }
                        if(!$contentToImport.TemplateSpec){
                            $global:baseCreateUiDefinition.parameters.outputs | Add-Member -NotePropertyName "playbook$global:playbookCounter-$paramName" -NotePropertyValue "[steps('playbooks').playbook$global:playbookCounter.playbook$global:playbookCounter-$paramName]"
                        }
                    }

                    foreach ($playbookVariable in $playbookData.variables.PsObject.Properties) {
                        $variableName = $playbookVariable.Name
                        $variableValue = $playbookVariable.Value
                        if ($variableValue -is [System.String]) {
                            $variableValue = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" $variableValue $global:playbookCounter)
                        }
                        if($contentToImport.TemplateSpec -and $variableName.ToLower().Contains("connection"))
                        {
                            $variableValue = "[" + $variableValue ;
                        }
                        if (!$contentToImport.TemplateSpec -and $variableName.ToLower().contains("apikey")) {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbook-$variableName" -NotePropertyValue "[$variableValue]"
                        }
                        elseif (!$contentToImport.TemplateSpec) {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbook$global:playbookCounter-$variableName" -NotePropertyValue $variableValue
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
                                    if($resourceObj.$key -eq "")
                                    {
                                        $resourceObj.$key = "[variables('blanks')]";

                                        if (!$global:baseMainTemplate.variables.blanks) {
                                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "blanks" -NotePropertyValue "[replace('b', 'b', '')]"
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
                                    $resourceObj.$key = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" "$(replaceQuotes $resourceObj.$key)" $global:playbookCounter)
                                    if($contentToImport.TemplateSpec -and ($resourceObj.$key.StartsWith("[") -and $resourceObj.$key.Contains("parameters(") -and !$resourceObj.$key.contains("parameters('workspace-location')")))
                                    {
                                        $resourceObj.$key = "[" + $resourceObj.$key;
                                    }
                                    if ($resourceObj.$key.StartsWith("[") -and $resourceObj.$key[$resourceObj.$key.Length - 1] -eq "]") {
                                        $resourceObj.$key = $(node "$PSScriptRoot/templating/replacePlaybookVarNames.js" "$(replaceQuotes $resourceObj.$key)" $global:playbookCounter)
                                    }
                                    $resourceObj.$key = $(node "$PSScriptRoot/templating/replaceLocationValue.js" "$(replaceQuotes $resourceObj.$key)" $global:playbookCounter)
                                    if ($resourceObj.$key.IndexOf($azureManagementUrl)) {
                                        $resourceObj.$key = $resourceObj.$key.Replace($azureManagementUrl, "@{variables('azureManagementUrl')}")
                                        $azureManagementUrlExists = $true
                                    }
                                    if ($key -eq "operationId") {
                                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "operationId-$($resourceobj.$key)" -NotePropertyValue $($resourceobj.$key)
                                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_operationId-$($resourceobj.$key)" -NotePropertyValue "[variables('operationId-$($resourceobj.$key)')]"
                                        $resourceObj.$key = "[variables('_operationId-$($resourceobj.$key)')]"
                                    }
                                }
                                elseif ($prop.Value -is [System.Array]) {
                                    foreach ($item in $prop.Value) {
                                        $itemIndex = $prop.Value.IndexOf($item)
                                        if ($null -ne $itemIndex) {
                                            if ($item -is [System.String]) {
                                                $item = $(node "$PSScriptRoot/templating/replaceLocationValue.js" $item $global:playbookCounter)
                                                $item = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" $item $global:playbookCounter)
                                                if($contentToImport.TemplateSpec -and ($item.StartsWith("[") -and $item.Contains("parameters(") -and !$item.contains("parameters('workspace-location')")))
                                                {
                                                    $item = "[" + $item;
                                                }
                                                if ($item.StartsWith("[") -and $item[$item.Length - 1] -eq "]") {
                                                    $item = $(node "$PSScriptRoot/templating/replacePlaybookVarNames.js" $item $global:playbookCounter)
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
                        foreach ($templateVar in $($global:baseMainTemplate.variables).PSObject.Properties) {
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
                    $global:contentShortName = '';
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
                                                contentId = $global:customConnectorsList[$templateVar.Value.defaultValue].id;
                                                version = $global:customConnectorsList[$templateVar.Value.defaultValue].version;
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
                                if(($playbookResource.properties.parameterValues) -and ($null -ne $global:baseMainTemplate.variables.'playbook-ApiKey')) {
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
                        } elseif ($contentToImport.TemplateSpec -and $playbookResource.type -eq "Microsoft.Web/customApis") {
                            $logicAppsPlaybookId = $playbookResource.name.Replace("parameters('","").Replace("'","").Replace(")","").Replace("]","").Replace("[","");
                            $customConnectorContentId = $playbookData.parameters.$logicAppsPlaybookId.defaultValue
                            
                        }


                        $playbookResource =  $playbookResource
                        $playbookResource = $(removePropertiesRecursively $playbookResource $false)
                        $playbookResource =  $(addInternalSuffixRecursively $playbookResource)
                        $playbookResource =  $(removeBlanksRecursively $playbookResource)
                        $playbookResources += $playbookResource;
                        $connectionCounter += 1
                    }

                    if(!$IsFunctionAppResource -and $rawData -like '*Microsoft.Web/sites*')
                    {
                        if ($null -ne $playbookData -and $null -ne $playbookData.parameters)
                        {
                            foreach($param in $playbookData.parameters.PsObject.Properties)
                            {
                                if($param.Value -match "defaultValue" -and $global:functionAppList.ContainsKey($param.Value.defaultValue))
                                {
                                    $playbookDependencies += [PSCustomObject] @{
                                            kind = "AzureFunction";
                                            contentId = $global:functionAppList[$param.Value.defaultValue].id;
                                            version = $global:functionAppList[$param.Value.defaultValue].version;
                                    }
                                }
                            }
                        }
                    }

                    if($contentToImport.TemplateSpec)
                    {
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookVersion$global:playbookCounter" -NotePropertyValue $playbookVersion
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookContentId$global:playbookCounter" -NotePropertyValue $fileName
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_playbookContentId$global:playbookCounter" -NotePropertyValue "[variables('playbookContentId$global:playbookCounter')]"

                        if (!$IsLogicAppsCustomConnector -and !$IsFunctionAppResource) {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookId$global:playbookCounter" -NotePropertyValue "[resourceId('Microsoft.Logic/workflows', variables('playbookContentId$global:playbookCounter'))]"
                        }

                        if ($contentResourceDetails.apiVersion -eq '3.0.0')
                        {
                            if ($IsLogicAppsCustomConnector) {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookTemplateSpecName$global:playbookCounter" -NotePropertyValue "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(concat(parameters('workspace'),'-lc-',uniquestring(variables('_playbookContentId$global:playbookCounter'))),variables('playbookVersion$global:playbookCounter')))]"
                                $global:contentShortName  = 'lc'
                            }
                            elseif ($IsFunctionAppResource) {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookTemplateSpecName$global:playbookCounter" -NotePropertyValue "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(concat(parameters('workspace'),'-fa-',uniquestring(variables('_playbookContentId$global:playbookCounter'))),variables('playbookVersion$global:playbookCounter')))]"
                                $global:contentShortName  = 'fa'
                            }
                            else {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookTemplateSpecName$global:playbookCounter" -NotePropertyValue  "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(concat(parameters('workspace'),'-pl-',uniquestring(variables('_playbookContentId$global:playbookCounter'))),variables('playbookVersion$global:playbookCounter')))]"
                                $global:contentShortName  = 'pl'
                            } 
                        }
                        else
                        {
                        if ($IsLogicAppsCustomConnector) {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookTemplateSpecName$global:playbookCounter" -NotePropertyValue "[concat(parameters('workspace'),'-lc-',uniquestring(variables('_playbookContentId$global:playbookCounter')))]"
                            $global:contentShortName  = 'lc'
                        }
                        elseif ($IsFunctionAppResource) {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookTemplateSpecName$global:playbookCounter" -NotePropertyValue "[concat(parameters('workspace'),'-fa-',uniquestring(variables('_playbookContentId$global:playbookCounter')))]"
                            $global:contentShortName  = 'fa'
                        }
                        else {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "playbookTemplateSpecName$global:playbookCounter" -NotePropertyValue "[concat(parameters('workspace'),'-pl-',uniquestring(variables('_playbookContentId$global:playbookCounter')))]"
                            $global:contentShortName  = 'pl'
                        }
                    }

                        # Add workspace resource ID if not available
                        if (!$global:baseMainTemplate.variables.workspaceResourceId) {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                        }
                        # Add base templateSpec
                        if ($contentResourceDetails.contentSchemaVersion -ne '3.0.0')
                        {
                            $basePlaybookTemplateSpec = [PSCustomObject]@{
                                type       = $contentResourceDetails.resourcetype; # "Microsoft.Resources/templateSpecs";
                                apiVersion = $contentResourceDetails.templateSpecsApiVersion; #"2022-02-01";
                                name       = "[variables('playbookTemplateSpecName$global:playbookCounter')]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ? "AzureFunction" : "Playbook";
                                };

                                properties = [PSCustomObject]@{
                                    description = $IsLogicAppsCustomConnector -or $IsFunctionAppResource ? $playbookName : "$($playbookName) playbook";
                                    displayName = $IsLogicAppsCustomConnector -or $IsFunctionAppResource ? $playbookName : "$($playbookName) playbook";
                                }
                            }

                            $global:baseMainTemplate.resources += $basePlaybookTemplateSpec
                        }
                        $author = $contentToImport.Author.Split(" - ");
                        $authorDetails = [PSCustomObject]@{
                            name  = $author[0];
                        };
                        if($null -ne $author[1])
                        {
                            $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
                        }
                        if ($IsLogicAppsCustomConnector) {
                            $global:customConnectorsList.add($customConnectorContentId, @{ id="[variables('_$filename')]"; version="[variables('playbookVersion$global:playbookCounter')]"});
                        }
                        if ($IsFunctionAppResource) {
                            $global:functionAppList.add($functionAppsPlaybookId, @{ id="[variables('_$filename')]"; version="[variables('playbookVersion$global:playbookCounter')]"});

                            # keeping it for furture use
                            # if ($null -ne $functionAppsPlaybookId)
                            # {
                            #     $global:functionAppList.add($functionAppsPlaybookId, @{ id="[variables('_$filename')]"; version="[variables('playbookVersion$global:playbookCounter')]"});
                            # }
                        }

                        $playbookMetadata = [PSCustomObject]@{
                            type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                            apiVersion = $contentResourceDetails.commonResourceMetadataApiVersion; #"2022-01-01-preview";
                            name       = $IsLogicAppsCustomConnector ? "[[concat(variables('workspace-name'),'/Microsoft.SecurityInsights/',concat('LogicAppsCustomConnector-', last(split(variables('playbookId$global:playbookCounter'),'/'))))]" : 
                            $IsFunctionAppResource ? "[[concat(variables('workspace-name'),'/Microsoft.SecurityInsights/',concat('AzureFunction-', last(split(variables('playbookId$global:playbookCounter'),'/'))))]" :
                            "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('Playbook-', last(split(variables('playbookId$global:playbookCounter'),'/'))))]";
                            properties = [PSCustomObject]@{
                                parentId  = $IsLogicAppsCustomConnector -or $IsFunctionAppResource ? "[[variables('playbookId$global:playbookCounter')]" : "[variables('playbookId$global:playbookCounter')]"
                                contentId = "[variables('_playbookContentId$global:playbookCounter')]";
                                kind      = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ? "AzureFunction" : "Playbook";
                                version   = "[variables('playbookVersion$global:playbookCounter')]";
                                source    = [PSCustomObject]@{
                                    kind     = "Solution";
                                    name     = $contentToImport.Name;
                                    sourceId = "[variables('_solutionId')]"
                                };
                                author    = $authorDetails;
                                support   = $baseMetadata.support
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
                            $playbookVariables | Add-Member -NotePropertyName "playbookContentId$global:playbookCounter" -NotePropertyValue $fileName;
                            $playbookVariables | Add-Member -NotePropertyName "playbookId$global:playbookCounter" -NotePropertyValue "[[resourceId('Microsoft.Web/customApis', parameters('$logicAppsPlaybookId'))]"
                        }

                        if ($IsFunctionAppResource) {
                            $playbookVariables | Add-Member -NotePropertyName "playbookContentId$global:playbookCounter" -NotePropertyValue $fileName;
                            $playbookVariables | Add-Member -NotePropertyName "playbookId$global:playbookCounter" -NotePropertyValue "[[resourceId('Microsoft.Logic/workflows', variables('playbookContentId$global:playbookCounter'))]"
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
                            type       = $contentResourceDetails.subtype; # "Microsoft.Resources/templateSpecs/versions";
                            apiVersion = $contentResourceDetails.templateSpecsVersionApiVersion;
                            name       = $contentResourceDetails.apiVersion -eq '3.0.0' ? "[variables('playbookTemplateSpecName$global:playbookCounter')]" : "[concat(variables('playbookTemplateSpecName$global:playbookCounter'),'/',variables('playbookVersion$global:playbookCounter'))]";
                            location   = "[parameters('workspace-location')]";
                            tags       = [PSCustomObject]@{
                                "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                "hidden-sentinelContentType" = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ? "AzureFunction" : "Playbook";
                            };

                            dependsOn  = $contentResourceDetails.apiVersion -eq '3.0.0' ? @(
                                "$($contentResourceDetails.dependsOn)") : @(
                                "$($contentResourceDetails.dependsOn), variables('playbookTemplateSpecName$global:playbookCounter'))]"
                            );
                            properties = [PSCustomObject]@{
                                description  = "$($playbookName) Playbook with template version $($contentToImport.Version)";
                                mainTemplate = [PSCustomObject]@{
                                    '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                    contentVersion = "[variables('playbookVersion$global:playbookCounter')]";
                                    parameters     = $playbookData.parameters;
                                    variables      = $playbookVariables;
                                    resources      = $playbookResources;
                                };
                            }
                        }
                        if ($contentResourceDetails.apiVersion -eq '3.0.0')
                        {
                            $playbookTemplateSpecContent = SetContentTemplateDefaultValuesToProperties -templateSpecResourceObj $playbookTemplateSpecContent
                            $playbookTemplateSpecContent.properties.contentId = "[variables('_playbookContentId$global:playbookCounter')]"
                            $playbookTemplateSpecContent.properties.contentKind = $IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ? "AzureFunction" : "Playbook"
                            $playbookTemplateSpecContent.properties.displayName = $playbookName

                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_playbookcontentProductId$global:playbookCounter" -NotePropertyValue "[concat(take(variables('_solutionId'),50),'-','$global:contentShortName','-', uniqueString(concat(variables('_solutionId'),'-','$($IsLogicAppsCustomConnector ? "LogicAppsCustomConnector" : $IsFunctionAppResource ? "AzureFunction" : "Playbook")','-',variables('_playbookContentId$global:playbookCounter'),'-', variables('playbookVersion$global:playbookCounter'))))]"
			    $playbookTemplateSpecContent.properties.contentProductId = "[variables('_playbookcontentProductId$global:playbookCounter')]"
                             $playbookTemplateSpecContent.properties.id = "[variables('_playbookcontentProductId$global:playbookCounter')]"
                            $playbookTemplateSpecContent.properties.version = "[variables('playbookVersion$global:playbookCounter')]"
                            $playbookTemplateSpecContent.PSObject.Properties.Remove('tags')
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
                            if (!$global:baseMainTemplate.variables.blanks) {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "blanks" -NotePropertyValue "[replace('b', 'b', '')]"
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
                        $global:baseMainTemplate.resources += $playbookTemplateSpecContent;
                    }
                    else
                    {
                        $global:baseMainTemplate.resources += $playbookResources;
                    }

                    if ($azureManagementUrlExists) {
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "azureManagementUrl" -NotePropertyValue $azureManagementUrl
                    }

                    $global:playbookCounter += 1
    }

    function GetDataConnectorMetadata($file, $contentResourceDetails)
    {
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

                    $global:DependencyCriteria += [PSCustomObject]@{
                        kind      = "DataConnector";
                        contentId = if ($contentToImport.TemplateSpec){"[variables('_dataConnectorContentId$global:connectorCounter')]"}else{"[variables('_$connectorId')]"};
                        version   = if ($contentToImport.TemplateSpec){"[variables('dataConnectorVersion$global:connectorCounter')]"}else{$contentToImport.Version};
                    };
                    foreach ($step in $templateSpecConnectorData.instructionSteps) {
                        # Remove empty properties from each instructionStep
                        $stepIndex = $templateSpecConnectorData.instructionSteps.IndexOf($step)
                        $templateSpecConnectorData.instructionSteps[$stepIndex] = handleEmptyInstructionProperties $step
                    }

                    if ($contentToImport.TemplateSpec) {
                        $connectorName = $contentToImport.Name
                        # Add workspace resource ID if not available
                        if (!$global:baseMainTemplate.variables.workspaceResourceId -and $contentResourceDetails.contentSchemaVersion -ne '3.0.0') {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                        }
                        # If both ID and Title exist, is standard GenericUI data connector
                        if ($templateSpecConnectorData.id -and $templateSpecConnectorData.title) {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "uiConfigId$global:connectorCounter" -NotePropertyValue $templateSpecConnectorData.id
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_uiConfigId$global:connectorCounter" -NotePropertyValue "[variables('uiConfigId$global:connectorCounter')]"
                        }
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorContentId$global:connectorCounter" -NotePropertyValue $templateSpecConnectorData.id
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$global:connectorCounter" -NotePropertyValue "[variables('dataConnectorContentId$global:connectorCounter')]"
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorId$global:connectorCounter" -NotePropertyValue "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/dataConnectors', variables('_dataConnectorContentId$global:connectorCounter'))]"
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorId$global:connectorCounter" -NotePropertyValue "[variables('dataConnectorId$global:connectorCounter')]"

                        if ($contentResourceDetails.apiVersion -eq '3.0.0')
                        {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorTemplateSpecName$global:connectorCounter" -NotePropertyValue "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentId$global:connectorCounter'))),variables('dataConnectorVersion$global:connectorCounter')))]"
                        }
                        else 
                        {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorTemplateSpecName$global:connectorCounter" -NotePropertyValue "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentId$global:connectorCounter')))]"
                        }

                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$global:connectorCounter" -NotePropertyValue (($null -ne $templateSpecConnectorData.metadata) ? "$($templateSpecConnectorData.metadata.version)" : "1.0.0")
                        if (!$contentToImport.TemplateSpec){
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "parentId" -NotePropertyValue $global:solutionId
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_parentId" -NotePropertyValue "[variables('parentId')]"
                        };

                        if ($contentResourceDetails.contentSchemaVersion -ne '3.0.0')
                        {
                            # Add base templateSpec
                            $baseDataConnectorTemplateSpec = [PSCustomObject]@{
                                type       = $contentResourceDetails.resourcetype; # "Microsoft.Resources/templateSpecs";
                                apiVersion = $contentResourceDetails.templateSpecsApiVersion; #"2022-02-01";
                                name       = "[variables('dataConnectorTemplateSpecName$global:connectorCounter')]";
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
                            $global:baseMainTemplate.resources += $baseDataConnectorTemplateSpec
                        }
                        if(!$contentToImport.Is1PConnector)
                        {
                            $existingFunctionApp = $false;
                            $instructionArray = $templateSpecConnectorData.instructionSteps
                            ($instructionArray | ForEach {if($_.description -and $_.description.IndexOf('[Deploy To Azure]') -gt 0){$existingFunctionApp = $true;}})
                            if($existingFunctionApp)
                            {
                                $templateSpecConnectorData.title = ($templateSpecConnectorData.title.Contains("using Azure Functions")) ? $templateSpecConnectorData.title : $templateSpecConnectorData.title + " (using Azure Functions)"
                            }
                        }
                        # Data Connector Content -- *Assumes GenericUI
                        if($contentToImport.Is1PConnector)
                        {
                            $1pconnectorData = $templateSpecConnectorData
                            $1pconnectorData = $1pconnectorData | Select-Object -Property id,title,publisher,descriptionMarkdown, graphQueries, connectivityCriterias,dataTypes
                        }
                        $templateSpecConnectorUiConfig = ($contentToImport.Is1PConnector -eq $true) ? $1pconnectorData : $templateSpecConnectorData
                        $templateSpecConnectorUiConfig.id = "[variables('_uiConfigId$global:connectorCounter')]"
                        if($contentToImport.Is1PConnector -eq $false)
                        {
                            $templateSpecConnectorUiConfig.availability.isPreview =  ($templateSpecConnectorUiConfig.availability.isPreview -eq $true) ? $false : $templateSpecConnectorUiConfig.availability.isPreview
                        }
                        $dataConnectorContent = [PSCustomObject]@{
                            name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$global:connectorCounter'))]";
                            apiVersion = $contentResourceDetails.dataConnectorsApiVersion; #"2021-03-01-preview";
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
                            apiVersion = $contentResourceDetails.metadataApiVersion; #"2022-01-01-preview";
                            name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('DataConnector-', last(split(variables('_dataConnectorId$global:connectorCounter'),'/'))))]";
                            properties = [PSCustomObject]@{
                                parentId  = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/dataConnectors', variables('_dataConnectorContentId$global:connectorCounter'))]";
                                contentId = "[variables('_dataConnectorContentId$global:connectorCounter')]";
                                kind      = "DataConnector";
                                version   = "[variables('dataConnectorVersion$global:connectorCounter')]";
                                source    = [PSCustomObject]@{
                                    kind     = "Solution";
                                    name     = $contentToImport.Name;
                                    sourceId = "[variables('_solutionId')]"
                                };
                                author    = $authorDetails;
                                support   = $baseMetadata.support
                            }
                        }
                        #one removed check from here for apiVersion
                        # Add templateSpecs/versions resource to hold actual content
                        $dataConnectorTemplateSpecContent = [PSCustomObject]@{
                            type       = $contentResourceDetails.subtype; # "Microsoft.Resources/templateSpecs/versions";
                            apiVersion = $contentResourceDetails.templateSpecsVersionApiVersion;
                            name       = $contentResourceDetails.apiVersion -eq '3.0.0' ? "[variables('dataConnectorTemplateSpecName$global:connectorCounter')]" : "[concat(variables('dataConnectorTemplateSpecName$global:connectorCounter'),'/',variables('dataConnectorVersion$global:connectorCounter'))]";
                            location   = "[parameters('workspace-location')]";
                            tags       = [PSCustomObject]@{
                                "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                "hidden-sentinelContentType" = "DataConnector";
                            };

                            dependsOn  = $contentResourceDetails.apiVersion -eq '3.0.0' ? @(
                                "$($contentResourceDetails.dependsOn)") : @(
                                "$($contentResourceDetails.dependsOn), variables('dataConnectorTemplateSpecName$global:connectorCounter'))]"
                            );
                            properties = [PSCustomObject]@{
                                description  = "$($connectorName) data connector with template version $($contentToImport.Version)";
                                mainTemplate = [PSCustomObject]@{
                                    '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                    contentVersion = "[variables('dataConnectorVersion$global:connectorCounter')]";
                                    parameters     = [PSCustomObject]@{};
                                    variables      = [PSCustomObject]@{};
                                    resources      = @(
                                        # Data Connector
                                        $dataConnectorContent,
                                        # Metadata
                                        $dataConnectorMetadata
                                    )
                                };
                            }
                        }
                        if ($contentResourceDetails.apiVersion -eq '3.0.0')
                        {
                            $dataConnectorTemplateSpecContent = SetContentTemplateDefaultValuesToProperties -templateSpecResourceObj $dataConnectorTemplateSpecContent
                            $dataConnectorTemplateSpecContent.properties.contentId = "[variables('_dataConnectorContentId$global:connectorCounter')]"
                            $dataConnectorTemplateSpecContent.properties.contentKind = "DataConnector"

                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorcontentProductId$global:connectorCounter" -NotePropertyValue "[concat(take(variables('_solutionId'),50),'-','dc','-', uniqueString(concat(variables('_solutionId'),'-','DataConnector','-',variables('_dataConnectorContentId$global:connectorCounter'),'-', variables('dataConnectorVersion$global:connectorCounter'))))]"
			                $dataConnectorTemplateSpecContent.properties.contentProductId = "[variables('_dataConnectorcontentProductId$global:connectorCounter')]"
                            $dataConnectorTemplateSpecContent.properties.id = "[variables('_dataConnectorcontentProductId$global:connectorCounter')]"

                            $dataConnectorTemplateSpecContent.properties.displayName = $templateSpecConnectorData.title
                            $dataConnectorTemplateSpecContent.properties.version = "[variables('dataConnectorVersion$global:connectorCounter')]"
                            $dataConnectorTemplateSpecContent.PSObject.Properties.Remove('tags')
                        }
                        $global:baseMainTemplate.resources += $dataConnectorTemplateSpecContent

                        # Add content-metadata item, in addition to template spec metadata item
                        $dataConnectorActiveContentMetadata = [PSCustomObject]@{
                            type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                            apiVersion = $contentResourceDetails.metadataApiVersion; #"2022-01-01-preview";
                            name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('DataConnector-', last(split(variables('_dataConnectorId$global:connectorCounter'),'/'))))]";
                            dependsOn  = @("[variables('_dataConnectorId$global:connectorCounter')]");
                            location   = "[parameters('workspace-location')]";
                            properties = [PSCustomObject]@{
                                parentId  = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/dataConnectors', variables('_dataConnectorContentId$global:connectorCounter'))]";
                                contentId = "[variables('_dataConnectorContentId$global:connectorCounter')]";
                                kind      = "DataConnector";
                                version   = "[variables('dataConnectorVersion$global:connectorCounter')]";
                                source    = [PSCustomObject]@{
                                    kind     = "Solution";
                                    name     = $contentToImport.Name;
                                    sourceId = "[variables('_solutionId')]"
                                };
                                author    = $authorDetails;
                                support   = $baseMetadata.support
                            }
                        }
                        $global:baseMainTemplate.resources += $dataConnectorActiveContentMetadata
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
                            $standardConnectorUiConfig | Add-Member -NotePropertyName "id" -NotePropertyValue "[variables('_uiConfigId$global:connectorCounter')]"

                        }

                        $connectorObj = [PSCustomObject]@{
                            name       = if ($contentToImport.TemplateSpec) { "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$global:connectorCounter'))]" }else { "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('connector$global:connectorCounter-name'))]" }
                            apiVersion = $contentResourceDetails.dataConnectorsApiVersion; #"2021-03-01-preview";
                            type       = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors";
                            location   = "[parameters('workspace-location')]";
                            kind       = ($contentToImport.Is1PConnector -eq $true) ? "StaticUI" : "GenericUI";
                            properties = [PSCustomObject]@{
                                connectorUiConfig = $standardConnectorUiConfig
                            }
                        }

                        if(!$contentToImport.TemplateSpec)
                        {
                            $connectorObj | Add-Member -NotePropertyName "id" -NotePropertyValue "[variables('_connector$global:connectorCounter-source')]";
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
                        $connectorUiConfig.id = if ($contentToImport.TemplateSpec) { "[variables('_uiConfigId$global:connectorCounter')]" }else { "[variables('_connector$global:connectorCounter-source')]" };

                        $connectorObj = [PSCustomObject]@{
                            name       = if ($contentToImport.TemplateSpec) { "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$global:connectorCounter'))]" }else { "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('connector$global:connectorCounter-name'))]" }
                            apiVersion = $contentResourceDetails.dataConnectorsApiVersion; #"2021-03-01-preview";
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

                    $global:baseMainTemplate.resources += $connectorObj

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
                    $baseDescriptionText = "This Solution installs the data connector for $solutionName. You can get $solutionName $connectorDataType data in your Microsoft Sentinel workspace. Configure and enable this data connector in the Data Connector gallery after this Solution deploys."
                    $customLogsText = "$baseDescriptionText This data connector creates custom log table(s) $(getAllDataTypeNames $connectorData.dataTypes) in your Microsoft Sentinel / Azure Log Analytics workspace."
                    $syslogText = "$baseDescriptionText The logs will be received in the Syslog table in your Microsoft Sentinel / Azure Log Analytics workspace."
                    $commonSecurityLogText = "$baseDescriptionText The logs will be received in the CommonSecurityLog table in your Microsoft Sentinel / Azure Log Analytics workspace."
                    $connectorDescriptionText = "This Solution installs the data connector for $solutionName. You can get $solutionName $connectorDataType data in your Microsoft Sentinel workspace. After installing the solution, configure and enable this data connector by following guidance in Manage solution view."
                    $parserText = "The Solution installs a parser that transforms the ingested data into Microsoft Sentinel normalized format. The normalized format enables better correlation of different types of data from different data sources to drive end-to-end outcomes seamlessly in security monitoring, hunting, incident investigation and response scenarios in Microsoft Sentinel."

                    $baseDataConnectorStep = [PSCustomObject] @{
                        name       = "dataconnectors";
                        label      = "Data Connectors";
                        bladeTitle = "Data Connectors";
                        elements   = @();
                    }
                    $baseDataConnectorTextElement = [PSCustomObject] @{
                        name    = "dataconnectors$global:connectorCounter-text";
                        type    = "Microsoft.Common.TextBlock";
                        options = [PSCustomObject] @{
                            text = $connectorDescriptionText;
                        }
                    }

                    if ($global:connectorCounter -eq 1) {
                        $global:baseCreateUiDefinition.parameters.steps += $baseDataConnectorStep
                    }
                    $currentStepNum = $global:baseCreateUiDefinition.parameters.steps.Count - 1
                    $global:baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $baseDataConnectorTextElement
                    if ($global:connectorCounter -eq $contentToImport."Data Connectors".Count) {
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
                            $global:baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $parserTextElement
                        }
                        $global:baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $connectDataSourcesLink
                    }

                    # Update Connector Counter
                    $global:connectorCounter += 1			
    }

    function GetHuntingDataMetadata($file, $rawData, $contentResourceDetails)
    {
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

                        
                        $hasHuntingQueryVersion = [bool]($global:baseMainTemplate.variables.PSobject.Properties.Name -match "huntingQueryVersion$global:huntingQueryCounter")
                        if ($hasHuntingQueryVersion)
                        {
                            $global:huntingQueryCounter += 1
                        }
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQueryVersion$global:huntingQueryCounter" -NotePropertyValue (($null -ne $yaml.version) ? "$($yaml.version)" : "1.0.0")
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQuerycontentId$global:huntingQueryCounter" -NotePropertyValue $yaml.id
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_huntingQuerycontentId$global:huntingQueryCounter" -NotePropertyValue "[variables('huntingQuerycontentId$global:huntingQueryCounter')]"
                        $global:DependencyCriteria += [PSCustomObject]@{
                            kind      = "HuntingQuery";
                            contentId = "[variables('_huntingQuerycontentId$global:huntingQueryCounter')]";
                            version   = "[variables('huntingQueryVersion$global:huntingQueryCounter')]";
                        };

                        if ($global:huntingQueryCounter -eq 1) {
                            if (!$(queryResourceExists) -and !$contentToImport.TemplateSpec) {
                                $baseHuntingQueryResource = [PSCustomObject] @{
                                    type       = "Microsoft.OperationalInsights/workspaces";
                                    apiVersion = $contentResourceDetails.huntingOperationalInsightsWorkspacesApiVersion;
                                    name       = "[parameters('workspace')]";
                                    location   = "[parameters('workspace-location')]";
                                    resources  = @()
                                }
                                $global:baseMainTemplate.resources += $baseHuntingQueryResource
                            }
                            if (!$contentToImport.TemplateSpec -and $null -eq $global:baseMainTemplate.variables.'workspace-dependency') {
                                #Add parser dependency variable once to ensure validation passes.
                                $global:baseMainTemplate.variables | Add-Member -MemberType NoteProperty -Name "workspace-dependency" -Value "[concat('Microsoft.OperationalInsights/workspaces/', parameters('workspace'))]"
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
                            $global:baseCreateUiDefinition.parameters.steps += $huntingQueryBaseStep
                        }

                        if($yaml.metadata -and $yaml.metadata.source -and $yaml.metadata.source.kind -and ($yaml.metadata.source.kind -eq "Community" -or $yaml.metadata.source.kind -eq "Standalone"))
                        {
                            throw "The file $fileName has metadata with source -> kind = Community | Standalone. Please remove it so that it can be packaged as a solution."
                        }

                        $huntingQueryObj = [PSCustomObject] @{
                            type       = $contentToImport.TemplateSpec ? "Microsoft.OperationalInsights/savedSearches" : "savedSearches";
                            apiVersion = $contentResourceDetails.savedSearchesApiVersion; #"2020-08-01";
                            name       = $contentToImport.TemplateSpec ? "$($solutionName.Replace(' ', '_'))_Hunting_Query_$global:huntingQueryCounter" : "$solutionName Hunting Query $global:huntingQueryCounter";
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
                            #$huntingQueryDescription = $yaml.description.substring(1, $yaml.description.length - 3)
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

                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQueryId$global:huntingQueryCounter" -NotePropertyValue "[resourceId('Microsoft.OperationalInsights/savedSearches', variables('_huntingQuerycontentId$global:huntingQueryCounter'))]"

                            if ($contentResourceDetails.apiVersion -eq '3.0.0')
                            {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQueryTemplateSpecName$global:huntingQueryCounter" -NotePropertyValue "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(concat(parameters('workspace'),'-hq-',uniquestring(variables('_huntingQuerycontentId$global:huntingQueryCounter'))),variables('huntingQueryVersion$global:huntingQueryCounter')))]"
                            }
                            else 
                            {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "huntingQueryTemplateSpecName$global:huntingQueryCounter" -NotePropertyValue "[concat(parameters('workspace'),'-hq-',uniquestring(variables('_huntingQuerycontentId$global:huntingQueryCounter')))]"
                            }

                            if (!$global:baseMainTemplate.variables.workspaceResourceId -and $contentResourceDetails.contentSchemaVersion -ne '3.0.0') {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                            }

                            if ($contentResourceDetails.contentSchemaVersion -ne '3.0.0')
                            {
                                $baseHuntingQueryTemplateSpec = [PSCustomObject]@{
                                    type       = $contentResourceDetails.resourcetype; # "Microsoft.Resources/templateSpecs";
                                    apiVersion = $contentResourceDetails.templateSpecsApiVersion; #"2022-02-01";
                                    name       = "[variables('huntingQueryTemplateSpecName$global:huntingQueryCounter')]";
                                    location   = "[parameters('workspace-location')]";
                                    tags       = [PSCustomObject]@{
                                        "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                        "hidden-sentinelContentType" = "HuntingQuery";
                                    };
                                    properties = [PSCustomObject]@{
                                        description = "$($solutionName) Hunting Query $global:huntingQueryCounter with template";
                                        displayName = "$($solutionName) Hunting Query template";
                                    }
                                }

                                if($baseHuntingQueryTemplateSpec.properties.displayName.length -ge 64)
                                {
                                    $baseHuntingQueryTemplateSpec.properties.displayName = "$($solutionName) HQ template";
                                }

                                $global:baseMainTemplate.resources += $baseHuntingQueryTemplateSpec
                            }
                            
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
                                apiVersion = $contentResourceDetails.commonResourceMetadataApiVersion; #"2022-01-01-preview";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('HuntingQuery-', last(split(variables('huntingQueryId$global:huntingQueryCounter'),'/'))))]";
                                properties = [PSCustomObject]@{
                                    description = "$($solutionName) Hunting Query $global:huntingQueryCounter";
                                    parentId  = "[variables('huntingQueryId$global:huntingQueryCounter')]";
                                    contentId = "[variables('_huntingQuerycontentId$global:huntingQueryCounter')]";
                                    kind      = "HuntingQuery";
                                    version   = "[variables('huntingQueryVersion$global:huntingQueryCounter')]";
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
                                type       = $contentResourceDetails.subtype; # "Microsoft.Resources/templateSpecs/versions";
                                apiVersion = $contentResourceDetails.templateSpecsVersionApiVersion;
                                name       = $contentResourceDetails.apiVersion -eq '3.0.0' ? "[variables('huntingQueryTemplateSpecName$global:huntingQueryCounter')]" : "[concat(variables('huntingQueryTemplateSpecName$global:huntingQueryCounter'),'/',variables('huntingQueryVersion$global:huntingQueryCounter'))]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "HuntingQuery";
                                };

                                dependsOn  = $contentResourceDetails.apiVersion -eq '3.0.0' ? @(
                                "$($contentResourceDetails.dependsOn)") : @(
                                    "$($contentResourceDetails.dependsOn), variables('huntingQueryTemplateSpecName$global:huntingQueryCounter'))]"
                                );
                                properties = [PSCustomObject]@{
                                    description  = "$($fileName) Hunting Query with template version $($contentToImport.Version)";
                                    mainTemplate = [PSCustomObject]@{
                                        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                        contentVersion = "[variables('huntingQueryVersion$global:huntingQueryCounter')]";
                                        parameters     = [PSCustomObject]@{};
                                        variables      = [PSCustomObject]@{};
                                        resources      = @(
                                            # workbook
                                            $huntingQueryObj,
                                            # Metadata
                                            $huntingQueryMetadata
                                        )
                                    };
                                }
                            }
                            if ($contentResourceDetails.apiVersion -eq '3.0.0')
                            {
                                $huntingQueryTemplateSpecContent = SetContentTemplateDefaultValuesToProperties -templateSpecResourceObj $huntingQueryTemplateSpecContent
                                $huntingQueryTemplateSpecContent.properties.contentId = "[variables('_huntingQuerycontentId$global:huntingQueryCounter')]"
                                $huntingQueryTemplateSpecContent.properties.contentKind = "HuntingQuery"
                                $huntingQueryTemplateSpecContent.properties.displayName = $yaml.name

                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_huntingQuerycontentProductId$global:huntingQueryCounter" -NotePropertyValue "[concat(take(variables('_solutionId'),50),'-','hq','-', uniqueString(concat(variables('_solutionId'),'-','HuntingQuery','-',variables('_huntingQuerycontentId$global:huntingQueryCounter'),'-', variables('huntingQueryVersion$global:huntingQueryCounter'))))]"
				$huntingQueryTemplateSpecContent.properties.contentProductId = "[variables('_huntingQuerycontentProductId$global:huntingQueryCounter')]"
                                $huntingQueryTemplateSpecContent.properties.id = "[variables('_huntingQuerycontentProductId$global:huntingQueryCounter')]"
                                $huntingQueryTemplateSpecContent.properties.version = "[variables('huntingQueryVersion$global:huntingQueryCounter')]"
                                $huntingQueryTemplateSpecContent.PSObject.Properties.Remove('tags')
                            }
                            $global:baseMainTemplate.resources += $huntingQueryTemplateSpecContent
                        }
                        else{
                            if(!$contentToImport.TemplateSpec)
                            {
                                $dependsOn  = @(
                                    "[variables('workspace-dependency')]"
                                );

                                $huntingQueryObj | Add-Member -NotePropertyName "dependsOn" -NotePropertyValue $dependsOn
                            }
                            $queryLocation = $(getQueryResourceLocation)
                            if ($null -eq $queryLocation)
                            {
                                Write-Host "For Hunting queries getQueryResourceLocation function returned null for $file which is not valid!"
                                return;
                            }
                            else {
                                $global:baseMainTemplate.resources[$(getQueryResourceLocation)].resources += $huntingQueryObj
                            }
                        }
                        $dependencyDescription = ""
                        if ($yaml.requiredDataConnectors) {
                            $dependencyDescription = "This hunting query depends on $($yaml.requiredDataConnectors.connectorId) data connector ($($($yaml.requiredDataConnectors.dataTypes)) Parser or Table)"
                        }
                        $huntingQueryElement = [PSCustomObject]@{
                            name     = "huntingquery$global:huntingQueryCounter";
                            type     = "Microsoft.Common.Section";
                            label    = $yaml.name;
                            elements = @()
                        }
                        $huntingQueryElementDescription = [PSCustomObject]@{
                            name    = "huntingquery$global:huntingQueryCounter-text";
                            type    = "Microsoft.Common.TextBlock";
                            options = [PSCustomObject]@{
                                text = "$($huntingQueryDescription)$dependencyDescription";
                            }
                        }
                        if ($huntingQueryDescription -or $dependencyDescription) {
                            $huntingQueryElement.elements += $huntingQueryElementDescription
                        }
                        $global:baseCreateUiDefinition.parameters.steps[$global:baseCreateUiDefinition.parameters.steps.Count - 1].elements += $huntingQueryElement

                        # Update HuntingQuery Counter
                        $global:huntingQueryCounter += 1
    }

    function GenerateAlertRule($file, $contentResourceDetails)
    {
        
                        # If yaml and not hunting query, process as Alert Rule
                        Write-Host "Generating Alert Rule using $file"
                        if ($global:analyticRuleCounter -eq 1) {
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
                            $global:baseCreateUiDefinition.parameters.steps += $baseAnalyticRuleStep
                        }
                        $yamlPropertiesToCopyFrom = "name", "severity", "triggerThreshold", "query"
                        $yamlPropertiesToCopyTo = "displayName", "severity", "triggerThreshold", "query"
                        $alertRuleParameterName = "analytic$global:analyticRuleCounter-id"
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

                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRuleVersion$global:analyticRuleCounter" -NotePropertyValue (($null -ne $yaml.version) ? "$($yaml.version)" : "1.0.0")
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRulecontentId$global:analyticRuleCounter" -NotePropertyValue "$($yaml.id)"
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_analyticRulecontentId$global:analyticRuleCounter" -NotePropertyValue "[variables('analyticRulecontentId$global:analyticRuleCounter')]"
                        $global:DependencyCriteria += [PSCustomObject]@{
                            kind      = "AnalyticsRule";
                            contentId = "[variables('analyticRulecontentId$global:analyticRuleCounter')]";
                            #post bug bash ,remove this below comments!
                            version   = "[variables('analyticRuleVersion$global:analyticRuleCounter')]";
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
                            if (!$global:baseMainTemplate.variables.TemplateEmptyArray) 
                            {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "TemplateEmptyArray" -NotePropertyValue "[json('[]')]"
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
                            name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('analytic$global:analyticRuleCounter-id'))]";
                            apiVersion = $contentResourceDetails.alertRuleApiVersion; #"2022-04-01-preview";
                            kind       =  "$($yaml.kind)";
                            location   = "[parameters('workspace-location')]";
                            properties = $alertRule;
                        }

                        if($contentToImport.TemplateSpec) {

                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRuleId$global:analyticRuleCounter" -NotePropertyValue "[resourceId('Microsoft.SecurityInsights/AlertRuleTemplates', variables('analyticRulecontentId$global:analyticRuleCounter'))]"

                            if ($contentResourceDetails.apiVersion -eq '3.0.0')
                            {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRuleTemplateSpecName$global:analyticRuleCounter" -NotePropertyValue "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(concat(parameters('workspace'),'-ar-',uniquestring(variables('_analyticRulecontentId$global:analyticRuleCounter'))),variables('analyticRuleVersion$global:analyticRuleCounter')))]"
                            }
                            else 
                            {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "analyticRuleTemplateSpecName$global:analyticRuleCounter" -NotePropertyValue "[concat(parameters('workspace'),'-ar-',uniquestring(variables('_analyticRulecontentId$global:analyticRuleCounter')))]"
                            }

                            if (!$global:baseMainTemplate.variables.workspaceResourceId -and $contentResourceDetails.contentSchemaVersion -ne '3.0.0') {
                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
                            }
                            
                            if ($contentResourceDetails.contentSchemaVersion -ne '3.0.0')
                            {
                                $baseAnalyticRuleTemplateSpec = [PSCustomObject]@{
                                    type       = $contentResourceDetails.resourcetype; # "Microsoft.Resources/templateSpecs";
                                    apiVersion = $contentResourceDetails.templateSpecsApiVersion; #"2022-02-01";
                                    name       = "[variables('analyticRuleTemplateSpecName$global:analyticRuleCounter')]";
                                    location   = "[parameters('workspace-location')]";
                                    tags       = [PSCustomObject]@{
                                        "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                        "hidden-sentinelContentType" = "AnalyticsRule";
                                    };
                                    properties = [PSCustomObject]@{
                                        description = "$($solutionName) Analytics Rule $global:analyticRuleCounter with template";
                                        displayName = "$($solutionName) Analytics Rule template";
                                    }
                                }

                                if ($baseAnalyticRuleTemplateSpec.properties.displayName.length -ge 64)
                                {
                                    $baseAnalyticRuleTemplateSpec.properties.displayName = "$($solutionName) AR template";
                                }
                                $global:baseMainTemplate.resources += $baseAnalyticRuleTemplateSpec
                            }

                            $newAnalyticRule.name = "[variables('analyticRulecontentId$global:analyticRuleCounter')]"
                            
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
                                apiVersion = $contentResourceDetails.commonResourceMetadataApiVersion; #"2022-01-01-preview";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('AnalyticsRule-', last(split(variables('analyticRuleId$global:analyticRuleCounter'),'/'))))]";
                                properties = [PSCustomObject]@{
                                    description = "$($solutionName) Analytics Rule $global:analyticRuleCounter";
                                    parentId  = "[variables('analyticRuleId$global:analyticRuleCounter')]";
                                    contentId = "[variables('_analyticRulecontentId$global:analyticRuleCounter')]";
                                    kind      = "AnalyticsRule";
                                    # Need to remove the below assigned property for the yaml version after bug bash
                                    version   = "[variables('analyticRuleVersion$global:analyticRuleCounter')]";
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
                                type       = $contentResourceDetails.subtype; # "Microsoft.Resources/templateSpecs/versions";
                                apiVersion = $contentResourceDetails.templateSpecsVersionApiVersion;
                                name       = $contentResourceDetails.apiVersion -eq '3.0.0' ? "[variables('analyticRuleTemplateSpecName$global:analyticRuleCounter')]" : "[concat(variables('analyticRuleTemplateSpecName$global:analyticRuleCounter'),'/',variables('analyticRuleVersion$global:analyticRuleCounter'))]";
                                location   = "[parameters('workspace-location')]";
                                tags       = [PSCustomObject]@{
                                    "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                                    "hidden-sentinelContentType" = "AnalyticsRule";
                                };

                                dependsOn  = $contentResourceDetails.apiVersion -eq '3.0.0' ? @(
                                "$($contentResourceDetails.dependsOn)") : @(
                                    "$($contentResourceDetails.dependsOn), variables('analyticRuleTemplateSpecName$global:analyticRuleCounter'))]"
                                );
                                properties = [PSCustomObject]@{
                                    description  = "$($fileName) Analytics Rule with template version $($contentToImport.Version)";
                                    mainTemplate = [PSCustomObject]@{
                                        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                                        contentVersion = "[variables('analyticRuleVersion$global:analyticRuleCounter')]";
                                        parameters     = [PSCustomObject]@{};
                                        variables      = [PSCustomObject]@{};
                                        resources      = @(
                                            # Analytics Rule
                                            $newAnalyticRule,
                                            # Metadata
                                            $analyticRuleMetadata
                                        )
                                    };
                                }
                            }
                            if ($contentResourceDetails.apiVersion -eq '3.0.0')
                            {
                                $analyticRuleTemplateSpecContent = SetContentTemplateDefaultValuesToProperties -templateSpecResourceObj $analyticRuleTemplateSpecContent
                                $analyticRuleTemplateSpecContent.properties.contentId = "[variables('_analyticRulecontentId$global:analyticRuleCounter')]"
                                $analyticRuleTemplateSpecContent.properties.contentKind = "AnalyticsRule"
                                $analyticRuleTemplateSpecContent.properties.displayName = $yaml.name

                                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_analyticRulecontentProductId$global:analyticRuleCounter" -NotePropertyValue "[concat(take(variables('_solutionId'),50),'-','ar','-', uniqueString(concat(variables('_solutionId'),'-','AnalyticsRule','-',variables('_analyticRulecontentId$global:analyticRuleCounter'),'-', variables('analyticRuleVersion$global:analyticRuleCounter'))))]"
				$analyticRuleTemplateSpecContent.properties.contentProductId = "[variables('_analyticRulecontentProductId$global:analyticRuleCounter')]"
                                $analyticRuleTemplateSpecContent.properties.id = "[variables('_analyticRulecontentProductId$global:analyticRuleCounter')]"
                                $analyticRuleTemplateSpecContent.properties.version = "[variables('analyticRuleVersion$global:analyticRuleCounter')]"
                                $analyticRuleTemplateSpecContent.PSObject.Properties.Remove('tags')
                            }
                            $global:baseMainTemplate.resources += $analyticRuleTemplateSpecContent
                        }
                        else {
                            # Add Resource and Parameters to Template
                            $global:baseMainTemplate.resources += $newAnalyticRule
                        }

                        if(!$contentToImport.TemplateSpec)
                        {
                            $global:baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $alertRuleParameterName -Value $alertRuleParameter
                        }
                        $alertRuleUIParameter = [PSCustomObject] @{ name = "analytic$global:analyticRuleCounter"; type = "Microsoft.Common.Section"; label = $alertRule.displayName; elements = @( [PSCustomObject] @{ name = "analytic$global:analyticRuleCounter-text"; type = "Microsoft.Common.TextBlock"; options = @{ text = $alertRule.description; } } ) }
                        $global:baseCreateUiDefinition.parameters.steps[$global:baseCreateUiDefinition.parameters.steps.Count - 1].elements += $alertRuleUIParameter

                        # Update Counter
                        $global:analyticRuleCounter += 1
                    
    }

    function GenerateWatchList($json, $isPipelineRun)
    {
        $watchlistData = $json.resources[0]

                    $watchlistName = $watchlistData.properties.displayName;
                    if ($contentToImport.Metadata -or $isPipelineRun) {
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName $watchlistName -NotePropertyValue $watchlistName
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_$watchlistName" -NotePropertyValue "[variables('$watchlistName')]"
                    }

                    $global:DependencyCriteria += [PSCustomObject]@{
                        kind      = "Watchlist";
                        contentId = "[variables('_$watchlistName')]";
                        version   = $contentToImport.Version;
                    };

                    #Handle CreateUiDefinition Base Step
                    if ($global:watchlistCounter -eq 1) {
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
                        $global:baseCreateUiDefinition.parameters.steps += $baseWatchlistStep
                    }

                    #Handle CreateUiDefinition Step Sub-Element
                    $watchlistDescriptionText = $(if ($contentToImport.WatchlistDescription -and $contentToImport.WatchlistDescription -is [System.Array]) { $contentToImport.WatchlistDescription[$global:watchlistCounter - 1] } elseif ($contentToImport.WatchlistDescription -and $contentToImport.WatchlistDescription -is [System.String]) { $contentToImport.WatchlistDescription } else { $watchlistData.properties.description })
                    $currentStepNum = $global:baseCreateUiDefinition.parameters.steps.Count - 1
                    $watchlistStepElement = [PSCustomObject]@{
                        name     = "watchlist$global:watchlistCounter";
                        type     = "Microsoft.Common.Section";
                        label    = $watchlistData.properties.displayName;
                        elements = @(
                            [PSCustomObject]@{
                                name    = "watchlist$global:watchlistCounter-text";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject]@{
                                    text = $watchlistDescriptionText
                                }
                            }
                        )
                    }
                    $global:baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $watchlistStepElement

                    # Add Watchlist ID to MainTemplate parameters
                    $watchlistIdParameterName = "watchlist$global:watchlistCounter-id"
                    $watchlistIdParameter = [PSCustomObject] @{ type = "string"; defaultValue = "$($watchlistData.properties.watchlistAlias)"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the watchlist" }; }
                    $global:baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $watchlistIdParameterName -Value $watchlistIdParameter

                    # Replace watchlist resource id
                    $watchlistData.name = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('watchlist$global:watchlistCounter-id'))]"

                    # Handle MainTemplate Resource
                    $global:baseMainTemplate.resources += $watchlistData #Assume 1 watchlist per template

                    # Update Watchlist Counter
                    $global:watchlistCounter += 1
    }


    function GenerateSavedSearches($json, $contentResourceDetails)
    {
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
                            $savedSearchIdParameterName = "savedsearch$global:savedSearchCounter-id"
                            $savedSearchIdParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the watchlist" }; }
                            $global:baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $savedSearchIdParameterName -Value $savedSearchIdParameter

                            $savedSearchResource = [PSCustomObject]@{
                                type       = "Microsoft.OperationalInsights/workspaces/savedSearches";
                                apiVersion =  $contentResourceDetails.savedSearchesApiVersion; #"2020-08-01";
                                name       = "[concat(parameters('workspace'),'/',parameters('$savedSearchIdParameterName'))]";
                                properties = [PSCustomObject]@{
                                    category      = $search.properties.category;
                                    displayName   = $search.properties.displayName;
                                    query         = $search.properties.query;
                                    functionAlias = $search.properties.functionAlias;
                                    version       = $search.properties.version;
                                };
                            }
                            $global:baseMainTemplate.resources += $savedSearchResource
                            $global:savedSearchCounter++
                        }
                    }
                    elseif ($isStandardTemplate) {
                        $global:baseMainTemplate.resources += $searchData
                    }
    }

    function GenerateParsersList($file, $contentToImport, $contentResourceDetails)
    {
        # Assume file is Parser due to parsers having inconsistent types. (.txt, .kql, or none)
        Write-Host "Generating Data Parser using $file"
        generateParserContent $file $contentToImport $contentResourceDetails
    }

    function RunArmTtkOnPackage
    {
        param(
            [Parameter(Mandatory=$True)]
            [string]$solutionName,
            [Parameter(Mandatory=$True)]
            [System.Boolean]$isPipelineRun
        )
        if ($isPipelineRun -eq $false)
        {
            #downloading and running arm-ttk on generated solution
            $armTtkFolder = "$PSScriptRoot/../arm-ttk"
            if (!$(Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)) {
                Write-Output "Missing arm-ttk validations. Downloading module..."
                Invoke-Expression "$armTtkFolder/download-arm-ttk.ps1"
            }
            Invoke-Expression "$armTtkFolder/run-arm-ttk-in-automation.ps1 '$solutionName'"
        }
    }

    function GeneratePackage($solutionName, $contentToImport, $calculatedBuildPipelinePackageVersion = '')
    {
        if ($contentToImport.Description) {
            $global:baseCreateUiDefinition.parameters.config.basics.description = $global:baseCreateUiDefinition.parameters.config.basics.description -replace "{{SolutionDescription}}", $contentToImport.Description
        }
        else {
            $global:baseCreateUiDefinition.parameters.config.basics.description = $global:baseCreateUiDefinition.parameters.config.basics.description -replace "{{SolutionDescription}}", ""
        }
        
        # Update the descriptionHtml field and icon field only for the content templates 
        #    and for resource type /contenttemplates
        if ($contentResourceDetails.apiVersion -eq '3.0.0')
        {
            $updatecontentpackage = $baseMainTemplate.resources | Where-Object {$_.type -eq "Microsoft.OperationalInsights/workspaces/providers/contentPackages"}
            $descriptionHtml = $global:baseCreateUiDefinition.parameters.config.basics.description -replace "{{Logo}}\n\n", ""
            $md = $descriptionHtml | ConvertFrom-Markdown
            $updatecontentpackage.properties.descriptionHtml = $md.Html
            $updatecontentpackage.properties.icon = $contentToImport.Logo
        }
        # Update Logo in CreateUiDefinition Description
        if ($contentToImport.Logo) {
            $global:baseCreateUiDefinition.parameters.config.basics.description = $global:baseCreateUiDefinition.parameters.config.basics.description -replace "{{Logo}}", $contentToImport.Logo
        }
        else {
            $global:baseCreateUiDefinition.parameters.config.basics.description = $global:baseCreateUiDefinition.parameters.config.basics.description -replace "{{Logo}}\n\n", ""
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
            $global:baseCreateUiDefinition.parameters.steps = $global:baseCreateUiDefinition.parameters.steps | Sort-Object { $createUiDefinitionOrder.IndexOf($_.name) }
            # Ensure single-step UI Definitions have proper type for steps
            if ($($global:baseCreateUiDefinition.parameters.steps).GetType() -ne [System.Object[]]) {
                $global:baseCreateUiDefinition.parameters.steps = @($global:baseCreateUiDefinition.parameters.steps)
            }
            $global:baseCreateUiDefinition | ConvertTo-Json -Depth $jsonConversionDepth | Out-File $createUiDefinitionOutputPath -Encoding utf8
        }
        catch {
            Write-Host "Failed to write output file $createUiDefinitionOutputPath" -ForegroundColor Red
            break;
        }
        
        if ($calculatedBuildPipelinePackageVersion -eq '')
        {
            $zipPackageName = "$(if($contentToImport.Version){$contentToImport.Version}else{"newSolutionPackage"}).zip"
        }
        else {
            $zipPackageName = "$calculatedBuildPipelinePackageVersion" + ".zip"
        }
        Compress-Archive -Path "$solutionFolder/*" -DestinationPath "$solutionFolder/$zipPackageName" -Force
    }

    function global:GetContentTemplateDefaultValues()
    {
        return @{
            'packageKind' = "Solution"
            'packageVersion' = "[variables('_solutionVersion')]"
            'packageName' = "[variables('_solutionName')]"
            'packageId' = "[variables('_solutionId')]"
            'contentSchemaVersion' = '3.0.0'
        }
    }

    function global:SetContentTemplateDefaultValuesToProperties($templateSpecResourceObj)
    {
        $contentTemplateDefaultValues = GetContentTemplateDefaultValues
        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "packageKind" -Value $contentTemplateDefaultValues.packageKind

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "packageVersion" -Value $contentTemplateDefaultValues.packageVersion

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "packageName" -Value $contentTemplateDefaultValues.packageName

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "packageId" -Value $contentTemplateDefaultValues.packageId

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "contentSchemaVersion" -Value $contentTemplateDefaultValues.contentSchemaVersion

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "contentId" -Value ""

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "contentKind" -Value ""

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "displayName" -Value ""

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "contentProductId" -Value ""

        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "id" -Value ""
        
        $templateSpecResourceObj.properties | Add-Member -MemberType NoteProperty -Name "version" -Value ""

        return $templateSpecResourceObj
    }
# =================START: RESOURCE CONTENT BY VERSION=====================
    function global:returnContentResources ($item)
    {
        try
        {
            $dict = $null;   
            $version =  constructVersionNumber($item) 
            if($version.Major -eq 3)
            {    
                $dict = @{
                    #'resourcetype' = "Microsoft.OperationInsights/workspaces/providers/contentPackages"
                    'subtype' = "Microsoft.OperationalInsights/workspaces/providers/contentTemplates"
                    'dependsOn' = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
                    'metadata' = "Microsoft.OperationalInsights/workspaces/providers/contentPackages"
                    'contentSchemaVersion' = '3.0.0'
                    'apiVersion' = '3.0.0'

                    'metadataApiVersion' = '2023-04-01-preview'
                    'templateSpecsVersionApiVersion' = '2023-04-01-preview'

                    'resources' = @("Microsoft.OperationalInsights/workspaces/providers/dataConnectors",
                                    "Microsoft.OperationalInsights/workspaces/providers/metadata",
                                    "Microsoft.OperationalInsights/workspaces/savedSearches",
                                    "Microsoft.OperationalInsights/workspaces/providers/Watchlists",
                                    "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
                                    "Microsoft.OperationalInsights/workspaces/providers/contentPackages")
                    }
            }
            elseif ($version.Major -eq 2)
            {
                $dict = @{
                    'resourcetype' = "Microsoft.Resources/templateSpecs"
                    'subtype' = "Microsoft.Resources/templateSpecs/versions"
                    'dependsOn' = "[resourceId('Microsoft.Resources/templateSpecs'"
                    'metadata' = "Microsoft.OperationalInsights/workspaces/providers/metadata"
                    'contentSchemaVersion' = '2.0.0'
                    'apiVersion' = '2.0.0'

                    'metadataApiVersion' = '2022-01-01-preview'
                    'templateSpecsVersionApiVersion' = '2022-02-01'

                    'resources' = @("Microsoft.OperationalInsights/workspaces/providers/dataConnectors",
                                    "Microsoft.OperationalInsights/workspaces/providers/metadata",
                                    "Microsoft.OperationalInsights/workspaces/savedSearches",
                                    "Microsoft.OperationalInsights/workspaces/providers/Watchlists",
                                    "Microsoft.Resources/templateSpecs",
                                    "Microsoft.Resources/templateSpecs/versions")
                    }
            }
            else
            {
                Write-Host "Returning Empty dictionary object because the version information is given as null or empty" -ForegroundColor Red
                return $dict 
            }

            if ($null -ne $dict)
            {
                # ADD COMMON API VERSION
                $dict.Add('templateSpecsApiVersion', '2022-02-01')
                $dict.Add('dataConnectorsApiVersion', '2021-03-01-preview')
                $dict.Add('huntingOperationalInsightsWorkspacesApiVersion', '2021-06-01')
                $dict.Add('parserOperationalInsightsWorkspacesApiVersion', '2020-08-01')
                $dict.Add('savedSearchesApiVersion', '2022-10-01')
                $dict.Add('alertRuleApiVersion', '2022-04-01-preview')
                $dict.Add('commonResourceMetadataApiVersion', '2022-01-01-preview')
                $dict.Add('insightsWorkbookApiVersion', '2021-08-01')
            }

            return $dict
        }
        catch 
        {
                Write-Host "Expected Version information is coming as null. Please correct the version number accordingly: $($_.Exception.Message)" -ForegroundColor Red
                break;
        }
    }

    function global:constructVersionNumber($version)
    {
        $major,$minor,$build,$revision = $version.split(".")    
        $version = [version]::new($major,$minor,$build)
        return $version
    }
# =================END: RESOURCE CONTENT BY VERSION=====================

function ConvertHashTo-StringData {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, Position = 0, ValueFromPipeline)]
        [HashTable[]]$HashTable
    )
        $Parameters = ""
        foreach ($item in $HashTable) {
            if($Parameters -ne "")
            {
                $Parameters = $Parameters + ","
            }
            if($item.Type.StartsWith('table:'))
            {
                $Parameters = $Parameters + "{0}:{1}" -f $item.Name, $item.Type.split(":")[-1]
            }
            else
            {
                if($null -ne $item.Default)
                {
                    $Default = $item.Default
                    if($item.Type.ToLower() -eq 'string')
                    {
                        $Default = "'$default'"
                    }
                    $Parameters = $Parameters + "{0}:{1}={2}" -f $item.Name, $item.Type,$Default
                }
                else {
                    $Parameters = $Parameters + "{0}:{1}" -f $item.Name, $item.Type
                }
            }
        }
        return $Parameters
}

function global:GenerateIdHash($packageId, $contentKind, $contentId, $contentVersion)
{
    if ([string]::IsNullOrWhiteSpace($packageId) -or [string]::IsNullOrEmpty($contentId))
    {
            return [string]::Empty
    }
    $sb = [System.Text.StringBuilder]::new()
    [int]$limit = 50
    $sb.Append($packageId.Length -gt $limit ? $packageId.Substring(0, $limit) : $packageId).Append('-')
    if ($ContentKindDict.ContainsKey($contentKind))
    {
            $sb.Append($ContentKindDict[$contentKind])
    }
    else
    {
            $sb.Append($contentKind.ToString().substring(0,2).tolower())
    }
    $sb.Append('-')
    $str = "$packageId-$($contentKind.ToString())-$contentId";
    if ([string]::IsNullOrEmpty($contentVersion))
    {
        $str += "-$contentVersion";
    }
    $val = HashLine -value $str
    $sb.Append($val)
    return $sb.ToString()
}

function HashLine($value)
{
        $val = [string](Base32Encode -charValue "$(ComputeSHA($value))")
        return $val.ToString()
}

function  ComputeSHA {
    Param (
    [Parameter(Mandatory=$true)]
    [string]
    $ClearString
    )
    $hasher = [System.Security.Cryptography.HashAlgorithm]::Create('sha256')
    $hash = $hasher.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($ClearString))
    $hashString = [System.BitConverter]::ToInt32($hash)
    return $hashString
}

function Base32Encode([uint32]$charValue)
{  
        $chars = "abcdefghijklmnopqrstuvwxyz234567"
        $Charset = ($chars).ToCharArray()

        $sb = [System.Text.StringBuilder]::new()
        for($index = 0; $index -lt 13; $index++)
        {
                $sb.Append($Charset[[int]($charValue -shr 59)])
                $charValue -shl 5
        }
        return $sb.ToString()
}

function addTemplateSpecParserResource($content,$yaml,$isyaml, $contentResourceDetails)
{
        # Add workspace resource ID if not available
        if (!$global:baseMainTemplate.variables.workspaceResourceId -and $contentResourceDetails.contentSchemaVersion -ne '3.0.0') {
            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
        }

        if ($contentResourceDetails.contentSchemaVersion -ne '3.0.0')
        {
            # Add base templateSpec
            $baseParserTemplateSpec = [PSCustomObject]@{
                type       = "Microsoft.Resources/templateSpecs";
                apiVersion = $contentResourceDetails.templateSpecsApiVersion;  #"2022-02-01";
                name       = "[variables('parserTemplateSpecName$global:parserCounter')]";
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
            $global:baseMainTemplate.resources += $baseParserTemplateSpec
        }
        # Parser Content
        $parserContent = [PSCustomObject]@{
            name       = "[variables('_parserName$global:parserCounter')]";
            apiVersion = $contentResourceDetails.savedSearchesApiVersion; #"2020-08-01";
            type       = "Microsoft.OperationalInsights/workspaces/savedSearches";
            location   = "[parameters('workspace-location')]";
            properties = [PSCustomObject]@{
                eTag          = "*"
                displayName   = "$($displayDetails.displayName)"
                category      = $isyaml ? "$($yaml.Category)" : "Samples"
                functionAlias = "$($displayDetails.functionAlias)"
                query         = $isyaml ? "$($yaml.FunctionQuery)" : "$content"
                functionParameters = $isyaml ? "$(ConvertHashTo-StringData $yaml.FunctionParams)" : ""
                version       = $isyaml ? 2 : 1
                tags          = @([PSCustomObject]@{
                    "name"  = "description"
                    "value" = $isyaml ? "$($yaml.Description)" : "$($displayDetails.displayName)"
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
            apiVersion = $contentResourceDetails.commonResourceMetadataApiVersion; #"2022-01-01-preview";
            name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('Parser-', last(split(variables('_parserId$global:parserCounter'),'/'))))]";
            dependsOn  =  @(
                "[variables('_parserName$global:parserCounter')]"
            );
            properties = [PSCustomObject]@{
                parentId  = "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', parameters('workspace'), variables('parserName$global:parserCounter'))]"
                contentId = "[variables('_parserContentId$global:parserCounter')]";
                kind      = "Parser";
                version   = "[variables('parserVersion$global:parserCounter')]";
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
            type       =  $contentResourceDetails.subtype; #"Microsoft.Resources/templateSpecs/versions";
            apiVersion = $contentResourceDetails.templateSpecsVersionApiVersion;
            name       = $contentResourceDetails.apiVersion -eq '3.0.0' ? "[variables('parserTemplateSpecName$global:parserCounter')]" : "[concat(variables('parserTemplateSpecName$global:parserCounter'),'/',variables('parserVersion$global:parserCounter'))]";
            location   = "[parameters('workspace-location')]";
            tags       = [PSCustomObject]@{
                "hidden-sentinelWorkspaceId" = "[variables('workspaceResourceId')]";
                "hidden-sentinelContentType" = "Parser";
            };
            dependsOn  = $contentResourceDetails.apiVersion -eq '3.0.0' ? @(
                                "$($contentResourceDetails.dependsOn)") : @(
                "[resourceId('Microsoft.Resources/templateSpecs', variables('parserTemplateSpecName$global:parserCounter'))]"
            );
            properties = [PSCustomObject]@{
                description  = "$($fileName) Data Parser with template version $($contentToImport.Version)";
                mainTemplate = [PSCustomObject]@{
                    '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                    contentVersion = "[variables('parserVersion$global:parserCounter')]";
                    parameters     = [PSCustomObject]@{};
                    variables      = [PSCustomObject]@{};
                    resources      = @(
                        # Parser
                        $parserContent,
                        # Metadata
                        $parserMetadata
                    )
                };
                
            }
        }
        if ($contentResourceDetails.apiVersion -eq '3.0.0')
        {
            $parserTemplateSpecContent = SetContentTemplateDefaultValuesToProperties -templateSpecResourceObj $parserTemplateSpecContent
            $parserTemplateSpecContent.properties.contentId = "[variables('_parserContentId$global:parserCounter')]"
            $parserTemplateSpecContent.properties.contentKind = "Parser"
            $parserTemplateSpecContent.properties.displayName = "$($displayDetails.displayName)"

            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_parsercontentProductId$global:parserCounter" -NotePropertyValue "[concat(take(variables('_solutionId'),50),'-','$($ContentKindDict.ContainsKey("Parser") ? $ContentKindDict["Parser"] : '')','-', uniqueString(concat(variables('_solutionId'),'-','Parser','-',variables('_parserContentId$global:parserCounter'),'-', variables('parserVersion$global:parserCounter'))))]"
	    $parserTemplateSpecContent.properties.contentProductId = "[variables('_parsercontentProductId$global:parserCounter')]"
            $parserTemplateSpecContent.properties.id = "[variables('_parsercontentProductId$global:parserCounter')]"
            $parserTemplateSpecContent.properties.version = "[variables('parserVersion$global:parserCounter')]"
            $parserTemplateSpecContent.PSObject.Properties.Remove('tags')
        }
        
        $global:baseMainTemplate.resources += $parserTemplateSpecContent

        $parserObj = [PSCustomObject] @{
            type       = "Microsoft.OperationalInsights/workspaces/savedSearches";
            apiVersion = $contentResourceDetails.savedSearchesApiVersion; #"2020-08-01";
            name       = "[variables('_parserName$parserCounter')]";
            location   = "[parameters('workspace-location')]";
            properties = [PSCustomObject] @{
                eTag          = "*"
                displayName   = "$($displayDetails.displayName)"
                category      = $isyaml ? "$($yaml.Category)" :"Samples"
                functionAlias = "$($displayDetails.functionAlias)"
                query         = $isyaml ? "$($yaml.FunctionQuery)" : "$content"
                functionParameters = $isyaml ? "$(ConvertHashTo-StringData $yaml.FunctionParams)" : ""
                version       = $isyaml ? 2 : 1
                tags          = @([PSCustomObject]@{
                    "name"  = "description"
                    "value" = $isyaml ? "$($yaml.Description)" : "$($displayDetails.displayName)"
                    };
                )
            }
        }
        $global:baseMainTemplate.resources += $parserObj

        $parserMetadata = [PSCustomObject]@{
            type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
            apiVersion = $contentResourceDetails.commonResourceMetadataApiVersion #"2022-01-01-preview";
            location   = "[parameters('workspace-location')]";
            name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat('Parser-', last(split(variables('_parserId$global:parserCounter'),'/'))))]";
            dependsOn  =  @(
                "[variables('_parserId$global:parserCounter')]"
            );
            properties = [PSCustomObject]@{
                parentId  = "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', parameters('workspace'), variables('parserName$global:parserCounter'))]"
                contentId = "[variables('_parserContentId$global:parserCounter')]";
                kind      = "Parser";
                version   = "[variables('parserVersion$global:parserCounter')]";
                source    = [PSCustomObject]@{
                    kind     = "Solution";
                    name     = $contentToImport.Name;
                    sourceId = "[variables('_solutionId')]"
                };
                author    = $authorDetails;
                support   = $baseMetadata.support
            }
        }

        $global:baseMainTemplate.resources += $parserMetadata
}

function generateParserContent($file, $contentToImport, $contentResourceDetails)
{
    $solutionName = $contentToImport.name
    if ($global:parserCounter -eq 1 -and $null -eq $global:baseMainTemplate.variables.'workspace-dependency' -and !$contentToImport.TemplateSpec) {
        # Add parser dependency variable once to ensure validation passes.
        $global:baseMainTemplate.variables | Add-Member -MemberType NoteProperty -Name "workspace-dependency" -Value "[concat('Microsoft.OperationalInsights/workspaces/', parameters('workspace'))]"
    }

    $fileName = Split-Path $file -leafbase;
    function getFileNameFromPath ([string]$inputFilePath) {
        # Split out path
        $indexOfSlashInFile = $inputFilePath.IndexOf("/")
        if ($indexOfSlashInFile -gt 0)
        {
            $output = $inputFilePath.Split("/")
            Write-Host "input file path is $inputFilePath output $output"
            $output = $output[$output.Length - 1]
            Write-Host "updated output $output"
            # Split out file type
            $output = $output.Split(".")[0]
            return $output
        }
        else {
            # GET NAME OF THE FILE WITHOUT ANY EXTENSION
            $output = $inputFilePath.Split(".")[0]
            return $output
        }
    }
    $content = ''
    $yaml = $null
    $isyaml = $false
    $rawData = $rawData.Split("`n")
    foreach ($line in $rawData) {
        # Remove comment lines before condensing query
        if (!$line.StartsWith("//")) {
            $content = $content + "`n" + $line
        }
    }
    if($file -match "(\.yaml)$")
    {        
        try {
            $yaml = ConvertFrom-YAML $content
            $isyaml = $true
        }
        catch {
        Write-Host "Failed to deserialize while converting the Saved Search Function from Yaml $file" -ForegroundColor Red
        break;
        }
    }
    
    $displayDetails = getParserDetails $global:solutionId $yaml $isyaml
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "parserName$global:parserCounter" -NotePropertyValue "$($displayDetails.name)"
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_parserName$global:parserCounter" -NotePropertyValue "[concat(parameters('workspace'),'/',variables('parserName$global:parserCounter'))]"
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "parserId$global:parserCounter" -NotePropertyValue "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', parameters('workspace'), variables('parserName$global:parserCounter'))]"
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_parserId$global:parserCounter" -NotePropertyValue "[variables('parserId$global:parserCounter')]"

    if ($contentResourceDetails.apiVersion -eq '3.0.0')
    {
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "parserTemplateSpecName$global:parserCounter" -NotePropertyValue "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(concat(parameters('workspace'),'-pr-',uniquestring(variables('_parserContentId$global:parserCounter'))),variables('parserVersion$global:parserCounter')))]"
    }
    else 
    {
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "parserTemplateSpecName$global:parserCounter" -NotePropertyValue "[concat(parameters('workspace'),'-pr-',uniquestring(variables('_parserContentId$global:parserCounter')))]"
    }

    # Use File Name as Parser Name
    $functionAlias = ($null -ne $yaml -and $yaml.Count -gt 0) ? $yaml.FunctionName : "$($displayDetails.functionAlias)"
    $global:parserVersion = ($null -ne $yaml -and $yaml.Count -gt 0) ? ($null -eq $yaml.Function.Version ? "1.0.0" : $yaml.Function.Version) : "1.0.0"
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "parserVersion$global:parserCounter" -NotePropertyValue $global:parserVersion
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "parserContentId$global:parserCounter" -NotePropertyValue "$($functionAlias)-Parser"
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_parserContentId$global:parserCounter" -NotePropertyValue "[variables('parserContentId$global:parserCounter')]"
    $global:DependencyCriteria += [PSCustomObject]@{
        kind      = "Parser";
        contentId = "[variables('_parserContentId$global:parserCounter')]";
        version   = "[variables('parserVersion$global:parserCounter')]";
    };

    if($contentToImport.TemplateSpec) {
        # Adding the Parser respective TemplateSpec Resources and Active Parser and Metadata Resource
        addTemplateSpecParserResource $content $yaml $isyaml $contentResourceDetails
    }
    else {
        if ($global:parserCounter -eq 1 -and $(queryResourceExists) -and !$contentToImport.TemplateSpec) {
            $baseParserResource = [PSCustomObject] @{
                type       = "Microsoft.OperationalInsights/workspaces";
                apiVersion = $contentResourceDetails.parserOperationalInsightsWorkspacesApiVersion; #"2020-08-01";
                name       = "[parameters('workspace')]";
                location   = "[parameters('workspace-location')]";
                resources  = @(

                )
            }
            $global:baseMainTemplate.resources += $baseParserResource
        }
        $parserObj = [PSCustomObject] @{
            type       = "savedSearches";
            apiVersion = $contentResourceDetails.savedSearchesApiVersion; #"2020-08-01";
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
        $queryLocation = $(getQueryResourceLocation)
        if ($null -eq $queryLocation)
        {
            Write-Host  "For Parser, getQueryResourceLocation function returned null for $file which is not valid"
            return;
        }
        else
        {
            $global:baseMainTemplate.resources[$queryLocation].resources += $parserObj
        }
    }
    
    $global:parserCounter += 1
}
