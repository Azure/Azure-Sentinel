
[hashtable]$templateKindByCounter = @{
    1 = "ConnectorDefinition"; 
    2 = "Connections";
}

[hashtable]$templateContentTypeByCounter = @{
    1 = "DataConnector"; 
    2 = "ResourcesDataConnector";
}

#build the connection template parameters, according to the connector definition instructions
function Get-ConnectionsTemplateParameters($activeResource, $ccpItem) {
    # this is for data connector definition only
    $title = $ccpItem.title;
    $paramTestForDefinition = [PSCustomObject]@{
        defaultValue = $title;
        type         = "securestring";
        minLength    = 1;
    }

    $workspaceParameter = [PSCustomObject]@{
        defaultValue = "[parameters('workspace')]";
        type         = "securestring";
    }

    $dcrConfigParameter = [PSCustomObject]@{
        defaultValue = [PSCustomObject]@{
            dataCollectionEndpoint        = "data collection Endpoint";
            dataCollectionRuleImmutableId = "data collection rule immutableId";
        };
        type         = "object";
    }

    $templateParameter = [PSCustomObject]@{
        connectorDefinitionName = $paramTestForDefinition;
        workspace               = $workspaceParameter;
        dcrConfig               = $dcrConfigParameter;
    }

    $connectorDefinitionObject = $activeResource | where-object -Property "type" -eq 'Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions'
    foreach ($instructionSteps in $connectorDefinitionObject.properties.connectorUiConfig.instructionSteps) {
        New-ParametersForConnectorInstuctions $instructionSteps.instructions   
    }

    return $templateParameter;
}

function New-ParametersForConnectorInstuctions($instructions) {
    foreach ($instruction in $instructions) {
        if ($instruction.type -eq "Textbox") {
            $newParameter = [PSCustomObject]@{
                defaultValue = $instruction.parameters.name;
                type         = "securestring";
                minLength    = 1;
            }

            $setDefaultValueAndRemoveMinLength = $false
            $hasRequiredValidationProperty = [bool]($instruction.parameters.PSobject.Properties.name -match "validations")
            if ($hasRequiredValidationProperty) {
                $hasRequiredProperty = [bool]($instruction.parameters.validations.PSobject.Properties.name -match "required")
                if ($hasRequiredProperty) {
                    $isRequiredTrue = [bool]($instruction.parameters.validations.required) 
                    if (!$isRequiredTrue) {
                        $setDefaultValueAndRemoveMinLength = $true
                    }
                }
            }

            if ($setDefaultValueAndRemoveMinLength) {
                $newParameter.defaultValue = ""
                $newParameter.PSObject.Properties.Remove('minLength')
            }

            $templateParameter | Add-Member -MemberType NoteProperty -Name $instruction.parameters.name -Value $newParameter
        }
        elseif ($instruction.type -eq "OAuthForm") {
            $newParameter = [PSCustomObject]@{
                defaultValue = "-NA-";
                type         = "securestring";
                minLength    = 1;
            }

            if (![bool]($templateParameter.PSobject.Properties.name -match "ClientId")) {
                $templateParameter | Add-Member -MemberType NoteProperty -Name "ClientId" -Value $newParameter
            }
            
            if (![bool]($templateParameter.PSobject.Properties.name -match "ClientSecret")) {
                $templateParameter | Add-Member -MemberType NoteProperty -Name "ClientSecret" -Value $newParameter
            }

            if (![bool]($templateParameter.PSobject.Properties.name -match "AuthorizationCode")) {
                $templateParameter | Add-Member -MemberType NoteProperty -Name "AuthorizationCode" -Value $newParameter
            }
        }
        elseif ($instruction.type -eq "ContextPane") {
            New-ParametersForConnectorInstuctions $instruction.parameters.instructionSteps.instructions    
        }
        elseif ($instruction.type -eq "Dropdown") {
            $newParameter = [PSCustomObject]@{
                defaultValue = $instruction.parameters.name;
                type         = "array";
                minLength    = 1;
            }

            $templateParameter | Add-Member -MemberType NoteProperty -Name $instruction.parameters.name -Value $newParameter
        }
        else {
            $instructionType = $instruction.type;
            Write-Host "Info: Specified Instruction type '$instructionType' is not from the instruction type list like Textbox, OAuthForm and ContextPane!"
        }
    }
}

function Get-MetaDataBaseResource($resourceName, $parentId, $contentId, $kind, $contentVersion, $dataFileMetadata, $solutionFileMetadata) {
    $author = $dataFileMetadata.Author.Split(" - ");
    $authorDetails = [PSCustomObject]@{
        name = $author[0];
    };
    if ($null -ne $author[1]) {
        $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
    }

    $properties = [PSCustomObject]@{
        parentId  = $parentId;
        contentId = $contentId;
        kind      = $kind;
        version   = $contentVersion;
        source    = [PSCustomObject]@{
            sourceId = "[variables('_solutionId')]";
            name     = "[variables('_solutionName')]";
            kind     = "Solution";
        };
        author    = $authorDetails;
        support   = $solutionFileMetadata.support;
    }

    return [PSCustomObject]@{
        name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',$resourceName)]";
        apiVersion = "2022-01-01-preview"
        type       = "Microsoft.OperationalInsights/workspaces/providers/metadata"
        properties = $properties;
    }
}

function Get-MetaDataResource($TemplateCounter, $dataFileMetadata, $solutionFileMetadata) {
    if ($templateContentTypeByCounter[$TemplateCounter] -eq "DataConnector") {
        $parentIdResourceName = "'Microsoft.SecurityInsights/dataConnectorDefinitions'"
    }
    else {
        $parentIdResourceName = "'Microsoft.SecurityInsights/dataConnectors'"
    }

    $parentId = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), $parentIdResourceName, variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)'))]"
    $metaDataResourceName = "concat('DataConnector-', variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)'))"
    $metaDataContentId = "[variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')]"
    $metaDatsContentVersion = "[variables('dataConnectorCCPVersion')]"
    $metaDataResource = Get-MetaDataBaseResource $metaDataResourceName $parentId $metaDataContentId $templateContentTypeByCounter[$TemplateCounter] $metaDatsContentVersion $dataFileMetadata $solutionFileMetadata
    
    if ($templateContentTypeByCounter[$TemplateCounter] -eq "DataConnector") {
        $dependencies = [PSCustomObject]@{
            "criteria" = @(
                [PSCustomObject]@{
                    "version"   = "[variables('dataConnectorCCPVersion')]";
                    "contentId" = "[variables('_dataConnectorContentId$($templateKindByCounter[2])$($global:connectorCounter)')]";
                    "kind"      = "ResourcesDataConnector"
                }
            )
        }

        $metaDataResource.properties | Add-Member -NotePropertyName "dependencies" -NotePropertyValue $dependencies
    }

    return  $metaDataResource;
}

