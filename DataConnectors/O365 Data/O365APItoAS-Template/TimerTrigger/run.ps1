# Input bindings are passed in via param block.
param($Timer)

#Import-module .\TimerTrigger\modules\Write-OMSLogfile.ps1
###################################################################################
#  API Log to OMS Log Analytics Workspace
###################################################################################
#Credit: https://github.com/tsrob50/LogAnalyticsAPIFunction
function Write-OMSLogfile {
    <#
    .SYNOPSIS
    Inputs a hashtable, date and workspace type and writes it to a Log Analytics Workspace.
    .DESCRIPTION
    Given a  value pair hash table, this function will write the data to an OMS Log Analytics workspace.
    Certain variables, such as Customer ID and Shared Key are specific to the OMS workspace data is being written to.
    This function will not write to multiple OMS workspaces.  Build-signature and post-analytics function from Microsoft documentation
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
    Purpose/Change: Crating a stand alone function.
    .EXAMPLE
    This Example will log data to the "LoggingTest" Log Analytics table
    $type = 'LoggingTest'
    $dateTime = Get-Date
    $data = @{
        ErrorText   = 'This is a test message'
        ErrorNumber = 1985
    }
    $returnCode = Write-OMSLogfile $dateTime $type $data -Verbose
    write-output $returnCode
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

        #region Workspace ID and Key
        # Workspace ID for the workspace
        #$CustomerID = 'ENTER WORKSPACE ID HERE'

        # Shared key needs to be set for environment
        # Below uses an encrypted variable from Azure Automation
        # Uncomment the next two lines if using Azure Automation Variable and comment the last
        # $automationVarName = 'Enter Variable Name Here'
        # $sharedKey = Get-AutomationVariable -name $automationVarName
        # Key Vault is another secure option for storing the value
        # Less secure option is to put the key in the code
        #$SharedKey = 'ENTER WORKSPACE KEY HERE'

        #endregion

        # Supporting Functions
        # Function to create the auth signature
        function Build-signature ($CustomerID, $SharedKey, $Date, $ContentLength, $method, $ContentType, $resource) {
            $xheaders = 'x-ms-date:' + $Date
            $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource
            $bytesToHash = [text.Encoding]::UTF8.GetBytes($stringToHash)
            $keyBytes = [Convert]::FromBase64String($SharedKey)
            $sha256 = New-Object System.Security.Cryptography.HMACSHA256
            $sha256.key = $keyBytes
            $calculateHash = $sha256.ComputeHash($bytesToHash)
            $encodeHash = [convert]::ToBase64String($calculateHash)
            $authorization = 'SharedKey {0}:{1}' -f $CustomerID,$encodeHash
            return $authorization
        }
        # Function to create and post the request
        Function Post-LogAnalyticsData ($CustomerID, $SharedKey, $Body, $Type) {
            $method = "POST"
            $ContentType = 'application/json'
            $resource = '/api/logs'
            $rfc1123date = ($dateTime).ToString('r')
            $ContentLength = $Body.Length
            $signature = Build-signature `
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
                "Authorization" = $signature;
                "Log-Type" = $type;
                "x-ms-date" = $rfc1123date
                "time-generated-field" = $dateTime
            }
            $response = Invoke-WebRequest -Uri $LAURI -Method $method -ContentType $ContentType -Headers $headers -Body $body -UseBasicParsing
            Write-Verbose -message ('Post Function Return Code ' + $response.statuscode)
            return $response.statuscode
        }

        # Check if time is UTC, Convert to UTC if not.
        # $dateTime = (Get-Date)
        if ($dateTime.kind.tostring() -ne 'Utc'){
            $dateTime = $dateTime.ToUniversalTime()
            Write-Verbose -Message $dateTime
        }

        # Add DateTime to hashtable
        #$logdata.add("DateTime", $dateTime)
        $logdata | Add-Member -MemberType NoteProperty -Name "DateTime" -Value $dateTime

        #Build the JSON file
        $logMessage = ConvertTo-Json $logdata -Depth 20
        Write-Verbose -Message $logMessage

        #Submit the data
        $returnCode = Post-LogAnalyticsData -CustomerID $CustomerID -SharedKey $SharedKey -Body ([System.Text.Encoding]::UTF8.GetBytes($logMessage)) -Type $type
        Write-Verbose -Message "Post Statement Return Code $returnCode"
        return $returnCode
    }

function Get-AuthToken{
    [cmdletbinding()]
        Param(
            [Parameter(Mandatory = $true, Position = 0)]
            [string]$ClientID,
            [parameter(Mandatory = $true, Position = 1)]
            [string]$ClientSecret,
            [Parameter(Mandatory = $true, Position = 2)]
            [string]$tenantdomain,
            [Parameter(Mandatory = $true, Position = 3)]
            [string]$TenantGUID
        )
    # Create app of type Web app / API in Azure AD, generate a Client Secret, and update the client id and client secret here
    if ([string]::IsNullOrEmpty($loginURL)){$loginURL = "https://login.microsoftonline.com/"}
    # Get the tenant GUID from Properties | Directory ID under the Azure Active Directory section
    
    $resource = "https://$managementApi"
    # auth
    $body = @{grant_type="client_credentials";resource=$resource;client_id=$ClientID;client_secret=$ClientSecret}
    $oauth = Invoke-RestMethod -Method Post -Uri $loginURL/$tenantdomain/oauth2/token?api-version=1.0 -Body $body
    $headerParams = @{'Authorization'="$($oauth.token_type) $($oauth.access_token)"}
    return $headerParams 
}

function Get-O365Data{
    [cmdletbinding()]
    Param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$startTime,
        [parameter(Mandatory = $true, Position = 1)]
        [string]$endTime,
        [Parameter(Mandatory = $true, Position = 2)]
        [psobject]$headerParams,
        [parameter(Mandatory = $true, Position = 3)]
        [string]$tenantGuid
    )
    #List Available Content
    $contentTypes = $env:contentTypes.split(",")
    #Loop for each content Type like Audit.General
    foreach($contentType in $contentTypes){
        $listAvailableContentUri = "https://$managementApi/api/v1.0/$tenantGUID/activity/feed/subscriptions/content?contentType=$contentType&PublisherIdentifier=$env:publisher&startTime=$startTime&endTime=$endTime"
        do {
            #List Available Content
            $contentResult = Invoke-RestMethod -Method GET -Headers $headerParams -Uri $listAvailableContentUri
            $contentResult.Count
            #Loop for each Content
            foreach($obj in $contentResult){
                #Retrieve Content
                $data = Invoke-RestMethod -Method GET -Headers $headerParams -Uri ($obj.contentUri)
                $data.Count
                #Loop through each Record in the Content
                foreach($event in $data){
                    #Filtering for Recrord types
                    #Get all Record Types
                    if($env:recordTypes -eq "0"){
                        #We dont need Cloud App Security Alerts due to MCAS connector
                        if(($event.Source) -ne "Cloud App Security"){
                            #Write each event to Log A
                            $writeResult = Write-OMSLogfile (Get-Date) $env:customLogName $event $env:workspaceId $env:workspaceKey
                            #$writeResult
                        }
                    }
                    else{
                        #Get only certain record types
                        $types = ($env:recordTypes).split(",")
                        if(($event.RecordType) -in $types){
                            #We dont need Cloud App Security Alerts due to MCAS connector
                            if(($event.Source) -ne "Cloud App Security"){
                                #write each event to Log A
                                $writeResult = Write-OMSLogfile (Get-Date) $env:customLogName $event $env:workspaceId $env:workspaceKey
                                #$writeResult
                            }
                        }
                        
                    }
                }
            }
            
            #Handles Pagination
            $nextPageResult = Invoke-WebRequest -Method GET -Headers $headerParams -Uri $listAvailableContentUri
            If(($nextPageResult.Headers.NextPageUrl) -ne $null){
                $nextPage = $true
                $listAvailableContentUri = $nextPageResult.Headers.NextPageUrl
            }
            Else{$nextPage = $false}
        } until ($nextPage -eq $false)
    }
}
# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

$LAURI = $env:LAURI
if (-Not [string]::IsNullOrEmpty($LAURI)){
	if($LAURI.Trim() -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
	{
		Write-Error -Message "MCASActivity-SecurityEvents: Invalid Log Analytics Uri." -ErrorAction Stop
		Exit
	}
}
$LoginURL = $env:loginEndpoint
if (-Not [string]::IsNullOrEmpty($LoginURL)){
	if($LoginURL.Trim() -notin @("https://login.microsoftonline.us","https://login.partner.microsoftonline.cn","https://login.microsoftonline.com"))
	{
		Write-Error -Message "MCASActivity-SecurityEvents: Invalid Login Endpoint Uri." -ErrorAction Stop
		Exit
	}
}
$managementApi = $env:managementApi
if (-Not [string]::IsNullOrEmpty($managementApi)){
	if($managementApi.Trim() -notin @("manage.office.com","manage-gcc.office.com","manage.office365.us","manage.protection.apps.mil"))
	{
		Write-Error -Message "MCASActivity-SecurityEvents: Invalid Management API Endpoint." -ErrorAction Stop
		Exit
	}
} else {$managementApi = "manage.office.com"}

#add last run time to blob file to ensure no missed packages
$endTime = $currentUTCtime | Get-Date -Format yyyy-MM-ddTHH:mm:ss
$azstoragestring = $Env:WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
$Context = New-AzStorageContext -ConnectionString $azstoragestring
if((Get-AzStorageContainer -Context $Context).Name -contains "lastlog"){
    #Set Container
    $Blob = Get-AzStorageBlob -Context $Context -Container (Get-AzStorageContainer -Name "lastlog" -Context $Context).Name -Blob "lastlog.log"
    $lastlogTime = $blob.ICloudBlob.DownloadText()
    $startTime = $lastlogTime | Get-Date -Format yyyy-MM-ddTHH:mm:ss
    $endTime | Out-File "$env:TEMP\lastlog.log"
    Set-AzStorageBlobContent -file "$env:TEMP\lastlog.log" -Container (Get-AzStorageContainer -Name "lastlog" -Context $Context).Name -Context $Context -Force
}
else {
    #create container
    $azStorageContainer = New-AzStorageContainer -Name "lastlog" -Context $Context
    $endTime | Out-File "$env:TEMP\lastlog.log"
    Set-AzStorageBlobContent -file "$env:TEMP\lastlog.log" -Container $azStorageContainer.name -Context $Context -Force
    $startTime = $currentUTCtime.AddSeconds(-300) | Get-Date -Format yyyy-MM-ddTHH:mm:ss
}
$startTime
$endTime
$lastlogTime


$headerParams = Get-AuthToken $env:clientID $env:clientSecret $env:domain $env:tenantGuid
Get-O365Data $startTime $endTime $headerParams $env:tenantGuid


# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
