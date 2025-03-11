using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)
$flag = 0
# Write to the Azure Functions log stream.
Write-Host "Creating sender Block list entries"

$ListType = $Request.Body.ListType
$Entries = $Request.Body.Entries
$ExpirationDate  = $Request.Body.ExpirationDate
# Interact with query parameters or the body of the request.

try{
if($ListType -AND $Entries)
{
    if($ExpirationDate){
    $Result = New-TenantAllowBlockListItems -ListType $ListType -Block -Entries $Entries -ExpirationDate $ExpirationDate
    if($?){
        Write-Host "Successfully Blocked Entries"
        $flag = 1
    }
    else
    {
        
        Write-Host "Failed to Block Entries"
    
    }
    }else{
      
        $Result = New-TenantAllowBlockListItems -ListType $ListType -Block -Entries $Entries -NoExpiration
        if($?){
            Write-Host "Successfully Blocked Entries"
            $flag = 1
        }
        else
        {
            
            Write-Host "Failed to Block Entries"
        
        }
    }

}else{
    Write-Host "Missing parameters (ListType ,Entries)"
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
