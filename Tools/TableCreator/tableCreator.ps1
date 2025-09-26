<#
.SYNOPSIS
    Creates a new Sentinel table with the same schema as an existing table.

.DESCRIPTION
    This script queries the schema of an existing Sentinel table and creates a new table with the same schema.
    It supports Analytics, Auxiliary/Data Lake, and Basic table types, and allows for retention settings and conversion of dynamic columns to string for Auxiliary/Data Lake tables.
    The script prompts for any missing parameters and can be run interactively or with command-line arguments.

.PARAMETER FullResourceId
    The full resource ID of the Sentinel/Log Analytics Workspace. If not provided, you will be prompted.
    Resource ID can be found in Log Analytics Workspace > JSON View > Copy button.
    To hardcode the Resource ID for your environment, edit the $resourceId variable in the script (line 70).

.PARAMETER tableName
    The name of the existing table to copy the schema from (e.g., SecurityEvent).

.PARAMETER newTableName
    The name of the new table to be created (e.g., MyNewTable_CL). Remember to include the _CL suffix for custom tables.

.PARAMETER type
    The table type: analytics (default), dl/datalake, aux/auxiliary, or basic. 

.PARAMETER retention
    Retention in days for analytics tables (4-730). If not provided, the workspace default is used.

.PARAMETER totalRetention
    Total retention in days for the table. 
    Allowed values: 4-730 days, 1095 (3 yr), 1460 (4 yr), 1826 (5 yr), 2191 (6 yr), 2556 (7 yr), 2922 (8 yr), 3288 (9 yr), 3653 (10 yr), 4018 (11 yr), 4383 (12 yr).

.PARAMETER ConvertToString
    For Auxiliary/Data Lake tables, converts dynamic columns to string. 
    PRO TIP: If the copied table has dynamic columns, you may create it initially as Analytics, and then change to Data Lake later. This will preserve the dynamic types.

.PARAMETER tenantId
    Azure tenant ID. Required only if not running in Azure Cloud Shell.
    Requires the Az PowerShell module installed.

.EXAMPLE
    .\tableCreator.ps1 -tableName MyTable -newTableName MyNewTable_CL -type analytics -retention 180 -totalRetention 365

.EXAMPLE
    .\tableCreator.ps1 -ConvertToString

#>

# Define parameters for the script
param (
    [string]$tenantId,
    [string]$tableName,
    [string]$newTableName,
    [string]$type,
    [int]$retention,
    [int]$totalRetention,
    [switch]$ConvertToString,
    [ValidateScript({
        if ($_ -match '^/subscriptions/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/resourcegroups/[a-zA-Z0-9-_]+/providers/microsoft.operationalinsights/workspaces/[a-zA-Z0-9-_]+$') {
            $true
        } else {
            throw "`n'$_' doesn't look like a valid full resource ID. If provided, it needs to be the full resource ID."
        }
    })]
    [string] $FullResourceId # From Log Analytics Workspace, hit 'JSON View' and then the copy button at the top of the JSON pane.
)

##################################################################################################################
# You can edit this ResourceID to make this script easy to re-use for one environment, 
# or provide -FullResourceId on the command line each time.

$resourceId = "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/YOUR_RESOURCE_GROUP/providers/Microsoft.OperationalInsights/workspaces/YOUR_WORKSPACE_NAME"

# override with whatever the command line said, if it was used.
if($FullResourceId){
    $resourceId = $FullResourceId
}
##################################################################################################################

# Connect Azure Account, no need to run in Cloud Shell, but you do need the Az module installed. 
if ($tenantId) {
    Connect-AzAccount -TenantId $tenantId
}

# Display the banner
Write-Host " +=======================+" -ForegroundColor Green
Write-Host " | tableCreator.ps1 v2.4 |" -ForegroundColor Green
Write-Host " +=======================+" -ForegroundColor Green
Write-Host ""

# Function to repeatedly prompt for input until a valid value is entered
function PromptForInput {
    param (
        [string]$promptMessage
    )

    $inputValue = ""
    while (-not $inputValue) {
        $inputValue = Read-Host -Prompt $promptMessage
        if (-not $inputValue) {
            Write-Host "This value is required. Please provide a valid input."
        }
    }

    return $inputValue
}

# Check if the resourceId is still the default placeholder value
if ($resourceId -eq "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/YOUR_RESOURCE_GROUP/providers/Microsoft.OperationalInsights/workspaces/YOUR_WORKSPACE_NAME") {

    $resourceId = PromptForInput "Enter Sentinel Resource Id"

    # Validate the entered resourceId format
    if ($resourceId -notmatch '^/subscriptions/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/resourcegroups/[a-zA-Z0-9-_]+/providers/microsoft.operationalinsights/workspaces/[a-zA-Z0-9-_]+$') {
        Write-Host "`n'$resourceId' doesn't look like a valid resource id. Please provide the full resource ID in the correct format." -ForegroundColor Red
        Write-Host "(format: /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/microsoft.operationalinsights/workspaces/<workspace-name>)" -ForegroundColor Red
        exit
    }
}

