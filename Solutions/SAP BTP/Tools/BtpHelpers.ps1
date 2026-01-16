# BtpHelpers.ps1
# Shared helper functions for SAP BTP integration scripts
# This module provides common functionality for Cloud Foundry authentication,
# API endpoint management, and logging across multiple BTP automation scripts.

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

# Function to check if BTP CLI is installed
function Test-BtpCli {
    try {
        $btpVersion = btp --version 2>&1
        Write-Log "BTP CLI is installed: $btpVersion"
        return $true
    }
    catch {
        Write-Log "BTP CLI is not installed or not in PATH. Please install it first." -Level "ERROR"
        Write-Log "Download from: https://tools.hana.ondemand.com/#cloud-btpcli" -Level "ERROR"
        return $false
    }
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

# Function to acquire CF UAA OAuth token 
function Get-CfUaaToken {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Username,
        
        [Parameter(Mandatory=$true)]
        [SecureString]$Password,
        
        [Parameter(Mandatory=$true)]
        [string]$Region
    )
    
    try {
        Write-Log "Acquiring CF UAA OAuth token for region $Region..."
        
        $cfUaaEndpoint = "https://login.cf.$Region.hana.ondemand.com/oauth/token"
        
        # Convert SecureString to plain text for API call
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
        $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
        
        $body = @{
            username = $Username
            password = $plainPassword
            client_id = "cf"
            grant_type = "password"
            response_type = "token"
        }
        
        # Clear password from memory
        $plainPassword = $null
        
        # Basic Auth: cf: (empty password)
        $basicAuth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("cf:"))
        
        $headers = @{
            "Authorization" = "Basic $basicAuth"
            "Content-Type" = "application/x-www-form-urlencoded"
        }
        
        $response = Invoke-RestMethod -Uri $cfUaaEndpoint `
            -Method Post `
            -Headers $headers `
            -Body $body `
            -ErrorAction Stop
        
        Write-Log "CF UAA token acquired successfully (expires in $($response.expires_in)s)" -Level "SUCCESS"
        
        return @{
            AccessToken = $response.access_token
            TokenType = $response.token_type
            ExpiresIn = $response.expires_in
        }
    }
    catch {
        Write-Log "Failed to acquire CF UAA token: $($_.Exception.Message)" -Level "ERROR"
        return $null
    }
}

# Function to make authenticated CF API calls
function Invoke-CfApi {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CfApiEndpoint,
        
        [Parameter(Mandatory=$true)]
        [string]$AccessToken,
        
        [Parameter(Mandatory=$true)]
        [string]$Path,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("GET", "POST", "DELETE", "PATCH")]
        [string]$Method = "GET",
        
        [Parameter(Mandatory=$false)]
        [object]$Body = $null
    )
    
    try {
        $headers = @{
            "Authorization" = "Bearer $AccessToken"
            "Content-Type" = "application/json"
        }
        
        $uri = "$CfApiEndpoint$Path"
        
        $params = @{
            Uri = $uri
            Method = $Method
            Headers = $headers
            ErrorAction = "Stop"
            StatusCodeVariable = "statusCode"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        
        # For successful operations that return no body (like 202 Accepted), return a success indicator
        if (-not $response -and $statusCode -ge 200 -and $statusCode -lt 300) {
            return @{ Success = $true; StatusCode = $statusCode }
        }
        
        return $response
    }
    catch {
        $errorMessage = $_.Exception.Message
        if ($_.ErrorDetails.Message) {
            $errorMessage = $_.ErrorDetails.Message
        }
        Write-Log "CF API call failed ($Method $Path): $errorMessage" -Level "ERROR"
        return $null
    }
}

# Function to validate and prompt for CF credentials
function Get-CfCredentials {
    param(
        [string]$Username,
        [SecureString]$Password
    )
    
    # Debug: Check what we received
    $passwordProvided = $null -ne $Password -and $Password.Length -gt 0
    Write-Host "DEBUG: Username: '$Username'" -ForegroundColor Cyan
    Write-Host "DEBUG: Password provided: $passwordProvided" -ForegroundColor Cyan
    if ($null -ne $Password) {
        Write-Host "DEBUG: Password type: $($Password.GetType().Name), Length: $($Password.Length)" -ForegroundColor Cyan
    }
    
    # Convert password from environment variable if not provided as parameter
    if (($null -eq $Password -or $Password.Length -eq 0) -and -not [string]::IsNullOrWhiteSpace($env:CF_PASSWORD)) {
        Write-Host "DEBUG: Converting from CF_PASSWORD environment variable" -ForegroundColor Cyan
        $Password = ConvertTo-SecureString -String $env:CF_PASSWORD -AsPlainText -Force
        # Clear environment variable for security
        Remove-Item Env:\CF_PASSWORD -ErrorAction SilentlyContinue
    }
    
    # Validate and prompt if credentials are missing
    if ([string]::IsNullOrWhiteSpace($Username) -or $null -eq $Password -or $Password.Length -eq 0) {
        Write-Host "" -ForegroundColor Yellow
        Write-Host "WARNING: CF credentials not fully provided." -ForegroundColor Yellow
        Write-Host "The script requires Cloud Foundry credentials to authenticate." -ForegroundColor Yellow
        Write-Host "" -ForegroundColor Yellow
        Write-Host "Please provide credentials using one of these methods:" -ForegroundColor Yellow
        Write-Host "  1. Parameters: -CfUsername 'user' -CfPassword `$securePassword" -ForegroundColor Cyan
        Write-Host "  2. Environment variables: CF_USERNAME and CF_PASSWORD" -ForegroundColor Cyan
        Write-Host "  3. Interactive prompt (press Enter to continue)" -ForegroundColor Cyan
        Write-Host "" -ForegroundColor Yellow
        
        $response = Read-Host "Press Enter to provide credentials interactively, or Ctrl+C to exit"
        
        if ([string]::IsNullOrWhiteSpace($Username)) {
            $Username = Read-Host "Enter CF Username"
        }
        
        if ($null -eq $Password) {
            $Password = Read-Host "Enter CF Password" -AsSecureString
        }
        
        if ([string]::IsNullOrWhiteSpace($Username) -or $null -eq $Password) {
            Write-Log "Credentials not provided. Exiting." -Level "ERROR"
            return $null
        }
    }
    
    return @{
        Username = $Username
        Password = $Password
    }
}

# Function to validate and prompt for BTP CLI credentials
function Get-BtpCredentials {
    param(
        [string]$Username,
        [SecureString]$Password,
        [string]$Subdomain
    )
    
    # Convert password from environment variable if not provided as parameter
    if (($null -eq $Password -or $Password.Length -eq 0) -and -not [string]::IsNullOrWhiteSpace($env:BTP_PASSWORD)) {
        $Password = ConvertTo-SecureString -String $env:BTP_PASSWORD -AsPlainText -Force
        # Clear environment variable for security
        Remove-Item Env:\BTP_PASSWORD -ErrorAction SilentlyContinue
    }
    
    # Validate and prompt if credentials are missing
    if ([string]::IsNullOrWhiteSpace($Username) -or $null -eq $Password -or $Password.Length -eq 0 -or [string]::IsNullOrWhiteSpace($Subdomain)) {
        Write-Host "" -ForegroundColor Yellow
        Write-Host "WARNING: BTP credentials not fully provided." -ForegroundColor Yellow
        Write-Host "The script requires BTP CLI credentials to authenticate." -ForegroundColor Yellow
        Write-Host "" -ForegroundColor Yellow
        Write-Host "Please provide credentials using one of these methods:" -ForegroundColor Yellow
        Write-Host "  1. Parameters: -BtpUsername 'user' -BtpPassword `$securePassword -BtpSubdomain 'subdomain'" -ForegroundColor Cyan
        Write-Host "  2. Environment variables: BTP_USERNAME, BTP_PASSWORD, and BTP_SUBDOMAIN" -ForegroundColor Cyan
        Write-Host "  3. Interactive prompt (press Enter to continue)" -ForegroundColor Cyan
        Write-Host "" -ForegroundColor Yellow
        
        Read-Host "Press Enter to provide credentials interactively, or Ctrl+C to exit" | Out-Null
        
        if ([string]::IsNullOrWhiteSpace($Username)) {
            $Username = Read-Host "Enter BTP Username (email)"
        }
        
        if ($null -eq $Password -or $Password.Length -eq 0) {
            $Password = Read-Host "Enter BTP Password" -AsSecureString
        }
        
        if ([string]::IsNullOrWhiteSpace($Subdomain)) {
            $Subdomain = Read-Host "Enter BTP Global Account Subdomain"
        }
        
        if ([string]::IsNullOrWhiteSpace($Username) -or $null -eq $Password -or [string]::IsNullOrWhiteSpace($Subdomain)) {
            Write-Log "Credentials not provided. Exiting." -Level "ERROR"
            return $null
        }
    }
    
    return @{
        Username = $Username
        Password = $Password
        Subdomain = $Subdomain
    }
}

