using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)
$flag = 0
# Write to the Azure Functions log stream.
Write-Host "Creating spam policies"

$Name = $Request.Body.Name
$HighConfidenceSpamAction = $Request.Body.HighConfidenceSpamAction
$SpamAction  = $Request.Body.SpamAction
$BulkThreshold   = $Request.Body.BulkThreshold
$BlockedSenderDomains  = $Request.Body.BlockedSenderDomains
# Interact with query parameters or the body of the request.
try{
if($Name -AND $HighConfidenceSpamAction -AND $SpamAction -AND $BulkThreshold -AND $BlockedSenderDomains)
{
    $Result = New-HostedContentFilterPolicy -Name $Name -HighConfidenceSpamAction $HighConfidenceSpamAction -SpamAction $SpamAction -BulkThreshold $BulkThreshold -BlockedSenderDomains $BlockedSenderDomains
    if($?){Write-Host "Successfully Created policies"
    $flag = 1
}
    else
    {Write-Host "Failed to create policies"}

}else{
    Write-Host "Missing parameters (Name ,HighConfidenceSpamAction ,SpamAction ,BulkThreshold, BlockedSenderDomains)"
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

