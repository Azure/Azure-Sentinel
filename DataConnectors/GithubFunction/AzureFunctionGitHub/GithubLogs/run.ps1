<#  
    Title:          GitHub Repo Logs Data Connector
    Language:       PowerShell
    Version:        1.2
    Author:         Nicholas Dicola, Sreedhar Ande
    Last Modified:  03/29/2021
    
    DESCRIPTION
    This Function App calls the GitHub REST API (https://api.github.com/) to pull the GitHub
    Audit, Repo and Vulnerability logs. The response from the GitHub API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post each log type to their individual tables in Log Analytics, for example,
    Github_CL and GitHubRepoLogs_CL.
#>

# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

[int]$maxdurationminutes=10
$script_start_time=([System.DateTime]::UtcNow)
# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"

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
$azstoragestring = $env:AzureWebJobsStorage
$Context = New-AzStorageContext -ConnectionString $azstoragestring
if((Get-AzStorageContainer -Context $Context).Name -contains "lastlog"){
    #Set Container
    $Blob = Get-AzStorageBlob -Context $Context -Container (Get-AzStorageContainer -Name "lastlog" -Context $Context).Name -Blob "lastlog.log"
    $lastlogTime = $blob.ICloudBlob.DownloadText()
    $startTime = $lastlogTime | Get-Date -Format yyyy-MM-ddTHH:mm:ss
    return $startTime
}

}   
# Main
if ($env:MSI_SECRET -and (Get-Module -ListAvailable Az.Accounts)){
    Connect-AzAccount -Identity
}


$currentStartTime = (get-date).ToUniversalTime() | get-date  -Format yyyy-MM-ddTHH:mm:ss:ffffffZ

