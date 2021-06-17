<#  
    Title:          Qualys Vulnerability Management (VM) Host Detection Data Connector
    Language:       PowerShell    
    Version:        1.1
    Author(s):      Microsoft
    Last Modified:  12/04/2020
    Comment:        Added support for special characters in username and/or password

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

$logAnalyticsUri = $env:logAnalyticsUri

if ([string]::IsNullOrEmpty($logAnalyticsUri))
{
    $logAnalyticsUri = "https://" + $customerId + ".ods.opinsights.azure.com"
}

# Returning if the Log Analytics Uri is in incorrect format.
# Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
{
    throw "Qualys KB: Invalid Log Analytics Uri."
}

# The 'IsPastDue' property is 'true' when the current function invocation is later than was originally scheduled
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# Define the Log Analytics Workspace ID and Key and Custom Table Name
$CustomerId = $env:workspaceId
$SharedKey = $env:workspaceKey
$TimeStampField = "DateValue"
$TableName = "QualysHostDetection"

# Build the headers for the Qualys API request
$username = [uri]::EscapeDataString($env:apiUsername)
$password = [uri]::EscapeDataString($env:apiPassword)
$hdrs = @{"X-Requested-With"="PowerShell"}
$uri = $env:uri
$filterParameters = $env:filterParameters       
$time = $env:timeInterval

$base =  [regex]::matches($uri, '(https:\/\/[\w\.]+\/api\/\d\.\d\/fo)').captures.groups[1].value
$body = "action=login&username=$($username)&password=$($password)"  
Invoke-RestMethod -Headers $hdrs -Uri "$base/session/" -Method Post -Body $body -SessionVariable LogonSession

# ISO:8601-compliant DateTime required.
$startDate = [System.DateTime]::UtcNow.AddMinutes(-$($time))

# Invoke the API Request and assign the response to a variable ($response)
$response = (Invoke-RestMethod -Headers $hdrs -Uri "$uri$($startDate.ToString('yyyy-MM-ddTHH:mm:ssZ'))$($filterParameters)" -WebSession $LogonSession)

# Identifies the number of hosts with detections were found in the API call
$hostcount = $response.HOST_LIST_VM_DETECTION_OUTPUT.RESPONSE.HOST_LIST.HOST.Count
Write-Output "$($hostcount) hosts with detection found"

