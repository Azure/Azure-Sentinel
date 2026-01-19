# IntegrationSuiteHelpers.ps1
# Shared helper functions for SAP Integration Suite Sentinel Connector scripts
# This module provides common functionality for Azure authentication, DCR/DCE management,
# and data connector operations for SAP Integration Suite integration with Microsoft Sentinel.

# Function to log messages with colored output
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Function to check if Azure CLI is installed
function Test-AzCli {
    try {
        $azVersionJson = az version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $versionInfo = $azVersionJson | ConvertFrom-Json
            Write-Log "Azure CLI is installed: $($versionInfo.'azure-cli')"
            return $true
        }
        else {
            Write-Log "Azure CLI is not installed or not in PATH. Please install it first." -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Azure CLI is not installed or not in PATH. Please install it first." -Level "ERROR"
        return $false
    }
}

# Function to get Azure access token
function Get-AzureAccessToken {
    try {
        $token = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to get Azure access token: $token" -Level "ERROR"
            return $null
        }
        return $token
    }
    catch {
        Write-Log "Error getting Azure access token: $_" -Level "ERROR"
        return $null
    }
}

# Function to parse Integration Suite service key credentials
# AuthType parameter controls authentication method:
#   - "OAuth2" (default for CF): OAuth2 with credentials in request body
#   - "OAuth2WithBasicHeader": OAuth2 with credentials in Basic Auth header (for SAP NEO)
#   - "Basic": True HTTP Basic Auth without OAuth (username/password on every request)
function Get-IntegrationSuiteCredentials {
    param(
        [Parameter(Mandatory=$false)]
        [string]$ServiceKeyJson,
        
        [Parameter(Mandatory=$false)]
        [string]$ServiceKeyPath,
        
        [Parameter(Mandatory=$false)]
        [string]$ClientId,
        
        [Parameter(Mandatory=$false)]
        [SecureString]$ClientSecret,
        
        [Parameter(Mandatory=$false)]
        [string]$IntegrationServerUrl,
        
        [Parameter(Mandatory=$false)]
        [string]$TokenEndpoint,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("OAuth2", "OAuth2WithBasicHeader", "Basic")]
        [string]$AuthType = "OAuth2WithBasicHeader"
    )
    
    try {
        # If direct parameters are provided, use them
        # For Basic auth, TokenEndpoint is not required
        $tokenEndpointRequired = $AuthType -ne "Basic"
        
        if (-not [string]::IsNullOrWhiteSpace($ClientId) -and
            $null -ne $ClientSecret -and
            -not [string]::IsNullOrWhiteSpace($IntegrationServerUrl) -and
            (-not $tokenEndpointRequired -or -not [string]::IsNullOrWhiteSpace($TokenEndpoint))) {
            
            Write-Log "Using directly provided credentials with AuthType: $AuthType"
            
            # Convert SecureString to plain text for validation only
            $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ClientSecret)
            $plainSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
            [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
            
            return @{
                ClientId = $ClientId
                ClientSecret = $plainSecret
                IntegrationServerUrl = $IntegrationServerUrl.TrimEnd('/')
                TokenEndpoint = $TokenEndpoint
                AuthType = $AuthType  # Authentication type: OAuth2, OAuth2WithBasicHeader, or Basic
            }
        }
        
        # Try to load from service key JSON string or file
        $serviceKey = $null
        
        if (-not [string]::IsNullOrWhiteSpace($ServiceKeyJson)) {
            Write-Log "Parsing service key from JSON string"
            $serviceKey = $ServiceKeyJson | ConvertFrom-Json
        }
        elseif (-not [string]::IsNullOrWhiteSpace($ServiceKeyPath)) {
            if (-not (Test-Path $ServiceKeyPath)) {
                Write-Log "Service key file not found: $ServiceKeyPath" -Level "ERROR"
                return $null
            }
            Write-Log "Loading service key from file: $ServiceKeyPath"
            $serviceKey = Get-Content -Path $ServiceKeyPath -Raw | ConvertFrom-Json
        }
        else {
            Write-Log "No credentials provided. Please provide either direct credentials or a service key." -Level "ERROR"
            return $null
        }
        
        # Extract credentials from service key structure
        # Service key format can be:
        #   - Direct: { "oauth": { "clientid", "clientsecret", "url", "tokenurl" } }
        #   - Wrapped: { "credentials": { "oauth": { "clientid", "clientsecret", "url", "tokenurl" } } }
        $oauth = $null
        if ($null -ne $serviceKey.credentials -and $null -ne $serviceKey.credentials.oauth) {
            # Wrapped format (from cf service-key command output)
            Write-Log "Detected wrapped credentials format (credentials.oauth)"
            $oauth = $serviceKey.credentials.oauth
        }
        elseif ($null -ne $serviceKey.oauth) {
            # Direct format
            $oauth = $serviceKey.oauth
        }
        else {
            Write-Log "Service key missing 'oauth' property (checked both direct and credentials.oauth formats)" -Level "ERROR"
            return $null
        }
        
        # Validate required fields
        if ([string]::IsNullOrWhiteSpace($oauth.clientid)) {
            Write-Log "Service key missing oauth.clientid" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($oauth.clientsecret)) {
            Write-Log "Service key missing oauth.clientsecret" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($oauth.url)) {
            Write-Log "Service key missing oauth.url (Integration Server URL)" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($oauth.tokenurl)) {
            Write-Log "Service key missing oauth.tokenurl" -Level "ERROR"
            return $null
        }
        
        Write-Log "Successfully parsed service key credentials" -Level "SUCCESS"
        
        return @{
            ClientId = $oauth.clientid
            ClientSecret = $oauth.clientsecret
            IntegrationServerUrl = $oauth.url.TrimEnd('/')
            TokenEndpoint = $oauth.tokenurl
            AuthType = "OAuth2"  # CF service keys use standard OAuth2 (credentials in body)
        }
    }
    catch {
        Write-Log "Error parsing credentials: $_" -Level "ERROR"
        return $null
    }
}