function Get-ContentTemplateResource($contentResourceDetails, $TemplateCounter, $ccpItem) {
    $contentVersion = "variables('dataConnectorCCPVersion')";
    $contentTemplateName = "variables('dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')";
    $contentId = "variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')";
    $resoureKind = $templateContentTypeByCounter[$TemplateCounter];
    if ($resoureKind -eq "DataConnector") {
        $resoureKindTag = "dc";
    }
    else {
        $resoureKindTag = "rdc";
    }

    $title = $ccpItem.title;
    $displayName = $title;

    return [PSCustomObject]@{
        type       = "Microsoft.OperationalInsights/workspaces/providers/contentTemplates";
        apiVersion = $contentResourceDetails.metadataApiVersion; # "2023-04-01-preview";
        name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', $contentTemplateName, $contentVersion)]";
        location   = "[parameters('workspace-location')]";
        dependsOn  = @(
            "$($contentResourceDetails.dependsOn)"
        );
        properties = [PSCustomObject]@{
            contentId            = "[$contentId]";
            displayName          = $displayName;
            contentKind          = $templateContentTypeByCounter[$TemplateCounter];
            mainTemplate         = [PSCustomObject]@{
                '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                contentVersion = "[$contentVersion]";
                parameters     = [PSCustomObject]@{};
                variables      = [PSCustomObject]@{};
                resources      = @(
                )
            };
            packageKind          = "Solution";
            packageVersion       = "[variables('_solutionVersion')]";
            packageName          = "[variables('_solutionName')]";
            contentProductId     = "[concat(take(variables('_solutionId'), 50),'-','$resoureKindTag','-', uniqueString(concat(variables('_solutionId'),'-','$resoureKind','-',$contentId,'-', $contentVersion)))]";
            packageId            = "[variables('_solutionId')]";
            contentSchemaVersion = $contentResourceDetails.contentSchemaVersion;
            version              = "[variables('dataConnectorCCPVersion')]";
        }
    }
}

function Get-ArmResource($name, $type, $kind, $properties) {
    [hashtable]$apiVersion = @{
        "Microsoft.SecurityInsights/dataConnectors"           = "2023-02-01-preview";
        "Microsoft.SecurityInsights/dataConnectorDefinitions" = "2022-09-01-preview";
        "Microsoft.OperationalInsights/workspaces/tables"     = "2022-10-01";
        "Microsoft.Insights/dataCollectionRules"              = "2022-06-01";
    }

    return [PSCustomObject]@{
        name       = $name;
        apiVersion = $apiVersion[$type]
        type       = $type;
        location   = "[parameters('workspace-location')]";
        kind       = $kind;
        properties = $properties;
    }
}

function addNewParameter($templateResourceObj, $parameterName, $isSecret = $false, $minLength = 1) {
    $hasParameter = [bool]($templateResourceObj.parameters.PSobject.Properties.name -match "$parameterName")
    if (!$hasParameter) {
        $templateResourceObj.parameters | Add-Member -NotePropertyName "$parameterName" -NotePropertyValue ([PSCustomObject] @{
                defaultValue = $isSecret ? "-NA-" : "Enter $parameterName value";
                type         = "securestring";
                minLength    = $minLength;
            })
    }

    return $templateResourceObj;
}

function addWorkspaceParameter($templateResourceObj, $parameterName) {
    $hasParameter = [bool]($templateResourceObj.parameters.PSobject.Properties.name -match "$parameterName")
    if (!$hasParameter) {
        $templateResourceObj.parameters | Add-Member -NotePropertyName "$parameterName" -NotePropertyValue ([PSCustomObject] @{
            defaultValue = "[parameters('workspace')]";
            type         = "securestring";
        })
    }

    return $templateResourceObj;
}

function addGuidValueParameter($templateResourceObj) {
    $hasParameter = [bool]($templateResourceObj.parameters.PSobject.Properties.name -match "guidValue")
    if (!$hasParameter) {
        $templateResourceObj.parameters | Add-Member -NotePropertyName "guidValue" -NotePropertyValue ([PSCustomObject] @{
            defaultValue = "[[newGuid()]";
            type         = "securestring";
        })
    }

    return $templateResourceObj;
}

function Add-NewObjectParameter {
    param (
        [Parameter(Mandatory = $true)] [PSCustomObject] $TemplateResourceObj,
        [Parameter(Mandatory = $true)] [string] $ParameterName
    )

    # Check if the parameter already exists
    $hasParameter = $TemplateResourceObj.parameters.PSObject.Properties.Name -contains $ParameterName

    if (-not $hasParameter) {
        # Add the new parameter with the desired structure
        $TemplateResourceObj.parameters | Add-Member -NotePropertyName $ParameterName -NotePropertyValue ([PSCustomObject] @{
                type         = "object"
                defaultValue = [PSCustomObject] @{}
            })
    }

    return $TemplateResourceObj
}

function Convert-ToParameterFormat($propValue) {

    $regex = [regex]'\{{([a-zA-Z0-9_]+)\}}'
    $matchesPattern = $regex.Matches($propValue)
 
    if ($matchesPattern.Count -eq 0) {
        # No placeholders, return as-is
        return $propValue
    }
 
    # If the value is exactly one match and no literal text
    if ($matchesPattern.Count -eq 1 -and $propValue -eq $matchesPattern[0].Value) {
        $paramName = $matchesPattern[0].Groups[1].Value

        $templateContentConnections.properties.mainTemplate = addNewParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName "$paramName" -isSecret $true

        return "[[parameters('$paramName')]"
    }

    $result = "[[concat("
    $lastIndex = 0
 
    foreach ($matchValue in $matchesPattern) {
        # Add the part before the match as a string (if not empty)
        if ($matchValue.Index -gt $lastIndex) {
            $literalPart = $propValue.Substring($lastIndex, $matchValue.Index - $lastIndex)
            $escapedLiteral = $literalPart -replace "'", "''"  # Escape single quotes
            $result += "'$escapedLiteral',"
        }
 
        # Add the parameter reference
        $paramName = $matchValue.Groups[1].Value
 
        $templateContentConnections.properties.mainTemplate = addNewParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName "$paramName" -isSecret $true
 
        $result += "parameters('$paramName'),"
        $lastIndex = $matchValue.Index + $matchValue.Length
    }
 
    # Add the remaining part after the last match
    if ($lastIndex -lt $propValue.Length) {
        $remaining = $propValue.Substring($lastIndex)
        $escapedRemaining = $remaining -replace "'", "''"
        $result += "'$escapedRemaining',"
    }
 
    # Remove trailing comma and close concat
    $result = $result.TrimEnd(',') + ")]"
    return $result
}

