<#
.SYNOPSIS
Create DCRs for custom tables and ingest CSV telemetry using the Azure Monitor Logs Ingestion API.

.DESCRIPTION
This script scans the custom Telemetry folder for CSVs (custom tables),
creates DCR templates that match the CSV schema, optionally deploys DCE/DCR resources, and
ingests the data using the Logs Ingestion API.

Built-in tables can be ingested by either providing an existing DCR immutable ID or by
creating a DCR per built-in table with -DeployBuiltInDcr.

.REQUIREMENTS
- Azure CLI (az) installed and authenticated.
- Permissions to create Data Collection Endpoint/Rules and ingest data.

.PARAMETER SubscriptionId
Azure subscription ID.

.PARAMETER ResourceGroupName
Resource group containing the Log Analytics workspace and DCR/DCE resources.

.PARAMETER Location
Azure region for DCE/DCR resources (e.g., eastus). Optional - when omitted the
script automatically uses the location of the Log Analytics workspace.

.PARAMETER WorkspaceName
Log Analytics workspace name. Used to resolve the workspace resource ID when not provided.

.PARAMETER WorkspaceResourceId
Full resource ID of the Log Analytics workspace (optional).

.PARAMETER DceName
Data Collection Endpoint name (created if not exists).

.PARAMETER DcrPrefix
Prefix for DCR names (one DCR per custom table).

.PARAMETER TelemetryPath
Path to the custom telemetry CSV folder.

.PARAMETER BuiltInTelemetryPath
Path to the built-in telemetry CSV folder (optional).

.PARAMETER TemplatesOutputPath
Folder where DCR JSON templates will be written.

.PARAMETER Deploy
When specified, creates DCE/DCR resources in Azure.

.PARAMETER Ingest
When specified, ingests CSV rows using the Logs Ingestion API.

.PARAMETER AssigneeObjectId
Optional Entra ID object ID to grant the Monitoring Metrics Publisher role on each DCR for ingestion.

.PARAMETER TenantId
Microsoft Entra tenant ID for service principal authentication (optional).

.PARAMETER ClientId
Service principal application (client) ID for ingestion auth (optional).

.PARAMETER ClientSecret
Service principal client secret for ingestion auth (optional).

.PARAMETER BuiltInDcrImmutableId
Immutable ID of an existing DCR configured for built-in table ingestion (optional).

.PARAMETER BuiltInDcrPrefix
Prefix for built-in table DCR names created with -DeployBuiltInDcr.

.PARAMETER BuiltInStreamPrefix
Prefix for the input stream when ingesting with -BuiltInDcrImmutableId (defaults to Custom-).

.PARAMETER DeployBuiltInDcr
When specified, creates DCRs for built-in tables based on CSV schemas.

.PARAMETER BuiltInTableMapPath
Path to a JSON file that maps CSV file names to built-in table names (optional).

.PARAMETER BuiltInIngestionEndpoint
Logs ingestion endpoint to use for the built-in DCR (optional). If not set, uses the DCE endpoint.

.PARAMETER BuiltInOnly
When specified, skips custom table processing and runs only built-in table handling.

.PARAMETER CustomTableFilter
Optional list of custom table base names or CSV file names to process (e.g., CommonSecurityLog_CL).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [string]$Location,

    [Parameter(Mandatory = $true)]
    [string]$WorkspaceName,

    [string]$WorkspaceResourceId,

    [string]$DceName = "sentinel-training-dce",

    [string]$DcrPrefix = "sentinel-training-",

    [string]$TelemetryPath,

    [string]$BuiltInTelemetryPath,

    [string]$TemplatesOutputPath,

    [switch]$Deploy,

    [switch]$Ingest,

    [string]$AssigneeObjectId,

    [string]$TenantId,

    [string]$ClientId,

    [string]$ClientSecret,

    [string]$BuiltInDcrImmutableId,

    [string]$BuiltInDcrPrefix = "sentinel-training-builtin-",

    [string]$BuiltInStreamPrefix = "Custom-",

    [string]$BuiltInTableMapPath,

    [string]$BuiltInIngestionEndpoint,

    [switch]$DeployBuiltInDcr,

    [switch]$BuiltInOnly,

    [string[]]$CustomTableFilter
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $TelemetryPath) {
    $basePath = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
    $TelemetryPath = Join-Path -Path $basePath -ChildPath "..\Telemetry\Custom"
}

if (-not $BuiltInTelemetryPath) {
    $basePath = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
    $BuiltInTelemetryPath = Join-Path -Path $basePath -ChildPath "..\Telemetry\BuildIn"
}

if (-not $TemplatesOutputPath) {
    $basePath = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
    $TemplatesOutputPath = Join-Path -Path $basePath -ChildPath "..\DCRTemplates"
}