# Prompt for input if necessary
if (-not $tableName) {
    $tableName = PromptForInput "Enter Table Name to get Schema from"
} 

if (-not $newTableName) {
    $newTableName = PromptForInput "Enter new Table Name to be created with the same Schema (remember _CL -suffix)"
}

# Prompt for table type, defaulting to 'analytics' if not provided
if (-not $type) {
    $type = Read-Host -Prompt "Enter table type (analytics, dl/datalake, aux/auxiliary or basic, or press Enter for default 'analytics')"
}

$datalake = $false

if ($type.ToLower() -eq "datalake" -or $type.ToLower() -eq "dl") {
    $datalake = $true
    $type = "auxiliary"
}

if ($type.ToLower() -eq "aux") { $type = "auxiliary" }

# Define an array of valid types
$validTypes = @("auxiliary", "basic", "analytics")

$type = $type.ToLower()

# If $type is not valid, default it to 'analytics'
if (-not $type -or -not ($validTypes -contains $type)) {
    $type = 'analytics'
    Write-Host "Invalid or no table type provided. Defaulting to 'analytics'."
}

# Prompt for retention values if not provided
if (-not $retention -and $type -eq "analytics") {
    $retention = Read-Host -Prompt "Enter analytics retention in days (4-730) or press Enter for workspace default"
}

if (-not $totalRetention) {
    if ($type -ne "analytics") {
        Write-Host "Allowed values for total retention: 30-730 days, 1095 (3 yr), 1460 (4 yr), 1826 (5 yr), 2191 (6 yr), 2556 (7 yr), 2922 (8 yr), 3288 (9 yr), 3653 (10 yr), 4018 (11 yr), 4383 (12 yr)"
    } else {
        Write-Host "Allowed values for total retention: $retention-730 days, 1095 (3 yr), 1460 (4 yr), 1826 (5 yr), 2191 (6 yr), 2556 (7 yr), 2922 (8 yr), 3288 (9 yr), 3653 (10 yr), 4018 (11 yr), 4383 (12 yr)"
    }
    $totalRetention = Read-Host -Prompt "Enter total retention in days or press Enter for table default"
}

# Set query to get the schema of the specified table
$query = "$tableName | getschema | project ColumnName, ColumnType"

# Query the workspace to get the schema
Write-Host "[Querying $tableName table schema...]"

# Construct the request body
$body = @{
    query = $query
} | ConvertTo-Json -Depth 2

$response = Invoke-AzRestMethod -Path "$resourceId/query?api-version=2017-10-01" -Method POST  -Payload $body

# Convert Content from JSON string to PowerShell object
$data = $response.Content | ConvertFrom-Json

# Check if the response is successful
if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 202) {
    Write-Host "[Table schema successfully captured]"
}
else {
    # Output error details if the creation failed
    Write-Host "[Error] Failed to query the table '$TableName'. Status code: $($response.StatusCode)" -ForegroundColor Red

    exit
}

# do the mapping to queryResult
$columns = $data.tables[0].columns
$rows = $data.tables[0].rows

$queryResult = $rows | ForEach-Object {
    $object = @{}
    for ($i = 0; $i -lt $columns.Count; $i++) {
        $object[$columns[$i].name] = $_[$i]
    }
    [pscustomobject]$object
}

## Prepare an array to hold names of columns converted to string
$StringList = @()

