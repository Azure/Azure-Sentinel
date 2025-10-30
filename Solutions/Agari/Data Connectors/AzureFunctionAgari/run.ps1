# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format 
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

$logAnalyticsUri = $env:logAnalyticsUri

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"

# Get ENV parameters 

# Agari Client ID and Secret 
$client_id = $env:clientID
$client_secret = $env:clientSecret
$apiToken = $false
$revoke_api_token_uri = $false

# Define the Log Analytics Workspace ID and Keys
$CustomerId = $env:workspaceId
$SharedKey = $env:workspaceKey

# Define the Graph API credentials
$GraphTenantId = $env:GraphTenantId
$GraphClientId = $env:GraphClientId
$GraphClientSecret = $env:GraphClientSecret

#Define Product(s) Enabled
$bpEnabled = $env:enableBrandProtectionAPI
$aprEnabled = $env:enablePhishingResponseAPI
$apdEnabled = $env:enablePhishingDefenseAPI
$sgEnabled = $env:enableSecurityGraphSharing

#Function App Configuration for Timer Functions
$resGrp = $env:resGroup
$appName = $env:functionName
$subid = $env:subId
$bplastLog = $env:BPlastLogTime
$apdlastLog = $env:APDlastLogTime
$aprlastLog = $env:APRlastLogTime

if ([string]::IsNullOrEmpty($logAnalyticsUri))
{
    $logAnalyticsUri = "https://" + $CustomerId + ".ods.opinsights.azure.com"
}

# Returning if the Log Analytics Uri is in incorrect format.
# Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
{
    throw "Agari: Invalid Log Analytics Uri."
}

# Set boolean values based on environment variables
if ($bpEnabled -Match "True"){
    $bpEnabled = $true
} else {
    $bpEnabled = $false 
}

if ($apdEnabled -Match  "True"){
    $apdEnabled = $true
} else {
    $apdEnabled = $false 
}

if ($aprEnabled -Match  "True"){
    $aprEnabled = $true
} else {
    $aprEnabled = $false
}

if ($sgEnabled -Match "True"){
    $sgEnabled = $true
} else {
    $sgEnabled = $false
}

# Function to build the Authorization signature for the Log Analytics Data Connector API
Function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
{
    $xHeaders = "x-ms-date:" + $date
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource

    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
    $keyBytes = [Convert]::FromBase64String($sharedKey)

    $sha256 = New-Object System.Security.Cryptography.HMACSHA256
    $sha256.Key = $keyBytes
    $calculatedHash = $sha256.ComputeHash($bytesToHash)
    $encodedHash = [Convert]::ToBase64String($calculatedHash)
    $authorization = 'SharedKey {0}:{1}' -f $customerId,$encodedHash
    
    # Dispose SHA256 from heap before return.
    $sha256.Dispose()

    return $authorization
}

