using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)

# Write to the Azure Functions log stream.
Write-Host "Initiating Disconnecting request...."
$flag = 0
# Interact with query parameters or the body of the request.

try{
Disconnect-ExchangeOnline -Confirm:$false
if($?)
{
    Write-Host "Disconnecting from exchange succesfull"
    $body = "Disconnecting from exchange succesfull"
    $flag = 1

}else{
    
    Write-Host "Disconnecting from exchange failed"
    $body = "Disconnecting from exchange failed"
}
}

catch{
    Write-Host "$_.Exception"
    $Body = "$_.Exception"
}

finally{
# Associate values to output bindings by calling 'Push-OutputBinding'.
if($flag){
    # Associate values to output bindings by calling 'Push-OutputBinding'.
    Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
        StatusCode = [HttpStatusCode]::OK
        Body = $body
    })}else{
    
        Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
            StatusCode = [HttpStatusCode]::NotFound
            Body = $body
        })
    }
}