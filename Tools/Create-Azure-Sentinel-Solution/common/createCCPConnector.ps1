
[hashtable]$templateKindByCounter = @{
    1 = "ConnectorDefinition"; 
    2 = "Connections";
}

[hashtable]$templateContentTypeByCounter = @{
    1 = "DataConnector"; 
    2 = "ResourcesDataConnector";
}

# read first folder and create the first template
# create 2 real active property on the side - outside
# create second template for second folder
# add solution metadata
# add variables
# Formats JSON in a nicer format than the built-in ConvertTo-Json does.
function Format-Json {
    <#
    .SYNOPSIS
        Prettifies JSON output.
    .DESCRIPTION
        Reformats a JSON string so the output looks better than what ConvertTo-Json outputs.
    .PARAMETER Json
        Required: [string] The JSON text to prettify.
    .PARAMETER Minify
        Optional: Returns the json string compressed.
    .PARAMETER Indentation
        Optional: The number of spaces (1..1024) to use for indentation. Defaults to 4.
    .PARAMETER AsArray
        Optional: If set, the output will be in the form of a string array, otherwise a single string is output.
    .EXAMPLE
        $json | ConvertTo-Json  | Format-Json -Indentation 2
    #>
    [CmdletBinding(DefaultParameterSetName = 'Prettify')]
    Param(
        [Parameter(Mandatory = $true, Position = 0, ValueFromPipeline = $true)]
        [string]$Json,

        [Parameter(ParameterSetName = 'Minify')]
        [switch]$Minify,

        [Parameter(ParameterSetName = 'Prettify')]
        [ValidateRange(1, 1024)]
        [int]$Indentation = 4,

        [Parameter(ParameterSetName = 'Prettify')]
        [switch]$AsArray
    )

    if ($PSCmdlet.ParameterSetName -eq 'Minify') {
        return ($Json | ConvertFrom-Json) | ConvertTo-Json -Depth 100 -Compress
    }

    # If the input JSON text has been created with ConvertTo-Json -Compress
    # then we first need to reconvert it without compression
    if ($Json -notmatch '\r?\n') {
        $Json = ($Json | ConvertFrom-Json) | ConvertTo-Json -Depth 100
    }

    $indent = 0
    $regexUnlessQuoted = '(?=([^"]*"[^"]*")*[^"]*$)'

    $result = $Json -split '\r?\n' |
        ForEach-Object {
            # If the line contains a ] or } character, 
            # we need to decrement the indentation level unless it is inside quotes.
            if ($_ -match "[}\]]$regexUnlessQuoted") {
                $indent = [Math]::Max($indent - $Indentation, 0)
            }

            # Replace all colon-space combinations by ": " unless it is inside quotes.
            $line = (' ' * $indent) + ($_.TrimStart() -replace ":\s+$regexUnlessQuoted", ': ')

            # If the line contains a [ or { character, 
            # we need to increment the indentation level unless it is inside quotes.
            if ($_ -match "[\{\[]$regexUnlessQuoted") {
                $indent += $Indentation
            }

            $line
        }

    if ($AsArray) { return $result }
    return $result -Join [Environment]::NewLine
}

#build the connection template parameters, according to the connector definition instructions
function Get-ConnectionsTemplateParameters($activeResource, $ccpItem){
    $title = $ccpItem.title;
    #$dataCollectionEndpoint = $ccpItem.PollerDataCollectionEndpoint;
    #$dataCollectionRuleImmutableId = $ccpItem.PollerDataCollectionRuleImmutableId;

    $paramTestForDefinition = [PSCustomObject]@{
        defaultValue = $title; #"connectorDefinitionName";
        type = "string";
        minLength = 1;
    }

    $workspaceParameter = [PSCustomObject]@{
        defaultValue = "[parameters('workspace')]";
        type = "string";
    }

    $dcrConfigParameter = [PSCustomObject]@{
        defaultValue = [PSCustomObject]@{
            dataCollectionEndpoint = "data collection Endpoint";
            dataCollectionRuleImmutableId = "data collection rule immutableId";
        };
        type = "object";
    }

    $templateParameter = [PSCustomObject]@{
        connectorDefinitionName = $paramTestForDefinition;
        workspace = $workspaceParameter;
        dcrConfig = $dcrConfigParameter;
    }

    $connectorDefinitionObject =  $activeResource | where-object -Property "type" -eq 'Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions'
    foreach ($instructionSteps in $connectorDefinitionObject.properties.connectorUiConfig.instructionSteps) {
        New-ParametersForConnectorInstuctions $instructionSteps.instructions   
    }

    return $templateParameter;
}

