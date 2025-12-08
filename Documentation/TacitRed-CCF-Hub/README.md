# TacitRed CCF Hub (Threat Intelligence) - Solution Documentation

## Overview
**TacitRed CCF Hub** (Cloud Connector Framework) is the core integration for streaming TacitRed threat intelligence data into **Azure Sentinel**. It creates entries in the `ThreatIntelligenceIndicator` table, allowing Sentinel analytics rules to correlate internal log data with external TacitRed findings.

## Capabilities
- **High-Volume Ingestion**: Efficiently processes thousands of indicators per hour via the CCF data connector.
- **Sentinel Native**: Populates the standard `ThreatIntelligenceIndicator` table.
- **Compromised Credentials**: Specifically focuses on compromised credential intelligence and botnet findings.

## Purpose
This solution is the primary "Data Connector" for TacitRed customers using Azure Sentinel. It turns raw intelligence into actionable rows in your SIEM.

## Support & Contact
- **Publisher**: Data443 Risk Mitigation, Inc.
- **Website**: [https://www.data443.com](https://www.data443.com)
- **Support Email**: [support@data443.com](mailto:support@data443.com)
- **Product Page**: [TacitRed](https://www.data443.com/products/tacitred/)

## How to Run / Deploy Manually

### Prerequisites
1.  **TacitRed API Key**.
2.  **Azure Sentinel Workspace**.

### Manual Deployment via Azure Portal
1.  Go to **Azure Sentinel** > **Content Hub**.
2.  (If published) Search for "TacitRed".
3.  (If manual) Use "Deploy a custom template" with `Package/mainTemplate.json`.

### Manual Deployment via PowerShell
```powershell
New-AzResourceGroupDeployment -ResourceGroupName "YourResourceGroup" `
    -TemplateFile "Package/mainTemplate.json" `
    -workspace "YourLogAnalyticsWorkspaceName"
```

## Pull Request
- **PR #13242**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13242)
- **Status**: Active / In Review
