param(
    [Parameter(Mandatory = $true)]
    [string]$FunctionAppName,

    [Parameter(Mandatory = $true)]
    [string]$StorageAccountName,

    [string]$AppServicePlanName = "",

    [ValidateSet("flex", "consumption", "premium")]
    [string]$HostingModel = "flex",

    [string]$KustoClusterUrl = "https://dataacquisition.eastus.kusto.windows.net",
    [string]$KustoDatabase = "dataacquisition",
    [ValidateSet("managed-identity", "azure-cli")]
    [string]$KustoAuthMode = "managed-identity",
    [string]$ManagedIdentityClientId = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$deployScript = Join-Path $scriptDir "deploy_function.ps1"

$args = @{
  SubscriptionId = "2f0fdbc8-ab60-4386-af30-dd0fac77130e"
  ResourceGroup = "dataacquisition-rg"
  Location = "eastus"
  FunctionAppName = $FunctionAppName
  StorageAccountName = $StorageAccountName
  KustoClusterUrl = $KustoClusterUrl
  KustoDatabase = $KustoDatabase
  SaOutputRawBaseUrl = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/solution_analyzer_output/Tools/Solutions%20Analyzer"
  KustoAuthMode = $KustoAuthMode
  ManagedIdentityClientId = $ManagedIdentityClientId
  HostingModel = $HostingModel
}

if ($HostingModel -eq "premium") {
  if ([string]::IsNullOrWhiteSpace($AppServicePlanName)) {
    throw "AppServicePlanName is required when HostingModel is premium."
  }
  $args.AppServicePlanName = $AppServicePlanName
}

& $deployScript @args
