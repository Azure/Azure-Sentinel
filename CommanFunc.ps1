#common function to verify azure function

param
(
  [string]$uri,
  [System.Collections.Generic.Dictionary[[String],[String]]]$headers,
  [string]$body
)

#$response = Invoke-RestMethod -Headers $authHeaders -Uri $uri
Write-Host("URI : $uri")
Write-Host("header :$($headers)")
Write-Host("$body")

$response = Invoke-WebRequest -Uri $uri -Method 'GET' -Headers $headers -UseBasicParsing

$responseObj = (ConvertFrom-Json $response.Content)
$responseCount = $responseObj.count

Write-Host("API Response : $($responseObj)")
Write-Host("API returned :$($responseCount) records")
