param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceId,

    [Parameter(Mandatory=$true)]
    [string]$Query
)

## 1. Write payload to file (avoids all shell-escaping issues)
$payload = @{query = $Query} | ConvertTo-Json -Depth 5 -Compress
[System.IO.File]::WriteAllText("$env:TEMP\la_query.json", $payload, [System.Text.Encoding]::UTF8)

## 2. Get access token
$token = (az account get-access-token --resource https://api.loganalytics.io --query accessToken -o tsv)
if (-not $token) {
    Write-Error "Failed to get access token. Ensure you are logged in with 'az login'."
    return
}

## 3. POST via Invoke-WebRequest
$resp = Invoke-WebRequest -Method Post `
  -Uri "https://api.loganalytics.io/v1/workspaces/$WorkspaceId/query" `
  -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
  -Body ([System.IO.File]::ReadAllBytes("$env:TEMP\la_query.json")) `
  -SkipHttpErrorCheck

## 5. Parse and display results
if ($resp.StatusCode -eq 200) {
    $tables = ($resp.Content | ConvertFrom-Json).tables
    $columns = $tables[0].columns
    $rows = $tables[0].rows
    $rowLimit = 500
    if ($rows.Count -gt $rowLimit) {
        Write-Host "Showing first $rowLimit of $($rows.Count) rows."
        $rows = $rows | Select-Object -First $rowLimit
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