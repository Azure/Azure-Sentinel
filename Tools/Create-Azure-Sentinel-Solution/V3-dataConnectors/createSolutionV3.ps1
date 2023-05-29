".functions\Format-Json.ps1"
".function\Get-ConnectionsTemplateParameters.ps1"
".function\Get-MetaDataResource.ps1"

[hashtable]$templateKindByCounter = @{
    1 = "ConnectorDefinition"; 
    2 = "Connections";
}

[hashtable]$templateContentTypeByCounter = @{
    1 = "DataConnector"; 
    2 = "ResourcesDataConnector";
}

function Get-ContentTemplateResource($templateName, $TemplateCounter){
    $contentVersion = "variables('dataConnectorVersion$($templateKindByCounter[$TemplateCounter])')";

    return [PSCustomObject]@{
        type       = "Microsoft.OperationalInsights/workspaces/providers/contentTemplates";
        apiVersion = "2023-04-01-preview";
        name        = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', variables('dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])'),$contentVersion)]";
        location   = "[parameters('workspace-location')]";
        dependsOn  = @(
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
        );
        properties = [PSCustomObject]@{
            contentId  =  "[variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])')]";
            displayName = "[concat(variables('_solutionName'), variables('dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])'))]";
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
            packageId = "[variables('_solutionId')]";
            contentSchemaVersion = "3.0.0";
        }
    }
}

function Get-ArmResource($name, $type, $kind, $properties){
    [hashtable]$apiVersion = @{
        "Microsoft.SecurityInsights/dataConnectors" = "2022-12-01-preview";
        "Microsoft.SecurityInsights/dataConnectorDefinitions" = "2022-09-01-preview";
        "Microsoft.OperationalInsights/workspaces" = "2021-03-01-privatepreview";
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


$inputFilesPath = "$PSScriptRoot\input"
$baseMainTemplatePath = "$PSScriptRoot/templating/baseMainTemplate.json"
$solutionMetadataPath = "$PSScriptRoot/input/solutionMetadata.json"
$baseMainTemplate = Get-Content -Raw $baseMainTemplatePath | Out-String | ConvertFrom-Json
$solutionMetadata = Get-Content -Raw $solutionMetadataPath | Out-String | ConvertFrom-Json

$baseMainTemplate.variables | Add-Member -NotePropertyName "workspaceResourceId" -NotePropertyValue "[resourceId('microsoft.OperationalInsights/Workspaces', parameters('workspace'))]"
$baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionName" -NotePropertyValue $solutionMetadata.SolutionName
$baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionVersion" -NotePropertyValue $solutionMetadata.SolutionVersion
$baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionAuthor" -NotePropertyValue $solutionMetadata.SolutionAuthor
$baseMainTemplate.variables | Add-Member -NotePropertyName "_packageIcon" -NotePropertyValue $solutionMetadata.PackageIcon
$baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionId" -NotePropertyValue "azuresentinel.azure-sentinel-solution-$($solutionMetadata.PackageId)"
$baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$($templateKindByCounter[1])" -NotePropertyValue $solutionMetadata.ConnectorDefinitionTemplateVersion
$baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$($templateKindByCounter[2])" -NotePropertyValue $solutionMetadata.DataConnectorsTemplateVersion

# create the base Templates.
# One for connector definition (dataConnectorDefinition, DCR, table) and one for the connections (dataConnectors)
$activeResource =  @()
For ($TemplateCounter = 1; $TemplateCounter -lt 3; $TemplateCounter++) {

    $baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])" -NotePropertyValue "$templateName$($templateKindByCounter[$TemplateCounter])"
    $baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])" -NotePropertyValue "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])')))]"
    
    $templateContent = Get-ContentTemplateResource $solutionMetadata.TemplateName $TemplateCounter; 
    $templateContent.properties.mainTemplate.resources += Get-MetaDataResource $TemplateCounter
    
    if($TemplateCounter -eq 2)
    {
        $templateContent.properties.mainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])" -NotePropertyValue "[variables('_dataConnectorContentId$($templateKindByCounter[2])')]"        
        $templateContentConnections = $templateContent
    }
    else
    {
        $templateContentConnectorDefinition = $templateContent
    }
}

