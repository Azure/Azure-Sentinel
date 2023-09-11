## Globals ##
$CloudEnv = $Env:cloudEnv
$ResourceGroupName = $Env:resourceGroupName
$WorkspaceName = $Env:workspaceName
$WorkspaceId = $Env:workspaceId
$Directory = $Env:directory
$Creds = $Env:creds
$contentTypes = $Env:contentTypes
$contentTypeMapping = @{
    "AnalyticsRule"=@("Microsoft.OperationalInsights/workspaces/providers/alertRules", "Microsoft.OperationalInsights/workspaces/providers/alertRules/actions");
    "AutomationRule"=@("Microsoft.OperationalInsights/workspaces/providers/automationRules");
    "HuntingQuery"=@("Microsoft.OperationalInsights/workspaces/savedSearches");
    "Parser"=@("Microsoft.OperationalInsights/workspaces/savedSearches");
    "Playbook"=@("Microsoft.Web/connections", "Microsoft.Logic/workflows", "Microsoft.Web/customApis");
    "Workbook"=@("Microsoft.Insights/workbooks");
}
$sourceControlId = $Env:sourceControlId 
$rootDirectory = $Env:rootDirectory
$githubAuthToken = $Env:githubAuthToken
$githubRepository = $Env:GITHUB_REPOSITORY
$branchName = $Env:branch
$smartDeployment = $Env:smartDeployment
$newResourceBranch = $branchName + "-sentinel-deployment"
$csvPath = "$rootDirectory\.sentinel\tracking_table_$sourceControlId.csv"
$configPath = "$rootDirectory\sentinel-deployment.config"
$global:localCsvTablefinal = @{}
$global:updatedCsvTable = @{}
$global:parameterFileMapping = @{}
$global:prioritizedContentFiles = @()
$global:excludeContentFiles = @()

$guidPattern = '(\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)'
$namePattern = '([-\w\._\(\)]+)'
$sentinelResourcePatterns = @{
    "AnalyticsRule" = "/subscriptions/$guidPattern/resourceGroups/$namePattern/providers/Microsoft.OperationalInsights/workspaces/$namePattern/providers/Microsoft.SecurityInsights/alertRules/$namePattern"
    "AutomationRule" = "/subscriptions/$guidPattern/resourceGroups/$namePattern/providers/Microsoft.OperationalInsights/workspaces/$namePattern/providers/Microsoft.SecurityInsights/automationRules/$namePattern"
    "HuntingQuery" = "/subscriptions/$guidPattern/resourceGroups/$namePattern/providers/Microsoft.OperationalInsights/workspaces/$namePattern/savedSearches/$namePattern"
    "Parser" = "/subscriptions/$guidPattern/resourceGroups/$namePattern/providers/Microsoft.OperationalInsights/workspaces/$namePattern/savedSearches/$namePattern"
    "Playbook" = "/subscriptions/$guidPattern/resourceGroups/$namePattern/providers/Microsoft.Logic/workflows/$namePattern"
    "Workbook" = "/subscriptions/$guidPattern/resourceGroups/$namePattern/providers/Microsoft.Insights/workbooks/$namePattern"
}

if ([string]::IsNullOrEmpty($contentTypes)) {
    $contentTypes = "AnalyticsRule"
}

$metadataFilePath = "metadata.json"
@"
{
    "`$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "parentResourceId": {
            "type": "string"
        },
        "kind": {
            "type": "string"
        },
        "sourceControlId": {
            "type": "string"
        },
        "workspace": {
            "type": "string"
        },
        "contentId": {
            "type": "string"
        }
    },
    "variables": {
        "metadataName": "[concat(toLower(parameters('kind')), '-', parameters('contentId'))]"
    },
    "resources": [
        {
            "type": "Microsoft.OperationalInsights/workspaces/providers/metadata",
            "apiVersion": "2022-01-01-preview",
            "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',variables('metadataName'))]",
            "properties": {
                "parentId": "[parameters('parentResourceId')]",
                "kind": "[parameters('kind')]",
                "source": {
                    "kind": "SourceRepository",
                    "name": "Repositories",
                    "sourceId": "[parameters('sourceControlId')]"
                }
            }
        }
    ]
}
"@ | Out-File -FilePath $metadataFilePath 

