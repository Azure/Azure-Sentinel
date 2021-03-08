<#  
    Title:          DocuSign Security Events Data Connector
    Language:       PowerShell
    Version:        2.0
    Author:         Sreedhar Ande
    Last Modified:  2/16/2021
    Comment:        V2 re-designed; 
					Ingests Security Events for your DocuSign account into Azure Log Analytics Workspace using DocuSign Monitor REST API
                    Ingests DocuSign Account Users into Azure Log Analytics Workspace using DocuSign Users REST API	
					Note:Above API's resumes getting records from the spot where the previous call left off to avoid duplication of records in DocuSignSecurityEvents_CL and DocuSignUsers_CL Log Analytics Workspace custom tables

    DESCRIPTION
    This Function App calls the DocuSign Monitor REST API (https://lens.docusign.net/api/v2.0/datasets/monitor/stream/) to pull the security events for your DocuSign account. 
    The response from the DocuSign Monitor REST API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API.
#>

# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

if ($Timer.IsPastDue) {
    Write-Host "DocuSign-SecurityEvents: Azure Function triggered at: $currentUTCtime - timer is running late!"
}
else{
    Write-Host "DocuSign-SecurityEvents: Azure Function triggered at: $currentUTCtime - timer is ontime!"
}

# Main
if ($env:MSI_SECRET -and (Get-Module -ListAvailable Az.Accounts)){
    Connect-AzAccount -Identity
}


$AzureWebJobsStorage = $env:AzureWebJobsStorage
$DocuSignIntegrationKey = $env:DocuSignIntegrationKey
$DocuSignAdminUserGUID = $env:DocuSignAdminUserGUID
$DocuSignAccountAPIID = $env:DocuSignAccountAPIID
$DocuSignEnvironment = $env:DocuSignEnvironment
$workspaceId = $env:WorkspaceId
$workspaceKey = $env:WorkspaceKey
$storageAccountContainer = "docusign-monitor"
$storageAccountTableName = "docusignexecutions"
$LATableDSMAPI = $env:LATableDSMAPI
$LATableDSUsers = $env:LATableDSUsers
$LAURI = $env:LAURI
$DocuSignUserInfoBaseURI = $env:DocuSignUserInfoBaseURI

# Flag to turn on/off DocuSign Users information into LA Workspace Table
$DocuSignUsersIngestion = $env:NeedDocuSignUsers

$currentStartTime = (get-date).ToUniversalTime() | get-date  -Format yyyy-MM-ddTHH:mm:ss:ffffffZ
Write-Output "LAURI : $LAURI"

if($LAURI.Trim() -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
{
    Write-Error -Message "DocuSign-SecurityEvents: Invalid Log Analytics Uri." -ErrorAction Stop
	Exit
}


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
        $LAURI = $LAURI.Trim() + $resource + "?api-version=2016-04-01"
		Write-Output "LAURI : $LAURI"
        $headers = @{
            "Authorization"        = $signature;
            "Log-Type"             = $type;
            "x-ms-date"            = $rfc1123date
            "time-generated-field" = $dateTime
        }
        $response = Invoke-WebRequest -Uri $LAURI.Trim() -Method $method -ContentType $contentType -Headers $headers -Body $Body -UseBasicParsing
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

Function SendToLogA ($eventsData, $eventsTable) {    	
	#Test Size; Log A limit is 30MB
    $tempdata = @()
    $tempDataSize = 0
    
    if ((($eventsData |  Convertto-json -depth 20).Length) -gt 25MB) {        
		Write-Host "Upload is over 25MB, needs to be split"									 
        foreach ($record in $eventsData) {            
            $tempdata += $record
            $tempDataSize += ($record | ConvertTo-Json -depth 20).Length
            if ($tempDataSize -gt 25MB) {
                $postLAStatus = Write-OMSLogfile -dateTime (Get-Date) -type $eventsTable -logdata $tempdata -CustomerID $workspaceId -SharedKey $workspaceKey
                write-Host "Sending data = $TempDataSize"
                $tempdata = $null
                $tempdata = @()
                $tempDataSize = 0
            }
        }
        Write-Host "Sending left over data = $Tempdatasize"
        $postLAStatus = Write-OMSLogfile -dateTime (Get-Date) -type $eventsTable -logdata $eventsData -CustomerID $workspaceId -SharedKey $workspaceKey
    }
    Else {          
        $postLAStatus = Write-OMSLogfile -dateTime (Get-Date) -type $eventsTable -logdata $eventsData -CustomerID $workspaceId -SharedKey $workspaceKey        
    }

    return $postLAStatus
}


If ($DocuSignEnvironment.ToLower() -eq "developer") {
    $jwtHost = "account-d"
    $dsmHost = "lens-d"
} 
Else {
    $jwtHost = "account"
    $dsmHost = "lens"
}

$apiVersion = "eSignature"

$timestamp = [int][double]::Parse((Get-Date (Get-Date).ToUniversalTime() -UFormat %s))

$storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage
$checkBlob = Get-AzStorageBlob -Blob "DocuSignRSAPrivateKey.key" -Container $storageAccountContainer -Context $storageAccountContext
if($null -ne $checkBlob){
    Get-AzStorageBlobContent -Blob "DocuSignRSAPrivateKey.key" -Container $storageAccountContainer -Context $storageAccountContext -Destination "C:\local\Temp\DocuSignRSAPrivateKey.key" -Force
    $privateKeyPath = "C:\local\Temp\DocuSignRSAPrivateKey.key"
}
else{
    Write-Error "No DocuSignRSAPrivateKey.key file, exiting"
    exit
}

if ($apiVersion -eq "rooms") {
    $scopes = "signature%20impersonation%20dtr.rooms.read%20dtr.rooms.write%20dtr.documents.read%20dtr.documents.write%20dtr.profile.read%20dtr.profile.write%20dtr.company.read%20dtr.company.write%20room_forms"
  } elseif ($apiVersion -eq "eSignature") {    
    $scopes = "signature%20impersonation"
  } elseif ($apiVersion -eq "click") {
    $scopes = "click.manage"
}


# Step 1. Create a JWT

$decJwtHeader = [ordered]@{
    'typ' = 'JWT';
    'alg' = 'RS256'
} | ConvertTo-Json -Compress

# Remove %20 from scope string
$scopes = $scopes -replace '%20',' '
$exp = $timestamp + 7200

$decJwtPayLoad = [ordered]@{
    'iss'   = $DocuSignIntegrationKey;
    'sub'   = $DocuSignAdminUserGUID;
    'iat'   = $timestamp;
    'exp'   = $exp;
    'aud'   = "$jwtHost.docusign.com";
    'scope' = $scopes
} | ConvertTo-Json -Compress

$encJwtHeaderBytes = [System.Text.Encoding]::UTF8.GetBytes($decJwtHeader)
$encJwtHeader = [System.Convert]::ToBase64String($encJwtHeaderBytes) -replace '\+', '-' -replace '/', '_' -replace '='

$encJwtPayLoadBytes = [System.Text.Encoding]::UTF8.GetBytes($decJwtPayLoad)
$encJwtPayLoad = [System.Convert]::ToBase64String($encJwtPayLoadBytes) -replace '\+', '-' -replace '/', '_' -replace '='

$jwtToken = "$encJwtHeader.$encJwtPayLoad"

try{
	Add-Type -Path "C:\home\site\wwwroot\Modules\DerConverter.dll"
	Add-Type -Path "C:\home\site\wwwroot\Modules\PemUtils.dll"

	$keyStream = [System.IO.File]::OpenRead($privateKeyPath)
	$rsaParameters = [PemUtils.PemReader]::new($keyStream).ReadRsaKey()
	$rsa = [System.Security.Cryptography.RSA]::Create($rsaParameters)

	$tokenBytes = [System.Text.Encoding]::ASCII.GetBytes($jwtToken)
	$signedToken = $rsa.SignData(
		$tokenBytes,
		[System.Security.Cryptography.HashAlgorithmName]::SHA256,
		[System.Security.Cryptography.RSASignaturePadding]::Pkcs1)

	$signedBase64Token = [System.Convert]::ToBase64String($signedToken) -replace '\+', '-' -replace '/', '_' -replace '='

	$jwtToken = "$encJwtHeader.$encJwtPayLoad.$signedBase64Token"

	$keyStream.Close()
	$keyStream.Dispose()
}
catch {
	Write-Output "Please check you have DerConverter.dll and PemUtils.dll under C:\home\site\wwwroot\Modules"
	$keyStream.Close()
	$keyStream.Dispose()
}

# Step 2. Obtain the access token
try {
	Write-Output "Obtaining DocuSign access token"
    $authorizationEndpoint = "https://$jwtHost.docusign.com/oauth/"    
    $tokenResponse = Invoke-WebRequest `
        -Uri "$authorizationEndpoint/token" `
        -Method "POST" `
        -Body "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=$jwtToken"
    
    $docuSignAccessToken = ($tokenResponse | ConvertFrom-Json).access_token
	
	#Setup uri Headers for requests to DSM API & User API
	$docuSignAPIHeaders = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
	$docuSignAPIHeaders.Add("Content-Type", "application/json")
	$docuSignAPIHeaders.Add("Authorization", "Bearer $docuSignAccessToken")

	$StorageTable = Get-AzStorageTable -Name $storageAccountTableName -Context $storageAccountContext -ErrorAction Ignore
	if($null -eq $StorageTable.Name){  
		New-AzStorageTable -Name $storageAccountTableName -Context $storageAccountContext
		$docuSignTimeStampTbl = (Get-AzStorageTable -Name $storageAccountTableName -Context $storageAccountContext.Context).cloudTable    
		Add-AzTableRow -table $docuSignTimeStampTbl -PartitionKey "docusignmonitor" -RowKey "lastRunEndCursor" -property @{"lastCursorValue"=""} -UpdateExisting		
	}
	Else {
		$docuSignTimeStampTbl = (Get-AzStorageTable -Name $storageAccountTableName -Context $storageAccountContext.Context).cloudTable
	}
	# retrieve the last execution values
	$lastExeEndCursor = Get-azTableRow -table $docuSignTimeStampTbl -partitionKey "docusignmonitor" -RowKey "lastRunEndCursor" -ErrorAction Ignore	
	$lastRunEndCursorValue = $lastExeEndCursor.lastCursorValue
	
	$complete=$false    
	$iterations=0
	DO{
		$iterations++	
		try{
			$docuSignMonitorAPI=$null
			$monitorApiResponse = $null
			$docuSignMonitorAPI = "https://$dsmHost.docusign.net/api/v2.0/datasets/monitor/stream?cursor=${lastRunEndCursorValue}&limit=2000"
			Write-Output "Calling DocuSign Monitor API"
			$monitorApiResponse = Invoke-RestMethod -Uri $docuSignMonitorAPI -Method 'GET' -Headers $docuSignAPIHeaders
			
			# Display the data
			Write-Output "Iteration:$iterations"           

			# Get the endCursor value from the response. This lets you resume
			# getting records from the spot where this call left off
			#Response from Invoke-RestMethod        
			$currentRunEndCursorValue = $monitorApiResponse.endCursor			
			Write-Output "currentRunEndCursorValue :$currentRunEndCursorValue"
			Write-Output "Last run cursorValue : $lastRunEndCursorValue"
				
			if (![string]::IsNullOrEmpty($lastRunEndCursorValue))
			{
				# If the endCursor from the response is the same as the one that you already have,
				# it means that you have reached the end of the records
				if ($currentRunEndCursorValue -eq $lastRunEndCursorValue)
				{
					Write-Output 'Current run endCursor & last run endCursor values are the same. This indicates that you have reached the end of your available records.'
					$complete=$true
				}
			}
			
			if(!$complete){           
				Write-Output "Updating the cursor value of $lastRunEndCursorValue to the new value of $currentRunEndCursorValue"
				$lastRunEndCursorValue=$currentRunEndCursorValue  
				$securityEvents = $monitorApiResponse.data
				$securityEventsCount = $monitorApiResponse.data.length
				if ($securityEventsCount -gt 0) {
					$postReturnCode = SendToLogA -EventsData $securityEvents -EventsTable $LATableDSMAPI
					$securityEventsCount = $monitorApiResponse.data.length
					if($postReturnCode -eq 200)
					{
						Write-Output ("$securityEventsCount - DocuSign Security Events have been ingested into Azure Log Analytics Workspace Table --> $LATableDSMAPI")
					}
				}
				Remove-Item $monitorApiResponse
				Add-AzTableRow -table $docuSignTimeStampTbl -PartitionKey "docusignmonitor" -RowKey "lastRunEndCursor" -property @{"lastCursorValue"=$lastRunEndCursorValue} -UpdateExisting                           
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
	
	#users Export
	if ($DocuSignUsersIngestion.ToLower() -eq "true"){		
		try{
			$docuSignUsersAPI = $null
			$userApiResponse = $null
			$docuSignUsersAPI = "$DocuSignUserInfoBaseURI/restapi/v2.1/accounts/$DocuSignAccountAPIID/users?additional_info=true"
			Write-Output "Calling DocuSign Users API"
			$userApiResponse = Invoke-RestMethod -Uri $docuSignUsersAPI -Method 'GET' -Headers $docuSignAPIHeaders			
			$docuSignUsers = $userApiResponse.users
			
			$accountUsers = @()	
            foreach($dsUser in $docuSignUsers)
            {
                $isUserExisting = Get-azTableRow -table $docuSignTimeStampTbl -partitionKey $dsUser.userId.ToString() -ErrorAction Ignore
                if ($null -eq $isUserExisting) {
                    Add-AzTableRow -table $docuSignTimeStampTbl -PartitionKey $dsUser.userId.ToString() -RowKey $dsUser.userName.ToString() -UpdateExisting
                    $accountUsers += $dsUser					
                }
            }	
            $totalUsers = $accountUsers.Count
			Write-Output "New Users Count : $totalUsers"
			if($totalUsers -gt 0) {
				Write-Output "Ingesting DocuSign Users information to $LATableDSUsers"
                $postReturnCode = SendToLogA -EventsData $accountUsers -EventsTable $LATableDSUsers
                
                if($postReturnCode -eq 200)
                {
                    Write-Output ("$totalUsers users have been ingested into Azure Log Analytics Workspace Table $LATableDSUsers")
                }
            }
            else {
                Write-Output ("No New Users")
            }
			Remove-Item $userApiResponse			
		}
		catch {
			$int = 0
			foreach($header in $_.Exception.Response.Headers){
				if($header -eq "X-DocuSign-TraceToken"){ write-host "TraceToken : " $_.Exception.Response.Headers[$int]}
				$int++
			}
			write-host "Error : $_.ErrorDetails.Message"
			write-host "Command : $_.InvocationInfo.Line"   
		}	
	}
	Remove-Item $privateKeyPath -Force
	Write-Output "Done."

}
catch {
	$int = 0
	foreach($header in $_.Exception.Response.Headers){
		if($header -eq "X-DocuSign-TraceToken")
		{ write-host "TraceToken : " $_.Exception.Response.Headers[$int]}
		$int++
	}
	write-host "Error : $_.ErrorDetails.Message"
	write-host "Command : $_.InvocationInfo.Line"
}