# Function to perform CF authentication using OAuth
function Invoke-CfLogin {
    param(
        [string]$ApiEndpoint,
        [string]$Username,
        [SecureString]$Password,
        [string]$OrgName = "",
        [string]$SpaceName = "",
        [string]$Region = ""
    )
    
    try {
        if ([string]::IsNullOrWhiteSpace($Username) -or $null -eq $Password) {
            Write-Log "CF credentials missing for login attempt." -Level "ERROR"
            return $false
        }
        
        # Extract region from API endpoint if not provided
        if ([string]::IsNullOrWhiteSpace($Region) -and $ApiEndpoint -match '\.cf\.([^.]+)\.') {
            $Region = $matches[1]
            Write-Log "Extracted region from API endpoint: $Region"
        }
        
        if ([string]::IsNullOrWhiteSpace($Region)) {
            Write-Log "Cannot determine CF region for OAuth authentication" -Level "ERROR"
            return $false
        }
        
        Write-Log "Authenticating to Cloud Foundry API: $ApiEndpoint using OAuth"
        
        $tokenInfo = Get-CfUaaToken -Username $Username -Password $Password -Region $Region
        
        if ($null -eq $tokenInfo) {
            Write-Log "Failed to acquire CF OAuth token" -Level "ERROR"
            return $false
        }
        
        $script:CfAccessToken = $tokenInfo.AccessToken
        $script:CfApiEndpoint = $ApiEndpoint
        $script:CfOrgName = $OrgName
        $script:CfSpaceName = $SpaceName
        
        Write-Log "Successfully authenticated to Cloud Foundry using OAuth" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Error during authentication: $_" -Level "ERROR"
        return $false
    }
}

# Function to perform BTP CLI login with credentials
function Invoke-BtpLogin {
    param(
        [string]$Username,
        [SecureString]$Password,
        [string]$Subdomain,
        [string]$Url = "https://cli.btp.cloud.sap"
    )
    
    try {
        if ([string]::IsNullOrWhiteSpace($Username) -or $null -eq $Password -or [string]::IsNullOrWhiteSpace($Subdomain)) {
            Write-Log "BTP credentials missing for login attempt." -Level "ERROR"
            Write-Log "Username provided: $(-not [string]::IsNullOrWhiteSpace($Username))" -Level "ERROR"
            Write-Log "Password provided: $($null -ne $Password)" -Level "ERROR"
            Write-Log "Subdomain provided: $(-not [string]::IsNullOrWhiteSpace($Subdomain))" -Level "ERROR"
            return $false
        }
        
        Write-Log "Authenticating to BTP CLI (subdomain: $Subdomain, url: $Url)"
        
        # Convert SecureString to plain text for BTP CLI (only in memory during login)
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
        $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
        
        # Execute btp login command
        # BTP CLI login format: btp login --url <url> --subdomain <subdomain> --user <username> --password <password>
        $result = btp login --url $Url --subdomain $Subdomain --user $Username --password $plainPassword 2>&1
        
        # Clear the password from memory immediately
        $plainPassword = $null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully authenticated to BTP CLI" -Level "SUCCESS"
            return $true
        }
        else {
            Write-Log "BTP authentication failed: $result" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error during BTP authentication: $_" -Level "ERROR"
        return $false
    }
    finally {
        # Ensure password is cleared from memory
        if ($plainPassword) {
            $plainPassword = $null
        }
    }
}

# Function to switch CF API endpoint and authenticate (OAuth-based)
function Set-CfApiEndpoint {
    param(
        [string]$ApiEndpoint,
        [string]$Username,
        [SecureString]$Password,
        [string]$OrgName = "",
        [string]$SpaceName = ""
    )
    
    try {
        # Extract region from API endpoint
        $region = $null
        if ($ApiEndpoint -match '\.cf\.([^.]+)\.') {
            $region = $matches[1]
        }
        
        if ([string]::IsNullOrWhiteSpace($region)) {
            Write-Log "Cannot extract region from API endpoint: $ApiEndpoint" -Level "ERROR"
            return $false
        }
        
        # Check if already authenticated to this endpoint
        if ($script:CfApiEndpoint -eq $ApiEndpoint -and $script:CfAccessToken) {
            Write-Log "Already authenticated to API endpoint: $ApiEndpoint"
            return $true
        }
        
        Write-Log "Authenticating to API endpoint: $ApiEndpoint"
        
        # Authenticate using OAuth
        if (-not (Invoke-CfLogin -ApiEndpoint $ApiEndpoint -Username $Username -Password $Password -OrgName $OrgName -SpaceName $SpaceName -Region $region)) {
            Write-Log "Failed to authenticate to API endpoint" -Level "ERROR"
            return $false
        }
        
        return $true
    }
    catch {
        Write-Log "Error switching API endpoint: $_" -Level "ERROR"
        return $false
    }
}

# Function to target CF org and space
function Set-CfTarget {
    param(
        [string]$OrgName,
        [string]$SpaceName
    )
    
    try {
        Write-Log "Setting target org: '$OrgName', space: '$SpaceName'"
        
        # Update script scope variables (used by CF API calls)
        $script:CfOrgName = $OrgName
        $script:CfSpaceName = $SpaceName
        
        Write-Log "Successfully set target org/space" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Error targeting org/space: $_" -Level "ERROR"
        return $false
    }
}

# Helper function to get CF Space ID from org name and space name
function Get-CfSpaceId {
    param(
        [Parameter(Mandatory=$true)]
        [string]$OrgName,
        
        [Parameter(Mandatory=$false)]
        [string]$SpaceName = ""
    )
    
    try {
        # First, get the org ID
        $orgsResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/organizations?names=$OrgName"
        
        if (-not $orgsResponse -or $orgsResponse.pagination.total_results -eq 0) {
            Write-Log "Org '$OrgName' not found" -Level "ERROR"
            return $null
        }
        
        $orgId = $orgsResponse.resources[0].guid
        
        # Get spaces in this org
        $spacePath = "/v3/spaces?organization_guids=$orgId"
        if (-not [string]::IsNullOrWhiteSpace($SpaceName)) {
            $spacePath += "&names=$SpaceName"
        }
        
        $spacesResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path $spacePath
        
        if (-not $spacesResponse -or $spacesResponse.pagination.total_results -eq 0) {
            Write-Log "Space '$SpaceName' not found in org '$OrgName'" -Level "ERROR"
            return $null
        }
        
        # Return first space (or specified space)
        return $spacesResponse.resources[0].guid
    }
    catch {
        Write-Log "Error getting space ID: $_" -Level "ERROR"
        return $null
    }
}

# Function to discover service instances by offering type
function Get-CfServiceKeys {
    param(
        [Parameter(Mandatory=$true)]
        [string]$InstanceName
    )
    
    try {
        Write-Log "Listing service keys for instance '$InstanceName'..."
        
        # Get space ID
        if ([string]::IsNullOrWhiteSpace($script:CfOrgName) -or [string]::IsNullOrWhiteSpace($script:CfSpaceName)) {
            Write-Log "CF org/space not set. Call Set-CfTarget first." -Level "ERROR"
            return @()
        }
        
        $spaceId = Get-CfSpaceId -OrgName $script:CfOrgName -SpaceName $script:CfSpaceName
        if (-not $spaceId) {
            return @()
        }
        
        # Get service instance GUID by name
        $instancesResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_instances?space_guids=$spaceId&names=$InstanceName"
        
        if (-not $instancesResponse -or $instancesResponse.pagination.total_results -eq 0) {
            Write-Log "Service instance '$InstanceName' not found" -Level "ERROR"
            return @()
        }
        
        $instanceGuid = $instancesResponse.resources[0].guid
        
        # Get service credential bindings (keys) for this instance
        $keysResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_credential_bindings?service_instance_guids=$instanceGuid&type=key"
        
        if (-not $keysResponse) {
            Write-Log "Failed to list service keys" -Level "ERROR"
            return @()
        }
        
        # Extract key names
        $keyNames = @($keysResponse.resources | ForEach-Object { $_.name })
        
        if ($keyNames.Count -gt 0) {
            Write-Log "Found $($keyNames.Count) service key(s)" -Level "SUCCESS"
        }
        else {
            Write-Log "No service keys found for instance '$InstanceName'" -Level "INFO"
        }
        
        return $keyNames
    }
    catch {
        Write-Log "Error listing service keys: $_" -Level "ERROR"
        return @()
    }
}

