# PR Analysis wrapper f     if ($SourcePath -and (Test-Path $SourcePath)) {
        Write-ColorOutput "🔍 Using custom PR source path for testing: $SourcePath" $yellow if ($SourcePath -and (Test-Path $SourcePath)) {
        Write-ColorOutput "🔍 Testing ASim parsers from custom source: $SourcePath" $yellow runAsimTesters.ps1
# This wrapper enables the original PowerShell script to analyze code from different directories
# by modifying paths and git operations to work with PR code in an isolated folder.

param(
    [Parameter(Mandatory=$false)]
    [string]$SourcePath = ""
)

# ANSI escape codes for colored output
$green = "`e[32m"
$yellow = "`e[33m"
$red = "`e[31m"
$reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $reset)
    Write-Host "$Color$Message$reset"
}

function Invoke-SecureAsimTests {
    param([string]$SourcePath)
    
    if ($SourcePath -and (Test-Path $SourcePath)) {
        Write-ColorOutput "� Analyzing code from: $SourcePath" $yellow
        
        # Read the original script content
        $originalScript = Get-Content "$PSScriptRoot\runAsimTesters.ps1" -Raw
        
        # Replace path references to point to the source directory
        $modifiedScript = $originalScript
        
        # Replace relative path references
        $modifiedScript = $modifiedScript -replace 
            '\$\(\$PSScriptRoot\)\/\.\.\/.\.\.\/\.\.\/Parsers\/',
            "$($SourcePath.Replace('\', '/'))/Parsers/"
        
        # Replace git commands to work in the source directory
        $modifiedScript = $modifiedScript -replace 
            'git diff --name-status upstream/master -- \$\(\$PSScriptRoot\)\/\.\.\/.\.\.\/\.\.\/Parsers\/',
            "git diff --name-status upstream/master -- $($SourcePath.Replace('\', '/'))/Parsers/"
        
        # Add source directory context to git operations
        $gitSetupCode = @"
# Setup git environment for source directory
Set-Location '$SourcePath'

# Check if upstream remote already exists in source directory
`$remoteExists = Invoke-Expression "git remote" | Select-String -Pattern "upstream"
if (-not `$remoteExists) {
    Write-Host "Adding upstream remote to source directory..."
    Invoke-Expression "git remote add upstream https://github.com/Azure/Azure-Sentinel.git"
}

# Fetch the latest changes from upstream repositories in source directory
Write-Host "Fetching latest changes from upstream in source directory..."
Invoke-Expression "git fetch upstream" *> `$null

"@
        
        # Insert the git setup code at the beginning of the run function
        $modifiedScript = $modifiedScript -replace 
            '(function run \{[\s\S]*?Write-Host "This is the script from PR\.")',
            "`$1`n$gitSetupCode"
        
        # Create a temporary script file
        $tempScriptPath = [System.IO.Path]::GetTempFileName() + ".ps1"
        $modifiedScript | Out-File -FilePath $tempScriptPath -Encoding UTF8
        
        try {
            # Execute the modified script
            & $tempScriptPath
        }
        finally {
            # Clean up the temporary file
            if (Test-Path $tempScriptPath) {
                Remove-Item $tempScriptPath -ErrorAction SilentlyContinue
            }
        }
    }
    else {
        Write-ColorOutput "📂 Testing ASim parsers from current repository" $green
        # Run the original script without modifications
        & "$PSScriptRoot\runAsimTesters.ps1"
    }
}

# Main execution
try {
    Write-ColorOutput "ASim Parser Test Runner" $green
    Write-ColorOutput "========================" $green
    
    Invoke-SecureAsimTests -SourcePath $SourcePath
    
    Write-ColorOutput "ASim parser tests completed successfully!" $green
}
catch {
    Write-ColorOutput "ASim parser tests failed: $_" $red
    exit 1
}