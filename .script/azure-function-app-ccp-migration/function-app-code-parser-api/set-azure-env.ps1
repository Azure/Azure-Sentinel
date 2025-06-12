# Check if you’re logged in; if not, trigger az login.
try {
    # Try to retrieve account info; an error means you’re not logged in.
    az account show | Out-Null
} catch {
    Write-Host "Not logged in. Launching az login..."
    az login | Out-Null
}    

# Retrieve the tenant ID and client ID from the current Azure account.
$tenantId = az account show --query tenantId -o tsv
$clientId = az account show --query user.name -o tsv
    
# Set the environment variables for the current PowerShell session.
$env:AZURE_TENANT_ID = $tenantId
$env:AZURE_CLIENT_ID = $clientId
$env:UAMI_CLIENT_ID = ""
$env:BING_SEARCH_V7_SUBSCRIPTION_KEY = ""
$env:BING_SEARCH_V7_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
$env:AZURE_OPENAI_ENDPOINT = "https://anki-openai.openai.azure.com/"
$env:AZURE_OPENAI_MODEL_NAME = "gpt-4.1"
$env:AZURE_OPENAI_MODEL_DEPLOYMENT = "sachin-gpt-4.1"
$env:AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
    
Write-Host "Azure Tenant ID set to:" $env:AZURE_TENANT_ID
Write-Host "Azure Client ID set to:" $env:AZURE_CLIENT_ID
    
# Note: For interactive user logins, the client secret is not applicable.
Write-Host "Please manually set AZURE_CLIENT_SECRET if necessary."