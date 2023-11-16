# MDTI-Base

## Overview
This playbook creates a shared Connection for all Microsoft Defender Threat Intelligence(MDTI) playbooks to leverage. This eases the configuration process for a user during deployment of the MDTI solution. In time, this base playbook may be extended to set more functionality. If you have trouble accessing your account or your credentials contact your account representative.

## Pre-deployment Instructions

1. Microsoft Entra ID App Registration credentials(ClientId/ClientSecret/TenantId) with MDTI API Permissions are needed when configuring this playbook. Please check here for instructions on creating an App Registration [Azure Client App](https://learn.microsoft.com/en-us/rest/api/azure/#register-your-client-application-with-azure-ad) page. 
2. MDTI API Permissions needed for the App registration is "ThreatIntelligence.Read.All" which needs to be granted consent by your Azure Tenant admin.
3. Also, all playbooks part of the MDTI Solution require "Microsoft Sentinel Contributor" role to update Incidents. 

MDTI API documentation for more details, [MDTI API](https://learn.microsoft.com/en-us/graph/api/resources/security-threatintelligence-overview?view=graph-rest-beta&branch=pr-en-us-20472)

If you have trouble accessing your account or your credentials contact your account representative or reach out to discussMDTI[@]microsoft.com.

## Deployment

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoft%2520Defender%2520Threat%2520Intelligence%2FPlaybooks%2FMDTI-Base%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoft%2520Defender%2520Threat%2520Intelligence%2FPlaybooks%2FMDTI-Base%2Fazuredeploy.json" target="_blank">
    <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

### Post-Deployment Instructions
After deploying the playbook, you must authorize the connections leveraged.

1. Visit the playbook resource.
2. Under "Development Tools" (located on the left), click "API Connections".
3. Ensure each connection has been authorized.

**Note: If you've deployed the [MDTI-Base](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Microsoft%20Defender%20Threat%20Intelligence/Playbooks/MDTI-Base/azuredeploy.json) playbook, you will only need to authorize the Microsoft Sentinel connection.**
