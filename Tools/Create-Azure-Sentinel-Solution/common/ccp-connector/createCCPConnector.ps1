. "ccp-commonFunctions.ps1"

[hashtable]$templateKindByCounter = @{
    1 = "ConnectorDefinition"; 
    2 = "Connections";
}

[hashtable]$templateContentTypeByCounter = @{
    1 = "DataConnector"; 
    2 = "ResourcesDataConnector";
}

# hasCCPFolder --> inside of DC folder check if ccp folder is present if not then all files are inside of Dc folder only
param ($dataConnectorFolderPath, $hasCCPFolder, $solutionMetadata, $dataFileMetadata, $solutionId, $dataConnectorArrayList)

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
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionAuthor" -NotePropertyValue $solutionMetadata.providers[0]
}

if (!$global:baseMainTemplate.variables._packageIcon) { 
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_packageIcon" -NotePropertyValue "icon icon icon icon"
}

if (!$global:baseMainTemplate.variables._solutionId) { 
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionId" -NotePropertyValue "$solutionId"
}

if (!$global:baseMainTemplate.variables."dataConnectorVersion$($templateKindByCounter[1])") { 
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$($templateKindByCounter[1])" -NotePropertyValue $solutionMetadata.ConnectorDefinitionTemplateVersion
}

if (!$global:baseMainTemplate.variables."dataConnectorVersion$($templateKindByCounter[2])") { 
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorVersion$($templateKindByCounter[2])" -NotePropertyValue $solutionMetadata.DataConnectorsTemplateVersion
}

if (!$global:baseMainTemplate.variables._solutionTier) { 
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_solutionTier" -NotePropertyValue $solutionMetadata.support.tier
}

# if (!$global:baseMainTemplate.variables._packageIcon) { 
    
# }

$activeResource =  @()

For ($TemplateCounter = 1; $TemplateCounter -lt 3; $TemplateCounter++) {
    $templateName = $dataFileMetadata.Name;

    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])" -NotePropertyValue "$templateName$($templateKindByCounter[$TemplateCounter])"

    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "dataConnectorTemplateName$($templateKindByCounter[$TemplateCounter])" -NotePropertyValue "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])')))]"
    
    $templateContent = Get-ContentTemplateResource $templateName $TemplateCounter; 
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

# From $dataConnectorArrayList identify the dataDefinition list
# eg: if connectorDefinition file contains "id" property value as "abc". Then search for poller file having attribute [{properties -->  { connectorDefinitionName = <id from connector definition ie. abc >} }]. If property is not specified fail. If no value of id property is not found in any of the poller file then also fail the packaging.

# iterate through all of the files inside of the data connector folder or array given. if there is no connector definition then skip ccp as there is no ccp connector for a given solution. --TODO THIS HAS TO BE FIRST STEP AND THEN EXECUTE THIS CODE.

# if we identify 1 ccp then identify the poller
























