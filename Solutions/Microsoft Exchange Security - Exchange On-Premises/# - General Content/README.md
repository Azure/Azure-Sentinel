# Microsoft Exchange Security Sentinel Solution - Public Contents

**Exchange Servers** have recently been the target of many attacks. The cases and escalations opened recently have revealed poorly managed environments. Exchange Server security assessments regularly discover many insecured configurations putting the messaging system at risk of being compromised without much effort. However Exchange Servers are rarely monitored sufficiently from a security perspective and traces and logs often can’t be collected on time when investigations need to be performed.

Introducing **M**icrosoft **E**xchange **S**ecurity Solution

We built two Sentinel solutions :

* **Microsoft Exchange Security for Exchange On-Premises**
* **Microsoft Exchange Security for Exchange Online**

Both solution collects and detects sensitive security operations happening on On-Premises Exchange Servers and Exchange Online using Microsoft Sentinel. This allows service owners and SOC teams to :

* Detect unsecure configurations
* Detect to attacks targeting Exchange Servers
* Alert on sensitive administrative operations
* Report on incorrect RBAC configurations putting the environment at risk

The solution also allows hunters to search a very diverse set of data to find abnormal behaviors.

## Microsoft Exchange Security for Exchange On-Premises

### DATA Collection

We build the solution to give you the possibility to collect multiple logs and configurations reports following your needs and the quantity of logs you want to upload to Microsoft Sentinel.

The collection is based on two connectors :

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
A watchlist per solution is created.
Fill it with the name of your VIP.
These watchlist help track activities on VIP in the Workbook :
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

All options are **optional**. It is your call to decide which information you want to collect.
**Be careful**, some options can have result to the upload of a **huge amount**. Ex: IIS log, Messsage Tracking, HTTP Proxy logs. You need to think carefully before configue each options. However, remember that these will be very useful for detection and forensic. You'll find detailed informations on how to choose which logs will be uploaded in the connector configuration in the documentations section.

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

* Data connector : 
  * Exchange Security Insights Online Collector (using Azure Functions)
  * This connector come with our solution Microsoft Exchange Security for Exchange Online
* Solution : Microsoft 365. Microsoft Solution that will transfer Office Activity logs in Sentinel. Required for two workbooks

#### Exchange Security Insights Online Collector (using Azure Functions)

Connector  brief description :

* This connectors is **Mandatory**
* A script deployed using an Azure Automarion, will  collect Security configuration from Exchange Online and send them to Sentinel
* This connector has functions that help displayed useful information in Workbooks

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
