$username = "ProofPointTap Username"
$password = "ProofPointTap Password"
$uri = "https://tap-api-v2.proofpoint.com/v2/siem/all?format=json&sinceSeconds=300"

$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $username,$password)))
$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("au", "")
$headers.Add("Authorization", "Basic " + $base64AuthInfo)


# Invoke the API Request and assign the response to a variable ($response)
$response = Invoke-RestMethod $uri -Method 'GET' -Headers $headers

# Define the different ProofPoint Log Types. These values are set by the ProofPoint API and required to seperate the log types into the respective Log Analytics tables
$ProofPointlogTypes = @(
    "ClicksBlocked", 
    "ClicksPermitted",
    "MessagesBlocked", 
    "MessagesDelivered")


# Iterate through the ProofPoint API response and if there are log events present, POST the events to the Log Analytics API into the respective tables.
ForEach ($PPLogType in $ProofpointLogTypes) {
    if ($response.$PPLogType.Length -eq 0 ){ 
        Write-Host ("ProofPointTAP$($PPLogType) reported no new logs for the time interval configured.")
    }
    else {
        if($response.$PPLogType -eq $null) {                            # if the log entry is a null, this occurs on the last line of each LogType. Should only be one per log type
            Write-Host ("ProofPointTAP$($PPLogType) null line excluded")    # exclude it from being posted
        } else {            
            $json = $response.$PPLogType | ConvertTo-Json -Depth 3                # convert each log entry and post each entry to the Log Analytics API
            Write-Host ("ProofPointTAP$($PPLogType) reported $($response.$PPLogType.Length) new logs for the time interval configured.")
            }
        }
}