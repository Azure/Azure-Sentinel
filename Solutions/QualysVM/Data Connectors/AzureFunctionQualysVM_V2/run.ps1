<#
    Title:          Qualys Vulnerability Management (VM) Host Detection Data Connector
    Language:       PowerShell
    Version:        1.2
    Author(s):      Microsoft
    Last Modified:  8/14/2020
    Comment:        Added pagination support and flatten the data.

    DESCRIPTION
    This Function App calls the Qualys Vulnerability Management (VM) API (https://www.qualys.com/docs/qualys-api-vmpc-user-guide.pdf) specifically for Host List Detection data (/api/2.0/fo/asset/host/vm/detection/).
    The response from the Qualys API is recieved in XML format. This function will parse the XML into JSON format, build the signature and authorization header needed to post the data
    to the Log Analytics workspace via the HTTP Data Connector API. The Function App will omit API responses that with an empty host list, which indicates there were no records for that
    time interval. Often, there are Hosts with numerous scan detections, which causes the record submitted to the Data Connector API to be truncated and improperly ingested, The Function App
    will also identify those records greater than the 32Kb limit per record and seperate them into individual records.
#>

# Input bindings are passed in via param block
param($Timer)

# Get the current Universal Time
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than was originally scheduled
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# Define the Log Analytics Workspace ID and Key and Custom Table Name
$CustomerId = $env:workspaceId
$SharedKey = $env:workspaceKey
$TimeStampField = "DateValue"
$TableName = "QualysHostDetectionV2"

# Build the headers for the Qualys API request
$username = $env:apiUserName
$password = $env:apiPassword
$logAnalyticsUri = $env:logAnalyticsUri
$hdrs = @{"X-Requested-With"="PowerShell"}
$uri = $env:uri
$filterParameters = $env:filterParameters
$api = "/api/2.0/fo/asset/host/vm/detection/?"
$LOGGED = $BATCH = 0
$param = @{'status'='New,Active,Fixed,Re-Opened'; 'action'='list'; 'show_results'=1; 'show_igs'=0}

# ISO:8601-compliant DateTime required.
$time = $env:timeInterval
# the $time will be reduced from the current UTC time to achive incremental pull.
$vm_processed_before = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$vm_processed_after = ([System.DateTime]::UtcNow.AddMinutes(-$($time))).ToString('yyyy-MM-ddTHH:mm:ssZ')

if ([string]::IsNullOrEmpty($logAnalyticsUri))
{
    $logAnalyticsUri = "https://" + $CustomerId + ".ods.opinsights.azure.com"
}

# Returning if the Log Analytics Uri is in incorrect format.
# Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
{
    throw "QualysVM: Invalid Log Analytics Uri."
}

#check if the filterParameters are allowed or not
$allParameters = ""
$notAllowedParams = @("action","vm_processed_after", "vm_processed_before")
if ($filterParameters){
	$filterParameters.split("&") | ForEach-Object{
		$k,$v = $_.split("=")
		if ($notAllowedParams.Contains($k)){
			Write-Host "$_ parameter is not allowed and not added in the request. Please remove it from the filterParameters."
		} else{
			Write-Host "adding filterParameters: $_"
			$param[$k] = $v
		}
	}
}
foreach($i in $param.Keys){
	$allParameters += "${i}=$($param.Item($i))&"
}
# create a request URI
$all_params = $allParameters+"vm_processed_after="+$vm_processed_after+"&vm_processed_before="+$vm_processed_before
$request = ($uri + $api + $all_params)

# try creating a session to get the data from Qualys
try {
	Write-Host "Trying to create a session"
	$base =  [regex]::matches(($uri+ $api), '(https:\/\/[\w\.]+\/api\/\d\.\d\/fo)').captures.groups[1].value
	$body = "action=login&username=$($username)&password=$($password)"
	# Create a Logon Session variable
	Invoke-RestMethod -Headers $hdrs -Uri "$base/session/" -Method Post -Body $body -SessionVariable LogonSession

} catch{
	$exp = $_.Exception
	$expStatusCode = $exp.Response.StatusCode.value__
	if($expStatusCode -eq 401){
		Write-Host "APIStatusCode:$expStatusCode`nAPIStatusMessage:$exp.Message `nPlease verify the API credentials. Not able to create session.  `nError @ line #$line. `nI'm exiting now!!"
	} elseif (-not ($expStatusCode -eq 200)){
		Write-Host "APIStatusCode:$expStatusCode `nAPIStatusMessage:$exp. `nMessage Not able to create a session. `nError @ line #$line. `nI'm exiting now!!"
	}
	Invoke-WebRequest -Headers $hdrs -Uri "$($base)/session/" -Method Post -Body "action=logout" -WebSession $LogonSession
	Exit
}
# print the request details
Write-Host "Session creation is successfull `nUsing API Server: $uri `nUsing Host Detection API: $api `nUsing Username: $username `nUsing Parameters : $all_params, `nTable name: $TableName"

#===================================== Function Definitions =====================================#

# Function to build the Authorization signature for the Log Analytics Data Connector API
Function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
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

	# Dispose SHA256 from heap before return
	$sha256.Dispose()

	return $authorization
} # Build-Signature

