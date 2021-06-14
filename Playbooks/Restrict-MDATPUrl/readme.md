# Restrict-MDATPUrl
author: Nathan Swift

This playbook will take URL entities and generate alert and block threat indicators for each URL in MDATP for 90 days.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRestrict-MDATPUrl%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRestrict-MDATPUrl%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

**Additional Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI) to authenticate and authorize against api.securitycenter.windows.com to update threat indicators.

The MSI must be assigned API Permissions 'Ti.ReadWrite' to WindowsDefenderATP App. To assign use PowerShell and AzureAD Module. Run the following commands:

`$msi= Get-AzureADServicePrincipal -Filter "displayname eq 'Restrict-MDATPUrl'"`

`$graph = Get-AzureADServicePrincipal -Filter "AppId eq 'fc780465-2017-40d4-a0c5-307022471b92'"`

`$roles = $graph.AppRoles | Where-Object {$_.Value -imatch "Ti.ReadWrite"}`

`Foreach ($role in $roles){`
`New-AzureADServiceAppRoleAssignment -ObjectId $msi.ObjectId -PrincipalId $msi.ObjectId -Id $role.Id -ResourceId $graph.ObjectId`
`}`