# Function to list service keys with full details
function Get-CfServiceKeysWithDetails {
    param(
        [Parameter(Mandatory=$true)]
        [string]$InstanceName
    )
    
    try {
        # Get space ID
        if ([string]::IsNullOrWhiteSpace($script:CfOrgName) -or [string]::IsNullOrWhiteSpace($script:CfSpaceName)) {
            Write-Log "CF org/space not set. Call Set-CfTarget first." -Level "ERROR"
            return @()
        }
        
        $spaceId = Get-CfSpaceId -OrgName $script:CfOrgName -SpaceName $script:CfSpaceName
        if (-not $spaceId) {
            return @()
        }
        
        # Get service instance GUID by name
        $instancesResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_instances?space_guids=$spaceId&names=$InstanceName"
        
        if (-not $instancesResponse -or $instancesResponse.pagination.total_results -eq 0) {
            Write-Log "Service instance '$InstanceName' not found" -Level "ERROR"
            return @()
        }
        
        $instanceGuid = $instancesResponse.resources[0].guid
        
        # Get service credential bindings (keys) with full details
        $keysResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_credential_bindings?service_instance_guids=$instanceGuid&type=key"
        
        if (-not $keysResponse) {
            Write-Log "Failed to list service keys" -Level "ERROR"
            return @()
        }
        
        # Return full key objects (includes guid, name, created_at, updated_at)
        return @($keysResponse.resources)
    }
    catch {
        Write-Log "Error listing service keys with details: $_" -Level "ERROR"
        return @()
    }
}

