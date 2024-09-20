<#  
    Title:          Duo Security Data Connector
    Language:       PowerShell
    Version:        1.0
    Author(s):      Microsoft
    Last Modified:  2/10/2021
    Comment:        Inital Release

    DESCRIPTION
    This Function App calls the Duo Security Admin API (https://duo.com/docs/adminapi#logs) to pull the Duo
    Authentication, Administrator, Telephony and Offline Enrollment logs. The response from the Duo Security API is recieved in JSON format. This function will build the signature and authorization headers 
    needed to pull data from the Duo Security API and post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post each log type to their individual tables in Log Analytics, for example,
    DuoSecurityAuthentication_CL, DuoSecurityAdministrator_CL, DuoSecurityTelephony_CL, and DuoSecurityOfflineEnrollment_CL.
#>

# Input bindings are passed in via param block.
param($Timer)
# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()
# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late! $($Timer.ScheduledStatus.Last)"
    
}

# Define the different Duo Security Log Types. These values are set by the Duo Security API and required to seperate the log types into the respective Log Analytics tables
$DuoSecuritylogTypes = @{
    Authentication    = "/admin/v2/logs/authentication" 
    Administrator     = "/admin/v1/logs/administrator"
    Telephony         = "/admin/v1/logs/telephony"
    OfflineEnrollment = "/admin/v1/logs/offline_enrollment"
    TrustMonitor      = "/admin/v1/trust_monitor/events"
}

# Get Enviroment variables
$iKey = $env:iKey
$sKey = $env:sKey
$apiServer = $env:apiServer
$time = $env:timeInterval
$minTime = (((Get-Date).ToUniversalTime()).AddMinutes(-$time) | Get-Date -UFormat %s).ToString() + "000"
$maxTime = (Get-Date -UFormat %s).ToString() + "000"
$minTimeSeconds = (((Get-Date).ToUniversalTime()).AddMinutes(-$time) | Get-Date -UFormat %s).ToString()
$userAgent = "PowerShell"+$PSVersionTable.PSEdition+"/"+$PSVersionTable.PSVersion.ToString()+" ("+$PSVersionTable.OS+"; "+$PSVersionTable.Platform+"; "+"en-US) AzureSentinelDataConnector/1.0"


# Define the Log Analytics Workspace ID and Key
$CustomerId = $env:workspaceId
$SharedKey = $env:workspaceKey
$logAnalyticsUri = $env:logAnalyticsUri
$TimeStampField = "DateValue"

if (-Not [string]::IsNullOrEmpty($logAnalyticsUri)){
	if($logAnalyticsUri.Trim() -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
	{
		Write-Error -Message "DuoSecurity: Invalid Log Analytics Uri." -ErrorAction Stop
		Exit
	}
}

#Function to build Duo Security API Request
#Pulled from https://github.com/PWSHNinja/PSDuo/blob/master/PSDuo/private/Convertto-DUORequest.ps1
function Convertto-DuoRequest() {
    param(
        $iKey,
        $sKey,
        $apiServer,
        $DuoMethodPath,
        $APIParams,
        $method
    )
    #Decrypt our keys from our config
    $Date = (Get-Date).ToUniversalTime().ToString("ddd, dd MMM yyyy HH:mm:ss -0000")

    #Stringified Params/URI Safe chars - I think this should grab everything...
    $StringAPIParams = ($APIParams.Keys | Sort-Object | ForEach-Object {
            $_ + "=" + [uri]::EscapeDataString($APIParams.$_)
        }) -join "&"

    #DUO Params formatted and stored as bytes with StringAPIParams
    $DuoParams = (@(
            $Date.Trim(),
            $method.ToUpper().Trim(),
            $apiServer.ToLower().Trim(),
            $DuoMethodPath.Trim(),
            $StringAPIParams.trim()
        ).trim() -join "`n").ToCharArray().ToByte([System.IFormatProvider]$UTF8)

    #Hash out some secrets 
    $HMACSHA1 = [System.Security.Cryptography.HMACSHA1]::new($sKey.ToCharArray().ToByte([System.IFormatProvider]$UTF8))
    $hmacsha1.ComputeHash($DuoParams) | Out-Null
    $ASCII = [System.BitConverter]::ToString($hmacsha1.Hash).Replace("-", "").ToLower()

    #Create the new header and combing it with our iKey to use it as Authentication
    $AuthHeadder = $iKey + ":" + $ASCII
    [byte[]]$ASCIBytes = [System.Text.Encoding]::ASCII.GetBytes($AuthHeadder)

    #Create our Parameters for the webrequest - Easy @Splatting!
    $DUOWebRequestParams = @{
        URI         = ('Https://{0}{1}' -f $apiServer, $DuoMethodPath)
        Headers     = @{
            "X-Duo-Date"    = $Date
            "Authorization" = ('Basic {0}' -f [System.Convert]::ToBase64String($ASCIBytes))
        }
        Body        = $APIParams
        Method      = $method
        ContentType = 'application/x-www-form-urlencoded'
        UserAgent   = $userAgent
    }
    return $DUOWebRequestParams
}

# Function to build the Authorization signature for the Log Analytics Data Connector API
Function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource) {
    $xHeaders = "x-ms-date:" + $date
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource

    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
    $keyBytes = [Convert]::FromBase64String($sharedKey)

    $sha256 = New-Object System.Security.Cryptography.HMACSHA256
    $sha256.Key = $keyBytes
    $calculatedHash = $sha256.ComputeHash($bytesToHash)
    $encodedHash = [Convert]::ToBase64String($calculatedHash)
    $authorization = 'SharedKey {0}:{1}' -f $customerId, $encodedHash
    
    # Dispose SHA256 from heap before return.
    $sha256.Dispose()

    return $authorization
}

