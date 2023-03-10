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

# Function to call the Netskope API for different Event Types
function CallNetskope($logtype) {

# Function to contruct the Netskope Uri for alerts, event types, and to accomodate for pagination
function GetUrl ($uri, $ApiKey, $StartTime, $EndTime, $LogType, $Page, $Skip){
    if("$logtype" -eq "alert") {
        $url = "$uri/api/v1/alerts?token=$ApiKey&limit=$Page&starttime=$StartTime&endtime=$EndTime"
    }
    else {
        $url = "$uri/api/v1/events?token=$ApiKey&limit=$Page&type=$LogType&starttime=$StartTime&endtime=$EndTime"
    }
    if ($skip -ne 0) {
        $url = "$url&skip=$Skip"
        Write-Host "Retrieving next page of $LogType events skipping the previous $Skip records"
        return $url
    }
    else {
        return $url
    }
}

    # Function for retrieving alerts and events from Netskope's APIs
    function GetNetSkopeAPILogs($logtype) {

        $timeInterval = [int]($env:timeInterval) * 60
        $pageLimit = 10000
        $skip = 0
        $cwd = (Get-Location).Drive.Root
        $checkPointFile = "$($cwd)home\site\NetskopeCheckpoint.csv"
        # $checkPointFile = "C:\Users\v-rucdu\Downloads\NetskopeCheckpoint.csv"
        $apikey = $env:apikey
        $uri = $env:uri
        $tableName = "Netskope"
        $LastRecordObject = GetStartTime -CheckpointFile $checkPointFile -LogType $logtype -TimeInterval $timeInterval # function to create starttime
        $LastRecordData = $LastRecordObject.Split("|");
        $startTime = [Int]($LastRecordData[0])
        $skip = $LastRecordData.Length -gt 1 ? [Int]($LastRecordData[1]) : $skip
        $endTime = [Int]($startTime + $timeInterval)
        Write-Host "For Logtype $($logtype) starttime is $($startTime) and endtime is $($endTime)."
        #$netskopestartInterval = (Get-Date 01.01.1970)+([System.TimeSpan]::fromseconds($startTime))
        #netskopeendInterval = (Get-Date 01.01.1970)+([System.TimeSpan]::fromseconds($endTime))
        #$netskopetimediff = ($netskopeendInterval - $netskopestartInterval)
        #if($netskopetimediff.TotalSeconds -gt 300)
        #{
        #   Write-Host "Time difference is > 10 minutes for Logtype :- $($logtype).Hence Resetting the endtime to add 10 minutes difference between starttime - $($startTime)  and endtime - $($endTime) "
        #   $endTime = [Int](Get-Date -Date ($netskopestartInterval.AddSeconds(600)) -UFormat %s)
        #   Write-Host "For Logtype $($logtype) new modified endtime is $($endTime)"
        #}
        #$alleventobjs = @()
        $count = 0
        $functionStartTimeEpoch = (Get-Date -Date ((Get-Date).DateTime) -UFormat %s)
        Do {
            try {
                $endTime = [Int]($startTime + $timeInterval)
                if ($endTime -gt ((Get-Date -Date ((Get-Date).DateTime) -UFormat %s))) {
                    break
                }
                $response = GetLogs -Uri $uri -ApiKey $apikey -StartTime $startTime -EndTime $endTime -LogType $logtype -Page $pageLimit -Skip $skip
                $netskopeevents = $response.data

                if($null -ne $netskopeevents)
                {
                    $netskopeevents | Add-Member -MemberType NoteProperty dlp_incidentid -Value ""
                    $netskopeevents | Add-Member -MemberType NoteProperty dlp_parentid -Value ""
                    $netskopeevents | Add-Member -MemberType NoteProperty connectionid -Value ""
                    $netskopeevents | Add-Member -MemberType NoteProperty app_sessionid -Value ""
                    $netskopeevents | Add-Member -MemberType NoteProperty transactionid -Value ""
                    $netskopeevents | Add-Member -MemberType NoteProperty browser_sessionid -Value ""
                    $netskopeevents | Add-Member -MemberType NoteProperty requestid -Value ""

                    $netskopeevents | ForEach-Object{
                        if($_.dlp_incident_id -ne $NULL){
                                $_.dlp_incidentid = [string]$_.dlp_incident_id
                        }
                        if($_.dlp_parent_id -ne $NULL){
                                $_.dlp_parentid = [string]$_.dlp_parent_id
                        }
                        if($_.connection_id -ne $NULL){
                                $_.connectionid = [string]$_.connection_id
                        }
                        if($_.app_session_id -ne $NULL){
                                $_.app_sessionid = [string]$_.app_session_id
                        }
                        if($_.transaction_id -ne $NULL){
                                $_.transactionid = [string]$_.transaction_id
                        }
                        if($_.browser_session_id -ne $NULL){
                                $_.browser_sessionid = [string]$_.browser_session_id
                        }
                        if($_.request_id -ne $NULL){
                                $_.requestid = [string]$_.request_id
                        }
                    }

                    #$dataLength = $netskopeevents.Length
                    #$alleventobjs += $netskopeevents
                    $allEventsLength = $netskopeevents.Length
                    $responseCode = ProcessData -allEventsLength $allEventsLength -alleventobjs $netskopeevents -checkPointFile $checkPointFile -logtype $logtype -endTime $endTime
                    # If the API response length for the given log type is equal to the page limit, it indicates there are subsquent pages, continue while loop, and increment the skip value by the records already recieved for the subquent API requests
                    if($allEventsLength -eq $pageLimit){
                        $skip = $skip + $pageLimit
                    }
                    else {
                        # If the API response length for the given logtype is less than the page limit, it indicates there are no subsquent pages, break the while loop and move to the next logtype
                        $skip = 0
                        $count = 1
                        
                     }
                }                
                
                if($responseCode -ne 200) {
                   Write-Error "ERROR: Log Analytics POST, Status Code: $responseCode, unsuccessful."
                    $skip =  $skip - $pageLimit -lt 0 ? 0 : $skip - $pageLimit
                    UpdateCheckpointTime -CheckpointFile $checkPointFile -LogType $logtype -LastSuccessfulTime $startTime -skip $skip
                }elseif($count -eq 0) {
                   UpdateCheckpointTime -CheckpointFile $checkPointFile -LogType $logtype -LastSuccessfulTime $startTime -skip $skip
                }else {
                   UpdateCheckpointTime -CheckpointFile $checkPointFile -LogType $logtype -LastSuccessfulTime $endTime -skip $skip
                    $startTime = $startTime + $timeInterval
                    $count = 0
                    Write-Host "For Logtype $($logtype) modified starttime is $($startTime)."
                }   

                $functionCurrentTimeEpoch = (Get-Date -Date ((Get-Date).DateTime) -UFormat %s)
                $TimeDifferenceEpoch = $functionCurrentTimeEpoch - $functionStartTimeEpoch
                
                if ($TimeDifferenceEpoch -ge 420) {
                    Write-Host "Exiting from do while loop for logType : $($logtype) to avoid function timeout."
                    #UpdateCheckpointTime -CheckpointFile $checkPointFile -LogType $logtype -LastSuccessfulTime $startTime -skip $skip
                    break
                }

            }
            catch {
                UpdateCheckpointTime -CheckpointFile $checkPointFile -LogType $logtype -LastSuccessfulTime $startTime -skip $skip
                Write-Host "Exiting from do while loop for logType : $($logtype) because of error message as : " + $($Error[0].Exception.Message)
                break
            }

        } while ($count -eq 0)

        #if($count -eq 1)
        #{
        #    UpdateCheckpointTime -CheckpointFile $checkPointFile -LogType $logtype -LastSuccessfulTime $endTime -skip $skip
        #} 
    }

    # Function for processing the Netskope's API response
    function ProcessData($allEventsLength, $alleventobjs, $checkPointFile, $logtype, $endTime, $skip) {
        Write-Host "Process Data function:- EventsLength - $($allEventsLength), Logtype - $($logtype) and Endtime - $($endTime)"
        $customerId = $env:workspaceId
        $sharedKey = $env:workspacekey
        $responseCode = 200
        if ($allEventsLength -ne 0) {
            $jsonPayload = $alleventobjs | ConvertTo-Json -Depth 3
            $mbytes = ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload)).Count / 1024 / 1024
            Write-Host "Total mbytes :- $($mbytes) for type :- $($logtype)"
            # Check the payload size, if under 30MB post to Log Analytics.
            if (($mbytes -le 30)) {
                $responseCode = Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload)) -logType $tableName
                if($responseCode -eq 200){
                    Write-Host "SUCCESS: $allEventsLength total '$logType' events posted to Log Analytics: $mbytes MB" -ForegroundColor Green
                }
            }
            else {
                Write-Host "Warning!: Total data size is > 30mb hence performing the operation of split and process."
                $responseCode = SplitDataAndProcess -customerId $customerId -sharedKey $sharedKey -payload $alleventobjs -logType $tableName
            }
        }
        else {
            $startInterval = (Get-Date 01.01.1970) + ([System.TimeSpan]::fromseconds($startTime))
            $endInterval = (Get-Date 01.01.1970) + ([System.TimeSpan]::fromseconds($endTime))
            Write-Host "INFO: No new '$logtype' records created between $startInterval and $endInterval"
        }
        return $responseCode
    }

    # Function to update the checkpoint time with the last successful API call end time
    function UpdateCheckpointTime ($CheckpointFile, $LogType, $LastSuccessfulTime, $skip) {
        try {
            Write-Host "CheckpointFile : $($checkPointFile) | LogType : $($LogType) | LastSuccessfulTime : $($LastSuccessfulTime) | skip : $($skip)"
            $mutex = New-Object System.Threading.Mutex($false, 'NetSkopeCsvConnection')
        
                $mutex.WaitOne() > $null;
                $LastSuccessfulTime  = $LastSuccessfulTime.ToString() + "|" + $skip
                $checkpoints = Import-Csv -Path $CheckpointFile
                if ($null -ne $checkpoints){                
                    Write-Host "CHECKPOINT FILE : $($checkpoints.Length)"
                } else {
                    Write-Host "Checkpointing file is Null."
                }
                $checkpoints | ForEach-Object { if ($_.Key -eq $LogType) { $_.Value = $LastSuccessfulTime } }
                # $checkpoints | Select-Object -Property Key,Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
                $checkpoints.GetEnumerator() | Select-Object -Property Key, Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
                Write-Host "Updated LastSuccessfulTime as $($LastSuccessfulTime) for LogType $($LogType)"                
                $mutex.ReleaseMutex();

            #if ($mutex.WaitOne(2000)) {                
            #} else {
            #    Write-Host "Could not aquire the Mutex for Updated to Checkpoint File with $($LastSuccessfulTime) for LogType $($LogType)"
            #}       
        }
        catch {
            Write-Host "Error while updating the checkpointfile. Message: $($Error[0].Exception.Message)"
        }
    }

    function GetLogs ($Uri, $ApiKey, $StartTime, $EndTime, $LogType, $Page, $Skip) {
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
    function GetStartTime($CheckpointFile, $LogType, $TimeInterval) {
        
        $loggingOptions = $env:logTypes
        $apitypes = @($loggingOptions.split(",").Trim())
    
        $firstEndTimeRecord = (Get-Date -Date ((Get-Date).DateTime) -UFormat %s)
        $firstStartTimeRecord = $firstEndTimeRecord - $TimeInterval
        if ([System.IO.File]::Exists($CheckpointFile) -eq $false) {
            $CheckpointLog = @{}
            foreach ($apiType in $apitypes) {
                $CheckpointLog.Add($apiType, $firstStartTimeRecord.ToString() + "|" + 0)
            }
            $mutex = New-Object System.Threading.Mutex($false, 'NetSkopeCsvConnection')
            $mutex.WaitOne() > $null;
            $CheckpointLog.GetEnumerator() | Select-Object -Property Key, Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
            $mutex.ReleaseMutex()
        }
        else {
            $GetLastRecordTime = Import-Csv -Path $CheckpointFile
            if($null -eq $GetLastRecordTime)
            {
                $firstEndTimeRecord = (Get-Date -Date ((Get-Date).DateTime) -UFormat %s)
                $firstStartTimeRecord = $firstEndTimeRecord - $TimeInterval
                $CheckpointLog = @{}
                foreach ($apiType in $apitypes) {
                    $CheckpointLog.Add($apiType, $firstStartTimeRecord.ToString() + "|" + 0)
                }
                $mutex = New-Object System.Threading.Mutex($false, 'NetSkopeCsvConnection')
                $mutex.WaitOne() > $null;
                $CheckpointLog.GetEnumerator() | Select-Object -Property Key, Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
                $mutex.ReleaseMutex()
            }
            else
            {
                $LastRecordObject = $GetLastRecordTime | ForEach-Object{
                    if($_.Key -eq $LogType){
                        $_.Value
                    }
                }
                if ($null -ne $LastRecordObject) { 
                    return $LastRecordObject 
                } else {
                    $firstEndTimeRecord = (Get-Date -Date ((Get-Date).DateTime) -UFormat %s)
                    $firstStartTimeRecord = $firstEndTimeRecord - $TimeInterval
                    $CheckpointLog = @{}
                    $CheckpointLog.Add($LogType, $firstStartTimeRecord.ToString() + "|" + 0)
                    $mutex = New-Object System.Threading.Mutex($false, 'NetSkopeCsvConnection')
                    $mutex.WaitOne() > $null;
                    $CheckpointLog.GetEnumerator() | Select-Object -Property Key, Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
                    $mutex.ReleaseMutex()
                }
            }
        }
        return $firstStartTimeRecord.ToString() + "|" + 0
    }

    # Function to build the authorization signature to post to Log Analytics
function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource) {
    $xHeaders = "x-ms-date:" + $date;
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource;
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash);
    $keyBytes = [Convert]::FromBase64String($sharedKey);
    $sha256 = New-Object System.Security.Cryptography.HMACSHA256;
    $sha256.Key = $keyBytes;
    $calculatedHash = $sha256.ComputeHash($bytesToHash);
    $encodedHash = [Convert]::ToBase64String($calculatedHash);
    $authorization = 'SharedKey {0}:{1}' -f $customerId, $encodedHash;
    return $authorization;
}