$resourceTypes = $contentTypes.Split(",") | ForEach-Object { $contentTypeMapping[$_] } | ForEach-Object { $_.ToLower() }
$MaxRetries = 3
$secondsBetweenAttempts = 5

#Converts hashtable to string that can be set as content when pushing csv file
function ConvertTableToString {
    $output = "FileName, CommitSha`n"
    $global:updatedCsvTable.GetEnumerator() | ForEach-Object {
        $key = RelativePathWithBackslash $_.Key
        $output += "{0},{1}`n" -f $key, $_.Value
    }
    return $output
}

$header = @{
    "authorization" = "Bearer $githubAuthToken"
}

#Gets all files and commit shas using Get Trees API 
function GetGithubTree {
    $branchResponse = AttemptInvokeRestMethod "Get" "https://api.github.com/repos/$githubRepository/branches/$branchName" $null $null 3
    $treeUrl = "https://api.github.com/repos/$githubRepository/git/trees/" + $branchResponse.commit.sha + "?recursive=true"
    $getTreeResponse = AttemptInvokeRestMethod "Get" $treeUrl $null $null 3
    return $getTreeResponse
}

#Creates a table using the reponse from the tree api, creates a table 
function GetCommitShaTable($getTreeResponse) {
    $shaTable = @{}
    $getTreeResponse.tree | ForEach-Object {
        $truePath = AbsolutePathWithSlash $_.path
        if (([System.IO.Path]::GetExtension($_.path) -eq ".json") -or ($truePath -eq $configPath))
        {
            $shaTable.Add($truePath, $_.sha)
        }
    }
    return $shaTable
}

function PushCsvToRepo() {
    $content = ConvertTableToString
    $relativeCsvPath = RelativePathWithBackslash $csvPath
    $resourceBranchExists = git ls-remote --heads "https://github.com/$githubRepository" $newResourceBranch | wc -l 

    if ($resourceBranchExists -eq 0) {
        git switch --orphan $newResourceBranch
        git commit --allow-empty -m "Initial commit on orphan branch"
        git push -u origin $newResourceBranch
        New-Item -ItemType "directory" -Path ".sentinel"
    } else {
        git fetch > $null
        git checkout $newResourceBranch
    }
    
    Write-Output $content > $relativeCsvPath
    git add $relativeCsvPath
    git commit -m "Modified tracking table"
    git push -u origin $newResourceBranch
    git checkout $branchName
}

function ReadCsvToTable {
    $csvTable = Import-Csv -Path $csvPath
    $HashTable=@{}
    foreach($r in $csvTable)
    {
        $key = AbsolutePathWithSlash $r.FileName 
        $HashTable[$key]=$r.CommitSha
    }   
    return $HashTable    
}

function AttemptInvokeRestMethod($method, $url, $body, $contentTypes, $maxRetries) {
    $Stoploop = $false
    $retryCount = 0
    do {
        try {
            $result = Invoke-RestMethod -Uri $url -Method $method -Headers $header -Body $body -ContentType $contentTypes
            $Stoploop = $true
        }
        catch {
            if ($retryCount -gt $maxRetries) {
                Write-Host "[Error] API call failed after $retryCount retries: $_"
                $Stoploop = $true
            }
            else {
                Write-Host "[Warning] API call failed: $_.`n Conducting retry #$retryCount."
                Start-Sleep -Seconds 5
                $retryCount = $retryCount + 1
            }
        }
    }
    While ($Stoploop -eq $false)
    return $result
}

