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
[int]$maxMainQueuemessages=[int]$env:maxMainQueuemessages
[int]$maxdurationminutes=10


# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}
$script_start_time=([System.DateTime]::UtcNow)
<#
.SYNOPSIS
Short description

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function GenerateDate()
{
    
    $time= [int]$Env:timeInterval
    $startTime=getCheckpoint
    if($null -ne $startTime)
    {
       $startTime = Get-Date -Date $startTime
    }

    if($null -ne $startTime)
    {
        Write-Host "The last start time in file share is" $startTime
    }
    else {
        $startTime = [System.DateTime]::UtcNow.AddMinutes(-$($time))
    }

    $now = [System.DateTime]::UtcNow
    #$Duration = New-TimeSpan -Start $startTime -End $now()

    if($startTime -le $now)
    {
        [int]$noofmins = $($now-$startTime).TotalMinutes
    }
    else {
        Write-Host "Start time is greater than current time,Please check the start time and correct it."
    }
    if($noofmins -gt $time)
    {
        if($null -ne $startTime)
        {
          $now=$startTime.AddMinutes($time)
        }
        Write-Host "The no of mins b/w start and end time is greater than $time"
    }
    Write-Host "The now time is" $now

    return $startTime, $now
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
function getCheckpoint()
{
$azstoragestring = $Env:WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
$Context = New-AzStorageContext -ConnectionString $azstoragestring
if((Get-AzStorageContainer -Context $Context).Name -contains "lastlog"){
    #Set Container
    $Blob = Get-AzStorageBlob -Context $Context -Container (Get-AzStorageContainer -Name "lastlog" -Context $Context).Name -Blob "lastlog.log"
    $lastlogTime = $blob.ICloudBlob.DownloadText()
    $startTime = $lastlogTime | Get-Date -Format yyyy-MM-ddTHH:mm:ss
    return $startTime
}

}
function CarbonBlackS3Messages()
{
    $logType = $env:CarbonBlackLogTypes
    $apiId = $env:apiId
    $time = $env:timeInterval
    $EventLogTable = "CarbonBlackEvents"
    $NotificationTable  = "CarbonBlackNotifications"
    $OrgKey = $env:CarbonBlackOrgKey
    $s3BucketName = $env:s3BucketName
    $EventprefixFolder = $env:EventPrefixFolderName
    $AlertprefixFolder = $env:AlertPrefixFolderName
    $AWSAccessKeyId = $env:AWSAccessKeyId
    $AWSSecretAccessKey = $env:AWSSecretAccessKey

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
    ProcessMessagesToQueue
}

function ProcessMessagesToQueue()
{
    if(-not([string]::IsNullOrWhiteSpace($s3BucketName)) -and -not([string]::IsNullOrWhiteSpace($AWSAccessKeyId)) -and -not([string]::IsNullOrWhiteSpace($AWSSecretAccessKey)) -and -not([string]::IsNullOrWhiteSpace($OrgKey)))
    {
        if($LogTypeArr -contains "event")
        {
        
            $time=[System.DateTime]::UtcNow
            # get queue count ---> if less than < 200 call below fn, if no, wait for 10sec and check again queue count size
            GetBucketFiles($EventprefixFolder)
            Write-Host "Events are processsed in $(([System.DateTime]::UtcNow - $time).Seconds) Seconds"
        }
        else{
            Write-Warning "'Event' was not selected as a LogType, therefore event logs will not be ingested to the workspace."
        }
    }
    else {
        Write-Host "Input parameters are empty for event logs"
    }

    if($LogTypeArr -contains "alertSIEMAPI" -or $LogTypeArr -contains "alertAWSS3")
    {
        
            if(-not([string]::IsNullOrWhiteSpace($s3BucketName)) -and -not([string]::IsNullOrWhiteSpace($AWSAccessKeyId)) -and -not([string]::IsNullOrWhiteSpace($AWSSecretAccessKey)) -and -not([string]::IsNullOrWhiteSpace($OrgKey)))
            {
                $time=[System.DateTime]::UtcNow
                GetBucketFiles($AlertprefixFolder)
                Write-Host "Alerts are processsed in $(([System.DateTime]::UtcNow - $time).Seconds) Seconds"
            }
        
    }
    else {
        Write-Host "Input parameters are empty for alert logs"
    }

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
function CreateQueue($queueNameParameter)
{
   
try
{
    if(-not([string]::IsNullOrWhiteSpace($carbonBlackStorage)) -and -not([string]::IsNullOrWhiteSpace($queueNameParameter)))
    {
        $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
        if ($null -ne $ctx)
        {
            
            $queue = Get-AzStorageQueue –Name $queueNameParameter –Context $ctx
            if(-not $queue)
            {
               #Creating the queue
               $queue = New-AzStorageQueue –Name $queueNameParameter -Context $ctx  
            }
            else {
                
                #Queue already present
            }         
        }
        else
        {
          Write-Host "Storage context not available"
        }
    }
    else
    {
        Write-Host "Input parameters are empty"
    }
}
catch {
  Write-Error "Failed at CreateQueue with error message: $($_.Exception.Message)" -ErrorAction SilentlyContinue
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
function GetBucketFiles($prefixFolder)
{
    IF ($Null -ne $s3BucketName) {
        Set-AWSCredentials -AccessKey $AWSAccessKeyId -SecretKey $AWSSecretAccessKey
        $totalTime
        [int]$totalQueueCount=0
        $started=[System.DateTime]::UtcNow 
        $time=[int]$Env:timeInterval
        while ($startTime -le $now) {
            $keyPrefix = "$prefixFolder/org_key=$OrgKey/year=$($startTime.Year)/month=$($startTime.Month)/day=$($startTime.Day)/hour=$($startTime.Hour)/minute=$($startTime.Minute)"
            $paths=@()
            $msgs=@()
            foreach ($items in (Get-S3Object -BucketName $s3BucketName -KeyPrefix $keyPrefix) | Select-Object Key ) 
            {
                if($items.Key.Contains(".gz"))
                {
                    $path = split-path $items.Key -Parent
                    $keyValuePairs = $path -split '\\'
                $s3Dict = @{}
                $mainPath=$null
                foreach ($pair in $keyValuePairs) {
                    $key, $value = $pair -split '='
                    $s3Dict[$key] = $value
                    if($null -eq $value)
                    {
                        if([string]::IsNullOrWhiteSpace($mainPath))
                        {
                            $mainPath=$key
                        }
                        else {
                            <# Action when all if and elseif conditions are false #>
                            $mainPath=$mainPath+"/"+$key
                        }
                       
                    }
                }
                if(("$($mainPath)/org_key=$OrgKey/year=$($s3Dict["year"])/month=$($s3Dict["month"])/day=$($s3Dict["day"])/hour=$($s3Dict["hour"])/minute=$($s3Dict["minute"])") -eq $keyPrefix)
                {
                    $paths += $items.Key
                    if($items.Key.Contains($EventprefixFolder))
                    {
                        $json = Convert-ToJSON -s3BucketName $s3BucketName -keyPrefix $items.Key -tableName $EventLogTable -logtype "event"
                    }
                    if($items.Key.Contains($AlertprefixFolder))
                    {
                        $json = Convert-ToJSON -s3BucketName $s3BucketName -keyPrefix $items.Key -tableName $NotificationTable -logtype "alert"
                    }
                    $msgs+=$json
                }
                else {
                    Write-Host "Paths doesn't have gz files" $items.Key
                }  
                }
           }
        $paths = $paths | sort -Unique
        $totalQueueCount+=$msgs.Count
        $startQueue=[System.DateTime]::UtcNow 
        try {
            $queueCount = GetQueueCount
            Write-Host "Queue Count in main queue is $($queueCount)" 
            Push-OutputBinding -Name Msg -Value $msgs
            Write-Host "Total time to process messages to queue under 1 min for $prefixFolder in seconds $(([System.DateTime]::UtcNow-$startQueue).seconds)" 
        }
        catch {
            "Failed at Pushoutpubinding with error message: $($_.Exception.Message)"
        }
            $startTime = $startTime.AddMinutes(1)
            
    }
    Write-Host "Total Messages pushed to queue under $time mins for $prefixFolder : $totalQueueCount" 
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
function CreateQueuePostMessageToQueue($message,$queueNameParam,$i)
{
   
try
{
    if(-not([string]::IsNullOrWhiteSpace($message)) -and -not([string]::IsNullOrWhiteSpace($carbonBlackStorage)) -and -not([string]::IsNullOrWhiteSpace($queueNameParam)))
    {
        $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
        if ($null -ne $ctx)
        {
            
            $queue = Get-AzStorageQueue –Name $queueNameParam –Context $ctx
            if(-not $queue)
            {
               #Creating the queue
               $queue = New-AzStorageQueue –Name $queueNameParam -Context $ctx  
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
          Write-Host "unable to get queue details for" $message
        }
        if($null -ne $status)
        {
          $i=$i+1
          Write-Host "Message count posted to Queue" $queueNameParam "count="$i  
          Write-Host "Queue Message added Successfully" $message
        }
        else 
        {  
           Write-Host "Queue Message not added Successfully" $message 
        }
    }
    else
    {
        Write-Host "Input parameters are empty"
    }
}
catch {
    Write-Error "Failed at CreateQueuePostMessageToQueue with error message: $($_.Exception.Message)" -ErrorAction SilentlyContinue
}

}

$azstoragestring = $Env:WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
$queueName=$env:queueName
$maxMainQueuemessages=$env:maxMainQueuemessages
$carbonBlackStorage=$env:AzureWebJobsStorage
$Context = New-AzStorageContext -ConnectionString $azstoragestring
CreateQueue($queueName)
$startTime,$now=GenerateDate
$startTime
$now
#postCheckpoint
# Execute the Function to Pull CarbonBlack data and Post to the Log Analytics Workspace
$sleepTime = 15
Do
{
    
    $queueCount = GetQueueCount
    Write-Host "The queue count before do while is $queueCount"
    if($queueCount -lt $maxMainQueuemessages)
    {
        try {
            CarbonBlackS3Messages
            if((Get-AzStorageContainer -Context $Context).Name -contains "lastlog"){
                #Set Container
                $now | Get-Date -Format yyyy-MM-ddTHH:mm:ss | Out-File "$env:TEMP\lastlog.log"
                Set-AzStorageBlobContent -file "$env:TEMP\lastlog.log" -Container (Get-AzStorageContainer -Name "lastlog" -Context $Context).Name -Context $Context -Force
            }
            else {
            $blob=(Get-AzStorageContainer -Context $Context).Name -contains "lastlog"
            if(-not $blob)
            {
            $azStorageContainer = New-AzStorageContainer -Name "lastlog" -Context $Context
            $now | Get-Date -Format yyyy-MM-ddTHH:mm:ss | Out-File "$env:TEMP\lastlog.log"
            Set-AzStorageBlobContent -file "$env:TEMP\lastlog.log" -Container $azStorageContainer.name -Context $Context -Force
            }
            }
            Write-Host "The now time in file share is" $now
            break
        }
        catch {
            Write-Error "Failed at GetBucketFiles with error message: $($_.Exception.Message)" -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -s 15
    $sleepTime = $sleepTime + 15
}
while ($sleepTime -lt 168) {
}

#This method posts the message to queue
# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"