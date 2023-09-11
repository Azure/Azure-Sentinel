<# Input Parameters #>
Param(
[Parameter(Mandatory = $true)]
[String] $apiAccessToken,

[Parameter(Mandatory = $true)]
[String] $EnvironmentEndpointURL, 

[Parameter(Mandatory = $true)]
[String] $keyVaulturl,

[Parameter(Mandatory = $true)]
[String] $keyVaultTenantID,

[Parameter(Mandatory = $true)]
[String] $keyVaultClientID,

[Parameter(Mandatory = $true)]
[String] $keyVaultClientSecret
)
<# End Input Parameters #>

<# Global Variables #>
$headers = @{}
$headers.add("Accept", "application/json")
$headers.add("Content-Type", "application/json")
$authToken = "QSDK " + $apiAccessToken
$headers.add("Authtoken", $authToken) 
<# End of Global Variables #>

<# Get the current date and time as a Unix timestamp #>
$currentUnixTime = [int][double]::Parse((Get-Date -UFormat %s))

<# Add 7 days in seconds (7 * 24 * 60 * 60) #>
$sevenDaysInSeconds = 604800

<# Add 7 days to the current Unix timestamp #>
$desiredTimeUNIXtimestamp = $currentUnixTime + $sevenDaysInSeconds

<# Generate unique AccessToken name that contain creation and expiry timestamp #>
$newTokenName = "soar-crt$currentUnixTime-exp$desiredTimeUNIXtimestamp"

<# Create new API AccessToken #>
$body = @{
    tokenExpires = @{
        time = $desiredTimeUNIXtimestamp
    }
    scope        = 2
    tokenName    = $newTokenName
} | ConvertTo-Json
$generateAccessTokenURL = "https://$EnvironmentEndpointURL/commandcenter/api/ApiToken/User"
$generateAccessTokenResult = Invoke-RestMethod $generateAccessTokenURL -Method POST -Headers $headers -Body $body

<# If the new access token was generated, set it in KeyVault #>
$newAccessToken = $null
$newAccessToken = $generateAccessTokenResult.token
if ($newAccessToken -ne $null) { 
    $url = "https://login.microsoftonline.com/$keyVaultTenantId/oauth2/token"
    $headers = @{
        "Content-Type" = "application/x-www-form-urlencoded"
    }
    $data = @{
        "grant_type" = "client_credentials"
        "client_id" = $keyVaultClientID
        "client_secret" = $keyVaultClientSecret
        "resource" = "https://vault.azure.net"
    }
    $response = Invoke-RestMethod -Uri $url -Method POST -Body $data -Headers $headers
    $keyvault_access_token = $response.access_token
    $endpoint = "$keyVaultUrl/secrets/access-token?api-version=7.2"
    $headers = @{
        "Authorization" = "Bearer $keyvault_access_token"
        "Content-Type" = "application/json"
    }
    $body = @{
        "value" = $newAccessToken 
    }
    $response = Invoke-RestMethod -Uri $endpoint -Method PUT -Body ($body | ConvertTo-Json) -Headers $headers -ContentType 'application/json'
    Write-Output $response.value
}
else { Write-Output "FAIL. Could not generate a new access token." }