function Assert-AzCli {
    try {
        $null = Get-Command az -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Get-ManagementAccessToken {
    if (Assert-AzCli) {
        return (az account get-access-token --resource "https://management.azure.com/" --query accessToken -o tsv)
    }

    if (-not (Get-Module -ListAvailable -Name Az.Accounts)) {
        throw "Az.Accounts module is required when Azure CLI is unavailable."
    }

    Import-Module Az.Accounts -ErrorAction Stop
    $token = (Get-AzAccessToken -ResourceUrl "https://management.azure.com/").Token
    if (-not $token) {
        throw "Failed to acquire management access token."
    }
    return $token
}

function Invoke-ArmRest {
    param(
        [string]$Method,
        [string]$Uri,
        [string]$JsonBody
    )

    if (Assert-AzCli) {
        if ($Method -eq "GET") {
            $prevEA = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            $output = az rest --method get --uri $Uri 2>&1
            $exitCode = $LASTEXITCODE
            $ErrorActionPreference = $prevEA
            if ($exitCode -ne 0) {
                $errorOutput = ($output | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] }) -join "`n"
                throw "az rest GET failed with exit code $exitCode for ${Uri}: $errorOutput"
            }
            $jsonText = ($output | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] }) -join "`n"
            return $jsonText | ConvertFrom-Json
        }
        if (-not $JsonBody -or -not $JsonBody.Trim()) {
            throw "Request body is empty."
        }
        $tempFile = [System.IO.Path]::GetTempFileName()
        try {
            $JsonBody | Out-File -FilePath $tempFile -Encoding utf8
            $prevEA = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            $output = az rest --method put --uri $Uri --headers "Content-Type=application/json" --body "@$tempFile" 2>&1
            $exitCode = $LASTEXITCODE
            $ErrorActionPreference = $prevEA
            if ($exitCode -ne 0) {
                $errorOutput = ($output | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] }) -join "`n"
                throw "az rest PUT failed with exit code $exitCode for ${Uri}: $errorOutput"
            }
        } finally {
            Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
        }
        return $null
    }

    $headers = @{ Authorization = "Bearer $(Get-ManagementAccessToken)" }
    if ($Method -eq "GET") {
        return Invoke-RestMethod -Method Get -Uri $Uri -Headers $headers
    }

    if (-not $JsonBody -or -not $JsonBody.Trim()) {
        throw "Request body is empty."
    }
    $headers["Content-Type"] = "application/json"
    return Invoke-RestMethod -Method Put -Uri $Uri -Headers $headers -Body $JsonBody
}

function Read-TelemetryData {
    param(
        [string]$Path
    )

    $extension = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
    if ($extension -eq ".json") {
        $raw = Get-Content -Path $Path -Raw
        if (-not $raw) {
            return @()
        }
        $data = $raw | ConvertFrom-Json
        if ($null -eq $data) {
            return @()
        }
        if ($data -is [System.Array]) {
            return @($data)
        }
        return @($data)
    }

    return @(Import-Csv -Path $Path)
}

function Invoke-AzRestPutJson {
    param(
        [string]$Uri,
        [string]$JsonBody
    )

    $null = Invoke-ArmRest -Method "PUT" -Uri $Uri -JsonBody $JsonBody
}

function Get-AccessToken {
    param(
        [string]$TenantId,
        [string]$ClientId,
        [string]$ClientSecret
    )

    if ($TenantId -and $ClientId -and $ClientSecret) {
        $tokenUri = "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token"
        $body = @{
            client_id     = $ClientId
            client_secret = $ClientSecret
            grant_type    = "client_credentials"
            scope         = "https://monitor.azure.com/.default"
        }
        $response = Invoke-RestMethod -Method Post -Uri $tokenUri -Body $body -ContentType "application/x-www-form-urlencoded"
        if (-not $response.access_token) {
            throw "Failed to acquire access token using service principal."
        }
        return $response.access_token
    }

    if (Assert-AzCli) {
        $token = az account get-access-token --resource "https://monitor.azure.com/" --query accessToken -o tsv
    } else {
        if (-not (Get-Module -ListAvailable -Name Az.Accounts)) {
            throw "Az.Accounts module is required when Azure CLI is unavailable."
        }
        Import-Module Az.Accounts -ErrorAction Stop
        $token = (Get-AzAccessToken -ResourceUrl "https://monitor.azure.com/").Token
    }
    if (-not $token) {
        throw "Failed to acquire access token. Ensure you're logged in with 'az login' or provide service principal credentials."
    }
    return $token
}

function Resolve-WorkspaceInfo {
    param(
        [string]$WorkspaceName,
        [string]$ResourceGroupName,
        [string]$SubscriptionId
    )

    $apiVersion = "2022-10-01"
    $uri = "https://management.azure.com/subscriptions/${SubscriptionId}/resourceGroups/${ResourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/${WorkspaceName}?api-version=${apiVersion}"
    $workspace = Invoke-ArmRest -Method "GET" -Uri $uri
    if (-not $workspace -or -not $workspace.id) {
        throw "Unable to resolve workspace. Check the workspace name and resource group."
    }
    return @{
        Id       = $workspace.id
        Location = $workspace.location
    }
}

function Initialize-CustomTable {
    param(
        [string]$WorkspaceResourceId,
        [string]$TableName,
        [string[]]$Columns
    )

    $apiVersion = "2022-10-01"
    $tableUri = "https://management.azure.com${WorkspaceResourceId}/tables/${TableName}?api-version=$apiVersion"

    try {
        $table = Invoke-ArmRest -Method "GET" -Uri $tableUri
        if ($table.properties.provisioningState -eq "Succeeded") {
            $existingColumns = Get-TableSchemaColumns -WorkspaceResourceId $WorkspaceResourceId -TableName $TableName
            $existingNames = @($existingColumns | ForEach-Object { $_.name })
            $desiredNames = @("TimeGenerated") + ($Columns | Where-Object { $_ -ne "TimeGenerated" })
            $missing = @($desiredNames | Where-Object { $existingNames -notcontains $_ })
            if ($missing.Count -eq 0) {
                return
            }

            $schemaColumns = @(
                foreach ($col in $existingColumns) {
                    @{
                        name        = $col.name
                        type        = $col.type
                        description = $col.description
                    }
                }
            )

            foreach ($col in $missing) {
                $schemaColumns += @{
                    name        = $col
                    type        = "string"
                    description = "Auto-generated column"
                }
            }

            $body = @{
                properties = @{
                    schema = @{
                        name    = $TableName
                        columns = $schemaColumns
                    }
                }
            } | ConvertTo-Json -Depth 20 -Compress

            Write-Host "Updating schema for custom table '$TableName' with $($missing.Count) new columns..."
            Invoke-AzRestPutJson -Uri $tableUri -JsonBody $body

            for ($i = 0; $i -lt 10; $i++) {
                Start-Sleep -Seconds 5
                try {
                    $table = Invoke-ArmRest -Method "GET" -Uri $tableUri
                    if ($table.properties.provisioningState -eq "Succeeded") {
                        return
                    }
                } catch {
                    # keep waiting
                }
            }

            throw "Custom table '$TableName' did not reach Succeeded provisioning state after schema update."
        }
    } catch {
        # Table does not exist; create it below.
    }

    $schemaColumns = @(
        @{
            name        = "TimeGenerated"
            type        = "datetime"
            description = "The time at which the data was generated"
        }
    )

    foreach ($col in $Columns) {
        if ($col -eq "TimeGenerated") {
            continue
        }
        $schemaColumns += @{
            name        = $col
            type        = "string"
            description = "Auto-generated column"
        }
    }

    $body = @{
        properties = @{
            schema = @{
                name    = $TableName
                columns = $schemaColumns
            }
        }
    } | ConvertTo-Json -Depth 20 -Compress

    Invoke-AzRestPutJson -Uri $tableUri -JsonBody $body

    for ($i = 0; $i -lt 10; $i++) {
        Start-Sleep -Seconds 5
        try {
            $table = Invoke-ArmRest -Method "GET" -Uri $tableUri
            if ($table.properties.provisioningState -eq "Succeeded") {
                return
            }
        } catch {
            # keep waiting
        }
    }

    throw "Custom table '$TableName' did not reach Succeeded provisioning state."
}