# Function to get CF service key and parse JSON
function Get-CfServiceKey {
    param(
        [string]$InstanceName,
        [string]$KeyName,
        [int]$MaxRetries = 5,
        [int]$InitialDelaySeconds = 2
    )
    
    try {
        Write-Log "Retrieving service key '$KeyName' for instance '$InstanceName'..."
        
        # Get space ID
        if ([string]::IsNullOrWhiteSpace($script:CfOrgName) -or [string]::IsNullOrWhiteSpace($script:CfSpaceName)) {
            Write-Log "CF org/space not set. Call Set-CfTarget first." -Level "ERROR"
            return $null
        }
        
        $spaceId = Get-CfSpaceId -OrgName $script:CfOrgName -SpaceName $script:CfSpaceName
        if (-not $spaceId) {
            return $null
        }
        
        # Get service instance GUID
        $instancesResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_instances?space_guids=$spaceId&names=$InstanceName"
        
        if (-not $instancesResponse -or $instancesResponse.pagination.total_results -eq 0) {
            Write-Log "Service instance '$InstanceName' not found" -Level "ERROR"
            return $null
        }
        
        $instanceGuid = $instancesResponse.resources[0].guid
        
        # Get service credential binding (key) by name
        $keysResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_credential_bindings?service_instance_guids=$instanceGuid&type=key&names=$KeyName"
        
        if (-not $keysResponse -or $keysResponse.pagination.total_results -eq 0) {
            Write-Log "Service key '$KeyName' not found" -Level "ERROR"
            return $null
        }
        
        $keyGuid = $keysResponse.resources[0].guid
        
        # Get key details (credentials) with retry logic for async provisioning
        $attempt = 0
        $delaySeconds = $InitialDelaySeconds
        $keyDetailsResponse = $null
        
        while ($attempt -lt $MaxRetries) {
            $attempt++
            
            $keyDetailsResponse = Invoke-CfApi `
                -CfApiEndpoint $script:CfApiEndpoint `
                -AccessToken $script:CfAccessToken `
                -Path "/v3/service_credential_bindings/$keyGuid/details"
            
            # Check if we got a valid response
            if ($keyDetailsResponse -and $keyDetailsResponse.credentials) {
                break
            }
            
            # If this was the last attempt, fail
            if ($attempt -ge $MaxRetries) {
                Write-Log "Failed to retrieve key credentials after $MaxRetries attempts" -Level "ERROR"
                return $null
            }
            
            # Key might still be provisioning - wait with exponential backoff
            Write-Log "Key provisioning in progress (attempt $attempt/$MaxRetries). Waiting $delaySeconds seconds..." -Level "WARNING"
            Start-Sleep -Seconds $delaySeconds
            
            # Exponential backoff: 2, 4, 8, 16 seconds
            $delaySeconds = $delaySeconds * 2
        }
        
        if (-not $keyDetailsResponse) {
            Write-Log "Failed to retrieve key credentials" -Level "ERROR"
            return $null
        }
        
        Write-Log "Successfully retrieved service key (attempt $attempt/$MaxRetries)" -Level "SUCCESS"
        
        # CF API v3 returns credentials directly in the response (no .credentials wrapper)
        # Return the entire response as it contains the credentials
        return $keyDetailsResponse
    }
    catch {
        Write-Log "Error retrieving service key: $_" -Level "ERROR"
        return $null
    }
}

# Function to validate and extract BTP service key credentials
function Get-BtpServiceKeyCredentials {
    param(
        [Parameter(Mandatory=$true)]
        [object]$ServiceKey
    )
    
    try {
        # CF API v3 returns credentials directly (no wrapper), but structure may vary
        # Try to detect if this is wrapped in .credentials or not
        $credentials = $ServiceKey
        
        # If it has a .credentials property, use that (legacy format)
        if ($null -ne $ServiceKey.credentials) {
            $credentials = $ServiceKey.credentials
        }
        
        # Validate required fields - check both direct access and .uaa nested access
        $clientId = $null
        $clientSecret = $null
        $uaaUrl = $null
        $apiUrl = $null
        
        # Try direct access first (CF API v3 format)
        if ($credentials.uaa) {
            $clientId = $credentials.uaa.clientid
            $clientSecret = $credentials.uaa.clientsecret
            $uaaUrl = $credentials.uaa.url
            $apiUrl = $credentials.url
        }
        # Fallback to old nested format if needed
        elseif ($credentials.clientid) {
            $clientId = $credentials.clientid
            $clientSecret = $credentials.clientsecret
            $uaaUrl = $credentials.url
            $apiUrl = $credentials.url
        }
        
        if ([string]::IsNullOrWhiteSpace($clientId)) {
            Write-Log "Service key missing UAA client ID" -Level "ERROR"
            Write-Log "Service key structure: $($ServiceKey | ConvertTo-Json -Depth 3)" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($clientSecret)) {
            Write-Log "Service key missing UAA client secret" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($uaaUrl)) {
            Write-Log "Service key missing UAA URL" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($apiUrl)) {
            Write-Log "Service key missing audit log API URL" -Level "ERROR"
            return $null
        }
        
        # Extract subdomain from UAA URL (e.g., https://subdomain.authentication.region.hana.ondemand.com)
        $subdomain = ""
        if ($uaaUrl -match "https?://([^.]+)\..*") {
            $subdomain = $matches[1]
        }
        
        # Extract subaccount ID
        $subaccountId = $credentials.uaa.subaccountid
        if ([string]::IsNullOrWhiteSpace($subaccountId)) {
            $subaccountId = $credentials.subaccountid
        }
        
        # Return validated credentials object
        # Note: Full OAuth token endpoint path with grant_type parameter is required
        return @{
            ClientId = $clientId
            ClientSecret = $clientSecret
            TokenEndpoint = "$uaaUrl/oauth/token?grant_type=client_credentials"
            ApiUrl = $apiUrl
            SubaccountId = $subaccountId
            Subdomain = $subdomain
        }
    }
    catch {
        Write-Log "Error extracting service key credentials: $_" -Level "ERROR"
        return $null
    }
}

# Function to build SAP BTP data connector connection request body
function New-BtpConnectionRequestBody {
    param(
        [Parameter(Mandatory=$true)]
        [object]$BtpCredentials,

        [Parameter(Mandatory=$true)]
        [object]$DcrConfig,

        [Parameter(Mandatory=$false)]
        [string]$SubaccountName = "Unknown",
        
        [Parameter(Mandatory=$false)]
        [int]$PollingFrequencyMinutes = 1,
        
        [Parameter(Mandatory=$false)]
        [int]$IngestDelayMinutes = 20
    )
    
    try {
        # Validate DcrConfig
        if ($null -eq $DcrConfig -or
            [string]::IsNullOrWhiteSpace($DcrConfig.DataCollectionEndpoint) -or
            [string]::IsNullOrWhiteSpace($DcrConfig.DataCollectionRuleImmutableId)) {
            Write-Log "DcrConfig is required with DataCollectionEndpoint and DataCollectionRuleImmutableId" -Level "ERROR"
            return $null
        }
        
        # Build API endpoint for audit log records
        $apiEndpoint = "$($BtpCredentials.ApiUrl)/auditlog/v2/auditlogrecords"
        
        # Build request body matching SAPBTP_PollingConfig.json template
        $body = @{
            kind = "RestApiPoller"
            properties = @{
                connectorDefinitionName = "SAPBTPAuditEvents"
                dataType = "SAPBTPAuditLog_CL"
                # DCR configuration required for data ingestion via Azure Monitor Logs Ingestion API
                dcrConfig = @{
                    dataCollectionEndpoint = $DcrConfig.DataCollectionEndpoint
                    dataCollectionRuleImmutableId = $DcrConfig.DataCollectionRuleImmutableId
                    streamName = "Custom-SAPBTPAuditLog_CL"
                }
                addOnAttributes = @{
                    SubaccountName = if ([string]::IsNullOrWhiteSpace($SubaccountName)) { "Unknown" } else { $SubaccountName }
                }
                auth = @{
                    type = "OAuth2"
                    ClientId = $BtpCredentials.ClientId
                    ClientSecret = $BtpCredentials.ClientSecret
                    TokenEndpoint = $BtpCredentials.TokenEndpoint
                    GrantType = "client_credentials"
                    TokenEndpointHeaders = @{
                        "Content-Type" = "application/x-www-form-urlencoded"
                    }
                }
                request = @{
                    apiEndpoint = $apiEndpoint
                    httpMethod = "Get"
                    queryWindowInMin = $PollingFrequencyMinutes
                    queryWindowDelayInMin = $IngestDelayMinutes
                    queryTimeFormat = "yyyy-MM-ddTHH:mm:ss.fff"
                    retryCount = 3
                    timeoutInSeconds = 120
                    startTimeAttributeName = "time_from"
                    endTimeAttributeName = "time_to"
                    headers = @{
                        "Accept" = "application/json"
                        "User-Agent" = "Scuba"
                    }
                }
                response = @{
                    eventsJsonPaths = @('$')
                }
                paging = @{
                    pagingType = "NextPageToken"
                    nextPageTokenResponseHeader = "paging"
                    nextPageParaName = "handle"
                    tokenTransform = @{
                        TransformType = "SplitOnDelimiter"
                        SliceDelimiter = "="
                        StringIndex = 1
                    }
                }
                isActive = $true
            }
        }
        
        Write-Log "Built connection request body with DCR configuration"
        
        return $body
    }
    catch {
        Write-Log "Error building connection request body: $_" -Level "ERROR"
        return $null
    }
}

# Function to create CF service instance
function New-CfServiceInstance {
    param(
        [string]$InstanceName,
        [string]$Service,
        [string]$Plan
    )
    
    try {
        Write-Log "Creating service instance '$InstanceName' with service '$Service' and plan '$Plan'..."
        
        # Get space ID
        if ([string]::IsNullOrWhiteSpace($script:CfOrgName) -or [string]::IsNullOrWhiteSpace($script:CfSpaceName)) {
            Write-Log "CF org/space not set. Call Set-CfTarget first." -Level "ERROR"
            return $false
        }
        
        $spaceId = Get-CfSpaceId -OrgName $script:CfOrgName -SpaceName $script:CfSpaceName
        if (-not $spaceId) {
            return $false
        }
        
        # Check if service instance already exists
        $existingResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_instances?space_guids=$spaceId&names=$InstanceName"
        
        if ($existingResponse -and $existingResponse.pagination.total_results -gt 0) {
            Write-Log "Service instance '$InstanceName' already exists. Skipping creation." -Level "WARNING"
            return $true
        }
        
        # Get service offering and plan GUIDs
        # First, get service offerings
        $offeringsResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_offerings?names=$Service"
        
        if (-not $offeringsResponse -or $offeringsResponse.pagination.total_results -eq 0) {
            Write-Log "Service offering '$Service' not found" -Level "ERROR"
            return $false
        }
        
        $serviceOfferingGuid = $offeringsResponse.resources[0].guid
        
        # Get service plan
        $plansResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_plans?service_offering_guids=$serviceOfferingGuid&names=$Plan"
        
        if (-not $plansResponse -or $plansResponse.pagination.total_results -eq 0) {
            Write-Log "Service plan '$Plan' not found for service '$Service'" -Level "ERROR"
            return $false
        }
        
        $servicePlanGuid = $plansResponse.resources[0].guid
        
        # Create service instance
        $createBody = @{
            type = "managed"
            name = $InstanceName
            relationships = @{
                space = @{
                    data = @{
                        guid = $spaceId
                    }
                }
                service_plan = @{
                    data = @{
                        guid = $servicePlanGuid
                    }
                }
            }
        }
        
        $createResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_instances" `
            -Method "POST" `
            -Body $createBody
        
        if ($createResponse -and ($createResponse.Success -eq $true -or $createResponse.guid)) {
            Write-Log "Successfully initiated creation of service instance '$InstanceName'" -Level "SUCCESS"
            Write-Log "Note: Service instance creation is asynchronous. It may take a few minutes to complete." -Level "INFO"
            return $true
        }
        else {
            Write-Log "Failed to create service instance '$InstanceName' - check error details above" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error creating service instance: $_" -Level "ERROR"
        return $false
    }
}

# Function to create CF service key (CF API-based)
function New-CfServiceKey {
    param(
        [string]$InstanceName,
        [string]$KeyName
    )
    
    try {
        Write-Log "Creating service key '$KeyName' for service instance '$InstanceName'..."
        
        # Get space ID
        if ([string]::IsNullOrWhiteSpace($script:CfOrgName) -or [string]::IsNullOrWhiteSpace($script:CfSpaceName)) {
            Write-Log "CF org/space not set. Call Set-CfTarget first." -Level "ERROR"
            return $false
        }
        
        $spaceId = Get-CfSpaceId -OrgName $script:CfOrgName -SpaceName $script:CfSpaceName
        if (-not $spaceId) {
            return $false
        }
        
        # Get service instance GUID
        $instancesResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_instances?space_guids=$spaceId&names=$InstanceName"
        
        if (-not $instancesResponse -or $instancesResponse.pagination.total_results -eq 0) {
            Write-Log "Service instance '$InstanceName' not found" -Level "ERROR"
            return $false
        }
        
        $instanceGuid = $instancesResponse.resources[0].guid
        
        # Check if key already exists
        $existingKeysResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_credential_bindings?service_instance_guids=$instanceGuid&type=key&names=$KeyName"
        
        if ($existingKeysResponse -and $existingKeysResponse.pagination.total_results -gt 0) {
            Write-Log "Service key '$KeyName' already exists. Skipping creation." -Level "WARNING"
            return $true
        }
        
        # Create the service key
        $createKeyBody = @{
            type = "key"
            name = $KeyName
            relationships = @{
                service_instance = @{
                    data = @{
                        guid = $instanceGuid
                    }
                }
            }
        }
        
        $newKeyResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_credential_bindings" `
            -Method "POST" `
            -Body $createKeyBody
        
        if ($newKeyResponse -and ($newKeyResponse.Success -eq $true -or $newKeyResponse.guid)) {
            Write-Log "Successfully created service key '$KeyName'" -Level "SUCCESS"
            return $true
        }
        else {
            Write-Log "Failed to create service key '$KeyName' - check error details above" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error creating service key: $_" -Level "ERROR"
        return $false
    }
}

# Function to delete CF service key (CF API-based)
function Remove-CfServiceKey {
    param(
        [Parameter(Mandatory=$true)]
        [string]$KeyGuid,
        
        [Parameter(Mandatory=$false)]
        [string]$KeyName = "Unknown"
    )
    
    try {
        Write-Log "Deleting service key '$KeyName' (GUID: $KeyGuid)..."
        
        $deleteResponse = Invoke-CfApi `
            -CfApiEndpoint $script:CfApiEndpoint `
            -AccessToken $script:CfAccessToken `
            -Path "/v3/service_credential_bindings/$KeyGuid" `
            -Method "DELETE"
        
        if ($deleteResponse -and ($deleteResponse.Success -eq $true -or $deleteResponse.guid)) {
            Write-Log "Successfully deleted service key '$KeyName'" -Level "SUCCESS"
            return $true
        }
        else {
            Write-Log "Failed to delete service key '$KeyName'" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error deleting service key: $_" -Level "ERROR"
        return $false
    }
}

# Function to load and validate CSV with required columns
function Import-BtpSubaccountsCsv {
    param(
        [string]$CsvPath,
        [string[]]$RequiredColumns = @("SubaccountId", "cf-api-endpoint", "cf-org-name", "cf-space-name")
    )
    
    try {
        if (-not (Test-Path $CsvPath)) {
            Write-Log "CSV file not found at path: $CsvPath" -Level "ERROR"
            return $null
        }
        
        Write-Log "Loading subaccounts from CSV file: $CsvPath"
        $subaccounts = Import-Csv -Path $CsvPath -Delimiter ';'
        Write-Log "Found $($subaccounts.Count) subaccount(s) to process"
        
        # Validate CSV has required columns
        $csvColumns = $subaccounts[0].PSObject.Properties.Name
        
        foreach ($column in $RequiredColumns) {
            if ($column -notin $csvColumns) {
                Write-Log "CSV file must contain '$column' column" -Level "ERROR"
                return $null
            }
        }
        
        return $subaccounts
    }
    catch {
        Write-Log "Error reading CSV file: $_" -Level "ERROR"
        return $null
    }
}

# Function to export BTP subaccounts to CSV
function Export-BtpSubaccountsCsv {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Subaccounts,
        
        [Parameter(Mandatory=$true)]
        [string]$CsvPath,
        
        [Parameter(Mandatory=$false)]
        [switch]$Append
    )
    
    try {
        if ($Subaccounts.Count -eq 0) {
            Write-Log "No subaccounts to export" -Level "WARNING"
            return $false
        }
        
        Write-Log "Exporting $($Subaccounts.Count) subaccount(s) to: $CsvPath"
        
        if ($Append -and (Test-Path $CsvPath)) {
            # Load existing data
            $existing = Import-Csv -Path $CsvPath -Delimiter ';'
            
            # Merge with new data (avoiding duplicates based on SubaccountId)
            $existingIds = $existing | ForEach-Object { $_.SubaccountId }
            $newSubaccounts = $Subaccounts | Where-Object { $_.SubaccountId -notin $existingIds }
            
            if ($newSubaccounts.Count -eq 0) {
                Write-Log "No new subaccounts to add (all already exist in CSV)" -Level "INFO"
                return $true
            }
            else {
                $combined = $existing + $newSubaccounts
                $combined | Export-Csv -Path $CsvPath -Delimiter ';' -NoTypeInformation
                Write-Log "Appended $($newSubaccounts.Count) new subaccount(s)" -Level "SUCCESS"
                return $true
            }
        }
        else {
            # Create new file
            $Subaccounts | Export-Csv -Path $CsvPath -Delimiter ';' -NoTypeInformation
            Write-Log "Successfully exported $($Subaccounts.Count) subaccount(s) to CSV" -Level "SUCCESS"
            return $true
        }
    }
    catch {
        Write-Log "Error exporting to CSV: $_" -Level "ERROR"
        return $false
    }
}

# Function to export service key credentials to CSV (for split permissions scenarios)
# WARNING: This stores sensitive credentials in plaintext. Use only for testing or with secure file transfer.
function Export-ServiceKeyToCsv {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CsvPath,
        
        [Parameter(Mandatory=$true)]
        [string]$SubaccountId,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Credentials
    )
    
    try {
        if (-not (Test-Path $CsvPath)) {
            Write-Log "CSV file not found at path: $CsvPath" -Level "ERROR"
            return $false
        }
        
        Write-Log "Exporting service key credentials for subaccount '$SubaccountId' to CSV..."
        
        # Load existing CSV
        $csvData = Import-Csv -Path $CsvPath -Delimiter ';'
        
        # Find the row matching this subaccount
        $updated = $false
        foreach ($row in $csvData) {
            if ($row.SubaccountId -eq $SubaccountId) {
                # Add credential columns to this row
                $row | Add-Member -NotePropertyName 'ClientId' -NotePropertyValue $Credentials.ClientId -Force
                $row | Add-Member -NotePropertyName 'ClientSecret' -NotePropertyValue $Credentials.ClientSecret -Force
                $row | Add-Member -NotePropertyName 'TokenEndpoint' -NotePropertyValue $Credentials.TokenEndpoint -Force
                $row | Add-Member -NotePropertyName 'ApiUrl' -NotePropertyValue $Credentials.ApiUrl -Force
                $row | Add-Member -NotePropertyName 'Subdomain' -NotePropertyValue $Credentials.Subdomain -Force
                $updated = $true
                Write-Log "Updated credentials for subaccount '$SubaccountId'" -Level "SUCCESS"
                break
            }
        }
        
        if (-not $updated) {
            Write-Log "Subaccount '$SubaccountId' not found in CSV" -Level "ERROR"
            return $false
        }
        
        # Write back to CSV
        $csvData | Export-Csv -Path $CsvPath -Delimiter ';' -NoTypeInformation
        Write-Log "Successfully exported credentials to CSV" -Level "SUCCESS"
        Write-Log "WARNING: CSV contains sensitive credentials in plaintext. Secure this file appropriately." -Level "WARNING"
        
        return $true
    }
    catch {
        Write-Log "Error exporting service key to CSV: $_" -Level "ERROR"
        return $false
    }
}

# Function to import service key credentials from CSV (for split permissions scenarios)
function Get-ServiceKeyFromCsv {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CsvPath,
        
        [Parameter(Mandatory=$true)]
        [string]$SubaccountId
    )
    
    try {
        if (-not (Test-Path $CsvPath)) {
            Write-Log "CSV file not found at path: $CsvPath" -Level "ERROR"
            return $null
        }
        
        Write-Log "Loading service key credentials for subaccount '$SubaccountId' from CSV..."
        
        # Load CSV
        $csvData = Import-Csv -Path $CsvPath -Delimiter ';'
        
        # Find the row matching this subaccount
        $row = $csvData | Where-Object { $_.SubaccountId -eq $SubaccountId } | Select-Object -First 1
        
        if ($null -eq $row) {
            Write-Log "Subaccount '$SubaccountId' not found in CSV" -Level "ERROR"
            return $null
        }
        
        # Check if credential columns exist and are populated
        $requiredFields = @('ClientId', 'ClientSecret', 'TokenEndpoint', 'ApiUrl', 'Subdomain')
        $missingFields = @()
        
        foreach ($field in $requiredFields) {
            if (-not $row.PSObject.Properties.Name.Contains($field) -or 
                [string]::IsNullOrWhiteSpace($row.$field)) {
                $missingFields += $field
            }
        }
        
        if ($missingFields.Count -gt 0) {
            Write-Log "CSV row for subaccount '$SubaccountId' missing required credential fields: $($missingFields -join ', ')" -Level "ERROR"
            return $null
        }
        
        # Return credentials object matching the format from Get-BtpServiceKeyCredentials
        $credentials = @{
            ClientId = $row.ClientId
            ClientSecret = $row.ClientSecret
            TokenEndpoint = $row.TokenEndpoint
            ApiUrl = $row.ApiUrl
            SubaccountId = $SubaccountId
            Subdomain = $row.Subdomain
        }
        
        Write-Log "Successfully loaded credentials from CSV" -Level "SUCCESS"
        return $credentials
    }
    catch {
        Write-Log "Error reading service key from CSV: $_" -Level "ERROR"
        return $null
    }
}

# Function to export service key credentials to Azure Key Vault (for split permissions scenarios)
function Export-ServiceKeyToKeyVault {
    param(
        [Parameter(Mandatory=$true)]
        [string]$KeyVaultName,
        
        [Parameter(Mandatory=$true)]
        [string]$SubaccountId,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Credentials
    )
    
    try {
        Write-Log "Exporting service key credentials for subaccount '$SubaccountId' to Key Vault '$KeyVaultName'..."
        
        # Normalize subaccount ID for secret name (replace invalid characters)
        $normalizedId = $SubaccountId -replace '[^a-zA-Z0-9-]', '-'
        
        # Secret name: btp-{subaccount-id}
        $secretName = "btp-$normalizedId"
        
        # Create JSON object with all credentials
        $credentialsJson = @{
            ClientId = $Credentials.ClientId
            ClientSecret = $Credentials.ClientSecret
            TokenEndpoint = $Credentials.TokenEndpoint
            ApiUrl = $Credentials.ApiUrl
            Subdomain = $Credentials.Subdomain
        } | ConvertTo-Json -Compress
        
        # Store as single secret - use PowerShell's call operator with proper escaping
        Write-Log "Storing credentials as secret: $secretName"
        
        # Escape JSON for Azure CLI - need to escape double quotes
        $escapedJson = $credentialsJson.Replace('"', '\"')
        
        # Use az CLI with properly escaped JSON
        $result = az keyvault secret set --vault-name $KeyVaultName --name $secretName --value $escapedJson 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully stored credentials to Key Vault" -Level "SUCCESS"
            return $true
        } else {
            # Check for common permission errors
            $errorMessage = $result -join " "
            
            if ($errorMessage -match "Forbidden|ForbiddenByRbac|not authorized") {
                Write-Log "Access denied to Key Vault '$KeyVaultName'" -Level "ERROR"
                Write-Log "Please ensure your account has the 'Key Vault Secrets Officer' role assignment" -Level "ERROR"
                Write-Log "Run: az role assignment create --role 'Key Vault Secrets Officer' --assignee <your-email> --scope /subscriptions/$SubscriptionId/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/$KeyVaultName" -Level "ERROR"
            } elseif ($errorMessage -match "ObjectIsDeletedButRecoverable|deleted but recoverable") {
                Write-Log "Secret '$secretName' is in deleted state (soft-delete enabled)" -Level "WARNING"
                Write-Log "Purging and recreating..." -Level "INFO"
                
                # Purge the deleted secret
                $purgeResult = & az keyvault secret purge --vault-name $KeyVaultName --name $secretName 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Log "Successfully purged deleted secret" -Level "SUCCESS"
                    Start-Sleep -Seconds 2
                    
                    # Retry creation
                    $result = & az @azArgs 2>&1
                    
                    if ($LASTEXITCODE -eq 0) {
                        Write-Log "Successfully stored credentials to Key Vault" -Level "SUCCESS"
                        return $true
                    } else {
                        Write-Log "Failed to store secret after purge: $result" -Level "ERROR"
                        return $false
                    }
                } else {
                    Write-Log "Failed to purge secret: $purgeResult" -Level "ERROR"
                    Write-Log "Run: az keyvault secret purge --vault-name $KeyVaultName --name $secretName" -Level "ERROR"
                    return $false
                }
            } elseif ($errorMessage -match "not found|does not exist") {
                Write-Log "Key Vault '$KeyVaultName' not found" -Level "ERROR"
                Write-Log "Please verify the Key Vault name and ensure it exists" -Level "ERROR"
            } else {
                Write-Log "Failed to store secret: $result" -Level "ERROR"
            }
            
            return $false
        }
    }
    catch {
        Write-Log "Error exporting service key to Key Vault: $_" -Level "ERROR"
        return $false
    }
}

# Function to import service key credentials from Azure Key Vault (for split permissions scenarios)
function Get-ServiceKeyFromKeyVault {
    param(
        [Parameter(Mandatory=$true)]
        [string]$KeyVaultName,
        
        [Parameter(Mandatory=$true)]
        [string]$SubaccountId
    )
    
    try {
        Write-Log "Loading service key credentials for subaccount '$SubaccountId' from Key Vault '$KeyVaultName'..."
        
        # Normalize subaccount ID for secret name (replace invalid characters)
        $normalizedId = $SubaccountId -replace '[^a-zA-Z0-9-]', '-'
        
        # Secret name: btp-{subaccount-id}
        $secretName = "btp-$normalizedId"
        
        # Retrieve the secret
        Write-Log "Retrieving secret: $secretName"
        $result = az keyvault secret show --vault-name $KeyVaultName --name $secretName --query "value" -o tsv 2>&1
        
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($result)) {
            # Check for common errors
            $errorMessage = $result -join " "
            
            if ($errorMessage -match "Forbidden|ForbiddenByRbac|not authorized") {
                Write-Log "Access denied to Key Vault '$KeyVaultName'" -Level "ERROR"
                Write-Log "Please ensure your account has the 'Key Vault Secrets User' role assignment" -Level "ERROR"
            } elseif ($errorMessage -match "SecretNotFound|not found") {
                Write-Log "Secret '$secretName' not found in Key Vault '$KeyVaultName'" -Level "ERROR"
                Write-Log "Please ensure credentials were exported using -ExportCredentialsToKeyVault" -Level "ERROR"
            } elseif ($errorMessage -match "VaultNotFound|does not exist") {
                Write-Log "Key Vault '$KeyVaultName' not found" -Level "ERROR"
            } else {
                Write-Log "Failed to retrieve secret '$secretName': $result" -Level "ERROR"
            }
            
            return $null
        }
        
        Write-Log "Successfully retrieved secret '$secretName'" -Level "SUCCESS"
        
        # Debug: Show what we retrieved
        Write-Log "Retrieved value: $result" -Level "INFO"
        
        # Parse JSON
        $credentialsObj = $result | ConvertFrom-Json
        
        # Return credentials object matching the format from Get-BtpServiceKeyCredentials
        $credentials = @{
            ClientId = $credentialsObj.ClientId
            ClientSecret = $credentialsObj.ClientSecret
            TokenEndpoint = $credentialsObj.TokenEndpoint
            ApiUrl = $credentialsObj.ApiUrl
            SubaccountId = $SubaccountId
            Subdomain = $credentialsObj.Subdomain
        }
        
        Write-Log "Successfully loaded credentials from Key Vault" -Level "SUCCESS"
        return $credentials
    }
    catch {
        Write-Log "Error reading service key from Key Vault: $_" -Level "ERROR"
        return $null
    }
}

# Function to create SAP BTP connection in Microsoft Sentinel
function New-SentinelBtpConnection {
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
        [object]$BtpCredentials,
        [Parameter(Mandatory=$true)]
        [string]$SubaccountId,
        [Parameter(Mandatory=$true)]
        [object]$DcrConfig,
        [Parameter(Mandatory=$false)]
        [int]$PollingFrequencyMinutes = 1,
        [Parameter(Mandatory=$false)]
        [int]$IngestDelayMinutes = 20,
        [Parameter(Mandatory=$false)]
        [string]$ApiVersion = "2025-07-01-preview"
    )
    
    try {
        # Validate SubaccountId is a valid GUID (connector ID must be the subaccount GUID)
        try {
            $guidTest = [System.Guid]::Parse($SubaccountId)
        }
        catch {
            Write-Log "SubaccountId '$SubaccountId' is not a valid GUID" -Level "ERROR"
            return $false
        }
        
        # Use SubaccountId (GUID) as the connector ID (already validated as proper GUID format)
        $connectorId = $SubaccountId.ToLower()
        
        Write-Log "Creating SAP BTP connection for subaccount '$SubaccountId'..."
        Write-Log "  Connector ID (ARM resource): $connectorId"
        Write-Log "  Display Name: $ConnectionName"
        
        # Validate credentials
        $requiredFields = @('ClientId', 'ClientSecret', 'TokenEndpoint', 'ApiUrl')
        foreach ($field in $requiredFields) {
            if ([string]::IsNullOrWhiteSpace($BtpCredentials.$field)) {
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
        Write-Log "  Client ID: $($BtpCredentials.ClientId)"
        Write-Log "  Token Endpoint: $($BtpCredentials.TokenEndpoint)"
        Write-Log "  API URL: $($BtpCredentials.ApiUrl)"
        Write-Log "  Subdomain: $($BtpCredentials.Subdomain)"
        
        # Get Azure access token
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $false
        }
        
        # Build request body with DCR configuration
        # Use ConnectionName for display/friendly name in the connection properties
        $bodyObject = New-BtpConnectionRequestBody -BtpCredentials $BtpCredentials -DcrConfig $DcrConfig -SubaccountName $ConnectionName -PollingFrequencyMinutes $PollingFrequencyMinutes -IngestDelayMinutes $IngestDelayMinutes
        if ($null -eq $bodyObject) {
            return $false
        }
        
        $body = $bodyObject | ConvertTo-Json -Depth 10
        
        # Construct ARM API URI using SubaccountId (GUID) as the connector resource ID
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/providers/Microsoft.SecurityInsights/dataConnectors/$connectorId`?api-version=$ApiVersion"
        
        # Create headers
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        # Make REST API call
        $response = Invoke-RestMethod -Uri $uri -Method Put -Headers $headers -Body $body
        
        Write-Log "Successfully created SAP BTP connection with connector ID '$connectorId'" -Level "SUCCESS"
        Write-Log "  Display Name: $ConnectionName"
        Write-Log "  Subaccount: $SubaccountId"
        Write-Log "  API Endpoint: $($BtpCredentials.ApiUrl)"
        return $true
    }
    catch {
        Write-Log "Error creating SAP BTP connection: $_" -Level "ERROR"
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

# Function to get list of BTP subaccounts
function Get-BtpSubaccounts {
    try {
        Write-Log "Retrieving BTP subaccounts..."
        
        # Use --format json for reliable parsing
        $subaccountsJson = btp --format json list accounts/subaccount 2>&1 | Out-String
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to retrieve subaccounts: $subaccountsJson" -Level "ERROR"
            return $null
        }
        
        # Parse JSON output
        $subaccountsData = $subaccountsJson | ConvertFrom-Json
        
        if (-not $subaccountsData.value -or $subaccountsData.value.Count -eq 0) {
            Write-Log "No subaccounts found" -Level "WARNING"
            return @()
        }
        
        # Return array of subaccounts (maintains compatibility with existing code)
        $subaccounts = $subaccountsData.value | ForEach-Object {
            [PSCustomObject]@{
                guid = $_.guid
                displayName = $_.displayName
                subdomain = $_.subdomain
                region = $_.region
                state = $_.state
            }
        }
        
        Write-Log "Found $($subaccounts.Count) subaccount(s)" -Level "SUCCESS"
        return $subaccounts
    }
    catch {
        Write-Log "Error retrieving BTP subaccounts: $_" -Level "ERROR"
        return $null
    }
}

# Function to get Cloud Foundry details for a BTP subaccount
function Get-BtpSubaccountCfDetails {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubaccountId
    )
    
    try {
        # Get Cloud Foundry environment instances using --format json
        $envInstancesJson = btp --format json list accounts/environment-instance --subaccount $SubaccountId 2>&1 | Out-String
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to list environment instances for subaccount $SubaccountId" -Level "WARNING"
            return $null
        }
        
        # Parse JSON output
        $envInstancesData = $envInstancesJson | ConvertFrom-Json
        
        if (-not $envInstancesData.environmentInstances) {
            Write-Log "No environment instances found for subaccount $SubaccountId" -Level "WARNING"
            return $null
        }
        
        # Find Cloud Foundry instance
        $cfInstance = $envInstancesData.environmentInstances | Where-Object { $_.environmentType -eq "cloudfoundry" }
        
        if (-not $cfInstance) {
            Write-Log "No Cloud Foundry instance found for subaccount $SubaccountId" -Level "WARNING"
            return $null
        }
        
        Write-Log "Found Cloud Foundry instance: $($cfInstance.name) (ID: $($cfInstance.id))"
        
        # Parse labels (it's a JSON string in the response)
        $labels = $cfInstance.labels | ConvertFrom-Json
        
        $cfApiEndpoint = $labels.'API Endpoint'
        $cfOrgId = $labels.'Org ID'
        $cfOrgName = $labels.'Org Name'
        
        if ([string]::IsNullOrWhiteSpace($cfApiEndpoint) -or [string]::IsNullOrWhiteSpace($cfOrgName)) {
            Write-Log "Could not extract CF details from environment instance for subaccount $SubaccountId" -Level "WARNING"
            return $null
        }
        
        # Extract region from API endpoint (e.g., https://api.cf.eu10.hana.ondemand.com -> eu10)
        $cfRegion = $null
        if ($cfApiEndpoint -match '\.cf\.([^.]+)\.') {
            $cfRegion = $matches[1]
        }
        
        return @{
            ApiEndpoint = $cfApiEndpoint
            OrgId = $cfOrgId
            OrgName = $cfOrgName
            Region = $cfRegion
        }
    }
    catch {
        Write-Log "Error retrieving CF details for subaccount $SubaccountId : $_" -Level "ERROR"
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
        Write-Log "Getting workspace details via Azure Resource Graph for '$WorkspaceName'..."
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $null
        }
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }

        $argQuery = @"