function New-ParametersForConnectorInstuctions($instructions)
{
    foreach ($instruction in $instructions){
        if($instruction.type -eq "Textbox")
        {
            $newParameter = [PSCustomObject]@{
                defaultValue = $instruction.parameters.name;
                type = "string";
                minLength = 1;
            }
            $templateParameter | Add-Member -MemberType NoteProperty -Name $instruction.parameters.name -Value $newParameter
        }
        elseif($instruction.type -eq "OAuthForm")
        {
            $newParameter = [PSCustomObject]@{
                defaultValue = "-NA-";
                type = "securestring";
                minLength = 1;
            }
            $templateParameter | Add-Member -MemberType NoteProperty -Name "ClientId" -Value $newParameter
            $templateParameter | Add-Member -MemberType NoteProperty -Name "ClientSecret" -Value $newParameter
            $templateParameter | Add-Member -MemberType NoteProperty -Name "AuthorizationCode" -Value $newParameter
        }
        elseif($instruction.type -eq "ContextPane")
        {
            New-ParametersForConnectorInstuctions $instruction.parameters.instructionSteps.instructions    
        }
    }
}

function Get-MetaDataBaseResource($resourceName, $parentId, $contentId, $kind, $contentVersion, $dataFileMetadata, $solutionFileMetadata){
    $author = $dataFileMetadata.Author.Split(" - ");
    $authorDetails = [PSCustomObject]@{
        name  = $author[0];
    };
    if($null -ne $author[1])
    {
        $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
    }

    $properties = [PSCustomObject]@{
        parentId  = $parentId;
        contentId =  $contentId;
        kind     = $kind;
        version      = $contentVersion;
        source      = [PSCustomObject]@{
            sourceId = "[variables('_solutionId')]";
            name = "[variables('_solutionName')]";
            kind = "Solution";
        };
        author = $authorDetails;
        support = $solutionFileMetadata.support;
    }

    return [PSCustomObject]@{
        name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',$resourceName)]";
        apiVersion = "2022-01-01-preview"
        type       = "Microsoft.OperationalInsights/workspaces/providers/metadata"
        properties = $properties;
    }
}

function Get-MetaDataResource($TemplateCounter, $dataFileMetadata, $solutionFileMetadata){
    if($templateContentTypeByCounter[$TemplateCounter] -eq "DataConnector")
    {
        $parentIdResourceName = "'Microsoft.SecurityInsights/dataConnectorDefinitions'"
    }
    else {
        $parentIdResourceName = "'Microsoft.SecurityInsights/dataConnectors'"
    }

    $parentId = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), $parentIdResourceName, variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)'))]"
    $metaDataResourceName = "concat('DataConnector-', variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)'))"
    $metaDataContentId = "[variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')]"
    $metaDatsContentVersion  = "[variables('dataConnectorVersion$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')]"
    $metaDataResource =  Get-MetaDataBaseResource $metaDataResourceName $parentId $metaDataContentId $templateContentTypeByCounter[$TemplateCounter] $metaDatsContentVersion $dataFileMetadata $solutionFileMetadata
    
    if($templateContentTypeByCounter[$TemplateCounter] -eq "DataConnector")
    {
        $dependencies = [PSCustomObject]@{
                "criteria" =  @(
                    [PSCustomObject]@{
                        "version" = "[variables('dataConnectorVersion$($templateKindByCounter[2])$($global:connectorCounter)')]";
                        "contentId" = "[variables('_dataConnectorContentId$($templateKindByCounter[2])$($global:connectorCounter)')]";
                        "kind" = "ResourcesDataConnector"
                    }
                )
            }

        $metaDataResource.properties | Add-Member -NotePropertyName "dependencies" -NotePropertyValue $dependencies
    }

    return  $metaDataResource;
}

