<#
.SYNOPSIS
    Copy-AzOperationalInsightsTable is a function that copies a table from one Azure Monitor workspace to another.

.DESCRIPTION
    This function copies a table from a source Azure Monitor workspace to a target Azure Monitor workspace. It creates a new table in the target workspace with the same schema and data as the source table.

.PARAMETER WorkspaceResourceId
    Specifies the resource ID of the target Azure Monitor workspace where the table will be copied to.

.PARAMETER SourceTableName
    Specifies the name of the existing (source) table that will be copied.

.PARAMETER TargetTableName
    Specifies the name of the target table in the target workspace. If not provided, the function will append "_CL" to the source table name to create the target table name.

.PARAMETER TablePlan
    Specifies the plan for the target table. Valid values are "Analytics" and "Basic". Default value is "Basic".

.EXAMPLE
    Copy-AzOperationalInsightsTable -WorkspaceResourceId "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/myWorkspace" -SourceTableName "AADNonInteractiveUserSignInLogs" -TablePlan "Basic"

    This example copies the table "AADNonInteractiveUserSignInLogs" to a custom log in the same workspace. The name defaults to "AADNonInteractiveUserSignInLogs_CL" with the default selected table plan "Basic".


.EXAMPLE
    Copy-AzOperationalInsightsTable -WorkspaceResourceId "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/myWorkspace" -SourceTableName "AADNonInteractiveUserSignInLogs" -TargetTableName "AADNonInteractiveUserSignInLogs_Custom_CL" -TablePlan "Analytics"

    This example copies the table "AADNonInteractiveUserSignInLogs" to a custom log named "AADNonInteractiveUserSignInLogs_Custom_CL" with the selected table plan "Analytics".

.NOTES
    This function requires the Az module to be installed. You can install it by running 'Install-Module -Name Az' in PowerShell.
#>
function Copy-AzOperationalInsightsTable {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceResourceId,

        [Parameter(Mandatory = $true)]
        [string]$SourceTableName,
        
        # Optional Parameter
        [Parameter(Mandatory = $false)]
        [ValidatePattern('^[a-zA-Z][a-zA-Z0-9_]{0,44}_CL$')]
        [string]$TargetTableName,

        [Parameter(Mandatory = $false)]
        [ValidateSet('Analytics', 'Basic')]
        [string]$TablePlan = "Basic"
    )

    try {
        $workspace = Get-AzResource -ResourceId $WorkspaceResourceId -erroraction stop
        Write-Information "Workspace exists"
    }
    catch {
        write-error "Please ensure you have the right workspace resource id, subscription context and permissions to access the workspace"
        break
    }

    # List the Parameters with Write-Information
    Write-Information "Workspace Resource Id: $WorkspaceResourceId"
    Write-Information "Source Table Name: $SourceTableName"
    
    
    # Set Target Table Name if not provided    
    if (-not $TargetTableName) {
        $TargetTableName = $SourceTableName + "_CL"
        Write-Information "Target Table Name not provided as parameter. Defaulting to $TargetTableName"
    }
    else {
        Write-Information "Target Table Name: $TargetTableName"
    }


    # Get Source Table and throw error if it does not exist
    try {
        $SourceTable = Get-AzOperationalInsightsTable -ResourceGroupName $Workspace.ResourceGroupName -WorkspaceName $Workspace.Name -TableName $SourceTableName -ErrorAction Stop
        Write-Information "Source Table $SourceTableName exists in the workspace"
    }
    catch {
        write-error "Source Table $SourceTableName does not exist in the workspace"
        break
    }

    # Get the new table and throw error if it already exists
    try {
        $Table = Get-AzOperationalInsightsTable -ResourceGroupName $Workspace.ResourceGroupName -WorkspaceName $Workspace.Name -TableName $NewTableName -ErrorAction Stop
        write-error "Target Table $TargetTableName already exists in the workspace"
        break
    }
    catch {
        Write-Information "Target Table $TargetTableName does not exist in the workspace"
    }

    # Checks passed
    Write-Information "Copying Table $SourceTableName to $TargetTableName"

    $DisallowedCustomColumninCustomTables = @("_ResourceId", "id", "_SubscriptionId", "TenantId", "Type", "UniqueId", "Title")

    if ($SourceTable.schema.TableType -eq "Microsoft") { 
        $TableSchemaColumns = $SourceTable.Schema.StandardColumns | Where-Object Name -notin $DisallowedCustomColumninCustomTables
    }
    else {
        $TableSchemaColumns = $SourceTable.Schema.Columns  | Where-Object Name -notin $DisallowedCustomColumninCustomTables
    }
    
    $TableProperties = @{
        properties = @{
            schema = @{
                name    = $TargetTableName
                columns = $TableSchemaColumns
            }
            plan   = $TablePlan
        }
    } | ConvertTo-Json -Depth 10

    $TargetTablePath = "$WorkspaceResourceId/tables/$TargetTableName" + "?api-version=2022-10-01"

    Write-Information "Creating Table $TargetTableName in the workspace"
    Write-Information "Target Table Path: $TargetTablePath"
    Write-Verbose "Table Properties:\n$TableProperties"

    $Request = Invoke-AzRestMethod -Path $TargetTablePath -Method Put -Payload  $TableProperties -erroraction stop

    if ($Request.StatusCode -in @(200,201)) {
        Write-Information "Table $TargetTableName created successfully"
        $Table = Get-AzOperationalInsightsTable -ResourceGroupName $Workspace.ResourceGroupName -WorkspaceName $Workspace.Name -TableName $TargetTableName -ErrorAction SilentlyContinue
        return $Table
    }
    elseif ($Request.StatusCode -eq 202) {
        Write-Information "Table $TargetTableName is being created. Polling for success status for 60 seconds"

        # Poll for the table creation status everyy 10 seconds for 60 seconds
        $i = 0
        do {
            $Table = Get-AzOperationalInsightsTable -ResourceGroupName $Workspace.ResourceGroupName -WorkspaceName $Workspace.Name -TableName $TargetTableName -ErrorAction SilentlyContinue
            if ($Table.ProvisioningState -eq "Succeeded") {
                Write-Information "Table $TargetTableName created successfully"
                return $Table
            }
            else {
                Start-Sleep -Seconds 10
                $i++
            }
        } while ($i -lt 6)
    }
    else {
        write-error "Failed to get table status after 60 seconds. Please check the status of the table creation manually"
        $Request.Content
    } 
}
