# Check Point Software Technologies Logic Apps Connector and Sentinel Playbook templates

<br>
<br>
<p align="center">  
<img width="800" src="./images/check_point_logo.png"> </a>
</p>
<br>

# Table of Contents

1. [Overview](#overview)
1. [Deploy Connector and Playbook templates](#deployall)
1. [Deployment instructions](#deployinstr)
1. [Test the playbook](#testplaybook)
1. [Security Recommendations](#securityrecommendation)

<br>

<a name="overview">

# Overview

The Check Point Logic App Connector and Playbooks allows you to automate security operations to all managed Check Point devices. The connector enables you to run Logic App playbooks that utilize Check Point Management API to automate most common security operations tasks. 

<p align="left">  
<img width="800" src="./images/cp_integration_detail.png"> </a>
</p>


For more information see:

[Check Point Management API](https://sc1.checkpoint.com/documents/latest/APIs/#introduction~v1.6%20)  
[Logic App Overview](https://azure.microsoft.com/services/logic-apps/) 

<br>
<a name="deployall">

# Deploy Connector and Playbook templates

## This package includes: 

1. Custom Connector which is based on Check Point Management API v1.6
2. Playbook that will create IP objects and add objects to group
3. FunctionApp Proxy

You can deploy Custom Connector, FunctionApp Proxy and Playbook all together or seperately from their specific folder.

   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FdeployCP.json)
   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FdeployCPgov.json)


<br>

<a name="deployinstr">

# Deployment instructions

1. Create an API key from Check Point management console

    <p align="left">  
    <img width="400" src="./images/cp_create_api_key.png"> </a>
    </p>

2. Launch the template
<br>

   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FdeployCP.json)
   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FdeployCPgov.json)


3. Fill in the template - Make sure you include the backslash of API extension /web_api/ 

    <p align="left">  
    <img width="400" src="./images/cp_template.png"> </a>
    </p>

4. Copy the API key from the function app

    <p align="left">  
    <img width="400" src="./images/cp_copy_function_key.png"> </a>
    </p>

5. Paste function API key into the API management

    <p align="left">  
    <img width="400" src="./images/cp_copy_apimgmt_key.png"> </a>
    </p>

6. Update LogicApp Sentinel Connection

    <p align="left">  
    <img width="400" src="./images/cp_logicapp_sentinel.png"> </a>
    </p>

7. Configure Sentinel Analytics Rule

    <p align="left">  
    <img width="400" src="./images/cp_sentinel_analytic_rule.png"> </a>
    </p>


<a name="testplaybook"> 

# Test the playbook

* Dry run

    <p align="left">  
    <img width="400" src="./images/cp_logicapp_test.png"> </a>
    </p>
    
* Dry run result

    <p align="left">  
    <img width="400" src="./images/cp_logicapp_test_result.png"> </a>
    </p>


<br>
<br>

<a name="securityrecommendation"> 

# Security Recommendations

## Define Check Point Management User Profile

The following is the recommended Check Point user profile which will allow the Sentinel user to manage objects, policy and install security policy, all other access are turned off. 

1. Create a new user profile

    <p align="left">  
    <img width="400" src="./images/cp_userprofile.png"> </a>
    </p>

2. Access Control

    <p align="left">  
    <img width="400" src="./images/cp_userprofile_acl.png"> </a>
    </p>

3. Threat Prevention

    <p align="left">  
    <img width="400" src="./images/cp_userprofile_threat.png"> </a>
    </p>

4. Management

    <p align="left">  
    <img width="400" src="./images/cp_userprofile_mgmt.png"> </a>
    </p>

5. Disable all other settings

<br>

## Access Control for Function Proxy

<br>
### Ingress to Function Proxy
Only the Azure API Management is required to access the Proxy Function. 

This deployment template is using Management API "Consumption" SKU, this is the lightweight and serverless version of API Management service, billed per execution and first 1M calls are free. However, this Management API SKU does not offer a static ip address, you will need to extract the IP address ranges of the entire region and apply it to the function rule. 

For example, the following JSON fragment is what the allowlist for Western Europe might look like, Refer to [Azure Region outbound IP ranges](https://docs.microsoft.com/azure/azure-functions/ip-addresses#data-center-outbound-ip-addresses) for your region. 
 

    {
    "name": "AzureCloud.westeurope",
    "id": "AzureCloud.westeurope",
    "properties": {
        "changeNumber": 9,
        "region": "westeurope",
        "platform": "Azure",
        "systemService": "",
        "addressPrefixes": [
        "13.69.0.0/17",
        "13.73.128.0/18",
        ... Some IP addresses not shown here
        "213.199.180.192/27",
        "213.199.183.0/24"
        ]
    }
    }

Once you have the IP address ranges, you can define the IP address under Access Restrictions

    # Setting the SCM to be same as function
    az functionapp config access-restriction set --use-same-restrictions-for-scm-site true -g ResourceGroup -n AppName

    # Repeat the following per subnet
    az functionapp config access-restriction add -g ResourceGroup -n AppName --action Allow --ip-address 13.64.0.0/16 --priority 200



    Example: 
    az functionapp config access-restriction set --use-same-restrictions-for-scm-site true -g guoapr2311130-rg -n guoapr2311130-proxy-mrbz7

    az functionapp config access-restriction add -g guoapr2311130-rg -n guoapr2311130-proxy-mrbz7 --action Allow --ip-address 13.64.0.0/16 --priority 200

    az functionapp config access-restriction add -g guoapr2311130-rg -n guoapr2311130-proxy-mrbz7 --action Allow --ip-address 13.73.32.0/19 --priority 200

    ....


Function Access Restrictions from Azure portal: 

<p align="left">  
    <img width="600" src="./images/cp_function_acl.png"> </a>
    </p>

<br>

Note: If your subscription is already using API management other than "Consumption" SKU then you can extract the IP address as per [api-management-howto-ip-addresses](https://docs.microsoft.com/azure/api-management/api-management-howto-ip-addresses)

<br>

### Egress from Function Proxy

The function proxy will connect to Check Point Management Station

[How to get Function IP outbound IP address](https://docs.microsoft.com/azure/azure-functions/ip-addresses)

To find the available outbound IP addresses is by using the Cloud Shell:

    az webapp show --resource-group <group_name> --name <app_name> --query outboundIpAddresses --output tsv
    az webapp show --resource-group <group_name> --name <app_name> --query possibleOutboundIpAddresses --output tsv

1. Modify nesseary Firewall rules to allow the IP ranges from above
2. Apply IP ranges as Check Point Mangement GUI clients, [how to define GUI Clients](https://sc1.checkpoint.com/documents/R80.30/WebAdminGuides/CP_R80.30_Gaia_AdminGuide/html_frameset.htm?topic=documents/R80.30/WebAdminGuides/CP_R80.30_Gaia_AdminGuide/214749)


<br>

## Rotate API Keys

Rotate the following API Keys every 90 days

    * Check Point API Key
    * Mgmt API Key
    * Function Proxy Key
