$today = Get-Date -Format "MM-dd-yyyy"
$suffix = Get-Random -Maximum 100
$deploymentName = "_" + $today + "_$suffix"

Import-Module Az.Resources
New-AzResourceGroupDeployment -ResourceGroupName Soc -TemplateFile .\UserEnrichment.template.json -TemplateParameterFile ".\parameters.json" -Name "UserEnrichment_$deploymentName" -Verbose

New-AzResourceGroupDeployment -ResourceGroupName Soc -TemplateFile .\Get-AlertEntitiesEnrichment.json -Name "Get-AlertEntitiesEnrichment_$deploymentName" -Verbose