Resources
| where subscriptionId =~ '$SubscriptionId'
| where resourceGroup =~ '$ResourceGroupName'
| where type =~ 'Microsoft.OperationalInsights/workspaces' and name =~ '$WorkspaceName'
| extend workspaceGuid = tostring(properties.customerId)
| extend workspaceShortId = substring(workspaceGuid, 0, 12)
| project workspaceId = id, workspaceLocation = location, workspaceName = name, workspaceGuid, workspaceShortId, 
    dceName = strcat('ASI-', workspaceGuid), 
    dcrNamePrefix = strcat('Microsoft-Sentinel-SAP-BTP-DCR-', workspaceShortId),
    resourceName = '', resourceType = '', resourceId = '', resourceProperties = dynamic({})
| union (
    Resources
    | where subscriptionId =~ '$SubscriptionId'
    | where resourceGroup =~ '$ResourceGroupName'
    | where type in~ ('Microsoft.Insights/dataCollectionEndpoints', 'Microsoft.Insights/dataCollectionRules')
    | project workspaceId = '', workspaceLocation = '', workspaceName = '', workspaceGuid = '', workspaceShortId = '', 
        dceName = '', dcrNamePrefix = '', 
        resourceName = name, resourceType = type, resourceId = id, resourceProperties = properties
)
"@
        
        $argBody = @{
            subscriptions = @($SubscriptionId)
            query = $argQuery
        } | ConvertTo-Json -Depth 10
        
        $uri = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01"
        $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $argBody
        
        if ($null -eq $response.data -or $response.data.Count -eq 0) {
            Write-Log "Workspace '$WorkspaceName' not found in resource group '$ResourceGroupName'" -Level "ERROR"
            return $null
        }
        
        $workspaceRow = $response.data | Where-Object { -not [string]::IsNullOrEmpty($_.workspaceName) } | Select-Object -First 1
        
        if ($null -eq $workspaceRow) {
            Write-Log "Workspace '$WorkspaceName' not found in ARG response" -Level "ERROR"
            return $null
        }
        
        $dceName = $workspaceRow.dceName
        $dcrNamePrefix = $workspaceRow.dcrNamePrefix
        
        $dceRow = $response.data | Where-Object { 
            $_.resourceType -eq "microsoft.insights/datacollectionendpoints" -and $_.resourceName -eq $dceName 
        } | Select-Object -First 1
        
        $dcrRow = $response.data | Where-Object { 
            $_.resourceType -eq "microsoft.insights/datacollectionrules" -and $_.resourceName -like "$dcrNamePrefix*" 
        } | Select-Object -First 1
        
        Write-Log "Workspace details retrieved successfully via ARG" -Level "SUCCESS"
        Write-Log "  Location: $($workspaceRow.workspaceLocation)"
        Write-Log "  Workspace GUID: $($workspaceRow.workspaceGuid)"
        Write-Log "  Short ID for naming: $($workspaceRow.workspaceShortId)"
        
        $dceInfo = $null
        if ($dceRow) {
            Write-Log "  Found existing DCE: $($dceRow.resourceName)" -Level "SUCCESS"
            $dceInfo = @{
                Name = $dceRow.resourceName
                ResourceId = $dceRow.resourceId
                LogsIngestionEndpoint = $dceRow.resourceProperties.logsIngestion.endpoint
            }
        }
        
        $dcrInfo = $null
        if ($dcrRow) {
            Write-Log "  Found existing DCR: $($dcrRow.resourceName)" -Level "SUCCESS"
            $dcrInfo = @{
                Name = $dcrRow.resourceName
                ResourceId = $dcrRow.resourceId
                ImmutableId = $dcrRow.resourceProperties.immutableId
                DataCollectionEndpointId = $dcrRow.resourceProperties.dataCollectionEndpointId
            }
        }
        
        return @{
            ResourceId = $workspaceRow.workspaceId
            Location = $workspaceRow.workspaceLocation
            WorkspaceGuid = $workspaceRow.workspaceGuid
            ShortId = $workspaceRow.workspaceShortId
            Name = $WorkspaceName
            ExistingDCE = $dceInfo
            ExistingDCR = $dcrInfo
        }
    }
    catch {
        Write-Log "Error getting workspace details: $_" -Level "ERROR"
        return $null
    }
}

