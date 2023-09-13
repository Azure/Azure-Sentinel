<# Input Variables #>
<# $EnvironmentEndpointURL = Read-Host -Prompt 'Input Metallic RingURL / Commvault endpoint URL / examples: m102.metallic.io | 10.0.0.5' #>
<# $apiAccessToken = Read-Host -Prompt 'Input Commvault RestAPI user AccessToken' #>
<# $clientName = Read-Host -Prompt 'Input Server Hostname or ClientName' #> 

Param(
[Parameter(Mandatory = $true)]
[String] $apiAccessToken,

[Parameter(Mandatory = $true)]
[String] $EnvironmentEndpointURL,

[Parameter(Mandatory = $true)]
[String] $clientName
)


<# End of Input Variables #>

<# Global Variables #>
$headers = @{}
$headers.add("Accept", "application/json")
$headers.add("Content-Type","application/json")
$authToken = "QSDK "+$apiAccessToken
$headers.add("Authtoken",$authToken) 
<# End of Global Variables #>

<# Get all Tenant Clients #>
$getClientsURL = "https://$EnvironmentEndpointURL/commandcenter/api/client"
$getClientsResult = Invoke-RestMethod $getClientsURL -Method GET -Headers $headers
 
<# End of Get all Tenant Clients #>

<# Add wildcard (on the end) to Server Input to address scenario that server short name would be given and we have full FQDN or if there is additon on our ClientName like (1) #>
$clientName = $clientName + "*"
<# Select all Clients that match Input Server Hostname or ClientName #>
$selectedClients = @()
foreach ($client in $getClientsResult.clientProperties.client.clientEntity | Where-Object { $_.hostname -like $clientName -or $_.clientName -like $clientName}) {
    $selectedClients += New-Object PSObject -Property @{
        ClientName = $client.clientName
        ClientHostname = $client.hostname
        ClientID = $client.ClientId
        }
}

<# Check if Clients array is not empty | if anything was matched in previous step #>
if ($selectedClients -ne "") {

    <# Print matched Clients for referance #>
    Write-Output "Following Client(s) were found that match input Server Hostname or ClientName"
    Write-Output $selectedClients
    Write-Output "------------------------------"

<# Start flow for each matched Client in array #>
foreach ($selectedclient in $selectedClients) {
    <# Get attributes as ID, ClientName and Hostname from matched Clients array for current Client #>
    $selectedclientId = $selectedclient.ClientId
    $selectedclientName = $selectedclient.ClientName
    $selectedclientHostname = $selectedclient.ClientHostname
    <# Get Client Properties and Archive Pruning Status #>
    $getClientPropURL = "https://$EnvironmentEndpointURL/commandcenter/api/client/$selectedclientId"
    $getClientPropResult = Invoke-RestMethod $getClientPropURL -Method GET -Headers $headers
    $getClientActivityControlOptions = $getClientPropResult.clientProperties.clientProps.clientActivityControl.activityControlOptions
    $getClientActivityType16ControlOptions = ($getClientActivityControlOptions | Where-Object { $_.activityType -eq 16 })
    $clientArchivePruningStatus = $getClientActivityType16ControlOptions.enableActivityType

    <# Check what is Archive Pruning Status and perform relevant action #>
    <# First check if Archive Pruning Status is Enabled and then Disable it #>
    if ($clientArchivePruningStatus -eq $true) {

        $body = "{
            `n    `"clientProperties`": {
            `n        `"clientProps`": {
            `n            `"clientActivityControl`": {
            `n                `"activityControlOptions`": [
            `n                    {
            `n                        `"activityType`": 16,
            `n                        `"enableAfterADelay`": false,
            `n                        `"enableActivityType`": false
            `n                    }
            `n                ]
            `n            }
            `n        }
            `n    }
            `n}"
        $disableClientArchivePruningURL = "https://$EnvironmentEndpointURL/commandcenter/api/client/$selectedclientId"
        $disableClientArchivePruningResult = Invoke-RestMethod $getClientPropURL -Method POST -Headers $headers -Body $body
        $disableClientArchivePruningResultErrorCode = $disableClientArchivePruningResult.response.errorCode
        <# Check status of operation to Disable Archive Pruning Status and print relevant message #>
        if ($disableClientArchivePruningResultErrorCode -eq 0) {
            Write-Output "Archive Pruning succesfully Disabled for Client $selectedclientName (Hostname: $selectedclientHostname)"
        } else {Write-Output "Something went wrong. Error code $disableClientArchivePruningResultErrorCode do not indicate success for disabling Archive Pruning on Client $selectedclientName (Hostname: $selectedclientHostname)"}
    <# In case Archive Pruning Status is already Disabled print status #>
    } elseif ($clientArchivePruningStatus -eq $false) {
        Write-Output "Archive Pruning is already Disabled for Client $selectedclientName (Hostname: $selectedclientHostname). No further action taken."
    <# In case there was a problem with getting Archive Pruning Status print error message #>
    } else {Write-Output "Something went wrong. Unable to retrieve Archive Pruning status for Client $selectedclientName (Hostname: $selectedclientHostname)"}
}

<# In case Clients array is empty print eror message #>
} else {
    Write-Output "Something went wrong. No Client(s) found"
}