function Get-ContentTemplateResource($contentResourceDetails, $TemplateCounter, $ccpItem){
    $contentVersion = "variables('dataConnectorVersion$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')";
    $contentTemplateName = "variables('dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')";
    $contentId = "variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')";
    $resoureKind = $templateContentTypeByCounter[$TemplateCounter];
    if($resoureKind -eq "DataConnector")
    {
        $resoureKindTag = "dc";
    }
    else {
        $resoureKindTag = "rdc";
    }

    $title = $ccpItem.title;
    $displayName = $title; #  + "-" + $templateContentTypeByCounter[$TemplateCounter]
    $randomNumber = Get-Random
    return [PSCustomObject]@{
        type       = "Microsoft.OperationalInsights/workspaces/providers/contentTemplates";
        apiVersion = $contentResourceDetails.metadataApiVersion; # "2023-04-01-preview";
        name        = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', $contentTemplateName, $randomNumber)]";
        location   = "[parameters('workspace-location')]";
        dependsOn  = @(
            "$($contentResourceDetails.dependsOn)"
        );
        properties = [PSCustomObject]@{
            contentId  =  "[$contentId]";
            displayName = $displayName;
            contentKind = $templateContentTypeByCounter[$TemplateCounter];
            mainTemplate = [PSCustomObject]@{
                '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
                contentVersion = "[$contentVersion]";
                parameters     = [PSCustomObject]@{};
                variables      = [PSCustomObject]@{};
                resources      = @(
                )
            };
            packageKind = "Solution";
            packageVersion = "[variables('_solutionVersion')]";
            packageName = "[variables('_solutionName')]";
            contentProductId = "[concat(take(variables('_solutionId'), 50),'-','$resoureKindTag','-', uniqueString(concat(variables('_solutionId'),'-','$resoureKind','-',$contentId,'-', $contentVersion)))]";
            packageId = "[variables('_solutionId')]";
            contentSchemaVersion = $contentResourceDetails.contentSchemaVersion;
            version = "[variables('_solutionVersion')]";
        }
    }
}

function Get-ArmResource($name, $type, $kind, $properties){
    [hashtable]$apiVersion = @{
        "Microsoft.SecurityInsights/dataConnectors" = "2022-12-01-preview";
        "Microsoft.SecurityInsights/dataConnectorDefinitions" = "2022-09-01-preview";
        "Microsoft.OperationalInsights/workspaces/tables" = "2021-03-01-privatepreview";
        "Microsoft.Insights/dataCollectionRules" = "2021-09-01-preview";
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

function addNewParameter($parameterName) {
    $hasParameter = [bool]($global:baseMainTemplate.PSobject.Properties.name -match "$parameterName")
    if (!$hasParameter) {
        $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$parameterName" -NotePropertyValue ([PSCustomObject] @{
            defaultValue = "Enter $parameterName value";
            type         = "string";
            minLength    = 1;
        })
    }
}