# Function to get workspace details including resource ID and location
function Get-SentinelWorkspaceDetails {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubscriptionId,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceName
    )
    
    try {
        Write-Log "Getting workspace details for '$WorkspaceName'..."
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $null
        }
        
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName`?api-version=2022-10-01"
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
        
        # Extract a short ID from workspace ID for naming (first 12 chars of last GUID segment)
        $workspaceId = $response.properties.customerId
        $shortId = $workspaceId.Substring(0, [Math]::Min(12, $workspaceId.Length))
        
        Write-Log "Workspace details retrieved successfully" -Level "SUCCESS"
        Write-Log "  Location: $($response.location)"
        Write-Log "  Workspace ID: $workspaceId"
        Write-Log "  Short ID for naming: $shortId"
        
        return @{
            ResourceId = $response.id
            Location = $response.location
            WorkspaceId = $workspaceId
            ShortId = $shortId
            Name = $WorkspaceName
        }
    }
    catch {
        Write-Log "Error getting workspace details: $_" -Level "ERROR"
        return $null
    }
}

# Function to get or create Data Collection Endpoint for SAP Integration Suite
function Get-OrCreateSapccDataCollectionEndpoint {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubscriptionId,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceShortId,
        [Parameter(Mandatory=$true)]
        [string]$Location
    )
    
    try {
        # DCE naming convention: Microsoft-Sentinel-SAPCC-{workspace-short-id}
        $dceName = "Microsoft-Sentinel-SAPCC-$WorkspaceShortId"
        
        Write-Log "Checking for existing Data Collection Endpoint '$dceName'..."
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $null
        }
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/dataCollectionEndpoints/$dceName`?api-version=2022-06-01"
        
        # Try to get existing DCE
        try {
            $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
            
            Write-Log "Found existing DCE '$dceName'" -Level "SUCCESS"
            Write-Log "  Logs Ingestion Endpoint: $($response.properties.logsIngestion.endpoint)"
            
            return @{
                Name = $dceName
                ResourceId = $response.id
                LogsIngestionEndpoint = $response.properties.logsIngestion.endpoint
            }
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 404) {
                Write-Log "DCE '$dceName' not found, creating new one..."
            }
            else {
                throw $_
            }
        }
        
        # Create new DCE
        $dceBody = @{
            location = $Location
            properties = @{
                networkAcls = @{
                    publicNetworkAccess = "Enabled"
                }
            }
        } | ConvertTo-Json -Depth 5
        
        $response = Invoke-RestMethod -Uri $uri -Method Put -Headers $headers -Body $dceBody
        
        Write-Log "Successfully created DCE '$dceName'" -Level "SUCCESS"
        Write-Log "  Logs Ingestion Endpoint: $($response.properties.logsIngestion.endpoint)"
        
        return @{
            Name = $dceName
            ResourceId = $response.id
            LogsIngestionEndpoint = $response.properties.logsIngestion.endpoint
        }
    }
    catch {
        Write-Log "Error with Data Collection Endpoint: $_" -Level "ERROR"
        return $null
    }
}

