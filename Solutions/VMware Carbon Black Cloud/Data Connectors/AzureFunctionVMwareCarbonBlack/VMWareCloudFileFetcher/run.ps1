<#
    Title:          VMware Carbon Black Cloud Data Connector
    Language:       PowerShell
    Version:        1.0
    Author:         Microsoft
    Last Modified:  5/19/2020
    Comment:        Inital Release

    DESCRIPTION
    This Function App calls the VMware Carbon Black Cloud REST API (https://developer.carbonblack.com/reference/carbon-black-cloud/cb-defense/latest/rest-api/) to pull the Carbon Black
    Audit, Notification and Event logs. The response from the CarbonBlack API is recieved in JSON format. This function will build the signature and authorization header
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post each log type to their individual tables in Log Analytics, for example,
    CarbonBlackAuditLogs_CL, CarbonBlackNotifications_CL and CarbonBlackEvents_CL.
#>
# Input bindings are passed in via param block.
param($Timer)

#Requires -Modules @{ModuleName='AWS.Tools.Common';ModuleVersion='4.1.14'}
#Requires -Modules @{ModuleName='AWS.Tools.S3';ModuleVersion='4.1.14'}

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()
$logAnalyticsUri = $env:logAnalyticsUri
##TODO: need to move params and validations
[int]$maxMainQueuemessages=150
[int]$maxdurationminutes=10

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}
$script_start_time=([System.DateTime]::UtcNow)


