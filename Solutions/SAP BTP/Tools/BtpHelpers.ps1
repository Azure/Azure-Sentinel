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

# Function to check if Cloud Foundry CLI is installed
function Test-CfCli {
    try {
        $cfVersion = cf --version 2>&1
        Write-Log "CF CLI is installed: $cfVersion"
        return $true
    }
    catch {
        Write-Log "CF CLI is not installed or not in PATH. Please install it first." -Level "ERROR"
        return $false
    }
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

# Function to perform CF login with credentials
function Invoke-CfLogin {
    param(
        [string]$ApiEndpoint,
        [string]$Username,
        [SecureString]$Password,
        [string]$OrgName = "",
        [string]$SpaceName = ""
    )
    
    try {
        if ([string]::IsNullOrWhiteSpace($Username) -or $null -eq $Password) {
            Write-Log "CF credentials missing for login attempt." -Level "ERROR"
            Write-Log "Username provided: $(-not [string]::IsNullOrWhiteSpace($Username))" -Level "ERROR"
            Write-Log "Password provided: $($null -ne $Password)" -Level "ERROR"
            return $false
        }
        
        Write-Log "Authenticating to Cloud Foundry API: $ApiEndpoint"
        
        # Convert SecureString to plain text for CF CLI (only in memory during login)
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
        $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
        
        # Build cf login command with org and space if provided
        $loginArgs = @("login", "-a", $ApiEndpoint, "-u", $Username, "-p", $plainPassword)
        if (-not [string]::IsNullOrWhiteSpace($OrgName)) {
            $loginArgs += @("-o", $OrgName)
        }
        if (-not [string]::IsNullOrWhiteSpace($SpaceName)) {
            $loginArgs += @("-s", $SpaceName)
        }
        
        # Execute cf login
        $result = & cf $loginArgs 2>&1
        
        # Clear the password from memory immediately
        $plainPassword = $null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully authenticated to Cloud Foundry" -Level "SUCCESS"
            return $true
        }
        else {
            Write-Log "Authentication failed: $result" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error during authentication: $_" -Level "ERROR"
        return $false
    }
    finally {
        # Ensure password is cleared from memory
        if ($plainPassword) {
            $plainPassword = $null
        }
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

# Function to switch CF API endpoint and authenticate
function Set-CfApiEndpoint {
    param(
        [string]$ApiEndpoint,
        [string]$Username,
        [SecureString]$Password,
        [string]$OrgName = "",
        [string]$SpaceName = ""
    )
    
    try {
        # Get current API endpoint
        $currentApi = cf api 2>&1 | Select-String -Pattern "api endpoint:" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
        
        if ($currentApi -eq $ApiEndpoint) {
            Write-Log "Already connected to API endpoint: $ApiEndpoint"
            
            # Verify authentication is still valid
            $authCheck = cf apps 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Session expired or not authenticated. Re-authenticating..." -Level "WARNING"
                if (-not (Invoke-CfLogin -ApiEndpoint $ApiEndpoint -Username $Username -Password $Password -OrgName $OrgName -SpaceName $SpaceName)) {
                    return $false
                }
            }
            return $true
        }
        
        Write-Log "Switching to API endpoint: $ApiEndpoint"
        $result = cf api $ApiEndpoint 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully switched to API endpoint: $ApiEndpoint" -Level "SUCCESS"
            
            # API switch logs you out, so re-authenticate
            Write-Log "Re-authenticating after API endpoint switch..."
            if (-not (Invoke-CfLogin -ApiEndpoint $ApiEndpoint -Username $Username -Password $Password -OrgName $OrgName -SpaceName $SpaceName)) {
                Write-Log "Failed to re-authenticate after API switch" -Level "ERROR"
                return $false
            }
            return $true
        }
        else {
            Write-Log "Failed to switch API endpoint: $result" -Level "ERROR"
            return $false
        }
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
        Write-Log "Targeting org: '$OrgName', space: '$SpaceName'"
        $result = cf target -o $OrgName -s $SpaceName 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully targeted org/space" -Level "SUCCESS"
            return $true
        }
        else {
            Write-Log "Failed to target org/space: $result" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error targeting org/space: $_" -Level "ERROR"
        return $false
    }
}

# Function to get CF service key and parse JSON
function Get-CfServiceKey {
    param(
        [string]$InstanceName,
        [string]$KeyName
    )
    
    try {
        Write-Log "Retrieving service key '$KeyName' for instance '$InstanceName'..."
        
        # Get service key output (may contain informational text before JSON)
        $rawOutput = cf service-key $InstanceName $KeyName 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to retrieve service key: $rawOutput" -Level "ERROR"
            return $null
        }
        
        # Extract JSON from the output (skip lines until we find the opening brace)
        $jsonLines = @()
        $jsonStarted = $false
        
        foreach ($line in $rawOutput) {
            if ($line -match '^\s*\{') {
                $jsonStarted = $true
            }
            if ($jsonStarted) {
                $jsonLines += $line
            }
        }
        
        if ($jsonLines.Count -eq 0) {
            Write-Log "No JSON found in service key output" -Level "ERROR"
            return $null
        }
        
        # Parse the JSON
        $jsonString = $jsonLines -join "`n"
        $result = $jsonString | ConvertFrom-Json
        
        if ($null -ne $result) {
            Write-Log "Successfully retrieved service key" -Level "SUCCESS"
            return $result
        }
        else {
            Write-Log "Failed to parse service key JSON" -Level "ERROR"
            return $null
        }
    }
    catch {
        Write-Log "Error retrieving service key: $_" -Level "ERROR"
        Write-Log "Raw output: $rawOutput" -Level "ERROR"
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
        # Extract credentials from service key structure
        $credentials = $ServiceKey.credentials
        if ($null -eq $credentials) {
            Write-Log "Service key missing 'credentials' property" -Level "ERROR"
            return $null
        }
        
        # Validate required fields
        if ([string]::IsNullOrWhiteSpace($credentials.uaa.clientid)) {
            Write-Log "Service key missing UAA client ID" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($credentials.uaa.clientsecret)) {
            Write-Log "Service key missing UAA client secret" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($credentials.uaa.url)) {
            Write-Log "Service key missing UAA URL" -Level "ERROR"
            return $null
        }
        if ([string]::IsNullOrWhiteSpace($credentials.url)) {
            Write-Log "Service key missing audit log API URL" -Level "ERROR"
            return $null
        }
        
        # Extract subdomain from UAA URL (e.g., https://subdomain.authentication.region.hana.ondemand.com)
        $subdomain = ""
        if ($credentials.uaa.url -match "https?://([^.]+)\..*") {
            $subdomain = $matches[1]
        }
        
        # Return validated credentials object
        # Note: Full OAuth token endpoint path with grant_type parameter is required
        return @{
            ClientId = $credentials.uaa.clientid
            ClientSecret = $credentials.uaa.clientsecret
            TokenEndpoint = "$($credentials.uaa.url)/oauth/token?grant_type=client_credentials"
            ApiUrl = $credentials.url
            SubaccountId = $credentials.uaa.subaccountid
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
        [Parameter(Mandatory=$false)]
        [string]$SubaccountName
    )
    
    try {
        # Build API endpoint for audit log records
        $apiEndpoint = "$($BtpCredentials.ApiUrl)/auditlog/v2/auditlogrecords"
        
        # Build request body matching SAPBTP_PollingConfig.json template
        $body = @{
            kind = "RestApiPoller"
            properties = @{
                connectorDefinitionName = "SAPBTPAuditEvents"
                dataType = "SAPBTPAuditLog_CL"
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
                    queryWindowInMin = 1
                    queryTimeFormat = "yyyy-MM-ddTHH:mm:ss.fff"
                    retryCount = 3
                    timeoutInSeconds = 60
                    queryWindowDelayInMin = 20
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
        
        # Check if service instance already exists
        $existingService = cf service $InstanceName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Service instance '$InstanceName' already exists. Skipping creation." -Level "WARNING"
            return $true
        }
        
        # Create service instance using CF CLI
        $result = cf create-service $Service $Plan $InstanceName 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully created service instance '$InstanceName'" -Level "SUCCESS"
            return $true
        }
        else {
            Write-Log "Failed to create service instance '$InstanceName': $result" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error creating service instance: $_" -Level "ERROR"
        return $false
    }
}

# Function to create CF service key
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

# Function to generate connection name from BTP credentials
function Get-BtpConnectionName {
    param(
        [Parameter(Mandatory=$true)]
        [object]$BtpCredentials,
        [Parameter(Mandatory=$true)]
        [string]$SubaccountId
    )
    
    # Use subaccount ID as connection name
    # Pattern: subaccount-id (e.g., 59408ac3-f5b3-4fba-9ee1-ded934352397)
    $connectionName = $SubaccountId
    
    Write-Log "Using subaccount ID as connection name: $connectionName"
    
    return $connectionName
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
        [Parameter(Mandatory=$false)]
        [string]$SubaccountName,
        [Parameter(Mandatory=$false)]
        [string]$ApiVersion = "2025-09-01"
    )
    
    try {
        Write-Log "Creating SAP BTP connection '$ConnectionName' for subaccount '$SubaccountId'..."
        
        # Validate credentials
        $requiredFields = @('ClientId', 'ClientSecret', 'TokenEndpoint', 'ApiUrl')
        foreach ($field in $requiredFields) {
            if ([string]::IsNullOrWhiteSpace($BtpCredentials.$field)) {
                Write-Log "Invalid $field - cannot create connection" -Level "ERROR"
                return $false
            }
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
        
        # Build request body
        $bodyObject = New-BtpConnectionRequestBody -BtpCredentials $BtpCredentials -SubaccountName $SubaccountName
        if ($null -eq $bodyObject) {
            return $false
        }
        
        $body = $bodyObject | ConvertTo-Json -Depth 10
        
        # Construct ARM API URI
        $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/providers/Microsoft.SecurityInsights/dataConnectors/$($ConnectionName)?api-version=$ApiVersion"
        
        # Create headers
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        # Make REST API call
        $response = Invoke-RestMethod -Uri $uri -Method Put -Headers $headers -Body $body
        
        Write-Log "Successfully created SAP BTP connection '$ConnectionName'" -Level "SUCCESS"
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
        Write-Log "Retrieving list of BTP subaccounts..."
        $subaccountsOutput = btp list accounts/subaccount 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to retrieve subaccounts: $subaccountsOutput" -Level "ERROR"
            return $null
        }
        
        # Parse table output
        $subaccounts = @()
        $headerPassed = $false
        
        foreach ($line in $subaccountsOutput) {
            if ($line -match 'guid|subaccount id') {
                $headerPassed = $true
                continue
            }
            
            if ($line -match '^[-\s]+$' -or [string]::IsNullOrWhiteSpace($line)) {
                continue
            }
            
            if ($headerPassed) {
                $columns = $line -split '\s{2,}' | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
                
                if ($columns.Count -ge 2) {
                    $subaccounts += [PSCustomObject]@{
                        guid = $columns[0].Trim()
                        displayName = $columns[1].Trim()
                        region = if ($columns.Count -ge 4) { $columns[3].Trim() } else { "" }
                    }
                }
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
        # Get Cloud Foundry environment instances
        $envInstancesOutput = btp list accounts/environment-instance --subaccount $SubaccountId 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to list environment instances for subaccount $SubaccountId" -Level "WARNING"
            return $null
        }
        
        # Join all output lines into a single string to handle line wrapping
        $fullOutput = $envInstancesOutput -join " "
        
        # Find Cloud Foundry instance ID using regex pattern
        # Pattern looks for: any text followed by GUID format followed by "cloudfoundry"
        # GUID format: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
        $cfInstanceId = $null
        
        if ($fullOutput -match '([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\s+cloudfoundry') {
            $cfInstanceId = $matches[1]
            Write-Log "Found Cloud Foundry instance ID: $cfInstanceId"
        }
        else {
            Write-Log "Could not find cloudfoundry environment instance in output" -Level "WARNING"
        }
        
        if ([string]::IsNullOrWhiteSpace($cfInstanceId)) {
            Write-Log "No Cloud Foundry instance found for subaccount $SubaccountId" -Level "WARNING"
            return $null
        }
        
        # Get CF instance details
        $cfDetailsOutput = btp get accounts/environment-instance $cfInstanceId --subaccount $SubaccountId 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to get CF instance details for subaccount $SubaccountId" -Level "WARNING"
            return $null
        }
        
        # Parse CF details - join output to handle line wrapping
        $fullDetailsOutput = $cfDetailsOutput -join " "
        
        $cfApiEndpoint = $null
        $cfOrgId = $null
        $cfOrgName = $null
        
        # Extract labels JSON using regex - it appears between "labels:" and "service name:"
        if ($fullDetailsOutput -match 'labels:\s+(\{.+?\})\s+service name:') {
            $labelsJson = $matches[1].Trim()
            try {
                $labels = $labelsJson | ConvertFrom-Json
                
                # Handle both formats: with and without trailing colons in property names
                $cfApiEndpoint = if ($labels.'API Endpoint:') { $labels.'API Endpoint:' } else { $labels.'API Endpoint' }
                $cfOrgId = if ($labels.'Org ID:') { $labels.'Org ID:' } else { $labels.'Org ID' }
                $cfOrgName = if ($labels.'Org Name:') { $labels.'Org Name:' } else { $labels.'Org Name' }
            }
            catch {
                Write-Log "Failed to parse labels JSON for subaccount $SubaccountId : $_" -Level "WARNING"
                Write-Log "Labels JSON: $labelsJson" -Level "WARNING"
            }
        }
        else {
            Write-Log "Could not find labels in output for subaccount $SubaccountId" -Level "WARNING"
        }
        
        if ([string]::IsNullOrWhiteSpace($cfApiEndpoint) -or [string]::IsNullOrWhiteSpace($cfOrgName)) {
            Write-Log "Could not extract CF details for subaccount $SubaccountId" -Level "WARNING"
            return $null
        }
        
        return @{
            ApiEndpoint = $cfApiEndpoint
            OrgId = $cfOrgId
            OrgName = $cfOrgName
        }
    }
    catch {
        Write-Log "Error retrieving CF details for subaccount $SubaccountId : $_" -Level "ERROR"
        return $null
    }
}