# THIS IS THE STARTUP FUNCTION FOR CCP RESOURCE CREATOR
function createCCPConnectorResources($contentResourceDetails, $dataFileMetadata, $solutionFileMetadata, $dcFolderName, $ccpDict, $solutionBasePath, $solutionName, $ccpTables, $ccpTablesCounter) {
    Write-Host "Inside of CCP Connector Code!"
    $solutionId = $solutionFileMetadata.publisherId + "." + $solutionFileMetadata.offerId
    $placeHolderPatternMatches = '\{{[a-zA-Z0-9]+\}}'

    if (!$global:baseMainTemplate.variables.workspaceResourceId) {
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
    }

    if (!$global:baseMainTemplate.variables._solutionName) {
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionName" -NotePropertyValue $dataFileMetadata.Name
    }

    if (!$global:baseMainTemplate.variables._solutionVersion) { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionVersion" -NotePropertyValue $dataFileMetadata.Version
    }

    if (!$global:baseMainTemplate.variables._solutionId) { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionId" -NotePropertyValue "$solutionId"
    }

    if (!$global:baseMainTemplate.variables.dataConnectorCCPVersion) {
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorCCPVersion" -NotePropertyValue "1.0.0"
    }

    try {
        foreach ($ccpItem in $ccpDict) {
            $activeResource = @()
            $tableCounter = 1;
            $templateName = $ccpItem.DCDefinitionId;

            For ($TemplateCounter = 1; $TemplateCounter -lt 3; $TemplateCounter++) {
                if (!$global:baseMainTemplate.variables."_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)") {
                    if ($TemplateCounter -eq 1) {
                        $dataConnectorContentIdName = $templateName;
                    }
                    else {
                        $dataConnectorContentIdName = $templateName + $templateKindByCounter[$TemplateCounter];
                    }
                    
                    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)" -NotePropertyValue "$dataConnectorContentIdName"
                }
            
                if (!$global:baseMainTemplate.variables."dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)") {
                    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)" -NotePropertyValue "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')))]"
                }
                
                $templateContent = Get-ContentTemplateResource $contentResourceDetails $TemplateCounter $ccpItem; 

                if ($TemplateCounter -eq 1) {
                    #========start:dc definition resource===========
                    $dcDefinitionFilteredPath = $ccpItem.DCDefinitionFilePath.Replace($solutionName + "/", "").Replace($dcFolderName + "/", "")
                    $ccpDataDefinitionFilePath = $solutionBasePath + "/" + $solutionName + "/" + $dcFolderName + "/" + $dcDefinitionFilteredPath
                    $ccpDataDefinitionFilePath = $ccpDataDefinitionFilePath.Replace("//", "/")
                    Write-Host "CCP DataDefinition File Path : $ccpDataDefinitionFilePath"
                    
                    #$fileContent = Get-Content -Raw "$ccpDataDefinitionFilePath" | Out-String | ConvertFrom-Json
                    $fileContent = ReadFileContent -filePath $ccpDataDefinitionFilePath
                    if ($null -eq $fileContent) {
                        exit 1;
                    }

                    if ($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectorDefinitions") {
                        Write-Host "Processing for CCP DataDefinition file path: $dcDefinitionFilteredPath"
                        $resourceName = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$($templateKindByCounter[1])$($global:connectorCounter)'))]"

                        $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
                        $armResource.type = "Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions"

                        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource -propertyName 'location' -isInnerObject $false -innerObjectName $null -kindType $null -isSecret $true -isRequired $false -fileType 'dataConnectorDefinitions' -minLength 1

                        $templateContentConnectorDefinition = $templateContent;
                        $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource

                        $activeResource += $armResource
                        $activeResource += Get-MetaDataResource $TemplateCounter $dataFileMetadata $solutionFileMetadata
                    }

                    #========end:dc definition resource===========
                }
                
                $templateContent.properties.mainTemplate.resources += Get-MetaDataResource $TemplateCounter $dataFileMetadata $solutionFileMetadata
                
                if ($TemplateCounter -eq 2) {
                    $templateContent.properties.mainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)" -NotePropertyValue "[variables('_dataConnectorContentId$($templateKindByCounter[2])$($global:connectorCounter)')]"        
                    $templateContentConnections = $templateContent

                    $global:DependencyCriteria += [PSCustomObject]@{
                        kind      = "DataConnector";
                        contentId = "[variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')]";
                        version   = if ($dataFileMetadata.TemplateSpec) { "[variables('dataConnectorCCPVersion')]" }else { $dataFileMetadata.Version };
                    };
                }
                else {
                    $templateContentConnectorDefinition = $templateContent
                }
            }

            #========start:dc definition resource===========
            $ccpPollerFilePath = $ccpItem.DCPollerFilePath
            Write-Host "CCP Poller File Path : $ccpPollerFilePath"
            $ccpPollerFilePath = $ccpPollerFilePath.Replace("//", "/")

            $fileContent = ReadFileContent -filePath $ccpPollerFilePath
            if ($null -eq $fileContent) {
                exit 1;
            }

            function GetDataConnectorPollerResourceName ($dataConnectorName) {
                $splitNamesBySlash = $dataConnectorName -split '/'
                $concatenateParts = @()
                $outputString = ''
                $guidValue = "parameters('guidValue')"

                foreach ($currentName in $splitNamesBySlash) {
                    if ($currentName.Contains('{{')) {
                        $placeHolderFieldName = $currentName -replace '{{', '' -replace '}}', ''
                        $placeHolderMatched = [regex]::Matches($currentName, $placeHolderPatternMatches)
                        if ($placeHolderMatched.Length -eq $currentName.Length) {
                            if ($placeHolderFieldName -eq 'workspace') {
                                $concatenateParts += "parameters('innerWorkspace')"
                                $templateContentConnections.properties.mainTemplate = addWorkspaceParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName $($placeHolderFieldName) -isSecret $true
                            } else {
                                $concatenateParts += "parameters('$($placeHolderFieldName)')"
                                $templateContentConnections.properties.mainTemplate = addNewParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName $($placeHolderFieldName) -isSecret $true
                            }
                        } else {
                            $text = $currentName -replace $placeHolderMatched.Value, ''
                            $concatenateParts += "'/$($text)'"
                            $parameterNameValue = $placeHolderMatched.Value -replace '{{', '' -replace '}}', ''
                            $concatenateParts += "parameters('$($parameterNameValue)')"

                            $templateContentConnections.properties.mainTemplate = addNewParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName $($parameterNameValue) -isSecret $true
                        }
                    } else {
                        if ($currentName.Count -eq 1 -and $currentName -like '{{') {
                            $concatenateParts = "[concat(parameters('innerWorkspace'),'/Microsoft.SecurityInsights/', '$($currentName)', $guidValue)]"
                        } else {
                            if ($concatenateParts.Count -ge 1) {
                                # if we have multiple parts in name {{innerWorkspace}}/Microsoft.SecurityInsights/OktaDCV1_{{domainname}}
                                $concatenateParts += "'/$($currentName)'"
                            } else {
                                # if name is abcwork
                                $concatenateParts += "$($currentName)"
                            }
                        }
                    }
                }

                if ($concatenateParts.Count -gt 1 -and $concatenateParts -notmatch 'concat') {
                    $outputString = "[[concat($($concatenateParts -join ', '), $guidValue)]"
                } elseif ($concatenateParts.Count -eq 1 -and $concatenateParts[0] -match 'parameters') {
                    # if we just have parameters('abcwork')
                    $outputString = "[[concat(parameters('innerWorkspace'),'/Microsoft.SecurityInsights/', $($concatenateParts[0]), $guidValue)]"
                } else {
                    # if we just have 'abcwork'
                    $outputString = "[[concat(parameters('innerWorkspace'),'/Microsoft.SecurityInsights/', '$($concatenateParts[0])', $guidValue)]"
                }
            
                return $outputString
            }

            function CCPDataConnectorsResource($fileContent) {
                if ($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectors") {
                    # add parameter of guidValue if not present
                    $templateContentConnections.properties.mainTemplate = addGuidValueParameter -templateResourceObj $templateContentConnections.properties.mainTemplate

                    # add parameter of innerWorkspace if not present
                    $templateContentConnections.properties.mainTemplate = addWorkspaceParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName 'innerWorkspace' -isSecret $true

                    Write-Host "Processing for CCP Poller file path: $ccpPollerFilePath"
                    $resourceName = GetDataConnectorPollerResourceName -dataConnectorName $fileContent.name

                    $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
                    $armResource.type = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors"
                    $armResource.kind = $ccpItem.PollerKind;
    
                    # dataCollectionEndpoint : this is optional field for users to add.
                    $hasDataCollectionEndpoint = [bool](($armResource.properties.dcrConfig).PSobject.Properties.name -match "dataCollectionEndpoint")
                    if ($hasDataCollectionEndpoint) {
                        $dataCollectionEndpointProperty = $armResource.properties.dcrConfig.dataCollectionEndpoint
                        $placeHoldersMatched = $dataCollectionEndpointProperty | Select-String $placeHolderPatternMatches -AllMatches
    
                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $armResource.properties.dcrConfig.dataCollectionEndpoint = "[[parameters('dcrConfig').dataCollectionEndpoint]"
                        }
                    }
                    else {
                        # if dataCollectionEndpoint property not present then add it 
                        $armResource.properties.dcrConfig | Add-Member -MemberType NoteProperty -Name "dataCollectionEndpoint" -Value "[[parameters('dcrConfig').dataCollectionEndpoint]"
                    }
    
                    # dataCollectionRuleImmutableId
                    $hasDataCollectionRuleImmutableId = [bool](($armResource.properties.dcrConfig).PSobject.Properties.name -match "dataCollectionRuleImmutableId")
                    if ($hasDataCollectionRuleImmutableId) {
                        $dataCollectionRuleImmutableIdProperty = $armResource.properties.dcrConfig.dataCollectionRuleImmutableId
                        $placeHoldersMatched = $dataCollectionRuleImmutableIdProperty | Select-String $placeHolderPatternMatches -AllMatches
    
                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $armResource.properties.dcrConfig.dataCollectionRuleImmutableId = "[[parameters('dcrConfig').dataCollectionRuleImmutableId]"
                        }
                    }
                    else {
                        # if dataCollectionRuleImmutableId property not present then add it 
                        $armResource.properties.dcrConfig | Add-Member -MemberType NoteProperty -Name "dataCollectionRuleImmutableId" -Value "[[parameters('dcrConfig').dataCollectionRuleImmutableId]"
                    }
                    
                    $fileType = 'data Connector poller'
                    if ($armResource.kind.ToLower() -eq 'gcp')
                    {
                        CreateGCPResourceProperties -armResource $armResource -templateContentConnections $templateContentConnections -fileType $fileType
                    }
                    elseif ($armResource.kind.ToLower() -eq 'restapipoller')
                    {
                        CreateRestApiPollerResourceProperties -armResource $armResource -templateContentConnections $templateContentConnections -fileType $fileType
                    }
                    elseif ($armResource.kind.ToLower() -eq 'push' ) {

                        $templateContentConnections.properties.mainTemplate = Add-NewObjectParameter `
                            -TemplateResourceObj $templateContentConnections.properties.mainTemplate `
                            -ParameterName 'auth'

                        # Add properties to the 'defaultValue' object within 'auth'
                        if ($templateContentConnections.properties.mainTemplate.parameters.auth -is [PSCustomObject]) {
                            $templateContentConnections.properties.mainTemplate.parameters.auth.defaultValue | Add-Member -MemberType NoteProperty -Name "appId" -Value "[[parameters('auth').appId]]"
                            $templateContentConnections.properties.mainTemplate.parameters.auth.defaultValue | Add-Member -MemberType NoteProperty -Name "servicePrincipalId" -Value "[[parameters('auth').servicePrincipalId]]"
                        }
                        else {
                            Write-Error "Failed to create or update 'auth' parameter."
                        }

                        $hasAppId = [bool](($armResource.properties.auth).PSobject.Properties.name -match "appId")
                        if ($hasAppId) {
                            $appIdProperty = $armResource.properties.auth.appId
                            $placeHoldersMatched = $appIdProperty | Select-String $placeHolderPatternMatches -AllMatches
    
                            if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                                $armResource.properties.auth.appId = "[[parameters('auth').appId]"
                            }
                        }
                        else {
                            # if dataCollectionEndpoint property not present then add it 
                            $armResource.properties.auth | Add-Member -MemberType NoteProperty -Name "appId" -Value "[[parameters('auth').appId]"
                        }

                        $hasServicePrincipalId = [bool](($armResource.properties.auth).PSobject.Properties.name -match "servicePrincipalId")
                        if ($hasServicePrincipalId) {
                            $servicePrincipalIdProperty = $armResource.properties.auth.servicePrincipalId
                            $placeHoldersMatched = $servicePrincipalIdProperty | Select-String $placeHolderPatternMatches -AllMatches
    
                            if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                                $armResource.properties.auth.servicePrincipalId = "[[parameters('auth').servicePrincipalId]"
                            }
                        }
                        else {
                            # if dataCollectionEndpoint property not present then add it 
                            $armResource.properties.auth | Add-Member -MemberType NoteProperty -Name "servicePrincipalId" -Value "[[parameters('auth').servicePrincipalId]"
                        }
                    }
                    elseif ($armResource.kind.ToLower() -eq 'amazonwebservicess3')
                    {
                        CreateAwsResourceProperties -armResource $armResource -templateContentConnections $templateContentConnections -fileType $fileType
                    }
                    else 
                    {
                        Write-Host "Error: Data Connector Poller file should have 'kind' attribute with value either 'RestApiPoller', 'GCP', 'AmazonWebServicesS3' or 'Push'." -BackgroundColor Red
                        exit 1;
                    }

                    $templateContentConnections.properties.mainTemplate.resources += $armResource
                }
            }

            if ($fileContent -is [System.Object[]]) {
                foreach ($content in $fileContent) {
                    CCPDataConnectorsResource -fileContent $content;
                }
            }
            else {
                CCPDataConnectorsResource -fileContent $fileContent;
            }
            #========end:dc definition resource===========
            #========start: dcr resource===========
            $ccpDCRFilePath = $ccpItem.DCRFilePath
            $ccpDCRFilePath = $ccpDCRFilePath.Replace("//", "/")
            Write-Host "CCP DCR File Path : $ccpDCRFilePath"

            #$fileContent = Get-Content -Raw "$ccpDCRFilePath" | Out-String | ConvertFrom-Json
            
            $fileContent = ReadFileContent -filePath $ccpDCRFilePath
            if ($null -eq $fileContent) {
                exit 1;
            }

            if ($fileContent.type -eq "Microsoft.Insights/dataCollectionRules") {
                Write-Host "Processing for CCP DCR file path: $ccpDCRFilePath"
                if (-not $fileContent.properties.destinations.PSObject.Properties.Name -contains "logAnalytics") {
                    # if logAnalytics array is not specified
                    $logAnalyticsObject = @{
                        "name" = "clv2ws1"
                        "workspaceResourceId" = "[variables('workspaceResourceId')]"
                    }
                    $fileContent.properties.destinations | Add-Member -MemberType NoteProperty -Name "logAnalytics" -Value $logAnalyticsObject
                } else {
                    if (-not $fileContent.properties.destinations.logAnalytics[0].PSObject.Properties.Name -contains "name") {
                        $fileContent.properties.destinations.logAnalytics[0] | Add-Member -MemberType NoteProperty -Name "name" -Value "clv2ws1"
                    }

                    if ($fileContent.properties.destinations.logAnalytics[0].PSObject.Properties.Name -contains "workspaceResourceId") {
                        $fileContent.properties.destinations.logAnalytics[0].workspaceResourceId = "[variables('workspaceResourceId')]"
                    } else {
                        $fileContent.properties.destinations.logAnalytics[0] | Add-Member -MemberType NoteProperty -Name "workspaceResourceId" -Value "[variables('workspaceResourceId')]"
                    }
                }

                $dcrPlaceHolderMatched = $fileContent.name | Select-String $placeHolderPatternMatches -AllMatches
                if ($dcrPlaceHolderMatched.Matches.Value.Count -gt 0) {
                    $startIndexOfOpenBraces = $fileContent.name.indexOf('{{')
                    $nameWithoutPlaceHolder = $fileContent.name.substring(0, $startIndexOfOpenBraces)
                    $fileContent.name = "[concat('" + $nameWithoutPlaceHolder + "', parameters('workspace'))]"
                }
                $armResource = Get-ArmResource $fileContent.name $fileContent.type $fileContent.kind $fileContent.properties

                # location
                ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource -propertyName 'location' -isInnerObject $false -innerObjectName $null -kindType $null -isSecret $true -isRequired $false -fileType 'dataCollectionRules' -minLength 1

                # dataCollectionEndpointId
                $hasDataCollectionEndpointIdProperty = [bool](($armResource.properties).PSobject.Properties.name -match "dataCollectionEndpointId")
                if ($hasDataCollectionEndpointIdProperty) {
                    $dataCollectionEndpointIdProperty = $armResource.properties.dataCollectionEndpointId
                    $placeHoldersMatched = $dataCollectionEndpointIdProperty | Select-String $placeHolderPatternMatches -AllMatches

                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        $dataCollectionEndpointIdPropertyName = $placeHolderName + $global:connectorCounter
                        $armResource.properties.dataCollectionEndpointId = "[variables('$($dataCollectionEndpointIdPropertyName)')]"
                        
                        if (!$global:baseMainTemplate.variables."$dataCollectionEndpointIdPropertyName") {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "$dataCollectionEndpointIdPropertyName" -NotePropertyValue "[concat('/subscriptions/',parameters('subscription'),'/resourceGroups/',parameters('resourceGroupName'),'/providers/Microsoft.Insights/dataCollectionEndpoints/',parameters('workspace'))]"
                        }
                    }
                }
                else {
                    # if dataCollectionEndpointId property not present then add it 
                    $armResource.properties | Add-Member -MemberType NoteProperty -Name "dataCollectionEndpointId" -Value "[variables('dataCollectionEndpointId')]"

                    if (!$global:baseMainTemplate.variables.dataCollectionEndpointId) {
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataCollectionEndpointId" -NotePropertyValue "[concat('/subscriptions/',parameters('subscription'),'/resourceGroups/',parameters('resourceGroupName'),'/providers/Microsoft.Insights/dataCollectionEndpoints/',parameters('workspace'))]"
                    }
                }

                if (!$global:baseMainTemplate.parameters.resourceGroupName) {
                    $resourceGroupNameParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[resourceGroup().name]"; metadata = [PSCustomObject] @{ description = "resource group name where Microsoft Sentinel is setup" }; }
                    $global:baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name "resourceGroupName" -Value $resourceGroupNameParameter
                }

                if (!$global:baseMainTemplate.parameters.subscription) {
                    $subscriptionParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[last(split(subscription().id, '/'))]"; metadata = [PSCustomObject] @{ description = "subscription id where Microsoft Sentinel is setup" }; }
                    $global:baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name "subscription" -Value $subscriptionParameter
                }

                # workspaceResourceId
                $hasWorkspaceResourceIdProperty = [bool](($armResource.properties.destinations.logAnalytics[0]).PSobject.Properties.name -match "workspaceResourceId")
                if ($hasWorkspaceResourceIdProperty) {
                    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.destinations.logAnalytics[0] -propertyName 'workspaceResourceId' -isInnerObject $true -innerObjectName $logAnalytics -kindType $null -isSecret $true -isRequired $false -fileType 'dataCollectionRules' -minLength 1
                }
                else {
                    # if workspaceResourceId property not present then add it 
                    $armResource.properties.destinations.logAnalytics | Add-Member -MemberType NoteProperty -Name "workspaceResourceId" -Value "[[parameters('workspaceResourceId')]"

                    $templateContentConnections.properties.mainTemplate = addNewParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName 'workspaceResourceId' -isSecret $true
                }

                $armResource = $(removePropertiesRecursively $armResource $false)
                $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
            }
            #========end: dcr resource===========
            #========start: tables resource===========
            $ccpTablesFilePath = $ccpItem.TableFilePath
            Write-Host "CCP Table File Path : $ccpTablesFilePath"

            if ($null -ne $ccpTablesFilePath -and $ccpTablesFilePath -ne '') {
                $fileContent = ReadFileContent -filePath $ccpTablesFilePath
                if ($null -eq $fileContent) {
                    exit 1;
                }
                
                foreach ($tableContent in $fileContent) {
                    if($tableContent.type -eq "Microsoft.OperationalInsights/workspaces/tables") {
                        $resourceName = $tableContent.name
                        $armResource = Get-ArmResource $resourceName $tableContent.type $tableContent.kind $tableContent.properties
    
                        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource -propertyName 'location' -isInnerObject $false -innerObjectName $null -kindType $null -isSecret $true -isRequired $false -fileType 'tables' -minLength 1
    
                        $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
                        $tableCounter ++;
                    }
                }
            }

            if ($null -ne $ccpTables -and $ccpTables.count -gt 0 -and $ccpTablesCounter -eq 1) {
                # add additional tables if any and run this code only once

                foreach ($tableFilePath in $ccpTables) {
                    #$fileContent = Get-Content -Raw "$tableFilePath" | Out-String | ConvertFrom-Json
                    $fileContent = ReadFileContent -filePath $tableFilePath
                    if ($null -eq $fileContent) {
                        exit 1;
                    }

                    if ($fileContent.type -eq "Microsoft.OperationalInsights/workspaces/tables") {
                        foreach($fileContentData in $fileContent) {
                            $resourceName = $fileContentData.name

                            $hasTable = $templateContentConnectorDefinition.properties.mainTemplate.resources | Where-Object { $_.type -eq "Microsoft.OperationalInsights/workspaces/tables" -and $_.name -eq $resourceName }
                            if ($hasTable) {
                                continue
                            }

                            $armResource = Get-ArmResource $resourceName $fileContentData.type $fileContentData.kind $fileContentData.properties

                            $hasLocationProperty = [bool]($armResource.PSobject.Properties.name -match "location")
                            if ($hasLocationProperty) {
                                $locationProperty = $armResource.location
                                $placeHoldersMatched = $locationProperty | Select-String $placeHolderPatternMatches -AllMatches

                                if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                                    $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                                    $templateContentConnections.properties.mainTemplate = addNewParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName $placeHolderName -isSecret $true
                                }
                            }

                        $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
                        }
                    }
                }

                $ccpTablesCounter += 1
            }
            #========end: tables resource===========

            ## Build the full package resources
            $paramItems = Get-ConnectionsTemplateParameters $activeResource $ccpItem;
            $finalParameters = $templateContentConnections.properties.mainTemplate.parameters;
            foreach ($paramItem in $paramItems.PSObject.Properties) {
                $existingParam = $finalParameters.PSObject.Properties[$paramItem.Name]
            
                if (-not $existingParam) {
                    # Parameter doesn't exist, add it
                    $finalParameters | Add-Member -MemberType NoteProperty -Name $paramItem.Name -Value $paramItem.Value
                } else {
                    # Parameter exists, compare and update if necessary
                    $paramValue = $paramItem.Value
                    $existingValue = $existingParam.Value
            
                    # Simple comparison, can be made deeper if properties are nested
                    $isDifferent = $false
            
                    foreach ($subProp in $paramValue.PSObject.Properties) {
                        if (-not $existingValue.PSObject.Properties[$subProp.Name] -or 
                            $existingValue.$($subProp.Name) -ne $subProp.Value) {
                            $isDifferent = $true
                            break
                        }
                    }
            
                    if ($isDifferent) {
                        # Update the whole parameter if it's different
                        $finalParameters.PSObject.Properties.Remove($paramItem.Name)
                        $finalParameters | Add-Member -MemberType NoteProperty -Name $paramItem.Name -Value $paramItem.Value
                    }
                }
            }

            $global:baseMainTemplate.resources += $templateContentConnectorDefinition

            $global:baseMainTemplate.resources += $activeResource
            $global:baseMainTemplate.resources += $templateContentConnections

            if ($global:connectorCounter -eq 1) {
                $baseDataConnectorStep = [PSCustomObject] @{
                    name       = "dataconnectors";
                    label      = "Data Connectors";
                    bladeTitle = "Data Connectors";
                    elements   = @();
                }
                
                $global:baseCreateUiDefinition.parameters.steps += $baseDataConnectorStep
            }

            $connectorDescriptionText = "This Solution installs the data connector for $solutionName. You can get $solutionName data in your Microsoft Sentinel workspace. After installing the solution, configure and enable this data connector by following guidance in Manage solution view."

            $baseDataConnectorTextElement = [PSCustomObject] @{
                name    = "dataconnectors$global:connectorCounter-text";
                type    = "Microsoft.Common.TextBlock";
                options = [PSCustomObject] @{
                    text = $connectorDescriptionText;
                }
            }

            $currentStepNum = $global:baseCreateUiDefinition.parameters.steps.Count - 1
            $global:baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $baseDataConnectorTextElement
            $connectDataSourcesLink = [PSCustomObject] @{
                name    = "dataconnectors-link$($global:connectorCounter)";
                type    = "Microsoft.Common.TextBlock";
                options = [PSCustomObject] @{
                    link = [PSCustomObject] @{
                        label = "Learn more about connecting data sources";
                        uri   = "https://docs.microsoft.com/azure/sentinel/connect-data-sources";
                    }
                }
            }
            $global:baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $connectDataSourcesLink

            $global:connectorCounter += 1
        }
    }
    catch {
        Write-Host "Error occurred in createCCPConnector file. Error Details $_" -ForegroundColor Red
    }
}


