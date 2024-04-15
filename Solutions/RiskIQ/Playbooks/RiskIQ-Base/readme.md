# RiskIQ-Base

## Overview
This playbook creates a shared API Connection for all RiskIQ playbooks to leverage. This eases the configuration process for a user during deployment of the RiskIQ solution. In time, this base playbook may be extended to set more functionality. You will need your API credentials (email/secret) when configuring this playbook. Those can be found on your [account settings](https://community.riskiq.com/settings) page. For enterprise customers, it's preferred to use the "organization" credential pair, not the user. If you have trouble accessing your account or your credentials contact your account representative (support[@]riskiq.com).

## Deployment

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRiskIQ%2FPlaybooks%2FRiskIQ-Base%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRiskIQ%2FPlaybooks%2FRiskIQ-Base%2Fazuredeploy.json" target="_blank">
    <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

### Post-Deployment Instructions
After deploying the playbook, you must authorize the connections leveraged.

1. Visit the playbook resource.
2. Under "Development Tools" (located on the left), click "API Connections".
3. Ensure each connection has been authorized.

**Note: If you've deployed the [RiskIQ-Base](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/RiskIQ/Playbooks/RiskIQ-Base/azuredeploy.json) playbook, you will only need to authorize the Microsoft Sentinel connection.**