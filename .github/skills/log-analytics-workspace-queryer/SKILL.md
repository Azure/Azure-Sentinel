---
name: log-analytics-workspace-queryer
description: Uses REST API to query Log Analytics workspaces. Use this skill when you need to query a Log Analytics workspace, for example, to check if the table exists in the workspace, or to validate an ASIM parser.
---

# Query Log Analytics workspace using REST API

## Inputs
This skill requires two inputs. This information should come from another skill and you do not need to ask the user for it.
- **KQL query** — the query to run against the Log Analytics workspace.
- **Workspace ID** — the GUID of the Log Analytics workspace.

## Step 1: Verify Azure CLI authentication
Before querying, verify the user is authenticated by running `az account show`. If this fails, ask the user to run `az login` before continuing.

## Step 2: Run the query
Use the following PowerShell script to execute the KQL query against the workspace. Replace `<kql query>` and `<workspaceId>` with the actual values.

```powershell
## 1. Declare the query
$query = <kql query that needs to be run against the Log Analytics workspace>

## 2. Write payload to file (avoids all shell-escaping issues)
$payload = @{query = $query} | ConvertTo-Json -Depth 5 -Compress
[System.IO.File]::WriteAllText("$env:TEMP\la_query.json", $payload, [System.Text.Encoding]::UTF8)

## 3. Get access token
$token = (az account get-access-token --resource https://api.loganalytics.io --query accessToken -o tsv)
if (-not $token) {
    Write-Error "Failed to get access token. Ensure you are logged in with 'az login'."
    return
}

## 4. POST via Invoke-WebRequest
$resp = Invoke-WebRequest -Method Post `
  -Uri "https://api.loganalytics.io/v1/workspaces/<workspaceId>/query" `
  -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
  -Body ([System.IO.File]::ReadAllBytes("$env:TEMP\la_query.json")) `
  -SkipHttpErrorCheck

## 5. Parse and display results
if ($resp.StatusCode -eq 200) {
    $tables = ($resp.Content | ConvertFrom-Json).tables
    $columns = $tables[0].columns
    $rows = $tables[0].rows
    if ($rows.Count -gt 100) {
        Write-Host "Showing first 100 of $($rows.Count) rows."
        $rows = $rows | Select-Object -First 100
    }
    $rows | ForEach-Object {
        $row = $_
        $obj = [ordered]@{}
        for ($i = 0; $i -lt $columns.Count; $i++) {
            $obj[$columns[$i].name] = $row[$i]
        }
        [PSCustomObject]$obj
    } | Format-Table -AutoSize
} else {
    ($resp.Content | ConvertFrom-Json).error.innererror | ConvertTo-Json -Depth 4
}
```

## Step 3: Return results
Return the full query output to the calling skill. The calling skill is responsible for interpreting and filtering the results (e.g., filtering for Error or Warning patterns during ASIM validation).