function ProcessPropertyPlaceholders($armResource, $templateContentConnections, 
    $isOnlyObjectCheck, # check if object is present or not example: auth: {'seviceaccountemail'...}. Here check if auth is provided.
    $propertyObject, # $armResource.properties
    $propertyName, # sqsUrls
    $isInnerObject, # false. This propertyName is not inside of any other object or array other than properties. if yes then specify that name below
    $innerObjectName, # $null
    $kindType,   # AWS. This can we GCP or AWS or RestApiPoller or $null for location
    $isSecret, # false
    $isRequired, # true, if true then it checks if the field is present or not else give error and exit
    $fileType, #either dataConnectorDefinitions or dataConnectors poller or dataCollectionRules or tables
    $minLength = 1, # default 1
    $isCreateArray = $false # create if true then create array else string
    )
{
    $placeHolderPatternMatches = '\{{[a-zA-Z0-9]+\}}'
    $hasProperty = [bool]($propertyObject.PSobject.Properties.name -match "$($propertyName)")

    if ($hasProperty)
    {
        if (!$isOnlyObjectCheck)
        {
            $placeHoldersMatched = $propertyObject.$($propertyName) | Select-String $placeHolderPatternMatches -AllMatches
            if ($null -ne $placeHoldersMatched -and $placeHoldersMatched.Matches.Value.Count -gt 0) 
            {
                $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                if ($isCreateArray) {
                    # create array
                    $propertyObject.$($propertyName) = @("[[parameters('$($placeHolderName)')]")
                } else {
                    # normal string field
                    $hasMoreText = $placeHoldersMatched.Line.Replace("{{$($placeHolderName)}}", '')
                    if ($hasMoreText.Length -gt 0) {
                        $formattedValue = Convert-ToParameterFormat -propValue $propertyObject.$($propertyName)
                        $propertyObject.$($propertyName) = $formattedValue
                    } else {
                        $propertyObject.$($propertyName) = "[[parameters('$($placeHolderName)')]"
                    }
                }

                # when multiple placeholders are present in the same field
                if ($placeHolderName.Count -gt 1) {
                    foreach ($placeHolder in $placeHolderName) {
                        $templateContentConnections.properties.mainTemplate = addNewParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName $placeHolder -isSecret $isSecret -minLength $minLength
                    }
                } else {
                    $templateContentConnections.properties.mainTemplate = addNewParameter -templateResourceObj $templateContentConnections.properties.mainTemplate -parameterName $placeHolderName -isSecret $isSecret -minLength $minLength
                }
            }
        }
    }
    else
    {
        if ($isRequired -and $isInnerObject)
        {
            Write-Host "Error: Attribute '$($propertyName)' missing from '$($innerObjectName)' Object from $($kindType) $($fileType) 'properties' section." -BackgroundColor Red
            exit 1;
        }
        elseif ($isRequired -and $isInnerObject -eq $false)
        {
            Write-Host "Error: Attribute '$($propertyName)' missing from '$($kindType)' $($fileType) 'properties' section." -BackgroundColor Red
            exit 1;
        }
        else {
            Write-Host "Warning: Attribute '$($propertyName)' missing from $($fileType)."
        }
    }
}