function AttemptAzLogin($psCredential, $tenantId, $cloudEnv) {
    $maxLoginRetries = 3
    $delayInSeconds = 30
    $retryCount = 1
    $stopTrying = $false
    do {
        try {
            Connect-AzAccount -ServicePrincipal -Tenant $tenantId -Credential $psCredential -Environment $cloudEnv | out-null;
            Write-Host "Login Successful"
            $stopTrying = $true
        }
        catch {
            if ($retryCount -ge $maxLoginRetries) {
                Write-Host "Login failed after $maxLoginRetries attempts."
                $stopTrying = $true
            }
            else {
                Write-Host "Login attempt failed, retrying in $delayInSeconds seconds."
                Start-Sleep -Seconds $delayInSeconds
                $retryCount++
            }
        }
    }
    while (-not $stopTrying)
}

function ConnectAzCloud {
    $RawCreds = $Creds | ConvertFrom-Json

    Clear-AzContext -Scope Process;
    Clear-AzContext -Scope CurrentUser -Force -ErrorAction SilentlyContinue;
    
    Add-AzEnvironment `
        -Name $CloudEnv `
        -ActiveDirectoryEndpoint $RawCreds.activeDirectoryEndpointUrl `
        -ResourceManagerEndpoint $RawCreds.resourceManagerEndpointUrl `
        -ActiveDirectoryServiceEndpointResourceId $RawCreds.activeDirectoryServiceEndpointResourceId `
        -GraphEndpoint $RawCreds.graphEndpointUrl | out-null;

    $servicePrincipalKey = ConvertTo-SecureString $RawCreds.clientSecret.replace("'", "''") -AsPlainText -Force
    $psCredential = New-Object System.Management.Automation.PSCredential($RawCreds.clientId, $servicePrincipalKey)

    AttemptAzLogin $psCredential $RawCreds.tenantId $CloudEnv
    Set-AzContext -Tenant $RawCreds.tenantId | out-null;
}

function AttemptDeployMetadata($deploymentName, $resourceGroupName, $templateObject) {
    $deploymentInfo = $null
    try {
        $deploymentInfo = Get-AzResourceGroupDeploymentOperation -DeploymentName $deploymentName -ResourceGroupName $ResourceGroupName -ErrorAction Ignore
    }
    catch {
        Write-Host "[Warning] Unable to fetch deployment info for $deploymentName, no metadata was created for the resources in the file. Error: $_"
        return
    }
    $deploymentInfo | Where-Object { $_.TargetResource -ne "" } | ForEach-Object {
        $resource = $_.TargetResource
        $sentinelContentKinds = GetContentKinds $resource
        if ($sentinelContentKinds.Count -gt 0) {
            $contentKind = ToContentKind $sentinelContentKinds $resource $templateObject
            $contentId = $resource.Split("/")[-1]
            try {
                New-AzResourceGroupDeployment -Name "md-$deploymentName" -ResourceGroupName $ResourceGroupName -TemplateFile $metadataFilePath `
                    -parentResourceId $resource `
                    -kind $contentKind `
                    -contentId $contentId `
                    -sourceControlId $sourceControlId `
                    -workspace $workspaceName `
                    -ErrorAction Stop | Out-Host
                Write-Host "[Info] Created metadata metadata for $contentKind with parent resource id $resource"
            }
            catch {
                Write-Host "[Warning] Failed to deploy metadata for $contentKind with parent resource id $resource with error $_"
            }
        }
    }
}

function GetContentKinds($resource) {
    return $sentinelResourcePatterns.Keys | Where-Object { $resource -match $sentinelResourcePatterns[$_] }
}

function ToContentKind($contentKinds, $resource, $templateObject) {
    if ($contentKinds.Count -eq 1) {
       return $contentKinds 
    }
    if ($null -ne $resource -and $resource.Contains('savedSearches')) {
       if ($templateObject.resources.properties.Category -eq "Hunting Queries") {
           return "HuntingQuery"
       }
       return "Parser"
    }
    return $null
}

function IsValidTemplate($path, $templateObject) {
    Try {
        if (DoesContainWorkspaceParam $templateObject) {
            Test-AzResourceGroupDeployment -ResourceGroupName $ResourceGroupName -TemplateFile $path -workspace $WorkspaceName
        }
        else {
            Test-AzResourceGroupDeployment -ResourceGroupName $ResourceGroupName -TemplateFile $path
        }

        return $true
    }
    Catch {
        Write-Host "[Warning] The file $path is not valid: $_"
        return $false
    }
}

function IsRetryable($deploymentName) {
    $retryableStatusCodes = "Conflict","TooManyRequests","InternalServerError","DeploymentActive"
    Try {
        $deploymentResult = Get-AzResourceGroupDeploymentOperation -DeploymentName $deploymentName -ResourceGroupName $ResourceGroupName -ErrorAction Stop
        return $retryableStatusCodes -contains $deploymentResult.StatusCode
    }
    Catch {
        return $false
    }
}

function IsValidResourceType($template) {
    try {
        $isAllowedResources = $true
        $template.resources | ForEach-Object { 
            $isAllowedResources = $resourceTypes.contains($_.type.ToLower()) -and $isAllowedResources
        }
    }
    catch {
        Write-Host "[Error] Failed to check valid resource type."
        $isAllowedResources = $false
    }
    return $isAllowedResources
}

function DoesContainWorkspaceParam($templateObject) {
    $templateObject.parameters.PSobject.Properties.Name -contains "workspace"
}

function AttemptDeployment($path, $parameterFile, $deploymentName, $templateObject) {
    Write-Host "[Info] Deploying $path with deployment name $deploymentName"

    $isValid = IsValidTemplate $path $templateObject
    if (-not $isValid) {
        return $false
    }
    $isSuccess = $false
    $currentAttempt = 0
    While (($currentAttempt -lt $MaxRetries) -and (-not $isSuccess)) 
    {
        $currentAttempt ++
        Try 
        {
            Write-Host "[Info] Deploy $path with parameter file: [$parameterFile]"
            if (DoesContainWorkspaceParam $templateObject) 
            {
                if ($parameterFile) {
                    New-AzResourceGroupDeployment -Name $deploymentName -ResourceGroupName $ResourceGroupName -TemplateFile $path -workspace $workspaceName -TemplateParameterFile $parameterFile -ErrorAction Stop | Out-Host
                }
                else 
                {
                    New-AzResourceGroupDeployment -Name $deploymentName -ResourceGroupName $ResourceGroupName -TemplateFile $path -workspace $workspaceName -ErrorAction Stop | Out-Host
                }
            }
            else 
            {
                if ($parameterFile) {
                    New-AzResourceGroupDeployment -Name $deploymentName -ResourceGroupName $ResourceGroupName -TemplateFile $path -TemplateParameterFile $parameterFile -ErrorAction Stop | Out-Host
                }
                else 
                {
                    New-AzResourceGroupDeployment -Name $deploymentName -ResourceGroupName $ResourceGroupName -TemplateFile $path -ErrorAction Stop | Out-Host
                }
            }
            AttemptDeployMetadata $deploymentName $ResourceGroupName $templateObject

            $isSuccess = $true
        }
        Catch [Exception] 
        {
            $err = $_
            if (-not (IsRetryable $deploymentName)) 
            {
                Write-Host "[Warning] Failed to deploy $path with error: $err"
                break
            }
            else 
            {
                if ($currentAttempt -le $MaxRetries) 
                {
                    Write-Host "[Warning] Failed to deploy $path with error: $err. Retrying in $secondsBetweenAttempts seconds..."
                    Start-Sleep -Seconds $secondsBetweenAttempts
                }
                else
                {
                    Write-Host "[Warning] Failed to deploy $path after $currentAttempt attempts with error: $err"
                }
            }
        }
    }
    return $isSuccess
}

function GenerateDeploymentName() {
    $randomId = [guid]::NewGuid()
    return "Sentinel_Deployment_$randomId"
}

#Load deployment configuration
function LoadDeploymentConfig() {
    Write-Host "[Info] load the deployment configuration from [$configPath]"
    $global:parameterFileMapping = @{}
    $global:prioritizedContentFiles = @()
    $global:excludeContentFiles = @()
    try {
        if (Test-Path $configPath) {
            $deployment_config = Get-Content $configPath | Out-String | ConvertFrom-Json
            $parameterFileMappings = @{}
            if ($deployment_config.parameterfilemappings) {
                $deployment_config.parameterfilemappings.psobject.properties | ForEach { $parameterFileMappings[$_.Name] = $_.Value }
            }
            $key = ($parameterFileMappings.Keys | ? { $_ -eq $workspaceId })
            if ($null -ne $key) {
                $parameterFileMappings[$key].psobject.properties | ForEach { $global:parameterFileMapping[$_.Name] = $_.Value }
            }
            if ($deployment_config.prioritizedcontentfiles) {
                $global:prioritizedContentFiles = $deployment_config.prioritizedcontentfiles
            }
            $excludeList = $global:parameterFileMapping.Values + $global:prioritizedcontentfiles
            if ($deployment_config.excludecontentfiles) {
                $excludeList = $excludeList + $deployment_config.excludecontentfiles
            }
            $global:excludeContentFiles = $excludeList | Where-Object { Test-Path (AbsolutePathWithSlash $_) }
        }
    }
    catch {
        Write-Host "[Warning] An error occurred while trying to load deployment configuration."
        Write-Host "Exception details: $_"
        Write-Host $_.ScriptStackTrace
    }
}

function filterContentFile($fullPath) {
	$temp = RelativePathWithBackslash $fullPath
	return $global:excludeContentFiles | ? {$temp.StartsWith($_, 'CurrentCultureIgnoreCase')}
}

function RelativePathWithBackslash($absolutePath) {
	return $absolutePath.Replace($rootDirectory + "\", "").Replace("\", "/")
}

function AbsolutePathWithSlash($relativePath) {
	return Join-Path -Path $rootDirectory -ChildPath $relativePath
}

#resolve parameter file name, return $null if there is none.
function GetParameterFile($path) {
    $index = RelativePathWithBackslash $path
    $key = ($global:parameterFileMapping.Keys | ? { $_ -eq $index })
    if ($key) {
        $mappedParameterFile = AbsolutePathWithSlash $global:parameterFileMapping[$key]
        if (Test-Path $mappedParameterFile) {
            return $mappedParameterFile
        }
    }

    $parameterFilePrefix = $path.TrimEnd(".json")
    
    $workspaceParameterFile = $parameterFilePrefix + ".parameters-$WorkspaceId.json"
    if (Test-Path $workspaceParameterFile) {
        return $workspaceParameterFile
    }
    
    $defaultParameterFile = $parameterFilePrefix + ".parameters.json"
    if (Test-Path $defaultParameterFile) {
        return $defaultParameterFile
    }
    
    return $null
}

function Deployment($fullDeploymentFlag, $remoteShaTable, $tree) {
    Write-Host "Starting Deployment for Files in path: $Directory"
    if (Test-Path -Path $Directory) 
    {
        $totalFiles = 0;
        $totalFailed = 0;
	      $iterationList = @()
        $global:prioritizedContentFiles | ForEach-Object  { $iterationList += (AbsolutePathWithSlash $_) }
        Get-ChildItem -Path $Directory -Recurse -Filter *.json -exclude *metadata.json, *.parameters*.json |
                        Where-Object { $null -eq ( filterContentFile $_.FullName ) } |
                        Select-Object -Property FullName |
                        ForEach-Object { $iterationList += $_.FullName }
        $iterationList | ForEach-Object {
            $path = $_
            Write-Host "[Info] Try to deploy $path"
            if (-not (Test-Path $path)) {
                Write-Host "[Warning] Skipping deployment for $path. The file doesn't exist."
                return
            }
            $templateObject = Get-Content $path | Out-String | ConvertFrom-Json
            if (-not (IsValidResourceType $templateObject))
            {
                Write-Host "[Warning] Skipping deployment for $path. The file contains resources for content that was not selected for deployment. Please add content type to connection if you want this file to be deployed."
                return
            }       
            $parameterFile = GetParameterFile $path
            $result = SmartDeployment $fullDeploymentFlag $remoteShaTable $path $parameterFile $templateObject
            if ($result.isSuccess -eq $false) {
                $totalFailed++
            }
            if (-not $result.skip) {
                $totalFiles++
            }
            if ($result.isSuccess -or $result.skip) {
                $global:updatedCsvTable[$path] = $remoteShaTable[$path]
                if ($parameterFile) {
                    $global:updatedCsvTable[$parameterFile] = $remoteShaTable[$parameterFile]
                }
            }
        }
        PushCsvToRepo
        if ($totalFiles -gt 0 -and $totalFailed -gt 0) 
        {
            $err = "$totalFailed of $totalFiles deployments failed."
            Throw $err
        }
    }
    else 
    {
        Write-Output "[Warning] $Directory not found. nothing to deploy"
    }
}

function SmartDeployment($fullDeploymentFlag, $remoteShaTable, $path, $parameterFile, $templateObject) {
    try {
        $skip = $false
        $isSuccess = $null
        if (!$fullDeploymentFlag) {
            $existingSha = $global:localCsvTablefinal[$path]
            $remoteSha = $remoteShaTable[$path]
            $skip = (($existingSha) -and ($existingSha -eq $remoteSha))
            if ($skip -and $parameterFile) {
                $existingShaForParameterFile = $global:localCsvTablefinal[$parameterFile]
                $remoteShaForParameterFile = $remoteShaTable[$parameterFile]
                $skip = (($existingShaForParameterFile) -and ($existingShaForParameterFile -eq $remoteShaForParameterFile))
            }
        }
        if (!$skip) {
            $deploymentName = GenerateDeploymentName
            $isSuccess = AttemptDeployment $path $parameterFile $deploymentName $templateObject    
        }
        return @{
            skip = $skip
            isSuccess = $isSuccess
        }
    }
    catch {
        Write-Host "[Error] An error occurred while trying to deploy file $path. Exception details: $_"
        Write-Host $_.ScriptStackTrace
    }
}

function TryGetCsvFile {
    if (Test-Path $csvPath) {
        $global:localCsvTablefinal = ReadCsvToTable
        Remove-Item -Path $csvPath
        git add $csvPath
        git commit -m "Removed tracking file and moved to new sentinel created branch"
        git push origin $branchName
    }

    $relativeCsvPath = RelativePathWithBackslash $csvPath
    $resourceBranchExists = git ls-remote --heads "https://github.com/$githubRepository" $newResourceBranch | wc -l 
    
    if ($resourceBranchExists -eq 1) {
        git fetch > $null
        git checkout $newResourceBranch
        
        if (Test-Path $relativeCsvPath) {
            $global:localCsvTablefinal = ReadCsvToTable
        }
        git checkout $branchName
    }
}

function main() {
    git config --global user.email "donotreply@microsoft.com"
    git config --global user.name "Sentinel"

    if ($CloudEnv -ne 'AzureCloud') 
    {
        Write-Output "Attempting Sign In to Azure Cloud"
        ConnectAzCloud
    }

    TryGetCsvFile
    LoadDeploymentConfig
    $tree = GetGithubTree
    $remoteShaTable = GetCommitShaTable $tree

    $existingConfigSha = $global:localCsvTablefinal[$configPath]
    $remoteConfigSha = $remoteShaTable[$configPath]
    $modifiedConfig = ($existingConfigSha -xor $remoteConfigSha) -or ($existingConfigSha -and $remoteConfigSha -and ($existingConfigSha -ne $remoteConfigSha))
    
    if ($remoteConfigSha) {
        $global:updatedCsvTable[$configPath] = $remoteConfigSha
    }

    $fullDeploymentFlag = $modifiedConfig -or ($smartDeployment -eq "false")
    Deployment $fullDeploymentFlag $remoteShaTable $tree
}

main