function Initialize-Dce {
    param(
        [string]$SubscriptionId,
        [string]$ResourceGroupName,
        [string]$Location,
        [string]$DceName
    )

    $dceId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/dataCollectionEndpoints/$DceName"
    $apiVersion = "2022-06-01"
    $dce = $null

    try {
        $dce = Invoke-ArmRest -Method "GET" -Uri "https://management.azure.com${dceId}?api-version=$apiVersion"
    } catch {
        $dce = $null
    }

    if (-not $dce) {
        Write-Host "Creating Data Collection Endpoint '$DceName'..."
        $body = @{
            location   = $Location
            properties = @{
                description = "Sentinel training lab ingestion endpoint"
                networkAcls = @{
                    publicNetworkAccess = "Enabled"
                }
            }
        } | ConvertTo-Json -Depth 10 -Compress

        Invoke-AzRestPutJson -Uri "https://management.azure.com${dceId}?api-version=$apiVersion" -JsonBody $body
        $dce = Invoke-ArmRest -Method "GET" -Uri "https://management.azure.com${dceId}?api-version=$apiVersion"
    }

    return $dce
}

function New-DcrTemplate {
    param(
        [string]$TableName,
        [string[]]$Columns,
        [string]$WorkspaceResourceId,
        [string]$DceResourceId,
        [string]$Location,
        [string]$TransformKql
    )

    $baseName = $TableName.Substring(0, $TableName.Length - 3)
    $streamName = "Custom-$baseName"
    $outputStream = "Custom-$TableName"

    $columnDefinitions = @(
        foreach ($col in $Columns) {
            @{
                name = $col
                type = "string"
            }
        }
    )

    $transformKql = if ($TransformKql) {
        $TransformKql
    } elseif ($Columns -contains "TimeGenerated") {
        "source"
    } else {
        "source | extend TimeGenerated = now()"
    }

    $template = @{
        location   = $Location
        kind       = "Direct"
        properties = @{
            dataCollectionEndpointId = $DceResourceId
            streamDeclarations       = @{
                $streamName = @{
                    columns = $columnDefinitions
                }
            }
            destinations = @{
                logAnalytics = @(
                    @{
                        name = "la"
                        workspaceResourceId = $WorkspaceResourceId
                    }
                )
            }
            dataFlows = @(
                @{
                    streams      = @($streamName)
                    destinations = @("la")
                    transformKql = $transformKql
                    outputStream = $outputStream
                }
            )
        }
    }

    return $template
}

function Initialize-Dcr {
    param(
        [string]$DcrName,
        [string]$SubscriptionId,
        [string]$ResourceGroupName,
        [hashtable]$Template
    )

    $apiVersion = "2023-03-11"
    $dcrId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/dataCollectionRules/$DcrName"
    $body = $Template | ConvertTo-Json -Depth 20 -Compress

    Invoke-AzRestPutJson -Uri "https://management.azure.com${dcrId}?api-version=$apiVersion" -JsonBody $body
    return $dcrId
}

function Get-DcrImmutableId {
    param(
        [string]$DcrId
    )

    $apiVersion = "2023-03-11"
    $dcr = Invoke-ArmRest -Method "GET" -Uri "https://management.azure.com${DcrId}?api-version=$apiVersion"
    return $dcr.properties.immutableId
}

function Get-TableSchemaColumns {
    param(
        [string]$WorkspaceResourceId,
        [string]$TableName
    )

    $apiVersion = "2022-10-01"
    $tableUri = "https://management.azure.com${WorkspaceResourceId}/tables/${TableName}?api-version=$apiVersion"
    $table = Invoke-ArmRest -Method "GET" -Uri $tableUri
    $schema = $table.properties.schema
    if ($schema -and ($schema.PSObject.Properties.Match('columns').Count -gt 0) -and $schema.columns) {
        return $schema.columns
    }
    if ($schema -and ($schema.PSObject.Properties.Match('standardColumns').Count -gt 0) -and $schema.standardColumns) {
        return $schema.standardColumns
    }
    return @()
}

function Get-JsonByteCount {
    param([string]$Json)
    return [System.Text.Encoding]::UTF8.GetByteCount($Json)
}