# Exclude specific columns by name and prepare the columns for tableParams
$columns = $queryResult | Where-Object {
    $_.ColumnName -notin @("TenantId", "Type", "Id", "MG")
} | ForEach-Object {

    ## Aux/datalake uses column type boolean istead of bool
    if ($type -eq "auxiliary" -and $_.ColumnType -eq "bool") { 
        $_.ColumnType = "boolean" 
    }

    # Check if the column type is dynamic and if ConvertToString is set
    if ($type -eq "auxiliary" -and $_.ColumnType -eq "dynamic") {
        if ($ConvertToString) { 

            $StringList += $_.ColumnName  # Add to array for later processing

            $_.ColumnName = $_.ColumnName + "_str"
            $_.ColumnType = "string"

            #Write-Host "[DEBUG - CONVERTED $($_.ColumnName) - $($_.ColumnType)"        
        } 
    }

    # Check if the table name is "SecurityEvent" and specific columns which are type guid. Getschema fails to report these properly, so it needs some manual intervention.
    if ($_.ColumnName -in @("InterfaceUuid", "LogonGuid", "SourceComputerId", "SubcategoryGuid", "TargetLogonGuid") -and $tableName -eq "SecurityEvent") {
        $_.ColumnType = "guid"
    }
    # Check if the table name is "SigninLogs" and specific columns which are type guid. Getschema fails to report these properly, so it needs some manual intervention.
    if ($_.ColumnName -in @("OriginalRequestId") -and $tableName -eq "SigninLogs") {
        $_.ColumnType = "guid"
    }

     ## Aux do not support dynamic tables
    if ($type -eq "auxiliary" -and $_.ColumnType -eq "dynamic" -and !($ConvertToString)) {

        # Log the skipping message
        Write-Host "[SKIPPING $($_.ColumnName) due to Dynamic type which is not supported by Data lake/Auxiliary table, use -ConvertToString to convert it to String]" -ForegroundColor Yellow

    } else {
        # Include the column in the result
        @{
            "name" = $_.ColumnName
            "type" = $_.ColumnType
        }
        #Write-Host "[DEBUG - INCL $($_.ColumnName) - $($_.ColumnType)"

    }

}

# Construct the base tableParams for the new table
$tableParams = @{
    "properties" = @{
        "schema" = @{
            "name"    = $newTableName
            "columns" = $columns
        }
    }
}

# Normalize the type input and add details if set
switch ($type.ToLower()) {
    "auxiliary" {
        $tableParams.properties.plan = "Auxiliary"

        if ($datalake) {
            Write-Host "[Plan set to Data Lake]"
        } else {
            Write-Host "[Plan set to Auxiliary]"
            Write-Host "[Interactive retention is set to 30 days]"
        }

    }
    "analytics" {
        $tableParams.properties.plan = "Analytics"
        Write-Host "[Plan set to Analytics]"
        if ($retention -ge 4 -and $retention -le 730) {
            $tableParams.properties.retentionInDays = $retention
            Write-Host "[Analytics retention set to $retention days]"
        }
    }
    "basic" {
        $tableParams.properties.plan = "Basic"
        Write-Host "[Plan set to Basic]"
        Write-Host "[Interactive retention is set to 30 days]"
    }
    default {
        Write-Host "Invalid type provided. Using default 'analytics'."
        $tableParams.properties.plan = "Analytics"
        Write-Host "[Plan set to Analytics]"
        if ($retention -ge 4 -and $retention -le 730) {
            $tableParams.properties.retentionInDays = $retention
            Write-Host "[Analytics retention set to $retention days]"
        }
    }
}

# Set totalRetentionInDays based on the input condition
if ($totalRetention -ge 4 -and $totalRetention -le 4383) { 
    $tableParams.properties.totalRetentionInDays = $totalRetention 
    Write-Host "[Total retention set to $totalRetention days]"    
} 

# Convert tableParams to JSON for the API call
$tableParamsJson = $tableParams | ConvertTo-Json -Depth 10
#Write-Host "$tableParamsJson"

Write-Host "[Initiating new table $newTableName creation (or updating if it exists) with the same schema as in $tableName]"

# Create the new Sentinel table
$response = Invoke-AzRestMethod -Path "$resourceId/tables/${newTableName}?api-version=2023-01-01-preview" -Method PUT -Payload $tableParamsJson

# Check if the response is successful
if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 202) {
    Write-Host "[Success] Table '$newTableName' created successfully with status code: $($response.StatusCode)" -ForegroundColor Green
}
else {
    # Output error details if the creation failed
    Write-Host "[Error] Failed to create table '$newTableName'. Status code: $($response.StatusCode)" -ForegroundColor Red
    
    # Convert Content from JSON string to PowerShell object
    $content = $response.Content | ConvertFrom-Json

    # Check if the error object is present and output the message
    if ($content.error) {
        Write-Host "[Error] Code: $($content.error.code)" -ForegroundColor Red
        Write-Host "[Error] Message: $($content.error.message)" -ForegroundColor Red
    }
    else {
        Write-Host "[Error] No detailed error information available." -ForegroundColor Red
    }
}

# Check if there are any columns to converted to string and output the transformation KQL
if ($StringList) {
    $extendParts = ""
    foreach ($col in $StringList) {
        $newCol = $col + "_str"
        $extendParts += "$newCol = tostring($col), "
    }
    $transformKql = "source | extend $extendParts"
    $transformKql = $transformKql.Substring(0, $transformKql.Length - 2)
    Write-Host ""
    Write-Host "NOTICE: There were Dynamic columns in the table and they were converted to String (as requested). Please include this in the DCR:" -ForegroundColor Yellow
    Write-Host "`"transformKql`": `"$transformKql`"" -ForegroundColor Yellow
}