## create the template resource according to the input files
$tableCounter = 1;
foreach ($file in $(Get-ChildItem $inputFilesPath)) {
    $filePath = Join-Path -Path $inputFilesPath -ChildPath "$($file.Name)"
    $fileContent = Get-Content -Raw $filePath | Out-String | ConvertFrom-Json
    $name = $fileContent.name

    if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectorDefinitions")
    {
        $resourceName = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('_dataConnectorContentId$($templateKindByCounter[1])'))]"

        $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
        $armResource.type = "Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions"
        $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
        
        $activeResource += $armResource
        $activeResource += Get-MetaDataResource 1
    }
    elseif($fileContent.type -eq "Microsoft.Insights/dataCollectionRules")
    {
        $dcrEndpoint = "[concat('/subscriptions/',parameters('subscription'),'/resourceGroups/',parameters('resourceGroupName'),'/providers/Microsoft.Insights/dataCollectionEndpoints/',parameters('workspace'))]"
        $fileContent.properties | Add-Member -MemberType NoteProperty -Name dataCollectionEndpointId -Value $dcrEndpoint
        foreach ($logAnalyticDestination in $fileContent.properties.destinations.logAnalytics)
        {
            $logAnalyticDestination.workspaceResourceId = "[variables('workspaceResourceId')]"
        }

        $armResource = Get-ArmResource $fileContent.name $fileContent.type $fileContent.kind $fileContent.properties
        $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
    }
    elseif($fileContent.type -eq "Microsoft.OperationalInsights/workspaces/tables")
    {
        $baseMainTemplate.variables | Add-Member -NotePropertyName "_logAnalyticsTableId$tableCounter" -NotePropertyValue $resourceName
        $resourceName = "[concat(parameters('workspace'),'/', variables('_logAnalyticsTableId$tableCounter'))]"
        $fileContent.properties.schema.name = "[variables('_logAnalyticsTableId$tableCounter')]"
        $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
        $templateContentConnectorDefinition.properties.mainTemplate.resources += $armResource
        $tableCounter ++;
    }
    elseif($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectors") {
        $resourceName = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', '$name')]"
        $armResource = Get-ArmResource $resourceName $fileContent.type $fileContent.kind $fileContent.properties
        $armResource.properties.connectorDefinitionName = "[[parameters('connectorDefinitionName')]"
        $armResource.properties.dcrConfig.dataCollectionEndpoint = "[[parameters('dcrConfig').dataCollectionEndpoint]"
        $armResource.properties.dcrConfig.dataCollectionRuleImmutableId = "[[parameters('dcrConfig').dataCollectionRuleImmutableId]"
        
        $templateContentConnections.properties.mainTemplate.resources += $armResource
    } 
}

## Build the full package resources
$templateContentConnections.properties.mainTemplate.parameters = Get-ConnectionsTemplateParameters($activeResource);
$armResourceContentPackage = Get-ContentPackagesForSolution
$baseMainTemplate.resources += $templateContentConnectorDefinition
$baseMainTemplate.resources += $activeResource
$baseMainTemplate.resources += $templateContentConnections
$baseMainTemplate.resources += $armResourceContentPackage

## convert the object to Json and write it to file
try {
    $jsonConversionDepth = 50
    $mainTemplateOutputPath = "$PSScriptRoot/mainTemplate.json"
    ($baseMainTemplate | ConvertTo-Json -Depth $jsonConversionDepth).Replace('\n','\\n').Replace('\r','\\r').Replace('\"','\\"')  | % { [System.Text.RegularExpressions.Regex]::Unescape($_) } | Format-Json | Out-File $mainTemplateOutputPath -Encoding utf8
}
catch {
    Write-Host "Failed to write output file $mainTemplateOutputPath" -ForegroundColor Red
    break;
}