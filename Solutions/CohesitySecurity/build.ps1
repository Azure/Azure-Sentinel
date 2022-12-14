$SolutionJsonPath = "Solution_CohesitySecurity.json"

$configPath = Join-Path -Path $PSScriptRoot -ChildPath "cohesity.json"
$json = Get-Content -Raw $configPath | ConvertFrom-Json
$cohesity_support_email = $json.cohesity_support_email
$apiKey_string = $json.apiKey_string

$sourceFile = Join-Path -Path $PSScriptRoot -ChildPath "SolutionMetadata.json"
((Get-Content -path $sourceFile -Raw) -replace 'cohesity_support_email', $cohesity_support_email) | Set-Content -Path $sourceFile
$sourceFile = Join-Path -Path $PSScriptRoot -ChildPath "Playbooks" | Join-Path -ChildPath "Incident_VM_Playbook" | Join-Path -ChildPath "azuredeploy.json"
((Get-Content -path $sourceFile -Raw) -replace 'apiKey_string', $apiKey_string) | Set-Content -Path $sourceFile

Invoke-Expression "$PSScriptRoot/build_one_solution.ps1 '$SolutionJsonPath'"
