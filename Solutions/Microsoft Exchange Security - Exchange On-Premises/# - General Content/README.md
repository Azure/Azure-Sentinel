# Microsoft Exchange Security Solutions for Microsoft Sentinel

For several years, Exchange Servers have been frequent targets of cyberattacks. Support cases and escalations have repeatedly exposed poorly managed environments, while security assessments continue to uncover insecure configurations that leave messaging systems vulnerable to compromise. Despite these risks—and the highly sensitive nature of the data they store and process—Exchange Servers are often insufficiently monitored from a security perspective, and the logs and traces required for investigations are not always collected or retained in time.

Introducing **M**icrosoft **E**xchange **S**ecurity Solution

The Microsoft Exchange Security offering consists of two Microsoft Sentinel solutions:

* **Microsoft Exchange Security for Exchange On-Premises**
* **Microsoft Exchange Security for Exchange Online**

Both solutions collect data about security-sensitive operations performed in on-premises Exchange and Exchange Online environments. They provide Microsoft Sentinel content that enables service owners and SOC teams to:

* Identify insecure configurations
* Detect attacks targeting Exchange Servers
* Monitor sensitive administrative operations
* Identify incorrect or overly permissive RBAC configurations that could put the environment at risk

The solutions also provide threat hunters with a broad range of data for identifying suspicious or anomalous behavior.

## Microsoft Exchange Security for Exchange On-Premises

### DATA Collection

The solution supports the collection of multiple log types and security configuration reports. You can select the data sources that best meet your security requirements while controlling the volume of data ingested into Microsoft Sentinel.

Data collection is provided through two connectors:

* Exchange Security Insights On-Premise Collector
* Microsoft Exchange Logs and Events

#### Exchange Security Insights On-Premise Collector - Data Collector - Mandatory

Connector  brief description :

* This connectors is **Mandatory**
* A script deployed on an On-Premises machine, will  collect Security configuration from Exchange Servers and send them to Sentinel
* This connector install functions that help displayed useful information in Workbooks

#### Workbooks

List of workbook based on this connector :

* Microsoft Exchange Security Review
* Microsoft Exchange Least Privilege with RBAC

#### VIP management

A dedicated watchlist is created for each solution. Add the names of your VIP users to this watchlist to monitor activity affecting them in the following workbooks:

* Microsoft Exchange Admin Activity
* Microsoft Exchange Admin Activity - Online

#### Microsoft Exchange Logs and Events - Data Collector - Optional

Connector  brief description :

* This connector is **Optional**
* This connector allow you to collect the following information :

  * Option 1 : Exchange Audit Log : This option collects MS Exchange Manahement logs (retrieved from the Event Viewer) for every Exchange servers using Azure Monitor Agent or Azure Log Analytics agent on each Exchange Server. This content is used to analyze Admin activities on your On-Premises Exchange environment(s)
  * Option 2 : Security/Application/System logs from all Exchange servers
  * Option 3 : Security logs for DC located in Exchange AD site
  * Option 4 : Security logs for all DC
  * Option 5 : IIS logs for all Exchange servers
  * Option 6 : Message Tracking logs for all Exchange servers
  * Option 7 : HTTPProxy logs for all Exchange Servers

All collection options are optional, allowing you to select only the data required for your monitoring and investigation scenarios.

> **Important:** Some options—particularly IIS, Message Tracking, and HTTP proxy logs—can generate a significant volume of data and increase ingestion costs. Carefully assess the expected data volume before enabling each option. These logs can nevertheless provide valuable information for threat detection and forensic investigations. For guidance on selecting the appropriate logs, refer to the connector configuration documentation.

#### Workbook

List of workbook based on this connectors :

* Microsoft Exchange Admin Activity :  **Require Option 1** (require the upload of the MS Exchange Management log)
* Microsoft Exchange Search AdminAuditLog : **Require Option 1** (require the upload of the MS Exchange Management log)

### Documentations

In order to deploy the solution, you can find documentation in the folder : [Documentations](./Documentations/)

* [Deployment Microsoft Exchange Security for Exchange On-Premises](./Documentations/Deployment-MES-OnPremises.md)
* [Exchange Security Insights On-Premise/Online Collector](./Documentations/ESICollector.md)

## Microsoft Exchange Security for Exchange Online

### DATA Collection

We build the solution to give you the ability to collect security configuration from Exchange Online and to displayed useful information based on the Micorosft 365 logs (Office365 Activity).

The collection is based on one connector and one additonal solution:

* **Exchange Security Insights Online Collector:** Included with the Microsoft Exchange Security for Exchange Online solution
* **Microsoft 365 solution:** Ingests Office 365 activity logs into Microsoft Sentinel and is required by two of the workbooks

#### Exchange Security Insights Online Collector (using Azure Functions)

This connector:

* Is **mandatory**
* Collects security configuration data from Exchange Online and sends it to Microsoft Sentinel
* Deploys functions used by the workbooks to display relevant security information
### Workbooks

List of workbook based on this connector :

* Microsoft Exchange Security Review - Online
* Microsoft Exchange Least Privilege with RBAC - Online
* Microsoft Exchange Admin Activity - Online (Microsoft 365 solution required)
* Microsoft Exchange Search AdminAuditLog - Online (Microsoft 365 solution required)

### Documentations

In order to deploy the solution, you can find documentation in the folder : [Documentations](./Documentations/)

* [Deployment Microsoft Exchange Security for Exchange Online](./Documentations/Deployment-MES-Online.md)
* [Exchange Security Insights On-Premise/Online Collector](./Documentations/ESICollector.md)