function Format-ColumnName {
    param(
        [string]$Name,
        [switch]$AllowReserved
    )

    $normalized = if ($null -ne $Name) { $Name.Trim() } else { "" }
    $normalized = [regex]::Replace($normalized, "[^A-Za-z0-9_]", "_")
    if (-not $normalized) {
        $normalized = "C"
    }
    if ($normalized -notmatch "^[A-Za-z]" ) {
        $normalized = "C_$normalized"
    }
    if ($normalized.Length -gt 45) {
        $normalized = $normalized.Substring(0, 45)
    }
    if (-not $AllowReserved) {
        $reserved = @("_ResourceId", "id", "_SubscriptionId", "TenantId", "Type", "UniqueId", "Title")
        if ($reserved -contains $normalized) {
            $normalized = "C_$normalized"
        }
    }
    return $normalized
}

function Get-ColumnNameMap {
    param(
        [string[]]$Columns,
        [switch]$AllowReserved
    )

    $map = @{}
    $used = @{}
    foreach ($col in $Columns) {
        $base = Format-ColumnName -Name $col -AllowReserved:$AllowReserved
        $candidate = $base
        $i = 1
        while ($used.ContainsKey($candidate)) {
            $candidate = "$base`_$i"
            $i++
        }
        $used[$candidate] = $true
        $map[$col] = $candidate
    }
    return $map
}

function Normalize-SigninLogsColumnMap {
    param(
        [hashtable]$ColumnMap
    )

    if (-not $ColumnMap) {
        return $ColumnMap
    }

    $renames = @{
        "CreatedDateTime__UTC_"              = "CreatedDateTime"
        "ConditionalAccessPolicies_dynamic" = "ConditionalAccessPolicies"
        "DeviceDetail_dynamic"              = "DeviceDetail"
        "LocationDetails_dynamic"           = "LocationDetails"
        "MfaDetail_dynamic"                 = "MfaDetail"
        "Status_dynamic"                    = "Status"
        "C_Id"                              = "Id"
    }

    $drops = @(
        "ConditionalAccessPolicies_string",
        "DeviceDetail_string",
        "LocationDetails_string",
        "MfaDetail_string",
        "Status_string"
    )

    $normalized = @{}
    $used = @{}
    foreach ($key in $ColumnMap.Keys) {
        $value = $ColumnMap[$key]
        if ($drops -contains $value) {
            continue
        }
        if ($renames.ContainsKey($value)) {
            $value = $renames[$value]
        }
        if (-not $value) {
            continue
        }
        if ($used.ContainsKey($value)) {
            continue
        }
        $used[$value] = $true
        $normalized[$key] = $value
    }

    return $normalized
}

function Convert-RecordsToNormalizedColumns {
    param(
        [array]$Records,
        [hashtable]$ColumnMap
    )

    $normalized = foreach ($record in $Records) {
        $obj = [ordered]@{}
        foreach ($prop in $record.PSObject.Properties) {
            $newName = $ColumnMap[$prop.Name]
            if (-not $newName) {
                $newName = Format-ColumnName -Name $prop.Name
            }
            if (-not $newName) {
                continue
            }
            $obj[$newName] = $prop.Value
        }
        [pscustomobject]$obj
    }

    return $normalized
}

function Get-BuiltInTableMap {
    param([string]$MapPath)

    if ($MapPath -and (Test-Path -Path $MapPath)) {
        $raw = Get-Content -Path $MapPath -Raw
        return ($raw | ConvertFrom-Json)
    }

    return @{
        "ASimProcessEventLogs"      = "ASimProcessEventLogs"
        "AWSGuardDuty"              = "AWSGuardDuty"
        "GCPAuditLogs"              = "GCPAuditLogs"
        "CommonSecurityLog"         = "CommonSecurityLog"
        "CEF"                       = "CommonSecurityLog"
        "DeviceFileEvents"          = "DeviceFileEvents"
        "securityEvents"            = "SecurityEvent"
        "signinLogs"                = "SigninLogs"
        "sign-in_adelete"           = "SigninLogs"
        "disable_accounts"          = "SigninLogs"
        "office_activity"           = "OfficeActivity"
        "office_activity_inbox_rule"= "OfficeActivity"
        "azureActivity_adele"       = "AzureActivity"
        "azure_activity"            = "AzureActivity"
        "AuditLogs_Hunting"         = "AuditLogs"
    }
}

function Get-BuiltInStreamName {
    param(
        [string]$TableName,
        [string]$StreamPrefix
    )

    if ($StreamPrefix) {
        return "$StreamPrefix$TableName"
    }

    return "Custom-$TableName"
}

function Get-ColumnDefinitionsFromRecord {
    param(
        [object]$Record,
        [hashtable]$ColumnMap
    )

    $columns = @()
    foreach ($prop in $Record.PSObject.Properties) {
        $mappedName = if ($ColumnMap -and $ColumnMap[$prop.Name]) { $ColumnMap[$prop.Name] } else { Format-ColumnName -Name $prop.Name }
        $value = $prop.Value
        $type = "string"
        if ($null -eq $value) {
            $type = "string"
        } elseif ($value -is [bool]) {
            $type = "boolean"
        } elseif ($value -is [int] -or $value -is [long]) {
            $type = "long"
        } elseif ($value -is [double] -or $value -is [decimal] -or $value -is [single]) {
            $type = "real"
        } elseif ($value -is [datetime]) {
            $type = "datetime"
        } elseif ($value -is [hashtable] -or $value -is [pscustomobject] -or $value -is [System.Array]) {
            $type = "dynamic"
        }

        $columns += @{
            name = $mappedName
            type = $type
        }
    }

    return $columns
}

function Split-RecordsBySize {
    param(
        [array]$Records,
        [int]$MaxBytes = 900000
    )

    $current = @()
    $currentSize = 2 # []

    foreach ($record in $Records) {
        $recordJson = $record | ConvertTo-Json -Depth 20 -Compress
        $recordSize = (Get-JsonByteCount -Json $recordJson) + 1

        if (($currentSize + $recordSize) -gt $MaxBytes -and $current.Count -gt 0) {
            ,$current
            $current = @()
            $currentSize = 2
        }

        $current += $record
        $currentSize += $recordSize
    }

    if ($current.Count -gt 0) {
        ,$current
    }
}