# Function to create and invoke an API POST request to the Log Analytics Data Connector API
Function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType)
{
    $method = "POST"
    $contentType = "application/json"
    $resource = "/api/logs"
    $rfc1123date = [DateTime]::UtcNow.ToString("r")
    $contentLength = $body.Length
    $signature = Build-Signature `
        -customerId $customerId `
        -sharedKey $sharedKey `
        -date $rfc1123date `
        -contentLength $contentLength `
        -method $method `
        -contentType $contentType `
        -resource $resource

    $logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"

    $headers = @{
        "Authorization" = $signature;
        "Log-Type" = $logType;
        "x-ms-date" = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    }

    $response = Invoke-WebRequest -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    return $response.StatusCode
}

# Timer Function to stamp the last successful log into the environment variable
Function SetLastLogTime ($subid,$resGrp,$appName,$nextStartDate,$apdLogSuccess,$aprLogSuccess,$bpLogSuccess)
{
    #Get the subscription
    Select-AzSubscription -Subscriptionid $subid
    #Getting WebApp info
    $webApp = Get-AzWebApp -ResourceGroupName $resGrp -Name $appName

    # Read App Settings and load into Hash Table
    $appSettingList = $webApp.SiteConfig.AppSettings
    $newAppSettingList = @{}
    ForEach ($kvp in $appSettingList) {
        $newAppSettingList[$kvp.Name] = $kvp.Value
    }

    # Add in new value for last log time NOTE: have to mangle the date with a "t" prefix due to issue Set-AzWebApp #8277
    if ($apdLogSuccess){
        $newAppSettingList['APDlastLogTime'] = "t$nextStartDate"
    }
    if ($aprLogSuccess){
        $newAppSettingList['APRlastLogTime'] = "t$nextStartDate"
    }
    if ($bpLogSuccess){
        $newAppSettingList['BPlastLogTime'] = "t$nextStartDate"
    }
    # Write to App Settings if there are changes
    if(($apdLogSuccess) -or ($aprLogSuccess) -or ($bpLogSuccess)){
        Set-AzWebApp -ResourceGroupName $resGrp -Name $appName -AppSettings $newAppSettingList
    }
}

# Function to get Agari product bearer token
Function GetToken($client_id,$client_secret,$TokenURI) {
    $GetTokenHeaders=@{
        'accept'='application/json'
        'content-type'='application/x-www-form-urlencoded'
    }
    $result = Try {Invoke-WebRequest -uri $TokenURI -Method 'POST' -Headers $GetTokenHeaders -Body "grant_type=client_credentials&client_id=$client_id&client_secret=$client_secret"} catch {Write-Host "StatusCode:" $_.Exception.Response.StatusCode.value__}
    # Really simple error check, if we get a 200 return the bearer token, ortherwise return false
    if ($result.StatusCode -eq 200) {
        return ($result.Content | ConvertFrom-Json).access_token 
    } else {
        return $false
    }
}

# Function to revoke the Agari bearer token
Function RevokeToken($revokeToken_uri, $token) {
    $RevokeTokenHeaders=@{
        'accept'='application/json'
        'content-type'='application/x-www-form-urlencoded'
        'authorization'="Bearer $token"
    }
        Invoke-WebRequest -uri $revokeToken_uri -Method POST -Headers $RevokeTokenHeaders -Body "token=$token" | Out-Null
}

# Function for creating the Threat Indicators body based on threat type
Function Body-SentinelTI($GraphTenantId,$IoC_Type,$IoC,$Product,$expiry){
    $body=@{
        'action' = "alert"
        'azureTenantId' = $GraphTenantId
        'description' = "$IoC_Type IoC from Agari $Product"
        'expirationDateTime'= $expiry
        'targetProduct' = 'Azure Sentinel'
        'tlpLevel' = "Amber"
        'vendorInformation'= 'Agari'
    }
        switch ($IoC_Type) {
        'Domain' {$body.Add("emailSourceDomain", "$IoC")}
        'Domain' {$body.Add('threatType','Phishing')}
        'IP' {$body.Add('networkDestinationIPv4',"$IoC")}
        'IP'{$body.Add('threatType','Phishing')}
        'URL' {$body.Add('url',"$IoC")}
        'URL'{$body.Add('threatType','MaliciousURL')}
        'File'{$body.Add('fileHashValue',"$IoC")}
        'File'{$body.Add('fileHashType','sha256')}
        'File'{$body.Add('threatType','Malware')}
        }
    $sg_body = $body | ConvertTo-Json
    return $sg_body
    }

# Setup the SGAPI call
if ($sgEnabled){
    # Set a 10 day expiry for the IoC
    $expiry=(Get-Date (get-date).addDays(10) -UFormat "+%Y-%m-%dT%H:00:00.00Z")
    #Get the token for the Securty Graph API calls
        $uri = "https://login.microsoftonline.com/$GraphTenantId/oauth2/v2.0/token"
        $body = @{
            client_id     = $GraphClientId
            scope         = "https://graph.microsoft.com/.default"
            client_secret = $GraphClientSecret
            grant_type    = "client_credentials"
        }
        # Get OAuth 2.0 Token
        $tokenRequest = Invoke-WebRequest -Method Post -Uri $uri -ContentType "application/x-www-form-urlencoded" -Body $body -UseBasicParsing
        # Unpack Access Token if we get a success
        if ($tokenRequest.StatusCode -eq 200) {
            $sgapi_token = ($tokenRequest.Content | ConvertFrom-Json).access_token
            # Base URL
            $sgapi_uri = 'https://graph.microsoft.com/beta/security/tiIndicators'
            $sgapi_headers = @{
                            'Authorization' = "Bearer $sgapi_token"
                            'ContentType' = 'application/json'
                        }
        } else {
            $sgEnabled = $false
            Write-Host "Error fetching token for the Security Graph API call"
        }
}

#Set uris for get/revoke bearer tokens
$get_apd_token_uri='https://api.agari.com/v1/ep/token'
$get_bp_token_uri='https://api.agari.com/v1/cp/oauth/token'
$get_apr_token_uri='https://api.agari.com/v1/apr/token'
$revoke_apd_token_uri='https://api.agari.com/v1/ep/revoke'
$revoke_apr_token_uri='https://api.agari.com/v1/apr/revoke'
$revoke_bp_token_uri='https://api.agari.com/v1/cp/oauth/revoke'

# Get the Bearer Tokens
if ($bpEnabled){
    #Get the bearer token
    if ($apiToken){
    } else {
        $apiToken = GetToken $client_id $client_secret $get_bp_token_uri
    }
    # set the headers
    if ($apiToken){
        $bpHeaders = @{
                    'Authorization' = "Bearer $apiToken"
                    'ContentType' = 'application/json'
                    'UserAgent' = "AgariSentinel BP_Integration/v1.0 SentinelPowerShellCore/v$PSVersionTable.PSVersion.major"
                }
        $revoke_api_token_uri = $revoke_bp_token_uri
    } else {
        $apiToken = $false
        Write-Host "Error Fetching BP Token" 
        }
}
if ($apdEnabled){
    #Get the bearer token
    if ($apiToken){
    } else {
        $apiToken = GetToken $client_id $client_secret $get_apd_token_uri
    }
    # set the headers
    if ($apiToken){
        $apdHeaders = @{
                    'Authorization'="Bearer $apiToken"
                    'ContentType' = 'application/json'
                    'UserAgent' = "AgariSentinel APD_Integration/v1.0 SentinelPowerShellCore/v$PSVersionTable.PSVersion.major"
                }
        $revoke_api_token_uri = $revoke_adp_token_uri
    } else {
        $apiToken = $false
        Write-Host "Error Fetching APD Token" 
        }
}
if ($aprEnabled){
    #Get the bearer token
    if ($apiToken){
    } else {
        $apiToken = GetToken $client_id $client_secret $get_apr_token_uri
    }
    # set the headers
    if ($apiToken){
        $aprHeaders = @{
                    'Authorization'="Bearer $apiToken"
                    'ContentType' = 'application/json'
                    'UserAgent' = "AgariSentinel APR_Integration/v1.0 SentinelPowerShellCore/v$PSVersionTable.PSVersion.major"
                }
        $revoke_api_token_uri = $revoke_apr_token_uri
    } else {
        $apiToken = $false
        Write-Host "Error Fetching APR Token" 
        }
}

#Set global api variables
#set first run startdate
$fr_startdate=(Get-Date (get-date).addMinutes(-6) -UFormat "+%Y-%m-%dT%H:%M:00:001Z")
#set the enddate
$enddate=(Get-Date (get-date).addMinutes(-1) -UFormat "+%Y-%m-%dT%H:%M:00.000Z")
#if successful, we'll popoulate the environment variable with the end date + 1ms
$nextStartDate = (Get-Date (get-date).addMinutes(-1) -UFormat "+%Y-%m-%dT%H:%M:00:001Z")
$limit = 200
$offset = 0
$TimeStampField = "DateValue"

# --------------------------------------------------- #
# Below is for loading BP Logs and TIs into Sentinel. #
# --------------------------------------------------- #

#Check if BP is enabled and we got a token
if (($bpEnabled) -and ($apiToken)) {
    #Check to see if start time empty - usally first run, otherwise set the time from the env variable
    if ($BPlastLog){
        $BPstartdate = $BPlastLog.substring(1)  
    } else {
        $BPstartdate = $fr_startdate
    }
    $offset = 0
    do {
        $BPAlertsListAPI = "https://api.agari.com/v1/cp/alert_events?start_date=$BPstartdate&end_date=$enddate&fields=id%2C&limit=$limit&offset=$offset&sort=created_at%20ASC"
        Invoke-RestMethod -Uri $BPAlertsListAPI -Method 'GET' -Headers $bpHeaders  | ForEach-Object {
        $ids += $_.alert_events | Select-Object -ExpandProperty id
        $count = $_.count
        $bpLogSuccess = $true
        }
    $offset += $limit
    } while ($count -eq $limit)

    #Loop through each ID and add to the bp_alert log
    foreach ($id in $ids) {
        $GetIDAPI="https://api.agari.com:443/v1/cp/alert_events/$id"
        Invoke-RestMethod -Uri $GetIDAPI -Method 'GET' -Headers $bpHeaders | ForEach-Object {
            $id_data = $_.alert_event
            $id_log = $id_data | ConvertTo-Json -Depth 3
            Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($id_log)) -logType "agari_bpalerts_log"
            }
    }
    # Load the URLs from the BP Threat Feed to Security Graph if enabled
    if ($sgEnabled){
        $Product = 'Brand Protection'
        #Get the Threat Feed ID
        $BP_TF_Url = "https://api.agari.com/v1/cp/threat_feeds"
        Invoke-RestMethod -Uri $BP_TF_Url -Method 'GET' -Headers $bpHeaders | Out-Null 
        # If there is a Threat ID, get the URIs in the feed
        if ($_.threat_feeds.id){
            $IoC_Type = 'URL'
            foreach ($sub_id in $_.threat_feeds.id){
                $BP_SubmissionUrl = "https://api.agari.com/v1/cp/threat_feeds/$sub_id/submissions?start_date=$BPstartdate&end_date=$enddate"
                Invoke-RestMethod -Uri $BP_SubmissionUrl -Method 'GET' -Headers $bpHeaders | ForEach-Object {
                    $bpBody = (Body-SentinelTI $GraphTenantId $IoC_Type $_.threat_feed_submissions.uri $Product $expiry)
                    Invoke-WebRequest -Method POST -Uri $sgapi_uri -Headers $sgapi_headers -Body $bpBody 
                }
            }
        }
    }
}

# -------------------------------------------- #
# Below is for loading APD Logs into Sentinel. #
# -------------------------------------------- #

#Check if APD is enabled 
if (($apdEnabled) -and ($apiToken)){
        #Check to see if start time empty - usally first run, otherwise set the time from the env variable
        if ($apdlastLog){
            $APDstartdate = $APDlastLog.substring(1)  
        } else {
            $APDstartdate = $fr_startdate
        }
        #Reset the Offset
        $offset = 0          
        #Get the APD policy hits with the offset for paging
        do {
            $APDPolicyAPI = "https://api.agari.com/v1/ep/policy_events?limit=$limit&offset=$offset&sort=created_at%20DESC&policy_enabled=true&start_date=$APDstartdate&end_date=$enddate"
            Invoke-RestMethod -Uri $APDPolicyAPI -Method 'GET' -Headers $apdHeaders | ForEach-Object {
                $APDPolicyData += $_.alert_events | Select-Object -Property created_at, id, alert_definition_name
                $count = $_.count
                }
                $offset += $limit
        } while ($count -eq $limit)

        # If there are results, convert log to JSON and Post the data to log analytics API
        if ($APDPolicyData){
            $APDPolicyLog = $APDPolicyData | ConvertTo-JSON
            Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($APDPolicyLog)) -logType "agari_apdpolicy_log"
        }
        #Get the Threat Categories and push to Sentinel
        #Reset the Offset
        $offset = 0   
        #Get the APD Threat Categories API call with the offset for paging
        do {
        $APDThreatCatAPI = "https://api.agari.com/v1/ep/messages?start_date=$APDstartdate&end_date=$enddate&fields=attack_types%2Cto%2Cfrom%2Cid%2Cfrom_domain%2Ctimestamp_ms&limit=$limit&offset=$offset&sort=timestamp_ms%20DESC&search=attack_types%20is%20not%20empty"
            Invoke-RestMethod -Uri $APDThreatCatAPI -Method 'GET' -Headers $apdHeaders | ForEach-Object {
            $APDThreatCatData += $_.messages | Select-Object -Property to, from, from_domain, attack_types,id,timestamp_ms 
            $count = $_.count
            $apdLogSuccess = $true
            }
        $offset += $limit
        } while ($count -eq $limit)
        # If there are results, convert log to JSON and Post the data to log analytics API
        if ($APDThreatCatData){
            $APDThreatCatLog = $APDThreatCatData | ConvertTo-Json
            Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($APDThreatCatLog)) -logType "agari_apdtc_log"
        }
}

# ---------------------------------------------------------------------- #
# Below is for loading APR TIs into Sentinel via the Security Graph API. #
# ---------------------------------------------------------------------- #

if ($sgEnabled){
    # If APR enabled, get all malicious IoC verdicts from investigations 
    if (($aprEnabled) -and ($apiToken)){
        #Check to see if start time empty - usally first run, otherwise set the time from the env variable
        if ($aprlastLog){
            $APRstartdate = $APRlastLog.substring(1)  
        } else {
            $APRstartdate = $fr_startdate
        }
        $Product = 'Phishing Response'
        #Query the latest investigations that are malicious and get the TIs
        $APRUrl = "https://api.agari.com/v1/apr/investigations?start_date=$APRstartdate&end_date=$enddate&classification=malicious"
        Invoke-RestMethod -Uri $APRUrl -Method 'GET' -Headers $aprHeaders | ForEach-Object {
            #Get the IDs of the investigations, we'll need these to get file hash values
            $inv_id = $_.investigations.id
            #Get the unique IoCs from the investigations
            $TI_DOMAIN = $_.investigations.indicators.domain.summary.resource | Select-Object -Unique
            $TI_URI = $_.investigations.indicators.uri.summary.resource | Select-Object -Unique
            $TI_IP = $_.investigations.indicators.ip.summary.resource | Select-Object -Unique
            $aprLogSuccess = $true
        }
        #Load the Domain IoCs
        if ($TI_DOMAIN) {
            $IoC_Type = "Domain"
            foreach ($domain_ioc in $TI_DOMAIN) {
                $domainBody = Body-SentinelTI $GraphTenantId $IoC_Type $domain_ioc $Product $expiry
                Invoke-WebRequest -Method POST -Uri $sgapi_uri -Headers $sgapi_headers -Body $domainBody
            }
        }
        #Load the URL IoCs
        if ($TI_URI) {
            $IoC_Type = "URL"
            foreach ($url_ioc in $TI_URL) {
                $urlBody = Body-SentinelTI $GraphTenantId $IoC_Type $url_ioc $Product $expiry
                Invoke-WebRequest -Method POST -Uri $sgapi_uri -Headers $sgapi_headers -Body $urlBody
            }
        }
        #Load the IP IoCs
        if ($TI_IP) {
        $IoC_Type = "IP"
        foreach ($ip_ioc in $TI_IP) {
            $ipBody = Body-SentinelTI $GraphTenantId $IoC_Type $ip_ioc $Product $expiry
            Invoke-WebRequest -Method POST -Uri $sgapi_uri -Headers $sgapi_headers -Body $ipBody
            }
        }
        #Files are special, need to go by ID to fetch the SHA values
        foreach ($hash_byid in $inv_id) {
            $GetHashAPI = "https://api.agari.com/v1/apr/investigations/$hash_byid/attachments?fields=hash_sha256"
            $HashAPIcall = Invoke-RestMethod -Uri $GetHashAPI -Method 'GET' -Headers $aprHeaders
            if ($HashAPIcall.attachments.hash_sha256) {
                $IoC_Type = "File"
                foreach ($file_ioc in $HashAPIcall.attachments.hash_sha256) {
                $hashBody = Body-SentinelTI $GraphTenantId $IoC_Type $file_ioc $Product $expiry
                Invoke-WebRequest -Method POST -Uri $sgapi_uri -Headers $sgapi_headers -Body $hashBody
                }
            }
        }
    }
}

# We done, revoke the apiToken!
if ($revoke_api_token_uri){
    RevokeToken $revoke_api_token_uri $apiToken
}

# Write the environment variable for the next startdate
SetLastLogTime $subid $resGrp $appName $nextStartDate $apdLogSuccess $aprLogSuccess $bpLogSuccess