# Function to POST the data payload to a Log Analytics workspace
function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType) {
    $TimeStampField = "DateValue"
    $method = "POST";
    $contentType = "application/json";
    $customerId = $customerId
    $resource = "/api/logs";
    $rfc1123date = [DateTime]::UtcNow.ToString("r");
    $contentLength = $body.Length;
    $signature = Build-Signature -customerId $customerId -sharedKey $sharedKey -date $rfc1123date -contentLength $contentLength -method $method -contentType $contentType -resource $resource;
    if ([string]::IsNullOrEmpty($logAnalyticsUri)) {
        $logAnalyticsUri = "https://" + $customerId + ".ods.opinsights.azure.com"
    }
    # Returning if the Log Analytics Uri is in incorrect format.
    # Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
    if ($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$') {
        throw "Netskope: Invalid Log Analytics Uri."
    }
    $logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"

    $headers = @{
        "Authorization"        = $signature;
        "Log-Type"             = $logType;
        "x-ms-date"            = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    };
    $response = Invoke-WebRequest -Body $body -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -UseBasicParsing
    return $response.StatusCode
}

# Function to POST the data payload to a Log Analytics workspace
function SplitDataAndProcess($customerId, $sharedKey, $payload, $logType) {
    $tempdata = @()
    $tempdataLength = 0
    $tempDataSize = 0
    $StartTime = (Get-Date).ToUniversalTime()
    try {
        if ((($payload |  Convertto-json -depth 3).Length) -gt 25MB) {
            Write-Host "Upload is over 25MB, needs to be split"
            foreach ($record in $payload) {
                $tempdata += $record
                $tempdataLength = $tempdata.Count
                $tempDataSize += ($record  | ConvertTo-Json).Length
                if ($tempDataSize -gt 25MB) {
                    write-Host "Sending data to log analytics when data size = $TempDataSize greater than 25mb post chuncking the data and length of events = $tempdataLength"
                    $responseCode = Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes(($tempdata | ConvertTo-Json))) -logType $logType
                    Write-Host "Post-LogAnalyticsData response code is $($responseCode) for LogType : $($logType)"
                    $tempdata = $null
                    $tempdata = @()
                    $tempDataSize = 0
                    $tempdataLength = 0
                }
            }
            Write-Host "Sending left over data = $Tempdatasize after all the chuncking of done is completed. Now datasize will be < 25mb and length of events = $tempdataLength"
            $responseCode = Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes(($tempdata | ConvertTo-Json))) -logType $logType
            $elapsedTime = (Get-Date).ToUniversalTime() - $StartTime
        }
        $totalTime = "{0:HH:mm:ss}" -f ([datetime]$elapsedTime.Ticks)
        Write-Host "Total Time taken to Split and Process this data = $totalTime"
        return $responseCode
    }
    catch {
        Write-Host "Error, error message: $($Error[0].Exception.Message)"
    }
}   
    GetNetSkopeAPILogs -logtype $logtype
}


# Main Function to call the API and Post the response to the Log Analytics API
function Netskope () {
    Write-Host "PS Version : $($PSVersionTable.PSVersion)"
    $Time = [System.Diagnostics.Stopwatch]::StartNew()
    $loggingOptions = $env:logTypes
    #"page,alert"
    $apitypes = @($loggingOptions.split(",").Trim())
    # foreach($iapiType in $apitypes)
    # {
    #     CallNetskope($iapiType)
    # }

    # Get the function's definition *as a string*
    $funcDef = $function:CallNetskope.ToString()
    $job = $apitypes | ForEach-Object -Parallel {
        # Define the function inside this thread...
        $function:CallNetskope = $using:funcDef
        CallNetskope($_)
        #Start-Sleep 1
    } -ThrottleLimit 50 -AsJob
    $job | Receive-Job -Wait
    $CurrentTime = $Time.Elapsed
    write-host $([string]::Format("`rTotal Time Taken to execute: {0:d2}:{1:d2}:{2:d2}",
                                  $CurrentTime.hours,
                                  $CurrentTime.minutes,
                                  $CurrentTime.seconds))
}

# Execute the Function to pull Netskope alerts and events and post to a Log Analytics workspace

Netskope

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"