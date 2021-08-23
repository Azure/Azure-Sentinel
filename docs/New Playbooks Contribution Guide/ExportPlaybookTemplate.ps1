param(
    [string]$PlaybookArmId,
    [string]$PlaybookSubscriptionId,
    [string]$PlaybookResourceGroupName,
    [string]$PlaybookResourceName,
    [boolean]$GenerateForGallery = $false
)

# Ask for user sign in if not signed in to generate a new token
$azContext = Get-AzContext
if (!$azContext) {
    $connectResult = Connect-AzAccount

    if (!$connectResult) {
        FailWithError -errorMessage "Token argument or interactive sign-in are required"
    }
}
$tokenToUse =  (Get-AzAccessToken).Token
$armHostUrl = $azContext.Environment.ResourceManagerUrl

$apiConnectionResources = [System.Collections.ArrayList]@()
$templateParameters = @{}
$templateVariables = @{}

# Taken from https://stackoverflow.com/questions/56322993/proper-formating-of-json-using-powershell/56324939
function FixJsonIndentation ($jsonOutput)
{
    $currentIndent = 0
    $tabSize = 4
    $lines = $jsonOutput.Split([Environment]::NewLine)
    $newString = ""
    foreach ($line in $lines)
    {
        # skip empty line
        if ($line.Trim() -eq "") {
            continue
        }

        # if the line with ], or }, reduce indent
        if ($line -match "[\]\}]+\,?\s*$") {
            $currentIndent -= 1
        }

        # add the line with the right indent
        if ($newString -eq "") {
            $newString = $line
        } else {
            $spaces = ""
            $matchFirstChar = [regex]::Match($line, '[^\s]+')
            
            $totalSpaces = $currentIndent * $tabSize
            if ($totalSpaces -gt 0) {
                $spaces = " " * $totalSpaces
            }
            
            $newString += [Environment]::NewLine + $spaces + $line.Substring($matchFirstChar.Index)
        }

        # if the line with { or [ increase indent
        if ($line -match "[\[\{]+\s*$") {
            $currentIndent += 1
        }
    }

    return $newString
}

function FailWithError($errorMessage) {
    Write-Host "Script failed with error: $errorMessage" -ForegroundColor Red
    exit
}

function BuildPlaybookArmId() {
    if ($PlaybookArmId) {
        return $PlaybookArmId
    }

    if ($PlaybookSubscriptionId -and $PlaybookResourceGroupName -and $PlaybookResourceName) {
        return "/subscriptions/$PlaybookSubscriptionId/resourceGroups/$PlaybookResourceGroupName/providers/Microsoft.Logic/workflows/$PlaybookResourceName"
    }

    FailWithError -errorMessage "Playbook full ARM id, or subscription, resource group and resource name are required"
}

function SendArmGetCall($relativeUrl) {
    $authHeader = @{
        'Authorization'='Bearer ' + $tokenToUse
    }

    $absoluteUrl = $armHostUrl+$relativeUrl
    
    $result = Invoke-RestMethod -Uri $absoluteUrl -Method Get -Headers $authHeader
    return $result
}

function GetPlaybookResource() {
    $playbookArmIdToUse = BuildPlaybookArmId
    $playbookResource = SendArmGetCall -relativeUrl "$($playbookArmIdToUse)?api-version=2017-07-01"

    $templateParameters.Add("PlaybookName", @{
        "defaultValue"= $playbookResource.Name
        "type"= "string"
    })

    # Update properties to fit ARM template structure
    if ($GenerateForGallery) {
        if (!$playbookResource.tags) {
            $playbookResource.tags = @{
                "hidden-SentinelTemplateName"= $playbookResource.name
                "hidden-SentinelTemplateVersion"= "1.0"
            }
        }
        else {
            if (!$playbookResource.tags["hidden-SentinelTemplateName"]) {
                Add-Member -InputObject $playbookResource.tags -Name "hidden-SentinelTemplateName" -Value $playbookResource.name -MemberType NoteProperty
            }

            if (!$playbookResource.tags["hidden-SentinelTemplateVersion"]) {
                Add-Member -InputObject $playbookResource.tags -Name "hidden-SentinelTemplateVersion" -Value "1.0" -MemberType NoteProperty
            }
        }

        # The azuresentinel connection will use MSI when exported for the gallery, so the playbook must support it too
        if ($playbookResource.identity.type -ne "SystemAssigned") {
            if (!$playbookResource.identity) {
                Add-Member -InputObject $playbookResource -Name "identity" -Value @{
                    "type"= "SystemAssigned"
                } -MemberType NoteProperty
            }
            else {
                $playbookResource.identity = @{
                    "type"= "SystemAssigned"
                }
            }
        }
    }

    $playbookResource.PSObject.Properties.remove("id")
    $playbookResource.location = "[resourceGroup().location]"
    $playbookResource.name = "[parameters('PlaybookName')]"
    Add-Member -InputObject $playbookResource -Name "apiVersion" -Value "2017-07-01" -MemberType NoteProperty
    Add-Member -InputObject $playbookResource -Name "dependsOn" -Value @() -MemberType NoteProperty

    # Remove properties specific to an instance of a deployed playbook
    $playbookResource.properties.PSObject.Properties.remove("createdTime")
    $playbookResource.properties.PSObject.Properties.remove("changedTime")
    $playbookResource.properties.PSObject.Properties.remove("version")
    $playbookResource.properties.PSObject.Properties.remove("accessEndpoint")
    $playbookResource.properties.PSObject.Properties.remove("endpointsConfiguration")

    if ($playbookResource.identity) {
        $playbookResource.identity.PSObject.Properties.remove("principalId")
        $playbookResource.identity.PSObject.Properties.remove("tenantId")
    }

    return $playbookResource
}

