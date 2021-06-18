param(
		[Parameter(Mandatory=$true,ValueFromPipeline=$true)]
        [hashtable]$hash
    )

    $api ="Invoke-WebRequest "

  foreach ($key in $hash.Keys){
         $api+= "$key" +" "+ '$hash'+ '["'+ $key+ '"]'+ " "
         Write-Host("Key : $($key)"+ "`n" +"Value : $($hash[$key])")
     }

     $api+= "-UseBasicParsing"

try
{
    $response = Invoke-Expression $api 
  }
catch { 

Write-host("An API error occurred.")
Write-Host $_
 }

#$response = Invoke-WebRequest -Uri $hash["uri"] -Method 'GET' -Headers $hash["headers"] -Body $hash["body"] -UseBasicParsing

$responseObj = (ConvertFrom-Json $response.Content)
$responseCount = $responseObj.count

Write-Host("API Response : $($responseObj)")
Write-Host("API returned :$($responseCount) records")