function CreateRestApiPollerResourceProperties($armResource, $templateContentConnections, $fileType) {
    $kindType = 'RestApiPoller'
    if($armResource.properties.auth.type.ToLower() -eq 'oauth2')
    {
        # clientid
        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'ClientId' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 4 -isCreateArray $false

        # client secret
        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'ClientSecret' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 4 -isCreateArray $false

        # authorization code
        if($armResource.properties.auth.grantType -eq 'authorization_code')
        {
            ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'AuthorizationCode' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $false -fileType $fileType -minLength 4 -isCreateArray $false
        }

        # AuthorizationEndpoint placeholder
        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'AuthorizationEndpoint' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $false -fileType $fileType -minLength 4 -isCreateArray $false

        # TokenEndpoint placeholder 
        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'TokenEndpoint' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $false -fileType $fileType -minLength 4 -isCreateArray $false
    }
    elseif ($armResource.properties.auth.type.ToLower() -eq 'basic') 
    {
        # username
        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'username' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 4 -isCreateArray $false

        # password 
        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'password' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 4 -isCreateArray $false
    }
    elseif ($armResource.properties.auth.type.ToLower() -eq 'apikey') 
    {
        # ApiKey 
        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'apikey' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 4 -isCreateArray $false
    }
    else 
    {
        Write-Host "Error: For kind RestApiPoller, Data Connector Poller file should have 'auth' object with 'type' attribute having value either 'Basic', 'OAuth2' or 'APIKey'." -BackgroundColor Red
        exit 1;
    }

    if ($armResource.properties.request.PSObject.Properties["apiEndPoint"] -and 
        $armResource.properties.request.apiEndPoint.contains("{{"))
    {
        $apiPointUrl = $armResource.properties.request.apiEndPoint
        $armResource.properties.request.apiEndPoint = Convert-ToParameterFormat -propValue $apiPointUrl
    }

    # headers placeholder
    $hasHeaders = [bool]($armResource.properties.request.PSobject.Properties.name -match "headers")
    if ($hasHeaders) 
    {
        foreach ($headerProps in $armResource.properties.request.headers.PsObject.Properties) 
        {
            $headerPropName = $headerProps.Name
            $headerPropValue = $headerProps.Value
            $armResource.properties.request.headers."$headerPropName" = Convert-ToParameterFormat -propValue $headerPropValue
        }
    }

    # paging placeholder
    Paging($armResource)

    # stepInfo placeholder
    $hasStepInfo = [bool]($armResource.properties.PSobject.Properties.name -match "stepInfo")
    $stepIds = @()
    if ($hasStepInfo) {
        $hasNextSteps = [bool]($armResource.properties.stepInfo.PSobject.Properties.name -match "nextSteps")
        if ($hasNextSteps) {
            foreach ($step in $armResource.properties.stepInfo.nextSteps) {
                $stepIds += $step.stepId
            }
        } else {
            Write-Host "Warning: 'stepInfo' object is missing 'nextSteps' array."
        }

        if ($stepIds.Count -gt 0) {
            $stepIdsString = $stepIds -join ', '
            Write-Host "List of identified 'stepId' in 'stepInfo' are: $stepIdsString"
        }
    }

    # stepCollectorConfigs placeholder
    $hasStepCollectorConfigs = [bool]($armResource.properties.PSobject.Properties.name -match "stepCollectorConfigs")
    if ($hasStepCollectorConfigs) {
        foreach ($stepId in $stepIds) {
            # Check if the stepId exists in the stepCollectorConfigs
            if ($armResource.properties.stepCollectorConfigs.PSObject.Properties.Match($stepId)) {
                $propObect = $armResource.properties.stepCollectorConfigs.$stepId.request
                ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $propObect -propertyName 'apiEndpoint' -isInnerObject $true -innerObjectName 'request' -kindType $kindType -isSecret $true -isRequired $false -fileType $fileType -minLength 4 -isCreateArray $false

                $hasStepCollectorConfigsHeaders = [bool]($propObect.PSobject.Properties.name -match "headers")
                if ($hasStepCollectorConfigsHeaders) 
                {
                    foreach ($headerProps in $propObect.headers.PsObject.Properties) 
                    {
                        $headerPropName = $headerProps.Name
                        $headerPropValue = $headerProps.Value
                        $propObect.headers."$headerPropName" = Convert-ToParameterFormat -propValue $headerPropValue
                    }
                }
            } else {
                Write-Host "Warning: Step ID $stepId not found in stepCollectorConfigs."
            }
        }
    }

    QueryParameters($armResource)

    $hasQueryParametersTemplate = [bool]($armResource.properties.request.PSobject.Properties.name -match "queryParametersTemplate")
    if ($hasQueryParametersTemplate) {
        $queryParametersTemplateValue = $armResource.properties.request.queryParametersTemplate
        $armResource.properties.request.queryParametersTemplate = Convert-ToParameterFormat -propValue $queryParametersTemplateValue
    }
}