# Iterate through each detection recieved from the API call and assign the variables (Column Names in LA) to each XML variable
if (-not ($response.HOST_LIST_VM_DETECTION_OUTPUT.RESPONSE.HOST_LIST -eq $null))
{
    $customObjects = @()
    $response.HOST_LIST_VM_DETECTION_OUTPUT.RESPONSE.HOST_LIST.HOST | ForEach-Object {
        $customObject = New-Object -TypeName PSObject
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "Id" -Value $_.ID
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "IpAddress" -Value $_.IP
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "TrackingMethod" -Value $_.TRACKING_METHOD
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "OperatingSystem" -Value $_.OS."#cdata-section"
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "DnsName" -Value $_.DNS."#cdata-section"
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "NetBios" -Value $_.NETBIOS."#cdata-section"
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "QGHostId" -Value $_.QG_HOSTID."#cdata-section"
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "LastScanDateTime" -Value $_.LAST_SCAN_DATETIME
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "LastVMScannedDateTime" -Value $_.LAST_VM_SCANNED_DATE
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "LastVMAuthScannedDateTime" -Value $_.LAST_VM_AUTH_SCANNED_DATE
        $detections = @()
        foreach($detection in $_.DETECTION_LIST.DETECTION)
        {
            $customSubObject = New-Object -TypeName PSObject
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "QID" -Value $detection.QID
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "Type" -Value $detection.TYPE
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "Severity" -Value $detection.SEVERITY
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "SSL" -Value $detection.SSL
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "Results" -Value $detection.RESULTS.'#cdata-section'
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "Status" -Value $detection.STATUS
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "TimesFound" -Value $detection.TIMES_FOUND
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "FirstFound" -Value $detection.FIRST_FOUND_DATETIME
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "LastFixed" -Value $detection.LAST_FIXED_DATETIME
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "LastFound" -Value $detection.LAST_FOUND_DATETIME
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "LastProcessed" -Value $detection.LAST_PROCESSED_DATETIME
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "LastUpdate" -Value $detection.LAST_UPDATE_DATETIME
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "Ignored" -Value $detection.IS_IGNORED
            Add-Member -InputObject $customSubObject -MemberType NoteProperty -Name "Disabled" -Value $detection.IS_DISABLED
            $detections += $customSubObject
        }

        # Add the custom object as a child object to the parent
        Add-Member -InputObject $customObject -MemberType NoteProperty -Name "Detections" -Value $detections
        $customObjects += $customObject
    }

    # Dispose of the session
    Invoke-RestMethod -Headers $hdrs -Uri "$($base)/session/" -Method Post -Body "action=logout" -WebSession $LogonSession

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
    }

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
        
        $logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"
        $headers = @{
            "Authorization" = $signature;
            "Log-Type" = $logType;
            "x-ms-date" = $rfc1123date;
            "time-generated-field" = $TimeStampField;
    	}

    	$response = Invoke-WebRequest -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    	return $response.StatusCode

    }

    # Convert to JSON and API POST to Log Analytics Workspace
    $newcustomObjects = @()
    $under30kbObjects = @()
	$customObjects | ForEach-Object {  
        $records = $_ | ConvertTo-Json -Compress -Depth 3
        # Calculate the kbytes/record
        $kbytes = ([System.Text.Encoding]::UTF8.GetBytes($records)).Count/1024         
            # If the record is greater than 30kb (Azure HTTP Data Connector field size limit-32kb), create a new object. Record size surpasses this limit due to large amounts of detections per host                           
            if ($kbytes -gt 30){                                                                                                                                                                           
                $newObject = @()
                # The new object will consist of only a single detection with all the parent/host record information
                ForEach ($QID in $_.Detections){
                    $newObject = New-Object -TypeName PSObject
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "Id" -Value $_.ID
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "IpAddress" -Value $_.IpAddress
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "TrackingMethod" -Value $_.TrackingMethod
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "OperatingSystem" -Value $_.OperatingSystem
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "DnsName" -Value $_.DnsName
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "NetBios" -Value $_.NetBios
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "QGHostId" -Value $_.QGHostId
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "LastScanDateTime" -Value $_.LastScanDateTime
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "LastVMScannedDateTime" -Value $_.LastVMScannedDateTime
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "LastVMAuthScannedDateTime" -Value $_.LastVMAuthScannedDateTime
                    $subdetection = @()
                    $QID | ForEach-Object {                                                                             
                    $newSubObject = New-Object -TypeName PSObject
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "QID" -Value $QID.QID
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "Type" -Value $QID.Type
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "Severity" -Value $QID.Severity
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "SSL" -Value $QID.SSL
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "Results" -Value $QID.Results
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "Status" -Value $QID.Status
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "TimesFound" -Value $QID.TimesFound
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "FirstFound" -Value $QID.FirstFound
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "LastFixed" -Value $QID.FirstFound
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "LastFound" -Value $QID.LastFound
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "LastProcessed" -Value $QID.LastProcessed
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "LastUpdate" -Value $LastUpdate
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "Ignored" -Value $QID.Ignored
                        Add-Member -InputObject $newSubObject -MemberType NoteProperty -Name "Disabled" -Value $QID.Disabled
                        $subdetection += $newSubObject
                    }
                    # Add the custom object as a child object to the parent
                    Add-Member -InputObject $newObject -MemberType NoteProperty -Name "Detections" -Value $subdetection
                    
                    # Add it to the array that contains all the records parent information / individual detection to be posted
                    $newcustomObjects += $newObject
                }
            }
            else {
            # The record is less than 30kb, add to the array to be posted
            $under30kbObjects += $_
            }
        }

        # Convert the arrays containing all the records to JSON and send API POST to Log Analytics Workspace
        if($newcustomObjects.Length -gt 0){
            $json = $newcustomObjects | ConvertTo-Json -Compress -Depth 3
            # $mbytes = [math]::Round(([System.Text.Encoding]::UTF8.GetBytes($records)).Count/1024/1024,2)
            # Write-Output "$($mbytes) MB ALA API POST payload size)  
            Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($json)) -logType $TableName 
        }
        if($under30kbObjects.Length -gt 0){
            # $mbytes2 = [math]::Round(([System.Text.Encoding]::UTF8.GetBytes($records)).Count/1024/1024,2)
            # Write-Output "$($mbytes2) MB ALA API POST payload size)  
            $under30kbjson = $under30kbObjects | ConvertTo-Json -Compress -Depth 3
            Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($under30kbjson)) -logType $TableName
        }
    }
else
    {
    # If the response from the Qualys API is null or empty, dispose of the session
    Invoke-RestMethod -Headers $hdrs -Uri "$($base)/session/" -Method Post -Body "action=logout" -WebSession $LogonSession
    Write-Host "No new results found for this interval"
} 