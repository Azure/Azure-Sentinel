<# Input Variables #>
<# $EnvironmentEndpointURL = Read-Host -Prompt 'Input Metallic RingURL / Commvault endpoint URL / examples: m102.metallic.io | 10.0.0.5' #>
<# $apiAccessToken = Read-Host -Prompt 'Input Commvault RestAPI user AccessToken' #>

Param(
[Parameter(Mandatory = $true)]
[String] $apiAccessToken,

[Parameter(Mandatory = $true)]
[String] $EnvironmentEndpointURL
)

<# Global Variables #>
$headers = @{}
$headers.add("Accept", "application/json")
$headers.add("Content-Type","application/json")
$authToken = "QSDK "+$apiAccessToken
$headers.add("Authtoken",$authToken)
<# End of Global Variables #>

<# Get all Tenant Identity Servers #>
$getIdentityServersURL = "https://$EnvironmentEndpointURL/commandcenter/api/IdentityServers"
$getIdentityServersResult = Invoke-RestMethod $getIdentityServersURL -Method GET -Headers $headers
<# End of Get all Tenant Identity Servers #>

<# Filter Identity Servers that are SAML type #>
$samlIdentityServers = $getIdentityServersResult.identityServers | Where-Object { $_.samlType -eq 1}
<# For each SAML Identity Server go with steps to check it's state and take action #>
foreach ($samlIdentityServer in $samlIdentityServers) {

    <# Gets details of SAML Identity Server #>
    $samlIdentityServerName = $samlIdentityServer.IdentityServerName
    $getsamlIdentityServerPropURL = "https://$EnvironmentEndpointURL/commandcenter/api/V4/SAML/$samlIdentityServerName"
    $getsamlIdentityServerPropResult = Invoke-RestMethod $getsamlIdentityServerPropURL -Method GET -Headers $headers

    <# Check if SAML Identity Server is enabled or disabled and take action or give status #>
    if ($getsamlIdentityServerPropResult.enabled -eq $true) {
        Write-Output "Going to disable IDP server $samlIdentityServerName"
        <# Disable SAML Identity Server if it is enabled #>
        $body = "{`"enabled`": false, `"type`": `"SAML`"}"
        $disablesamlIdentityServerURL = "https://$EnvironmentEndpointURL/commandcenter/api/V4/SAML/$samlIdentityServerName"
        $disablesamlIdentityServerResult = Invoke-RestMethod $disablesamlIdentityServerURL -Method PUT -Headers $headers -Body $body
        $disablesamlIdentityServerResulterrorCode = $disablesamlIdentityServerResult.errorCode
        <# Based on response error code verify if action was succesfull and return status #>
        if ($disablesamlIdentityServerResulterrorCode -eq 0) {
        Write-Output "SAML IdentityProvider $samlIdentityServerName succesfully disabled"
        } else {"Something went wrong. Error code $disablesamlIdentityServerResulterrorCode for disabling SAML IdentityProvider $samlIdentityServerName action do not indicate success"}
    <# In case SAML Identity Server is alredy disabled return status #>
    } elseif ($getsamlIdentityServerPropResult.enabled -eq $false) {
        Write-Output "SAML IdentityProvider $samlIdentityServerName is already disabled. No action taken"
    <# In case SAML Identity Server disabled/enabled state is not correctly retrieved return status #>
    } else {Write-Output "Something went wrong. Unable to retrieve state for SAML IdentityProvider $samlIdentityServerName"}
}