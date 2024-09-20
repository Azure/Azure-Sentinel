using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)
$flag = 0
# Write to the Azure Functions log stream.
Write-Host "Proceeding with delete of Inbox Rule"

$Mailbox = $Request.Body.Mailbox
$Identity = $Request.Body.Identity
# Interact with query parameters or the body of the request.

try{
if($Mailbox -AND $Identity)
{
    $Result = Remove-InboxRule -Mailbox "$Mailbox" -Identity "$Identity" -Confirm:$false
    if($?){Write-Host "Successfully Deleted the rule"
    $flag = 1
}
    else
    {Write-Host "Failed to delete Inbox Rules"}

}else
    {Write-Host "Mailbox or Identity not provided : Failed to delete Inbox Rules"} 
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