if (-Not [string]::IsNullOrEmpty($LAURI)){
	if($LAURI.Trim() -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
	{
		Write-Error -Message "DocuSign-SecurityEvents: Invalid Log Analytics Uri." -ErrorAction Stop
		Exit
	}
}

function Write-OMSLogfile {
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



    $script_start_time=([System.DateTime]::UtcNow)

 
    # Supporting Functions
    # Function to create the auth signature
    function BuildSignature ($CustomerID, $SharedKey, $Date, $ContentLength, $method, $ContentType, $resource) {
        $xheaders = 'x-ms-date:' + $Date
        $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource
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
        $ContentType = 'application/json'
        $resource = '/api/logs'
        $rfc1123date = ($dateTime).ToString('r')
        $ContentLength = $Body.Length
        $signature = BuildSignature `
            -customerId $CustomerID `
            -sharedKey $SharedKey `
            -date $rfc1123date `
            -contentLength $ContentLength `
            -method $method `
            -contentType $ContentType `
            -resource $resource
        
		# Compatible with previous version
		if ([string]::IsNullOrEmpty($LAURI)){
			$LAURI = "https://" + $CustomerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
		}
		else
		{
			$LAURI = $LAURI + $resource + "?api-version=2016-04-01"
		}
		
        $headers = @{
            "Authorization"        = $signature;
            "Log-Type"             = $type;
            "x-ms-date"            = $rfc1123date
            "time-generated-field" = $dateTime
        }
        $response = Invoke-WebRequest -Uri $LAURI -Method $method -ContentType $ContentType -Headers $headers -Body $Body -UseBasicParsing
        Write-Verbose -message ('Post Function Return Code ' + $response.statuscode)
        return $response.statuscode
    }

    # Check if time is UTC, Convert to UTC if not.
    # $dateTime = (Get-Date)
    if ($dateTime.kind.tostring() -ne 'Utc') {
        $dateTime = $dateTime.ToUniversalTime()
        Write-Verbose -Message $dateTime
    }

    # Add DateTime to hashtable
    #$logdata.add("DateTime", $dateTime)
    $logdata | Add-Member -MemberType NoteProperty -Name "DateTime" -Value $dateTime

    #Build the JSON file
    $logMessage = ($logdata | ConvertTo-Json -Depth 20)
    Write-Verbose -Message $logMessage

    #Submit the data
    $returnCode = PostLogAnalyticsData -CustomerID $CustomerID -SharedKey $SharedKey -Body $logMessage -Type $type
    Write-Verbose -Message "Post Statement Return Code $returnCode"
    return $returnCode
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
function SendToLogA ($gitHubData, $customLogName) {    
    #Test Size; Log A limit is 30MB
    $tempdata = @()
    $tempDataSize = 0
    
    if ((($gitHubData |  Convertto-json -depth 20).Length) -gt 25MB) {        
		Write-Host "Upload is over 25MB, needs to be split"									 
        foreach ($record in $gitHubData) {            
            $tempdata += $record
            $tempDataSize += ($record | ConvertTo-Json -depth 20).Length
            if ($tempDataSize -gt 25MB) {
                Write-OMSLogfile -dateTime (Get-Date) -type $customLogName -logdata $tempdata -CustomerID $workspaceId -SharedKey $workspaceKey
                write-Host "Sending data = $TempDataSize"
                $tempdata = $null
                $tempdata = @()
                $tempDataSize = 0
            }
        }
        Write-Host "Sending left over data = $Tempdatasize"
        Write-OMSLogfile -dateTime (Get-Date) -type $customLogName -logdata $gitHubData -CustomerID $workspaceId -SharedKey $workspaceKey
    }
    Else {
        #Send to Log A as is        
        Write-OMSLogfile -dateTime (Get-Date) -type $customLogName -logdata $gitHubData -CustomerID $workspaceId -SharedKey $workspaceKey
    }
}


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
function GithubLogsProcessor()
{
$AzureWebJobsStorage = $env:AzureWebJobsStorage
$workspaceId = $env:WorkspaceId
$workspaceKey = $env:WorkspaceKey
$LAURI = $env:LAURI
$secret=$env:PEM
$storageAccountContainer = "github-repo-logs"
$AuditLogTable = "GitHub_CL"
$RepoLogTable = "GitHubRepoLogs_CL"
$apiSecret = [System.Text.Encoding]::UTF8.GetBytes($secret)
$appID=$env:appID
$appName=$env:appName

#Import-Module -Name powershell-jwt
$exp = [int][double]::parse((Get-Date -Date $((Get-Date).addseconds(300).ToUniversalTime()) -UFormat %s)) 
$iat = [int][double]::parse((Get-Date -Date $((Get-Date).ToUniversalTime()) -UFormat %s)) 
if(-not([string]::IsNullOrWhiteSpace($apiSecret)) -and -not([string]::IsNullOrWhiteSpace($appID)))
{
# create a Json Web Tokken using new-jwt from the powershell-jwt module
$jwt = New-JWT -Algorithm "RS256" -Issuer $appID -ExpiryTimestamp $exp -SecretKey $apiSecret -PayloadClaims @{ "iat" = $iat}
Write-Host $jwt
if(-not([string]::IsNullOrWhiteSpace($jwt)))
{
#Get Orgs from ORGS.json in Az Storage
$storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage
$checkBlob = Get-AzStorageBlob -Blob ORGS.json -Container $storageAccountContainer -Context $storageAccountContext
if($null -ne $checkBlob){
    Get-AzStorageBlobContent -Blob ORGS.json -Container $storageAccountContainer -Context $storageAccountContext -Destination "$env:temp\orgs.json" -Force
    $githubOrgs = Get-Content "$env:temp\orgs.json" | ConvertFrom-Json
}
else{
    Write-Error "No ORGS.json file, exiting"
    exit
}
$headersjwt = @{
    "Accept" = "application/vnd.github+json"
    "Authorization" = "Bearer $jwt"
}
#Process each Org
$repoList = @()
foreach($org in $githubOrgs){

    $orgName = $org.org
    $orguri= "https://api.github.com/orgs/$orgName/installation"
    $output = Invoke-WebRequest -Uri $orguri  -Headers $headersjwt
    if($null -ne $output)
    {
    $converted=ConvertFrom-Json $output
    Write-Host $converted.access_tokens_url
    $accesstokenurl=$converted.access_tokens_url
    if(-not([string]::IsNullOrWhiteSpace($accesstokenurl)) -and ($appID -eq $converted.app_id)  -and ($appName -eq $converted.app_slug))
    {
        
   $res = Invoke-WebRequest -Uri  $converted.access_tokens_url -Headers $headersjwt -Method Post
   $json_res = ConvertFrom-Json($res.Content)
   if($null -ne $json_res)
   {
   $token = $json_res.token
    Write-Host "Starting to process ORG: $orgName"
    $headersaccesstoken = @{
        Accept="application/vnd.github+json"
        Authorization="Bearer $token"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
   
    
    #Get the Audit Entries
    Write-Host "Starting to process ORG: $orgName Audit Entries"
    $uri = "https://api.github.com/orgs/$orgName/audit-log?phrase=created:>=$startTime and created:<=$now"
    $auditLogs = $null
    $auditLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headersaccesstoken
    if ($auditLogs.Length -gt 0){

                #Send to log A;
      SendToLogA -gitHubData $auditLogs -customLogName $AuditLogTable
    }
    else {
        Write-Host "There are no audit logs for this org: " $orgName
    }
    
    $uri = $null
    $results = $null
    
    #get Org repos
    $hasMoreRepos = $true
    $pageNumber = 1
    do {
        $uri = "https://api.github.com/orgs/$orgName/repos?page=$pageNumber"
        $results = Invoke-RestMethod -Method GET -Uri $uri -Headers $headersaccesstoken
        $repoList += $results
        if($results.Count -eq 0){
            Write-Host "No more repos found for Org: $orgName"
            $hasMoreRepos = $false
        }
        else {
            Write-Host "Getting more repos for Org: $orgName"
            $pageNumber++
        }
    } until ($hasMoreRepos -eq $false)
    
    $uri = $null
    $results = $null

    #For Each Repo in Org, get repo logs
    foreach($repo in $repoList){
        $repoName = $repo.Name        
        $uri = "https://api.github.com/repos/$orgName/$repoName/contributors"
        $contributorsInfo = Invoke-WebRequest -Method Get -Uri $uri -Headers $headersaccesstoken -UseBasicParsing
        Write-Host $contributorsInfo.statuscode
        # Status 204 represents No Content - ie., empty repo
        if ($contributorsInfo.statuscode -ne 204)
        {
            Write-Host "Starting to process ORG: $orgName Repo: $repoName"

            
            $uri = "https://api.github.com/repos/$orgName/$repoName/commits?&since=$startTime&until=$now"
            $commitLogs = $null
            $commitLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headersaccesstoken
            if ($commitLogs.Length -gt 0){
                $commitLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $commitLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $commitLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Commits
                #Send to log A
                SendToLogA -gitHubData $commitLogs -customLogName $RepoLogTable
            }
            else {
                Write-Host "There are no commits for this repo: "+$repoName+" Org Name:" $orgName
            }
            
         

			$uri = "https://api.github.com/repos/$orgName/$repoName/secret-scanning/alerts?&after>=$startTime?&before<=$now"
            $secretscanningalerts = $null
            try {
                $secretscanningalerts = Invoke-RestMethod -Method Get -Uri $uri -Headers $headersaccesstoken
            if ($secretscanningalerts.Length -gt 0){
                $secretscanningalerts | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $secretscanningalerts | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $secretscanningalerts | Add-Member -NotePropertyName LogType -NotePropertyValue SecretScanningAlerts
                #Send to log A
                SendToLogA -gitHubData $secretscanningalerts -customLogName $RepoLogTable
            }
            else {
                Write-Host "There are no SecretScanningAlerts for this repo: "+$repoName+" Org Name:" $orgName
            }      
            }
            catch {
                Write-Error "Failed at Scanning secrets with error message: $($_.Exception.Message)" -ErrorAction SilentlyContinue
            }
            
        }		 
        else {
            Write-Host "$repoName is empty"
            Write-Verbose "$repoName is empty"
        }       
    }
    
    # For each repo get Github Vulnerability Alerts
    foreach($repo in $repoList){
        $repoName = $repo.name
        
        #Build the query based on previous context or not
         $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100, before: \"'+$now+'\" after: \"'+$startTime+'\") { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
       
        $hasNextPage = $true
        $vulnList = @()
        $uri = $null
        do {
            $uri = "https://api.github.com/graphql"
            $results = $null
            $results = Invoke-RestMethod -Method Post -Uri $uri -Headers $headersaccesstoken -Body $VulnQuery
            if(($results.data.organization.repository.vulnerabilityAlerts.nodes).Count -ne 0){
                $vulnList += $results.data.organization.repository.vulnerabilityAlerts.nodes
                $vulnList | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $vulnList | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $vulnList | Add-Member -NotePropertyName LogType -NotePropertyValue vulnerabilityAlerts
                #send to log A; Name:GitHubRepoLogs
                SendToLogA -gitHubData $vulnList -customLogName $RepoLogTable                
            }
            else {
                Write-Host "There are no vulnerabilityAlerts for this repo: "+$repoName+" Org Name:" $orgName
            }
            $hasNextPage = $results.data.organization.repository.vulnerabilityAlerts.pageInfo.hasNextPage
            $lastRunContext = $results.data.organization.repository.vulnerabilityAlerts.pageInfo.endCursor
            if($hasNextPage -ne $false){
                if([string]::IsNullOrEmpty($lastRunContext)){
                    $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100, before: \"'+$now+'\" after: \"'+$startTime+'\") { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
                }
                else {
                    $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100, before: \"'+$lastRunContext+'\" after: \"'+$startTime+'\") { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
                }
            }
            else {
               # Do nothing
            }
        } until (($hasNextPage -eq $false) -or ($null -eq $hasNextPage))
    }
    #clear the repo list for next org
    $repoList = @()
	#clear the temp folder
	Remove-Item $env:temp\* -Recurse -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "No installation access token for this org " +$orgName
}
    }
    else {
        
        Write-Host "Access token not generated for this org " +$orgName
    }
}
else {
    Write-Host "Access token output not generated for this org " +$orgName
}
if((check_if_script_runs_too_long -percentage 0.8 -script_start_time $script_start_time))
{
    Write-Host "Script is running long"
    break
}
}

}
else {
    Write-Host "JWT is not generated"
}
}
else {
    Write-Error -Message "Please check APPId OR PEM in function app configuration." -ErrorAction Stop
	Exit
  
}

}
$azstoragestring = $env:AzureWebJobsStorage
$Context = New-AzStorageContext -ConnectionString $azstoragestring
$startTime,$now=GenerateDate
$startTime=$startTime | Get-Date -Format yyyy-MM-ddTHH:mm:ss.000K
if($startTime.Contains("Z"))
{
        ## Do Nothing
}
else {
    $startTime=$startTime+"Z"
}
$now= $now | Get-Date -Format yyyy-MM-ddTHH:mm:ss.000K
if($now.Contains("Z"))
{
        ## Do Nothing
}
else {
    $now=$now+"Z"
}
try {
    
    GithubLogsProcessor
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
}
catch {
    Write-Error "Failed at Github API with error message: $($_.Exception.Message)" -ErrorAction SilentlyContinue
}