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

# Function to list all service keys for a CF service instance
# Function to discover service instances by offering type
function Get-CfServiceInstancesByOffering {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ServiceOffering
    )
    
    try {
        Write-Log "Discovering service instances with offering '$ServiceOffering'..."
        
        # Get all services
        $rawOutput = cf services 2>&1 | Out-String
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to list services: $rawOutput" -Level "ERROR"
            return @()
        }
        
        # Parse service instances from the output
        # Format: name    offering    plan    bound apps    last operation    broker    upgrade available
        $matchingInstances = @()
        $lines = $rawOutput -split "`n"
        $headerLine = $null
        $nameColumnEnd = -1
        $offeringColumnEnd = -1
        
        foreach ($line in $lines) {
            # Skip empty lines and informational text
            if ([string]::IsNullOrWhiteSpace($line) -or 
                $line -match '^Getting service' -or 
                $line -match '^OK$' -or
                $line -match '^No services found' -or
                $line -match '^upgrade available') {
                continue
            }
            
            # Capture header line to determine column positions
            if ($line -match '^name\s+offering\s+plan' -and $null -eq $headerLine) {
                $headerLine = $line
                # Find where "offering" and "plan" columns start
                if ($line -match 'name\s+offering') {
                    $nameColumnEnd = $line.IndexOf('offering')
                    $planIndex = $line.IndexOf('plan')
                    if ($planIndex -gt $nameColumnEnd) {
                        $offeringColumnEnd = $planIndex
                    }
                }
                continue
            }
            
            # Parse data rows using fixed column positions
            if ($null -ne $headerLine -and $nameColumnEnd -gt 0 -and $offeringColumnEnd -gt 0) {
                if ($line.Length -ge $offeringColumnEnd) {
                    $instanceName = $line.Substring(0, $nameColumnEnd).Trim()
                    $offering = $line.Substring($nameColumnEnd, $offeringColumnEnd - $nameColumnEnd).Trim()
                    
                    if (-not [string]::IsNullOrWhiteSpace($instanceName) -and $offering -eq $ServiceOffering) {
                        Write-Log "Found matching instance: $instanceName" -Level "SUCCESS"
                        $matchingInstances += $instanceName
                    }
                }
            }
        }
        
        if ($matchingInstances.Count -gt 0) {
            Write-Log "Discovered $($matchingInstances.Count) instance(s) with offering '$ServiceOffering'" -Level "SUCCESS"
        }
        else {
            Write-Log "No instances found with offering '$ServiceOffering'" -Level "INFO"
        }
        
        return $matchingInstances
    }
    catch {
        Write-Log "Error discovering service instances: $_" -Level "ERROR"
        return @()
    }
}

