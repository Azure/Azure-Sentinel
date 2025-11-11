# Cisco SDWAN Intrusion Logic App

* [Summary](#Summary)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)


### Summary<a name="Summary"></a>

This playbook provides an end-to-end example of adding a comment in the generated incident.

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Subscription: Azure Subscription ID which is present in the subscription tab in Microsoft Sentinel.
    * Resource Group: The Azure Resource Group name in which you want to deploy the Logic App.
    * Playbook Name: Enter the playbook name here

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCisco%20SD-WAN%2FPlaybooks%2FCiscoSDWANIntrusionLogicApp%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCisco%20SD-WAN%2FPlaybooks%2FCiscoSDWANIntrusionLogicApp%2Fazuredeploy.json)

### Post-Deployment instructions<a name="Post-Deployment-instructions"></a>

##### a. Authorize connections

Once deployment is complete, authorize each connection like MicrosoftSentinel.

1. Click the connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save

##### b. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, analytics rules should be configured to trigger an incident. 
  > 1. Add your deployed logic app in analytic rule to be trigger on every generated incident, to do this follow below steps
  >> * Select the analytic rule you have deployed.
  >> * Click on **Edit**
  >> * Go to **Automated response** tab
  >> * Click on **Add new**
  >> * Provide name for your rule, In Actions dropdown select **Run playbook**
  >> * In second dropdown select your deployed playbook
  >> * Click on **Apply**
  >> * Save the Analytic rule.
  > 2. An incident should have the **signature_id** - custom entity that contains SignatureId from CiscoSyslogUTD.

#### Sample analytics rule query

* Analytic Rule : Intrusion Events

```
 CiscoSyslogUTD
| where SignatureId == "1-12451"
```