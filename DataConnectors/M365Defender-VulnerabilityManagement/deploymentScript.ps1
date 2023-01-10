param([string] $PackageUri, [string] $SubscriptionId, [string] $ResourceGroupName, [string] $FunctionAppName, [string] $FAScope, [string] $VnetScope, [string] $UAMIPrincipalId, [string] $RestrictedIPs)

Set-AzContext -Subscription $SubscriptionId

#Give Function App some time to fully finish provisioning.
Start-Sleep -Seconds 60

#Download Function App package and publish.
Invoke-WebRequest -Uri $PackageUri -OutFile functionPackage.zip
Publish-AzWebapp -ResourceGroupName $ResourceGroupName -Name $FunctionAppName -ArchivePath functionPackage.zip -Force

#Add IP restrictions on Function App if specified.
if ($RestrictedIPs -eq 'None') {
    $resource = Get-AzResource -ResourceType Microsoft.Web/sites -ResourceGroupName $ResourceGroupName -ResourceName $FunctionAppName
    $resource.Properties.publicNetworkAccess = 'Disabled'
    $resource | Set-AzResource -Force
}
elseif ($RestrictedIPs -ne '') {
    Add-AzWebAppAccessRestrictionRule -ResourceGroupName $ResourceGroupName -WebAppName $FunctionAppName `
        -Name "Allowed" -IpAddress $RestrictedIPs.Replace(' ', ',') -Priority 100 -Action Allow

    Add-AzWebAppAccessRestrictionRule -ResourceGroupName $ResourceGroupName -WebAppName $FunctionAppName `
        -Name "Allowed" -IpAddress $RestrictedIPs.Replace(' ', ',') -Priority 100 -Action Allow -TargetScmSite
}

#Cleanup the Service Principal Owner role assignments now that access is no longer needed.
Remove-AzRoleAssignment -ObjectId $UAMIPrincipalId -RoleDefinitionName Owner -Scope $FAScope
if ($VnetScope -ne '') { Remove-AzRoleAssignment -ObjectId $UAMIPrincipalId -RoleDefinitionName Owner -Scope $VnetScope }