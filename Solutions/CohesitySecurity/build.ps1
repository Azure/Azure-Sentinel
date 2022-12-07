$SolutionJsonPath = "Solution_CohesitySecurity.json"

$configPath = Join-Path -Path $PSScriptRoot -ChildPath "cohesity.config"
Get-Content "$configPath" | foreach-object -begin {$h=@{}} -process { $k = [regex]::split($_,'='); if(($k[0].CompareTo("") -ne 0) -and ($k[0].StartsWith("[") -ne $True)) { $h.Add($k[0], $k[1]) } }
$send_to_email_for_playbook = $h.Get_Item("send_to_email_for_playbook")
$cohesity_support_email = $h.Get_Item("cohesity_support_email")
$apiKey_string = $h.Get_Item("apiKey_string")

$sourceFile = Join-Path -Path $PSScriptRoot -ChildPath "Playbooks" | Join-Path -ChildPath "Incident_Email_Playbook" | Join-Path -ChildPath "azuredeploy.json"
((Get-Content -path $sourceFile -Raw) -replace 'send_to_email_for_playbook', $send_to_email_for_playbook) | Set-Content -Path $sourceFile
$sourceFile = Join-Path -Path $PSScriptRoot -ChildPath "SolutionMetadata.json"
((Get-Content -path $sourceFile -Raw) -replace 'cohesity_support_email', $cohesity_support_email) | Set-Content -Path $sourceFile
$sourceFile = Join-Path -Path $PSScriptRoot -ChildPath "Playbooks" | Join-Path -ChildPath "Incident_VM_Playbook" | Join-Path -ChildPath "azuredeploy.json"
((Get-Content -path $sourceFile -Raw) -replace 'apiKey_string', $apiKey_string) | Set-Content -Path $sourceFile

Invoke-Expression "$PSScriptRoot/build_one_solution.ps1 '$SolutionJsonPath'"
