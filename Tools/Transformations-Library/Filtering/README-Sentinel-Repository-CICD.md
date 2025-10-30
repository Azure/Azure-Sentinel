# Sentinel Repository Deployment aka CI/CD

To be deployed through Sentinel Repository feature, you must add to pipeline a deployment for Microsoft.Insights/dataCollectionRules inside `.sentinel/azure*sentinel-deploy*.ps1`

```
$contentTypeMapping = @{
[...]
    "Watchlist" = @("Microsoft.OperationalInsights/workspaces/providers/Watchlists");
    "DCR" = @("Microsoft.Insights/dataCollectionRules");
    "Metadata"=@("Microsoft.OperationalInsights/workspaces/providers/metadata");
```

IsValidTemplate should validate json file with parameters:
```
function IsValidTemplate($path, $templateObject) {
[...]
        } ElseIf (($path -like "*DCR*") -and (Test-Path -Path $parameterFile)) {
            Write-Host "[Debug] IsValidTemplate() DCR path + params: $path, $parameterFile"
            Test-AzResourceGroupDeployment -ResourceGroupName $ResourceGroupName -TemplateFile $path -TemplateParameterFile $parameterFile -workspace $WorkspaceName
        }
```

The corresponding service principal "Azure Sentinel Content Deployment App (GUID)" should have following extra permissions:
* Microsoft.Insights/dataCollectionRules/write
* Microsoft.OperationalInsights/workspaces/sharedKeys/action
