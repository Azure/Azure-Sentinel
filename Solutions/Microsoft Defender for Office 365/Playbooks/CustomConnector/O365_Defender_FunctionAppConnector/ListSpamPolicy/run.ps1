using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)
$flag = 0
# Write to the Azure Functions log stream.
Write-Host "Fetching list of spam policies"

$Identity = $Request.Body.Identity
# Interact with query parameters or the body of the request.

try{
if($Identity)
{
    $Result = Get-HostedContentFilterPolicy -Identity "$Identity"
    if($?){Write-Host "Successfully fetched list of policies"
    $flag = 1
}
    else
    {Write-Host "Failed to fetch list of policies"}

}else{
    
    $Result = Get-HostedContentFilterPolicy
    if($?){Write-Host "Successfully fetched list of policies"
    $flag = 1
}
    else
    {Write-Host "Failed to fetch list of policies"} 
}
}

catch{
    Write-Host "$_.Exception"
    $Result = "$_.Exception"
}

finally{
if($flag){
    # Associate values to output bindings by calling 'Push-OutputBinding'.
    Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
        StatusCode = [HttpStatusCode]::OK
        Body = $Result
    })}else{
    
        Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
            StatusCode = [HttpStatusCode]::NotFound
            Body = $Result
        })
    }
}    