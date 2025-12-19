# Lookout Mobile Risk API v2 - Quick Installation Guide

## 🚀 Automated Installers

Choose your preferred installation method:

### PowerShell Installer (Windows/PowerShell Core)

```powershell
# Download and run the PowerShell installer
.\Install-LookoutMRAv2.ps1 -SubscriptionId "your-subscription-id" -ResourceGroupName "your-rg" -WorkspaceName "your-workspace"
```

**Features:**
- ✅ Automatic prerequisite checking
- ✅ Azure PowerShell module installation
- ✅ Secure API key prompting
- ✅ Comprehensive validation
- ✅ Post-deployment verification

### Bash Installer (Linux/macOS)

```bash
# Make executable and run
chmod +x install-lookout-mrav2.sh
./install-lookout-mrav2.sh -s "your-subscription-id" -g "your-rg" -w "your-workspace"
```

**Features:**
- ✅ Azure CLI integration
- ✅ Automatic dependency installation
- ✅ Colored output and logging
- ✅ Validation mode support
- ✅ Cross-platform compatibility

## 📋 Quick Start Examples

### Basic Installation
```bash
# PowerShell
.\Install-LookoutMRAv2.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-sentinel" -WorkspaceName "sentinel-workspace"

# Bash
./install-lookout-mrav2.sh -s "12345678-1234-1234-1234-123456789012" -g "rg-sentinel" -w "sentinel-workspace"
```

### Installation with Debug Logging
```bash
# PowerShell
.\Install-LookoutMRAv2.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-sentinel" -WorkspaceName "sentinel-workspace" -EnableDebugLogging

# Bash
./install-lookout-mrav2.sh -s "12345678-1234-1234-1234-123456789012" -g "rg-sentinel" -w "sentinel-workspace" -d
```

### Validation Only (Dry Run)
```bash
# PowerShell
.\Install-LookoutMRAv2.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-sentinel" -WorkspaceName "sentinel-workspace" -ValidateOnly

# Bash
./install-lookout-mrav2.sh -s "12345678-1234-1234-1234-123456789012" -g "rg-sentinel" -w "sentinel-workspace" -v
```

## 🔧 Prerequisites

### Common Requirements
- ✅ Azure subscription with Microsoft Sentinel enabled
- ✅ Appropriate Azure permissions (Sentinel Contributor, Log Analytics Contributor)
- ✅ Lookout API key from Lookout console

### PowerShell Requirements
- ✅ PowerShell 5.1 or higher
- ✅ Azure PowerShell modules (auto-installed)

### Bash Requirements
- ✅ Azure CLI installed and configured
- ✅ jq for JSON processing (auto-installed)

## 📦 What Gets Deployed

Both installers deploy the comprehensive ARM template that includes:

1. **Data Collection Endpoint (DCE)** - Secure ingestion endpoint
2. **Data Collection Rule (DCR)** - Advanced KQL transformation with 60+ field extraction
3. **Custom Table** - LookoutMtdV2_CL with comprehensive schema
4. **Codeless Connector** - SSE-based streaming with OAuth2 authentication
5. **KQL Parser Function** - LookoutEvents function for normalized querying

## ✅ Post-Installation Validation

After installation, validate the deployment:

```kql
// Check if data is being ingested
LookoutMtdV2_CL
| take 10

// Test the parser function
LookoutEvents
| take 5

// Verify event types
LookoutMtdV2_CL
| summarize count() by event_type
```

## 🆘 Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure you have Sentinel Contributor and Log Analytics Contributor roles
2. **API Key Issues**: Verify your Lookout API key is valid and has proper permissions
3. **Resource Not Found**: Check subscription ID, resource group, and workspace names

### Getting Help

- **Detailed Guide**: See [`LookoutMRAv2_Deployment_Guide.md`](LookoutMRAv2_Deployment_Guide.md)
- **Lookout Support**: support@lookout.com
- **Azure Support**: [Azure Support Portal](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)

## 📁 Files Overview

| File | Description |
|------|-------------|
| [`LookoutMRAv2_Comprehensive.json`](LookoutMRAv2_Comprehensive.json) | Complete ARM template with all components |
| [`Install-LookoutMRAv2.ps1`](Install-LookoutMRAv2.ps1) | PowerShell automated installer |
| [`install-lookout-mrav2.sh`](install-lookout-mrav2.sh) | Bash automated installer |
| [`LookoutMRAv2_Deployment_Guide.md`](LookoutMRAv2_Deployment_Guide.md) | Comprehensive deployment documentation |
| [`README_Installation.md`](README_Installation.md) | This quick start guide |

---

**🎉 Ready to get started? Choose your installer and deploy Lookout MRA v2 in minutes!**