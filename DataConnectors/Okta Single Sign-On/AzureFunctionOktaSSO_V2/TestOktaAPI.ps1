# To test api result update $uri and $apitoken value to retrieves records 

$uri = "https://<admin.okta.com>/api/v1/logs?since=2021-04-21T00%3A00%3A00.000Z&limit=1000&after=1619009193338_1"
# e. g "https://dev-98980195-admin.okta.com/api/v1/logs?since=2021-04-21T00%3A00%3A00.000Z&limit=1000&after=1619009193338_1"
$apiToken = "<API Token>"

$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Content-Type", "application/json")
$headers.Add("User-Agent", "AzureFunction")
$headers.Add("Authorization", "SSWS $apiToken")
$headers.Add("Accept-Encoding", "gzip, br")



$response = Invoke-WebRequest -uri $uri  -Method 'GET' -Headers $headers -Body $body -UseBasicParsing
$responseObj = (ConvertFrom-Json $response.content)
$responseCount = $responseObj.count
Write-Host("This $uri retrieves `n: $responseCount records ")