function HandlePlaybookApiConnectionReference($apiConnectionReference, $playbookResource) {
    $connectionName = $apiConnectionReference.Name
    $connectionVariableName = "$($connectionName)ConnectionName"
    $templateVariables.Add($connectionVariableName, "[concat('$connectionName-', parameters('PlaybookName'))]")
    $connectorType = if ($apiConnectionReference.Value.id.ToLowerInvariant().Contains("/managedapis/")) { "managedApis" } else { "customApis" } 
    $connectionAuthenticationType = if ($apiConnectionReference.Value.connectionProperties.authentication.type -eq "ManagedServiceIdentity") { "Alternative" } else  { $null }    
    
    # We always convert azuresentinel connections to MSI during export
    if ($GenerateForGallery -and $connectionName -eq "azuresentinel" -and !$connectionAuthenticationType) {
        $connectionAuthenticationType = "Alternative"

        if (!$apiConnectionReference.Value.ConnectionProperties) {
            Add-Member -InputObject $apiConnectionReference.Value -Name "ConnectionProperties" -Value @{} -MemberType NoteProperty
        }
        $apiConnectionReference.Value.connectionProperties = @{
            "authentication"= @{
                "type"= "ManagedServiceIdentity"
            }
        }
    }

    try {
        $existingConnectionProperties = SendArmGetCall -relativeUrl "$($apiConnectionReference.Value.connectionId)?api-version=2016-06-01"
    }
    catch {
        $existingConnectionProperties = $null
    }
    
    $existingConnectorProperties = SendArmGetCall -relativeUrl "$($apiConnectionReference.Value.id)?api-version=2016-06-01"

    # Create API connection resource
    $apiConnectionResource = @{
        "type"= "Microsoft.Web/connections"
        "apiVersion"= "2016-06-01"
        "name"= "[variables('$connectionVariableName')]"
        "location"= "[resourceGroup().location]"
        "kind"= "V1"
        "properties"= @{
            "displayName"= "[variables('$connectionVariableName')]"
            "customParameterValues"= @{}
            "parameterValueType"= $connectionAuthenticationType
            "api"= @{
                "id"= "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/$connectorType/$connectionName')]"
            }
        }
    }
    if (!$apiConnectionResource.properties.parameterValueType) {
        $apiConnectionResource.properties.Remove("parameterValueType")
    }
        $apiConnectionResources.Add($apiConnectionResource) | Out-Null

    # Update API connection reference in the playbook resource
    $apiConnectionReference.Value = @{
        "connectionId"= "[resourceId('Microsoft.Web/connections', variables('$connectionVariableName'))]"
        "connectionName" = "[variables('$connectionVariableName')]"
        "id" = "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/$connectorType/$connectionName')]"
        "connectionProperties" = $apiConnectionReference.Value.connectionProperties
    }
    if (!$apiConnectionReference.Value.connectionProperties) {
        $apiConnectionReference.Value.Remove("connectionProperties")
    }
    $playbookResource.dependsOn += "[resourceId('Microsoft.Web/connections', variables('$connectionVariableName'))]"
    
    # Evaluate and add connection-specific parameters
    Foreach ($connectorParameter in $existingConnectorProperties.properties.connectionAlternativeParameters.PSObject.Properties) {
        if ($connectorParameter.Name -eq "authentication" -or $connectorParameter -match "token:") {
            continue
        }

        $matchingConnectionValue = $existingConnectionProperties.properties.alternativeParameterValues.$($connectorParameter.Name)

        $templateParameters.Add($connectorParameter.Name, @{
            "defaultValue"= $matchingConnectionValue
            "type"= $connectorParameter.Value.type
        })
    }
}

function BuildArmTemplate($playbookResource) {
    $armTemplate = @{
        '$schema'= "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
        "contentVersion"= "1.0.0.0"
        "parameters"= $templateParameters
        "variables"= $templateVariables
        "resources"= @($playbookResource)+$apiConnectionResources
    }

    if ($GenerateForGallery) {
        $armTemplate.metadata = @{
            "title"= ""
            "description"= ""
            "prerequisites"= ""
            "prerequisitesDeployTemplateFile"= ""
            "lastUpdateTime"= ""
            "entities"= @()
            "tags"= @()
            "support"= @{
                "tier"= "community" 
            }
            "author"= @{
                "name"= ""
            }
        }
    }

    return $armTemplate
}


$playbookResource = GetPlaybookResource

# Add changes for API connection resources
Foreach ($apiConnectionReference in $playbookResource.properties.parameters.'$connections'.value.PsObject.Properties) {
    HandlePlaybookApiConnectionReference -apiConnectionReference $apiConnectionReference -playbookResource $playbookResource
}

# Create and export the ARM template
$armTemplateOutput = BuildArmTemplate -playbookResource $playbookResource | ConvertTo-Json -Depth 30
$armTemplateOutput = $armTemplateOutput -replace "\\u0027", "'" # ConvertTo-Json escapes quotes, which we don't want
FixJsonIndentation -jsonOutput $armTemplateOutput | Set-Content azuredeploy.json