# The function will call the Carbon Black API and retrieve the Audit, Event, and Notifications Logs
function CarbonBlackAPI()
{
    $workspaceId = $env:workspaceId
    $workspaceSharedKey = $env:workspaceKey
    $hostName = $env:uri
    $apiSecretKey = $env:apiKey
    $logType = $env:CarbonBlackLogTypes
    $apiId = $env:apiId
    $SIEMapiKey = $env:SIEMapiKey
    $SIEMapiId = $env:SIEMapiId
    $time = $env:timeInterval
    $AuditLogTable = "CarbonBlackAuditLogs"
    $EventLogTable = "CarbonBlackEvents"
    $NotificationTable  = "CarbonBlackNotifications"
    $OrgKey = $env:CarbonBlackOrgKey
    $s3BucketName = $env:s3BucketName
    $EventprefixFolder = $env:EventPrefixFolderName
    $AlertprefixFolder = $env:AlertPrefixFolderName
    $AWSAccessKeyId = $env:AWSAccessKeyId
    $AWSSecretAccessKey = $env:AWSSecretAccessKey
    $queueName=$env:queueName
    $backlogQueue=$env:backlogQueue
    $carbonBlackStorage=$env:AzureWebJobsStorage

    $startTime = [System.DateTime]::UtcNow.AddMinutes(-$($time))
    $now = [System.DateTime]::UtcNow
 

    # Remove if addition slash or space added in hostName
    $hostName = $hostName.Trim() -replace "[.*/]$",""

    if ([string]::IsNullOrEmpty($logAnalyticsUri))
    {
        $logAnalyticsUri = "https://" + $workspaceId + ".ods.opinsights.azure.com"
    }

    # Returning if the Log Analytics Uri is in incorrect format.
    # Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
    if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
    {
        throw "VMware Carbon Black: Invalid Log Analytics Uri."
    }

    $authHeaders = @{
        "X-Auth-Token" = "$($apiSecretKey)/$($apiId)"
    }

    #Converting LogType to array
    if([string]::IsNullOrWhiteSpace($logType))
    {
        if ($SIEMapiKey -eq '<Optional>' -or  $SIEMapiId -eq '<Optional>'  -or [string]::IsNullOrWhitespace($SIEMapiKey) -or  [string]::IsNullOrWhitespace($SIEMapiId))
        {
            $LogTypeArr = @("event","audit")
        }
        else{
            $LogTypeArr = @("event","audit","alertSIEMAPI")
        }
    }else {
        if($logType -like "``[*``]")
        {
            $logType = $logType.Substring(1,$logType.Length-2)
        }
        $logType = $logType -replace """",""
        $LogTypeArr = $logType -split ','
    }
    

    if(-not([string]::IsNullOrWhiteSpace($apiId)) -and -not([string]::IsNullOrWhiteSpace($apiSecretKey)) -and -not([string]::IsNullOrWhiteSpace($hostName)))
    {
        if($LogTypeArr -contains "audit")
        {
            $auditLogsResult = Invoke-RestMethod -Headers $authHeaders -Uri ([System.Uri]::new("$($hostName)/integrationServices/v3/auditlogs"))

            if ($auditLogsResult.success -eq $true)
            {
                $AuditLogsJSON = $auditLogsResult.notifications | ConvertTo-Json -Depth 5
                if (-not([string]::IsNullOrWhiteSpace($AuditLogsJSON)))
                {
                    $responseObj = (ConvertFrom-Json $AuditLogsJSON)
                    $status = Post-LogAnalyticsData -customerId $workspaceId -sharedKey $workspaceSharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($AuditLogsJSON)) -logType $AuditLogTable;
                    Write-Host("$($responseObj.count) new Carbon Black Audit Events as of $([DateTime]::UtcNow). Pushed data to Azure sentinel Status code:$($status)")
                }
                else
                {
                    Write-Host "No new Carbon Black Audit Events as of $([DateTime]::UtcNow)"
                }
            }
            else
            {
                Write-Host "AuditLogsResult API status failed , Please check."
            }
        }
        else
        {
            Write-Warning "'Audit' was not selected as a LogType, therefore audit logs will not be ingested to the workspace."
        }
    }
    else
    {
        Write-Warning "API credentials were not defined, therefore audit logs will not be ingested to workspace."
    }

    if(-not([string]::IsNullOrWhiteSpace($s3BucketName)) -and -not([string]::IsNullOrWhiteSpace($AWSAccessKeyId)) -and -not([string]::IsNullOrWhiteSpace($AWSSecretAccessKey)) -and -not([string]::IsNullOrWhiteSpace($OrgKey)))
    {
        if($LogTypeArr -contains "event")
        {
            GetBucketFiles($EventprefixFolder)
           
            
        }
        else{
            Write-Warning "'Event' was not selected as a LogType, therefore event logs will not be ingested to the workspace."
        }
    }
    else
    {
        Write-Warning "S3Bucket credentials were not defined, therefore event logs will not be ingested to workspace."
    }


    if($LogTypeArr -contains "alertSIEMAPI" -or $LogTypeArr -contains "alertAWSS3")
    {
        if($SIEMapiKey -eq '<Optional>' -or  $SIEMapiId -eq '<Optional>'  -or [string]::IsNullOrWhitespace($SIEMapiKey) -or  [string]::IsNullOrWhitespace($SIEMapiId))
        {
            if(-not([string]::IsNullOrWhiteSpace($s3BucketName)) -and -not([string]::IsNullOrWhiteSpace($AWSAccessKeyId)) -and -not([string]::IsNullOrWhiteSpace($AWSSecretAccessKey)) -and -not([string]::IsNullOrWhiteSpace($OrgKey)))
            {
                GetBucketFiles($AlertprefixFolder)
                
            }
        }
        elseif(-not([string]::IsNullOrWhiteSpace($SIEMapiKey)) -and -not([string]::IsNullOrWhiteSpace($SIEMapiId)))
        {
            $authHeaders = @{"X-Auth-Token" = "$($SIEMapiKey)/$($SIEMapiId)"}
            $notifications = Invoke-RestMethod -Headers $authHeaders -Uri ([System.Uri]::new("$($hostName)/integrationServices/v3/notification"))
            if ($notifications.success -eq $true)
            {
                $NotifLogJson = $notifications.notifications | ConvertTo-Json -Depth 5
                if (-not([string]::IsNullOrWhiteSpace($NotifLogJson)))
                {
                    $responseObj = (ConvertFrom-Json $NotifLogJson)
                    $status = Post-LogAnalyticsData -customerId $workspaceId -sharedKey $workspaceSharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($NotifLogJson)) -logType $NotificationTable;
                    Write-Host("$($responseObj.count) new Carbon Black Notifications as of $([DateTime]::UtcNow). Pushed data to Azure sentinel Status code:$($status)")
                }
                else
                {
                        Write-Host "No new Carbon Black Notifications as of $([DateTime]::UtcNow)"
                }
            }
            else
            {
                Write-Host "Notifications API status failed , Please check."
            }
        }
        else
        {
            Write-Warning "No SIEM API ID and/or Key or S3Bucket value was defined, therefore alert logs will not to ingested to workspace."
        }
    }
    else{
        Write-Warning "'Alert' was not selected as a LogType, therefore alert logs will not be ingested to the workspace."
    } 
}

# Create the function to create the authorization signature
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

# Create the function to create and post the request
function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType)
{
    $TimeStampField = "eventTime"
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


<#
.SYNOPSIS
This is used to convert object to json

.DESCRIPTION
Long description

.PARAMETER s3BucketName
Parameter description

.PARAMETER prefixFolder
Parameter description

.PARAMETER tableName
Parameter description

.PARAMETER logtype
Parameter description

.EXAMPLE
An example

.NOTES
General notes
#>
function  Convert-ToJSON($s3BucketName,$keyPrefix,$tableName,$logtype)
{

    $bucketObject = [PSCustomObject]@{
        s3BucketName = $s3BucketName
        keyPrefix = $keyPrefix
        tableName = $tableName
        logType=$logtype
        msgId=New-Guid
    }
return ConvertTo-Json -InputObject $bucketObject
}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function GetStorageContext()
{
if(-not([string]::IsNullOrWhiteSpace($carbonBlackStorage)))
{
 $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
 return $ctx
}

}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function GetQueueCount()
{
    $context=GetStorageContext
    $messageCount = (Get-AzStorageQueue -Context $context | where-object{$_.name -eq $queueName}).ApproximateMessageCount
    return $messageCount
}
<#
.SYNOPSIS
##

.DESCRIPTION
Long description

.PARAMETER percentage
Parameter description

.PARAMETER script_start_time
Parameter description

.EXAMPLE
An example

.NOTES
General notes
#>
function check_if_script_runs_too_long($percentage, $script_start_time)
{
 [int]$seconds=(60)
 [int]$duration = $(([System.DateTime]::UtcNow - $script_start_time).Seconds)
 [int]$temp=$maxdurationminutes * $seconds 
 [double]$maxduration= $temp * 0.8
 return $duration -gt $maxduration
}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function GetBucketFiles($prefixFolder)
{
    IF ($Null -ne $s3BucketName) {
        Set-AWSCredentials -AccessKey $AWSAccessKeyId -SecretKey $AWSSecretAccessKey
        while ($startTime -le $now) {
            $prefixFolder="carbon-black-events"
            $keyPrefix = "$prefixFolder/org_key=$OrgKey/year=$($startTime.Year)/month=$($startTime.Month)/day=$($startTime.Day)/hour=$($startTime.Hour)/minute=$($startTime.Minute)"
            #$keyPrefix="carbon-black-events/org_key=7DESJ9GN/year=2023/month=12/day=2/hour=23/minute=30"
            #$path=Get-ChildItem -Path $keyPrefix -Recurse
            $paths=@()
            foreach ($items in (Get-S3Object -BucketName $s3BucketName -keyPrefix $keyPrefix | Select-Object Key )) 
            { 
                $path = split-path $items.Key
                if($path.Contains("second="))
                {
                    $paths += $path   
                }
               
            }
            $paths = $paths | sort -Unique
            Write-Host $paths

        foreach($item in $paths)
        {
            
          $item=$item.Replace($OrgKey,"")
          if($prefixFolder -eq "carbon-black-events")
           {
            $json = Convert-ToJSON -s3BucketName $s3BucketName -keyPrefix $item -tableName $EventLogTable -logtype "event"
           }
           else {
            $json = Convert-ToJSON -s3BucketName $s3BucketName -keyPrefix $item -tableName $NotificationTable -logtype "alert"
           }
            if((GetQueueCount) -gt $maxMainQueuemessages)
            {
                CreateQueuePostMessageToQueue -message $json -queueN $backlogQueue
            }
            else {

                CreateQueuePostMessageToQueue -message $json -queueN $queueName
            }
            if((check_if_script_runs_too_long -percentage 0.8 -script_start_time $script_start_time))
            {
                break
            }

        }
            $startTime = $startTime.AddMinutes(1)
       
        }

    }
}
<#
.SYNOPSIS
This method used for posting to queue
.DESCRIPTION
Long description

.PARAMETER message
$message from convert json from object

.EXAMPLE
An example

.NOTES
General methods
#>
function CreateQueuePostMessageToQueue($message,$queueN)
{
   
try
{
    if(-not([string]::IsNullOrWhiteSpace($message)) -and -not([string]::IsNullOrWhiteSpace($carbonBlackStorage)) -and -not([string]::IsNullOrWhiteSpace($queueName)))
    {
        $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
        if ($null -ne $ctx)
        {
            
            $queue = Get-AzStorageQueue –Name $queueN –Context $ctx
            if(-not $queue)
            {
               #Creating the queue
               $queue = New-AzStorageQueue –Name $queueN -Context $ctx  
            }
            else {
                
                #Queue already present
            }         
        }
        else
        {
          Write-Host "Storage context not available"
        }
        if ($null -ne $queue) 
        {  
           
           $queueMessage = [Microsoft.Azure.Storage.Queue.CloudQueueMessage]::new(($message))
           
           $status=$queue.CloudQueue.AddMessageAsync($queueMessage).GetAwaiter().GetResult()
        }
        else
        {
          Write-Host "unable to get queue details"
        }
        if($null -ne $status)
        {
          Write-Host "Queue Message added Successfully"
        }
        else 
        {  
           Write-Host "Queue Message not added Successfully"
        }
    }
    else
    {
        Write-Host "Input parameters are empty"
    }
}
catch {
    Write-Host $_
}

}



# Execute the Function to Pull CarbonBlack data and Post to the Log Analytics Workspace
CarbonBlackAPI

#This method posts the message to queue

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"