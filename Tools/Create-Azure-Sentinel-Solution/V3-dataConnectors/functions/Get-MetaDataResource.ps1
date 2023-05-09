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
        $parentIdResourceName = "Microsoft.SecurityInsights/dataConnectorDefinitions"
    }
    else {
        $parentIdResourceName = "Microsoft.SecurityInsights/dataConnectors"
    }

    $parentId = "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), $parentIdResourceName, variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])')]"
    $metaDataResourceName = "concat('DataConnector-', variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])'))"
    $metaDataContentId = "[variables('_dataConnectorContentId$($templateKindByCounter[$TemplateCounter])')]"
    $metaDatsContentVersion  = "[variables('dataConnectorVersion$($templateKindByCounter[$TemplateCounter])')]"
    $metaDataResource =  Get-MetaDataBaseResource  $metaDataResourceName $parentId $metaDataContentId $templateContentTypeByCounter[$TemplateCounter] $metaDatsContentVersion
    
    if($templateContentTypeByCounter[$TemplateCounter] -eq "DataConnector")
    {
        $dependencies = [PSCustomObject]@{
                "criteria" =  @(
                    [PSCustomObject]@{
                        "version" = "[variables('dataConnectorVersion$($templateKindByCounter[2])')]";
                        "contentId" = "[variables('_dataConnectorContentId$($templateKindByCounter[2])')]";
                        "kind" = "DataConnector"
                    }
                )
            }

        $metaDataResource.properties | Add-Member -NotePropertyName "dependencies" -NotePropertyValue $dependencies
    }

    return  $metaDataResource;
}