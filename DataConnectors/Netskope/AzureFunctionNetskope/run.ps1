<#  
    Title:          Netskope Connector
    Language:       PowerShell
    Version:        1.0
    Author(s):      Microsoft
    Last Modified:  11/13/2020
    Comment:        Initial Release

    DESCRIPTION
    This Function App calls the Netskope Platform API (https://innovatechcloud.goskope.com/docs/Netskope_Help/en/rest-api-v2-overview.html) to pull alert and events data. The response from the Netskope API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post to the Netskope_CL table in the Log Analytics workspace.
#>

# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

$logAnalyticsUri = $env:logAnalyticsUri

# Function to contruct the Netskope Uri for alerts, event types, and to accomodate for pagination
function GetUrl ($uri, $ApiKey, $StartTime, $EndTime, $LogType, $Page, $Skip){
    if("$logtype" -eq "alert") {
         $url = "$uri/api/v1/alerts?token=$ApiKey&limit=$Page&starttime=$StartTime&endtime=$EndTime"
    }
    else{
       $url = "$uri/api/v1/events?token=$ApiKey&limit=$Page&type=$LogType&starttime=$StartTime&endtime=$EndTime"
    }
    if($skip -ne 0){
        $url = "$url&skip=$Skip"
        Write-Host "Retrieving next page of $LogType events skipping the previous $Skip records"
        return $url
    }
    else{
        return $url
    }
}


# Function for retrieving alerts and events from Netskope's APIs
function GetLogs ($Uri, $ApiKey, $StartTime, $EndTime, $LogType, $Page, $Skip){
    $url = GetUrl -Uri $Uri -ApiKey $ApiKey -StartTime $StartTime -EndTime $EndTime -logtype $LogType -Page $Page -Skip $Skip
    $obfurl = $url -replace "token=[a-z0-9]+\&", "token=<apiToken>&"
    Write-Host "Retrieving '$LogType' events from $obfurl"
    $response = Invoke-RestMethod -Uri $url
    if ($response.status -eq "error") {
        $errorCode = $response.errorCode
        $errors = $response.errors
        Write-Host "ERROR encountered while retrieving '$LogType' events - $errorCode - $errors"
    }
    else {
       return $response      
    }
}


# Function to retrieve the checkpoint start time of the last successful API call for a given logtype. Checkpoint file will be created if none exists
function GetStartTime($CheckpointFile, $LogType, $TimeInterval){
    $firstEndTimeRecord = (Get-Date -Date ((Get-Date).DateTime) -UFormat %s)
    $firstStartTimeRecord = $firstEndTimeRecord - $TimeInterval
    if ([System.IO.File]::Exists($CheckpointFile) -eq $false) {
        $CheckpointLog = @{}
        foreach ($apiType in $apitypes){
            $CheckpointLog.Add($apiType,$firstStartTimeRecord)
        }
        $CheckpointLog.GetEnumerator() | Select-Object -Property Key,Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
        return $firstStartTimeRecord 
    }
    else{
        $GetLastRecordTime = Import-Csv -Path $CheckpointFile
        $startTime = $GetLastRecordTime | ForEach-Object{ 
                        if($_.Key -eq $LogType){
                            $_.Value
                        }
                    }
        return $startTime
    }
}

# Function to update the checkpoint time with the last successful API call end time
function UpdateCheckpointTime($CheckpointFile, $LogType, $LastSuccessfulTime){
    $checkpoints = Import-Csv -Path $CheckpointFile
    $checkpoints | ForEach-Object{ if($_.Key -eq $LogType){$_.Value = $LastSuccessfulTime}}
    $checkpoints.GetEnumerator() | Select-Object -Property Key,Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
}

# Main Function to call the API and Post the response to the Log Analytics API
function Netskope () {

    $customerId = $env:workspaceId
    $sharedKey = $env:workspacekey
    $apikey = $env:apikey
    $uri = $env:uri
    $tableName = "Netskope"
    $timeInterval = [int]($env:timeInterval) * 60
    $pageLimit = 5000
    $skip = 0
    $loggingOptions = $env:logTypes
    $apitypes = @($loggingOptions.split(",").Trim())

    $cwd = (Get-Location).Drive.Root
    $checkPointFile = "$($cwd)home\site\NetskopeCheckpoint.csv"

    if ([string]::IsNullOrEmpty($logAnalyticsUri))
    {
        $logAnalyticsUri = "https://" + $customerId + ".ods.opinsights.azure.com"
    }
    
    # Returning if the Log Analytics Uri is in incorrect format.
    # Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
    if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
    {
        throw "Netskope: Invalid Log Analytics Uri."
    }
            
    foreach($logtype in $apitypes){

        $endTime = (Get-Date -Date ((Get-Date).DateTime) -UFormat %s)  
        $startTime = GetStartTime -CheckpointFile $checkPointFile -LogType $logtype -TimeInterval $timeInterval # function to create starttime

        $alleventobjs = @()
        $count = 0
        Do {
            $response = GetLogs -Uri $uri -ApiKey $apikey -StartTime $startTime -EndTime $endTime -LogType $logtype -Page $pageLimit -Skip $skip                     
            $netskopeevents = $response.data
            $dataLength = $response.data.Length
            $alleventobjs += $netskopeevents
    
                # Write-Host "$dataLength records added for '$logtype' events" 
                # If the API response length for the given log type is equal to the page limit, it indicates there are subsquent pages, continue while loop, and increment the skip value by the records already recieved for the subquent API requests
                if($dataLength -eq $pageLimit){
                    $skip = $skip + $pageLimit      
                }
                else {
                    # If the API response length for the given logtype is less than the page limit, it indicates there are no subsquent pages, break the while loop and move to the next logtype
                    $count = 1
                    $skip = 0
                    }
         
        } while ($count -eq 0)

        $allEventsLength = $alleventobjs.Length

        if ($allEventsLength -ne 0){
        $jsonPayload = $alleventobjs | ConvertTo-Json -Depth 3
        $mbytes = ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload)).Count/1024/1024
          
        # Check the payload size, if under 30MB post to Log Analytics.
        if (($mbytes -le 30)){                                
             $responseCode = Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload)) -logType $tableName
            if ($responseCode -ne 200){
                Write-Host "ERROR: Log Analytics POST, Status Code: $responseCode, unsuccessful."
            } 
            else {
                Write-Host "SUCCESS: $allEventsLength total '$logType' events posted to Log Analytics: $mbytes MB" -ForegroundColor Green
                UpdateCheckpointTime -CheckpointFile $checkPointFile -LogType $logtype -LastSuccessfulTime $endTime
            }
        }
        else {
            Write-Host "ERROR: Log Analytics POST failed due to paylog exceeding 30Mb: $mbytes"
            }
        }
        else {
            $startInterval = (Get-Date 01.01.1970)+([System.TimeSpan]::fromseconds($startTime))
            $endInterval = (Get-Date 01.01.1970)+([System.TimeSpan]::fromseconds($endTime))
            Write-Host "INFO: No new '$logtype' records created between $startInterval and $endInterval"
            UpdateCheckpointTime -CheckpointFile $checkPointFile -LogType $logtype -LastSuccessfulTime $endTime
        }
    }
}
 
