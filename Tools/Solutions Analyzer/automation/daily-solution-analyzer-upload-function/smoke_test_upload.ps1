param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $true)]
    [string]$FunctionAppName
)

$ErrorActionPreference = "Stop"

az account set --subscription $SubscriptionId | Out-Null

Write-Host "Triggering admin sync and checking function metadata..."
az functionapp sync-functions --name $FunctionAppName --resource-group $ResourceGroup --output none

Write-Host "Listing functions:"
az functionapp function list --name $FunctionAppName --resource-group $ResourceGroup --query "[].name" -o tsv

Write-Host "\nOpen Azure Portal -> Function App -> Functions -> daily_solution_analyzer_upload -> Run"
Write-Host "Then check logs in Monitor/App Insights for uploader stdout/stderr."
