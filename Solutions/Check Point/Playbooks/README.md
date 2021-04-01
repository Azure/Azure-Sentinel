# Check Point Software Technologies Azure Logic App Connector

The Check Point Logic App Connector will allow you to automate security operations to all managed Check Point devices. The connector enables you to create Logic App workbooks that utilize Check Point Management API to automate most common security operations tasks. 

Logic App can easily integrate Check Point with all native Azure services and hundreds of connectors such as ServiceNow, Jira, PagerDuty, ZenDesk, and more. See the [full list of available connectors here.](https://docs.microsoft.com/connectors/connector-reference/)

Common use cases include: 

  1. Enable operation teams to automate common security functions such as creating objects, updating security policies, and schedule security policy updates to gateways. 
  2. Fully integrate with any orchestration platforms for both on-prem or public cloud providers
  3. Integrate with all leading SIEM/SOAR providers such as Azure Sentinel


For more information see
[Check Point Management API](https://sc1.checkpoint.com/documents/latest/APIs/#introduction~v1.7%20) and 
[Logic App Overview](https://azure.microsoft.com/services/logic-apps/) 

# How does the Logic App Connector work? 

<p align="left">  
<img width="800" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/cp_LogicApp_01.png"> </a>
</p>

The Logic App workbook can get triggers from any of the hundreds of connectors containing user-defined perimeters to fulfill the change request. 

Change request items include IP addresses, URLs, groups, gateways, and policy packages. 

The Check Point Logic App Connector contains Check Point Mgmt API parameters to cater most common tasks you want to automate. 

# How does everything tie together?

<p align="left">  
<img width="800" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/cp_LogicApp_01.png"> </a>
</p>

The solution is using Azure API Management, Function App, and Logic Apps. These services are secured by allowing access from respective Azure IP ranges and secured by API keys. See security guidance below.

  * API Management allows you to consolidate all API from a single static IP, fine-grained control and provides detailed reporting of your APIs. 
  * The Function App help connect Logic App to both cloud and on-prem Check Point Management station


# Deploy 

   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FPlaybooks%2FdeployCP.json)
   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FPlaybooks%2FdeployCPgov.json)

# Logic App playbook components

1. Trigger point - It can be scheduled, use HTTP post, or trigger point from a connector

    Example 1 - Scheduled tasks
    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/example1.png"> </a>
    </p>

    Example 2 - Azure Sentinel Alert
    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/example2.png"> </a>
    </p>

    Example 3 - HTTP post
    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/example3.png"> </a>
    </p>

2. Workflow - Logic App instructions

	  Define the Check Point gateway and policy package
    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/workflow1.png"> </a>
    </p>

	  Define the Check Point management station user/pw
    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/workflow2.png"> </a>
    </p>

    Define what action to take, in this case, create and add each host to predefined group
    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/workflow3.png"> </a>
    </p>

    Publish and Install security policy
    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/workflow4.png"> </a>
    </p>

# Deployment instructions

1. Create API user from Check Point management console

2. Launch the template

   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FPlaybooks%2FdeployCP.json)
   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FPlaybooks%2FdeployCPgov.json)

3. Template - Make sure you include the backslash of API extension /web_api/ 

    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/deploy1.png"> </a>
    </p>

4. Copy the API key from the function app

    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/deploy2.png"> </a>
    </p>

5. Paste function API key into the API management

    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/deploy3.png"> </a>
    </p>

## Test

1. From SmartConsole - create a simple group, for example, Sentinel_Block_Group

2. Copy the logic app trigger URL

    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/test1.png"> </a>
    </p>

3. Paste the URL and Body into Postman

    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/test2.png"> </a>
    </p>

    Request Body

```
    {
      "set-group": "Sentinel_Block_Group",
        "add-host": [
            "192.168.100.1",
            "192.168.100.2",
            "192.168.100.3",
            "192.168.100.4",
            "192.168.100.5",
            "192.168.100.6",
            "192.168.100.7",
            "192.168.100.8",
            "192.168.100.9",
            "192.168.100.10",
        ]
    }
```

4. Logic App run history should have green tickets next to each successful tasks

    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/test3.png"> </a>
    </p>

5. Smart Console should contain the above IP addresses in the Sentinel group created earlier

    <p align="left">  
    <img width="400" src="https://github.com/chkp-jguo/Azure-Sentinel/blob/b95ddb3cf3af55f75695737e555d57c17ce435a5/Solutions/Check%20Point/Playbooks/images/test4.png"> </a>
    </p>

# Security Guidance: 

1. Lockdown the Logic App, API Management, and Function App service with respective Azure region IP ranges. [List of Azure IP ranges here](https://www.microsoft.com/download/details.aspx?id=56519) 

    ```
      Logic Apps Ranges: 
      
      {
      "name": "LogicApps.AustraliaEast",
      "id": "LogicApps.AustraliaEast",
      "properties": {
      "changeNumber": 1,
      "region": "australiaeast",
      "regionId": 3,
      "platform": "Azure",
      "systemService": "LogicApps",
      "addressPrefixes": [
      "13.70.78.192/27",
      "13.75.149.4/32",
      "13.75.153.66/32",
      …
      "2603:1010:6:402::3c0/124",
      "2603:1010:6:402::3e0/123"
      ],
      
      
      API Management Ranges: 
      
      "name": "ApiManagement.AustraliaEast",
      "id": "ApiManagement.AustraliaEast",
      "properties": {
      "changeNumber": 2,
      "region": "australiaeast",
      "regionId": 3,
      "platform": "Azure",
      "systemService": "AzureApiManagement",
      "addressPrefixes": [
      "13.70.72.28/31",
      "13.70.72.240/28",
      "13.75.217.184/32",
      …
      "20.40.125.155/32",
      "2603:1010:6:402::140/124"
      ],
      
      Azure Functions Ranges:
      
      {
      "name": "AzureCloud.australiaeast",
      "id": "AzureCloud.australiaeast",
      "properties": {
      "changeNumber": 13,
      "region": "australiaeast",
      "regionId": 3,
      "platform": "Azure",
      "systemService": "",
      "addressPrefixes": [
      "13.70.64.0/18",
      "13.72.224.0/19",
      "13.73.192.0/20",
      "13.75.128.0/17",
      …
      "2603:1016:1400:60::/59",
      "2603:1016:2402::/48",
      "2603:1016:2500:c::/64",
      "2603:1017:0:60::/59"
      ],
    ```
  
2. Rotate access keys to API management, Function App, and Check Point user password/access keys every 90 days