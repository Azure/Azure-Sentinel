param(
  [string]$SubscriptionId = "2f0fdbc8-ab60-4386-af30-dd0fac77130e",

  [string]$ResourceGroup = "dataacquisition-rg",

  [string]$Location = "eastus",

    [Parameter(Mandatory = $true)]
    [string]$FunctionAppName,

    [Parameter(Mandatory = $true)]
    [string]$StorageAccountName,

    [string]$AppServicePlanName = "",

    [ValidateSet("flex", "consumption", "premium")]
    [string]$HostingModel = "flex",

    [Parameter(Mandatory = $true)]
    [string]$KustoClusterUrl,

    [Parameter(Mandatory = $true)]
    [string]$KustoDatabase,

    [string]$SaOutputRawBaseUrl = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/solution_analyzer_output/Tools/Solutions%20Analyzer",

    [ValidateSet("managed-identity", "azure-cli")]
    [string]$KustoAuthMode = "managed-identity",

    [string]$ManagedIdentityClientId = ""
)

$ErrorActionPreference = "Stop"

Write-Host "Setting Azure subscription..."
az account set --subscription $SubscriptionId | Out-Null

$sub = az account show --query "{id:id,name:name}" -o json | ConvertFrom-Json
Write-Host "Using subscription: $($sub.name) ($($sub.id))"

Write-Host "Checking access to resource group '$ResourceGroup'..."
az group show --name $ResourceGroup --subscription $SubscriptionId --output none 2>$null
if ($LASTEXITCODE -ne 0) {
  throw "No access to resource group '$ResourceGroup' in subscription '$SubscriptionId'. Activate PIM (Contributor) and retry."
}

Write-Host "Ensuring resource group exists..."
az group create --name $ResourceGroup --location $Location --output none

Write-Host "Ensuring storage account exists..."
az storage account create `
  --name $StorageAccountName `
  --resource-group $ResourceGroup `
  --location $Location `
  --sku Standard_LRS `
  --kind StorageV2 `
  --allow-blob-public-access false `
  --min-tls-version TLS1_2 `
  --output none
if ($LASTEXITCODE -ne 0) { throw "Failed to create/update storage account." }

if ($HostingModel -eq "premium") {
    if ([string]::IsNullOrWhiteSpace($AppServicePlanName)) {
    throw "AppServicePlanName is required when HostingModel is premium."
    }

    Write-Host "Ensuring App Service plan exists..."
    az functionapp plan create `
      --name $AppServicePlanName `
      --resource-group $ResourceGroup `
      --location $Location `
      --sku EP1 `
      --is-linux `
      --output none
    if ($LASTEXITCODE -ne 0) { throw "Failed to create/update App Service plan." }
}

$functionExists = az functionapp show --name $FunctionAppName --resource-group $ResourceGroup --output none 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating Function App..."
    if ($HostingModel -eq "flex") {
        az functionapp create `
          --name $FunctionAppName `
          --resource-group $ResourceGroup `
          --flexconsumption-location $Location `
          --runtime python `
          --runtime-version 3.11 `
          --functions-version 4 `
          --storage-account $StorageAccountName `
          --output none
    }
    elseif ($HostingModel -eq "consumption") {
    az functionapp create `
      --name $FunctionAppName `
      --resource-group $ResourceGroup `
      --consumption-plan-location $Location `
      --runtime python `
      --runtime-version 3.11 `
      --functions-version 4 `
      --storage-account $StorageAccountName `
      --os-type Linux `
      --output none
  }
    else {
    az functionapp create `
      --name $FunctionAppName `
      --resource-group $ResourceGroup `
      --plan $AppServicePlanName `
      --runtime python `
      --runtime-version 3.11 `
      --functions-version 4 `
      --storage-account $StorageAccountName `
      --os-type Linux `
      --output none
  }
  if ($LASTEXITCODE -ne 0) { throw "Failed to create Function App." }
} else {
    Write-Host "Function App already exists."
}

Write-Host "Enabling system-assigned managed identity..."
az functionapp identity assign --name $FunctionAppName --resource-group $ResourceGroup --output none
if ($LASTEXITCODE -ne 0) { throw "Failed to enable managed identity." }

Write-Host "Configuring app settings..."
$settings = @(
    "KUSTO_CLUSTER_URL=$KustoClusterUrl",
    "KUSTO_DATABASE=$KustoDatabase",
    "SA_OUTPUT_RAW_BASE_URL=$SaOutputRawBaseUrl",
  "KUSTO_AUTH_MODE=$KustoAuthMode"
)

if ($HostingModel -ne "flex") {
  $settings += "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
  $settings += "ENABLE_ORYX_BUILD=true"
}

if ($ManagedIdentityClientId -ne "") {
    $settings += "MANAGED_IDENTITY_CLIENT_ID=$ManagedIdentityClientId"
}

az functionapp config appsettings set `
  --name $FunctionAppName `
  --resource-group $ResourceGroup `
  --settings $settings `
  --output none
if ($LASTEXITCODE -ne 0) { throw "Failed to configure app settings." }

Write-Host "Packaging Function App for zip deployment..."
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$uploaderPath = Join-Path (Split-Path -Parent (Split-Path -Parent $scriptDir)) "upload_to_kusto.py"
if (-not (Test-Path $uploaderPath)) {
    throw "upload_to_kusto.py not found at expected path: $uploaderPath"
}

$packageRoot = Join-Path $env:TEMP ("sa-func-package-" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $packageRoot -Force | Out-Null

Copy-Item -Path (Join-Path $scriptDir "host.json") -Destination (Join-Path $packageRoot "host.json") -Force
Copy-Item -Path (Join-Path $scriptDir "function_app.py") -Destination (Join-Path $packageRoot "function_app.py") -Force
Copy-Item -Path (Join-Path $scriptDir "requirements.txt") -Destination (Join-Path $packageRoot "requirements.txt") -Force
Copy-Item -Path $uploaderPath -Destination (Join-Path $packageRoot "upload_to_kusto.py") -Force

$zipPath = Join-Path $env:TEMP ("sa-func-package-" + [guid]::NewGuid().ToString() + ".zip")
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $packageRoot "*") -DestinationPath $zipPath -Force

Write-Host "Deploying package with az functionapp deploy..."
az functionapp deploy `
  --name $FunctionAppName `
  --resource-group $ResourceGroup `
  --src-path $zipPath `
  --type zip `
  --output none
if ($LASTEXITCODE -ne 0) { throw "Function app deploy failed." }

Write-Host "Syncing function triggers..."
$syncUrl = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.Web/sites/$FunctionAppName/syncfunctiontriggers?api-version=2022-03-01"
az rest --method post --url $syncUrl --output none
if ($LASTEXITCODE -ne 0) { throw "Failed to sync function triggers via ARM REST." }

Remove-Item -Path $packageRoot -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $zipPath -Force -ErrorAction SilentlyContinue

$identityPrincipalId = az functionapp identity show --name $FunctionAppName --resource-group $ResourceGroup --query principalId -o tsv
Write-Host "\nDeployment complete."
Write-Host "Function principalId: $identityPrincipalId"
Write-Host "\nNext: grant Kusto permissions using grant_kusto_permissions.kql"