# Function to build the authorization signature to post to Log Analytics
function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
{
    $xHeaders = "x-ms-date:" + $date;
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource;
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash);
    $keyBytes = [Convert]::FromBase64String($sharedKey);
    $sha256 = New-Object System.Security.Cryptography.HMACSHA256;
    $sha256.Key = $keyBytes;
    $calculatedHash = $sha256.ComputeHash($bytesToHash);
    $encodedHash = [Convert]::ToBase64String($calculatedHash);
    $authorization = 'SharedKey {0}:{1}' -f $customerId,$encodedHash;
    return $authorization;
}

# Function to POST the data payload to a Log Analytics workspace 
function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType)
{
    $TimeStampField = "DateValue"
    $method = "POST";
    $contentType = "application/json";
    $resource = "/api/logs";
    $rfc1123date = [DateTime]::UtcNow.ToString("r");
    $contentLength = $body.Length;
    $signature = Build-Signature -customerId $customerId -sharedKey $sharedKey -date $rfc1123date -contentLength $contentLength -method $method -contentType $contentType -resource $resource;
    $logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"

    $headers = @{
        "Authorization" = $signature;
        "Log-Type" = $logType;
        "x-ms-date" = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    };
    $response = Invoke-WebRequest -Body $body -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -UseBasicParsing
    return $response.StatusCode
}

# Execute the Function to pull Netskope alerts and events and post to a Log Analytics workspace

Netskope

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
