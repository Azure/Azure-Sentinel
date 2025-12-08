# TacitRed Defender Threat Intelligence - Solution Documentation

## Overview
**TacitRed Defender Threat Intelligence** provides a seamless integration between TacitRed's high-fidelity threat intelligence and **Microsoft Defender for Endpoint**. This solution enables automated ingestion of TacitRed findings as IOCs (Indicators of Compromise) into your Defender environment, enhancing your threat detection and response capabilities.

## Capabilities
- **Automated Ingestion**: Periodically fetches compromised credentials and malware indicators from TacitRed.
- **Customizable Filtering**: Allows filtering findings by specific domains or severity levels.
- **Microsoft Defender Integration**: Post indicators directly to the Defender API for immediate blocking and alerting.
- **Sentinel Monitoring**: Provides logs and monitoring within Azure Sentinel for operational visibility.

## Purpose
This package is designed for Security Operations Centers (SOCs) that utilize both TacitRed (by Data443) for external threat intelligence and Microsoft Defender for Endpoint for endpoint protection. It bridges the gap by automating the operationalization of threat intel.

## Support & Contact
- **Publisher**: Data443 Risk Mitigation, Inc.
- **Website**: [https://www.data443.com](https://www.data443.com)
- **Support Email**: [support@data443.com](mailto:support@data443.com)
- **Product Page**: [TacitRed](https://www.data443.com/products/tacitred/)

## How to Run / Deploy Manually

### Prerequisites
1.  **TacitRed API Key**: You must have a valid API key from your TacitRed account.
2.  **Azure Subscription**: An active Azure subscription with permissions to deploy resources.
3.  **Microsoft Sentinel**: A Log Analytics workspace with Sentinel enabled (optional, but recommended).

### Manual Deployment via Azure Portal (Custom Template)
1.  Navigate to the [Azure Portal](https://portal.azure.com).
2.  Search for **"Deploy a custom template"**.
3.  Click **"Build your own template in the editor"**.
4.  Copy the contents of `Package/mainTemplate.json` and paste it into the editor.
5.  Click **Save**.
6.  Fill in the required parameters:
    -   `TacitRed_ApiKey`: Your API Key.
    -   `Workspace`: The name of your Log Analytics Workspace.
    -   `Location`: The region of your workspace.
7.  Click **Review + create** -> **Create**.

### Manual Deployment via PowerShell
```powershell
New-AzResourceGroupDeployment -ResourceGroupName "YourResourceGroup" `
    -TemplateFile "Package/mainTemplate.json" `
    -TacitRed_ApiKey "YOUR_API_KEY" `
    -workspace "YourLogAnalyticsWorkspaceName"
```

## Pull Request
- **PR #13247**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13247)
- **Status**: Submitted / Waiting for CI
