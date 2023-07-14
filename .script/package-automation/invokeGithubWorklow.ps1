param($pullRequestBranchName, $pullRequestNumber)
$header = @{
    "Accept" = "application/vnd.github+json"
}

$githubToken = "$($env:GITHUB_TOKEN_VALUE)"

$token = $githubToken | ConvertTo-SecureString -AsPlainText -Force
$pullRequestNumberInt = [int]$pullRequestNumber
$client_payload = @{
    "command" = "ping"
    "pullRequestBranchName" = "$pullRequestBranchName"
    "pullRequestNumber" = $pullRequestNumberInt
}

$BodyJson = @{
    "event_type" = "package-command"
    "client_payload" = $client_payload
} 

$jsonBody = $BodyJson | ConvertTo-Json
Write-Host "jsonBody $jsonBody"
$Parameters = @{
    Method      = "POST"
    Uri         = "https://api.github.com/repos/Azure/Azure-Sentinel/dispatches"
    Headers     = $Header
    ContentType = "application/json"
    Body        = $jsonBody
    Authentication = "Bearer"
    Token = $token
}

$result = Invoke-RestMethod @Parameters
Write-Host $result