# THIS IS THE STARTUP FUNCTION FOR CCP RESOURCE CREATOR
function createCCPConnectorResources($contentResourceDetails, $dataFileMetadata, $solutionFileMetadata, $dcFolderName, $ccpDict, $solutionBasePath, $solutionName) {
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

    if (!$global:baseMainTemplate.variables."dataConnectorVersion$($templateKindByCounter[1])$($global:connectorCounter)") { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$($templateKindByCounter[1])$($global:connectorCounter)" -NotePropertyValue "1.0.0"
    }

    if (!$global:baseMainTemplate.variables."dataConnectorVersion$($templateKindByCounter[2])$($global:connectorCounter)") { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$($templateKindByCounter[2])$($global:connectorCounter)" -NotePropertyValue "1.0.0"
    }

    try {
        $activeResource =  @()
        $tableCounter = 1;

        foreach ($ccpItem in $ccpDict) {
            $templateName = $ccpItem.DCDefinitionId; #$ccpItem.title;
            For ($TemplateCounter = 1; $TemplateCounter -lt 3; $TemplateCounter++) {
            
                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)" -NotePropertyValue "$templateName"
            
                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)" -NotePropertyValue "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')))]"
                
                $templateContent = Get-ContentTemplateResource $contentResourceDetails $TemplateCounter $ccpItem; 
                $templateContent.properties.mainTemplate.resources += Get-MetaDataResource $TemplateCounter $dataFileMetadata $solutionFileMetadata
                
                if($TemplateCounter -eq 2)
                {
                    $templateContent.properties.mainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)" -NotePropertyValue "[variables('_dataConnectorContentId$($templateKindByCounter[2])$($global:connectorCounter)')]"        
                    $templateContentConnections = $templateContent

                    $global:DependencyCriteria += [PSCustomObject]@{
                        kind      = "DataConnector";
                        contentId = "[variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')]";
                        version   = if ($dataFileMetadata.TemplateSpec){"[variables('dataConnectorVersion$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)')]"}else{$dataFileMetadata.Version};
                    };
                }
                else
                {
                    $templateContentConnectorDefinition = $templateContent
                }
            }

            #========start:dc definition resource===========
            $dcDefinitionFilteredPath = $ccpItem.DCDefinitionFilePath.Replace($solutionName + "/", "").Replace($dcFolderName + "/", "")
            $ccpDataDefinitionFilePath = $solutionBasePath + "/" + $solutionName + "/" + $dcFolderName + "/" + $dcDefinitionFilteredPath
            $ccpDataDefinitionFilePath = $ccpDataDefinitionFilePath.Replace("//", "/")
            Write-Host "CCP DataDefinition File Path : $ccpDataDefinitionFilePath"
            
            $fileContent = Get-Content -Raw $ccpDataDefinitionFilePath | Out-String | ConvertFrom-Json

            if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectorDefinitions")
            {
                Write-Host "Processing for CCP DataDefinition file path: $dcDefinitionFilteredPath"
                $resourceName = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$($templateKindByCounter[1])$($global:connectorCounter)'))]"

                $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
                $armResource.type = "Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions"

                $hasLocationProperty = [bool]($armResource.PSobject.Properties.name -match "location")
                if ($hasLocationProperty) {
                    $locationProperty = $armResource.location
                    $placeHoldersMatched = $locationProperty | Select-String $placeHolderPatternMatches -AllMatches

                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        $armResource.location = "[[parameters('$($placeHolderName)')]"
                        addNewParameter -parameterName $placeHolderName
                    }
                }

                $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource

                $activeResource += $armResource
                $activeResource += Get-MetaDataResource 1 $dataFileMetadata $solutionFileMetadata
            }
            
            
            #========end:dc definition resource===========
            #========start:dc definition resource===========
            $ccpPollerFilePath = $ccpItem.DCPollerFilePath
            Write-Host "CCP Poller File Path : $ccpPollerFilePath"
            $ccpPollerFilePath = $ccpPollerFilePath.Replace("//", "/")
            $fileContent = Get-Content -Raw $ccpPollerFilePath | Out-String | ConvertFrom-Json

            if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectors") {
                
                Write-Host "Processing for CCP Poller file path: $ccpPollerFilePath"
                $resourceName = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', '$templateName')]"
                $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
                $armResource.type = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors"
                $armResource.kind = $ccpItem.PollerKind;

                # dataCollectionEndpoint
                $hasDataCollectionEndpoint = [bool](($armResource.properties.dcrConfig).PSobject.Properties.name -match "dataCollectionEndpoint")
                if ($hasDataCollectionEndpoint) {
                    $dataCollectionEndpointProperty = $armResource.properties.dcrConfig.dataCollectionEndpoint
                    $placeHoldersMatched = $dataCollectionEndpointProperty | Select-String $placeHolderPatternMatches -AllMatches

                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        #$dataCollectionEndpointNameValue = "$($placeHolderName)$($global:connectorCounter)"
                        #$armResource.properties.dcrConfig.dataCollectionEndpoint = "[variables('$($dataCollectionEndpointNameValue)')]"
                        $armResource.properties.dcrConfig.dataCollectionEndpoint = "[[parameters('dcrConfig').dataCollectionEndpoint]"

                        # if (!$global:baseMainTemplate.variables."$dataCollectionEndpointNameValue") {
                        #     $global:baseMainTemplate.variables | Add-Member -NotePropertyName "$dataCollectionEndpointNameValue" -NotePropertyValue "dataCollectionEndpointId"
                        # }
                        #addNewParameter -parameterName $dataCollectionEndpointNameValue
                    }
                }

                # dataCollectionRuleImmutableId
                $hasDataCollectionRuleImmutableId = [bool](($armResource.properties.dcrConfig).PSobject.Properties.name -match "dataCollectionRuleImmutableId")
                if ($hasDataCollectionRuleImmutableId) {
                    $dataCollectionRuleImmutableIdProperty = $armResource.properties.dcrConfig.dataCollectionRuleImmutableId
                    $placeHoldersMatched = $dataCollectionRuleImmutableIdProperty | Select-String $placeHolderPatternMatches -AllMatches

                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        #$dataCollectionRuleImmutableIdValue = "$($placeHolderName)$($global:connectorCounter)"
                        #$armResource.properties.dcrConfig.dataCollectionRuleImmutableId = "[[parameters('$($dataCollectionRuleImmutableIdValue)')]"
                        $armResource.properties.dcrConfig.dataCollectionRuleImmutableId = "[[parameters('dcrConfig').dataCollectionRuleImmutableId]"
                        #addNewParameter -parameterName $dataCollectionRuleImmutableIdValue
                    }
                }

                if($armResource.properties.auth.type.ToLower() -eq 'oauth2')
                {
                    # clientid
                    $hasClientId = [bool]($armResource.properties.auth.PSobject.Properties.name -match "ClientId")
                    if ($hasClientId) {
                        $clientIdProperty = $armResource.properties.auth.ClientId
                        $placeHoldersMatched = $clientIdProperty | Select-String $placeHolderPatternMatches -AllMatches

                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                            $armResource.properties.auth.ClientId = "[[parameters('ClientId')]"

                            #$global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "ClientId"
                            addNewParameter -parameterName 'ClientId'
                        }
                    }

                    # client secret
                    $hasClientSecretId = [bool]($armResource.properties.auth.PSobject.Properties.name -match "ClientSecret")
                    if ($hasClientSecretId) {
                        $clientSecretIdProperty = $armResource.properties.auth.ClientSecret
                        $placeHoldersMatched = $clientSecretIdProperty | Select-String $placeHolderPatternMatches -AllMatches

                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                            $armResource.properties.auth.ClientSecret = "[[parameters('ClientSecret')]"

                            #$global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "ClientSecret"
                            addNewParameter -parameterName 'ClientSecret'
                        }
                    }

                    # authorization code
                    if($armResource.properties.auth.grantType -eq 'authorization_code') {
                        $hasAuthorizationCode = [bool]($armResource.properties.auth.PSobject.Properties.name -match "AuthorizationCode")
                        if ($hasAuthorizationCode) {
                            $authorizationCodeProperty = $armResource.properties.auth.AuthorizationCode
                            $placeHoldersMatched = $authorizationCodeProperty | Select-String $placeHolderPatternMatches -AllMatches

                            if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                                $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                                $armResource.properties.auth.AuthorizationCode = "[[parameters('AuthorizationCode')]"

                                #$global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "AuthorizationCode"
                                addNewParameter -parameterName 'AuthorizationCode'
                            }
                        }
                    }

                    # AuthorizationEndpoint placeholder
                    if ($null -ne $armResource.properties.auth.AuthorizationEndpoint -and $armResource.properties.request.auth.AuthorizationEndpoint.contains("{{")) {
                        $authorizationEndpointValue = $armResource.properties.auth.AuthorizationEndpoint
                        $placeHoldersMatched = $authorizationEndpointValue | Select-String $placeHolderPatternMatches -AllMatches
                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                            $armResource.properties.request.AuthorizationEndpoint = "[[parameters('AuthorizationEndpoint')]"

                            #$global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "AuthorizationEndpoint"
                            addNewParameter -parameterName 'AuthorizationEndpoint'
                        }
                    }

                    # TokenEndpoint placeholder 
                    if ($null -ne $armResource.properties.auth.TokenEndpoint -and $armResource.properties.request.auth.TokenEndpoint.contains("{{")) {
                        $tokenEndpointValue = $armResource.properties.auth.TokenEndpoint
                        $placeHoldersMatched = $tokenEndpointValue | Select-String $placeHolderPatternMatches -AllMatches
                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                            $armResource.properties.request.TokenEndpoint = "[[parameters('TokenEndpoint')]"

                            #$global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "TokenEndpoint"
                            addNewParameter -parameterName 'TokenEndpoint'
                        }
                    }
                }
                elseif ($armResource.properties.auth.type.ToLower() -eq 'basic') {
                    # username
                    $hasUsername = [bool]($armResource.properties.auth.PSobject.Properties.name -match "username")
                    if ($hasUsername) {
                        $usernameProperty = $armResource.properties.auth.username
                        $placeHoldersMatched = $usernameProperty | Select-String $placeHolderPatternMatches -AllMatches

                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                            $armResource.properties.auth.username = "[[parameters('username')]"

                            addNewParameter -parameterName 'username'
                            # if (!$global:baseMainTemplate.parameters.username) {
                            #     $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "username" -NotePropertyValue "username"
                            # }
                        }
                    }

                    # password 
                    $hasPassword = [bool]($armResource.properties.auth.PSobject.Properties.name -match "password")
                    if ($hasPassword) {
                        $passwordProperty = $armResource.properties.auth.password
                        $placeHoldersMatched = $passwordProperty | Select-String $placeHolderPatternMatches -AllMatches

                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                            $armResource.properties.auth.password = "[[parameters('password')]"

                            addNewParameter -parameterName 'password'
                            # if (!$global:baseMainTemplate.parameters."$placeHolderName") {
                            #     $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "password"
                            # }
                        }
                    }
                }
                elseif ($armResource.properties.auth.type.ToLower() -eq 'apikey') {
                    # ApiKey 
                    $hasApiKey = [bool]($armResource.properties.auth.PSobject.Properties.name -match "ApiKey")
                    if ($hasApiKey) {
                        $apiKeyProperty = $armResource.properties.auth.ApiKey
                        $placeHoldersMatched = $apiKeyProperty | Select-String $placeHolderPatternMatches -AllMatches

                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                            $armResource.properties.auth.ApiKey = "[[parameters('apikey')]"

                            addNewParameter -parameterName 'apikey'
                            # if (!$global:baseMainTemplate.parameters."$placeHolderName") {
                            #     $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "ApiKey"
                            # }
                        }
                    }
                }

                if ($armResource.properties.request.apiEndPoint.contains("{{")) {
                    # identify any placeholders in apiEndpoint
                    $endPointUrl = $armResource.properties.request.apiEndPoint                    
                    $placeHoldersMatched = $endPointUrl | Select-String $placeHolderPatternMatches -AllMatches
                    
                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        # has some placeholders 
                        $finalizedEndpointUrl = ""
                        $finalizedEndpointUrl = "[[concat("
                        $closureBrackets = ")]"

                        foreach ($currentPlaceHolder in $placeHoldersMatched.Matches.Value) {
                            $placeHolderName = $currentPlaceHolder.replace("{{", "").replace("}}", "")
                            $splitEndpoint = $endPointUrl -split "($currentPlaceHolder)"
                            $commaCount = 0
                            foreach($splitItem in $splitEndpoint) {
                                if ($splitItem -eq $currentPlaceHolder) {
                                    if ($finalizedEndpointUrl -eq '') {
                                        $finalizedEndpointUrl += "parameters('" + $placeHolderName + "')"
                                    } else {
                                        $finalizedEndpointUrl += ", parameters('" + $placeHolderName + "')"
                                    }
                                    
                                    addNewParameter -parameterName "$placeHolderName"
                                    # if (!$global:baseMainTemplate.parameters."$placeHolderName") {
                                    #     $global:baseMainTemplate.parameters | Add-Member -NotePropertyName " $placeHolderName" -NotePropertyValue "$placeHolderName"
                                    # }
                                } else {
                                    if ($commaCount -eq 0) {
                                        $finalizedEndpointUrl += "'"+ $splitItem + "'"
                                        $commaCount += 1
                                    } else {
                                        $finalizedEndpointUrl += ", '" + $splitItem + "'"
                                    }
                                }
                            }
                        }

                        $armResource.properties.request.apiEndPoint = $finalizedEndpointUrl + $closureBrackets
                    }
                }

                # retry count placeholders
                if ($null -ne $armResource.properties.request.retryCount -and ($armResource.properties.request.retryCount -is [System.String] -and $armResource.properties.request.retryCount.contains("{{"))) {
                    $retryCountValue = $armResource.properties.request.retryCount
                    $placeHoldersMatched = $retryCountValue | Select-String $placeHolderPatternMatches -AllMatches
                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        $armResource.properties.request.retryCount = "[[parameters('" + $placeHolderName + "')]"
                        addNewParameter -parameterName $placeHolderName
                        # if (!$global:baseMainTemplate.parameters."$placeHolderName") {
                        #     $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "retryCount"
                        # }
                    }
                }
                
                # rateLimitQPS placeholders
                if ($null -ne $armResource.properties.request.rateLimitQPS -and ($armResource.properties.request.rateLimitQPS -is [System.String] -and $armResource.properties.request.rateLimitQPS.contains("{{"))) {
                    $rateLimitQPSValue = $armResource.properties.request.rateLimitQPS
                    $placeHoldersMatched = $rateLimitQPSValue | Select-String $placeHolderPatternMatches -AllMatches
                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        $armResource.properties.request.rateLimitQPS = "[[parameters('" + $placeHolderName + "')]"

                        addNewParameter -parameterName "$placeHolderName"
                        # if (!$global:baseMainTemplate.parameters."$placeHolderName") {
                        #     $global:baseMainTemplate.parameters | Add-Member -NotePropertyName "$placeHolderName" -NotePropertyValue "rateLimitQPS"
                        # }
                    }
                }

                $templateContentConnections.properties.mainTemplate.resources += $armResource
            }
            #========end:dc definition resource===========
            #========start: dcr resource===========
            $ccpDCRFilePath = $ccpItem.DCRFilePath
            $ccpDCRFilePath = $ccpDCRFilePath.Replace("//", "/")
            Write-Host "CCP DCR File Path : $ccpDCRFilePath"

            $fileContent = Get-Content -Raw $ccpDCRFilePath | Out-String | ConvertFrom-Json

            if($fileContent.type -eq "Microsoft.Insights/dataCollectionRules")
            {
                Write-Host "Processing for CCP DCR file path: $ccpDCRFilePath"
                foreach ($logAnalyticDestination in $fileContent.properties.destinations.logAnalytics)
                {
                    $logAnalyticDestination.workspaceResourceId = "[variables('workspaceResourceId')]"
                }

                $dcrPlaceHolderMatched = $fileContent.name | Select-String $placeHolderPatternMatches -AllMatches
                if ($dcrPlaceHolderMatched.Matches.Value.Count -gt 0) {
                    $startIndexOfOpenBraces = $fileContent.name.indexOf('{{')
                    $nameWithoutPlaceHolder = $fileContent.name.substring(0, $startIndexOfOpenBraces)
                    $fileContent.name = "[concat('"+ $nameWithoutPlaceHolder + "', parameters('workspace'))]"
                }
                $armResource = Get-ArmResource $fileContent.name $fileContent.type $fileContent.kind $fileContent.properties

                # location
                $hasLocationProperty = [bool]($armResource.PSobject.Properties.name -match "location")
                if ($hasLocationProperty) {
                    $locationProperty = $armResource.location
                    $placeHoldersMatched = $locationProperty | Select-String $placeHolderPatternMatches -AllMatches

                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        #$armResource.location = "[[parameters('$($placeHolderName)')]"
                        addNewParameter -parameterName $placeHolderName
                    }
                }

                # dataCollectionEndpointId
                $hasDataCollectionEndpointIdProperty = [bool](($armResource.properties).PSobject.Properties.name -match "dataCollectionEndpointId")
                if ($hasDataCollectionEndpointIdProperty) {
                    $dataCollectionEndpointIdProperty = $armResource.properties.dataCollectionEndpointId
                    $placeHoldersMatched = $dataCollectionEndpointIdProperty | Select-String $placeHolderPatternMatches -AllMatches

                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        $dataCollectionEndpointIdPropertyName = $placeHolderName + $global:connectorCounter
                        $armResource.properties.dataCollectionEndpointId = "[[variables('$($dataCollectionEndpointIdPropertyName)')]"
                        
                        if (!$global:baseMainTemplate.variables."$dataCollectionEndpointIdPropertyName") {
                            $global:baseMainTemplate.variables | Add-Member -NotePropertyName "$dataCollectionEndpointIdPropertyName" -NotePropertyValue "[concat('/subscriptions/',parameters('subscription'),'/resourceGroups/',parameters('resourceGroupName'),'/providers/Microsoft.Insights/dataCollectionEndpoints/',parameters('workspace'))]"
                        }
                    }
                }

                # workspaceResourceId
                $hasWorkspaceResourceIdProperty = [bool](($armResource.properties).PSobject.Properties.name -match "workspaceResourceId")
                if ($hasWorkspaceResourceIdProperty) {
                    $workspaceResourceIdProperty = $armResource.properties.destinations.logAnalytics.workspaceResourceId
                    $placeHoldersMatched = $workspaceResourceIdProperty | Select-String $placeHolderPatternMatches -AllMatches

                    if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                        $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                        $armResource.properties.destinations.logAnalytics.workspaceResourceId = "[[parameters('$($placeHolderName)')]"

                        addNewParameter -parameterName $placeHolderName
                    }
                }

                # check if streamName and outputSteamName values are correct or not. If no then make it same
                # $dataFlowStreamName = $fileContent.properties.dataFlows[0].streams[0]
                # $dataFlowOutputStreamName = $fileContent.properties.dataFlows[0].outputStream

                # if ($dataFlowStreamName -ne $dataFlowOutputStreamName) {
                #     Write-Host "In DCR file, 'dataflow.streamName' and 'dataflow.outputStream' values are different. Resetting values for both to 'dataflow.streamName' value!"
                #     $fileContent.properties.dataFlows[0].outputStream = $dataFlowStreamName
                # }

                $armResource = $(removePropertiesRecursively $armResource $false)
                $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
            }
            #========end: dcr resource===========
            #========start: tables resource===========
            $ccpTablesFilePath = $ccpItem.TableFilePath
            Write-Host "CCP Table File Path : $ccpTablesFilePath"

            if ($null -ne $ccpTablesFilePath -and $ccpTablesFilePath -ne '') {
                $fileContent = Get-Content -Raw $ccpTablesFilePath | Out-String | ConvertFrom-Json

                if($fileContent.type -eq "Microsoft.OperationalInsights/workspaces/tables")
                {
                    $resourceName = $fileContent.name
                    $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties

                    $hasLocationProperty = [bool]($armResource.PSobject.Properties.name -match "location")
                    if ($hasLocationProperty) {
                        $locationProperty = $armResource.location
                        $placeHoldersMatched = $locationProperty | Select-String $placeHolderPatternMatches -AllMatches

                        if ($placeHoldersMatched.Matches.Value.Count -gt 0) {
                            $placeHolderName = $placeHoldersMatched.Matches.Value.replace("{{", "").replace("}}", "")
                            #$armResource.location = "[[parameters('$($placeHolderName)')]"
                            addNewParameter -parameterName $placeHolderName
                        }
                    }

                    #$armResource = $(removePropertiesRecursively $armResource $false)
                    $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
                    $tableCounter ++;
                }
            }
            #========end: tables resource===========

            ## Build the full package resources
            $templateContentConnections.properties.mainTemplate.parameters = Get-ConnectionsTemplateParameters $activeResource $ccpItem;
            $global:baseMainTemplate.resources += $templateContentConnectorDefinition
            $global:baseMainTemplate.resources += $activeResource
            $global:baseMainTemplate.resources += $templateContentConnections
            #$global:baseMainTemplate.resources += $dataDefinitionContent

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
                name    = "dataconnectors-link2";
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
        Write-Host "Error occured in createCCPConnector file. Error Details $_"
    }
}