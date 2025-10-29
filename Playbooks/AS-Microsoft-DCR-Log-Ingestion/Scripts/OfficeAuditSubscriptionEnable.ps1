# Prompt for tenantId, clientId, and clientSecret
$tenantId = Read-Host -Prompt "Enter Tenant ID"
$clientId = Read-Host -Prompt "Enter Client ID"
$clientSecret = Read-Host -Prompt "Enter Client Secret Value"

# Get an OAuth token for the API
$body = @{
    grant_type    = "client_credentials"
    resource      = "https://manage.office.com"
    client_id     = $clientId
    client_secret = $clientSecret
}

$tokenResponse = Invoke-RestMethod -Method Post -Uri "https://login.microsoftonline.com/$tenantId/oauth2/token" -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $tokenResponse.access_token

# Check the subscription status
$headers = @{
    Authorization = "Bearer $token"
}

$uri = "https://manage.office.com/api/v1.0/$tenantId/activity/feed/subscriptions/list"
$subscriptions = Invoke-RestMethod -Uri $uri -Headers $headers
$subscriptions

# Define the URL for starting the subscription
$startUri = "https://manage.office.com/api/v1.0/$tenantId/activity/feed/subscriptions/start?contentType=Audit.AzureActiveDirectory"

# Start the subscription
$startSubscription = Invoke-RestMethod -Uri $startUri -Headers $headers -Method POST

# Output the result
$startSubscription