# Function to create a new Data Collection Endpoint for SAP BTP
# Only called when DCE doesn't exist (checked via ARG query upfront)
function New-DataCollectionEndpoint {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubscriptionId,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceGuid,
        [Parameter(Mandatory=$true)]
        [string]$Location
    )
    
    try {
        $dceName = "ASI-$WorkspaceGuid"
        
        Write-Log "Creating Data Collection Endpoint '$dceName'..."
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $null
        }
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/dataCollectionEndpoints/$dceName`?api-version=2022-06-01"
        
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
        Write-Log "Error creating Data Collection Endpoint: $_" -Level "ERROR"
        return $null
    }
}

# Function to create or verify Log Analytics table exists
# Creates the table with schema from template if it doesn't exist
function Get-OrCreateLogAnalyticsTable {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubscriptionId,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceName,
        [Parameter(Mandatory=$true)]
        [string]$TableName,
        [Parameter(Mandatory=$true)]
        [array]$Columns
    )
    
    try {
        Write-Log "Checking if Log Analytics table '$TableName' exists..."
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $false
        }
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/tables/$TableName`?api-version=2021-12-01-preview"
        
        try {
            $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
            Write-Log "Table '$TableName' already exists" -Level "SUCCESS"
            return $true
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 404) {
                Write-Log "Table '$TableName' not found, creating..."
            }
            else {
                throw $_
            }
        }
        
        $hasTimeGenerated = $Columns | Where-Object { $_.name -eq "TimeGenerated" }
        if (-not $hasTimeGenerated) {
            Write-Log "Adding TimeGenerated column to table schema"
            $Columns = @(@{ name = "TimeGenerated"; type = "datetime" }) + $Columns
        }
        
        $tableBody = @{
            properties = @{
                schema = @{
                    name = $TableName
                    columns = $Columns
                }
            }
        } | ConvertTo-Json -Depth 10
        
        Write-Log "Creating table with $($Columns.Count) columns..."
        $response = Invoke-RestMethod -Uri $uri -Method Put -Headers $headers -Body $tableBody
        
        Write-Log "Successfully created table '$TableName'" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Error with Log Analytics table: $_" -Level "ERROR"
        Write-Log "Table creation is required before DCR can ingest data" -Level "ERROR"
        return $false
    }
}