# Function to create and invoke an API POST request to the Log Analytics Data Connector API
Function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType)
{
	$method = "POST"
	$contentType = "application/json"
	$resource = "/api/logs"
	$rfc1123date = [DateTime]::UtcNow.ToString("r")
	$contentLength = $body.Length
	$signature = Build-Signature `
		-customerId $customerId `
		-sharedKey $sharedKey `
		-date $rfc1123date `
		-contentLength $contentLength `
		-method $method `
		-contentType $contentType `
		-resource $resource
	$uri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"

	$headers = @{
		"Authorization" = $signature;
		"Log-Type" = $logType;
		"x-ms-date" = $rfc1123date;
		"time-generated-field" = $TimeStampField;
	}

	$response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
	return $response.StatusCode

} # Post-LogAnalyticsData

# Iterate through each detection recieved from the API call and assign the variables (Column Names in LA) to each XML variable
Function Parse-and-Send($qualysResponse){
	$detections = @()
	$results = "NA"
	#iterate over the HOST LIST AND DETECTION LIST to have gerenralised detections
	$qualysResponse.HOST_LIST_VM_DETECTION_OUTPUT.RESPONSE.HOST_LIST.HOST | ForEach-Object {
        $hostObject = New-Object -TypeName PSObject
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "HostId" -Value $_.ID
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "IpAddress" -Value $_.IP
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "TrackingMethod" -Value $_.TRACKING_METHOD
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "OperatingSystem" -Value $_.OS."#cdata-section"
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "DnsName" -Value $_.DNS."#cdata-section"
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "NetBios" -Value $_.NETBIOS."#cdata-section"
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "QGHostId" -Value $_.QG_HOSTID."#cdata-section"
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "LastScanDateTime" -Value $_.LAST_SCAN_DATETIME
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "LastVMScannedDateTime" -Value $_.LAST_VM_SCANNED_DATE
        Add-Member -InputObject $hostObject -MemberType NoteProperty -Name "LastVMAuthScannedDateTime" -Value $_.LAST_VM_AUTH_SCANNED_DATE
		Write-Output "Adding data for Host id = $($_.ID)"

		foreach($detection in $_.DETECTION_LIST.DETECTION){
			$detectionObject = $hostObject.PsObject.Copy()
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "QID" -Value $detection.QID
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "SSL" -Value $detection.SSL
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "Type" -Value $detection.TYPE
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "Status" -Value $detection.STATUS
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "Ignored" -Value $detection.IS_IGNORED
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "Severity" -Value $detection.SEVERITY
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "Disabled" -Value $detection.IS_DISABLED
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "LastFixed" -Value $detection.LAST_FIXED_DATETIME
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "LastFound" -Value $detection.LAST_FOUND_DATETIME
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "TimesFound" -Value $detection.TIMES_FOUND
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "FirstFound" -Value $detection.FIRST_FOUND_DATETIME
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "LastUpdate" -Value $detection.LAST_UPDATE_DATETIME
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "LastProcessed" -Value $detection.LAST_PROCESSED_DATE
			$results = $detection.RESULTS.'#cdata-section'
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "Result_column_count" -Value 1
			Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "Results_0" -Value $results
			# if the RESULTS field has data more than 30KB chunk it
			if ($results){
				[bool] $do_collect = $true
				$results_array = @()
				Do{
					$kbyte = ([System.Text.Encoding]::UTF8.GetBytes($results)).Count/1024
					if ($kbyte -gt 30){
						$regex = [regex] "\b"
						$r1, $r2 = $regex.split($results, 2, 30000)
						$results_array += $r1
						$results = $r2
					}
					else{
						if ($results_array){
							$results_array += $results
							$result_column_count = $results_array.Length
							$detectionObject.Result_column_count = $result_column_count
							for ($i = 0; $i -lt $result_column_count; $i++){
								$result_column = "Results_$i"
								if ([bool]($detectionObject.PSobject.Properties.name -match $result_column)){
									$detectionObject.$result_column = $results_array[$i]
								} else{
									Add-Member -InputObject $detectionObject -MemberType NoteProperty -Name "Results_$i" -Value $results_array[$i]
								} # end of if-else for checking and populate if the detectionObject has the member or not
							} # end of for loop to add chunked results in detectionObject's member columns
						} # end of if the $results_array is populated with chunked results data
						$do_collect = $false
					}
				}while($do_collect)	# this do-while is used to collect the chunked Results field in results_array. As per the HTTP Data Collector API, the field value should not exide 32KB data limit.
			}# end of if where we check if the Results in null or not

			$detections += $detectionObject
			#create a array list of detection per Host Id
			$jsonPayload = $detections | ConvertTo-Json -Compress -Depth 3
			$mbyte = ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload)).Count/1024/1024
			# if the detections object has payload more than 27MB or less than equal to 30MB we will POST the payload and rest will be POSTED out of the detectionObject loop.
			if (($mbytes -gt 27) -and ($mbytes -le 30)){
				$qidLength = [int] $detections.length
				$id = $hostObject.HostId
				$responseCode = Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload)) -logType $TableName
				if ($responseCode -ne 200){
					Write-Host "ERROR: Log Analytics POST, Status Code: $responseCode. Host Id: $id with QID count: $qidLength, Not able to Log."
				}else {
					$LOGGED += $qidLength
					Write-Host "SUCCESS: Log Analytics POST, Status Code: $responseCode. Host Id: $id with QID count: $qidLength, logged successfully. DETECTIONS LOGGED: $qidLength, in batch: $BATCH"
				}
				$detections = @()
				$responseCode = 0
			}
			# reinitialise the object to have the next host
			$detectionObject = New-Object -TypeName PSObject
		}# end of detectionObject for loop

		# if the detections object is greater than 0MB and less than or equal to 30MB we will POST the payload from here
		if ($detections.Count -gt 0) {
			# we probably did not flush at point A. So we need to POST to Sentinel API now.
			$jsonPayload = $detections | ConvertTo-Json -Compress -Depth 3
			$id = $hostObject.HostId
			$qidLength = [int] $detections.Length
			$responseCode = Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload)) -logType $TableName

			if ($responseCode -ne 200){
					Write-Host "ERROR: Log Analytics POST, Status Code: $responseCode. Host Id: $id with QID count: $qidLength, Not able to Log."
			}else {
				$LOGGED += $qidLength
				Write-Host "SUCCESS: Log Analytics POST, Status Code: $responseCode. Host Id: $id with QID count: $qidLength, logged successfully. DETECTIONS LOGGED: $qidLength, in batch: $BATCH"
			}
		}
		# reinitialise the object to have the correct count of detections
		[int] $script:TOTAL_LOGGED += [int] $LOGGED
		$LOGGED = 0
		$responseCode = 0
		$detections = @()
	}# end of hostObject for loop
} # end of Parse-and-Send Function

#===================================== main =====================================#
[bool] $keep_running = $true

Do {
	try {
		Write-Host "Making Request: $request"
		$response = Invoke-RestMethod -Headers $hdrs -Uri $request -WebSession $LogonSession

		if ($response.HOST_LIST_VM_DETECTION_OUTPUT.RESPONSE.HOST_LIST -eq $null) {
			Write-Output "No new results found for this interval. Exiting..."
			$keep_running = $false
		} else {
			$request = ""
			# provide the response for parsing to Parse-and-Send Function
			Parse-and-Send $response
			$request = $response.selectnodes("//WARNING").URL."#cdata-section"
			if($request){
				Write-Host "Making Paginated Request."
				$BATCH += 1
			}else{
				Write-Output "All data fetched!"
				[bool] $keep_running = $false
			}# end of pegination if
		}
	} catch{
		$exp = $_.Exception
		$expStatusCode = $exp.Response.StatusCode.value__
		$line = $_.InvocationInfo.ScriptLineNumber
		if (-not ($expStatusCode -eq 200)){
			Write-Host "APIStatusCode:$expStatusCode `nAPIStatusMessage:$exp.Message. `nError @ line #$line. `nI'm exiting!"
		} elseif ($expStatusCode -eq 409){
			Write-Host "API concurrency limit reached.`nError @ line #$line. `nI'm exiting!"
		}
		Invoke-WebRequest -Headers $hdrs -Uri "$($base)/session/" -Method Post -Body "action=logout" -WebSession $LogonSession
		Exit
	}
} while($keep_running) # end of main while loop

# dispose of the session
Invoke-WebRequest -Headers $hdrs -Uri "$($base)/session/" -Method Post -Body "action=logout" -WebSession $LogonSession
Write-Host "Qualys Host Detection session ended `nTOTAL DETECTIONS LOGGED: $script:TOTAL_LOGGED `nPowerShell timer trigger function ran! TIME: $currentUTCtime"