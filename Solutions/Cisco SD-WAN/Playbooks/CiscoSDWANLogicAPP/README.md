# Cisco SDWAN Logic App

* [Summary](#Summary)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)


## Summary<a name="Summary"></a>

This playbook provides an end-to-end example of sending an email, posting a message to the Microsoft Teams channel, and creating 3rd party ticket for the suspicious activity found in the data.

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill the below parameters:
    * Subscription: Azure Subscription ID which is present in the subscription tab in Microsoft Sentinel.
    * Resource Group: The Azure Resource Group name in which you want to deploy the Logic App.
    * Playbook Name: Enter the playbook name here
    * 3rd_Party_Ticket_System: Select 3rd Party Ticketing System.
    * Jira_Instance: Enter the URL of Jira Instance if you have selected Jira as 3rd Party Ticketing system.
    * Jira_Project_Key: Enter Jira Project Key if you have selected Jira as 3rd Party Ticketing system.
    * Email: Enter comma-separated email addresses on which alert details will be sent.
    * From_Mobile_No: Enter the source mobile number with the Country code for sending SMS.
    * To_Mobile_No: Enter the destination mobile number with the Country code for sending SMS.
    * Teams_Channel_ID: Enter the ID of the Microsoft Teams channel on which alert details will be sent.
    * Teams_Group_ID: Enter the ID of the Microsoft Teams channel group on which alert details will be sent.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCisco%20SD-WAN%2FPlaybooks%2FCiscoSDWANLogicApp%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCisco%20SD-WAN%2FPlaybooks%2FCiscoSDWANLogicApp%2Fazuredeploy.json)

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

#### Sample analytics rule query
* Analytic Rule : Monitor Critical IPs
```
CiscoSyslogUTD
| union (CiscoSDWANNetflow)
| where isnotempty(SourceIP) or isnotempty(NetflowFwSrcAddrIpv4)
| extend SourceIP = coalesce(SourceIP, NetflowFwSrcAddrIpv4)
| where ipv4_is_in_any_range(SourceIP, "172.16.101.9/24", "192.168.1.1/24", "208.67.220.220")
| summarize count() by SourceIP
```

* Analytic Rule : IPS Event Threshold
```
CiscoSyslogUTD 
| where Classification == "A Network Trojan was Detected" 
| summarize count() by Classification 
| where count_ > 10
```

* Analytic Rule : Malware Events
```
CiscoSyslogUTD
| where isnotempty(Malware) and Malware != "None"
| distinct Malware, SourceIP
| join kind=inner (CiscoSDWANNetflow
| where isnotempty(NetflowUsername)
| summarize arg_max(TimeStamp, NetflowUsername) by NetflowFwSrcAddrIpv4
| distinct 
    ["Username"] = NetflowUsername,
    ["SourceIP"] = NetflowFwSrcAddrIpv4) on SourceIP
| project Malware, SourceIP, Username
```