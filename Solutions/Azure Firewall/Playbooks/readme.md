# Azure Firewall Logic Apps connector and playbook templates

![Azure Firewall](./AzureFirewallConnector/AzureFirewallCustomConnector.png)<br>

## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 3 Playbook templates](#deployall)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)


<a name="overview">

## Overview
Azure Firewall is a cloud-based network security service, sitting at the edge of the Azure virtual network resources, to provide additional security beyond what is offered by NSGs. <br>
This integration allows to automate response to Microsoft Sentinel incidents which contains IPs. It contains the basic connector component, with which you can create your own playbooks that interact with Azure Firewall, Azure Firewall Policy and IP Groups. <br>
It also contains 3 playbook templates, ready to quick use, that allow direct response on Azure Firewall from Microsoft Teams together and VirusTotal enrichment.

The playbooks in this integration work with:

| **Playbook Name**                  | **Premium Policy** | **Standard Policy** | **Classic Rules** |
|------------------------------------|--------------------|---------------------|-------------------|
| AzureFirewall-BlockIP-addToIPGroup | Yes                | Yes | Yes |
| AzureFirewall-AddIPtoTIAllowList   | No                 | Yes | No |
| AzureFirewall-BlockIP-addNewRule   | No                 | No | Yes |

<a name="deployall">

## Deploy Custom Connector + 3 Playbook templates
This package includes:
* Custom connector for Azure Firewall
* Three playbook templates leverage Azure Firewall custom connector

You can choose to deploy the whole package: connector + all three playbook templates (below buttons), or each one seperately from it's specific folder.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAzure%2520Firewall%2FPlaybooks%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAzure%2520Firewall%2FPlaybooks%2Fazuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>


# Firewall connector documentation 

<a name="authentication">

## Authentication
This connector supports Service Principal authentication type.
### Azure Active Directory Service principal
To use your own application with the Microsoft Sentinel connector, perform the following steps:

1. Register the application with Azure AD and create a service principal. [Learn how](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#register-an-application-with-azure-ad-and-create-a-service-principal).

1. Get credentials (for future authentication).

    In the registered application blade, get the application credentials for later signing in:

    - Tenant Id: under **Overview**
    - Client ID: under **Overview**
    - Client secret: under **Certificates & secrets**.

1. Grant permissions to Azure Firewall, IP Groups or Azure Firewall Policies.

    - In the relevant resources of the above, go to Settings -> Access control (IAM)

    - Select **Add role assignment**.

    - Select the role you wish to assign to the application: **Contributor** role.

    - Find the required application and save. By default, Azure AD applications aren't displayed in the available options. To find your application, search for the name and select it.

1. Authenticate

    In this step we use the app credentials to authenticate to the Sentinel connector in Logic Apps.

    In the custom connector for Azure Firewall, fill in the required parameters (can be found in the registered application blade)
        - Tenant Id: under **Overview**
        - Client Id: under **Overview**
        - Client Secret: under **Certificates & secrets**

<a name="prerequisites">

### Prerequisites for using and deploying Custom Connector
1. Register an AAD app and capture the ClientID, SecretKey and TenantID
2. Playbook templates leverage VirusTotal for IP enrichment. To use this VirusTotal capabilities,generate a Virus Total API key. Refer this link [ how to generate the API Key](https://developers.virustotal.com/v3.0/reference#getting-started)

<a name="deployment">

### Deployment instructions 
1. Deploy the Custom Connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required parameteres:

| Parameters | Description |
|----------------|--------------|
|**Custom Connector name**| Enter the Custom connector name (e.g. AzureFirewallConnector)|
|**AzureFirewall-BlockIP-addNewRule Playbook Name**|  Enter the playbook name here (e.g. AzureFirewall-BlockIP-addNewRule)|
|**AzureFirewall-BlockIP-addToIPGroup Playbook Name** | Enter the playbook name here (e.g. AzureFirewall-BlockIP-addToIPGroup)| 
|**AzureFirewall-AddIPtoTIAllowList Playbook Name** |Enter the playbook name here (e.g. AzureFirewall-AddIPtoTIAllowList)|
|**Teams GroupId** | Enter the Teams channel id to send the adaptive card|
|**Teams ChannelId** | Enter the Teams Group id to send the adaptive card [Refer the below link to get the channel id and group id](https://docs.microsoft.com/powershell/module/teams/get-teamchannel?view=teams-ps)|
|**ClientId** | Enter the Client Id of the Service Principal which the custom connector will authenticate with|
|**ClientSecret** | Enter the Client secret of the Service Principal which the custom connector will authenticate with|
<a name="postdeployment">

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
 1. Click the Microsoft Sentinel connection resource
 2. Click edit API connection
 3. Click Authorize
 4. Sign in
 5. Click Save
 6. Repeat steps for other connection such as Teams connection and Virus Total (For authorizing the Virus Total API connection, the API Key needs to be provided)

#### b. Configurations in Microsoft Sentinel
1. Find Microsoft Sentinel Analytics rules that create alerts and incidents which includes IP entities.
2. Configure automation rule(s) to trigger the playbooks


<a name="references">

## Learn more
*  [Threat Intelligence in Azure Firewall Policies](https://docs.microsoft.com/azure/firewall/threat-intel)
*  [IP Groups](https://docs.microsoft.com/azure/firewall/ip-groups)
*  [Azure Firewall documentation](https://docs.microsoft.com/azure/firewall/)

##  Reference to the playbook templates and the connector

 Connector
* [AzureFirewallCustomConnector](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewallConnector)

Playbooks
* [AzureFirewall-AddIPtoTIAllowList : This playbook uses the Azure Firewall connector to add IP Address to the Threat Intel Allow list based on the Microsoft Sentinel Incident](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewall-AddIPtoTIAllowList)
* [AzureFirewall-BlockIP-addNewRule : This playbook uses the Azure Firewall connector to add IP Address to the Deny Network Rules collection based on the Microsoft Sentinel Incident](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewall-BlockIP-addNewRule)
* [AzureFirewall-BlockIP-addToIPGroup : This playbook uses the Azure Firewall connector to add IP Address to the IP Groups based on the Microsoft Sentinel Incident ](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewall-BlockIP-addToIPGroup)
