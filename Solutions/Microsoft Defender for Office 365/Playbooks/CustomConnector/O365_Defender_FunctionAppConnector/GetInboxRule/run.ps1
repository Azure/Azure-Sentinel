using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)
$flag = 0
# Write to the Azure Functions log stream.
Write-Host "Fetching list of Malware policies"

$Mailbox = $Request.Body.Mailbox
# Interact with query parameters or the body of the request.

try{
if($Mailbox)
{
    $Result = Get-InboxRule -Mailbox "$Mailbox"
    if($?){Write-Host "Successfully fetched list of Inbox Rules"
    $flag = 1
}
    else
    {Write-Host "Failed to fetch list of Inbox Rules"}

}else
    {Write-Host "Mailbox not provided : Failed to fetch list of Inbox Rules"} 
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