# Function to get Data Collection Endpoint by resource ID
function Get-DataCollectionEndpointById {
    param(
        [Parameter(Mandatory=$true)]
        [string]$DataCollectionEndpointId
    )
    
    try {
        Write-Log "Getting Data Collection Endpoint details from: $DataCollectionEndpointId"
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $null
        }
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $uri = "https://management.azure.com$DataCollectionEndpointId`?api-version=2022-06-01"
        
        $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
        
        # Extract DCE name from resource ID
        $dceName = $DataCollectionEndpointId.Split('/')[-1]
        
        Write-Log "Found DCE '$dceName'" -Level "SUCCESS"
        Write-Log "  Logs Ingestion Endpoint: $($response.properties.logsIngestion.endpoint)"
        
        return @{
            Name = $dceName
            ResourceId = $response.id
            LogsIngestionEndpoint = $response.properties.logsIngestion.endpoint
        }
    }
    catch {
        Write-Log "Error getting Data Collection Endpoint: $_" -Level "ERROR"
        return $null
    }
}

# Function to load DCR template from SAPCC_DCR.json file
function Get-SapccDcrTemplate {
    param(
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceResourceId,
        [Parameter(Mandatory=$true)]
        [string]$DataCollectionEndpointId
    )
    
    try {
        # Determine the path to SAPCC_DCR.json relative to this script
        $scriptDir = $PSScriptRoot
        if ([string]::IsNullOrWhiteSpace($scriptDir)) {
            # Fallback if $PSScriptRoot is not available (e.g., running in ISE)
            $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        }
        
        # Path to DCR template in the same directory
        $dcrTemplatePath = Join-Path -Path $scriptDir -ChildPath "SAPCC_DCR.json"
        $dcrTemplatePath = [System.IO.Path]::GetFullPath($dcrTemplatePath)
        
        if (-not (Test-Path $dcrTemplatePath)) {
            Write-Log "DCR template file not found at: $dcrTemplatePath" -Level "ERROR"
            return $null
        }
        
        Write-Log "Loading DCR template from: $dcrTemplatePath"
        
        # Read and parse the JSON template
        $templateContent = Get-Content -Path $dcrTemplatePath -Raw
        
        # Replace placeholders with actual values
        $templateContent = $templateContent -replace '\{\{workspaceResourceId\}\}', $WorkspaceResourceId
        $templateContent = $templateContent -replace '\{\{dataCollectionEndpointId\}\}', $DataCollectionEndpointId
        
        # Parse JSON - the template is an array with one element
        $templateArray = $templateContent | ConvertFrom-Json
        $template = $templateArray[0]
        
        if ($null -eq $template -or $null -eq $template.properties) {
            Write-Log "Invalid DCR template structure" -Level "ERROR"
            return $null
        }
        
        Write-Log "Successfully loaded DCR template" -Level "SUCCESS"
        
        # Return the properties section which contains the DCR configuration
        return $template.properties
    }
    catch {
        Write-Log "Error loading DCR template: $_" -Level "ERROR"
        return $null
    }
}

