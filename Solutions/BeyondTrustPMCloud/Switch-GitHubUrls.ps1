#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Switches GitHub URLs between production (Azure/Azure-Sentinel) and fork (jamos-bt/Azure-Sentinel) for testing.

.DESCRIPTION
    This script helps test package deployment by temporarily updating all GitHub URLs to point to your fork,
    then reverting them back after testing is complete.

.PARAMETER Mode
    'ToFork' - Changes Azure/Azure-Sentinel to jamos-bt/Azure-Sentinel
    'ToProduction' - Changes jamos-bt/Azure-Sentinel back to Azure/Azure-Sentinel

.EXAMPLE
    .\Switch-GitHubUrls.ps1 -Mode ToFork
    .\Switch-GitHubUrls.ps1 -Mode ToProduction
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('ToFork', 'ToProduction')]
    [string]$Mode
)

$solutionPath = $PSScriptRoot

if ($Mode -eq 'ToFork') {
    $oldOwner = 'Azure'
    $newOwner = 'jamos-bt'
    Write-Host "🔄 Switching URLs from $oldOwner to $newOwner..." -ForegroundColor Cyan
} else {
    $oldOwner = 'jamos-bt'
    $newOwner = 'Azure'
    Write-Host "🔄 Switching URLs from $oldOwner to $newOwner..." -ForegroundColor Cyan
}

$filesToUpdate = @(
    "README.md",
    "Data Connectors\README.md",
    "Data Connectors\BeyondTrustPMCloud_API_FunctionApp.json",
    "Data\Solution_BeyondTrustPMCloud.json",
    "Package\mainTemplate.json",
    "Package\createUiDefinition.json"
)

$filesUpdated = 0

foreach ($file in $filesToUpdate) {
    $filePath = Join-Path $solutionPath $file
    
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        $originalContent = $content
        
        # Replace github.com URLs
        $content = $content -replace "github\.com/$oldOwner/Azure-Sentinel", "github.com/$newOwner/Azure-Sentinel"
        
        # Replace raw.githubusercontent.com URLs
        $content = $content -replace "raw\.githubusercontent\.com/$oldOwner/Azure-Sentinel", "raw.githubusercontent.com/$newOwner/Azure-Sentinel"
        
        if ($content -ne $originalContent) {
            Set-Content -Path $filePath -Value $content -NoNewline
            Write-Host "  ✅ Updated: $file" -ForegroundColor Green
            $filesUpdated++
        } else {
            Write-Host "  ⏭️  No changes needed: $file" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ⚠️  File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n📊 Summary: Updated $filesUpdated file(s)" -ForegroundColor Cyan

if ($Mode -eq 'ToFork') {
    Write-Host "`n📝 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Regenerate the package: cd '$solutionPath' ; & 'C:\GitHub\Azure-Sentinel\Tools\Create-Azure-Sentinel-Solution\V3\createSolutionV3.ps1'" -ForegroundColor White
    Write-Host "  2. Commit changes: git add . ; git commit -m 'temp: update URLs for fork testing'" -ForegroundColor White
    Write-Host "  3. Push to fork: git push origin test-package-deployment" -ForegroundColor White
    Write-Host "  4. Test deployment via Azure Portal" -ForegroundColor White
    Write-Host "  5. When done, run: .\Switch-GitHubUrls.ps1 -Mode ToProduction" -ForegroundColor White
} else {
    Write-Host "`n📝 URLs restored to production. You can now:" -ForegroundColor Yellow
    Write-Host "  1. Discard the test branch: git checkout master ; git branch -D test-package-deployment" -ForegroundColor White
    Write-Host "  2. Or if you want to keep other changes, cherry-pick commits selectively" -ForegroundColor White
}
