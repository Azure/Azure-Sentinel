# Microsoft Exchange Security Solutions for Microsoft Sentinel

For several years, Exchange Servers have been frequent targets of cyberattacks. Support cases and escalations have repeatedly exposed poorly managed environments, while security assessments continue to uncover insecure configurations that leave messaging systems vulnerable to compromise. Despite these risks—and the highly sensitive nature of the data they store and process—Exchange Servers are often insufficiently monitored from a security perspective, and the logs and traces required for investigations are not always collected or retained in time.

Together, they form the **M**icrosoft **E**xchange **S**ecurity offering.

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

### Data collection

The solution supports the collection of multiple log types and security configuration reports. You can select the data sources that best meet your security requirements while controlling the volume of data ingested into Microsoft Sentinel.

Data collection is provided through two connectors:

* Exchange Security Insights On-Premise Collector
* Microsoft Exchange Logs and Events

#### Exchange Security Insights On-Premise Collector - Data Collector - Mandatory

This connector is **mandatory**. A script that runs on an on-premises Windows server collects Exchange Server security configuration and sends it to Microsoft Sentinel. The solution deploys the functions used by its workbooks.

#### Workbooks

Workbooks that use this connector:

* Microsoft Exchange Security Review
* Microsoft Exchange Least Privilege with RBAC

#### VIP management

A dedicated watchlist is created for each solution. Add the names of your VIP users to this watchlist to monitor activity affecting them in the following workbooks:

* Microsoft Exchange Admin Activity
* Microsoft Exchange Admin Activity - Online

#### Microsoft Exchange Logs and Events - Data Collector - Optional

This connector is **optional**. It can collect:

  * Option 1: Exchange administrative audit events from the **MSExchange Management** event log. This option is required only for workbooks that analyze on-premises administrative activity.
  * Option 2: Security, Application, and System event logs from Exchange Servers.
  * Option 3: Security event logs from domain controllers in the Exchange Active Directory site.
  * Option 4: Security event logs from all domain controllers.
  * Option 5: IIS logs from Exchange Servers.
  * Option 6: Message Tracking logs from Exchange Servers.
  * Option 7: HTTP Proxy logs from Exchange Servers.

All collection options are optional, allowing you to select only the data required for your monitoring and investigation scenarios.

> **Important:** Some options—particularly IIS, Message Tracking, and HTTP proxy logs—can generate a significant volume of data and increase ingestion costs. Carefully assess the expected data volume before enabling each option. These logs can nevertheless provide valuable information for threat detection and forensic investigations. For guidance on selecting the appropriate logs, refer to the connector configuration documentation.

#### Workbooks

Workbooks that require Option 1:

* Microsoft Exchange Admin Activity
* Microsoft Exchange Search AdminAuditLog

### Documentation

See the [Exchange On-Premises documentation index](./Documentations/README.md) for deployment, configuration, workbook, forwarding, and operational guidance.

## Microsoft Exchange Security for Exchange Online

### Data collection

The solution collects Exchange Online security configuration and can use Microsoft 365 audit data from the `OfficeActivity` table to display administrative activity.

Data collection is based on one connector and one additional solution:

* **Exchange Security Insights Online Collector:** Included with the Microsoft Exchange Security for Exchange Online solution
* **Microsoft 365 solution:** Ingests Office 365 activity logs into Microsoft Sentinel and is required by two of the workbooks

#### Exchange Security Insights Online Collector (using Azure Automation)

This connector:

* Is **mandatory**
* Collects security configuration data from Exchange Online and sends it to Microsoft Sentinel
* Deploys functions used by the workbooks to display relevant security information
### Workbooks

Workbooks that use this connector:

* Microsoft Exchange Security Review - Online
* Microsoft Exchange Least Privilege with RBAC - Online
* Microsoft Exchange Admin Activity - Online (Microsoft 365 solution required)
* Microsoft Exchange Search AdminAuditLog - Online (Microsoft 365 solution required)

### Documentation

See the [Exchange Online documentation index](../../Microsoft%20Exchange%20Security%20-%20Exchange%20Online/%23%20-%20General%20Content/Documentations/README.md) for deployment, configuration, workbook, and operational guidance.