# Function to get or create Data Collection Rule for SAP Integration Suite
function Get-OrCreateSapccDataCollectionRule {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubscriptionId,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceShortId,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceResourceId,
        [Parameter(Mandatory=$false)]
        [string]$DataCollectionEndpointId = "",
        [Parameter(Mandatory=$true)]
        [string]$Location
    )
    
    try {
        # DCR naming convention: Microsoft-Sentinel-SAPCC-DCR-{workspace-short-id}
        $dcrName = "Microsoft-Sentinel-SAPCC-DCR-$WorkspaceShortId"
        
        Write-Log "Checking for existing Data Collection Rule '$dcrName'..."
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $null
        }
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/dataCollectionRules/$dcrName`?api-version=2022-06-01"
        
        # Try to get existing DCR
        try {
            $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
            
            Write-Log "Found existing DCR '$dcrName'" -Level "SUCCESS"
            Write-Log "  Immutable ID: $($response.properties.immutableId)"
            Write-Log "  DCE Reference: $($response.properties.dataCollectionEndpointId)"
            
            return @{
                Name = $dcrName
                ResourceId = $response.id
                ImmutableId = $response.properties.immutableId
                DataCollectionEndpointId = $response.properties.dataCollectionEndpointId
            }
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 404) {
                Write-Log "DCR '$dcrName' not found, creating new one..."
            }
            else {
                throw $_
            }
        }
        
        # For creating new DCR, DataCollectionEndpointId is required
        if ([string]::IsNullOrWhiteSpace($DataCollectionEndpointId)) {
            Write-Log "DataCollectionEndpointId is required to create a new DCR" -Level "ERROR"
            return $null
        }
        
        # Load DCR schema from SAPCC_DCR.json
        $dcrProperties = Get-SapccDcrTemplate -WorkspaceResourceId $WorkspaceResourceId -DataCollectionEndpointId $DataCollectionEndpointId
        
        if ($null -eq $dcrProperties) {
            Write-Log "Failed to load DCR template from SAPCC_DCR.json" -Level "ERROR"
            return $null
        }
        
        # Build the DCR body with location and loaded properties
        $dcrBody = @{
            location = $Location
            properties = $dcrProperties
        } | ConvertTo-Json -Depth 10
        
        $response = Invoke-RestMethod -Uri $uri -Method Put -Headers $headers -Body $dcrBody
        
        Write-Log "Successfully created DCR '$dcrName'" -Level "SUCCESS"
        Write-Log "  Immutable ID: $($response.properties.immutableId)"
        
        return @{
            Name = $dcrName
            ResourceId = $response.id
            ImmutableId = $response.properties.immutableId
            DataCollectionEndpointId = $DataCollectionEndpointId
        }
    }
    catch {
        Write-Log "Error with Data Collection Rule: $_" -Level "ERROR"
        return $null
    }
}

# Function to build SAP Integration Suite data connector connection request body
function New-IntegrationSuiteConnectionRequestBody {
    param(
        [Parameter(Mandatory=$true)]
        [object]$Credentials,

        [Parameter(Mandatory=$true)]
        [object]$DcrConfig,

        [Parameter(Mandatory=$false)]
        [string]$ApiPathSuffix = "/microsoft/sentinel/sap-log-trigger",
        
        [Parameter(Mandatory=$false)]
        [string]$RfcDestinationName = "",
        
        [Parameter(Mandatory=$false)]
        [int]$PollingFrequencyMinutes = 5
    )
    
    try {
        # Validate DcrConfig
        if ($null -eq $DcrConfig -or
            [string]::IsNullOrWhiteSpace($DcrConfig.DataCollectionEndpoint) -or
            [string]::IsNullOrWhiteSpace($DcrConfig.DataCollectionRuleImmutableId)) {
            Write-Log "DcrConfig is required with DataCollectionEndpoint and DataCollectionRuleImmutableId" -Level "ERROR"
            return $null
        }
        
        # Build API endpoint for SAP log trigger
        $apiEndpoint = "$($Credentials.IntegrationServerUrl)/http$ApiPathSuffix"
        
        # Build headers including optional RFC destination
        $requestHeaders = @{
            "Accept" = "application/json"
            "User-Agent" = "Scuba"
        }
        if (-not [string]::IsNullOrWhiteSpace($RfcDestinationName)) {
            $requestHeaders["rfcDestinationName"] = $RfcDestinationName
        }
        
        # Determine auth configuration based on AuthType
        # Supported types:
        #   - "OAuth2": Standard OAuth2 with credentials in request body (default for CF)
        #   - "OAuth2WithBasicHeader": OAuth2 with credentials in Basic Auth header (for SAP NEO)
        #   - "Basic": True HTTP Basic Auth without OAuth (username/password on every request)
        $authConfig = $null
        $authType = if ($Credentials.AuthType) { $Credentials.AuthType } else { "OAuth2" }
        
        switch ($authType) {
            "Basic" {
                Write-Log "Using Basic auth (HTTP Basic Authentication on every request)"
                # True Basic Auth - sends username/password as Basic Auth header on every API request
                # No token endpoint needed - credentials are sent directly with each request
                $authConfig = @{
                    type = "Basic"
                    userName = $Credentials.ClientId
                    password = $Credentials.ClientSecret
                }
            }
            "OAuth2WithBasicHeader" {
                Write-Log "Using OAuth2 auth with Basic Auth header for token endpoint (for SAP NEO)"
                # OAuth2 with credentials in Basic Auth header
                # This is required for SAP NEO OAuth servers that don't accept credentials in the body
                
                # Build token endpoint - add grant_type to query string for SAP OAuth servers
                $tokenEndpoint = $Credentials.TokenEndpoint
                if (-not [string]::IsNullOrWhiteSpace($tokenEndpoint) -and -not $tokenEndpoint.Contains("grant_type")) {
                    $separator = if ($tokenEndpoint.Contains("?")) { "&" } else { "?" }
                    $tokenEndpoint = "$tokenEndpoint${separator}grant_type=client_credentials"
                }
                
                $authConfig = @{
                    type = "OAuth2"
                    ClientId = $Credentials.ClientId
                    ClientSecret = $Credentials.ClientSecret
                    GrantType = "client_credentials"
                    TokenEndpoint = $tokenEndpoint
                    IsClientSecretInHeader = $true
                    TokenEndpointHeaders = @{
                        "Accept" = "application/json"
                    }
                    TokenEndpointQueryParameters = @{}
                }
            }
            default {
                # "OAuth2" - Standard OAuth2 with credentials in body
                Write-Log "Using OAuth2 auth with credentials in body (for CF service keys)"
                
                # Build token endpoint - add grant_type to query string for SAP OAuth servers
                $tokenEndpoint = $Credentials.TokenEndpoint
                if (-not [string]::IsNullOrWhiteSpace($tokenEndpoint) -and -not $tokenEndpoint.Contains("grant_type")) {
                    $separator = if ($tokenEndpoint.Contains("?")) { "&" } else { "?" }
                    $tokenEndpoint = "$tokenEndpoint${separator}grant_type=client_credentials"
                }
                
                $authConfig = @{
                    type = "OAuth2"
                    ClientId = $Credentials.ClientId
                    ClientSecret = $Credentials.ClientSecret
                    GrantType = "client_credentials"
                    TokenEndpoint = $tokenEndpoint
                    TokenEndpointHeaders = @{
                        "Accept" = "application/json"
                        "Content-Type" = "application/x-www-form-urlencoded"
                    }
                    TokenEndpointQueryParameters = @{}
                }
            }
        }
        
        # Build request body matching SAPCC connector template
        $body = @{
            kind = "RestApiPoller"
            properties = @{
                connectorDefinitionName = "SAPCC"
                dataType = "SentinelHealth"
                # DCR configuration required for data ingestion
                dcrConfig = @{
                    dataCollectionEndpoint = $DcrConfig.DataCollectionEndpoint
                    dataCollectionRuleImmutableId = $DcrConfig.DataCollectionRuleImmutableId
                    streamName = "SENTINEL_HEALTH"
                }
                auth = $authConfig
                request = @{
                    apiEndpoint = $apiEndpoint
                    httpMethod = "GET"
                    queryWindowInMin = $PollingFrequencyMinutes
                    queryTimeFormat = "yyyy-MM-ddTHH:mm:ss.000000+00:00"
                    startTimeAttributeName = "startTimeUTC"
                    endTimeAttributeName = "endTimeUTC"
                    rateLimitQps = 2
                    retryCount = 1
                    timeoutInSeconds = 180
                    headers = $requestHeaders
                }
                response = @{
                    eventsJsonPaths = @('$')
                    format = "json"
                }
                paging = @{
                    pagingType = "LinkHeader"
                }
                isActive = $true
            }
        }
        
        Write-Log "Built connection request body with DCR configuration"
        Write-Log "  Auth Type: $authType"
        Write-Log "  API Endpoint: $apiEndpoint"
        if ($authType -ne "Basic") {
            Write-Log "  Token Endpoint: $tokenEndpoint"
        }
        
        return $body
    }
    catch {
        Write-Log "Error building connection request body: $_" -Level "ERROR"
        return $null
    }
}

# Function to create SAP Integration Suite connection in Microsoft Sentinel
function New-SentinelIntegrationSuiteConnection {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubscriptionId,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceName,
        [Parameter(Mandatory=$true)]
        [string]$ConnectionName,
        [Parameter(Mandatory=$true)]
        [object]$Credentials,
        [Parameter(Mandatory=$true)]
        [object]$DcrConfig,
        [Parameter(Mandatory=$false)]
        [string]$ApiPathSuffix = "/microsoft/sentinel/sap-log-trigger",
        [Parameter(Mandatory=$false)]
        [string]$RfcDestinationName = "",
        [Parameter(Mandatory=$false)]
        [int]$PollingFrequencyMinutes = 5,
        [Parameter(Mandatory=$false)]
        [string]$ApiVersion = "2025-07-01-preview"
    )
    
    try {
        # Sanitize connection name to be URL-compliant by removing unsupported characters
        $sanitizedConnectionName = $ConnectionName -replace '[^a-zA-Z0-9\-_\.]', ''
        
        Write-Log "Creating SAP Integration Suite connection '$sanitizedConnectionName'..."
        if ($sanitizedConnectionName -ne $ConnectionName) {
            Write-Log "  Original name '$ConnectionName' was sanitized for URL compliance" -Level "WARNING"
        }
        
        # Validate credentials - TokenEndpoint is only required for OAuth2 auth types
        $authType = if ($Credentials.AuthType) { $Credentials.AuthType } else { "OAuth2" }
        $requiredFields = @('ClientId', 'ClientSecret', 'IntegrationServerUrl')
        if ($authType -ne "Basic") {
            $requiredFields += 'TokenEndpoint'
        }
        foreach ($field in $requiredFields) {
            if ([string]::IsNullOrWhiteSpace($Credentials.$field)) {
                Write-Log "Invalid $field - cannot create connection" -Level "ERROR"
                return $false
            }
        }
        
        # Validate DcrConfig
        if ($null -eq $DcrConfig -or
            [string]::IsNullOrWhiteSpace($DcrConfig.DataCollectionEndpoint) -or
            [string]::IsNullOrWhiteSpace($DcrConfig.DataCollectionRuleImmutableId)) {
            Write-Log "DcrConfig is required with DataCollectionEndpoint and DataCollectionRuleImmutableId" -Level "ERROR"
            return $false
        }
        
        Write-Log "Credentials validated successfully"
        Write-Log "  Client ID: $($Credentials.ClientId)"
        Write-Log "  Token Endpoint: $($Credentials.TokenEndpoint)"
        Write-Log "  Integration Server URL: $($Credentials.IntegrationServerUrl)"
        
        # Get Azure access token
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $false
        }
        
        # Build request body
        $bodyObject = New-IntegrationSuiteConnectionRequestBody `
            -Credentials $Credentials `
            -DcrConfig $DcrConfig `
            -ApiPathSuffix $ApiPathSuffix `
            -RfcDestinationName $RfcDestinationName `
            -PollingFrequencyMinutes $PollingFrequencyMinutes
        
        if ($null -eq $bodyObject) {
            return $false
        }
        
        $body = $bodyObject | ConvertTo-Json -Depth 10
        
        # Construct ARM API URI
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/providers/Microsoft.SecurityInsights/dataConnectors/$sanitizedConnectionName`?api-version=$ApiVersion"
        
        # Create headers
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        # Make REST API call
        $response = Invoke-RestMethod -Uri $uri -Method Put -Headers $headers -Body $body
        
        Write-Log "Successfully created SAP Integration Suite connection '$sanitizedConnectionName'" -Level "SUCCESS"
        Write-Log "  Integration Server: $($Credentials.IntegrationServerUrl)"
        return $true
    }
    catch {
        Write-Log "Error creating SAP Integration Suite connection: $_" -Level "ERROR"
        Write-Log "Error details: $($_.Exception.Message)" -Level "ERROR"
        if ($_.Exception.Response) {
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $reader.BaseStream.Position = 0
                $responseBody = $reader.ReadToEnd()
                Write-Log "Response body: $responseBody" -Level "ERROR"
            }
            catch {
                Write-Log "Could not read error response body" -Level "ERROR"
            }
        }
        return $false
    }
}

# Function to create CF service instance (if not exists)
# Includes waiting for async service creation to complete
# For SAP Process Integration Runtime (it-rt) service, default configuration is applied automatically
function New-CfServiceInstance {
    param(
        [string]$InstanceName,
        [string]$Service,
        [string]$Plan,
        [int]$MaxWaitTimeSeconds = 300,
        [int]$WaitIntervalSeconds = 10
    )
    
    try {
        Write-Log "Creating service instance '$InstanceName' with service '$Service' and plan '$Plan'..."
        
        # Check if service instance already exists
        $existingService = cf service $InstanceName 2>&1
        if ($LASTEXITCODE -eq 0) {
            # Check if the existing service is ready
            if ($existingService -match "status:\s*create succeeded" -or $existingService -match "bound apps:") {
                Write-Log "Service instance '$InstanceName' already exists and is ready." -Level "SUCCESS"
                return $true
            }
            elseif ($existingService -match "status:\s*create in progress") {
                Write-Log "Service instance '$InstanceName' exists but is still creating. Waiting..."
            }
            else {
                Write-Log "Service instance '$InstanceName' already exists." -Level "WARNING"
                return $true
            }
        }
        else {
            # Service doesn't exist, create it
            # For SAP Process Integration Runtime (it-rt), apply required configuration parameters
            if ($Service -eq "it-rt") {
                $serviceConfig = @{
                    "grant-types" = @("client_credentials")
                    "redirect-uris" = @()
                    "roles" = @("ESBMessaging.send")
                }
                $configJson = $serviceConfig | ConvertTo-Json -Compress
                Write-Log "Applying SAP Process Integration Runtime configuration: $configJson"
                $result = cf create-service $Service $Plan $InstanceName -c $configJson 2>&1
            }
            else {
                $result = cf create-service $Service $Plan $InstanceName 2>&1
            }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Failed to create service instance '$InstanceName': $result" -Level "ERROR"
                return $false
            }
            Write-Log "Service instance creation initiated. Waiting for completion..."
        }
        
        # Wait for service to be ready (async creation)
        $elapsedTime = 0
        while ($elapsedTime -lt $MaxWaitTimeSeconds) {
            Start-Sleep -Seconds $WaitIntervalSeconds
            $elapsedTime += $WaitIntervalSeconds
            
            $serviceStatus = cf service $InstanceName 2>&1
            if ($serviceStatus -match "status:\s*create succeeded") {
                Write-Log "Service instance '$InstanceName' is ready" -Level "SUCCESS"
                return $true
            }
            elseif ($serviceStatus -match "status:\s*create failed") {
                Write-Log "Service instance creation failed" -Level "ERROR"
                Write-Log "Details: $serviceStatus" -Level "ERROR"
                return $false
            }
            else {
                Write-Log "Waiting for service instance... ($elapsedTime seconds elapsed)"
            }
        }
        
        Write-Log "Timeout waiting for service instance creation after $MaxWaitTimeSeconds seconds" -Level "WARNING"
        Write-Log "The service may still be creating. Check status with: cf service $InstanceName" -Level "WARNING"
        return $false
    }
    catch {
        Write-Log "Error creating service instance: $_" -Level "ERROR"
        return $false
    }
}

# Function to create CF service key (if not exists)
function New-CfServiceKey {
    param(
        [string]$InstanceName,
        [string]$KeyName
    )
    
    try {
        Write-Log "Creating service key '$KeyName' for service instance '$InstanceName'..."
        
        # Check if service key already exists
        $existingKey = cf service-key $InstanceName $KeyName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Service key '$KeyName' already exists. Skipping creation." -Level "WARNING"
            return $true
        }
        
        # Create service key
        $result = cf create-service-key $InstanceName $KeyName 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully created service key '$KeyName'" -Level "SUCCESS"
            return $true
        }
        else {
            Write-Log "Failed to create service key '$KeyName': $result" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error creating service key: $_" -Level "ERROR"
        return $false
    }
}

# Function to import and validate destinations from CSV file
function Import-DestinationsCsv {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CsvPath
    )
    
    try {
        # Validate file exists
        if (-not (Test-Path $CsvPath)) {
            Write-Log "Destinations CSV file not found: $CsvPath" -Level "ERROR"
            return $null
        }
        
        Write-Log "Loading destinations from: $CsvPath"
        
        # Read CSV with semicolon delimiter
        $destinations = Import-Csv -Path $CsvPath -Delimiter ';'
        
        if ($null -eq $destinations -or $destinations.Count -eq 0) {
            Write-Log "No destinations found in CSV file" -Level "ERROR"
            return $null
        }
        
        # Validate required columns exist
        $requiredColumns = @('DestinationName')
        $csvColumns = $destinations[0].PSObject.Properties.Name
        
        foreach ($column in $requiredColumns) {
            if ($column -notin $csvColumns) {
                Write-Log "CSV file missing required column: $column" -Level "ERROR"
                Write-Log "Found columns: $($csvColumns -join ', ')" -Level "ERROR"
                return $null
            }
        }
        
        # Validate each destination has a non-empty name
        $validDestinations = @()
        foreach ($dest in $destinations) {
            if ([string]::IsNullOrWhiteSpace($dest.DestinationName)) {
                Write-Log "Skipping row with empty DestinationName" -Level "WARNING"
                continue
            }
            
            # Set default polling frequency if not specified or invalid
            $pollingFreq = 5
            if ($dest.PSObject.Properties.Name -contains 'PollingFrequencyInMinutes') {
                $parsedFreq = 0
                if ([int]::TryParse($dest.PollingFrequencyInMinutes, [ref]$parsedFreq) -and $parsedFreq -gt 0) {
                    $pollingFreq = $parsedFreq
                }
            }
            
            $validDestinations += [PSCustomObject]@{
                DestinationName = $dest.DestinationName
                PollingFrequencyInMinutes = $pollingFreq
                Type = $dest.Type
                Description = $dest.Description
            }
        }
        
        if ($validDestinations.Count -eq 0) {
            Write-Log "No valid destinations found in CSV file" -Level "ERROR"
            return $null
        }
        
        Write-Log "Loaded $($validDestinations.Count) destination(s) from CSV" -Level "SUCCESS"
        foreach ($dest in $validDestinations) {
            Write-Log "  - $($dest.DestinationName) (polling: $($dest.PollingFrequencyInMinutes) min)"
        }
        
        return $validDestinations
    }
    catch {
        Write-Log "Error reading destinations CSV: $_" -Level "ERROR"
        return $null
    }
}

# Function to validate Cloud Foundry CLI is logged in
function Test-CfCliLogin {
    try {
        $cfTarget = cf target 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Cloud Foundry CLI is not logged in." -Level "ERROR"
            Write-Log "Please run 'cf login -a <cf-api-endpoint>' first." -Level "ERROR"
            Write-Log "Then target your org and space: 'cf target -o <org> -s <space>'" -Level "ERROR"
            return $false
        }
        Write-Log "CF CLI is logged in and targeting:" -Level "SUCCESS"
        # Parse target output for display
        foreach ($line in $cfTarget) {
            if ($line -match "^(api endpoint|org|space|user):" -or $line -match "^\s+(api endpoint|org|space|user):") {
                Write-Log "  $line"
            }
        }
        return $true
    }
    catch {
        Write-Log "Error checking CF CLI login status: $_" -Level "ERROR"
        return $false
    }
}

# Function to get Integration Suite credentials by calling provision-sap-cpi-runtime.ps1
function Get-IntegrationSuiteCredentialsFromCf {
    param(
        [Parameter(Mandatory=$false)]
        [string]$InstanceName = "cpi-sentinel-integration-rt",
        
        [Parameter(Mandatory=$false)]
        [string]$KeyName = "cpi-sentinel-integration-key"
    )
    
    try {
        Write-Log "Retrieving Integration Suite credentials from CF service key..."
        Write-Log "  Instance: $InstanceName"
        Write-Log "  Key: $KeyName"
        
        # Get the script directory
        $scriptDir = $PSScriptRoot
        if ([string]::IsNullOrWhiteSpace($scriptDir)) {
            $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        }
        
        $provisionScript = Join-Path -Path $scriptDir -ChildPath "provision-sap-cpi-runtime.ps1"
        
        if (-not (Test-Path $provisionScript)) {
            Write-Log "Provision script not found at: $provisionScript" -Level "ERROR"
            return $null
        }
        
        # Call the provision script to get credentials
        # The script will create the service instance and key if they don't exist
        $credentials = & $provisionScript -InstanceName $InstanceName -KeyName $KeyName
        
        if ($null -eq $credentials) {
            Write-Log "Failed to retrieve credentials from provision script" -Level "ERROR"
            return $null
        }
        
        # Validate the credentials object has required properties
        $requiredProps = @('ClientId', 'ClientSecret', 'IntegrationServerUrl', 'TokenEndpoint')
        foreach ($prop in $requiredProps) {
            if ([string]::IsNullOrWhiteSpace($credentials.$prop)) {
                Write-Log "Credentials missing required property: $prop" -Level "ERROR"
                return $null
            }
        }
        
        Write-Log "Successfully retrieved Integration Suite credentials" -Level "SUCCESS"
        Write-Log "  Integration Server URL: $($credentials.IntegrationServerUrl)"
        Write-Log "  Token Endpoint: $($credentials.TokenEndpoint)"
        Write-Log "  Client ID: $($credentials.ClientId)"
        
        return $credentials
    }
    catch {
        Write-Log "Error retrieving Integration Suite credentials: $_" -Level "ERROR"
        return $null
    }
}