# Function to create and invoke an API POST request to the Log Analytics Data Connector API
Function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType) {
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
    
        # Compatible with previous version
		if ([string]::IsNullOrEmpty($logAnalyticsUri)){
			$logAnalyticsUri = "https://" + $CustomerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
		}
		else
		{
			$logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"
		}

    $headers = @{
        "Authorization"        = $signature;
        "Log-Type"             = $logType;
        "x-ms-date"            = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    }

    $response = Invoke-WebRequest -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    return $response.StatusCode

}

# Iterate through the Duo Security API response and if there are log events present, POST the events to the Log Analytics API into the respective tables.
ForEach ($DSLogType in $DuoSecurityLogTypes.Keys) {
    Write-Debug $DSLogType
    $LogPath = $DuoSecuritylogTypes[$DSLogType]
    $moreLogs = $true
    
    #Define first run params for
    switch ($DSLogType) {
        "Authentication" { 
            $ApiParams = @{
                mintime = $minTime
                maxtime = $maxTime
                limit   = 1000
            }
        }
        "TrustMonitor" {
            $ApiParams = @{
                mintime = $minTime
                maxtime = $maxTime
                limit = 200
            }
        }
        Default {
            $ApiParams = @{
                mintime = $minTimeSeconds
            }
        }
    }

    #Loop to iterate and get logs
    do {
        #Get Logs
        $DuoRequest = Convertto-DuoRequest -DuoMethodPath $LogPath -method GET -APIParams $ApiParams -iKey $iKey -sKey $sKey -apiServer $apiServer
        $Response = Invoke-RestMethod @DuoRequest

        #Stop loop if call fails
        If ($Response.stat -ne 'OK') {
            Write-Warning 'DUO REST Call Failed'
            Write-Warning "APiParams:"+($APiParams | Out-String)
            Write-Warning "Method:GET    Path:$LogPath"
            break
        }

        #HAndle Various Outputs
        switch ($DSLogType) {
            "Authentication" { $Output = $Response | Select-Object -ExpandProperty Response | Select-Object -ExpandProperty authlogs }
            "TrustMonitor" { $Output = $Response | Select-Object -ExpandProperty Response | Select-Object -ExpandProperty events }
            Default { $Output = $Response | Select-Object -ExpandProperty Response }
        }     

        #Write Output
        if ($Output.Length -eq 0 ) { 
            Write-Host ("DuoSecurity$($DSLogType) reported no new logs for the time interval configured.")
        }
        else {
            # if the log entry is a null, this occurs on the last line of each LogType. Should only be one per log type
            if ($Output -eq $null) {
                # exclude it from being posted
                Write-Host ("DuoSecurity$($DSLogType) null line excluded")    
            } 
            else {
                # convert each log entry and post each entry to the Log Analytics API
                $json = $Output | ConvertTo-Json -Depth 20
                Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($json)) -logType "DuoSecurity$($DSLogType)"
            }
        }

        #Check for more logs
        switch ($DSLogType) {
            "Authentication" {
                if ($Response.response.metadata.next_offset.Count -eq 2) {
                    [string]$nextOffset = $Response.response.metadata.next_offset[0] + "," + $Response.response.metadata.next_offset[1]
                    $ApiParams = @{
                        mintime     = $minTime
                        maxtime     = $maxTime
                        limit       = 1000
                        next_offset = $nextOffset
                    }
                }
                else {
                    $moreLogs = $false
                }
            }
            "TrustMonitor" {
                if ($Response.response.metadata.next_offset.Count -eq 1) {
                    $offset = $Response.response.metadata.next_offset
                    $ApiParams = @{
                        mintime = $minTime
                        maxtime = $maxTime
                        limit   = 500
                        offset  = $offset
                    }
                }
                else {
                    $moreLogs = $false
                }
            }
            Default {
                if ($Response.response.Count -ne 0) {
                    $minTimeSeconds = $Response.response[-1].timestamp + 1
                    $ApiParams = @{
                        mintime = $minTimeSeconds
                    }
                }
                else {
                    $moreLogs = $false
                }
            }
        }

    } until ($moreLogs -eq $false)
}
# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
