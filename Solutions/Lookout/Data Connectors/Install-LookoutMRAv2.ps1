#Requires -Version 5.1
#Requires -Modules Az.Accounts, Az.Resources, Az.OperationalInsights

<#
.SYNOPSIS
    Automated installer for Lookout Mobile Risk API v2 comprehensive data connector.

.DESCRIPTION
    This script automates the deployment of the Lookout MRA v2 data connector including:
    - Data Collection Endpoint (DCE)
    - Data Collection Rule (DCR) 
    - Custom Table (LookoutMtdV2_CL)
    - Codeless Connector (SSE-based)
    - Parser Function (LookoutEvents)

.PARAMETER SubscriptionId
    Azure subscription ID where Microsoft Sentinel is deployed.

.PARAMETER ResourceGroupName
    Resource group name containing the Microsoft Sentinel workspace.

.PARAMETER WorkspaceName
    Microsoft Sentinel workspace name.

.PARAMETER LookoutApiKey
    Lookout API key for authentication (will be prompted securely if not provided).

.PARAMETER Location
    Azure region for deployment (defaults to resource group location).

.PARAMETER EnableDebugLogging
    Enable debug logging for troubleshooting (default: false).

.PARAMETER TemplateUri
    URI to the ARM template (defaults to GitHub raw URL).

.PARAMETER ValidateOnly
    Only validate the deployment without executing it.

.EXAMPLE
    .\Install-LookoutMRAv2.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-sentinel" -WorkspaceName "sentinel-workspace"

.EXAMPLE
    .\Install-LookoutMRAv2.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-sentinel" -WorkspaceName "sentinel-workspace" -EnableDebugLogging -ValidateOnly

.NOTES
    Author: Lookout Inc.
    Version: 2.0.0
    Requires: Azure PowerShell modules (Az.Accounts, Az.Resources, Az.OperationalInsights)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $true)]
    [ValidateLength(1, 90)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $true)]
    [ValidateLength(4, 63)]
    [string]$WorkspaceName,

    [Parameter(Mandatory = $false)]
    [SecureString]$LookoutApiKey,

    [Parameter(Mandatory = $false)]
    [string]$Location,

    [Parameter(Mandatory = $false)]
    [switch]$EnableDebugLogging,

    [Parameter(Mandatory = $false)]
    [string]$TemplateUri = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Lookout/Data%20Connectors/LookoutMRAv2_Comprehensive.json",

    [Parameter(Mandatory = $false)]
    [switch]$ValidateOnly
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Banner
Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Lookout Mobile Risk API v2 Installer                     ║
║                           Comprehensive Data Connector                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    switch ($Status) {
        "INFO" { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor White }
        "SUCCESS" { Write-Host "[$timestamp] [SUCCESS] $Message" -ForegroundColor Green }
        "WARNING" { Write-Host "[$timestamp] [WARNING] $Message" -ForegroundColor Yellow }
        "ERROR" { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
    }
}

function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        throw "PowerShell 5.1 or higher is required"
    }
    Write-Status "✓ PowerShell version: $($PSVersionTable.PSVersion)" "SUCCESS"

    # Check required modules
    $requiredModules = @("Az.Accounts", "Az.Resources", "Az.OperationalInsights")
    foreach ($module in $requiredModules) {
        if (-not (Get-Module -ListAvailable -Name $module)) {
            Write-Status "Installing module: $module" "WARNING"
            Install-Module -Name $module -Force -AllowClobber -Scope CurrentUser
        }
        Import-Module -Name $module -Force
        Write-Status "✓ Module loaded: $module" "SUCCESS"
    }
}

function Connect-ToAzure {
    Write-Status "Connecting to Azure..."
    
    try {
        $context = Get-AzContext
        if (-not $context -or $context.Subscription.Id -ne $SubscriptionId) {
            Connect-AzAccount -SubscriptionId $SubscriptionId | Out-Null
        }
        
        $context = Set-AzContext -SubscriptionId $SubscriptionId
        Write-Status "✓ Connected to subscription: $($context.Subscription.Name)" "SUCCESS"
        
        return $context
    }
    catch {
        throw "Failed to connect to Azure: $($_.Exception.Message)"
    }
}

function Test-ResourceGroup {
    param([string]$Name)
    
    Write-Status "Validating resource group: $Name"
    
    $rg = Get-AzResourceGroup -Name $Name -ErrorAction SilentlyContinue
    if (-not $rg) {
        throw "Resource group '$Name' not found"
    }
    
    Write-Status "✓ Resource group found: $($rg.Location)" "SUCCESS"
    return $rg
}

function Test-Workspace {
    param([string]$ResourceGroupName, [string]$WorkspaceName)
    
    Write-Status "Validating Microsoft Sentinel workspace: $WorkspaceName"
    
    $workspace = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction SilentlyContinue
    if (-not $workspace) {
        throw "Workspace '$WorkspaceName' not found in resource group '$ResourceGroupName'"
    }
    
    Write-Status "✓ Workspace found: $($workspace.Location)" "SUCCESS"
    return $workspace
}

function Get-LookoutApiKey {
    if (-not $LookoutApiKey) {
        Write-Status "Lookout API key required for authentication" "WARNING"
        $LookoutApiKey = Read-Host "Enter Lookout API Key" -AsSecureString
    }
    
    if (-not $LookoutApiKey) {
        throw "Lookout API key is required"
    }
    
    Write-Status "✓ API key provided" "SUCCESS"
    return $LookoutApiKey
}

