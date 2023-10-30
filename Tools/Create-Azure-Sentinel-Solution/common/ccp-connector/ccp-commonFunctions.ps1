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
    $metaDataResource =  Get-MetaDataBaseResource  $metaDataResourceName $parentId $metaDataContentId $templateContentTypeByCounter[$TemplateCounter] $metaDatsContentVersion
    
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