# Function to query SAP BTP Content Template API for DCR schema
# Returns DCR configuration from the Content Hub template including columns, streams, and transforms
function Get-SapBtpContentTemplate {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubscriptionId,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceName
    )
    
    try {
        Write-Log "Querying Content Template API for SAP BTP DCR schema..."
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $null
        }
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $contentId = "SAPBTPAuditEvents"
        $filterExpression = "properties/contentId eq '$contentId'"
        $encodedFilter = [System.Web.HttpUtility]::UrlEncode($filterExpression)
        
        $listUri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/providers/Microsoft.SecurityInsights/contentTemplates?api-version=2023-11-01&`$filter=$encodedFilter"
        
        Write-Log "Listing content templates to find resource ID..."
        $listResponse = Invoke-RestMethod -Uri $listUri -Method Get -Headers $headers
        
        if ($null -eq $listResponse.value -or $listResponse.value.Count -eq 0) {
            Write-Log "SAP BTP content template not found. Is the solution installed from Content Hub?" -Level "WARNING"
            return $null
        }
        
        $template = $listResponse.value[0]
        $templateResourceId = $template.id
        Write-Log "Found template: $($template.name)"
        
        $getUri = "https://management.azure.com$templateResourceId`?api-version=2025-09-01"
        
        Write-Log "Retrieving template mainTemplate with api-version=2025-09-01..."
        $getResponse = Invoke-RestMethod -Uri $getUri -Method Get -Headers $headers
        
        if ($null -eq $getResponse.properties.mainTemplate) {
            Write-Log "Template does not contain mainTemplate" -Level "WARNING"
            return $null
        }
        
        $dcrResource = $getResponse.properties.mainTemplate.resources | Where-Object { 
            $_.type -eq "Microsoft.Insights/dataCollectionRules" 
        } | Select-Object -First 1
        
        if ($null -eq $dcrResource) {
            Write-Log "No DCR resource found in mainTemplate" -Level "WARNING"
            return $null
        }
        
        Write-Log "Found DCR resource in template: $($dcrResource.name)" -Level "SUCCESS"
        
        $tableResource = $getResponse.properties.mainTemplate.resources | Where-Object { 
            $_.type -eq "Microsoft.OperationalInsights/workspaces/tables" 
        } | Select-Object -First 1
        
        if ($null -eq $tableResource) {
            Write-Log "No table resource found in mainTemplate" -Level "WARNING"
            return $null
        }
        
        Write-Log "Found table resource in template: $($tableResource.name)" -Level "SUCCESS"
        
        $streamDeclarations = $dcrResource.properties.streamDeclarations
        if ($null -eq $streamDeclarations) {
            Write-Log "No stream declarations found in DCR template" -Level "WARNING"
            return $null
        }
        
        $streamName = ($streamDeclarations.PSObject.Properties | Select-Object -First 1).Name
        $streamConfig = $streamDeclarations.$streamName
        
        $dataFlows = $dcrResource.properties.dataFlows
        $transformKql = $null
        if ($dataFlows -and $dataFlows.Count -gt 0) {
            $transformKql = $dataFlows[0].transformKql
        }
        
        Write-Log "  DCR Name: $($dcrResource.name)" -Level "SUCCESS"
        Write-Log "  Stream: $streamName" -Level "SUCCESS"
        Write-Log "  Stream Input Columns: $($streamConfig.columns.Count)" -Level "SUCCESS"
        Write-Log "  Table Name: $($tableResource.name)" -Level "SUCCESS"
        Write-Log "  Table Schema Columns: $($tableResource.properties.schema.columns.Count)" -Level "SUCCESS"
        Write-Log "  Transform KQL: $(if ($transformKql) { 'Present' } else { 'None' })" -Level "SUCCESS"
        
        return @{
            DcrName = $dcrResource.name
            StreamName = $streamName
            StreamColumns = $streamConfig.columns
            TableName = $tableResource.name
            TableColumns = $tableResource.properties.schema.columns
            TransformKql = $transformKql
            DataFlows = $dataFlows
            StreamDeclarations = $streamDeclarations
        }
    }
    catch {
        Write-Log "Error querying Content Template API: $_" -Level "ERROR"
        Write-Log "Cannot proceed without Content Template. Ensure SAP BTP solution is installed from Content Hub." -Level "ERROR"
        return $null
    }
}

