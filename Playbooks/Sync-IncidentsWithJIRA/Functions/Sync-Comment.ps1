using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)

#variables
$jiraUser = ""
$jiraSecretURL = ""
$sentinelSecretURL = ""
$tenantId = ""
$clientid = ""

# Write to the Azure Functions log stream.
Write-Host "PowerShell HTTP trigger function processed a request."

#find comment with highest updated time => comment we want to sync
$max = ($Request.body.fields.comment.comments | Measure-Object -Property updated -Maximum).Maximum

#Get latest comment
$newComment = $Request.body.fields.comment.comments  | ? {$_.updated -eq $max}

Write-Host $newComment.body

#Retrieve Graph API Secret
$tokenAuthURI = $Env:MSI_ENDPOINT +"?resource=https://vault.azure.net&api-version=2017-09-01"
$tokenResponse = Invoke-RestMethod -Method Get -Headers @{"Secret"="$env:MSI_SECRET"} -Uri $tokenAuthURI
$accessToken = $tokenResponse.access_token

#Retrieve JIRA secret
$headers = @{ 'Authorization' = "Bearer $accessToken" }
$queryUrl = $jiraSecretURL + "?api-version=7.0"
$keyResponse = Invoke-RestMethod -Method GET -Uri $queryUrl -Headers $headers
$jiraSecret= $keyResponse.value
$pair = "$($jiraUser):$($jiraSecret)"

$encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))

$basicAuthValue = "Basic $encodedCreds"

$Headers = @{
 Authorization = $basicAuthValue
 'Content-Type'='application/json'
}

#Retrieve latest comment
$comment = (Invoke-WebRequest -uri $newComment.self -Method GET -Headers $Headers).Content

$jsonComment = $comment | ConvertFrom-Json

#Check if this is a public or internal comment. We only sync public comments
if($jsonComment.jsdPublic -eq "True"){
    Write-Host "This is a public comment that will be posted"
    
    #remove images from comments
    $sanitizedComment = $newComment.body -replace "(?<=!image)(.*)(?=!)" -replace "!image!"

    #Create author text to add to incident
    $Author = "$($newcomment.updateAuthor.displayName) (The Collective) wrote: `n"

    #add author to comment
    $commentWithAuthor = $Author + $sanitizedComment

    Write-Host $commentWithAuthor

    Write-Host $sanitizedComment
    $tokenAuthURI = $Env:MSI_ENDPOINT +"?resource=https://vault.azure.net&api-version=2017-09-01"
    $tokenResponse = Invoke-RestMethod -Method Get -Headers @{"Secret"="$env:MSI_SECRET"} -Uri $tokenAuthURI
    $accessToken = $tokenResponse.access_token
    # get secret value sentinel
    $headers = @{ 'Authorization' = "Bearer $accessToken" }
    $queryUrl = $sentinelSecretURL + "?api-version=7.0"

    $keyResponse = Invoke-RestMethod -Method GET -Uri $queryUrl -Headers $headers
    $apiSecret= $keyResponse.value

    
    $body=@{
        client_id=$clientid
        client_secret=$apiSecret
        resource="https://management.azure.com"
        grant_type="client_credentials"
    }

    $accesstoken = Invoke-WebRequest -Uri "https://login.microsoftonline.com/$tenantId/oauth2/token" -ContentType "application/x-www-form-urlencoded" -Body $body -Method Post

    $accessToken=$accessToken.content | ConvertFrom-Json

    $authHeader = @{
        'Content-Type'='application/json'
        'Authorization'="Bearer " + $accessToken.access_token
        'ExpiresOn'=$accessToken.expires_in
    }

    $guid = (New-Guid).Guid

    #Create correct URL for api call
    $SentinelURL = "https://management.azure.com/subscriptions/$($request.body.fields.customfield_10162)/resourceGroups/$($request.body.fields.customfield_10169)/providers/Microsoft.OperationalInsights/workspaces/$($request.body.fields.customfield_10170)/providers/Microsoft.SecurityInsights/incidents/$($request.body.fields.customfield_10145)/comments/$($guid)?api-version=2019-01-01-preview"

    $body = @{
        "properties"= @{
            "message"= $commentWithAuthor
        }
    }

    $JSON = ConvertTo-Json $body

    #Add comment to Sentinel incident
    $data = Invoke-RestMethod -Headers $authHeader -URI $sentinelURL -Body $JSON -Method PUT -ContentType 'application/json'

}
else{
    Write-Host "Internal comment, not posting"
}


# Associate values to output bindings by calling 'Push-OutputBinding'.
Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = [HttpStatusCode]::OK
    Body = $body
})
