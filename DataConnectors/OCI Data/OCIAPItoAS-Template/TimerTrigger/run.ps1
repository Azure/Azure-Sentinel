# Input bindings are passed in via param block.
param($Timer)

# variables to authenticate and generate OCI Access Token
$b64clientidsecret = $env:b64clientidsecret
$IDCS = $env:IDCS
$siguri = "https://" + $IDCS + "/oauth2/v1/token"

# variables to Invoke and search for OCIAudit_CL latest table entry \ and HTTP DATA Collector API
$workspaceID = $env:workspaceID
$CustomerId = $env:workspaceID
$workspaceKey = $env:workspaceKey
$SharedKey = $env:workspaceKey
$LogType = "OCIAudit_CL"
$timeStampField = "timestamp"

# Form the Header and Body Request to obtain OCI Access Token
$sigHeaders = @{
    'Authorization' = 'Basic ' + $b64clientidsecret
    'Content-Type' = 'application/x-www-form-urlencoded;charset=UTF-8'
}

$sigBody = "grant_type=client_credentials&scope=urn:opc:idm:__myscopes__"

# Invoke to obtain OCI access token
$sig = (Invoke-RestMethod -Uri $siguri -Method POST -Headers $sigHeaders -Body $sigBody -Verbose).access_token

# Invoke and search for OCIAudit_CL latest table entry if found pass datetime value, if not pass a time generated from 5 days ago.
$starttime = (Invoke-AzOperationalInsightsQuery -WorkspaceId $workspaceID -Query "union isfuzzy=true (OCIAudit_CL |  summarize arg_max(TimeGenerated , TimeGenerated ) |project TimeGenerated ) | summarize arg_max(TimeGenerated , TimeGenerated ) | project TimeGenerated" -ErrorAction SilentlyContinue).Results.TimeGenerated

# Conditional check if OCIAudit_CL table does not exist need to prime and pump, set starttime a day ago
If (!$starttime) {

    #some additional if \ then to spot check if OCIAudit_CL table exists ?
    $starttime = (Get-date).AddDays(-1).ToString('yyyy-MM-ddThh:mm:ssZ') #.ffffZ   

}


# HTTP DATA Collector Functions

# Create the function to create the authorization signature
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
    return $authorization
}


# Create the function to create and post the request
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
    $uri = "https://" + $customerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"

    $headers = @{
        "Authorization" = $signature;
        "Log-Type" = $logType;
        "x-ms-date" = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    }

    $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    return $response.StatusCode

}

# Invoke to OCI AuditEvents using start time from tableresult
$headers = @{
    'Authorization' = 'Bearer ' + $sig
    'Content-Type' = 'application/scim+json'
}

# get the datetime from current run and format for OCI API Call to end the lookup range
$endtime = (Get-date -UFormat %Y-%m-%dT%R:%SZ) 


# Create the URI needed to invoke AuditEvents in OCI | BASE URI for testing #$audituri = "https://" + $IDCS + "/admin/v1/AuditEvents"
$audituri = "https://" + $IDCS + "/admin/v1/AuditEvents" + "?sortBy=timestamp&sortOrder=descending&filter=timestamp ge " + '"' + $starttime + '"' + " and timestamp le " + '"' + $endtime + '"'

# Invoke OCI AuditEvents API to obtain results
$auditresults = (Invoke-WebRequest -Uri $audituri -Method GET -Headers $headers).Content | ConvertFrom-Json

# define loop end upper boundary of pagination in this call 
$loopend = $auditresults.totalResults

# define the index start at result 1 for loop
$counter = 1

# Conditional check are the total results less than the pagination (defualtr 50 results per query, using index to start at), do we need to loop ?, default is 50 items per page but can be changed to 1000 in URI | count=1000
if ($loopend -le $auditresults.itemsPerPage) {

    # format the the first OCI AuditEvents API call into a JSON body
    $jsonbody = $auditresults.Resources | ConvertTo-Json
    
    # Use for testing uncomment below to writeout files to ensure while loop for pagination is working correctly. BE SURE TO COMMENT OUT Post-LogAnalyticsData line when tshooting.
    #$jsonbody | Out-File -FilePath c:\temp\jsonindex$counter.json

    # Send the JSONBody results to Azure Sentinel
    Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($jsonbody)) -logType $logType 
    
} else {

# Conditional chekc found that there are more results that per query result, leading to pagination. We will loop through and update the StartIndex each time to get the next batch of 50 results untill finished
do {

    # Create the URI needed to invoke AuditEvents in OCI using the StartIndex=$counter
    $audituri = "https://" + $IDCS + "/admin/v1/AuditEvents?startIndex=" + $counter + "&sortBy=timestamp&sortOrder=descending&filter=timestamp ge " + '"' + $starttime + '"' + " and timestamp le " + '"' + $endtime + '"'
    
    # Invoke OCI AuditEvents API to obtain results
    $auditresults = (Invoke-WebRequest -Uri $audituri -Method GET -Headers $headers).Content | ConvertFrom-Json
    
    # format the the first OCI AuditEvents API call into a JSON body
    $jsonbody = $auditresults.Resources | ConvertTo-Json

        # Use for testing uncomment below to writeout files to ensure while loop for pagination is working correctly. BE SURE TO COMMENT OUT Post-LogAnalyticsData line when tshooting.
        #$jsonbody | Out-File -FilePath c:\temp\jsonindex$counter.json

    # Send the JSONBody results to Azure Sentinel
    Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($jsonbody)) -logType $logType 
    
    # update pagination counter for the next set of results (defualt is 50 unless specified in URI to count=xxxx where xxxx is max value of 1000)
    $counter = $counter + $auditresults.itemsPerPage

# Continue the loop untill we are greater than the total AuditEvents pagination results
    } while ($counter -lt $loopend)
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"