function Paging($armResource) {
    $hasPaging = [bool]($armResource.properties.PSobject.Properties.name -match "paging")
    if ($hasPaging) 
    {
        $pagingProperties = $armResource.properties.paging.PSobject.Properties.name

        # Iterate over each property of the paging object
        foreach ($propertyName in $pagingProperties) {
            ProcessPropertyPlaceholders -armResource $armResource `
                -templateContentConnections $templateContentConnections `
                -isOnlyObjectCheck $false `
                -propertyObject $armResource.properties.paging `
                -propertyName $propertyName `
                -isInnerObject $true `
                -innerObjectName 'paging' `
                -kindType $kindType `
                -isSecret $true `
                -isRequired $false `
                -fileType $fileType `
                -minLength 4 `
                -isCreateArray $false
        }
    }
}

function QueryParameters($armResource) {
    $hasQueryParameters = [bool]($armResource.properties.request.PSobject.Properties.name -match "queryParameters")
    if ($hasQueryParameters) {
        $queryParameterProperties = $armResource.properties.request.queryParameters.PSobject.Properties.name
        $objectPattern = '{{.*?}}\[\d*\]' # check pattern {{queryType}}[0]
        foreach ($propertyName in $queryParameterProperties) {
            $propValue = $armResource.properties.request.queryParameters.$propertyName
            if ($propValue -match $objectPattern) {
                $armResource.properties.request.queryParameters.$propertyName = $propValue -replace '{{(.*?)}}(\[\d*\])', '[[parameters(''$1'')$2]'
            } else {
                ProcessPropertyPlaceholders -armResource $armResource `
                    -templateContentConnections $templateContentConnections `
                    -isOnlyObjectCheck $false `
                    -propertyObject $armResource.properties.request.queryParameters `
                    -propertyName $propertyName `
                    -isInnerObject $true `
                    -innerObjectName 'queryParameters' `
                    -kindType $kindType `
                    -isSecret $true `
                    -isRequired $false `
                    -fileType $fileType `
                    -minLength 4 `
                    -isCreateArray $false
            }
        }
    }
}

