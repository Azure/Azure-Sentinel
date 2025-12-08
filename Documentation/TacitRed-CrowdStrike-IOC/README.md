# TacitRed CrowdStrike IOC - Solution Documentation

## Overview
**TacitRed CrowdStrike IOC** is an automation solution (Playbook) that bridges **TacitRed** and **CrowdStrike Falcon**. It takes confirmed threat indicators discovered by TacitRed and automatically pushes them to the CrowdStrike IOC Management API, enabling immediate blocking or detecting on endpoints.

## Capabilities
- **Bidirectional-style Sync**: Fetches from TacitRed -> Pushes to CrowdStrike.
- **Automated Containment**: Reduces mean time to respond (MTTR) by blocking threats on endpoints as soon as they are detected by TacitRed.
- **Tagging**: Applies custom tags (e.g., "TacitRed", "Compromised") to indicators in CrowdStrike.

## Purpose
To automate the loop between external threat intelligence (TacitRed) and endpoint protection (CrowdStrike), removing the need for manual CSV uploads or copy-pasting of hash/IP/domain indicators.

## Support & Contact
- **Publisher**: Data443 Risk Mitigation, Inc.
- **Website**: [https://www.data443.com](https://www.data443.com)
- **Support Email**: [support@data443.com](mailto:support@data443.com)
- **Product Page**: [TacitRed](https://www.data443.com/products/tacitred/)

## How to Run / Deploy Manually

### Prerequisites
1.  **TacitRed API Key**.
2.  **CrowdStrike API Client ID & Secret**: Must have permissions to write to IOCs.
3.  **Active Playbook Permission**: The Logic App Managed Identity may need permissions.

### Manual Deployment via Azure Portal
1.  Use **"Deploy a custom template"** with `Package/mainTemplate.json`.
2.  Provide the TacitRed Key and CrowdStrike API Credentials.
3.  Once deployed, authorize the API connections in the Logic App designer if necessary (though this template uses HTTP actions, so likely just keys are needed).

### Manual Deployment via PowerShell
```powershell
New-AzResourceGroupDeployment -ResourceGroupName "YourResourceGroup" `
    -TemplateFile "Package/mainTemplate.json" `
    -TacitRed_ApiKey "..." `
    -CrowdStrike_ClientId "..." `
    -CrowdStrike_ClientSecret "..."
```

## Pull Request
- **PR #13241**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13241)
- **Status**: Active / In Review
