# Infoblox SOC Insights Playbooks for Microsoft Sentinel
[<img alt="Infoblox" src="images/infoblox.png"  />](https://www.infoblox.com/)

These playbooks integrate [Infoblox SOC Insights](https://docs.infoblox.com/space/BloxOneThreatDefense/35898533) data into Microsoft Sentinel.

# Installation
There are multiple ways to install the playbooks. You can either...
- Install the solution from the [Content Hub](https://portal.azure.com/#view/Microsoft_Azure_Marketplace/GalleryItemDetailsBladeNopdl/dontDiscardJourney~/true/id/infoblox.infoblox-cdc-solution/resourceGroupId/%2Fsubscriptions%2Fbe1e61b7-8dbe-4986-a9c2-d85f65524d6e%2FresourceGroups%2Ftme-rg)
(Recommended). This will not only install the playbook templates, but the other Sentinel templates as part of this solution as well.
- Copy and paste the ```azuredeploy.json``` files to a blank playbook.
- Click the **Deploy to Azure** buttons below for each desired playbook.

# The Playbooks
This solution installs several playbooks.

## Infoblox-SOC-Get-Open-Insights-API
This playbook uses the Infoblox SOC Insights REST API to ingest all Open/Active SOC Insights at time of run into the custom ```InfobloxInsight``` table. 

This playbook is an alternative to using the **Infoblox SOC Insight Data Connectors via the Microsoft forwarding agent**, which require the **Infoblox Cloud Data Connector (CDC)**. Instead, this playbook **ingests the same type of data via REST API**. This way, you do not need to set up and deploy and Infoblox CDC in your environment. 

You can use both methods in the same workspace, but **beware of duplicate data**.

Simply input your **Infoblox API Key** into the playbook parameters and it will ingest every open SOC Insight at runtime.

The Analytic Query **Infoblox - SOC Insight Detected - API Source** will read this data for insights and create an Incident when one is found. It is OK to run the playbook multiple times, as the Analytic Queries will group SOC Insight Incidents into one that have the same Infoblox Insight ID in the underlying data tables.

This playbook is scheduled to run on a daily basis. You can increase or decrease recurrence.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2520SOC%2520Insights%2FPlaybooks%2FInfoblox-SOC-Get-Open-Insights-API%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2520SOC%2520Insights%2FPlaybooks%2FInfoblox-SOC-Get-Open-Insights-API%2Fazuredeploy.json)


### Prerequisites
1. Create and copy an **Infoblox API key** into the playbook parameters. 
Find instructions [here](https://docs.infoblox.com/space/BloxOneThreatDefense/230394187).

## Infoblox-SOC-Get-Insight-Details
This playbook uses the Infoblox SOC Insights API to **get all the details** about an SOC Insight Incident. These Incidents are triggered by the **Infoblox - SOC Insight Detected** analytic queries packaged as part of this solution. These queries will read your data for insights and create an Incident when one is found, hereby known as a **SOC Insight Incident**.

Then, you can run this playbook on those incidents to **ingest many details about the Insight**, placed in several custom tables prefixed with ```InfobloxInsight```. This data also builds the **Infoblox SOC Insight Workbook** you can use to richly visualize and drilldown your Insights.

It will also add **several tags** to the SOC Insight Incident.

This playbook can be configured to run automatically when a SOC Insight Incident occurs or run on demand.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2520SOC%2520Insights%2FPlaybooks%2FInfoblox-SOC-Get-Insight-Details%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2520SOC%2520Insights%2FPlaybooks%2FInfoblox-SOC-Get-Insight-Details%2Fazuredeploy.json)

### Prerequisites
1. Apply the **Microsoft Sentinel Contributor** or **Microsoft Sentinel Responder** role to the playbooks. 
It is recommended to assign the role to the resource group that contains your Microsoft Sentinel workspace. 
Find instructions [here](https://learn.microsoft.com/en-us/azure/sentinel/roles).

2. Create and copy an **Infoblox API key** into the playbook parameters. 
Find instructions [here](https://docs.infoblox.com/space/BloxOneThreatDefense/230394187).

## Infoblox-SOC-Import-Indicators-TI
This playbook imports each Indicator of an SOC Insight Incident into the ```ThreatIntelligenceIndicator``` table you can use as **threat intelligence**. 

*You must run the **Infoblox-SOC-Get-Insight-Details** playbook on the SOC Insight Incident before running this playbook.*

This playbook can be configured to run automatically when a SOC Insight Incident occurs or run on demand.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2520SOC%2520Insights%2FPlaybooks%2FInfoblox-SOC-Import-Indicators-TI%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2520SOC%2520Insights%2FPlaybooks%2FInfoblox-SOC-Import-Indicators-TI%2Fazuredeploy.json)

### Prerequisites
1. Register an app with Microsoft Entra ID and apply appropriate permissions, and enable the Threat Intelligence data connector. 
Find instructions [here](https://learn.microsoft.com/en-us/azure/sentinel/connect-threat-intelligence-tip). 

2. Apply the **Microsoft Sentinel Contributor** or **Microsoft Sentinel Responder** role to the playbooks. 
It is recommended to assign the role to the resource group that contains your Microsoft Sentinel workspace. 
Find instructions [here](https://learn.microsoft.com/en-us/azure/sentinel/roles).