function Get-CfServiceKeys {
    param(
        [Parameter(Mandatory=$true)]
        [string]$InstanceName
    )
    
    try {
        Write-Log "Listing service keys for instance '$InstanceName'..."
        
        # Get service keys output
        $rawOutput = cf service-keys $InstanceName 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to list service keys: $rawOutput" -Level "ERROR"
            return @()
        }
        
        # Parse the output to extract key names
        # Output format:
        # Getting keys for service instance <name> as <user>...
        # 
        # name                     last operation     message
        # key-name-1              create succeeded
        # key-name-2              create succeeded
        $keyNames = @()
        $headerLine = $null
        $nameColumnEnd = -1
        
        foreach ($line in $rawOutput) {
            # Skip empty lines and informational text
            if ([string]::IsNullOrWhiteSpace($line) -or 
                $line -match '^Getting keys' -or 
                $line -match '^OK$') {
                continue
            }
            
            # Capture the header line to determine column positions
            if ($line -match '^name\s+' -and $null -eq $headerLine) {
                $headerLine = $line
                # Find where "last operation" starts (end of name column)
                # Look for the pattern "name" followed by spaces, then "last"
                if ($line -match 'name\s+last') {
                    $nameColumnEnd = $line.IndexOf('last')
                }
                continue
            }
            
            # Extract key names using fixed column width from header
            if ($null -ne $headerLine -and $nameColumnEnd -gt 0) {
                # Extract the name column (everything before the "last operation" column)
                if ($line.Length -ge $nameColumnEnd) {
                    $keyName = $line.Substring(0, $nameColumnEnd).Trim()
                } else {
                    $keyName = $line.Trim()
                }
                
                if (-not [string]::IsNullOrWhiteSpace($keyName)) {
                    $keyNames += $keyName
                }
            }
        }
        
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

# Function to check if a specific service key exists
function Test-CfServiceKeyExists {
    param(
        [Parameter(Mandatory=$true)]
        [string]$InstanceName,
        
        [Parameter(Mandatory=$true)]
        [string]$KeyName
    )
    
    try {
        $existingKeys = Get-CfServiceKeys -InstanceName $InstanceName
        $exists = $existingKeys -contains $KeyName
        
        if ($exists) {
            Write-Log "Service key '$KeyName' exists for instance '$InstanceName'" -Level "INFO"
        }
        else {
            Write-Log "Service key '$KeyName' does not exist for instance '$InstanceName'" -Level "INFO"
        }
        
        return $exists
    }
    catch {
        Write-Log "Error checking service key existence: $_" -Level "ERROR"
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
            Write-Log "Service key structure: $($ServiceKey | ConvertTo-Json -Depth 3)" -Level "ERROR"
            return $null
        }
        
        # Validate required fields
        if ([string]::IsNullOrWhiteSpace($credentials.uaa.clientid)) {
            Write-Log "Service key missing UAA client ID" -Level "ERROR"
            Write-Log "UAA structure: $($credentials.uaa | ConvertTo-Json -Depth 2)" -Level "ERROR"
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
        [object]$BtpCredentials
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
                    queryWindowInMin = 5
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

# Function to generate connection name from BTP credentials
function Get-BtpConnectionName {
    param(
        [Parameter(Mandatory=$true)]
        [object]$BtpCredentials,
        [Parameter(Mandatory=$true)]
        [string]$SubaccountId
    )
    
    # Use subdomain from UAA URL for connection name with subaccount ID suffix
    # Pattern: subdomain_subaccountid (e.g., msdemo_12345678-90ab-cdef-1234-567890abcdef)
    # Falls back to subaccount ID only if subdomain cannot be extracted
    $cleanSubaccountId = $SubaccountId.Replace('-', '')
    
    if ([string]::IsNullOrWhiteSpace($BtpCredentials.Subdomain)) {
        Write-Log "Subdomain not found in UAA URL, using subaccount ID only for connection name" -Level "WARNING"
        $connectionName = "$cleanSubaccountId"
    } else {
        # Remove any special characters and ensure valid Azure resource name
        $cleanSubdomain = $BtpCredentials.Subdomain -replace '[^a-zA-Z0-9]', ''
        $connectionName = "${cleanSubdomain}_${cleanSubaccountId}"
    }
    
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
        $bodyObject = New-BtpConnectionRequestBody -BtpCredentials $BtpCredentials
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
        $headerLine = $null
        $guidColumnEnd = -1
        $displayNameColumnEnd = -1
        
        foreach ($line in $subaccountsOutput) {
            if ($line -match 'guid|subaccount id') {
                $headerLine = $line
                # Find column positions - look for the next column header after guid/displayName
                # Typical format: "guid" or "subaccount id"  "display name"  "subdomain"  "region"
                $guidMatch = [regex]::Match($line, '(guid|subaccount id)\s+')
                if ($guidMatch.Success) {
                    $guidColumnEnd = $guidMatch.Index + $guidMatch.Length
                    # Find where display name column ends (look for next column)
                    $remainingLine = $line.Substring($guidColumnEnd)
                    if ($remainingLine -match 'display name\s+') {
                        $displayNameStart = $line.IndexOf('display name', $guidColumnEnd)
                        $afterDisplayName = $line.Substring($displayNameStart + 'display name'.Length)
                        if ($afterDisplayName -match '^\s+(\S+)') {
                            $displayNameColumnEnd = $line.IndexOf($matches[1], $displayNameStart)
                        }
                    }
                }
                continue
            }
            
            if ($line -match '^[-\s]+$' -or [string]::IsNullOrWhiteSpace($line)) {
                continue
            }
            
            if ($null -ne $headerLine -and $guidColumnEnd -gt 0) {
                # Extract columns using positions or fallback to split if positions not found
                if ($displayNameColumnEnd -gt $guidColumnEnd) {
                    $guid = $line.Substring(0, $guidColumnEnd).Trim()
                    $displayName = $line.Substring($guidColumnEnd, $displayNameColumnEnd - $guidColumnEnd).Trim()
                    $region = if ($line.Length -gt $displayNameColumnEnd) { 
                        $remaining = $line.Substring($displayNameColumnEnd).Trim()
                        # Skip subdomain, get region (may need to parse further)
                        ($remaining -split '\s{2,}')[1].Trim()
                    } else { "" }
                } else {
                    # Fallback to split method
                    $columns = $line -split '\s{2,}' | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
                    $guid = if ($columns.Count -ge 1) { $columns[0].Trim() } else { "" }
                    $displayName = if ($columns.Count -ge 2) { $columns[1].Trim() } else { "" }
                    $region = if ($columns.Count -ge 4) { $columns[3].Trim() } else { "" }
                }
                
                if (-not [string]::IsNullOrWhiteSpace($guid)) {
                    $subaccounts += [PSCustomObject]@{
                        guid = $guid
                        displayName = $displayName
                        region = $region
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