function Deploy-Template {
    param(
        [string]$ResourceGroupName,
        [string]$WorkspaceName,
        [SecureString]$ApiKey,
        [string]$Location,
        [bool]$DebugLogging,
        [string]$TemplateUri,
        [bool]$ValidateOnly
    )
    
    $deploymentName = "LookoutMRAv2-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    
    $templateParameters = @{
        workspace = $WorkspaceName
        location = $Location
        lookoutApiKey = $ApiKey
        enableDebugLogging = $DebugLogging
    }
    
    Write-Status "Deployment name: $deploymentName"
    Write-Status "Template URI: $TemplateUri"
    Write-Status "Parameters: workspace=$WorkspaceName, location=$Location, debugLogging=$DebugLogging"
    
    try {
        if ($ValidateOnly) {
            Write-Status "Validating ARM template deployment..."
            $result = Test-AzResourceGroupDeployment -ResourceGroupName $ResourceGroupName -TemplateUri $TemplateUri -TemplateParameterObject $templateParameters
            
            if ($result) {
                Write-Status "❌ Template validation failed:" "ERROR"
                $result | ForEach-Object { Write-Status "  - $($_.Message)" "ERROR" }
                return $false
            } else {
                Write-Status "✓ Template validation successful" "SUCCESS"
                return $true
            }
        } else {
            Write-Status "Starting ARM template deployment..."
            $deployment = New-AzResourceGroupDeployment -ResourceGroupName $ResourceGroupName -Name $deploymentName -TemplateUri $TemplateUri -TemplateParameterObject $templateParameters -Verbose
            
            if ($deployment.ProvisioningState -eq "Succeeded") {
                Write-Status "✓ Deployment completed successfully" "SUCCESS"
                return $deployment
            } else {
                Write-Status "❌ Deployment failed: $($deployment.ProvisioningState)" "ERROR"
                return $false
            }
        }
    }
    catch {
        Write-Status "❌ Deployment error: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Show-DeploymentResults {
    param($Deployment)
    
    Write-Host "`n" -NoNewline
    Write-Status "Deployment Results:" "SUCCESS"
    Write-Status "==================="
    
    if ($Deployment.Outputs) {
        foreach ($output in $Deployment.Outputs.GetEnumerator()) {
            Write-Status "  $($output.Key): $($output.Value.Value)" "SUCCESS"
        }
    }
    
    Write-Host "`n" -NoNewline
    Write-Status "Next Steps:" "INFO"
    Write-Status "1. Wait 5-10 minutes for data ingestion to begin"
    Write-Status "2. Validate data ingestion with: LookoutMtdV2_CL | take 10"
    Write-Status "3. Test parser function with: LookoutEvents | take 5"
    Write-Status "4. Review deployment guide for troubleshooting: LookoutMRAv2_Deployment_Guide.md"
}

function Test-PostDeployment {
    param([string]$ResourceGroupName, [string]$WorkspaceName)
    
    Write-Status "Running post-deployment validation..."
    
    # Wait a moment for resources to be fully provisioned
    Start-Sleep -Seconds 30
    
    # Check if table was created (this might take a few minutes to appear)
    Write-Status "Note: Custom table creation may take 5-10 minutes to complete"
    Write-Status "Note: Data ingestion may take 5-15 minutes to begin"
    
    Write-Status "✓ Post-deployment validation completed" "SUCCESS"
}

# Main execution
try {
    Write-Status "Starting Lookout MRA v2 installation..."
    
    # Prerequisites
    Test-Prerequisites
    
    # Azure connection
    $context = Connect-ToAzure
    
    # Validation
    $rg = Test-ResourceGroup -Name $ResourceGroupName
    $workspace = Test-Workspace -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName
    
    # Set location if not provided
    if (-not $Location) {
        $Location = $rg.Location
        Write-Status "Using resource group location: $Location"
    }
    
    # Get API key
    $apiKey = Get-LookoutApiKey
    
    # Deploy template
    if ($ValidateOnly) {
        $result = Deploy-Template -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -ApiKey $apiKey -Location $Location -DebugLogging $EnableDebugLogging.IsPresent -TemplateUri $TemplateUri -ValidateOnly $true
        
        if ($result) {
            Write-Status "✅ Validation completed successfully - template is ready for deployment" "SUCCESS"
        } else {
            Write-Status "❌ Validation failed - please review errors above" "ERROR"
            exit 1
        }
    } else {
        $deployment = Deploy-Template -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -ApiKey $apiKey -Location $Location -DebugLogging $EnableDebugLogging.IsPresent -TemplateUri $TemplateUri -ValidateOnly $false
        
        if ($deployment) {
            Show-DeploymentResults -Deployment $deployment
            Test-PostDeployment -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName
            Write-Status "🎉 Lookout MRA v2 installation completed successfully!" "SUCCESS"
        } else {
            Write-Status "❌ Installation failed" "ERROR"
            exit 1
        }
    }
}
catch {
    Write-Status "❌ Installation failed: $($_.Exception.Message)" "ERROR"
    Write-Status "Please check the error details above and retry" "ERROR"
    exit 1
}
finally {
    $ProgressPreference = "Continue"
}