# Function to build SAP BTP DCR schema from template configuration
# This provides the DCR schema definition based on the Content Template
# Returns the 'properties' section for the DCR; 'location' is set by the caller at top-level
function Get-SapBtpDcrTemplate {
    param(
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceResourceId,
        [Parameter(Mandatory=$true)]
        [string]$DataCollectionEndpointId,
        [Parameter(Mandatory=$true)]
        [object]$TemplateConfig
    )
    
    try {
        Write-Log "Building SAP BTP DCR schema from template..."
        Write-Log "  Stream: $($TemplateConfig.StreamName)"
        Write-Log "  Stream Input Columns: $($TemplateConfig.StreamColumns.Count)"
        
        $streamDeclarations = @{}
        $streamDeclarations[$TemplateConfig.StreamName] = @{
            columns = $TemplateConfig.StreamColumns
        }
        
        $dataFlows = @(
            @{
                streams = @($TemplateConfig.StreamName)
                destinations = @("clv2ws1")
                transformKql = $TemplateConfig.TransformKql
                outputStream = $TemplateConfig.StreamName
            }
        )
        
        $dcrProperties = @{
            dataCollectionEndpointId = $DataCollectionEndpointId
            streamDeclarations = $streamDeclarations
            dataSources = @{}
            destinations = @{
                logAnalytics = @(
                    @{
                        workspaceResourceId = $WorkspaceResourceId
                        name = "clv2ws1"
                    }
                )
            }
            dataFlows = $dataFlows
        }
        
        Write-Log "Successfully built DCR schema" -Level "SUCCESS"
        return $dcrProperties
    }
    catch {
        Write-Log "Error building DCR template: $_" -Level "ERROR"
        return $null
    }
}

# Function to create a new Data Collection Rule for SAP BTP
# Only called when DCR doesn't exist (checked via ARG query upfront)
function New-DataCollectionRule {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SubscriptionId,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceName,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceShortId,
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceResourceId,
        [Parameter(Mandatory=$true)]
        [string]$DataCollectionEndpointId,
        [Parameter(Mandatory=$true)]
        [string]$Location
    )
    
    try {
        $templateConfig = Get-SapBtpContentTemplate -SubscriptionId $SubscriptionId -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName
        
        if ($null -eq $templateConfig) {
            Write-Log "Failed to retrieve Content Template. Cannot proceed with DCR creation." -Level "ERROR"
            Write-Log "Ensure the SAP BTP solution is installed from Content Hub." -Level "ERROR"
            return $null
        }
        
        $dcrBaseName = $templateConfig.DcrName
        if ($dcrBaseName.StartsWith("Microsoft-Sentinel-")) {
            $dcrName = "$dcrBaseName-$WorkspaceShortId"
        } else {
            $dcrName = "Microsoft-Sentinel-$dcrBaseName-$WorkspaceShortId"
        }
        
        Write-Log "DCR Base Name from template: $dcrBaseName"
        Write-Log "Full DCR Name: $dcrName"
        Write-Log "Creating new DCR '$dcrName'..."
        
        $token = Get-AzureAccessToken
        if ($null -eq $token) {
            return $null
        }
        
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/dataCollectionRules/$dcrName`?api-version=2022-06-01"
        
        $tableName = $templateConfig.TableName

        if ($tableName -match '/([^/]+)$') {
            $tableName = $matches[1]
        }
        
        Write-Log "Table name: $tableName"
        
        $tableCreated = Get-OrCreateLogAnalyticsTable `
            -SubscriptionId $SubscriptionId `
            -ResourceGroupName $ResourceGroupName `
            -WorkspaceName $WorkspaceName `
            -TableName $tableName `
            -Columns $templateConfig.TableColumns
        
        if (-not $tableCreated) {
            Write-Log "Failed to create or verify table. Cannot proceed with DCR creation." -Level "ERROR"
            return $null
        }
        
        $dcrProperties = Get-SapBtpDcrTemplate -WorkspaceResourceId $WorkspaceResourceId -DataCollectionEndpointId $DataCollectionEndpointId -TemplateConfig $templateConfig
        
        if ($null -eq $dcrProperties) {
            Write-Log "Failed to build DCR schema from template" -Level "ERROR"
            return $null
        }
        
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
