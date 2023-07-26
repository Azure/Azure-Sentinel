param ($adoToken, $adoBaseUrl, $adoAreaPath, $adoTeamProject, $prNumber, $prTitle, $dataFileLink, $adoParentLink, $instrumentationKey)
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1

try
{
    Write-Host "adoBaseUrl $adoBaseUrl, adoAreaPath $adoAreaPath, adoTeamProject $adoTeamProject, prNumber $prNumber, prTitle $prTitle, dataFileLink $dataFileLink, adoParentLink $adoParentLink"

    $customProperties = @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'="$prNumber"; 'EventName'="CreateADOItem"; 'dataFileLink'="$dataFileLink"; 'prTitle'="$prTitle"; } 
    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "CreateADOItem" -CustomProperties $customProperties

        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for CreateADOItem started for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties 
    }
    $pair = "$(''):$($adoToken)"
    $encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))
    $basicAuthValue = "Basic $encodedCreds"

    # CHECK IF ADO ITEM ALREADY EXIST
    $queryHeaders = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $queryHeaders.Add("Content-Type", "application/json")
    $queryHeaders.Add("Authorization", $basicAuthValue)

    $adoTitle = "Bug: " + $prNumber + ": " + $prTitle + ""
    $body = "
    {
        `"query`": `"Select [System.Id], [System.Title], [System.State], [Custom.GitHubId], [Custom.ICMId], [System.History] From WorkItems Where ([System.WorkItemType] = 'Product Backlog Item' OR [System.WorkItemType] = 'Bug') AND System.Title ='$adoTitle'`"
    }"

    $uri = $adoBaseUrl + "wiql?api-version=6"
    $queryResponse = Invoke-RestMethod -Uri $uri -Method 'POST' -Headers $queryHeaders -Body $body
    $resultQueryResponse = $queryResponse | ConvertTo-Json -Depth 5
    if ($queryResponse.workItems.count -eq 0)
    {
        $customProperties = @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'="$prNumber"; 'EventName'="CreateADOItem"; 'dataFileLink'="$dataFileLink"; 'prTitle'="$prTitle"; 'ADOQueryResponse'="$resultQueryResponse"; } 

        if ($instrumentationKey -ne '')
        {
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CreateADOItem : There are no workitems created in ADO which matches title $adoTitle for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties 
        }
        # create ado item
        $pullRequestLink = "https://github.com/Azure/Azure-Sentinel/pull/$prNumber"
        Write-Host "pullRequestLink $pullRequestLink"
        if ($dataFileLink -eq '' -or $null -eq $dataFileLink)
        {
            $body = '[
                { "value": "'+ $adoAreaPath +'", "path": "/fields/System.AreaPath", "op": "add" },
                { "value": "'+ $adoTeamProject +'", "path": "/fields/System.TeamProject", "op": "add" },
                { "value": "Product Backlog Item", "path": "/fields/System.WorkitemType", "op": "add" },
                { "value": "New", "path": "/fields/System.State", "op": "add" },
                { "value": "GitHub PR", "path": "/fields/Custom.WorkitemType", "op": "add" },
                { "value": "'+ $adoTitle +'", "path": "/fields/System.Title", "op": "add" },
                { "value": "'+ $prNumber +'", "path": "/fields/Custom.GitHubId", "op": "add" },
                { "value": "<div><p><span style=\"color: red;\"> <strong>An error has encountered in Github workflow!</strong></span></p><br/> Github PR #'+ $prNumber +' <br/> <a href=\"'+ $pullRequestLink +'\">GitHub Pull Request Link</a>", "path": "/fields/System.Description", "op": "add" },
                { "value": "<div>Github PR #'+ $prNumber +' <br/><a href=\"'+ $pullRequestLink +'\">GitHub Pull Request Link</a>", "path": "/fields/System.History", "op": "add" },
                {"op": "add", "path": "/relations/-", "value": { "rel": "System.LinkTypes.Hierarchy-Reverse", "Url": "'+ $adoParentLink +'" }}
            ]'
        }
        else 
        {
            $body = '[
                { "value": "'+ $adoAreaPath +'", "path": "/fields/System.AreaPath", "op": "add" },
                { "value": "'+ $adoTeamProject +'", "path": "/fields/System.TeamProject", "op": "add" },
                { "value": "Product Backlog Item", "path": "/fields/System.WorkitemType", "op": "add" },
                { "value": "New", "path": "/fields/System.State", "op": "add" },
                { "value": "GitHub PR", "path": "/fields/Custom.WorkitemType", "op": "add" },
                { "value": "'+ $adoTitle +'", "path": "/fields/System.Title", "op": "add" },
                { "value": "<div><p><span style=\"color:red;\"> <strong>An error has encountered in Github workflow!</strong></span></p><br/>Github PR #'+ $prNumber +' <br/><a href=\"'+ $pullRequestLink +'\">GitHub Pull Request Link</a> </br> <a href=\"'+ $dataFileLink +'\">Data Input File Github Link</a></div>", "path": "/fields/System.Description", "op": "add" },
                { "value": "'+ $prNumber +'", "path": "/fields/Custom.GitHubId", "op": "add" },
                { "value": "<div>Github PR #'+ $prNumber +' <br/><a href=\"'+ $pullRequestLink +'\">GitHub Pull Request Link</a> </br> <a href=\"'+ $dataFileLink +'\">Data Input File Github Link</a></div>", "op": "add", "path": "/fields/System.History" },
                {"op": "add", "path": "/relations/-", "value": { "rel": "System.LinkTypes.Hierarchy-Reverse", "Url": "'+ $adoParentLink + '" }}
            ]'
        }

        Write-Host "Body $body"
        $postHeaders = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
        $postHeaders.Add("Accept", "application/vnd.github+json")
        $postHeaders.Add("Authorization", $basicAuthValue)
        $postHeaders.Add("Content-Type", "application/json-patch+json")

        $createADOUrl = $adoBaseUrl + 'workitems/$Task?api-version=6.0'
        $createResponse =Invoke-RestMethod $createADOUrl -Method 'POST' -Headers $postHeaders -Body $body

        $createResponseJson = $createResponse | ConvertTo-Json -Depth 5
        $newAdoId = $createResponse.id

        $customProperties = @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'="$prNumber"; 'EventName'="CreateADOItem"; 'dataFileLink'="$dataFileLink"; 'prTitle'="$prTitle"; 'ADOCreateResponse'="$createResponseJson" } 

        if ($instrumentationKey -ne '')
        {
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CreateADOItem : There are no workitems created in ADO which matches title $adoTitle for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties 
        }

        if ($null -eq $createResponse -or $createResponse -eq '')
        {
            Write-Host "ADO Create Response is empty"
            if ($instrumentationKey -ne '')
            {
                Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CreateADOItem : Failed to create ADO item for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties 
            }
        }
        else
        {
            Write-Host "Created ADO item with Id $newAdoId Successfully"
            if ($instrumentationKey -ne '')
            {
                Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CreateADOItem : Created ADO item with title '$adoTitle' Successfully for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties 
            }
        }
    }
    else 
    {
        Write-Host "ADO item already created!"
        $customProperties = @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'="$prNumber"; 'EventName'="CreateADOItem"; 'dataFileLink'="$dataFileLink"; 'prTitle'="$prTitle"; 'CreateADOResponse'="$resultQueryResponse"; }
        
        if ($instrumentationKey -ne '')
        {
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CreateADOItem : ADO item already exist with title '$adoTitle' for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties 
        }
    }
}
catch
{
    $errorInfo = $_.Exception
    Write-Host "CreateADOItem: Error occured in catch block. Error Info $errorInfo"
    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'="$pullRequestNumber"; 'ErrorDetails'="CreateADOItem : Error occured in catch block: $_"; 'EventName'="CreateADOItem"; 'SolutionOfferId'="$solutionOfferId";}
    }
    exit 1
}