function Get-OutputTypeOverridesFromError {
    param([string]$ErrorText)

    $overrides = @{}
    $typeMap = @{
        'String'   = 'string'
        'Int'      = 'int'
        'Long'     = 'long'
        'Double'   = 'real'
        'Bool'     = 'bool'
        'DateTime' = 'datetime'
        'Guid'     = 'guid'
        'Dynamic'  = 'dynamic'
    }

    $pattern = '(\w+)\s+\[produced:''(\w+)'',\s*output:''(\w+)''\]'
    $parsed = [regex]::Matches($ErrorText, $pattern)
    foreach ($m in $parsed) {
        $colName    = $m.Groups[1].Value
        $outputType = $m.Groups[3].Value
        if ($typeMap.ContainsKey($outputType)) {
            $overrides[$colName] = $typeMap[$outputType]
        }
    }
    return $overrides
}

function Get-FlattenedDynamicGroups {
    param(
        [string[]]$NormalizedColumns,
        [object[]]$SchemaColumns
    )

    $groups = [ordered]@{}
    if (-not $SchemaColumns) { return $groups }

    $dynamicCols = @($SchemaColumns | Where-Object { $_.type -eq "dynamic" })
    foreach ($dynCol in $dynamicCols) {
        $parentName = $dynCol.name
        $prefix = "${parentName}_"
        $subCols = @($NormalizedColumns | Where-Object {
            $_.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
        })
        if ($subCols.Count -ge 2) {
            $groups[$parentName] = $subCols
        }
    }

    return $groups
}

