using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)
$flag = 0
# Write to the Azure Functions log stream.
Write-Host "Fetching list of spam policies"

$ListType = $Request.Body.ListType
# Interact with query parameters or the body of the request.
try{
if($ListType)
{
    $Result = Get-TenantAllowBlockListItems -ListType $ListType
    if($?){Write-Host "Successfully fetched list of tenants"
    $flag = 1
}
    else
    {Write-Host "Failed to fetch list of tenants"}

}else{
    {Write-Host "Request failed : ListType Parameter not provided"} 
}
}

catch{
    Write-Host "$_.Exception"
    $Result = "$_.Exception"
}

finally{
# Associate values to output bindings by calling 'Push-OutputBinding'.
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