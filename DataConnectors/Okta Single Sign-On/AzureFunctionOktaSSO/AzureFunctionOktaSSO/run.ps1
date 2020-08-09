<#  
    Title:          Okta Data Connector
    Language:       PowerShell
    Version:        2.0
    Author(s):      Microsoft - Chris Abberley
    Last Modified:  7/22/2020
    Comment:        Fixes for the following issues with Version 1
                    -Potential Data loss due to code not processing linked pages
                    -Potential Data loss due to variations in execution of Triggers
                    -Corrected Timestamp field for Okta logs which use "published"
                    Clean up of code
                    -removed timer interval which is no longer required
                    -standardised code lode logging information messages


    DESCRIPTION
    This Function App calls the Okta System Log API (https://developer.okta.com/docs/reference/api/system-log/) to pull the Okta System logs. The response from the Okta API is recieved in JSON format. 
    This function will build the signature and authorization header needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. 
    The Function App will post the Okta logs to the Okta_CL table in the Log Analytics workspace.

    NOTES:
    Suggested timing trigger of no less than 10 minutes. Be aware that Azure Functions have a runtime execution time limit of 5 mins, at which point it will terminate the function.
    If this occurs you may get some duplicate records in your Azure Logs as it will not commit the last datetime until the records are written to Azure logs.
#>

# Input bindings are passed in via param block.
param($Timer)
# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()
# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "OKTASSO: Azure Function triggered at: $currentUTCtime - timer is running late!"
}
else{
    Write-Host "OKTASSO: Azure Function triggered at: $currentUTCtime - timer is ontime!"

}
#Azure Function State management between Executions
$AzureWebJobsStorage =$env:AzureWebJobsStorage  #Storage Account to use for table to maintain state for log queries between executions
$Tablename = "OKTA"                             #Tablename which will hold datetime record between executions
$TotalRecordCount = 0
$responseDate = $null

# variables needed for the Okta API request
$apiToken = $env:apiToken
$uri = $env:uri
$StartDate = [System.DateTime]::UtcNow.ToString("yyyy-MM-ddT00:00:00.000Z") # set default fallback start time to 0:00 UTC today

# Define the Log Analytics Workspace ID and Key and Custom Table Name
$customerId = $env:workspaceId
$sharedKey =  $env:workspaceKey
$LogType = "Okta"
$TimeStampField = "published"

# Retrieve Timestamp from last records received from Okta 
# Check if Tabale has already been created and if not create it to maintain state between executions of Function
$storage =  New-AzStorageContext -ConnectionString $AzureWebJobsStorage
$StorageTable = Get-AzStorageTable -Name $Tablename -Context $Storage -ErrorAction Ignore
if($null -eq $StorageTable.Name){  
    $result = New-AzStorageTable -Name $Tablename -Context $storage
    $Table = (Get-AzStorageTable -Name $Tablename -Context $storage.Context).cloudTable
    $result = Add-AzTableRow -table $Table -PartitionKey "part1" -RowKey $apiToken -property @{"StartTime"=$StartDate} -UpdateExisting
}
Else {
    $Table = (Get-AzStorageTable -Name $Tablename -Context $storage.Context).cloudTable
}
# retrieve the row
$row = Get-azTableRow -table $Table -partitionKey "part1" -RowKey $apiToken -ErrorAction Ignore
if($null -eq $row.StartTime){
    $result = Add-AzTableRow -table $Table -PartitionKey "part1" -RowKey $apiToken -property @{"StartTime"=$StartDate} -UpdateExisting
    $row = Get-azTableRow -table $Table -partitionKey "part1" -RowKey $apiToken -ErrorAction Ignore
}

#set starting uri for requests from Okta
$StartDate =  $row.StartTime
$after=(Get-Date -Date $StartDate -UFormat %s)+$startdate.Substring(20,3)+'_1'
$uri = "$uri$($StartDate)&limit=1000&after=$after"

#Setup uri Headers for requests to OKta
$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Content-Type", "application/json")
$headers.Add("User-Agent", "AzureFunction")
$headers.Add("Authorization", "SSWS $apiToken")

# begin looping through responses from OKTA until we get all available records
$exitDoUntil = $false
do {
    $body = $null
    if($uri.length -gt 0){
        $response = Invoke-WebRequest -uri $uri  -Method 'GET' -Headers $headers -Body $body
    }
    if($response.headers.Keys -contains "link"){
        $uri = $response.headers.link.split(",;")
        $uri = $uri.split(";")
        $uri = $uri[2] -replace "<|>", ""
    }
    ELSE{
        $exitDoUntil = $true
    }
    $responseCount = (ConvertFrom-Json $response.content).count
    if($ResponseCount -gt 0) {
        #breakdown into steps as Powershell in Azure Functions doesn't always like multistep combinations
        $responseDate = ConvertFrom-Json $response.content 
        $responseDate = $responseDate.published.ticks | Sort-Object -Descending
        $responseDate = $responseDate[0]
        $responseDate = Get-Date -Date $ResponseDate  
        $responsedate = $responsedate.tostring('yyyy-MM-ddTHH:mm:ss.fffZ')
 
        $TotalRecordCount= $TotalRecordCount + $responseCount

        Function new-BuildSignature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
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
        $method="POST"
        $contentType = "application/json"
        $resource = "/api/logs"
        $rfc1123date = [DateTime]::UtcNow.ToString("r")
        $body = ([System.Text.Encoding]::UTF8.GetBytes($response))
        $contentLength = $body.Length
        $signature = new-BuildSignature `
            -customerId $customerId `
            -sharedKey $sharedKey `
            -date $rfc1123date `
            -contentLength $contentLength `
            -method $method `
            -contentType $contentType `
            -resource $resource
        $LAuri = "https://" + $customerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
        $LAheaders = @{
            "Authorization" = $signature;
            "Log-Type" = $logType;
            "x-ms-date" = $rfc1123date;
            "time-generated-field" = $TimeStampField;
        }
        $result = Invoke-WebRequest -Uri $LAuri -Method $method -ContentType $contentType -Headers $LAheaders -Body $body -UseBasicParsing
        #update State table for next time we execute function
        #store details in function storage table to retrieve next time function runs 
        if($responseDate.length -gt 2){
            $result = Add-AzTableRow -table $Table -PartitionKey "part1" -RowKey $apiToken -property @{"StartTime"=$responseDate} -UpdateExisting
        }
    }
    else{
        $exitDoUntil = $true
    }
    #check on time running, Azure Function default timeout is 5 minutes, if we are getting close exit function cleanly now and get more records next execution
    IF((new-timespan -Start $currentUTCtime -end ((Get-Date).ToUniversalTime())).TotalSeconds -gt 260){$exitDoUntil = $true} 
}until($exitDoUntil) 

if($TotalRecordCount -lt 1){
    Write-Output "OKTASSO: No new Okta logs since $StartDate are available as of $currentUTCtime"
}
# Write an information log with the current time.
$finishtime = ((Get-Date).ToUniversalTime())
Write-Output "OktaSSO: Azure function completed, started: $currentUTCtime, Completed: $finishtime, Processed: $totalrecordcount records"
