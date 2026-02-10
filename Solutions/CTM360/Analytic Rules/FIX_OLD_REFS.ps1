#!/usr/bin/env powershell
<#
Fix analytics rules by removing old table references from requiredDataConnectors
but keeping the connectorId
#>

$rulesDir = Get-Location
$fixed = 0
$failed = 0

Get-ChildItem "*.yaml" | ForEach-Object {
  $path = $_.FullName
  $content = Get-Content $path -Raw
  $newContent = $content
  
  # Pattern: requiredDataConnectors section with old table refs
  # Change from:
  #   requiredDataConnectors:
  #   - connectorId: XXX
  #     dataTypes:
  #     - TABLE_CL
  # To:
  #   requiredDataConnectors:
  #   - connectorId: XXX
  
  if ($content -match 'requiredDataConnectors:\s*\n\s*- connectorId:\s*(\w+)\s*\n\s*dataTypes:\s*\n\s*-\s*(CBSLog_Azure_1_CL|HackerViewLog_Azure_1_CL)') {
    $connectorId = $matches[1]
    # Replace the entire requiredDataConnectors section
    $newContent = $content -replace `
      "requiredDataConnectors:\s*\n\s*- connectorId:\s*$connectorId\s*\n\s*dataTypes:\s*\n\s*-\s*(CBSLog_Azure_1_CL|HackerViewLog_Azure_1_CL)", `
      "requiredDataConnectors:`n- connectorId: $connectorId"
    
    if ($newContent -ne $content) {
      Set-Content $path $newContent
      Write-Host "FIXED: $($_.Name)" -ForegroundColor Green
      $fixed++
    } else {
      Write-Host "FAILED: $($_.Name) (regex didn't match)" -ForegroundColor Red
      $failed++
    }
  }
}

Write-Host "`nSummary: Fixed $fixed rules, Failed $failed" -ForegroundColor Cyan
