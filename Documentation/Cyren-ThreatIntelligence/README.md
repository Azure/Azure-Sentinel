# Cyren Threat Intelligence - Solution Documentation

## Overview
**Cyren Threat Intelligence** integrates Cyren's advanced threat data into **Azure Sentinel**. This solution utilizes the Cloud Connector Framework (CCF) to ingest high-fidelity indicators related to malware URLs, phishing domains, and IP reputation.

## Capabilities
- **Real-Time Feed**: Ingests Cyren's continuous stream of threat intelligence.
- **Sentinel Integration**: Populates the `ThreatIntelligenceIndicator` table.
- **Automated Polling**: Configurable polling interval to fetch new indicators automatically.

## Purpose
Enables organizations to leverage Cyren's global threat visibility within their Azure Sentinel SIEM for improved detection and correlation of network-based threats.

## Support & Contact
- **Publisher**: Data443 Risk Mitigation, Inc. (Acquirer of Cyren assets)
- **Website**: [https://www.data443.com](https://www.data443.com)
- **Support Email**: [support@data443.com](mailto:support@data443.com)
- **Product Page**: [Cyren URL Filtering](https://www.data443.com/products/cyren-url-filtering/)

## How to Run / Deploy Manually

### Prerequisites
1.  **Cyren API Credentials**: You need a valid API Key/Token from Cyren/Data443.
2.  **Azure Sentinel Workspace**.

### Manual Deployment via Azure Portal
1.  Search for **"Deploy a custom template"**.
2.  Load the `Package/mainTemplate.json` file.
3.  Enter your Cyren API credentials in the parameter fields.
4.  Select your workspace and deploy.

### Manual Deployment via PowerShell
```powershell
New-AzResourceGroupDeployment -ResourceGroupName "YourResourceGroup" `
    -TemplateFile "Package/mainTemplate.json" `
    -workspace "YourLogAnalyticsWorkspaceName" `
    -CyrenApiKey "YOUR_API_KEY"
```

## Pull Request
- **PR #13224**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13224)
- **Status**: Active / In Review
