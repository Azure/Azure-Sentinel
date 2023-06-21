using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)
$flag = 0
# Write to the Azure Functions log stream.
Write-Host "Connecting to exchange online......"

# Interact with query parameters or the body of the request.
# $name = $Request.Query.Name
# Collecting parameters from Body

$ApplicationId = $Request.Body.ApplicationId  

$OrganizationName = $Request.Body.OrganizationName

$CertificateThumbPrint = $Request.Body.CertificateThumbPrint
try{
    Connect-ExchangeOnline -CertificateThumbPrint $CertificateThumbPrint -AppID "$ApplicationId" -Organization "$OrganizationName"
    if($?){
        $body = "Exchange online connected"
        $flag = 1
    }
}

catch{
    Write-Host "$_.Exception"
    $body = "$_.Exception"
}


finally{
if ($flag){
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