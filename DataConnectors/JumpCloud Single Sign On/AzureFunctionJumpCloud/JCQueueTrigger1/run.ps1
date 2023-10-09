<#  
    Title:          JumpCloud Data Connector
    Language:       PowerShell
    Version:        1.0.1
    Author(s):      Microsoft - Chris Abberley
    Last Modified:  2020-08-03
    Comment:        First Release

    DESCRIPTION
    This Function App calls the JumpCloud Directory Insights API (https://jumpcloud-insights.api-docs.io/1.0/api-overview/directory-insights) to pull the JumpCloud logs. The response from the JumpCloud API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post the JumpCloud logs to the JumpCloud_CL table in the Log Analytics workspace.
#>

# Input bindings are passed in via param block.
param([string] $QueueItem, $TriggerMetadata)

# Write out the queue message and insertion time to the information log.
Write-Output "JumpCloud: Queue trigger for work item: $QueueItem, Queue item insertion time: $($TriggerMetadata.InsertionTime)"

import-module AzTable

# Retrieve Environment Variables and prep other Variables for the JumpCloud API request
$JCService = $QueueItem                         #Which eventlog set to rerieve from JumpCloud
$JCapiToken = $env:JumpCloudApiToken            #JumpCloud API
$JCuri = $env:JumpCloudUri                      #Standard JumpCloud URI
#$JCStartTime = $env:JumpCloudStartTime          #Initial Start time to collect logs
$AzureWebJobsStorage =$env:AzureWebJobsStorage  #Storage Account to use for table to maintain state for log queries between executions
$customerId = $env:workspaceId                  #Log Analytics Details
$sharedKey =  $env:workspaceKey                 #Log Analytics Details
$JCTablename = $env:AzureSentinelTable          #"JumpCloudQTest" #LogAnalytics Tablename which will have '_CL' added to it by LogAnalytics
$TimeStampField = "timestamp"                   #define JumpCloud Timestamp field
$JCSearchAfter = ""
$totalrecordcount =0

#fix date format
$DateFix = Get-Date
$JCStartTime = $DateFix.ToString('yyyy-MM-ddT00:00:00Z')
# using Azure Table on Functions Azure Storage to maintain state between runs
# Retrieve JumpCloud last retrieved record and Date-time or if first run create table
$JCstorage =  New-AzStorageContext -ConnectionString $AzureWebJobsStorage
$StorageTable = Get-AzStorageTable -Name $JCTablename -Context $JCStorage -ErrorAction Ignore
if($null -eq $storageTable.Name){  
    $result = New-AzStorageTable -Name $JCTablename -Context $JCstorage
    $JCTable = (Get-AzStorageTable -Name $JCTablename -Context $JCstorage.Context).cloudTable
    $result = Add-AzTableRow -table $JCTable -PartitionKey $JCapiToken -RowKey $JCService -property @{'SearchAfter' = "'"+$JCSearchAfter+"'";"StartTime"=$JCStartTime} -UpdateExisting
}
Else {
    $JCTable = (Get-AzStorageTable -Name $JCTablename -Context $JCstorage.Context).cloudTable
}
$row = Get-azTableRow -table $JCTable -partitionKey $JCapiToken -RowKey $JCService -ErrorAction Ignore
if($null -eq $row.StartTime){
    $result = Add-AzTableRow -table $JCTable -PartitionKey $JCapiToken -RowKey $JCService -property @{'SearchAfter' = "'"+$JCSearchAfter+"'";"StartTime"=$JCStartTime} -UpdateExisting
    $row = Get-azTableRow -table $JCTable -partitionKey $JCapiToken -RowKey $JCService -ErrorAction Ignore
}
$JCSearchAfter = $row.SearchAfter -replace "'",""
$JCStartTime =  $row.StartTime
if($null -eq $JCStartTime){$JCStartTime = $env:JumpCloudStartTime }

do {
    #JumpCloud API limits 1000 records in return set, it notifies via Headers if there is more to ask for loop until we have less records than limit
    #get first result set from API
    $headers = $null
    $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $headers.Add("Content-Type", "application/json")
    $headers.Add("x-api-key", "$JCapiToken")
    #create $body for request
    $body = '{"service": ["'+ $JCService + '"], ' 
    if ('' -ne $JCSearchAfter){ 
        $body = $body + ' "search_after": '+ $JCSearchAfter + ', '
    }
    $body = $body + '"start_time": "' + $JCStartTime +'"}'
    #send request to JumpCloud API for latest event entries
    $response = Invoke-WebRequest -uri "$JCuri"  -Method 'POST' -Headers $headers -Body $body
    $JCResultCount = 0
    $JCResultCount = [int]::parse($response.Headers["X-Result-Count"])
    $JCSearchAfter = $response.Headers["X-Search_after"]
    $totalrecordcount = $totalrecordcount + $JCResultCount
    #validate we have records and send them to Log Analytics if we do'
    if ($JCResultCount -gt 0) {
        $JCLimit = [int]::parse($response.Headers["X-Limit"])
        #$events = $response.Content | ConvertFrom-json
        #$LastRecordTimestamp = $events.timestamp[($events.count-1)].ToString
        Function New-BuildSignature (
            $customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource )
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
            return $authorization
        }
        # create and post the events to Log Analytics
            $method = "POST"
            $contentType = "application/json"
            $resource = "/api/logs"
            $rfc1123date = [DateTime]::UtcNow.ToString("r")
            $body = ([System.Text.Encoding]::UTF8.GetBytes($response))
            $contentLength = $body.Length
            $signature = New-BuildSignature `
                -customerId $customerId `
                -sharedKey $sharedKey `
                -date $rfc1123date `
                -contentLength $contentLength `
                -method $method `
                -contentType $contentType `
                -resource $resource
            $uri = "https://" + $customerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
            $headers1 = @{
                "Authorization" = $signature;
                "Log-Type" = $JCTablename;
                "x-ms-date" = $rfc1123date;
                "time-generated-field" = $TimeStampField;
            }
            $result = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers1 -Body $body -UseBasicParsing
    }
    else{
        Write-Output "JumpCloud: No new $JCService JumpCloud logs are avaliable as at $currentUTCtime"
        break
    }
    write-output " Limit: $JCLimit; ResultCount: $JCResultCount; Totalsofar: $totalrecordcount"
} until($JCResultCount -lt $JCLimit)

#store details in function storage table to retrieve next time function runs 
if($response.Headers.ContainsKey("X-Search_after")){
    if($response.Headers["X-Search_after"] -ne ''){
        #if($LastRecordTimestamp -eq ''){
            #$LastRecordTimestamp = [System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId($(([datetime]::parseexact(($response.headers.date),"ddd, dd MMM yyyy HH:mm:ss Z",$null))), [System.TimeZoneInfo]::Local.Id, 'Greenwich Standard Time').Tostring('yyyy-MM-ddTHH:mm:ssZ')
        #}
        $jbody = ConvertFrom-json $response.Content
        $LastRecordTimestamp= $jbody.timestamp[($jbody.count - 1)]
        $LastRecordTimestamp = $LastRecordTimeStamp.ToString('yyyy-MM-ddThh:mm:ssZ')
        $result = Add-AzTableRow -table $JCTable -PartitionKey $JCapiToken -RowKey $JCService -property @{"SearchAfter" = ("'"+$response.Headers["X-Search_after"]+"'");"StartTime"=$LastrecordTimestamp} -UpdateExisting
    }
}
# Write an information log with the current time.
Write-Output "JumpCloud: function ran using, Event Filter: $JCService, started: $currentUTCtime, Completed:"(Get-Date).ToUniversalTime()", Processed: $totalrecordcount records"