function CreateGCPResourceProperties($armResource, $templateContentConnections, $fileType) {
    $kindType = 'GCP'
    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties -propertyName 'connectorDefinitionName' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties -propertyName 'dataType' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'dcrConfig' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.dcrConfig -propertyName 'streamName' -isInnerObject $true -innerObjectName 'dcrConfig' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'auth' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'serviceAccountEmail' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 4 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'projectNumber' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 1 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'workloadIdentityProviderId' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -minLength 4 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'request' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.request -propertyName 'projectId' -isInnerObject $true -innerObjectName 'request' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 4 -isCreateArray $false

    # Request section subscriptionNames property
    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.request -propertyName 'subscriptionNames' -isInnerObject $true -innerObjectName 'request' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $true
}

$awsSolutions = @('VMware Carbon Black Cloud')

function CreateAwsResourceProperties($armResource, $templateContentConnections, $fileType) {
    $kindType = 'AmazonWebServicesS3'
    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'dataTypes' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties.dataTypes -propertyName 'logs' -isInnerObject $true -innerObjectName 'dataTypes' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.dataTypes.logs -propertyName 'state' -isInnerObject $true -innerObjectName 'logs' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'dcrConfig' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    if ($awsSolutions.Contains($solutionName)) {
        # Handle properties destinationTable and streamName in dc poller file for this solutions as a special case
        $armResource.properties.dcrConfig.streamName = "[[parameters('streamName')[0]]"
        $armResource.properties.destinationTable = "[[concat(parameters('streamName')[0],'_CL')]"
        $templateContentConnections.properties.mainTemplate.parameters | Add-Member -NotePropertyName "streamName" -NotePropertyValue ([PSCustomObject] @{ type = "array" })
    } else {
        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.dcrConfig -propertyName 'streamName' -isInnerObject $true -innerObjectName 'dcrConfig' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties -propertyName 'destinationTable' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false
    }

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties -propertyName 'roleArn' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties -propertyName 'sqsUrls' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $true

    $hasDataFormat = [bool]($armResource.properties.PSobject.Properties.name -match "dataFormat")
    if ($hasDataFormat) {
        $hasFormatProperty = [bool]($armResource.properties.dataFormat.PSobject.Properties.name.tolower() -match "format")
        if ($hasFormatProperty) {
            # check for csv format
            $hasCsvFormat = [bool]($armResource.properties.dataFormat.format -match "csv")
            if ($hasCsvFormat) {
                $hasCsvDelimiterProperty = [bool]($armResource.properties.dataFormat.PSobject.Properties.name.tolower() -match "csvdelimiter")
                if ($hasCsvDelimiterProperty) {
                    if ($armResource.properties.dataFormat.CsvDelimiter -eq " ") {
                        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "TemplateEmptySpaceString" -NotePropertyValue " "
                        $armResource.properties.dataFormat.CsvDelimiter = "[variables('TemplateEmptySpaceString')]"
                    }
                }
            } else {
                $armResource.properties.dataFormat.format = "json"
            }
        }
    }
}