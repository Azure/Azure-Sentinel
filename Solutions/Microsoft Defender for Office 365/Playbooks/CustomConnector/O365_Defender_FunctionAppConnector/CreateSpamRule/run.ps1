using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)
$flag = 0
# Write to the Azure Functions log stream.
Write-Host "Creating spam policy rule"

$Name = $Request.Body.Name
$HostedContentFilterPolicy = $Request.Body.HostedContentFilterPolicy
$SentToMemberOf  = $Request.Body.SentToMemberOf
$RecipientDomainIs = $Request.Body.RecipientDomainIs
$SentTo = $Request.Body.SentTo

# Interact with query parameters or the body of the request.
try{
if($Name -AND $HostedContentFilterPolicy -AND $SentToMemberOf -AND $RecipientDomainIs -AND $SentTo){
    $Result = New-HostedContentFilterRule -Name $Name -HostedContentFilterPolicy $HostedContentFilterPolicy -SentToMemberOf $SentToMemberOf -RecipientDomainIs $RecipientDomainIs -SentTo $SentTo
    $flag = 1
}
if($Name -AND $HostedContentFilterPolicy -AND $SentToMemberOf -AND $RecipientDomainIs){
    $Result = New-HostedContentFilterRule -Name $Name -HostedContentFilterPolicy $HostedContentFilterPolicy -SentToMemberOf $SentToMemberOf -RecipientDomainIs $RecipientDomainIs
    $flag = 1
}

if($Name -AND $HostedContentFilterPolicy -AND $RecipientDomainIs -AND $SentTo){
    $Result = New-HostedContentFilterRule -Name $Name -HostedContentFilterPolicy $HostedContentFilterPolicy -RecipientDomainIs $RecipientDomainIs -SentTo $SentTo
    $flag = 1
}

if($Name -AND $HostedContentFilterPolicy -AND $SentToMemberOf -AND $SentTo){
    $Result = New-HostedContentFilterRule -Name $Name -HostedContentFilterPolicy $HostedContentFilterPolicy -SentToMemberOf $SentToMemberOf -SentTo $SentTo
    $flag = 1
}

if($Name -AND $HostedContentFilterPolicy -AND $SentToMemberOf){
    $Result = New-HostedContentFilterRule -Name $Name -HostedContentFilterPolicy $HostedContentFilterPolicy -SentToMemberOf $SentToMemberOf
    $flag = 1
}
if($Name -AND $HostedContentFilterPolicy -AND $RecipientDomainIs){
    $Result = New-HostedContentFilterRule -Name $Name -HostedContentFilterPolicy $HostedContentFilterPolicy -RecipientDomainIs $RecipientDomainIs
    $flag = 1
}
if($Name -AND $HostedContentFilterPolicy -AND $SentTo){
    $Result = New-HostedContentFilterRule -Name $Name -HostedContentFilterPolicy $HostedContentFilterPolicy -SentTo $SentTo
    $flag = 1
}

}

catch{
    Write-Host "$_.Exception"
    $Result = "$_.Exception"
}



finally{
if($flag)
{
   Write-Host "Successfully Created policy rule"
}
else{
    Write-Host "Missing parameters (Name ,HostedContentFilterPolicy or May be group,people to whom this policy needs to be attached)"
}

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

