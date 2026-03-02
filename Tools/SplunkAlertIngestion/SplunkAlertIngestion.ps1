param (
    [Parameter(Mandatory = $true)]
    [string]$ServicePrincipalName,
    [Parameter(Mandatory = $true)]
    [string]$tableName,
    [Parameter(Mandatory = $true)]
    [string]$workspaceResourceId,
    [Parameter(Mandatory = $true)]
    [string]$dataCollectionRuleName,
    [Parameter(Mandatory = $true)]
    [string]$location,
    [Parameter(Mandatory = $false)]
    [string]$LogicAppName = "SplunkAlertAutomationLogicApp"
    
)

$resourceGroupName = $workspaceResourceId.Split('/')[4]
$subscription = $workspaceResourceId.Split('/')[2]

# Check if Az module is installed
if (Get-Module -ListAvailable -Name Az) {
    Write-Host "Az module is installed."

    Select-AzSubscription $subscription

    # Create a new service principal
    $sp = New-AzADServicePrincipal -DisplayName $ServicePrincipalName

    # Create a new service principal and retrieve its secret
    $spCredential = New-AzADSpCredential -ObjectId $sp.Id -EndDate (Get-Date).AddYears(1)
    $spSecret = $spCredential.SecretText

    $secureSpSecret = ConvertTo-SecureString $spSecret -AsPlainText -Force

    Write-Host "Service Principal created:"
    Write-Host "AppId: $($sp.AppId)"
    Write-Host "DisplayName: $($sp.DisplayName)"
    Write-Host "Secret: $spSecret"

} else {
    Write-Host "Az module is not installed. Please install it using:"
    Write-Host "Install-Module -Name Az -Scope CurrentUser -Repository PSGallery -Force"
}

# Get the tenant ID from the current context
$tenantId = (Get-AzContext).Tenant.Id


$tableName = "$tableName"  # Custom tables must end with '_CL'
$columns = @(
    @{
        name = "TimeGenerated"; type = "datetime"
    },
    @{
        name = "app"; type = "string"
    },
    @{
        name = "owner"; type = "string"
    },
    @{
        name = "result"; type = "dynamic"
    },
    @{
        name = "results_link"; type = "string"
    },
    @{
        name = "search_name"; type = "string"
    },
    @{
        name = "sid"; type = "string"
    }
)

# Create the table schema
$tableSchema = @{
    properties = @{
        schema = @{
            name = $tableName
            columns = $columns
        }
    }
}

# Convert schema to JSON
$tableSchemaJson = $tableSchema | ConvertTo-Json -Depth 10 -Compress


$fullPath = "$($workspaceResourceId)/tables/$($tableName)?api-version=2022-10-01"

#deploying the table schema
try{
    Write-Host "Deploying table schema for $tableName in $workspaceResourceId"
Invoke-AzRestMethod -Path "$fullPath" -Method PUT -payload $tableSchemaJson
    Write-Host "Table schema deployed successfully."
} catch {
    Write-Host "Failed to deploy table schema: $($_.Exception.Message)"
}

#deploying the data collection rule
try{
    Write-Host "Deploying data collection rule $dataCollectionRuleName in resource group $resourceGroupName"
New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName -TemplateFile "./DCR.json" -dataCollectionRuleName $dataCollectionRuleName -location $location -workspaceResourceId $workspaceResourceId -tableName $tableName
    Write-Host "Data collection rule deployed successfully."

    $dcr = (Get-AzDataCollectionRule -ResourceGroupName $resourceGroupName -Name $dataCollectionRuleName)
    $immutableId = $dcr.ImmutableId
    
} catch {
    Write-Host "Failed to deploy data collection rule: $($_.Exception.Message)"
}

try{
#assigning roles to newly created DCR
$roleDefinition = Get-AzRoleDefinition -Name "Monitoring Metrics Publisher"
$roleDefinitionId = $roleDefinition.Id

$getResource = Get-AzResource -Name $dataCollectionRuleName -ResourceGroupName $resourceGroupName -ExpandProperties
$getResourceId = $getResource.ResourceId
$getDcrIngestionEndpoint = $getResource.Properties.endpoints.logsIngestion
Write-Host "Assigning role 'Monitoring Metrics Publisher' to Service Principal $($sp.DisplayName) for Data Collection Rule $dataCollectionRuleName."
New-AzRoleAssignment -ObjectId $sp.Id -RoleDefinitionId $roleDefinitionId -Scope $getResourceId
Write-Host "Role 'Monitoring Metrics Publisher' assigned to Service Principal $($sp.DisplayName) for Data Collection Rule $dataCollectionRuleName."
} catch {
    Write-Host "Failed to assign role: $($_.Exception.Message)"
}

# Create the Logic App workflow
try{
    Write-Host "Creating Logic App workflow $LogicAppName in resource group $resourceGroupName"
    New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName -TemplateFile "./LogicApp.json" -workflowName $LogicAppName -location $location -tenantId $tenantId -clientId $sp.AppId -clientSecret $secureSpSecret -immutableId $immutableId -dcrIngestionEndpoint $getDcrIngestionEndpoint -tableName $tableName
    Write-Host "Logic App workflow $LogicAppName created successfully in resource group $resourceGroupName."

    $trigger = Get-AzLogicAppTriggerCallbackUrl -ResourceGroupName "secops" -Name "dcrDemo" -TriggerName "When_a_HTTP_request_is_received"
    $triggerUrl = $trigger.Value

    Write-Host "Logic App Trigger URL: $triggerUrl"
} catch {
    Write-Host "Failed to create Logic App workflow: $($_.Exception.Message)"
}
