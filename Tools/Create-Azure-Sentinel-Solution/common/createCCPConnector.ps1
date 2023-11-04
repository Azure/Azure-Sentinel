
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
function Get-ConnectionsTemplateParameters($activeResource){

    $paramTestForDefinition = [PSCustomObject]@{
        defaultValue = "connectorDefinitionName";
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

function Get-MetaDataBaseResource($resourceName, $parentId, $contentId, $kind, $contentVersion){
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
        author = [PSCustomObject]@{
            name = "[variables('_solutionAuthor')]";
        };
        support = [PSCustomObject]@{
            name = "[variables('_solutionAuthor')]";
            tier = "[variables('_solutionTier')]";
        };
    }

    return [PSCustomObject]@{
        name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',$resourceName)]";
        apiVersion = "2022-01-01-preview"
        type       = "Microsoft.OperationalInsights/workspaces/providers/metadata"
        properties = $properties;
    }
}

function Get-MetaDataResource($TemplateCounter){
    if($templateContentTypeByCounter[$TemplateCounter] -eq "DataConnector")
    {
        $parentIdResourceName = "'Microsoft.SecurityInsights/dataConnectorDefinitions'"
    }
    else {
        $parentIdResourceName = "'Microsoft.SecurityInsights/dataConnectors'"
    }

    $parentId = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), $parentIdResourceName, variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])'))]"
    $metaDataResourceName = "concat('DataConnector-', variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])'))"
    $metaDataContentId = "[variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])')]"
    $metaDatsContentVersion  = "[variables('dataConnectorVersion$($templateKindByCounter[$TemplateCounter])')]"
    $metaDataResource =  Get-MetaDataBaseResource $metaDataResourceName $parentId $metaDataContentId $templateContentTypeByCounter[$TemplateCounter] $metaDatsContentVersion
    
    if($templateContentTypeByCounter[$TemplateCounter] -eq "DataConnector")
    {
        $dependencies = [PSCustomObject]@{
                "criteria" =  @(
                    [PSCustomObject]@{
                        "version" = "[variables('dataConnectorVersion$($templateKindByCounter[2])')]";
                        "contentId" = "[variables('_dataConnectorContentId$($templateKindByCounter[2])')]";
                        "kind" = "ResourcesDataConnector"
                    }
                )
            }

        $metaDataResource.properties | Add-Member -NotePropertyName "dependencies" -NotePropertyValue $dependencies
    }

    return  $metaDataResource;
}

