<#  
    Title:          DocuSign Security Events Data Connector
    Language:       PowerShell
    Version:        1.0
    Author:         Sreedhar Ande
    Last Modified:  1/13/2021
    Comment:        Inital Release

    DESCRIPTION
    This Function App calls the DocuSign Monitor REST API (https://{ORG}.docusign.net/api/v2.0/datasets/monitor/stream/) to pull the security events for your DocuSign account. 
    The response from the DocuSign Monitor REST API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API.
#>

# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"

# Main
if ($env:MSI_SECRET -and (Get-Module -ListAvailable Az.Accounts)){
    Connect-AzAccount -Identity
}


$AzureWebJobsStorage = $env:AzureWebJobsStorage
$DocuSignAccessToken = $env:DocuSignOAuthAccessToken
$workspaceId = $env:WorkspaceId
$workspaceKey = $env:WorkspaceKey
$storageAccountContainer = "docusign-monitor"
$CustomLogTable = $env:CustomLogTableName
$tempDir=$env:TMPDIR
#The AzureTenant variable is used to specify other cloud environments like Azure Gov(.us) etc.,
$AzureTenant = $env:AZURE_TENANT

$currentStartTime = (get-date).ToUniversalTime() | get-date  -Format yyyy-MM-ddTHH:mm:ss:ffffffZ

Function Write-OMSLogfile {
    <#
    .SYNOPSIS
    Inputs a hashtable, date and workspace type and writes it to a Log Analytics Workspace.
    .DESCRIPTION
    Given a  value pair hash table, this function will write the data to an OMS Log Analytics workspace.
    Certain variables, such as Customer ID and Shared Key are specific to the OMS workspace data is being written to.
    This function will not write to multiple OMS workspaces.  BuildSignature and post-analytics function from Microsoft documentation
    at https://docs.microsoft.com/azure/log-analytics/log-analytics-data-collector-api
    .PARAMETER DateTime
    date and time for the log.  DateTime value
    .PARAMETER Type
    Name of the logfile or Log Analytics "Type".  Log Analytics will append _CL at the end of custom logs  String Value
    .PARAMETER LogData
    A series of key, value pairs that will be written to the log.  Log file are unstructured but the key should be consistent
    withing each source.
    .INPUTS
    The parameters of data and time, type and logdata.  Logdata is converted to JSON to submit to Log Analytics.
    .OUTPUTS
    The Function will return the HTTP status code from the Post method.  Status code 200 indicates the request was received.
    .NOTES
    Version:        2.0
    Author:         Travis Roberts
    Creation Date:  7/9/2018
    Purpose/Change: Crating a stand alone function    
    #>
    [cmdletbinding()]
    Param(
        [Parameter(Mandatory = $true, Position = 0)]
        [datetime]$dateTime,
        [parameter(Mandatory = $true, Position = 1)]
        [string]$type,
        [Parameter(Mandatory = $true, Position = 2)]
        [psobject]$logdata,
        [Parameter(Mandatory = $true, Position = 3)]
        [string]$CustomerID,
        [Parameter(Mandatory = $true, Position = 4)]
        [string]$SharedKey
    )
    Write-Verbose -Message "DateTime: $dateTime"
    Write-Verbose -Message ('DateTimeKind:' + $dateTime.kind)
    Write-Verbose -Message "Type: $type"
    write-Verbose -Message "LogData: $logdata"   

    # Supporting Functions
    # Function to create the auth signature
    Function BuildSignature ($CustomerID, $SharedKey, $Date, $ContentLength, $Method, $ContentType, $Resource) {
        $xheaders = 'x-ms-date:' + $Date
        $stringToHash = $Method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $Resource
        $bytesToHash = [text.Encoding]::UTF8.GetBytes($stringToHash)
        $keyBytes = [Convert]::FromBase64String($SharedKey)
        $sha256 = New-Object System.Security.Cryptography.HMACSHA256
        $sha256.key = $keyBytes
        $calculateHash = $sha256.ComputeHash($bytesToHash)
        $encodeHash = [convert]::ToBase64String($calculateHash)
        $authorization = 'SharedKey {0}:{1}' -f $CustomerID, $encodeHash
        return $authorization
    }
    # Function to create and post the request
    Function PostLogAnalyticsData ($CustomerID, $SharedKey, $Body, $Type) {
        $method = "POST"
        $contentType = 'application/json'
        $resource = '/api/logs'
        $rfc1123date = ($dateTime).ToString('r')
        $ContentLength = $Body.Length
        $signature = BuildSignature `
            -customerId $CustomerID `
            -sharedKey $SharedKey `
            -date $rfc1123date `
            -contentLength $ContentLength `
            -method $method `
            -contentType $contentType `
            -resource $resource
        $uri = "https://" + $customerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
        $headers = @{
            "Authorization"        = $signature;
            "Log-Type"             = $type;
            "x-ms-date"            = $rfc1123date
            "time-generated-field" = $dateTime
        }
        $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers -Body $Body -UseBasicParsing
        Write-Verbose -message ('Post Function Return Code ' + $response.statuscode)
        return $response.statuscode
    }   

    # Check if time is UTC, Convert to UTC if not.
    # $dateTime = (Get-Date)
    if ($dateTime.kind.tostring() -ne 'Utc') {
        $dateTime = $dateTime.ToUniversalTime()
        Write-Verbose -Message $dateTime
    }
    #Build the JSON file
    $logMessage = ($logdata | ConvertTo-Json -Depth 20)
    
    #Submit the data
    $returnCode = PostLogAnalyticsData -CustomerID $CustomerID -SharedKey $SharedKey -Body $logMessage -Type $type
    Write-Verbose -Message "Post Statement Return Code $returnCode"
    return $returnCode
}

Function SendToLogA ($eventsData) {    	
	#Test Size; Log A limit is 30MB
    $tempdata = @()
    $tempDataSize = 0
    
    if ((($eventsData |  Convertto-json -depth 20).Length) -gt 25MB) {        
		Write-Host "Upload is over 25MB, needs to be split"									 
        foreach ($record in $eventsData) {            
            $tempdata += $record
            $tempDataSize += ($record | ConvertTo-Json -depth 20).Length
            if ($tempDataSize -gt 25MB) {
                $postLAStatus = Write-OMSLogfile -dateTime (Get-Date) -type $CustomLogTable -logdata $tempdata -CustomerID $workspaceId -SharedKey $workspaceKey
                write-Host "Sending data = $TempDataSize"
                $tempdata = $null
                $tempdata = @()
                $tempDataSize = 0
            }
        }
        Write-Host "Sending left over data = $Tempdatasize"
        $postLAStatus = Write-OMSLogfile -dateTime (Get-Date) -type $CustomLogTable -logdata $eventsData -CustomerID $workspaceId -SharedKey $workspaceKey
    }
    Else {          
        $postLAStatus = Write-OMSLogfile -dateTime (Get-Date) -type $CustomLogTable -logdata $eventsData -CustomerID $workspaceId -SharedKey $workspaceKey        
    }
	
	return $postLAStatus
}

$docuSignAPIHeaders = @{
    Authorization = "bearer $DocuSignAccessToken"
    'Content-Type' = "application/json"
}

#Get Orgs from ORGS.json in Az Storage
$storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage
$checkBlob = Get-AzStorageBlob -Blob ORGS.json -Container $storageAccountContainer -Context $storageAccountContext
if($null -ne $checkBlob){
    Get-AzStorageBlobContent -Blob ORGS.json -Container $storageAccountContainer -Context $storageAccountContext -Destination "$tempDir\orgs.json" -Force
    $docuSignOrgs = Get-Content "$tempDir\orgs.json" | ConvertFrom-Json
}
else{
    Write-Error "No ORGS.json file, exiting"
    exit
}

foreach($org in $docuSignOrgs){
    $orgName = $org.org
    Write-Host "Starting to process ORG: $orgName"
       
    #check for last run file
    $checkBlob = Get-AzStorageBlob -Blob "lastrun-Monitor.json" -Container $storageAccountContainer -Context $storageAccountContext
    if($null -ne $checkBlob){
        #Blob found get data
        Get-AzStorageBlobContent -Blob "lastrun-Monitor.json" -Container $storageAccountContainer -Context $storageAccountContext -Destination "$tempDir\lastrun-Monitor.json" -Force
        $lastRunMonitorContext = Get-Content "$tempDir\lastrun-Monitor.json" | ConvertFrom-Json
    }
    else {
        #no blob create the context
        $lastRun = $currentStartTime
        $lastRunMonitor = @"
{
"org":$orgName
"lastRun": "$lastRun",
"lastRunEndCursor": ""
}
"@
        $lastRunMonitor | Out-File "$tempDir\lastrun-Monitor.json"
        $lastRunMonitorContext = $lastRunMonitor | ConvertFrom-Json
    }

    $lastRunEndCursorContext = $lastRunMonitorContext | Where-Object {$_.org -eq $orgName}    
    if([string]::IsNullOrEmpty($lastRunEndCursorContext.lastRunEndCursor)){    
        $lastRunEndCursorValue=""        
    }
    else {
        $lastRunEndCursorValue = $lastRunEndCursorContext.lastRunEndCursor        
    }

    $complete=$false    
    $iterations=0
    DO{
        $iterations++	
        try{
            $docuSignMonitorAPI=$null
            $monitorApiResponse = $null
            $docuSignMonitorAPI = "https://${orgName}.docusign.net/api/v2.0/datasets/monitor/stream?cursor=${lastRunEndCursorValue}&limit=2000"
            $monitorApiResponse = Invoke-RestMethod -Uri $docuSignMonitorAPI -Method 'GET' -Headers $docuSignAPIHeaders
            
            Write-Output "Iteration:$iterations"
             
            # Get the endCursor value from the response. 
            # This lets you resume getting records from the spot where this call left off
                  
            $currentRunEndCursorValue = $monitorApiResponse.endCursor            
            Write-Output "currentRunEndCursorValue :$currentRunEndCursorValue"
            Write-Output "Last run cursorValue : $lastRunEndCursorValue"            
            
			if (![string]::IsNullOrEmpty($lastRunEndCursorValue))
            {
                # If the endCursor from the response is the same as the one that you already have,
                # it means that you have reached the end of the records
                if ($currentRunEndCursorValue.Substring(0, $currentRunEndCursorValue.LastIndexOf('_')) -eq $lastRunEndCursorValue.Substring(0, $lastRunEndCursorValue.LastIndexOf('_')))
                {
                    Write-Output 'Current run endCursor & last run endCursor values are the same. This indicates that you have reached the end of your available records.'
                    $complete=$true
                }
            }
            
            if(!$complete){           
                Write-Output "Updating the cursor value of $lastRunEndCursorValue to the new value of $currentRunEndCursorValue"
                $lastRunEndCursorValue=$currentRunEndCursorValue                                
				$postReturnCode = SendToLogA -EventsData $monitorApiResponse.data
                if($postReturnCode -eq 200)
                {
                    Write-Host ("{$monitorApiResponse.data.length} DocuSign Security Events have been ingested into Azure Log Analytics Workspace Table {$CustomLogTable}")
                }
                Remove-Item $monitorApiResponse
                $lastRunEndCursorContext.org = $orgName
                $lastRunEndCursorContext.lastRunEndCursor = $lastRunEndCursorValue
                $lastRunEndCursorContext.lastRun = $currentStartTime
                $lastRunMonitorContext | ConvertTo-Json | Out-File "$tempDir\lastrun-Monitor.json"
                Set-AzStorageBlobContent -Blob "lastrun-Monitor.json" -Container $storageAccountContainer -Context $storageAccountContext -File "$tempDir\lastrun-Monitor.json" -Force
                Remove-Item "$tempDir\lastrun-Monitor.json" -Force
				Remove-Item "$tempDir\orgs.json" -Force
                Start-Sleep -Second 5
            }
        }
        catch{
            $int = 0
            foreach($header in $_.Exception.Response.Headers){
                if($header -eq "X-DocuSign-TraceToken"){ write-host "TraceToken : " $_.Exception.Response.Headers[$int]}
                $int++
            }
            write-host "Error : $_.ErrorDetails.Message"
            write-host "Command : $_.InvocationInfo.Line"
            $complete = $true
        } 
    
    } While ($complete -eq $false )

} # closing foreach 

Write-Output "Done."