function Build-BuiltInTransformKql {
    param(
        [hashtable]$ColumnMap,
        [object[]]$SchemaColumns,
        [hashtable]$OutputTypeOverrides
    )

    $typeCasts = @{
        int      = "toint"
        long     = "tolong"
        real     = "todouble"
        bool     = "tobool"
        boolean  = "tobool"
        guid     = "toguid"
        datetime = "todatetime"
        dynamic  = "todynamic"
    }

    $timeColumn = $null
    foreach ($kvp in $ColumnMap.GetEnumerator()) {
        if ($kvp.Key -eq "TimeCollected [UTC]") {
            $timeColumn = $kvp.Value
            break
        }
    }

    if (-not $timeColumn -and $ColumnMap.Values -contains "TimeGenerated") {
        $timeColumn = "TimeGenerated"
    }

    $transformParts = @()
    if ($timeColumn) {
        $transformParts += "TimeCollected = todatetime($timeColumn)"
    }
    $transformParts += "TimeGenerated = now()"

    $normalizedColumns = $ColumnMap.Values
    foreach ($column in $SchemaColumns) {
        $name = $column.name
        if (-not ($normalizedColumns -contains $name)) {
            continue
        }
        if ($name -eq "TimeGenerated" -or $name -eq "TimeCollected") {
            continue
        }
        $effectiveType = $column.type
        if ($OutputTypeOverrides -and $OutputTypeOverrides.ContainsKey($name)) {
            $effectiveType = $OutputTypeOverrides[$name]
        }
        $cast = $typeCasts[$effectiveType]
        if ($cast) {
            $transformParts += "$name = $cast($name)"
        }
    }

    # Detect flattened dynamic fields and recompose with pack()
    $flattenedGroups = Get-FlattenedDynamicGroups -NormalizedColumns @($normalizedColumns) -SchemaColumns $SchemaColumns
    $flattenedSubColumns = @()
    foreach ($parentName in $flattenedGroups.Keys) {
        $subCols = $flattenedGroups[$parentName]
        $flattenedSubColumns += $subCols
        $packArgs = @()
        foreach ($subCol in $subCols) {
            $subFieldName = $subCol.Substring($parentName.Length + 1)
            $packArgs += "`"$subFieldName`", $subCol"
        }
        $transformParts += "$parentName = pack($($packArgs -join ', '))"
        Write-Host "    Recomposing flattened columns into dynamic field '$parentName' ($($subCols.Count) sub-fields)" -ForegroundColor Cyan
    }

    if ($normalizedColumns -contains "EventTime") {
        $transformParts += "EventTime = todatetime(EventTime)"
    }

    $transformKql = "source | extend " + ($transformParts -join ", ")
    if ($timeColumn -and $timeColumn -ne "TimeCollected" -and $timeColumn -ne "TimeGenerated") {
        $transformKql += " | project-away $timeColumn"
    }

    if ($SchemaColumns) {
        $projectColumns = @($SchemaColumns.name | Where-Object { $normalizedColumns -contains $_ })
        # Add parent dynamic columns created via pack()
        foreach ($parentName in $flattenedGroups.Keys) {
            if (-not ($projectColumns -contains $parentName)) {
                $projectColumns += $parentName
            }
        }
        if (-not ($projectColumns -contains "TimeGenerated")) {
            $projectColumns += "TimeGenerated"
        }
        if ($normalizedColumns -contains "EventTime" -and -not ($projectColumns -contains "EventTime")) {
            $projectColumns += "EventTime"
        }
        if ($projectColumns.Count -gt 0) {
            $transformKql += " | project " + ($projectColumns -join ", ")
        }
    }

    return $transformKql
}

function Build-CustomTransformKql {
    param(
        [hashtable]$ColumnMap,
        [object[]]$SchemaColumns,
        [string[]]$CsvColumns
    )

    $typeCasts = @{
        int      = "toint"
        long     = "tolong"
        real     = "todouble"
        bool     = "tobool"
        boolean  = "tobool"
        guid     = "toguid"
        datetime = "todatetime"
    }

    $normalizedColumns = $ColumnMap.Values
    $transformParts = @()

    $transformParts += "TimeGenerated = now()"

    foreach ($column in $SchemaColumns) {
        $name = $column.name
        if ($name -eq "TimeGenerated") {
            continue
        }
        if (-not ($normalizedColumns -contains $name)) {
            continue
        }
        if ($name -eq "Timestamp" -and $column.type -eq "datetime") {
            $transformParts += "$name = todatetime($name)"
            continue
        }
        $cast = $typeCasts[$column.type]
        if ($cast) {
            $transformParts += "$name = $cast($name)"
        }
    }

    $transformKql = "source | extend " + ($transformParts -join ", ")
    if ($CsvColumns) {
        $projectColumns = @($CsvColumns | Where-Object { $normalizedColumns -contains $_ })
    } elseif ($SchemaColumns) {
        $projectColumns = @($SchemaColumns.name | Where-Object { $normalizedColumns -contains $_ })
    } else {
        $projectColumns = @($normalizedColumns)
    }
    if (-not ($projectColumns -contains "TimeGenerated")) {
        $projectColumns += "TimeGenerated"
    }
    if ($projectColumns.Count -gt 0) {
        $transformKql += " | project " + ($projectColumns -join ", ")
    }

    return $transformKql
}

function New-BuiltInDcrTemplate {
    param(
        [string]$TableName,
        [string]$WorkspaceResourceId,
        [string]$DceResourceId,
        [string]$Location,
        [object[]]$ColumnDefinitions,
        [string]$TransformKql
    )

    $streamName = Get-BuiltInStreamName -TableName $TableName -StreamPrefix $null
    $outputStream = "Microsoft-$TableName"
    $transform = if ($TransformKql) { $TransformKql } else { "source" }

    $template = @{
        location   = $Location
        kind       = "Direct"
        properties = @{
            dataCollectionEndpointId = $DceResourceId
            streamDeclarations       = @{
                $streamName = @{
                    columns = $ColumnDefinitions
                }
            }
            destinations = @{
                logAnalytics = @(
                    @{
                        name = "la"
                        workspaceResourceId = $WorkspaceResourceId
                    }
                )
            }
            dataFlows = @(
                @{
                    streams      = @($streamName)
                    destinations = @("la")
                    transformKql = $transform
                    outputStream = $outputStream
                }
            )
        }
    }

    return $template
}

function Send-Records {
    param(
        [string]$IngestionEndpoint,
        [string]$ImmutableId,
        [string]$StreamName,
        [array]$Records,
        [string]$AccessToken
    )

    if (-not $Records -or $Records.Count -eq 0) {
        return
    }

    $apiVersion = "2023-01-01"
    $uri = "$IngestionEndpoint/dataCollectionRules/$ImmutableId/streams/${StreamName}?api-version=$apiVersion"

    $headers = @{
        Authorization = "Bearer $AccessToken"
        "Content-Type" = "application/json"
    }

    $batches = @(Split-RecordsBySize -Records $Records)
    foreach ($batch in $batches) {
        $payload = $batch | ConvertTo-Json -Depth 20 -Compress
        $attempt = 0
        $maxAttempts = 4
        while ($true) {
            try {
                $clientRequestId = [guid]::NewGuid().ToString()
                $headers["x-ms-client-request-id"] = $clientRequestId
                $null = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $payload
                break
            } catch {
                $responseBody = $null
                $exception = $_.Exception
                $hasResponse = $false
                $statusCode = $null
                $retryAfterSeconds = $null
                if ($exception) {
                    $hasResponse = ($exception.PSObject.Properties.Match('Response').Count -gt 0) -and $exception.Response
                }
                if ($hasResponse) {
                    try {
                        $reader = New-Object System.IO.StreamReader($exception.Response.GetResponseStream())
                        $responseBody = $reader.ReadToEnd()
                    } catch {
                        $responseBody = $null
                    }
                    try {
                        $statusCode = [int]$exception.Response.StatusCode
                    } catch {
                        $statusCode = $null
                    }
                    try {
                        $retryAfterHeader = $exception.Response.Headers["Retry-After"]
                        if ($retryAfterHeader) {
                            if ([int]::TryParse($retryAfterHeader, [ref]$retryAfterSeconds)) {
                                # seconds parsed
                            } else {
                                $retryAfterDate = [datetime]::Parse($retryAfterHeader)
                                $retryAfterSeconds = [math]::Max(0, [int]($retryAfterDate.ToUniversalTime() - [datetime]::UtcNow).TotalSeconds)
                            }
                        }
                    } catch {
                        $retryAfterSeconds = $null
                    }
                }

                $isInvalidStream = $false
                if ($responseBody -and $responseBody -match "InvalidStream") {
                    $isInvalidStream = $true
                } elseif ($exception -and $exception.Message -match "InvalidStream") {
                    $isInvalidStream = $true
                }

                $isTransportError = $false
                if ($exception -and ($exception.Message -match "forcibly closed|underlying connection|transport connection|connection was closed|ReceiveFailure|SendFailure|ConnectFailure|KeepAliveFailure")) {
                    $isTransportError = $true
                } elseif ($exception.InnerException -and ($exception.InnerException.Message -match "forcibly closed|underlying connection|transport connection|connection was closed")) {
                    $isTransportError = $true
                }

                $isRetryable = ($statusCode -in @(429, 500, 502, 503, 504)) -or $isTransportError
                if (($isInvalidStream -or $isRetryable) -and $attempt -lt ($maxAttempts - 1)) {
                    $attempt++
                    $delaySeconds = if ($retryAfterSeconds -and $retryAfterSeconds -gt 0) { $retryAfterSeconds } else { [math]::Min(30, [math]::Pow(2, $attempt)) }
                    if ($isInvalidStream) {
                        Write-Host "InvalidStream detected. Waiting for DCR propagation (attempt $attempt/$maxAttempts)..."
                    } elseif ($isTransportError) {
                        Write-Host "Transport error (connection reset). Retrying in $delaySeconds seconds (attempt $attempt/$maxAttempts)..."
                    } else {
                        Write-Host "Transient ingest error (status $statusCode). Retrying in $delaySeconds seconds (attempt $attempt/$maxAttempts)..."
                    }
                    Start-Sleep -Seconds $delaySeconds
                    continue
                }

                Write-Host "Ingestion failed: $($_.Exception.Message)"
                if ($responseBody) {
                    Write-Host "Response body: $responseBody"
                }
                throw
            }
        }
    }
}

Assert-AzCli

if (-not (Test-Path -Path $TelemetryPath)) {
    throw "Custom telemetry path not found: $TelemetryPath"
}

if (($BuiltInDcrImmutableId -or $DeployBuiltInDcr) -and -not (Test-Path -Path $BuiltInTelemetryPath)) {
    throw "Built-in telemetry path not found: $BuiltInTelemetryPath"
}

if (-not (Test-Path -Path $TemplatesOutputPath)) {
    New-Item -ItemType Directory -Path $TemplatesOutputPath -Force | Out-Null
}

if (-not $WorkspaceResourceId -or -not $Location) {
    $wsInfo = Resolve-WorkspaceInfo -WorkspaceName $WorkspaceName -ResourceGroupName $ResourceGroupName -SubscriptionId $SubscriptionId
    if (-not $WorkspaceResourceId) {
        $WorkspaceResourceId = $wsInfo.Id
    }
    if (-not $Location) {
        $Location = $wsInfo.Location
        Write-Host "Using workspace location: $Location"
    }
}

$customCsvFiles = if ($BuiltInOnly) { @() } else { @((Get-ChildItem -Path $TelemetryPath -Filter "*.csv")) }
$builtInCsvFiles = @()
if ($BuiltInTelemetryPath -and (Test-Path -Path $BuiltInTelemetryPath)) {
    $builtInCsvFiles = @(
        Get-ChildItem -Path $BuiltInTelemetryPath -File |
            Where-Object { $_.Extension -and ($_.Extension.ToLowerInvariant() -in @(".csv", ".json")) }
    )
}

$watchlistSegment = [IO.Path]::Combine("Telemetry", "Watchlists")
$customCsvFiles = $customCsvFiles | Where-Object { $_.FullName -notmatch [regex]::Escape($watchlistSegment) }

if ($CustomTableFilter -and $customCsvFiles.Count -gt 0) {
    $filterSet = $CustomTableFilter | ForEach-Object { $_.ToLowerInvariant() }
    $customCsvFiles = $customCsvFiles | Where-Object {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        $nameLower = $_.Name.ToLowerInvariant()
        $baseLower = $base.ToLowerInvariant()
        $baseWithCl = if ($baseLower.EndsWith("_cl")) { $baseLower } else { "${baseLower}_cl" }
        ($filterSet -contains $nameLower) -or ($filterSet -contains $baseLower) -or ($filterSet -contains $baseWithCl)
    }
}

if (@($customCsvFiles).Count -eq 0 -and @($builtInCsvFiles).Count -eq 0) {
    Write-Host "No telemetry CSVs found in '$TelemetryPath' or '$BuiltInTelemetryPath'."
    exit 0
}

$dce = $null
$dceId = $null
$ingestionEndpoint = $null

if ($Deploy -or $Ingest -or $DeployBuiltInDcr) {
    $dce = Initialize-Dce -SubscriptionId $SubscriptionId -ResourceGroupName $ResourceGroupName -Location $Location -DceName $DceName
    $dceId = $dce.id
    $ingestionEndpoint = $dce.properties.logsIngestion.endpoint
}

$token = $null
if ($Ingest) {
    $token = Get-AccessToken -TenantId $TenantId -ClientId $ClientId -ClientSecret $ClientSecret
}

foreach ($csv in $customCsvFiles) {
    $tableName = [System.IO.Path]::GetFileNameWithoutExtension($csv.Name)
    $tableName = [regex]::Replace($tableName, "[^A-Za-z0-9_]", "_")
    if (-not $tableName.EndsWith("_CL")) {
        $tableName = "${tableName}_CL"
    }

    Write-Host "Preparing DCR template for custom table '$tableName'..."

    $data = @(Read-TelemetryData -Path $csv.FullName)
    if (@($data).Count -eq 0) {
        Write-Host "Skipping '$($csv.Name)' (no records)."
        continue
    }

    $rawColumns = $data[0].PSObject.Properties.Name
    $columnMap = Get-ColumnNameMap -Columns $rawColumns
    if ($tableName -eq "SigninLogs_CL") {
        $columnMap = Normalize-SigninLogsColumnMap -ColumnMap $columnMap
    }
    $columns = $rawColumns | ForEach-Object { $columnMap[$_] } | Where-Object { $_ }
    $transformKql = $null
    if ($Deploy) {
        Initialize-CustomTable -WorkspaceResourceId $WorkspaceResourceId -TableName $tableName -Columns $columns
        $schemaColumns = Get-TableSchemaColumns -WorkspaceResourceId $WorkspaceResourceId -TableName $tableName
        $transformKql = Build-CustomTransformKql -ColumnMap $columnMap -SchemaColumns $schemaColumns -CsvColumns $columns
    }
    $template = New-DcrTemplate -TableName $tableName -Columns $columns -WorkspaceResourceId $WorkspaceResourceId -DceResourceId $dceId -Location $Location -TransformKql $transformKql

    $templatePath = Join-Path -Path $TemplatesOutputPath -ChildPath "$tableName.dcr.json"
    $template | ConvertTo-Json -Depth 20 | Out-File -FilePath $templatePath -Encoding utf8

    Write-Host "Wrote DCR template: $templatePath"

    if ($Deploy) {
        $dcrName = "$DcrPrefix$tableName"
        Write-Host "Deploying DCR '$dcrName'..."
        try {
            $dcrId = Initialize-Dcr -DcrName $dcrName -SubscriptionId $SubscriptionId -ResourceGroupName $ResourceGroupName -Template $template
        } catch {
            Write-Host "Failed to deploy DCR '$dcrName': $($_.Exception.Message)"
            continue
        }

        if ($AssigneeObjectId) {
            try {
                $null = az role assignment create --assignee $AssigneeObjectId --role "Monitoring Metrics Publisher" --scope $dcrId
            } catch {
                if ($_.Exception.Message -notmatch "RoleAssignmentExists") {
                    Write-Host "Failed to assign role on DCR '$dcrName': $($_.Exception.Message)"
                }
            }
        }

        if ($Ingest) {
            $immutableId = Get-DcrImmutableId -DcrId $dcrId
            $streamName = "Custom-$($tableName.Substring(0, $tableName.Length - 3))"
            Write-Host "Ingesting '$($csv.Name)' into stream '$streamName'..."
            $normalizedData = Convert-RecordsToNormalizedColumns -Records $data -ColumnMap $columnMap
            Send-Records -IngestionEndpoint $ingestionEndpoint -ImmutableId $immutableId -StreamName $streamName -Records $normalizedData -AccessToken $token
        }
    }
}

if (($DeployBuiltInDcr -or ($Ingest -and $BuiltInDcrImmutableId)) -and @($builtInCsvFiles).Count -gt 0) {
    $builtInMap = Get-BuiltInTableMap -MapPath $BuiltInTableMapPath
    $builtInEndpoint = if ($BuiltInIngestionEndpoint) { $BuiltInIngestionEndpoint } else { $ingestionEndpoint }
    if (-not $builtInEndpoint) {
        throw "Built-in ingestion endpoint not available. Provide -BuiltInIngestionEndpoint or ensure DCE is created."
    }

    foreach ($csv in $builtInCsvFiles) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($csv.Name)
        $tableName = $builtInMap[$baseName]
        if (-not $tableName) {
            $tableName = $baseName
        }

        $data = @(Read-TelemetryData -Path $csv.FullName)
        if (@($data).Count -eq 0) {
            Write-Host "Skipping '$($csv.Name)' (no records)."
            continue
        }

        $rawColumns = $data[0].PSObject.Properties.Name
        $columnMap = Get-ColumnNameMap -Columns $rawColumns -AllowReserved
        $normalizedData = Convert-RecordsToNormalizedColumns -Records $data -ColumnMap $columnMap

        if ($DeployBuiltInDcr) {
            $columnDefinitions = Get-ColumnDefinitionsFromRecord -Record $data[0] -ColumnMap $columnMap
            $schemaColumns = Get-TableSchemaColumns -WorkspaceResourceId $WorkspaceResourceId -TableName $tableName
            $transformKql = Build-BuiltInTransformKql -ColumnMap $columnMap -SchemaColumns $schemaColumns
            $template = New-BuiltInDcrTemplate -TableName $tableName -WorkspaceResourceId $WorkspaceResourceId -DceResourceId $dceId -Location $Location -ColumnDefinitions $columnDefinitions -TransformKql $transformKql

            $dcrName = "$BuiltInDcrPrefix$tableName"
            Write-Host "Deploying built-in DCR '$dcrName'..."
            try {
                $dcrId = Initialize-Dcr -DcrName $dcrName -SubscriptionId $SubscriptionId -ResourceGroupName $ResourceGroupName -Template $template
            } catch {
                $errMsg = $_.Exception.Message
                if ($errMsg -match 'InvalidTransformOutput') {
                    Write-Host "Type mismatch detected, adjusting transform and retrying..."
                    $overrides = Get-OutputTypeOverridesFromError -ErrorText $errMsg
                    if ($overrides.Count -gt 0) {
                        $transformKql = Build-BuiltInTransformKql -ColumnMap $columnMap -SchemaColumns $schemaColumns -OutputTypeOverrides $overrides
                        $template = New-BuiltInDcrTemplate -TableName $tableName -WorkspaceResourceId $WorkspaceResourceId -DceResourceId $dceId -Location $Location -ColumnDefinitions $columnDefinitions -TransformKql $transformKql
                        try {
                            $dcrId = Initialize-Dcr -DcrName $dcrName -SubscriptionId $SubscriptionId -ResourceGroupName $ResourceGroupName -Template $template
                        } catch {
                            Write-Host "Failed to deploy built-in DCR '$dcrName' after retry: $($_.Exception.Message)"
                            continue
                        }
                    } else {
                        Write-Host "Failed to deploy built-in DCR '$dcrName': $errMsg"
                        continue
                    }
                } else {
                    Write-Host "Failed to deploy built-in DCR '$dcrName': $errMsg"
                    continue
                }
            }

            $immutableId = Get-DcrImmutableId -DcrId $dcrId
            if ($Ingest) {
                $streamName = Get-BuiltInStreamName -TableName $tableName -StreamPrefix $null
                Write-Host "Ingesting built-in '$($csv.Name)' into stream '$streamName'..."
                Send-Records -IngestionEndpoint $builtInEndpoint -ImmutableId $immutableId -StreamName $streamName -Records $normalizedData -AccessToken $token
            }
        } elseif ($Ingest -and $BuiltInDcrImmutableId) {
            $streamName = Get-BuiltInStreamName -TableName $tableName -StreamPrefix $BuiltInStreamPrefix
            Write-Host "Ingesting built-in '$($csv.Name)' into stream '$streamName'..."
            Send-Records -IngestionEndpoint $builtInEndpoint -ImmutableId $BuiltInDcrImmutableId -StreamName $streamName -Records $normalizedData -AccessToken $token
        }
    }
}

Write-Host "Done."
