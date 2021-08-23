param(
    [string]$PlaybookArmId,
    [string]$PlaybookSubscriptionId,
    [string]$PlaybookResourceGroupName,
    [string]$PlaybookResourceName,
    [boolean]$AddGalleryMetadata = $false
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
    $playbookResource.id = $null
    $playbookResource.location = "[resourceGroup().location]"
    $playbookResource.name = "[parameters('PlaybookName')]"
    Add-Member -InputObject $playbookResource -Name "apiVersion" -Value "2017-07-01" -MemberType NoteProperty
    Add-Member -InputObject $playbookResource -Name "dependsOn" -Value @() -MemberType NoteProperty

    # Remove properties specific to an instance of a deployed playbook
    $playbookResource.properties.createdTime = $null
    $playbookResource.properties.changedTime = $null
    $playbookResource.properties.version = $null
    $playbookResource.properties.accessEndpoint = $null

    if ($playbookResource.identity) {
        $playbookResource.identity.principalId = $null
        $playbookResource.identity.tenantId = $null
    }

    return $playbookResource
}

function HandlePlaybookApiConnectionReference($apiConnectionReference, $playbookResource) {
    $connectionName = $apiConnectionReference.Name
    $connectionVariableName = "$($connectionName)ConnectionName"
    $templateVariables.Add($connectionVariableName, "[concat('$connectionName-', parameters('PlaybookName'))]")
    $connectorType = if ($apiConnectionReference.Value.id.ToLowerInvariant().Contains("/managedapis/")) { "managedApis" } else { "customApis" } 
    $connectionAuthenticationType = if ($apiConnectionReference.Value.connectionProperties.authentication.type -eq "ManagedServiceIdentity") { "Alternative" } else  { $null }    
    $existingConnectionProperties = SendArmGetCall -relativeUrl "$($apiConnectionReference.Value.connectionId)?api-version=2016-06-01"
    $existingConnectorProperties = SendArmGetCall -relativeUrl "$($apiConnectionReference.Value.id)?api-version=2016-06-01"

    $apiConnectionResources.Add(@{
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
    }) | Out-Null

    $apiConnectionReference.Value = @{
        "connectionId"= "[resourceId('Microsoft.Web/connections', variables('$connectionVariableName'))]"
        "connectionName" = "[variables('$connectionVariableName')]"
        "id" = "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/$connectorType/$connectionName')]"
        "connectionProperties" = $apiConnectionReference.Value.connectionProperties
    }

    $playbookResource.dependsOn += "[resourceId('Microsoft.Web/connections', variables('$connectionVariableName'))]"
    
    # Evaluate and add connection-specific parameters
    Foreach ($connectorParameter in $existingConnectorProperties.properties.connectionAlternativeParameters.PSObject.Properties) {
        if ($connectorParameter.Name -eq "authentication" -or $connectorParameter -contains "token:") {
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

    if ($AddGalleryMetadata) {
        $armTemplate.metadata = @{
            "title"= ""
            "description"= ""
            "prerequisites"= ""
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