function Get-ContentTemplateResource($contentResourceDetails, $TemplateCounter){
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

    return [PSCustomObject]@{
        type       = "Microsoft.OperationalInsights/workspaces/providers/contentTemplates";
        apiVersion = "2023-04-01-preview";
        name        = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', $contentTemplateName, $contentVersion)]";
        location   = "[parameters('workspace-location')]";
        dependsOn  = @(
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
        );
        properties = [PSCustomObject]@{
            contentId  =  "[$contentId]";
            displayName = "[concat(variables('_solutionName'), $contentTemplateName)]";
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
            contentProductId = "[concat(substring(variables('_solutionId'), 0, 50),'-','$resoureKindTag','-', uniqueString(concat(variables('_solutionId'),'-','$resoureKind','-',$contentId,'-', $contentVersion)))]";
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

function Get-ContentPackagesForSolution(){
    $contentPackagesPath = "$PSScriptRoot/templating/contentPackages.json"
    $contentPackages = Get-Content -Raw $contentPackagesPath | Out-String | ConvertFrom-Json
    return $contentPackages
}

# THIS IS THE STARTUP FUNCTION FOR CCP RESOURCE CREATOR
function createCCPConnectorResources($contentResourceDetails, $dataFileMetadata, $solutionFileMetadata, $dcFolderName, $ccpDict, $solutionBasePath, $solutionName) {
    $solutionId = $solutionFileMetadata.publisherId + "." + $solutionFileMetadata.offerId
    
    if (!$global:baseMainTemplate.variables.workspaceResourceId) {
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
    }

    if (!$global:baseMainTemplate.variables._solutionName) {
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionName" -NotePropertyValue $dataFileMetadata.Name
    }

    if (!$global:baseMainTemplate.variables._solutionVersion) { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionVersion" -NotePropertyValue $dataFileMetadata.Version
    }

    if (!$global:baseMainTemplate.variables._solutionAuthor) { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionAuthor" -NotePropertyValue $solutionFileMetadata.providers[0]
    }

    if (!$global:baseMainTemplate.variables._packageIcon) { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_packageIcon" -NotePropertyValue "icon icon icon icon"
    }

    if (!$global:baseMainTemplate.variables._solutionId) { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionId" -NotePropertyValue "$solutionId"
    }

    if (!$global:baseMainTemplate.variables."dataConnectorVersion$($templateKindByCounter[1])") { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$($templateKindByCounter[1])" -NotePropertyValue "1.0.0"
    }

    if (!$global:baseMainTemplate.variables."dataConnectorVersion$($templateKindByCounter[2])") { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$($templateKindByCounter[2])" -NotePropertyValue "1.0.0"
    }

    if (!$global:baseMainTemplate.variables._solutionTier) { 
        $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionTier" -NotePropertyValue $solutionFileMetadata.support.tier
    }

    try {
        $activeResource =  @()
        $tableCounter = 1;

        foreach ($ccpItem in $ccpDict) {
            $templateName = $solutionName;

            For ($TemplateCounter = 1; $TemplateCounter -lt 3; $TemplateCounter++) {
            
                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])" -NotePropertyValue "$templateName$($templateKindByCounter[$TemplateCounter])$($global:connectorCounter)"
            
                $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])" -NotePropertyValue "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$(global:connectorCounter)')))]"
                
                $templateContent = Get-ContentTemplateResource $contentResourceDetails $TemplateCounter; 
                $templateContent.properties.mainTemplate.resources += Get-MetaDataResource $TemplateCounter
                
                if($TemplateCounter -eq 2)
                {
                    $templateContent.properties.mainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])$(global:connectorCounter)" -NotePropertyValue "[variables('_dataConnectorContentId$($templateKindByCounter[2])$(global:connectorCounter)')]"        
                    $templateContentConnections = $templateContent
                }
                else
                {
                    $templateContentConnectorDefinition = $templateContent
                }
            }

            #========start:dc definition resource===========
            $dcDefinitionFilteredPath = $ccpItem.DCDefinitionFilePath.Replace($solutionName + "/", "").Replace($dcFolderName + "/", "")
            $ccpDataDefinitionFilePath = $solutionBasePath + "/" + $solutionName + "/" + $dcFolderName + "/" + $dcDefinitionFilteredPath
            Write-Host "CCP DataDefinition File Path : $ccpDataDefinitionFilePath"

            $fileContent = Get-Content -Raw $ccpDataDefinitionFilePath | Out-String | ConvertFrom-Json
            if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectorDefinitions")
            {
                Write-Host "Processing for CCP DataDefinition file path: $dcDefinitionFilteredPath"
                $resourceName = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$($templateKindByCounter[1])'))]"

                $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
                $armResource.type = "Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions"
                $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
                
                $activeResource += $armResource
                $activeResource += Get-MetaDataResource 1
            }
            #========end:dc definition resource===========
            #========start:dc definition resource===========
            $ccpPollerFilePath = $ccpItem.DCRFilePath
            Write-Host "CCP Poller File Path : $ccpPollerFilePath"

            $fileContent = Get-Content -Raw $ccpPollerFilePath | Out-String | ConvertFrom-Json

            if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectors") {
                Write-Host "Processing for CCP Poller file path: $ccpPollerFilePath"
                $resourceName = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', '$name')]"
                $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
                $armResource.type = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors"
                $armResource.properties.connectorDefinitionName = "[[parameters('connectorDefinitionName')]"
                $armResource.properties.dcrConfig.dataCollectionEndpoint = "[[parameters('dcrConfig').dataCollectionEndpoint]"
                $armResource.properties.dcrConfig.dataCollectionRuleImmutableId = "[[parameters('dcrConfig').dataCollectionRuleImmutableId]"
                
                if($armResource.properties.auth.type -eq 'OAuth2')
                {
                    $armResource.properties.auth.ClientId = "[[parameters('ClientId')]"
                    $armResource.properties.auth.ClientSecret = "[[parameters('ClientSecret')]"

                    if($armResource.properties.auth.grantType -eq 'authorization_code')
                    {
                        $armResource.properties.auth.AuthorizationCode = "[[parameters('AuthorizationCode')]"
                    }   
                }
                $templateContentConnections.properties.mainTemplate.resources += $armResource
            }
            #========end:dc definition resource===========
            #========start: dcr resource===========
            $ccpDCRFilePath = $ccpItem.DCRFilePath
            Write-Host "CCP DCR File Path : $ccpDCRFilePath"

            $fileContent = Get-Content -Raw $ccpDCRFilePath | Out-String | ConvertFrom-Json

            if($fileContent.type -eq "Microsoft.Insights/dataCollectionRules")
            {
                Write-Host "Processing for CCP DCR file path: $ccpDCRFilePath"
                if([bool]($fileContent.properties.PSobject.Properties.name -match "dataCollectionEndpointId") -eq $false)
                {
                    $dcrEndpoint = "[concat('/subscriptions/',parameters('subscription'),'/resourceGroups/',parameters('resourceGroupName'),'/providers/Microsoft.Insights/dataCollectionEndpoints/',parameters('workspace'))]"
                    $fileContent.properties | Add-Member -MemberType NoteProperty -Name dataCollectionEndpointId -Value $dcrEndpoint
                }
                
                foreach ($logAnalyticDestination in $fileContent.properties.destinations.logAnalytics)
                {
                    $logAnalyticDestination.workspaceResourceId = "[variables('workspaceResourceId')]"
                }

                $armResource = Get-ArmResource $fileContent.name $fileContent.type $fileContent.kind $fileContent.properties
                $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
            }
            #========end: dcr resource===========
            #========start: tables resource===========
            $ccpTablesFilePath = $ccpItem.TableFilePath
            Write-Host "CCP Table File Path : $ccpTablesFilePath"

            $fileContent = Get-Content -Raw $ccpTablesFilePath | Out-String | ConvertFrom-Json

            if($fileContent.type -eq "Microsoft.OperationalInsights/workspaces/tables")
            {
                $baseMainTemplate.variables | Add-Member -NotePropertyName "_logAnalyticsTableId$tableCounter" -NotePropertyValue $fileContent.name
                $resourceName = "[variables('_logAnalyticsTableId$tableCounter')]"
                $fileContent.properties.schema.name = "[variables('_logAnalyticsTableId$tableCounter')]"
                $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
                $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
                $tableCounter ++;
            }
            #========end: tables resource===========

            ## Build the full package resources
            $templateContentConnections.properties.mainTemplate.parameters = Get-ConnectionsTemplateParameters $activeResource;
            $armResourceContentPackage = Get-ContentPackagesForSolution
            $global:baseMainTemplate.resources += $templateContentConnectorDefinition
            $global:baseMainTemplate.resources += $activeResource
            $global:baseMainTemplate.resources += $templateContentConnections
            $global:baseMainTemplate.resources += $armResourceContentPackage

            $global:connectorCounter += 1
        }
    }
    catch {
        Write-Host "Error occured in createCCPConnector file. Error Details $_"
    }
}