# Microsoft Sentinel Connectors Index

Browse all data connectors available in Microsoft Sentinel Solutions.

**Browse by:**

- [Solutions](connector-reference-index.md)
- [Connectors](connectors-index.md) (this page)
- [Tables](tables-index.md)

---

## Overview

This page lists **462 unique connectors** across all solutions.

**Jump to:** [#](##) | [A](#a) | [B](#b) | [C](#c) | [D](#d) | [E](#e) | [F](#f) | [G](#g) | [H](#h) | [I](#i) | [J](#j) | [K](#k) | [L](#l) | [M](#m) | [N](#n) | [O](#o) | [P](#p) | [Q](#q) | [R](#r) | [S](#s) | [T](#t) | [V](#v) | [W](#w) | [Z](#z)

## #

### [ Atlassian Confluence Audit (via Codeless Connector Framework)](connectors/confluenceauditccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [AtlassianConfluenceAudit](solutions/atlassianconfluenceaudit.md)

**Tables (1):** `ConfluenceAuditLogs_CL`

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/confluenceauditccpdefinition.md)

---

### [ Dragos Notifications via Cloud Sitestore](connectors/dragossitestoreccp.md)

**Publisher:** Dragos

**Solution:** [Dragos](solutions/dragos.md)

**Tables (1):** `DragosAlerts_CL`

The [Dragos Platform](https://www.dragos.com/) is the leading Industrial Cyber Security platform it offers a comprehensive Operational Technology (OT) cyber threat detection built by unrivaled industrial cybersecurity expertise. This solution enables Dragos Platform notification data to be viewed in Microsoft Sentinel so that security analysts are able to triage potential cyber security events occurring in their industrial environments.

[→ View full connector details](connectors/dragossitestoreccp.md)

---

### [ Microsoft Active-Directory Domain Controllers Security Event Logs](connectors/esi-opt34domaincontrollerssecurityeventlogs.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange On-Premises](solutions/microsoft-exchange-security---exchange-on-premises.md)

**Tables (1):** `SecurityEvent`

[Option 3 & 4] - Using Azure Monitor Agent -You can stream a part or all Domain Controllers Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

[→ View full connector details](connectors/esi-opt34domaincontrollerssecurityeventlogs.md)

---

### [1Password](connectors/1password.md)

**Publisher:** 1Password

**Solution:** [1Password](solutions/1password.md)

**Tables (1):** `OnePasswordEventLogs_CL`

The [1Password](https://www.1password.com) solution for Microsoft Sentinel enables you to ingest 1Password logs and events into Microsoft Sentinel. The connector provides visibility into 1Password Events and Alerts in Microsoft Sentinel to improve monitoring and investigation capabilities.

**Underlying Microsoft Technologies used:**

This solution takes a dependency on the following technologies, and some of these dependencies either may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs:

-  [Azure Functions](https://azure.microsoft.com/services/functions/#overview)

[→ View full connector details](connectors/1password.md)

---

### [1Password (Serverless)](connectors/1passwordccpdefinition.md)

**Publisher:** 1Password

**Solution:** [1Password](solutions/1password.md)

**Tables (1):** `OnePasswordEventLogs_CL`

The 1Password CCP connector allows the user to ingest 1Password Audit, Signin & ItemUsage events into Microsoft Sentinel.

[→ View full connector details](connectors/1passwordccpdefinition.md)

---

### [[Recommended] Infoblox SOC Insight Data Connector via AMA](connectors/infobloxsocinsightsdataconnector-ama.md)

**Publisher:** Infoblox

**Solution:** [Infoblox](solutions/infoblox.md)

**Tables (1):** `CommonSecurityLog`

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 

This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the new Azure Monitor Agent. Learn more about ingesting using the new Azure Monitor Agent [here](https://learn.microsoft.com/azure/sentinel/connect-cef-ama). **Microsoft recommends using this Data Connector.**

[→ View full connector details](connectors/infobloxsocinsightsdataconnector-ama.md)

---

### [[Recommended] Vectra AI Stream via AMA](connectors/vectrastreamama.md)

**Publisher:** Vectra AI

**Solution:** [Vectra AI Stream](solutions/vectra-ai-stream.md)

**Tables (17):** `vectra_beacon_CL`, `vectra_dcerpc_CL`, `vectra_dhcp_CL`, `vectra_dns_CL`, `vectra_http_CL`, `vectra_isession_CL`, `vectra_kerberos_CL`, `vectra_ldap_CL`, `vectra_ntlm_CL`, `vectra_radius_CL`, `vectra_rdp_CL`, `vectra_smbfiles_CL`, `vectra_smbmapping_CL`, `vectra_smtp_CL`, `vectra_ssh_CL`, `vectra_ssl_CL`, `vectra_x509_CL`

The Vectra AI Stream connector allows to send Network Metadata collected by Vectra Sensors accross the Network and Cloud to Microsoft Sentinel

[→ View full connector details](connectors/vectrastreamama.md)

---

## A

### [AI Vectra Stream via Legacy Agent](connectors/aivectrastream.md)

**Publisher:** Vectra AI

**Solution:** [Vectra AI Stream](solutions/vectra-ai-stream.md)

**Tables (2):** `VectraStream`, `VectraStream_CL`

The AI Vectra Stream connector allows to send Network Metadata collected by Vectra Sensors accross the Network and Cloud to Microsoft Sentinel

[→ View full connector details](connectors/aivectrastream.md)

---

### [AIShield](connectors/boschaishield.md)

**Publisher:** Bosch

**Solution:** [AIShield AI Security Monitoring](solutions/aishield-ai-security-monitoring.md)

**Tables (1):** `AIShield_CL`

[AIShield](https://www.boschaishield.com/) connector allows users to connect with AIShield custom defense mechanism logs with Microsoft Sentinel, allowing the creation of dynamic Dashboards, Workbooks, Notebooks and tailored Alerts to improve investigation and thwart attacks on AI systems. It gives users more insight into their organization's AI assets security posturing and improves their AI systems security operation capabilities.AIShield.GuArdIan analyzes the LLM generated content to identify and mitigate harmful content, safeguarding against legal, policy, role based, and usage based violations

[→ View full connector details](connectors/boschaishield.md)

---

### [API Protection](connectors/42crunchapiprotection.md)

**Publisher:** 42Crunch

**Solution:** [42Crunch API Protection](solutions/42crunch-api-protection.md)

**Tables (1):** `apifirewall_log_1_CL`

Connects the 42Crunch API protection to Azure Log Analytics via the REST API interface

[→ View full connector details](connectors/42crunchapiprotection.md)

---

### [ARGOS Cloud Security](connectors/argoscloudsecurity.md)

**Publisher:** ARGOS Cloud Security

**Solution:** [ARGOSCloudSecurity](solutions/argoscloudsecurity.md)

**Tables (1):** `ARGOS_CL`

The ARGOS Cloud Security integration for Microsoft Sentinel allows you to have all your important cloud security events in one place. This enables you to easily create dashboards, alerts, and correlate events across multiple systems. Overall this will improve your organization's security posture and security incident response.

[→ View full connector details](connectors/argoscloudsecurity.md)

---

### [AWS S3 Server Access Logs (via Codeless Connector Framework)](connectors/awss3serveraccesslogsdefinition.md)

**Publisher:** Microsoft

**Solution:** [AWS_AccessLogs](solutions/aws-accesslogs.md)

**Tables (1):** `AWSS3ServerAccess`

This connector allows you to ingest AWS S3 Server Access Logs into Microsoft Sentinel. These logs contain detailed records for requests made to S3 buckets, including the type of request, resource accessed, requester information, and response details. These logs are useful for analyzing access patterns, debugging issues, and ensuring security compliance.

[→ View full connector details](connectors/awss3serveraccesslogsdefinition.md)

---

### [AWS Security Hub Findings (via Codeless Connector Framework)](connectors/awssecurityhubfindingsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [AWS Security Hub](solutions/aws-security-hub.md)

**Tables (1):** `AWSSecurityHubFindings`

This connector enables the ingestion of AWS Security Hub Findings, which are collected in AWS S3 buckets, into Microsoft Sentinel. It helps streamline the process of monitoring and managing security alerts by integrating AWS Security Hub Findings with Microsoft Sentinel's advanced threat detection and response capabilities.

[→ View full connector details](connectors/awssecurityhubfindingsccpdefinition.md)

---

### [AbnormalSecurity ](connectors/abnormalsecurity.md)

**Publisher:** AbnormalSecurity

**Solution:** [AbnormalSecurity](solutions/abnormalsecurity.md)

**Tables (2):** `ABNORMAL_CASES_CL`, `ABNORMAL_THREAT_MESSAGES_CL`

The Abnormal Security data connector provides the capability to ingest threat and case logs into Microsoft Sentinel using the [Abnormal Security Rest API.](https://app.swaggerhub.com/apis/abnormal-security/abx/)

[→ View full connector details](connectors/abnormalsecurity.md)

---

### [Agari Phishing Defense and Brand Protection](connectors/agari.md)

**Publisher:** Agari

**Solution:** [Agari](solutions/agari.md)

**Tables (3):** `agari_apdpolicy_log_CL`, `agari_apdtc_log_CL`, `agari_bpalerts_log_CL`

This connector uses a Agari REST API connection to push data into Azure Sentinel Log Analytics.

[→ View full connector details](connectors/agari.md)

---

### [Alibaba Cloud ActionTrail (via Codeless Connector Framework)](connectors/alicloudactiontrailccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Alibaba Cloud ActionTrail](solutions/alibaba-cloud-actiontrail.md)

**Tables (1):** `AliCloudActionTrailLogs_CL`

The [Alibaba Cloud ActionTrail](https://www.alibabacloud.com/product/actiontrail) data connector provides the capability to retrieve actiontrail events stored into [Alibaba Cloud Simple Log Service](https://www.alibabacloud.com/product/log-service) and store them into Microsoft Sentinel through the [SLS REST API](https://www.alibabacloud.com/help/sls/developer-reference/api-sls-2020-12-30-getlogs). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/alicloudactiontrailccpdefinition.md)

---

### [Alsid for Active Directory](connectors/alsidforad.md)

**Publisher:** Alsid

**Solution:** [Alsid For AD](solutions/alsid-for-ad.md)

**Tables (1):** `AlsidForADLog_CL`

Alsid for Active Directory connector allows to export Alsid Indicators of Exposures, trailflow and Indicators of Attacks logs to Azure Sentinel in real time.
It provides a data parser to manipulate the logs more easily. The different workbooks ease your Active Directory monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

[→ View full connector details](connectors/alsidforad.md)

---

### [Amazon Web Services](connectors/aws.md)

**Publisher:** Amazon

**Solution:** [Amazon Web Services](solutions/amazon-web-services.md)

**Tables (1):** `AWSCloudTrail`

Follow these instructions to connect to AWS and stream your CloudTrail logs into Microsoft Sentinel. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2218883&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/aws.md)

---

### [Amazon Web Services CloudFront (via Codeless Connector Framework) (Preview)](connectors/awscloudfrontccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [AWS CloudFront](solutions/aws-cloudfront.md)

**Tables (1):** `AWSCloudFront_AccessLog_CL`

This data connector enables the integration of AWS CloudFront logs with Microsoft Sentinel to support advanced threat detection, investigation, and security monitoring. By utilizing Amazon S3 for log storage and Amazon SQS for message queuing, the connector reliably ingests CloudFront access logs into Microsoft Sentinel

[→ View full connector details](connectors/awscloudfrontccpdefinition.md)

---

### [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](connectors/awsnetworkfirewallccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Amazon Web Services NetworkFirewall](solutions/amazon-web-services-networkfirewall.md)

**Tables (3):** `AWSNetworkFirewallAlert`, `AWSNetworkFirewallFlow`, `AWSNetworkFirewallTls`

This data connector allows you to ingest AWS Network Firewall logs into Microsoft Sentinel for advanced threat detection and security monitoring. By leveraging Amazon S3 and Amazon SQS, the connector forwards network traffic logs, intrusion detection alerts, and firewall events to Microsoft Sentinel, enabling real-time analysis and correlation with other security data

[→ View full connector details](connectors/awsnetworkfirewallccpdefinition.md)

---

### [Amazon Web Services S3](connectors/awss3.md)

**Publisher:** Amazon

**Solution:** [Amazon Web Services](solutions/amazon-web-services.md)

**Tables (4):** `AWSCloudTrail`, `AWSCloudWatch`, `AWSGuardDuty`, `AWSVPCFlow`

This connector allows you to ingest AWS service logs, collected in AWS S3 buckets, to Microsoft Sentinel. The currently supported data types are: 
* AWS CloudTrail
* VPC Flow Logs
* AWS GuardDuty
* AWSCloudWatch

For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2218883&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/awss3.md)

---

### [Amazon Web Services S3 DNS Route53 (via Codeless Connector Framework)](connectors/awsroute53resolverccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Amazon Web Services Route 53](solutions/amazon-web-services-route-53.md)

**Tables (1):** `AWSRoute53Resolver`

This connector enables ingestion of AWS Route 53 DNS logs into Microsoft Sentinel for enhanced visibility and threat detection. It supports DNS Resolver query logs ingested directly from AWS S3 buckets, while Public DNS query logs and Route 53 audit logs can be ingested using Microsoft Sentinel's AWS CloudWatch and CloudTrail connectors. Comprehensive instructions are provided to guide you through the setup of each log type. Leverage this connector to monitor DNS activity, detect potential threats, and improve your security posture in cloud environments.

[→ View full connector details](connectors/awsroute53resolverccpdefinition.md)

---

### [Amazon Web Services S3 VPC Flow Logs](connectors/awss3vpcflowlogsparquetdefinition.md)

**Publisher:** Microsoft

**Solution:** [AWS VPC Flow Logs](solutions/aws-vpc-flow-logs.md)

**Tables (1):** `AWSVPCFlow`

This connector allows you to ingest AWS VPC Flow Logs, collected in AWS S3 buckets, to Microsoft Sentinel. AWS VPC Flow Logs provide visibility into network traffic within your AWS Virtual Private Cloud (VPC), enabling security analysis and network monitoring.

[→ View full connector details](connectors/awss3vpcflowlogsparquetdefinition.md)

---

### [Amazon Web Services S3 WAF](connectors/awss3wafccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Amazon Web Services](solutions/amazon-web-services.md)

**Tables (1):** `AWSWAF`

This connector allows you to ingest AWS WAF logs, collected in AWS S3 buckets, to Microsoft Sentinel. AWS WAF logs are detailed records of traffic that web access control lists (ACLs) analyze, which are essential for maintaining the security and performance of web applications. These logs contain information such as the time AWS WAF received the request, the specifics of the request, and the action taken by the rule that the request matched.

[→ View full connector details](connectors/awss3wafccpdefinition.md)

---

### [Anvilogic](connectors/anvilogicccfdefinition.md)

**Publisher:** Anvilogic

**Solution:** [Anvilogic](solutions/anvilogic.md)

**Tables (1):** `Anvilogic_Alerts_CL`

The Anvilogic data connector allows you to pull events of interest generated in the Anvilogic ADX cluster into your Microsoft Sentinel

[→ View full connector details](connectors/anvilogicccfdefinition.md)

---

### [Armis Activities](connectors/armisactivities.md)

**Publisher:** Armis

**Solution:** [Armis](solutions/armis.md)

**Tables (1):** `Armis_Activities_CL`

The [Armis](https://www.armis.com/) Activities connector gives the capability to ingest Armis device Activities into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/doc` for more information. The connector provides the ability to get device activity information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis detects what all devices are doing in your environment and classifies those activities to get a complete picture of device behavior. These activities are analyzed for an understanding of normal and abnormal device behavior and used to assess device and network risk.

[→ View full connector details](connectors/armisactivities.md)

---

### [Armis Alerts](connectors/armisalerts.md)

**Publisher:** Armis

**Solution:** [Armis](solutions/armis.md)

**Tables (1):** `Armis_Alerts_CL`

The [Armis](https://www.armis.com/) Alerts connector gives the capability to ingest Armis Alerts into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get alert information from the Armis platform and to identify and prioritize threats in your environment. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. 

[→ View full connector details](connectors/armisalerts.md)

---

### [Armis Alerts Activities](connectors/armisalertsactivities.md)

**Publisher:** Armis

**Solution:** [Armis](solutions/armis.md)

**Tables (2):** `Armis_Activities_CL`, `Armis_Alerts_CL`

The [Armis](https://www.armis.com/) Alerts Activities connector gives the capability to ingest Armis Alerts and Activities into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get alert and activity information from the Armis platform and to identify and prioritize threats in your environment. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. 

[→ View full connector details](connectors/armisalertsactivities.md)

---

### [Armis Devices](connectors/armisdevices.md)

**Publisher:** Armis

**Solution:** [Armis](solutions/armis.md)

**Tables (1):** `Armis_Devices_CL`

The [Armis](https://www.armis.com/) Device connector gives the capability to ingest Armis Devices into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get device information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis can also integrate with your existing IT & security management tools to identify and classify each and every device, managed or unmanaged in your environment.

[→ View full connector details](connectors/armisdevices.md)

---

### [Armorblox](connectors/armorblox.md)

**Publisher:** Armorblox

**Solution:** [Armorblox](solutions/armorblox.md)

**Tables (1):** `Armorblox_CL`

The [Armorblox](https://www.armorblox.com/) data connector provides the capability to ingest incidents from your Armorblox instance into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, and more.

[→ View full connector details](connectors/armorblox.md)

---

### [Atlassian Beacon Alerts](connectors/atlassianbeaconalerts.md)

**Publisher:** DEFEND Ltd.

**Solution:** [Integration for Atlassian Beacon](solutions/integration-for-atlassian-beacon.md)

**Tables (1):** `atlassian_beacon_alerts_CL`

Atlassian Beacon is a cloud product that is built for Intelligent threat detection across the Atlassian platforms (Jira, Confluence, and Atlassian Admin). This can help users detect, investigate and respond to risky user activity for the Atlassian suite of products. The solution is  a custom data connector from DEFEND Ltd. that is used to visualize the alerts ingested from Atlassian Beacon to Microsoft Sentinel via a Logic App.

[→ View full connector details](connectors/atlassianbeaconalerts.md)

---

### [Atlassian Confluence](connectors/atlassianconfluence.md)

**Publisher:** Atlassian

**Solution:** [AtlassianConfluenceAudit](solutions/atlassianconfluenceaudit.md)

**Tables (1):** `AtlassianConfluenceNativePoller_CL`

The Atlassian Confluence data connector provides the capability to ingest [Atlassian Confluence audit logs](https://developer.atlassian.com/cloud/confluence/rest/api-group-audit/) into Microsoft Sentinel.

[→ View full connector details](connectors/atlassianconfluence.md)

---

### [Atlassian Jira Audit](connectors/jiraauditapi.md)

**Publisher:** Atlassian

**Solution:** [AtlassianJiraAudit](solutions/atlassianjiraaudit.md)

**Tables (1):** `Jira_Audit_CL`

The [Atlassian Jira](https://www.atlassian.com/software/jira) Audit data connector provides the capability to ingest [Jira Audit Records](https://support.atlassian.com/jira-cloud-administration/docs/audit-activities-in-jira-applications/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/jiraauditapi.md)

---

### [Atlassian Jira Audit (using REST API)](connectors/jiraauditccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [AtlassianJiraAudit](solutions/atlassianjiraaudit.md)

**Tables (1):** `Jira_Audit_v2_CL`

The [Atlassian Jira](https://www.atlassian.com/software/jira) Audit data connector provides the capability to ingest [Jira Audit Records](https://support.atlassian.com/jira-cloud-administration/docs/audit-activities-in-jira-applications/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/jiraauditccpdefinition.md)

---

### [Auth0 Access Management](connectors/auth0.md)

**Publisher:** Auth0

**Solution:** [Auth0](solutions/auth0.md)

**Tables (1):** `Auth0AM_CL`

The [Auth0 Access Management](https://auth0.com/access-management) data connector provides the capability to ingest [Auth0 log events](https://auth0.com/docs/api/management/v2/#!/Logs/get_logs) into Microsoft Sentinel

[→ View full connector details](connectors/auth0.md)

---

### [Auth0 Logs](connectors/auth0connectorccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Auth0](solutions/auth0.md)

**Tables (1):** `Auth0Logs_CL`

The [Auth0](https://auth0.com/docs/api/management/v2/logs/get-logs) data connector allows ingesting logs from Auth0 API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses Auth0 API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

[→ View full connector details](connectors/auth0connectorccpdefinition.md)

---

### [Authomize Data Connector](connectors/authomize.md)

**Publisher:** Authomize

**Solution:** [Authomize](solutions/authomize.md)

**Tables (1):** `Authomize_v2_CL`

The Authomize Data Connector provides the capability to ingest custom log types from Authomize into Microsoft Sentinel.

[→ View full connector details](connectors/authomize.md)

---

### [Automated Logic WebCTRL ](connectors/automatedlogicwebctrl.md)

**Publisher:** AutomatedLogic

**Solution:** [ALC-WebCTRL](solutions/alc-webctrl.md)

**Tables (1):** `Event`

You can stream the audit logs from the WebCTRL SQL server hosted on Windows machines connected to your Microsoft Sentinel. This connection enables you to view dashboards, create custom alerts and improve investigation. This gives insights into your Industrial Control Systems that are monitored or controlled by the WebCTRL BAS application.

[→ View full connector details](connectors/automatedlogicwebctrl.md)

---

### [Azure Activity](connectors/azureactivity.md)

**Publisher:** Microsoft

**Solution:** [Azure Activity](solutions/azure-activity.md)

**Tables (1):** `AzureActivity`

Azure Activity Log is a subscription log that provides insight into subscription-level events that occur in Azure, including events from Azure Resource Manager operational data, service health events, write operations taken on the resources in your subscription, and the status of activities performed in Azure. For more information, see the [Microsoft Sentinel documentation ](https://go.microsoft.com/fwlink/p/?linkid=2219695&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/azureactivity.md)

---

### [Azure CloudNGFW By Palo Alto Networks](connectors/azurecloudngfwbypaloaltonetworks.md)

**Publisher:** Palo Alto Networks

**Solution:** [Azure Cloud NGFW by Palo Alto Networks](solutions/azure-cloud-ngfw-by-palo-alto-networks.md)

**Tables (1):** `fluentbit_CL`

Cloud Next-Generation Firewall by Palo Alto Networks - an Azure Native ISV Service - is Palo Alto Networks Next-Generation Firewall (NGFW) delivered as a cloud-native service on Azure. You can discover Cloud NGFW in the Azure Marketplace and consume it in your Azure Virtual Networks (VNet). With Cloud NGFW, you can access the core NGFW capabilities such as App-ID, URL filtering based technologies. It provides threat prevention and detection through cloud-delivered security services and threat prevention signatures. The connector allows you to easily connect your Cloud NGFW logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities. For more information, see the [Cloud NGFW for Azure documentation](https://docs.paloaltonetworks.com/cloud-ngfw/azure).

[→ View full connector details](connectors/azurecloudngfwbypaloaltonetworks.md)

---

### [Azure DevOps Audit Logs (via Codeless Connector Platform)](connectors/azuredevopsauditlogs.md)

**Publisher:** Microsoft

**Solution:** [AzureDevOpsAuditing](solutions/azuredevopsauditing.md)

**Tables (1):** `ADOAuditLogs_CL`

The Azure DevOps Audit Logs data connector allows you to ingest audit events from Azure DevOps into Microsoft Sentinel. This data connector is built using the Microsoft Sentinel Codeless Connector Platform, ensuring seamless integration. It leverages the Azure DevOps Audit Logs API to fetch detailed audit events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview). These transformations enable parsing of the received audit data into a custom table during ingestion, improving query performance by eliminating the need for additional parsing. By using this connector, you can gain enhanced visibility into your Azure DevOps environment and streamline your security operations.

[→ View full connector details](connectors/azuredevopsauditlogs.md)

---

## B

### [BETTER Mobile Threat Defense (MTD)](connectors/bettermtd.md)

**Publisher:** BETTER Mobile

**Solution:** [BETTER Mobile Threat Defense (MTD)](solutions/better-mobile-threat-defense-(mtd).md)

**Tables (4):** `BetterMTDAppLog_CL`, `BetterMTDDeviceLog_CL`, `BetterMTDIncidentLog_CL`, `BetterMTDNetflowLog_CL`

The BETTER MTD Connector allows Enterprises to connect their Better MTD instances with Microsoft Sentinel, to view their data in Dashboards, create custom alerts, use it to trigger playbooks and expands threat hunting capabilities. This gives users more insight into their organization's mobile devices and ability to quickly analyze current mobile security posture which improves their overall SecOps capabilities.

[→ View full connector details](connectors/bettermtd.md)

---

### [Beyond Security beSECURE](connectors/beyondsecuritybesecure.md)

**Publisher:** Beyond Security

**Solution:** [Beyond Security beSECURE](solutions/beyond-security-besecure.md)

**Tables (3):** `beSECURE_Audit_CL`, `beSECURE_ScanEvent_CL`, `beSECURE_ScanResults_CL`

The [Beyond Security beSECURE](https://beyondsecurity.com/) connector allows you to easily connect your Beyond Security beSECURE scan events, scan results and audit trail with Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/beyondsecuritybesecure.md)

---

### [BigID DSPM connector](connectors/bigiddspmlogsconnectordefinition.md)

**Publisher:** BigID

**Solution:** [BigID](solutions/bigid.md)

**Tables (1):** `BigIDDSPMCatalog_CL`

The [BigID DSPM](https://bigid.com/data-security-posture-management/) data connector provides the capability to ingest BigID DSPM cases with affected objects and datasource information into Microsoft Sentinel.

[→ View full connector details](connectors/bigiddspmlogsconnectordefinition.md)

---

### [Bitglass](connectors/bitglass.md)

**Publisher:** Bitglass

**Solution:** [Bitglass](solutions/bitglass.md)

**Tables (1):** `BitglassLogs_CL`

The [Bitglass](https://www.bitglass.com/) data connector provides the capability to retrieve security event logs of the Bitglass services and more events into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/bitglass.md)

---

### [Bitsight data connector](connectors/bitsight.md)

**Publisher:** BitSight Technologies, Inc.

**Solution:** [BitSight](solutions/bitsight.md)

**Tables (11):** `BitsightAlerts_data_CL`, `BitsightBreaches_data_CL`, `BitsightCompany_details_CL`, `BitsightCompany_rating_details_CL`, `BitsightDiligence_historical_statistics_CL`, `BitsightDiligence_statistics_CL`, `BitsightFindings_data_CL`, `BitsightFindings_summary_CL`, `BitsightGraph_data_CL`, `BitsightIndustrial_statistics_CL`, `BitsightObservation_statistics_CL`

The [BitSight](https://www.BitSight.com/) Data Connector supports evidence-based cyber risk monitoring by bringing BitSight data in Microsoft Sentinel.

[→ View full connector details](connectors/bitsight.md)

---

### [Bitwarden Event Logs](connectors/bitwardeneventlogs.md)

**Publisher:** Bitwarden Inc

**Solution:** [Bitwarden](solutions/bitwarden.md)

**Tables (3):** `BitwardenEventLogs_CL`, `BitwardenGroups_CL`, `BitwardenMembers_CL`

This connector provides insight into activity of your Bitwarden organization such as user's activity (logged in, changed password, 2fa, etc.), cipher activity (created, updated, deleted, shared, etc.), collection activity, organization activity, and more.

[→ View full connector details](connectors/bitwardeneventlogs.md)

---

### [Bloodhound Enterprise](connectors/bloodhoundenterprise.md)

**Publisher:** SpecterOps

**Solution:** [BloodHound Enterprise](solutions/bloodhound-enterprise.md)

**Tables (1):** `BHEAttackPathsData_CL`

The solution is designed to test Bloodhound Enterprise package creation process.

[→ View full connector details](connectors/bloodhoundenterprise.md)

---

### [Box](connectors/boxdataconnector.md)

**Publisher:** Box

**Solution:** [Box](solutions/box.md)

**Tables (1):** `BoxEvents_CL`

The Box data connector provides the capability to ingest [Box enterprise's events](https://developer.box.com/guides/events/#admin-events) into Microsoft Sentinel using the Box REST API. Refer to [Box  documentation](https://developer.box.com/guides/events/enterprise-events/for-enterprise/) for more information.

[→ View full connector details](connectors/boxdataconnector.md)

---

### [Box Events (CCP)](connectors/boxeventsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Box](solutions/box.md)

**Tables (2):** `BoxEventsV2_CL`, `BoxEvents_CL`

The Box data connector provides the capability to ingest [Box enterprise's events](https://developer.box.com/guides/events/#admin-events) into Microsoft Sentinel using the Box REST API. Refer to [Box  documentation](https://developer.box.com/guides/events/enterprise-events/for-enterprise/) for more information.

[→ View full connector details](connectors/boxeventsccpdefinition.md)

---

## C

### [CITRIX SECURITY ANALYTICS](connectors/citrix.md)

**Publisher:** CITRIX

**Solution:** [Citrix Analytics for Security](solutions/citrix-analytics-for-security.md)

**Tables (4):** `CitrixAnalytics_indicatorEventDetails_CL`, `CitrixAnalytics_indicatorSummary_CL`, `CitrixAnalytics_riskScoreChange_CL`, `CitrixAnalytics_userProfile_CL`

Citrix Analytics (Security) integration with Microsoft Sentinel helps you to export data analyzed for risky events from Citrix Analytics (Security) into Microsoft Sentinel environment. You can create custom dashboards, analyze data from other sources along with that from Citrix Analytics (Security) and create custom workflows using Logic Apps to monitor and mitigate security events.

[→ View full connector details](connectors/citrix.md)

---

### [CTERA Syslog](connectors/ctera.md)

**Publisher:** CTERA Networks Ltd

**Solution:** [CTERA](solutions/ctera.md)

**Tables (1):** `Syslog`

The CTERA Data Connector for Microsoft Sentinel offers monitoring and threat detection capabilities for your CTERA solution.
 It includes a workbook visualizing the sum of all operations per type, deletions, and denied access operations.
 It also provides analytic rules which detects ransomware incidents and alert you when a user is blocked due to suspicious ransomware activity.
 Additionally, it helps you identify critical patterns such as mass access denied events, mass deletions, and mass permission changes, enabling proactive threat management and response.

[→ View full connector details](connectors/ctera.md)

---

### [CYFIRMA Attack Surface](connectors/cyfirmaattacksurfacealertsconnector.md)

**Publisher:** Microsoft

**Solution:** [Cyfirma Attack Surface](solutions/cyfirma-attack-surface.md)

**Tables (6):** `CyfirmaASCertificatesAlerts_CL`, `CyfirmaASCloudWeaknessAlerts_CL`, `CyfirmaASConfigurationAlerts_CL`, `CyfirmaASDomainIPReputationAlerts_CL`, `CyfirmaASDomainIPVulnerabilityAlerts_CL`, `CyfirmaASOpenPortsAlerts_CL`

[→ View full connector details](connectors/cyfirmaattacksurfacealertsconnector.md)

---

### [CYFIRMA Brand Intelligence](connectors/cyfirmabrandintelligencealertsdc.md)

**Publisher:** Microsoft

**Solution:** [Cyfirma Brand Intelligence](solutions/cyfirma-brand-intelligence.md)

**Tables (5):** `CyfirmaBIDomainITAssetAlerts_CL`, `CyfirmaBIExecutivePeopleAlerts_CL`, `CyfirmaBIMaliciousMobileAppsAlerts_CL`, `CyfirmaBIProductSolutionAlerts_CL`, `CyfirmaBISocialHandlersAlerts_CL`

[→ View full connector details](connectors/cyfirmabrandintelligencealertsdc.md)

---

### [CYFIRMA Compromised Accounts](connectors/cyfirmacompromisedaccountsdataconnector.md)

**Publisher:** Microsoft

**Solution:** [Cyfirma Compromised Accounts](solutions/cyfirma-compromised-accounts.md)

**Tables (1):** `CyfirmaCompromisedAccounts_CL`

The CYFIRMA Compromised Accounts data connector enables seamless log ingestion from the DeCYFIR/DeTCT API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR/DeTCT API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

[→ View full connector details](connectors/cyfirmacompromisedaccountsdataconnector.md)

---

### [CYFIRMA Cyber Intelligence](connectors/cyfirmacyberintelligencedc.md)

**Publisher:** Microsoft

**Solution:** [Cyfirma Cyber Intelligence](solutions/cyfirma-cyber-intelligence.md)

**Tables (4):** `CyfirmaCampaigns_CL`, `CyfirmaIndicators_CL`, `CyfirmaMalware_CL`, `CyfirmaThreatActors_CL`

The CYFIRMA Cyber Intelligence data connector enables seamless log ingestion from the DeCYFIR API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR Alerts API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

[→ View full connector details](connectors/cyfirmacyberintelligencedc.md)

---

### [CYFIRMA Digital Risk](connectors/cyfirmadigitalriskalertsconnector.md)

**Publisher:** Microsoft

**Solution:** [Cyfirma Digital Risk](solutions/cyfirma-digital-risk.md)

**Tables (7):** `CyfirmaDBWMDarkWebAlerts_CL`, `CyfirmaDBWMPhishingAlerts_CL`, `CyfirmaDBWMRansomwareAlerts_CL`, `CyfirmaSPEConfidentialFilesAlerts_CL`, `CyfirmaSPEPIIAndCIIAlerts_CL`, `CyfirmaSPESocialThreatAlerts_CL`, `CyfirmaSPESourceCodeAlerts_CL`

The CYFIRMA Digital Risk Alerts data connector enables seamless log ingestion from the DeCYFIR/DeTCT API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR Alerts API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

[→ View full connector details](connectors/cyfirmadigitalriskalertsconnector.md)

---

### [CYFIRMA Vulnerabilities Intelligence](connectors/cyfirmavulnerabilitiesinteldc.md)

**Publisher:** Microsoft

**Solution:** [Cyfirma Vulnerabilities Intel](solutions/cyfirma-vulnerabilities-intel.md)

**Tables (1):** `CyfirmaVulnerabilities_CL`

The CYFIRMA Vulnerabilities Intelligence data connector enables seamless log ingestion from the DeCYFIR API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the CYFIRMA API's to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

[→ View full connector details](connectors/cyfirmavulnerabilitiesinteldc.md)

---

### [Check Point CloudGuard CNAPP Connector for Microsoft Sentinel](connectors/cloudguardccpdefinition.md)

**Publisher:** CheckPoint

**Solution:** [Check Point CloudGuard CNAPP](solutions/check-point-cloudguard-cnapp.md)

**Tables (1):** `CloudGuard_SecurityEvents_CL`

The [CloudGuard](https://sc1.checkpoint.com/documents/CloudGuard_Dome9/Documentation/Overview/CloudGuard-CSPM-Introduction.htm?cshid=help_center_documentation) data connector enables the ingestion of security events from the CloudGuard API into Microsoft Sentinel™, using Microsoft Sentinel’s Codeless Connector Platform. The connector supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) which parses incoming security event data into custom columns. This pre-parsing process eliminates the need for query-time parsing, resulting in improved performance for data queries.

[→ View full connector details](connectors/cloudguardccpdefinition.md)

---

### [Check Point Cyberint Alerts Connector (via Codeless Connector Platform)](connectors/checkpointcyberintalerts.md)

**Publisher:** Checkpoint Cyberint

**Solution:** [Check Point Cyberint Alerts](solutions/check-point-cyberint-alerts.md)

**Tables (1):** `argsentdc_CL`

Cyberint, a Check Point company, provides a Microsoft Sentinel integration to streamline critical Alerts and bring enriched threat intelligence from the Infinity External Risk Management solution into Microsoft Sentinel. This simplifies the process of tracking the status of tickets with automatic sync updates across systems. Using this new integration for Microsoft Sentinel, existing Cyberint and Microsoft Sentinel customers can easily pull logs based on Cyberint's findings into Microsoft Sentinel platform.

[→ View full connector details](connectors/checkpointcyberintalerts.md)

---

### [Check Point Cyberint IOC Connector](connectors/checkpointcyberintioc.md)

**Publisher:** Checkpoint Cyberint

**Solution:** [Check Point Cyberint IOC](solutions/check-point-cyberint-ioc.md)

**Tables (1):** `iocsent_CL`

This is data connector for Check Point Cyberint IOC.

[→ View full connector details](connectors/checkpointcyberintioc.md)

---

### [Cisco Cloud Security](connectors/ciscoumbrelladataconnector.md)

**Publisher:** Cisco

**Solution:** [CiscoUmbrella](solutions/ciscoumbrella.md)

**Tables (12):** `Cisco_Umbrella_audit_CL`, `Cisco_Umbrella_cloudfirewall_CL`, `Cisco_Umbrella_dlp_CL`, `Cisco_Umbrella_dns_CL`, `Cisco_Umbrella_fileevent_CL`, `Cisco_Umbrella_firewall_CL`, `Cisco_Umbrella_intrusion_CL`, `Cisco_Umbrella_ip_CL`, `Cisco_Umbrella_proxy_CL`, `Cisco_Umbrella_ravpnlogs_CL`, `Cisco_Umbrella_ztaflow_CL`, `Cisco_Umbrella_ztna_CL`

The Cisco Cloud Security solution for Microsoft Sentinel enables you to ingest [Cisco Secure Access](https://docs.sse.cisco.com/sse-user-guide/docs/welcome-cisco-secure-access) and [Cisco Umbrella](https://docs.umbrella.com/umbrella-user-guide/docs/getting-started) [logs](https://docs.sse.cisco.com/sse-user-guide/docs/manage-your-logs) stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API. Refer to [Cisco Cloud Security log management documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management) for more information.

[→ View full connector details](connectors/ciscoumbrelladataconnector.md)

---

### [Cisco Cloud Security (using elastic premium plan)](connectors/ciscoumbrelladataconnectorelasticpremium.md)

**Publisher:** Cisco

**Solution:** [CiscoUmbrella](solutions/ciscoumbrella.md)

**Tables (12):** `Cisco_Umbrella_audit_CL`, `Cisco_Umbrella_cloudfirewall_CL`, `Cisco_Umbrella_dlp_CL`, `Cisco_Umbrella_dns_CL`, `Cisco_Umbrella_fileevent_CL`, `Cisco_Umbrella_firewall_CL`, `Cisco_Umbrella_intrusion_CL`, `Cisco_Umbrella_ip_CL`, `Cisco_Umbrella_proxy_CL`, `Cisco_Umbrella_ravpnlogs_CL`, `Cisco_Umbrella_ztaflow_CL`, `Cisco_Umbrella_ztna_CL`

The Cisco Umbrella data connector provides the capability to ingest [Cisco Umbrella](https://docs.umbrella.com/) events stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API. Refer to [Cisco Umbrella log management documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management) for more information.

**NOTE:** This data connector uses the [Azure Functions Premium Plan](https://learn.microsoft.com/azure/azure-functions/functions-premium-plan?tabs=portal) to enable secure ingestion capabilities and will incur additional costs. More pricing details are [here](https://azure.microsoft.com/pricing/details/functions/?msockid=2f4366822d836a7c2ac673462cfc6ba8#pricing).

[→ View full connector details](connectors/ciscoumbrelladataconnectorelasticpremium.md)

---

### [Cisco Duo Security](connectors/ciscoduosecurity.md)

**Publisher:** Cisco

**Solution:** [CiscoDuoSecurity](solutions/ciscoduosecurity.md)

**Tables (1):** `CiscoDuo_CL`

The Cisco Duo Security data connector provides the capability to ingest [authentication logs](https://duo.com/docs/adminapi#authentication-logs), [administrator logs](https://duo.com/docs/adminapi#administrator-logs), [telephony logs](https://duo.com/docs/adminapi#telephony-logs), [offline enrollment logs](https://duo.com/docs/adminapi#offline-enrollment-logs) and [Trust Monitor events](https://duo.com/docs/adminapi#trust-monitor) into Microsoft Sentinel using the Cisco Duo Admin API. Refer to [API documentation](https://duo.com/docs/adminapi) for more information.

[→ View full connector details](connectors/ciscoduosecurity.md)

---

### [Cisco ETD](connectors/ciscoetd.md)

**Publisher:** Cisco

**Solution:** [Cisco ETD](solutions/cisco-etd.md)

**Tables (1):** `CiscoETD_CL`

The connector fetches data from ETD api for threat analysis

[→ View full connector details](connectors/ciscoetd.md)

---

### [Cisco Meraki (using REST API)](connectors/ciscomerakimultirule.md)

**Publisher:** Microsoft

**Solution:** [Cisco Meraki Events via REST API](solutions/cisco-meraki-events-via-rest-api.md)

**Tables (3):** `ASimAuditEventLogs`, `ASimNetworkSessionLogs`, `ASimWebSessionLogs`

The [Cisco Meraki](https://aka.ms/ciscomeraki) connector allows you to easily connect your Cisco Meraki organization events (Security events, Configuration Changes and API Requests) to Microsoft Sentinel. The data connector uses the [Cisco Meraki REST API](https://developer.cisco.com/meraki/api-v1/#!get-organization-appliance-security-events) to fetch logs and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received data and ingests into ASIM and custom tables in your Log Analytics workspace. This data connector benefits from capabilities such as DCR based ingestion-time filtering, data normalization.

 **Supported ASIM schema:** 
 1. Network Session 
 2. Web Session  
 3. Audit Event

[→ View full connector details](connectors/ciscomerakimultirule.md)

---

### [Cisco Meraki (using REST API)](connectors/ciscomerakinativepoller.md)

**Publisher:** Microsoft

**Solution:** [CiscoMeraki](solutions/ciscomeraki.md)

**Tables (2):** `CiscoMerakiNativePoller_CL`, `meraki_CL`

The [Cisco Meraki](https://aka.ms/ciscomeraki) connector allows you to easily connect your Cisco Meraki MX [security events](https://aka.ms/ciscomerakisecurityevents) to Microsoft Sentinel. The data connector uses [Cisco Meraki REST API](https://developer.cisco.com/meraki/api-v1/#!get-organization-appliance-security-events) to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

 **Supported ASIM schema:** 
 1. Network Session

[→ View full connector details](connectors/ciscomerakinativepoller.md)

---

### [Cisco Secure Endpoint (via Codeless Connector Framework)](connectors/ciscosecureendpointlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Cisco Secure Endpoint](solutions/cisco-secure-endpoint.md)

**Tables (2):** `CiscoSecureEndpointAuditLogsV2_CL`, `CiscoSecureEndpointEventsV2_CL`

The Cisco Secure Endpoint (formerly AMP for Endpoints) data connector provides the capability to ingest Cisco Secure Endpoint [audit logs](https://developer.cisco.com/docs/secure-endpoint/auditlog/) and [events](https://developer.cisco.com/docs/secure-endpoint/v1-api-reference-event/) into Microsoft Sentinel.

[→ View full connector details](connectors/ciscosecureendpointlogsccpdefinition.md)

---

### [Cisco Software Defined WAN](connectors/ciscosdwan.md)

**Publisher:** Cisco

**Solution:** [Cisco SD-WAN](solutions/cisco-sd-wan.md)

**Tables (2):** `CiscoSDWANNetflow_CL`, `Syslog`

The Cisco Software Defined WAN(SD-WAN) data connector provides the capability to ingest [Cisco SD-WAN](https://www.cisco.com/c/en_in/solutions/enterprise-networks/sd-wan/index.html) Syslog and Netflow data into Microsoft Sentinel.

[→ View full connector details](connectors/ciscosdwan.md)

---

### [Claroty xDome](connectors/clarotyxdome.md)

**Publisher:** Claroty

**Solution:** [Claroty xDome](solutions/claroty-xdome.md)

**Tables (1):** `CommonSecurityLog`

[Claroty](https://claroty.com/) xDome delivers comprehensive security and alert management capabilities for healthcare and industrial network environments. It is designed to map multiple source types, identify the collected data, and integrate it into Microsoft Sentinel data models. This results in the ability to monitor all potential threats in your healthcare and industrial environments in one location, leading to more effective security monitoring and a stronger security posture.

[→ View full connector details](connectors/clarotyxdome.md)

---

### [Cloudflare (Using Blob Container) (via Codeless Connector Framework)](connectors/cloudflaredefinition.md)

**Publisher:** Microsoft

**Solution:** [Cloudflare](solutions/cloudflare.md)

**Tables (1):** `CloudflareV2_CL`

 The Cloudflare data connector provides the capability to ingest Cloudflare logs into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare documentation](https://developers.cloudflare.com/logs/about/)for more information.

[→ View full connector details](connectors/cloudflaredefinition.md)

---

### [Cofense Intelligence Threat Indicators Ingestion](connectors/cofenseintelligence.md)

**Publisher:** Cofense

**Solution:** [CofenseIntelligence](solutions/cofenseintelligence.md)

**Tables (2):** `Malware_Data_CL`, `ThreatIntelligenceIndicator`

The [Cofense-Intelligence](https://cofense.com/product-services/phishing-intelligence/) data connector provides the following capabilities: 
 1. CofenseToSentinel : 
 >* Get Threat Indicators from the Cofense Intelligence platform and create Threat Intelligence Indicators in Microsoft Sentinel. 
 2. SentinelToDefender : 
 >* Get Malware from Cofense Intelligence and post to custom logs table. 
 3. CofenseIntelligenceMalware : 
 >* Get Cofense Intelligence Threat Intelligence Indicators from Microsoft Sentinel Threat Intelligence and create/update Indicators in Microsoft Defender for Endpoints.
 4. DownloadThreatReports : 
 >* This data connector will fetch the malware data and create the Link from which we can download Threat Reports. 
 5. RetryFailedIndicators : 
 >* This data connector will fetch failed indicators from failed indicators file and retry creating/updating Threat Intelligence indicators in Microsoft Sentinel. 


 For more details of REST APIs refer to the below documentations: 
 1. Cofense Intelligence API documentation: 
> https://www.threathq.com/docs/rest_api_reference.html 
 2. Microsoft Threat Intelligence Indicator documentation: 
> https://learn.microsoft.com/rest/api/securityinsights/preview/threat-intelligence-indicator 
 3. Microsoft Defender for Endpoints Indicator documentation: 
> https://learn.microsoft.com/microsoft-365/security/defender-endpoint/ti-indicator?view=o365-worldwide

[→ View full connector details](connectors/cofenseintelligence.md)

---

### [Cofense Triage Threat Indicators Ingestion](connectors/cofensetriage.md)

**Publisher:** Cofense

**Solution:** [CofenseTriage](solutions/cofensetriage.md)

**Tables (3):** `Cofense_Triage_failed_indicators_CL`, `Report_links_data_CL`, `ThreatIntelligenceIndicator`

The [Cofense-Triage](https://cofense.com/product-services/cofense-triage/) data connector provides the following capabilities: 
 1. CofenseBasedIndicatorCreator : 
 >* Get Threat Indicators from the Cofense Triage platform and create Threat Intelligence Indicators in Microsoft Sentinel. 
 > * Ingest Cofense Indicator ID and report links into custom logs table. 
 2. NonCofenseBasedIndicatorCreatorToCofense : 
 >* Get Non-Cofense Threat Intelligence Indicators from Microsoft Sentinel Threat Intelligence and create/update Indicators in Cofense Triage platform. 
 3. IndicatorCreatorToDefender : 
 >* Get Cofense Triage Threat Intelligence Indicators from Microsoft Sentinel Threat Intelligence and create/update Indicators in Microsoft Defender for Endpoints. 
 4. RetryFailedIndicators : 
 >* Get failed indicators from failed indicators files and retry creating/updating Threat Intelligence indicators in Microsoft Sentinel. 


 For more details of REST APIs refer to the below two documentations: 
 1. Cofense API documentation: 
> https://`<your-cofense-instance-name>`/docs/api/v2/index.html 
 2. Microsoft Threat Intelligence Indicator documentation: 
> https://learn.microsoft.com/rest/api/securityinsights/preview/threat-intelligence-indicator 
 3. Microsoft Defender for Endpoints Indicator documentation: 
> https://learn.microsoft.com/microsoft-365/security/defender-endpoint/ti-indicator?view=o365-worldwide

[→ View full connector details](connectors/cofensetriage.md)

---

### [Cognni](connectors/cognnisentineldataconnector.md)

**Publisher:** Cognni

**Solution:** [Cognni](solutions/cognni.md)

**Tables (1):** `CognniIncidents_CL`

The Cognni connector offers a quick and simple integration with Microsoft Sentinel. You can use Cognni to autonomously map your previously unclassified important information and detect related incidents. This allows you to recognize risks to your important information, understand the severity of the incidents, and investigate the details you need to remediate, fast enough to make a difference.

[→ View full connector details](connectors/cognnisentineldataconnector.md)

---

### [Cohesity](connectors/cohesitydataconnector.md)

**Publisher:** Cohesity

**Solution:** [CohesitySecurity](solutions/cohesitysecurity.md)

**Tables (1):** `Cohesity_CL`

The Cohesity function apps provide the ability to ingest Cohesity Datahawk ransomware alerts into Microsoft Sentinel.

[→ View full connector details](connectors/cohesitydataconnector.md)

---

### [CommvaultSecurityIQ](connectors/commvaultsecurityiq-cl.md)

**Publisher:** Commvault

**Solution:** [Commvault Security IQ](solutions/commvault-security-iq.md)

**Tables (1):** `CommvaultSecurityIQ_CL`

This Azure Function enables Commvault users to ingest alerts/events into their Microsoft Sentinel instance. With Analytic Rules,Microsoft Sentinel can automatically create Microsoft Sentinel incidents from incoming events and logs.

[→ View full connector details](connectors/commvaultsecurityiq-cl.md)

---

### [ContrastADR](connectors/contrastadr.md)

**Publisher:** Contrast Security

**Solution:** [ContrastADR](solutions/contrastadr.md)

**Tables (2):** `ContrastADRIncident_CL`, `ContrastADR_CL`

The ContrastADR data connector provides the capability to ingest Contrast ADR attack events into Microsoft Sentinel using the ContrastADR Webhook. ContrastADR data connector can enrich the incoming webhook data with ContrastADR API enrichment calls.

[→ View full connector details](connectors/contrastadr.md)

---

### [Corelight Connector Exporter](connectors/corelightconnectorexporter.md)

**Publisher:** Corelight

**Solution:** [Corelight](solutions/corelight.md)

**Tables (108):** `Corelight_CL`, `Corelight_v2_bacnet_CL`, `Corelight_v2_capture_loss_CL`, `Corelight_v2_cip_CL`, `Corelight_v2_conn_CL`, `Corelight_v2_conn_long_CL`, `Corelight_v2_conn_red_CL`, `Corelight_v2_corelight_burst_CL`, `Corelight_v2_corelight_overall_capture_loss_CL`, `Corelight_v2_corelight_profiling_CL`, `Corelight_v2_datared_CL`, `Corelight_v2_dce_rpc_CL`, `Corelight_v2_dga_CL`, `Corelight_v2_dhcp_CL`, `Corelight_v2_dnp3_CL`, `Corelight_v2_dns_CL`, `Corelight_v2_dns_red_CL`, `Corelight_v2_dpd_CL`, `Corelight_v2_encrypted_dns_CL`, `Corelight_v2_enip_CL`, `Corelight_v2_enip_debug_CL`, `Corelight_v2_enip_list_identity_CL`, `Corelight_v2_etc_viz_CL`, `Corelight_v2_files_CL`, `Corelight_v2_files_red_CL`, `Corelight_v2_ftp_CL`, `Corelight_v2_generic_dns_tunnels_CL`, `Corelight_v2_generic_icmp_tunnels_CL`, `Corelight_v2_http2_CL`, `Corelight_v2_http_CL`, `Corelight_v2_http_red_CL`, `Corelight_v2_icmp_specific_tunnels_CL`, `Corelight_v2_intel_CL`, `Corelight_v2_ipsec_CL`, `Corelight_v2_irc_CL`, `Corelight_v2_iso_cotp_CL`, `Corelight_v2_kerberos_CL`, `Corelight_v2_known_certs_CL`, `Corelight_v2_known_devices_CL`, `Corelight_v2_known_domains_CL`, `Corelight_v2_known_hosts_CL`, `Corelight_v2_known_names_CL`, `Corelight_v2_known_remotes_CL`, `Corelight_v2_known_services_CL`, `Corelight_v2_known_users_CL`, `Corelight_v2_local_subnets_CL`, `Corelight_v2_local_subnets_dj_CL`, `Corelight_v2_local_subnets_graphs_CL`, `Corelight_v2_log4shell_CL`, `Corelight_v2_modbus_CL`, `Corelight_v2_mqtt_connect_CL`, `Corelight_v2_mqtt_publish_CL`, `Corelight_v2_mqtt_subscribe_CL`, `Corelight_v2_mysql_CL`, `Corelight_v2_notice_CL`, `Corelight_v2_ntlm_CL`, `Corelight_v2_ntp_CL`, `Corelight_v2_ocsp_CL`, `Corelight_v2_openflow_CL`, `Corelight_v2_packet_filter_CL`, `Corelight_v2_pe_CL`, `Corelight_v2_profinet_CL`, `Corelight_v2_profinet_dce_rpc_CL`, `Corelight_v2_profinet_debug_CL`, `Corelight_v2_radius_CL`, `Corelight_v2_rdp_CL`, `Corelight_v2_reporter_CL`, `Corelight_v2_rfb_CL`, `Corelight_v2_s7comm_CL`, `Corelight_v2_signatures_CL`, `Corelight_v2_sip_CL`, `Corelight_v2_smartpcap_CL`, `Corelight_v2_smartpcap_stats_CL`, `Corelight_v2_smb_files_CL`, `Corelight_v2_smb_mapping_CL`, `Corelight_v2_smtp_CL`, `Corelight_v2_smtp_links_CL`, `Corelight_v2_snmp_CL`, `Corelight_v2_socks_CL`, `Corelight_v2_software_CL`, `Corelight_v2_specific_dns_tunnels_CL`, `Corelight_v2_ssh_CL`, `Corelight_v2_ssl_CL`, `Corelight_v2_ssl_red_CL`, `Corelight_v2_stats_CL`, `Corelight_v2_stepping_CL`, `Corelight_v2_stun_CL`, `Corelight_v2_stun_nat_CL`, `Corelight_v2_suricata_corelight_CL`, `Corelight_v2_suricata_eve_CL`, `Corelight_v2_suricata_stats_CL`, `Corelight_v2_suricata_zeek_stats_CL`, `Corelight_v2_syslog_CL`, `Corelight_v2_tds_CL`, `Corelight_v2_tds_rpc_CL`, `Corelight_v2_tds_sql_batch_CL`, `Corelight_v2_traceroute_CL`, `Corelight_v2_tunnel_CL`, `Corelight_v2_unknown_smartpcap_CL`, `Corelight_v2_util_stats_CL`, `Corelight_v2_vpn_CL`, `Corelight_v2_weird_CL`, `Corelight_v2_weird_red_CL`, `Corelight_v2_weird_stats_CL`, `Corelight_v2_wireguard_CL`, `Corelight_v2_x509_CL`, `Corelight_v2_x509_red_CL`, `Corelight_v2_zeek_doctor_CL`

The [Corelight](https://corelight.com/) data connector enables incident responders and threat hunters who use Microsoft Sentinel to work faster and more effectively. The data connector enables ingestion of events from [Zeek](https://zeek.org/) and [Suricata](https://suricata-ids.org/) via Corelight Sensors into Microsoft Sentinel.

[→ View full connector details](connectors/corelightconnectorexporter.md)

---

### [Cribl](connectors/cribl.md)

**Publisher:** Cribl

**Solution:** [Cribl](solutions/cribl.md)

**Tables (4):** `CriblAccess_CL`, `CriblAudit_CL`, `CriblInternal_CL`, `CriblUIAccess_CL`

The [Cribl](https://cribl.io/accelerate-cloud-migration/) connector allows you to easily connect your Cribl (Cribl Enterprise Edition - Standalone) logs with Microsoft Sentinel. This gives you more security insight into your organization's data pipelines.

[→ View full connector details](connectors/cribl.md)

---

### [CrowdStrike API Data Connector (via Codeless Connector Framework)](connectors/crowdstrikeapiccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [CrowdStrike Falcon Endpoint Protection](solutions/crowdstrike-falcon-endpoint-protection.md)

**Tables (5):** `CrowdStrikeAlerts`, `CrowdStrikeDetections`, `CrowdStrikeHosts`, `CrowdStrikeIncidents`, `CrowdStrikeVulnerabilities`

The [CrowdStrike Data Connector](https://www.crowdstrike.com/) allows ingesting logs from the CrowdStrike API into Microsoft Sentinel. This connector is built on the Microsoft Sentinel Codeless Connector Platform and uses the CrowdStrike API to fetch logs for Alerts, Detections, Hosts, Incidents, and Vulnerabilities. It supports DCR-based ingestion time transformations so that queries can run more efficiently.

[→ View full connector details](connectors/crowdstrikeapiccpdefinition.md)

---

### [CrowdStrike Falcon Adversary Intelligence ](connectors/crowdstrikefalconadversaryintelligence.md)

**Publisher:** CrowdStrike

**Solution:** [CrowdStrike Falcon Endpoint Protection](solutions/crowdstrike-falcon-endpoint-protection.md)

**Tables (1):** `ThreatIntelligenceIndicator`

The [CrowdStrike](https://www.crowdstrike.com/) Falcon Indicators of Compromise connector retrieves the Indicators of Compromise from the Falcon Intel API and uploads them [Microsoft Sentinel Threat Intel](https://learn.microsoft.com/en-us/azure/sentinel/understand-threat-intelligence).

[→ View full connector details](connectors/crowdstrikefalconadversaryintelligence.md)

---

### [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](connectors/crowdstrikefalcons3ccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [CrowdStrike Falcon Endpoint Protection](solutions/crowdstrike-falcon-endpoint-protection.md)

**Tables (10):** `CrowdStrike_Additional_Events_CL`, `CrowdStrike_Audit_Events_CL`, `CrowdStrike_Auth_Events_CL`, `CrowdStrike_DNS_Events_CL`, `CrowdStrike_File_Events_CL`, `CrowdStrike_Network_Events_CL`, `CrowdStrike_Process_Events_CL`, `CrowdStrike_Registry_Events_CL`, `CrowdStrike_Secondary_Data_CL`, `CrowdStrike_User_Events_CL`

The Crowdstrike Falcon Data Replicator (S3) connector provides the capability to ingest FDR event datainto Microsoft Sentinel from the AWS S3 bucket where the FDR logs have been streamed. The connector provides ability to get events from Falcon Agents which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector requires an IAM role to be configured on AWS to allow access to the AWS S3 bucket and may not be suitable for environments that leverage CrowdStrike - managed buckets.</p><p>3. For environments that leverage CrowdStrike-managed buckets, please configure the <strong>CrowdStrike Falcon Data Replicator (CrowdStrike-Managed AWS S3)</strong> connector.</p></div>

[→ View full connector details](connectors/crowdstrikefalcons3ccpdefinition.md)

---

### [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](connectors/crowdstrikereplicatorv2.md)

**Publisher:** Crowdstrike

**Solution:** [CrowdStrike Falcon Endpoint Protection](solutions/crowdstrike-falcon-endpoint-protection.md)

**Tables (15):** `ASimAuditEventLogs`, `ASimAuthenticationEventLogs`, `ASimAuthenticationEventLogs_CL`, `ASimDnsActivityLogs`, `ASimFileEventLogs`, `ASimFileEventLogs_CL`, `ASimNetworkSessionLogs`, `ASimProcessEventLogs`, `ASimProcessEventLogs_CL`, `ASimRegistryEventLogs`, `ASimRegistryEventLogs_CL`, `ASimUserManagementActivityLogs`, `ASimUserManagementLogs_CL`, `CrowdStrike_Additional_Events_CL`, `CrowdStrike_Secondary_Data_CL`

This connector enables the ingestion of FDR data into Microsoft Sentinel using Azure Functions to support the assessment of potential security risks, analysis of collaboration activities, identification of configuration issues, and other operational insights.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector uses a Key & Secret based authentication and is suitable for CrowdStrike Managed buckets.</p><p>3. For environments that use a fully owned AWS S3 bucket, Microsoft recommends using the <strong>CrowdStrike Falcon Data Replicator (AWS S3)</strong> connector.</p></div>

[→ View full connector details](connectors/crowdstrikereplicatorv2.md)

---

### [Cyber Blind Spot Integration](connectors/cbspollingidazurefunctions.md)

**Publisher:** CTM360

**Solution:** [CTM360](solutions/ctm360.md)

**Tables (1):** `CBSLog_Azure_1_CL`

Through the API integration, you have the capability to retrieve all the issues related to your CBS organizations via a RESTful interface.

[→ View full connector details](connectors/cbspollingidazurefunctions.md)

---

### [CyberArkAudit](connectors/cyberarkaudit.md)

**Publisher:** CyberArk

**Solution:** [CyberArkAudit](solutions/cyberarkaudit.md)

**Tables (2):** `CyberArkAudit`, `CyberArk_AuditEvents_CL`

The [CyberArk Audit](https://docs.cyberark.com/Audit/Latest/en/Content/Resources/_TopNav/cc_Home.htm) data connector provides the capability to retrieve security event logs of the CyberArk Audit service and more events into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/cyberarkaudit.md)

---

### [Cybersixgill Actionable Alerts](connectors/cybersixgillactionablealerts.md)

**Publisher:** Cybersixgill

**Solution:** [Cybersixgill-Actionable-Alerts](solutions/cybersixgill-actionable-alerts.md)

**Tables (1):** `CyberSixgill_Alerts_CL`

Actionable alerts provide customized alerts based on configured assets

[→ View full connector details](connectors/cybersixgillactionablealerts.md)

---

### [Cyborg Security HUNTER Hunt Packages](connectors/cyborgsecurity-hunter.md)

**Publisher:** Cyborg Security

**Solution:** [Cyborg Security HUNTER](solutions/cyborg-security-hunter.md)

**Tables (1):** `SecurityEvent`

Cyborg Security is a leading provider of advanced threat hunting solutions, with a mission to empower organizations with cutting-edge technology and collaborative tools to proactively detect and respond to cyber threats. Cyborg Security's flagship offering, the HUNTER Platform, combines powerful analytics, curated threat hunting content, and comprehensive hunt management capabilities to create a dynamic ecosystem for effective threat hunting operations.

Follow the steps to gain access to Cyborg Security's Community and setup the 'Open in Tool' capabilities in the HUNTER Platform.

[→ View full connector details](connectors/cyborgsecurity-hunter.md)

---

### [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](connectors/cyerafunctionsconnector.md)

**Publisher:** Cyera Inc

**Solution:** [CyeraDSPM](solutions/cyeradspm.md)

**Tables (5):** `CyeraAssets_CL`, `CyeraAssets_MS_CL`, `CyeraClassifications_CL`, `CyeraIdentities_CL`, `CyeraIssues_CL`

The **Cyera DSPM Azure Function Connector** enables seamless ingestion of Cyera’s **Data Security Posture Management (DSPM)** telemetry — *Assets*, *Identities*, *Issues*, and *Classifications* — into **Microsoft Sentinel**.\n\nThis connector uses an **Azure Function App** to call Cyera’s REST API on a schedule, fetch the latest DSPM telemetry, and send it to Microsoft Sentinel through the **Azure Monitor Logs Ingestion API** via a **Data Collection Endpoint (DCE)** and **Data Collection Rule (DCR, kind: Direct)** — no agents required.\n\n**Tables created/used**\n\n| Entity | Table | Purpose |\n|---|---|---|\n| Assets | `CyeraAssets_CL` | Raw asset metadata and data-store context |\n| Identities | `CyeraIdentities_CL` | Identity definitions and sensitivity context |\n| Issues | `CyeraIssues_CL` | Findings and remediation details |\n| Classifications | `CyeraClassifications_CL` | Data class & sensitivity definitions |\n| MS View | `CyeraAssets_MS_CL` | Normalized asset view for dashboards |\n\n> **Note:** This v7 connector supersedes the earlier CCF-based approach and aligns with Microsoft’s recommended Direct ingestion path for Microsoft Sentinel.

[→ View full connector details](connectors/cyerafunctionsconnector.md)

---

### [Cyera DSPM Microsoft Sentinel Data Connector](connectors/cyeradspmccf.md)

**Publisher:** Cyera Inc

**Solution:** [CyeraDSPM](solutions/cyeradspm.md)

**Tables (5):** `CyeraAssets_CL`, `CyeraAssets_MS_CL`, `CyeraClassifications_CL`, `CyeraIdentities_CL`, `CyeraIssues_CL`

The [Cyera DSPM](https://api.cyera.io/) data connector allows you to connect to your Cyera's DSPM tenant and ingesting Classifications, Assets, Issues, and Identity Resources/Definitions into Microsoft Sentinel. The data connector is built on Microsoft Sentinel's Codeless Connector Framework and uses the Cyera's API to fetch Cyera's [DSPM Telemetry](https://www.cyera.com/) once received can be correlated with security events creating custom columns so that queries don't need to parse it again, thus resulting in better performance.

[→ View full connector details](connectors/cyeradspmccf.md)

---

### [Cynerio Security Events](connectors/cyneriosecurityevents.md)

**Publisher:** Cynerio

**Solution:** [Cynerio](solutions/cynerio.md)

**Tables (1):** `CynerioEvent_CL`

The [Cynerio](https://www.cynerio.com/) connector allows you to easily connect your Cynerio Security Events with Microsoft Sentinel, to view IDS Events. This gives you more insight into your organization network security posture and improves your security operation capabilities. 

[→ View full connector details](connectors/cyneriosecurityevents.md)

---

## D

### [Darktrace Connector for Microsoft Sentinel REST API](connectors/darktracerestconnector.md)

**Publisher:** Darktrace

**Solution:** [Darktrace](solutions/darktrace.md)

**Tables (1):** `darktrace_model_alerts_CL`

The Darktrace REST API connector pushes real-time events from Darktrace to Microsoft Sentinel and is designed to be used with the Darktrace Solution for Sentinel. The connector writes logs to a custom log table titled "darktrace_model_alerts_CL"; Model Breaches, AI Analyst Incidents, System Alerts and Email Alerts can be ingested - additional filters can be set up on the Darktrace System Configuration page. Data is pushed to Sentinel from Darktrace masters.

[→ View full connector details](connectors/darktracerestconnector.md)

---

### [Datalake2Sentinel](connectors/datalake2sentinelconnector.md)

**Publisher:** Orange Cyberdefense

**Solution:** [Datalake2Sentinel](solutions/datalake2sentinel.md)

**Tables (1):** `ThreatIntelligenceIndicator`

This solution installs the Datalake2Sentinel connector which is built using the Codeless Connector Platform and allows you to automatically ingest threat intelligence indicators from **Datalake Orange Cyberdefense's CTI platform** into Microsoft Sentinel via the Upload Indicators REST API. After installing the solution, configure and enable this data connector by following guidance in Manage solution view.

[→ View full connector details](connectors/datalake2sentinelconnector.md)

---

### [Dataminr Pulse Alerts Data Connector](connectors/dataminrpulsealerts.md)

**Publisher:** Dataminr

**Solution:** [Dataminr Pulse](solutions/dataminr-pulse.md)

**Tables (1):** `DataminrPulse_Alerts_CL`

Dataminr Pulse Alerts Data Connector brings our AI-powered real-time intelligence into Microsoft Sentinel for faster threat detection and response.

[→ View full connector details](connectors/dataminrpulsealerts.md)

---

### [Derdack SIGNL4](connectors/derdacksignl4.md)

**Publisher:** Derdack

**Solution:** [SIGNL4](solutions/signl4.md)

**Tables (2):** `SIGNL4_CL`, `SecurityIncident`

When critical systems fail or security incidents happen, SIGNL4 bridges the ‘last mile’ to your staff, engineers, IT admins and workers in the field. It adds real-time mobile alerting to your services, systems, and processes in no time. SIGNL4 notifies through persistent mobile push, SMS text and voice calls with acknowledgement, tracking and escalation. Integrated duty and shift scheduling ensure the right people are alerted at the right time.

[Learn more >](https://www.signl4.com)

[→ View full connector details](connectors/derdacksignl4.md)

---

### [Digital Shadows Searchlight](connectors/digitalshadowssearchlightazurefunctions.md)

**Publisher:** Digital Shadows

**Solution:** [Digital Shadows](solutions/digital-shadows.md)

**Tables (1):** `DigitalShadows_CL`

The Digital Shadows data connector provides ingestion of the incidents and alerts from Digital Shadows Searchlight into the Microsoft Sentinel using the REST API. The connector will provide the incidents and alerts information such that it helps to examine, diagnose and analyse the potential security risks and threats.

[→ View full connector details](connectors/digitalshadowssearchlightazurefunctions.md)

---

### [Doppel Data Connector](connectors/doppel-dataconnector.md)

**Publisher:** Doppel

**Solution:** [Doppel](solutions/doppel.md)

**Tables (1):** `DoppelTable_CL`

The data connector is built on Microsoft Sentinel for Doppel events and alerts and supports DCR-based [ingestion time transformations](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/ingestion-time-transformations) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

[→ View full connector details](connectors/doppel-dataconnector.md)

---

### [Druva Events Connector](connectors/druvaeventccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [DruvaDataSecurityCloud](solutions/druvadatasecuritycloud.md)

**Tables (3):** `DruvaInsyncEvents_CL`, `DruvaPlatformEvents_CL`, `DruvaSecurityEvents_CL`

Provides capability to ingest the Druva events from Druva APIs

[→ View full connector details](connectors/druvaeventccpdefinition.md)

---

### [Dynamics 365](connectors/dynamics365.md)

**Publisher:** Microsoft

**Solution:** [Dynamics 365](solutions/dynamics-365.md)

**Tables (1):** `Dynamics365Activity`

The Dynamics 365 Common Data Service (CDS) activities connector provides insight into admin, user, and support activities, as well as Microsoft Social Engagement logging events. By connecting Dynamics 365 CRM logs into Microsoft Sentinel, you can view this data in workbooks, use it to create custom alerts, and improve your investigation process. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com//fwlink/p/?linkid=2226719&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/dynamics365.md)

---

### [Dynamics 365 Finance and Operations](connectors/dynamics365finance.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Business Applications](solutions/microsoft-business-applications.md)

**Tables (1):** `FinanceOperationsActivity_CL`

Dynamics 365 for Finance and Operations is a comprehensive Enterprise Resource Planning (ERP) solution that combines financial and operational capabilities to help businesses manage their day-to-day operations. It offers a range of features that enable businesses to streamline workflows, automate tasks, and gain insights into operational performance.

The Dynamics 365 Finance and Operations data connector ingests Dynamics 365 Finance and Operations admin activities and audit logs as well as user business process and application activities logs into Microsoft Sentinel.

[→ View full connector details](connectors/dynamics365finance.md)

---

### [Dynatrace Attacks](connectors/dynatraceattacks.md)

**Publisher:** Dynatrace

**Solution:** [Dynatrace](solutions/dynatrace.md)

**Tables (1):** `DynatraceAttacks_CL`

This connector uses the Dynatrace Attacks REST API to ingest detected attacks into Microsoft Sentinel Log Analytics

[→ View full connector details](connectors/dynatraceattacks.md)

---

### [Dynatrace Audit Logs](connectors/dynatraceauditlogs.md)

**Publisher:** Dynatrace

**Solution:** [Dynatrace](solutions/dynatrace.md)

**Tables (1):** `DynatraceAuditLogs_CL`

This connector uses the [Dynatrace Audit Logs REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/audit-logs) to ingest tenant audit logs into Microsoft Sentinel Log Analytics

[→ View full connector details](connectors/dynatraceauditlogs.md)

---

### [Dynatrace Problems](connectors/dynatraceproblems.md)

**Publisher:** Dynatrace

**Solution:** [Dynatrace](solutions/dynatrace.md)

**Tables (1):** `DynatraceProblems_CL`

This connector uses the [Dynatrace Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/problems-v2) to ingest problem events into Microsoft Sentinel Log Analytics

[→ View full connector details](connectors/dynatraceproblems.md)

---

### [Dynatrace Runtime Vulnerabilities](connectors/dynatraceruntimevulnerabilities.md)

**Publisher:** Dynatrace

**Solution:** [Dynatrace](solutions/dynatrace.md)

**Tables (1):** `DynatraceSecurityProblems_CL`

This connector uses the [Dynatrace Security Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/application-security/vulnerabilities/get-vulnerabilities) to ingest detected runtime vulnerabilities into Microsoft Sentinel Log Analytics.

[→ View full connector details](connectors/dynatraceruntimevulnerabilities.md)

---

## E

### [ESET Inspect](connectors/esetinspect.md)

**Publisher:** ESET Netherlands

**Solution:** [ESET Inspect](solutions/eset-inspect.md)

**Tables (1):** `ESETInspect_CL`

This connector will ingest detections from [ESET Inspect](https://www.eset.com/int/business/solutions/xdr-extended-detection-and-response/) using the provided [REST API](https://help.eset.com/ei_navigate/latest/en-US/api.html). This API is present in ESET Inspect version 1.4 and later.

[→ View full connector details](connectors/esetinspect.md)

---

### [ESET Protect Platform](connectors/esetprotectplatform.md)

**Publisher:** ESET

**Solution:** [ESET Protect Platform](solutions/eset-protect-platform.md)

**Tables (2):** `IntegrationTableIncidents_CL`, `IntegrationTable_CL`

The ESET Protect Platform data connector enables users to inject detections data from [ESET Protect Platform](https://www.eset.com/int/business/protect-platform/) using the provided [Integration REST API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform/Data%20Connectors). Integration REST API runs as scheduled Azure Function App.

[→ View full connector details](connectors/esetprotectplatform.md)

---

### [Egress Defend](connectors/egressdefendpolling.md)

**Publisher:** Egress Software Technologies

**Solution:** [Egress Defend](solutions/egress-defend.md)

**Tables (1):** `EgressDefend_CL`

The Egress Defend audit connector provides the capability to ingest Egress Defend Data into Microsoft Sentinel.

[→ View full connector details](connectors/egressdefendpolling.md)

---

### [Egress Iris Connector](connectors/egresssiempolling.md)

**Publisher:** Egress Software Technologies

**Solution:** [Egress Iris](solutions/egress-iris.md)

**Tables (2):** `DefendAuditData`, `EgressEvents_CL`

The Egress Iris connector will allow you to ingest Egress data into Sentinel.

[→ View full connector details](connectors/egresssiempolling.md)

---

### [Elastic Agent](connectors/elasticagent.md)

**Publisher:** Elastic

**Solution:** [ElasticAgent](solutions/elasticagent.md)

**Tables (1):** `ElasticAgentLogs_CL`

The [Elastic Agent](https://www.elastic.co/security) data connector provides the capability to ingest Elastic Agent logs, metrics, and security data into Microsoft Sentinel.

[→ View full connector details](connectors/elasticagent.md)

---

### [Ermes Browser Security Events](connectors/ermesbrowsersecurityevents.md)

**Publisher:** Ermes Cyber Security S.p.A.

**Solution:** [Ermes Browser Security](solutions/ermes-browser-security.md)

**Tables (1):** `ErmesBrowserSecurityEvents_CL`

Ermes Browser Security Events

[→ View full connector details](connectors/ermesbrowsersecurityevents.md)

---

### [Eset Security Management Center](connectors/esetsmc.md)

**Publisher:** Eset

**Solution:** [Eset Security Management Center](solutions/eset-security-management-center.md)

**Tables (1):** `eset_CL`

Connector for [Eset SMC](https://help.eset.com/esmc_admin/72/en-US/) threat events, audit logs, firewall events and web sites filter.

[→ View full connector details](connectors/esetsmc.md)

---

### [Exchange Security Insights On-Premises Collector](connectors/esi-exchangeonpremisescollector.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange On-Premises](solutions/microsoft-exchange-security---exchange-on-premises.md)

**Tables (1):** `ESIExchangeConfig_CL`

Connector used to push Exchange On-Premises Security configuration for Microsoft Sentinel Analysis

[→ View full connector details](connectors/esi-exchangeonpremisescollector.md)

---

### [Exchange Security Insights Online Collector](connectors/esi-exchangeonlinecollector.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange Online](solutions/microsoft-exchange-security---exchange-online.md)

**Tables (1):** `ESIExchangeOnlineConfig_CL`

Connector used to push Exchange Online Security configuration for Microsoft Sentinel Analysis

[→ View full connector details](connectors/esi-exchangeonlinecollector.md)

---

### [ExtraHop Detections Data Connector](connectors/extrahop.md)

**Publisher:** ExtraHop

**Solution:** [ExtraHop](solutions/extrahop.md)

**Tables (1):** `ExtraHop_Detections_CL`

The [ExtraHop](https://extrahop.com/) Detections Data Connector enables you to import detection data from ExtraHop RevealX to Microsoft Sentinel through webhook payloads.

[→ View full connector details](connectors/extrahop.md)

---

## F

### [F5 BIG-IP](connectors/f5bigip.md)

**Publisher:** F5 Networks

**Solution:** [F5 BIG-IP](solutions/f5-big-ip.md)

**Tables (3):** `F5Telemetry_ASM_CL`, `F5Telemetry_LTM_CL`, `F5Telemetry_system_CL`

The F5 firewall connector allows you to easily connect your F5 logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/f5bigip.md)

---

### [Feedly](connectors/feedly.md)

**Publisher:** Feedly

**Solution:** [Feedly](solutions/feedly.md)

**Tables (1):** `feedly_indicators_CL`

This connector allows you to ingest IoCs from Feedly.

[→ View full connector details](connectors/feedly.md)

---

### [Flare](connectors/flare.md)

**Publisher:** Flare

**Solution:** [Flare](solutions/flare.md)

**Tables (1):** `Firework_CL`

[Flare](https://flare.systems/platform/) connector allows you to receive data and intelligence from Flare on Microsoft Sentinel.

[→ View full connector details](connectors/flare.md)

---

### [Forcepoint DLP](connectors/forcepoint-dlp.md)

**Publisher:** Forcepoint

**Solution:** [Forcepoint DLP](solutions/forcepoint-dlp.md)

**Tables (1):** `ForcepointDLPEvents_CL`

The Forcepoint DLP (Data Loss Prevention) connector allows you to automatically export DLP incident data from Forcepoint DLP into Microsoft Sentinel in real-time. This enriches visibility into user activities and data loss incidents, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

[→ View full connector details](connectors/forcepoint-dlp.md)

---

### [Forescout](connectors/forescout.md)

**Publisher:** Forescout

**Solution:** [Forescout (Legacy)](solutions/forescout-(legacy).md)

**Tables (1):** `Syslog`

The [Forescout](https://www.forescout.com/) data connector provides the capability to ingest [Forescout events](https://docs.forescout.com/bundle/syslog-3-6-1-h/page/syslog-3-6-1-h.How-to-Work-with-the-Syslog-Plugin.html) into Microsoft Sentinel. Refer to [Forescout documentation](https://docs.forescout.com/bundle/syslog-msg-3-6-tn/page/syslog-msg-3-6-tn.About-Syslog-Messages-in-Forescout.html) for more information.

[→ View full connector details](connectors/forescout.md)

---

### [Forescout Host Property Monitor](connectors/forescouthostpropertymonitor.md)

**Publisher:** Forescout

**Solution:** [ForescoutHostPropertyMonitor](solutions/forescouthostpropertymonitor.md)

**Tables (3):** `ForescoutComplianceStatus_CL`, `ForescoutHostProperties_CL`, `ForescoutPolicyStatus_CL`

The Forescout Host Property Monitor connector allows you to connect host/policy/compliance properties from Forescout platform with Microsoft Sentinel, to view, create custom incidents, and improve investigation. This gives you more insight into your organization network and improves your security operation capabilities.

[→ View full connector details](connectors/forescouthostpropertymonitor.md)

---

### [Forescout eyeInspect for OT Security](connectors/forescout-eyeinspect-for-ot-security.md)

**Publisher:** Forescout

**Solution:** [Forescout eyeInspect for OT Security](solutions/forescout-eyeinspect-for-ot-security.md)

**Tables (2):** `ForescoutOtAlert_CL`, `ForescoutOtAsset_CL`

Forescout eyeInspect for OT Security connector allows you to connect Asset/Alert information from Forescout eyeInspect OT platform with Microsoft Sentinel, to view and analyze data using Log Analytics Tables and Workbooks. This gives you more insight into OT organization network and improves security operation capabilities.

[→ View full connector details](connectors/forescout-eyeinspect-for-ot-security.md)

---

### [Fortinet FortiNDR Cloud](connectors/fortinetfortindrclouddataconnector.md)

**Publisher:** Fortinet

**Solution:** [Fortinet FortiNDR Cloud](solutions/fortinet-fortindr-cloud.md)

**Tables (3):** `FncEventsDetections_CL`, `FncEventsObservation_CL`, `FncEventsSuricata_CL`

The Fortinet FortiNDR Cloud data connector provides the capability to ingest [Fortinet FortiNDR Cloud](https://docs.fortinet.com/product/fortindr-cloud) data into Microsoft Sentinel using the FortiNDR Cloud API

[→ View full connector details](connectors/fortinetfortindrclouddataconnector.md)

---

### [Fortinet FortiWeb Web Application Firewall via AMA](connectors/fortinetfortiwebama.md)

**Publisher:** Microsoft

**Solution:** [Fortinet FortiWeb Cloud WAF-as-a-Service connector for Microsoft Sentinel](solutions/fortinet-fortiweb-cloud-waf-as-a-service-connector-for-microsoft-sentinel.md)

**Tables (1):** `CommonSecurityLog`

The [fortiweb](https://www.fortinet.com/products/web-application-firewall/fortiweb) data connector provides the capability to ingest Threat Analytics and events into Microsoft Sentinel.

[→ View full connector details](connectors/fortinetfortiwebama.md)

---

## G

### [GCP Cloud Run (via Codeless Connector Framework)](connectors/gcpcloudrunlogs-connectordefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Cloud Platform Cloud Run](solutions/google-cloud-platform-cloud-run.md)

**Tables (1):** `GCPCloudRun`

The GCP Cloud Run data connector provides the capability to ingest Cloud Run request logs into Microsoft Sentinel using Pub/Sub. Refer the [Cloud Run Overview](https://cloud.google.com/run/docs/logging) for more details.

[→ View full connector details](connectors/gcpcloudrunlogs-connectordefinition.md)

---

### [GCP Cloud SQL (via Codeless Connector Framework)](connectors/gcpcloudsqlccfdefinition.md)

**Publisher:** Microsoft

**Solution:** [GoogleCloudPlatformSQL](solutions/googlecloudplatformsql.md)

**Tables (1):** `GCPCloudSQL`

The GCP Cloud SQL data connector provides the capability to ingest Audit logs into Microsoft Sentinel using the GCP Cloud SQL API. Refer to [GCP cloud SQL Audit Logs](https://cloud.google.com/sql/docs/mysql/audit-logging) documentation for more information.

[→ View full connector details](connectors/gcpcloudsqlccfdefinition.md)

---

### [GCP Pub/Sub Audit Logs](connectors/gcpauditlogsdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Cloud Platform Audit Logs](solutions/google-cloud-platform-audit-logs.md)

**Tables (1):** `GCPAuditLogs`

The Google Cloud Platform (GCP) audit logs, ingested from Microsoft Sentinel's connector, enables you to capture three types of audit logs: admin activity logs, data access logs, and access transparency logs. Google cloud audit logs record a trail that practitioners can use to monitor access and detect potential threats across Google Cloud Platform (GCP) resources.

[→ View full connector details](connectors/gcpauditlogsdefinition.md)

---

### [GCP Pub/Sub Firewall Logs](connectors/gcpfirewalllogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Cloud Platform Firewall Logs](solutions/google-cloud-platform-firewall-logs.md)

**Tables (1):** `GCPFirewallLogs`

The Google Cloud Platform (GCP) firewall logs, enable you to capture network inbound and outbound activity to monitor access and detect potential threats across Google Cloud Platform (GCP) resources.

[→ View full connector details](connectors/gcpfirewalllogsccpdefinition.md)

---

### [GCP Pub/Sub Load Balancer Logs (via Codeless Connector Platform).](connectors/gcpfloadbalancerlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Cloud Platform Load Balancer Logs](solutions/google-cloud-platform-load-balancer-logs.md)

**Tables (1):** `GCPLoadBalancerLogs_CL`

Google Cloud Platform (GCP) Load Balancer logs provide detailed insights into network traffic, capturing both inbound and outbound activities. These logs are used for monitoring access patterns and identifying potential security threats across GCP resources. Additionally, these logs also include GCP Web Application Firewall (WAF) logs, enhancing the ability to detect and mitigate risks effectively.

[→ View full connector details](connectors/gcpfloadbalancerlogsccpdefinition.md)

---

### [GCP Pub/Sub VPC Flow Logs (via Codeless Connector Framework)](connectors/gcpvpcflowlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Cloud Platform VPC Flow Logs](solutions/google-cloud-platform-vpc-flow-logs.md)

**Tables (1):** `GCPVPCFlow`

The Google Cloud Platform (GCP) VPC Flow Logs enable you to capture network traffic activity at the VPC level, allowing you to monitor access patterns, analyze network performance, and detect potential threats across GCP resources.

[→ View full connector details](connectors/gcpvpcflowlogsccpdefinition.md)

---

### [Garrison ULTRA Remote Logs](connectors/garrisonultraremotelogs.md)

**Publisher:** Garrison

**Solution:** [Garrison ULTRA](solutions/garrison-ultra.md)

**Tables (1):** `Garrison_ULTRARemoteLogs_CL`

The [Garrison ULTRA](https://www.garrison.com/en/garrison-ultra-cloud-platform) Remote Logs connector allows you to ingest Garrison ULTRA Remote Logs into Microsoft Sentinel.

[→ View full connector details](connectors/garrisonultraremotelogs.md)

---

### [Gigamon AMX Data Connector](connectors/gigamondataconnector.md)

**Publisher:** Gigamon

**Solution:** [Gigamon Connector](solutions/gigamon-connector.md)

**Tables (1):** `Gigamon_CL`

Use this data connector to integrate with Gigamon Application Metadata Exporter (AMX) and get data sent directly to Microsoft Sentinel. 

[→ View full connector details](connectors/gigamondataconnector.md)

---

### [GitHub (using Webhooks)](connectors/githubwebhook.md)

**Publisher:** Microsoft

**Solution:** [GitHub](solutions/github.md)

**Tables (1):** `githubscanaudit_CL`

The [GitHub](https://www.github.com) webhook data connector provides the capability to ingest GitHub subscribed events into Microsoft Sentinel using [GitHub webhook events](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads). The connector provides ability to get events into Microsoft Sentinel which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. 

 **Note:** If you are intended to ingest Github Audit logs, Please refer to GitHub Enterprise Audit Log Connector from "**Data Connectors**" gallery.

[→ View full connector details](connectors/githubwebhook.md)

---

### [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](connectors/githubauditdefinitionv2.md)

**Publisher:** Microsoft

**Solution:** [GitHub](solutions/github.md)

**Tables (1):** `GitHubAuditLogsV2_CL`

The GitHub audit log connector provides the capability to ingest GitHub logs into Microsoft Sentinel. By connecting GitHub audit logs into Microsoft Sentinel, you can view this data in workbooks, use it to create custom alerts, and improve your investigation process. 

 **Note:** If you intended to ingest GitHub subscribed events into Microsoft Sentinel, please refer to GitHub (using Webhooks) Connector from "**Data Connectors**" gallery.

[→ View full connector details](connectors/githubauditdefinitionv2.md)

---

### [Google ApigeeX (via Codeless Connector Framework)](connectors/googleapigeexlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Apigee](solutions/google-apigee.md)

**Tables (1):** `GCPApigee`

The Google ApigeeX data connector provides the capability to ingest Audit logs into Microsoft Sentinel using the Google Apigee API. Refer to [Google Apigee API](https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/?apix=true) documentation for more information.

[→ View full connector details](connectors/googleapigeexlogsccpdefinition.md)

---

### [Google Cloud Platform CDN (via Codeless Connector Framework)](connectors/gcpcdnlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [GoogleCloudPlatformCDN](solutions/googlecloudplatformcdn.md)

**Tables (1):** `GCPCDN`

The Google Cloud Platform CDN data connector provides the capability to ingest Cloud CDN Audit logs and Cloud CDN Traffic logs into Microsoft Sentinel using the Compute Engine API. Refer the [Product overview](https://cloud.google.com/cdn/docs/overview) document for more details.

[→ View full connector details](connectors/gcpcdnlogsccpdefinition.md)

---

### [Google Cloud Platform Cloud IDS (via Codeless Connector Framework)](connectors/gcpcloudidslogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [GoogleCloudPlatformIDS](solutions/googlecloudplatformids.md)

**Tables (1):** `GCPIDS`

The Google Cloud Platform IDS data connector provides the capability to ingest Cloud IDS Traffic logs, Threat logs and Audit logs into Microsoft Sentinel using the Google Cloud IDS API. Refer to [Cloud IDS API](https://cloud.google.com/intrusion-detection-system/docs/audit-logging#google.cloud.ids.v1.IDS) documentation for more information.

[→ View full connector details](connectors/gcpcloudidslogsccpdefinition.md)

---

### [Google Cloud Platform Cloud Monitoring (via Codeless Connector Framework)](connectors/gcpmonitorccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Cloud Platform Cloud Monitoring](solutions/google-cloud-platform-cloud-monitoring.md)

**Tables (1):** `GCPMonitoring`

The Google Cloud Platform Cloud Monitoring data connector ingests Monitoring logs from Google Cloud into Microsoft Sentinel using the Google Cloud Monitoring API. Refer to [Cloud Monitoring API](https://cloud.google.com/monitoring/api/v3) documentation for more details.

[→ View full connector details](connectors/gcpmonitorccpdefinition.md)

---

### [Google Cloud Platform Compute Engine (via Codeless Connector Framework)](connectors/gcpcomputeenginelogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Cloud Platform Compute Engine](solutions/google-cloud-platform-compute-engine.md)

**Tables (1):** `GCPComputeEngine`

The Google Cloud Platform Compute Engine data connector provides the capability to ingest Compute Engine Audit logs into Microsoft Sentinel using the Google Cloud Compute Engine API. Refer to [Cloud Compute Engine API](https://cloud.google.com/compute/docs/reference/rest/v1) documentation for more information.

[→ View full connector details](connectors/gcpcomputeenginelogsccpdefinition.md)

---

### [Google Cloud Platform DNS (via Codeless Connector Framework)](connectors/gcpdnslogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [GoogleCloudPlatformDNS](solutions/googlecloudplatformdns.md)

**Tables (1):** `GCPDNS`

The Google Cloud Platform DNS data connector provides the capability to ingest Cloud DNS Query logs and Cloud DNS Audit logs into Microsoft Sentinel using the Google Cloud DNS API. Refer to [Cloud DNS API](https://cloud.google.com/dns/docs/reference/rest/v1) documentation for more information.

[→ View full connector details](connectors/gcpdnslogsccpdefinition.md)

---

### [Google Cloud Platform IAM (via Codeless Connector Framework)](connectors/gcpiamccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [GoogleCloudPlatformIAM](solutions/googlecloudplatformiam.md)

**Tables (1):** `GCPIAM`

The Google Cloud Platform IAM data connector provides the capability to ingest the Audit logs relating to Identity and Access Management (IAM) activities within Google Cloud into Microsoft Sentinel using the Google IAM API. Refer to [GCP IAM API](https://cloud.google.com/iam/docs/reference/rest) documentation for more information.

[→ View full connector details](connectors/gcpiamccpdefinition.md)

---

### [Google Cloud Platform NAT (via Codeless Connector Framework)](connectors/gcpnatlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [GoogleCloudPlatformNAT](solutions/googlecloudplatformnat.md)

**Tables (2):** `GCPNAT`, `GCPNATAudit`

The Google Cloud Platform NAT data connector provides the capability to ingest Cloud NAT Audit logs and Cloud NAT Traffic logs into Microsoft Sentinel using the Compute Engine API. Refer the [Product overview](https://cloud.google.com/nat/docs/overview) document for more details.

[→ View full connector details](connectors/gcpnatlogsccpdefinition.md)

---

### [Google Cloud Platform Resource Manager (via Codeless Connector Framework)](connectors/gcpresourcemanagerlogsccfdefinition.md)

**Publisher:** Microsoft

**Solution:** [GoogleCloudPlatformResourceManager](solutions/googlecloudplatformresourcemanager.md)

**Tables (1):** `GCPResourceManager`

The Google Cloud Platform Resource Manager data connector provides the capability to ingest Resource Manager [Admin Activity and Data Access Audit logs](https://cloud.google.com/resource-manager/docs/audit-logging) into Microsoft Sentinel using the Cloud Resource Manager API. Refer the [Product overview](https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy) document for more details.

[→ View full connector details](connectors/gcpresourcemanagerlogsccfdefinition.md)

---

### [Google Kubernetes Engine (via Codeless Connector Framework)](connectors/gkeccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Kubernetes Engine](solutions/google-kubernetes-engine.md)

**Tables (6):** `GKEAPIServer`, `GKEApplication`, `GKEAudit`, `GKEControllerManager`, `GKEHPADecision`, `GKEScheduler`

The Google Kubernetes Engine (GKE) Logs enable you to capture cluster activity, workload behavior, and security events, allowing you to monitor Kubernetes workloads, analyze performance, and detect potential threats across GKE clusters.

[→ View full connector details](connectors/gkeccpdefinition.md)

---

### [Google Security Command Center](connectors/googlesccdefinition.md)

**Publisher:** Microsoft

**Solution:** [Google Cloud Platform Security Command Center](solutions/google-cloud-platform-security-command-center.md)

**Tables (1):** `GoogleCloudSCC`

The Google Cloud Platform (GCP) Security Command Center is a comprehensive security and risk management platform for Google Cloud, ingested from Sentinel's connector. It offers features such as asset inventory and discovery, vulnerability and threat detection, and risk mitigation and remediation to help you gain insight into your organization's security and data attack surface. This integration enables you to perform tasks related to findings and assets more effectively.

[→ View full connector details](connectors/googlesccdefinition.md)

---

### [Google Workspace Activities (via Codeless Connector Framework)](connectors/googleworkspaceccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [GoogleWorkspaceReports](solutions/googleworkspacereports.md)

**Tables (1):** `GoogleWorkspaceReports`

The [Google Workspace](https://workspace.google.com/) Activities data connector provides the capability to ingest Activity Events from [Google Workspace API](https://developers.google.com/admin-sdk/reports/reference/rest/v1/activities/list) into Microsoft Sentinel.

[→ View full connector details](connectors/googleworkspaceccpdefinition.md)

---

### [GreyNoise Threat Intelligence](connectors/greynoise2sentinelapi.md)

**Publisher:** GreyNoise, Inc. and BlueCycle LLC

**Solution:** [GreyNoiseThreatIntelligence](solutions/greynoisethreatintelligence.md)

**Tables (1):** `ThreatIntelligenceIndicator`

This Data Connector installs an Azure Function app to download GreyNoise indicators once per day and inserts them into the ThreatIntelligenceIndicator table in Microsoft Sentinel.

[→ View full connector details](connectors/greynoise2sentinelapi.md)

---

## H

### [HYAS Protect](connectors/hyasprotect.md)

**Publisher:** HYAS

**Solution:** [HYAS Protect](solutions/hyas-protect.md)

**Tables (1):** `HYASProtectDnsSecurityLogs_CL`

HYAS Protect provide logs based on reputation values - Blocked, Malicious, Permitted, Suspicious.

[→ View full connector details](connectors/hyasprotect.md)

---

### [HackerView Intergration](connectors/hvpollingidazurefunctions.md)

**Publisher:** CTM360

**Solution:** [CTM360](solutions/ctm360.md)

**Tables (1):** `HackerViewLog_Azure_1_CL`

Through the API integration, you have the capability to retrieve all the issues related to your HackerView organizations via a RESTful interface.

[→ View full connector details](connectors/hvpollingidazurefunctions.md)

---

### [Holm Security Asset Data](connectors/holmsecurityassets.md)

**Publisher:** Holm Security

**Solution:** [HolmSecurity](solutions/holmsecurity.md)

**Tables (2):** `net_assets_CL`, `web_assets_CL`

The connector provides the capability to poll data from Holm Security Center into Microsoft Sentinel.

[→ View full connector details](connectors/holmsecurityassets.md)

---

## I

### [IIS Logs of Microsoft Exchange Servers](connectors/esi-opt5exchangeiislogs.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange On-Premises](solutions/microsoft-exchange-security---exchange-on-premises.md)

**Tables (1):** `W3CIISLog`

[Option 5] - Using Azure Monitor Agent - You can stream all IIS Logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

[→ View full connector details](connectors/esi-opt5exchangeiislogs.md)

---

### [IONIX Security Logs](connectors/cyberpionsecuritylogs.md)

**Publisher:** IONIX

**Solution:** [IONIX](solutions/ionix.md)

**Tables (1):** `CyberpionActionItems_CL`

The IONIX Security Logs data connector, ingests logs from the IONIX system directly into Sentinel. The connector allows users to visualize their data, create alerts and incidents and improve security investigations.

[→ View full connector details](connectors/cyberpionsecuritylogs.md)

---

### [IPinfo ASN Data Connector](connectors/ipinfoasndataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_ASN_CL`

This IPinfo data connector installs an Azure Function app to download standard_ASN datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfoasndataconnector.md)

---

### [IPinfo Abuse Data Connector](connectors/ipinfoabusedataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Abuse_CL`

This IPinfo data connector installs an Azure Function app to download standard_abuse datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfoabusedataconnector.md)

---

### [IPinfo Carrier Data Connector](connectors/ipinfocarrierdataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Carrier_CL`

This IPinfo data connector installs an Azure Function app to download standard_carrier datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfocarrierdataconnector.md)

---

### [IPinfo Company Data Connector](connectors/ipinfocompanydataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Company_CL`

This IPinfo data connector installs an Azure Function app to download standard_company datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfocompanydataconnector.md)

---

### [IPinfo Country ASN Data Connector](connectors/ipinfocountrydataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Country_CL`

This IPinfo data connector installs an Azure Function app to download country_asn datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfocountrydataconnector.md)

---

### [IPinfo Domain Data Connector](connectors/ipinfodomaindataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Domain_CL`

This IPinfo data connector installs an Azure Function app to download standard_domain datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfodomaindataconnector.md)

---

### [IPinfo Iplocation Data Connector](connectors/ipinfoiplocationdataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Location_CL`

This IPinfo data connector installs an Azure Function app to download standard_location datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfoiplocationdataconnector.md)

---

### [IPinfo Iplocation Extended Data Connector](connectors/ipinfoiplocationextendeddataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Location_extended_CL`

This IPinfo data connector installs an Azure Function app to download standard_location_extended datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfoiplocationextendeddataconnector.md)

---

### [IPinfo Privacy Data Connector](connectors/ipinfoprivacydataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Privacy_CL`

This IPinfo data connector installs an Azure Function app to download standard_privacy datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfoprivacydataconnector.md)

---

### [IPinfo Privacy Extended Data Connector](connectors/ipinfoprivacyextendeddataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_Privacy_extended_CL`

This IPinfo data connector installs an Azure Function app to download standard_privacy datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfoprivacyextendeddataconnector.md)

---

### [IPinfo RIRWHOIS Data Connector](connectors/ipinforirwhoisdataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_RIRWHOIS_CL`

This IPinfo data connector installs an Azure Function app to download RIRWHOIS datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinforirwhoisdataconnector.md)

---

### [IPinfo RWHOIS Data Connector](connectors/ipinforwhoisdataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_RWHOIS_CL`

This IPinfo data connector installs an Azure Function app to download RWHOIS datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinforwhoisdataconnector.md)

---

### [IPinfo WHOIS ASN Data Connector](connectors/ipinfowhoisasndataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_WHOIS_ASN_CL`

This IPinfo data connector installs an Azure Function app to download WHOIS_ASN datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfowhoisasndataconnector.md)

---

### [IPinfo WHOIS MNT Data Connector](connectors/ipinfowhoismntdataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_WHOIS_MNT_CL`

This IPinfo data connector installs an Azure Function app to download WHOIS_MNT datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfowhoismntdataconnector.md)

---

### [IPinfo WHOIS NET Data Connector](connectors/ipinfowhoisnetdataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_WHOIS_NET_CL`

This IPinfo data connector installs an Azure Function app to download WHOIS_NET datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfowhoisnetdataconnector.md)

---

### [IPinfo WHOIS ORG Data Connector](connectors/ipinfowhoisorgdataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_WHOIS_ORG_CL`

This IPinfo data connector installs an Azure Function app to download WHOIS_ORG datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfowhoisorgdataconnector.md)

---

### [IPinfo WHOIS POC Data Connector](connectors/ipinfowhoispocdataconnector.md)

**Publisher:** IPinfo

**Solution:** [IPinfo](solutions/ipinfo.md)

**Tables (1):** `Ipinfo_WHOIS_POC_CL`

This IPinfo data connector installs an Azure Function app to download WHOIS_POC datasets and insert it into custom log table in Microsoft Sentinel

[→ View full connector details](connectors/ipinfowhoispocdataconnector.md)

---

### [Illumio Insights](connectors/illumioinsightsdefinition.md)

**Publisher:** Microsoft

**Solution:** [Illumio Insight](solutions/illumio-insight.md)

**Tables (1):** `IllumioInsights_CL`

Illumio Insights Connector sends workload and security graph data from Illumio Insights into the Azure Microsoft Sentinel Data Lake, providing deep context for threat detection, lateral movement analysis, and real-time investigation.

[→ View full connector details](connectors/illumioinsightsdefinition.md)

---

### [Illumio Insights Summary](connectors/illumioinsightssummaryccp.md)

**Publisher:** Illumio

**Solution:** [Illumio Insight](solutions/illumio-insight.md)

**Tables (1):** `IllumioInsightsSummary_CL`

The Illumio Insights Summary connector Publishes AI-powered threat discovery and anomaly reports generated by the Illumio Insights Agent. Leveraging the MITRE ATT&CK framework, these reports surface high-fidelity insights into emerging threats and risky behaviors, directly into the Data Lake.

[→ View full connector details](connectors/illumioinsightssummaryccp.md)

---

### [Illumio SaaS](connectors/illumiosaasdataconnector.md)

**Publisher:** Illumio

**Solution:** [IllumioSaaS](solutions/illumiosaas.md)

**Tables (2):** `Illumio_Auditable_Events_CL`, `Illumio_Flow_Events_CL`

[Illumio](https://www.illumio.com/) connector provides the capability to ingest events into Microsoft Sentinel. The connector provides ability to ingest auditable and flow events from AWS S3 bucket.

[→ View full connector details](connectors/illumiosaasdataconnector.md)

---

### [Illumio Saas](connectors/illumiosaasccfdefinition.md)

**Publisher:** Microsoft

**Solution:** [IllumioSaaS](solutions/illumiosaas.md)

**Tables (1):** `IllumioFlowEventsV2_CL`

The Illumio Saas Cloud data connector provides the capability to ingest Flow logs into Microsoft Sentinel using the Illumio Saas Log Integration through AWS S3 Bucket. Refer to [Illumio Saas Log Integration](https://product-docs-repo.illumio.com/Tech-Docs/CloudSecure/out/en/administer-cloudsecure/connector.html#UUID-c14edaab-9726-1f23-9c4c-bc2937be39ee_section-idm234556433515698) for more information.

[→ View full connector details](connectors/illumiosaasccfdefinition.md)

---

### [Imperva Cloud WAF](connectors/impervacloudwaflogsccfdefinition.md)

**Publisher:** Microsoft

**Solution:** [ImpervaCloudWAF](solutions/impervacloudwaf.md)

**Tables (1):** `ImpervaWAFCloudV2_CL`

The Imperva WAF Cloud data connector provides the capability to ingest logs into Microsoft Sentinel using the Imperva Log Integration through AWS S3 Bucket. Refer to [Imperva WAF Cloud Log Integration](https://docs.imperva.com/bundle/cloud-application-security/page/settings/log-integration.htm) for more information.

[→ View full connector details](connectors/impervacloudwaflogsccfdefinition.md)

---

### [Imperva Cloud WAF](connectors/impervawafcloudapi.md)

**Publisher:** Imperva

**Solution:** [ImpervaCloudWAF](solutions/impervacloudwaf.md)

**Tables (1):** `ImpervaWAFCloud_CL`

The [Imperva Cloud WAF](https://www.imperva.com/resources/resource-library/datasheets/imperva-cloud-waf/) data connector provides the capability to integrate and ingest Web Application Firewall events into Microsoft Sentinel through the REST API. Refer to Log integration [documentation](https://docs.imperva.com/bundle/cloud-application-security/page/settings/log-integration.htm#Download) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/impervawafcloudapi.md)

---

### [Imperva WAF Gateway](connectors/impervawafgateway.md)

**Publisher:** Imperva

**Solution:** [Imperva WAF Gateway](solutions/imperva-waf-gateway.md)

**Tables (1):** `CommonSecurityLog`

The [Imperva](https://www.imperva.com) connector will allow you to quickly connect your Imperva WAF Gateway alerts to Azure Sentinel. This provides you additional insight into your organization's WAF traffic and improves your security operation capabilities.

[→ View full connector details](connectors/impervawafgateway.md)

---

### [InfoSecGlobal Data Connector](connectors/infosecdataconnector.md)

**Publisher:** InfoSecGlobal

**Solution:** [AgileSec Analytics Connector](solutions/agilesec-analytics-connector.md)

**Tables (1):** `InfoSecAnalytics_CL`

Use this data connector to integrate with InfoSec Crypto Analytics and get data sent directly to Microsoft Sentinel.

[→ View full connector details](connectors/infosecdataconnector.md)

---

### [Infoblox Data Connector via REST API](connectors/infobloxdataconnector.md)

**Publisher:** Infoblox

**Solution:** [Infoblox](solutions/infoblox.md)

**Tables (18):** `Failed_Range_To_Ingest_CL`, `Infoblox_Failed_Indicators_CL`, `dossier_atp_CL`, `dossier_atp_threat_CL`, `dossier_dns_CL`, `dossier_geo_CL`, `dossier_infoblox_web_cat_CL`, `dossier_inforank_CL`, `dossier_malware_analysis_v3_CL`, `dossier_nameserver_CL`, `dossier_nameserver_matches_CL`, `dossier_ptr_CL`, `dossier_rpz_feeds_CL`, `dossier_rpz_feeds_records_CL`, `dossier_threat_actor_CL`, `dossier_tld_risk_CL`, `dossier_whitelist_CL`, `dossier_whois_CL`

The Infoblox Data Connector allows you to easily connect your Infoblox TIDE data and Dossier data with Microsoft Sentinel. By connecting your data to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

[→ View full connector details](connectors/infobloxdataconnector.md)

---

### [Infoblox SOC Insight Data Connector via REST API](connectors/infobloxsocinsightsdataconnector-api.md)

**Publisher:** Infoblox

**Solution:** [Infoblox](solutions/infoblox.md)

**Tables (1):** `InfobloxInsight_CL`

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

[→ View full connector details](connectors/infobloxsocinsightsdataconnector-api.md)

---

### [Island Enterprise Browser Admin Audit (Polling CCP)](connectors/island-admin-polling.md)

**Publisher:** Island

**Solution:** [Island](solutions/island.md)

**Tables (1):** `Island_Admin_CL`

The [Island](https://www.island.io) Admin connector provides the capability to ingest Island Admin Audit logs into Microsoft Sentinel.

[→ View full connector details](connectors/island-admin-polling.md)

---

### [Island Enterprise Browser User Activity (Polling CCP)](connectors/island-user-polling.md)

**Publisher:** Island

**Solution:** [Island](solutions/island.md)

**Tables (1):** `Island_User_CL`

The [Island](https://www.island.io) connector provides the capability to ingest Island User Activity logs into Microsoft Sentinel.

[→ View full connector details](connectors/island-user-polling.md)

---

### [iboss via AMA](connectors/ibossama.md)

**Publisher:** iboss

**Solution:** [iboss](solutions/iboss.md)

**Tables (1):** `CommonSecurityLog`

The [iboss](https://www.iboss.com) data connector enables you to seamlessly connect your Threat Console to Microsoft Sentinel and enrich your instance with iboss URL event logs. Our logs are forwarded in Common Event Format (CEF) over Syslog and the configuration required can be completed on the iboss platform without the use of a proxy. Take advantage of our connector to garner critical data points and gain insight into security threats.

[→ View full connector details](connectors/ibossama.md)

---

## J

### [Jamf Protect Push Connector](connectors/jamfprotectpush.md)

**Publisher:** Jamf

**Solution:** [Jamf Protect](solutions/jamf-protect.md)

**Tables (3):** `jamfprotectalerts_CL`, `jamfprotecttelemetryv2_CL`, `jamfprotectunifiedlogs_CL`

The [Jamf Protect](https://www.jamf.com/products/jamf-protect/) connector provides the capability to read raw event data from Jamf Protect in Microsoft Sentinel.

[→ View full connector details](connectors/jamfprotectpush.md)

---

## K

### [Keeper Security Push Connector](connectors/keepersecuritypush2.md)

**Publisher:** Keeper Security

**Solution:** [Keeper Security](solutions/keeper-security.md)

**Tables (1):** `KeeperSecurityEventNewLogs_CL`

The [Keeper Security](https://keepersecurity.com) connector provides the capability to read raw event data from Keeper Security in Microsoft Sentinel.

[→ View full connector details](connectors/keepersecuritypush2.md)

---

## L

### [LastPass Enterprise - Reporting (Polling CCP)](connectors/lastpass-polling.md)

**Publisher:** The Collective Consulting BV

**Solution:** [LastPass](solutions/lastpass.md)

**Tables (1):** `LastPassNativePoller_CL`

The [LastPass Enterprise](https://www.lastpass.com/products/enterprise-password-management-and-sso) connector provides the capability to LastPass reporting (audit) logs into Microsoft Sentinel. The connector provides visibility into logins and activity within LastPass (such as reading and removing passwords).

[→ View full connector details](connectors/lastpass-polling.md)

---

### [Lookout Cloud Security for Microsoft Sentinel](connectors/lookoutcloudsecuritydataconnector.md)

**Publisher:** Lookout

**Solution:** [Lookout Cloud Security Platform for Microsoft Sentinel](solutions/lookout-cloud-security-platform-for-microsoft-sentinel.md)

**Tables (1):** `LookoutCloudSecurity_CL`

This connector uses a Agari REST API connection to push data into Microsoft Sentinel Log Analytics.

[→ View full connector details](connectors/lookoutcloudsecuritydataconnector.md)

---

### [Lookout Mobile Threat Detection Connector (via Codeless Connector Framework) (Preview)](connectors/lookoutstreaming-definition.md)

**Publisher:** Microsoft

**Solution:** [Lookout](solutions/lookout.md)

**Tables (1):** `LookoutMtdV2_CL`

The [Lookout Mobile Threat Detection](https://lookout.com) data connector provides the capability to ingest events related to mobile security risks into Microsoft Sentinel through the Mobile Risk API. Refer to [API documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) for more information. This connector helps you examine potential security risks detected in mobile devices.

[→ View full connector details](connectors/lookoutstreaming-definition.md)

---

### [Lumen Defender Threat Feed Data Connector](connectors/lumenthreatfeedconnector.md)

**Publisher:** Lumen Technologies, Inc.

**Solution:** [Lumen Defender Threat Feed](solutions/lumen-defender-threat-feed.md)

**Tables (1):** `ThreatIntelIndicators`

The [Lumen Defender Threat Feed](https://bll-analytics.mss.lumen.com/analytics) connector provides the capability to ingest STIX-formatted threat intelligence indicators from Lumen's Black Lotus Labs research team into Microsoft Sentinel. The connector automatically downloads and uploads daily threat intelligence indicators including IPv4 addresses and domains to the ThreatIntelIndicators table via the STIX Objects Upload API.

[→ View full connector details](connectors/lumenthreatfeedconnector.md)

---

### [Luminar IOCs and Leaked Credentials](connectors/cognyteluminar.md)

**Publisher:** Cognyte Technologies Israel Ltd

**Solution:** [CognyteLuminar](solutions/cognyteluminar.md)

**Tables (1):** `ThreatIntelligenceIndicator`

Luminar IOCs and Leaked Credentials connector allows integration of intelligence-based IOC data and customer-related leaked records identified by Luminar.

[→ View full connector details](connectors/cognyteluminar.md)

---

## M

### [MISP2Sentinel](connectors/misp2sentinelconnector.md)

**Publisher:** MISP project & cudeso.be

**Solution:** [MISP2Sentinel](solutions/misp2sentinel.md)

**Tables (1):** `ThreatIntelligenceIndicator`

This solution installs the MISP2Sentinel connector that allows you to automatically push threat indicators from MISP to Microsoft Sentinel via the Upload Indicators REST API. After installing the solution, configure and enable this data connector by following guidance in Manage solution view.

[→ View full connector details](connectors/misp2sentinelconnector.md)

---

### [MailGuard 365](connectors/mailguard365.md)

**Publisher:** MailGuard365

**Solution:** [MailGuard 365](solutions/mailguard-365.md)

**Tables (1):** `MailGuard365_Threats_CL`

MailGuard 365 Enhanced Email Security for Microsoft 365. Exclusive to the Microsoft marketplace, MailGuard 365 is integrated with Microsoft 365 security (incl. Defender) for enhanced protection against advanced email threats like phishing, ransomware and sophisticated BEC attacks.

[→ View full connector details](connectors/mailguard365.md)

---

### [MailRisk by Secure Practice](connectors/securepracticemailriskconnector.md)

**Publisher:** Secure Practice

**Solution:** [MailRisk](solutions/mailrisk.md)

**Tables (1):** `MailRiskEventEmails_CL`

The MailRisk by Secure Practice connector allows you to ingest email threat intelligence data from the MailRisk API into Microsoft Sentinel. This connector provides visibility into reported emails, risk assessments, and security events related to email threats.

[→ View full connector details](connectors/securepracticemailriskconnector.md)

---

### [Microsoft Copilot](connectors/microsoftcopilot.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Copilot](solutions/microsoft-copilot.md)

**Tables (1):** `LLMActivity`

The Microsoft Copilot logs connector in Microsoft Sentinel enables the seamless ingestion of Copilot-generated activity logs into Microsoft Sentinel for advanced threat detection, investigation, and response. It collects telemetry from Microsoft Copilot services - such as usage data, prompts and system responses - and ingests into Microsoft Sentinel, allowing security teams to monitor for misuse, detect anomalies, and maintain compliance with organizational policies.

[→ View full connector details](connectors/microsoftcopilot.md)

---

### [Microsoft Defender Threat Intelligence](connectors/microsoftdefenderthreatintelligence.md)

**Publisher:** Microsoft

**Solution:** [Threat Intelligence](solutions/threat-intelligence.md)

**Tables (3):** `ThreatIntelIndicators`, `ThreatIntelObjects`, `ThreatIntelligenceIndicator`

Microsoft Sentinel provides you the capability to import threat intelligence generated by Microsoft to enable monitoring, alerting and hunting. Use this data connector to import Indicators of Compromise (IOCs) from Microsoft Defender Threat Intelligence (MDTI) into Microsoft Sentinel. Threat indicators can include IP addresses, domains, URLs, and file hashes, etc.

[→ View full connector details](connectors/microsoftdefenderthreatintelligence.md)

---

### [Microsoft Defender for Office 365 (Preview)](connectors/officeatp.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Defender for Office 365](solutions/microsoft-defender-for-office-365.md)

**Tables (1):** `SecurityAlert`

Microsoft Defender for Office 365 safeguards your organization against malicious threats posed by email messages, links (URLs) and collaboration tools. By ingesting Microsoft Defender for Office 365 alerts into Microsoft Sentinel, you can incorporate information about email- and URL-based threats into your broader risk analysis and build response scenarios accordingly.
 
The following types of alerts will be imported:

-   A potentially malicious URL click was detected 
-   Email messages containing malware removed after delivery
-   Email messages containing phish URLs removed after delivery
-   Email reported by user as malware or phish 
-   Suspicious email sending patterns detected 
-   User restricted from sending email 

These alerts can be seen by Office customers in the ** Office Security and Compliance Center**.

For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219942&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/officeatp.md)

---

### [Microsoft Exchange Admin Audit Logs by Event Logs](connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange On-Premises](solutions/microsoft-exchange-security---exchange-on-premises.md)

**Tables (1):** `Event`

[Option 1] - Using Azure Monitor Agent - You can stream all Exchange Audit events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

[→ View full connector details](connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md)

---

### [Microsoft Exchange HTTP Proxy Logs](connectors/esi-opt7exchangehttpproxylogs.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange On-Premises](solutions/microsoft-exchange-security---exchange-on-premises.md)

**Tables (1):** `ExchangeHttpProxy_CL`

[Option 7] - Using Azure Monitor Agent - You can stream HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you create custom alerts, and improve investigation. [Learn more](https://aka.ms/ESI_DataConnectorOptions)

[→ View full connector details](connectors/esi-opt7exchangehttpproxylogs.md)

---

### [Microsoft Exchange Logs and Events](connectors/esi-opt2exchangeserverseventlogs.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange On-Premises](solutions/microsoft-exchange-security---exchange-on-premises.md)

**Tables (1):** `Event`

[Option 2] - Using Azure Monitor Agent - You can stream all Exchange Security & Application Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

[→ View full connector details](connectors/esi-opt2exchangeserverseventlogs.md)

---

### [Microsoft Exchange Message Tracking Logs](connectors/esi-opt6exchangemessagetrackinglogs.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange On-Premises](solutions/microsoft-exchange-security---exchange-on-premises.md)

**Tables (1):** `MessageTrackingLog_CL`

[Option 6] - Using Azure Monitor Agent - You can stream all Exchange Message Tracking from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. Those logs can be used to track the flow of messages in your Exchange environment. This data connector is based on the option 6 of the [Microsoft Exchange Security wiki](https://aka.ms/ESI_DataConnectorOptions).

[→ View full connector details](connectors/esi-opt6exchangemessagetrackinglogs.md)

---

### [Microsoft PowerBI](connectors/officepowerbi.md)

**Publisher:** Microsoft

**Solution:** [Microsoft PowerBI](solutions/microsoft-powerbi.md)

**Tables (1):** `PowerBIActivity`

Microsoft PowerBI is a collection of software services, apps, and connectors that work together to turn your unrelated sources of data into coherent, visually immersive, and interactive insights. Your data may be an Excel spreadsheet, a collection of cloud-based and on-premises hybrid data warehouses, or a data store of some other type. This connector lets you stream PowerBI audit logs into Microsoft Sentinel, allowing you to track user activities in your PowerBI environment. You can filter the audit data by date range, user, dashboard, report, dataset, and activity type.

[→ View full connector details](connectors/officepowerbi.md)

---

### [Microsoft Purview](connectors/microsoftazurepurview.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Purview](solutions/microsoft-purview.md)

**Tables (1):** `PurviewDataSensitivityLogs`

Connect to Microsoft Purview to enable data sensitivity enrichment of Microsoft Sentinel. Data classification and sensitivity label logs from Microsoft Purview scans can be ingested and visualized through workbooks, analytical rules, and more. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2224125&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/microsoftazurepurview.md)

---

### [Microsoft Purview Information Protection](connectors/microsoftpurviewinformationprotection.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Purview Information Protection](solutions/microsoft-purview-information-protection.md)

**Tables (1):** `MicrosoftPurviewInformationProtection`

Microsoft Purview Information Protection helps you discover, classify, protect, and govern sensitive information wherever it lives or travels. Using these capabilities enable you to know your data, identify items that are sensitive and gain visibility into how they are being used to better protect your data. Sensitivity labels are the foundational capability that provide protection actions, applying encryption, access restrictions and visual markings.
    Integrate Microsoft Purview Information Protection logs with Microsoft Sentinel to view dashboards, create custom alerts and improve investigation. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223811&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/microsoftpurviewinformationprotection.md)

---

### [Mimecast Audit](connectors/mimecastauditapi.md)

**Publisher:** Mimecast

**Solution:** [Mimecast](solutions/mimecast.md)

**Tables (2):** `Audit_CL`, `MimecastAudit_CL`

The data connector for [Mimecast Audit](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to audit and authentication events within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into user activity, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  
The Mimecast products included within the connector are: 
Audit
 

[→ View full connector details](connectors/mimecastauditapi.md)

---

### [Mimecast Awareness Training](connectors/mimecastatapi.md)

**Publisher:** Mimecast

**Solution:** [Mimecast](solutions/mimecast.md)

**Tables (4):** `Awareness_Performance_Details_CL`, `Awareness_SafeScore_Details_CL`, `Awareness_User_Data_CL`, `Awareness_Watchlist_Details_CL`

The data connector for [Mimecast Awareness Training](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Targeted Threat Protection inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  
The Mimecast products included within the connector are: 
- Performance Details 
- Safe Score Details 
- User Data
- Watchlist Details


[→ View full connector details](connectors/mimecastatapi.md)

---

### [Mimecast Cloud Integrated](connectors/mimecastciapi.md)

**Publisher:** Mimecast

**Solution:** [Mimecast](solutions/mimecast.md)

**Tables (1):** `Cloud_Integrated_CL`

The data connector for [Mimecast Cloud Integrated](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Cloud Integrated inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.

[→ View full connector details](connectors/mimecastciapi.md)

---

### [Mimecast Intelligence for Microsoft - Microsoft Sentinel](connectors/mimecasttiregionalconnectorazurefunctions.md)

**Publisher:** Mimecast

**Solution:** [MimecastTIRegional](solutions/mimecasttiregional.md)

**Tables (2):** `Event`, `ThreatIntelligenceIndicator`

The data connector for Mimecast Intelligence for Microsoft provides regional threat intelligence curated from Mimecast’s email inspection technologies with pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times.  
Mimecast products and features required: 
- Mimecast Secure Email Gateway 
- Mimecast Threat Intelligence


[→ View full connector details](connectors/mimecasttiregionalconnectorazurefunctions.md)

---

### [Mimecast Secure Email Gateway](connectors/mimecastsegapi.md)

**Publisher:** Mimecast

**Solution:** [Mimecast](solutions/mimecast.md)

**Tables (2):** `Seg_Cg_CL`, `Seg_Dlp_CL`

The data connector for [Mimecast Secure Email Gateway](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) allows easy log collection from the Secure Email Gateway to surface email insight and user activity within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities. Mimecast products and features required: 
- Mimecast Cloud Gateway 
- Mimecast Data Leak Prevention
 

[→ View full connector details](connectors/mimecastsegapi.md)

---

### [Mimecast Secure Email Gateway](connectors/mimecastsiemapi.md)

**Publisher:** Mimecast

**Solution:** [MimecastSEG](solutions/mimecastseg.md)

**Tables (2):** `MimecastDLP_CL`, `MimecastSIEM_CL`

The data connector for [Mimecast Secure Email Gateway](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) allows easy log collection from the Secure Email Gateway to surface email insight and user activity within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities. Mimecast products and features required: 
- Mimecast Secure Email Gateway 
- Mimecast Data Leak Prevention
 

[→ View full connector details](connectors/mimecastsiemapi.md)

---

### [Mimecast Targeted Threat Protection](connectors/mimecastttpapi.md)

**Publisher:** Mimecast

**Solution:** [Mimecast](solutions/mimecast.md)

**Tables (6):** `MimecastTTPAttachment_CL`, `MimecastTTPImpersonation_CL`, `MimecastTTPUrl_CL`, `Ttp_Attachment_CL`, `Ttp_Impersonation_CL`, `Ttp_Url_CL`

The data connector for [Mimecast Targeted Threat Protection](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Targeted Threat Protection inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  
The Mimecast products included within the connector are: 
- URL Protect 
- Impersonation Protect 
- Attachment Protect


[→ View full connector details](connectors/mimecastttpapi.md)

---

### [MongoDB Atlas Logs](connectors/mongodbatlaslogsazurefunctions.md)

**Publisher:** MongoDB

**Solution:** [MongoDBAtlas](solutions/mongodbatlas.md)

**Tables (1):** `MDBALogTable_CL`

The [MongoDBAtlas](https://www.mongodb.com/products/platform/atlas-database) Logs connector gives the capability to upload MongoDB Atlas database logs into Microsoft Sentinel through the MongoDB Atlas Administration API. Refer to the [API documentation](https://www.mongodb.com/docs/api/doc/atlas-admin-api-v2/) for more information. The connector provides the ability to get a range of database log messages for the specified hosts and specified project.

[→ View full connector details](connectors/mongodbatlaslogsazurefunctions.md)

---

### [Morphisec API Data Connector (via Codeless Connector Framework)](connectors/morphisecccf.md)

**Publisher:** Morphisec

**Solution:** [Morphisec](solutions/morphisec.md)

**Tables (1):** `MorphisecAlerts_CL`

The [Morphisec](https://www.morphisec.com/) solution for Microsoft Sentinel enables you to seamlessly ingest security alerts directly from the Morphisec API. By leveraging Morphisec's proactive breach prevention and moving target defense capabilities, this integration enriches your security operations with high-fidelity, low-noise alerts on evasive threats.
This solution provides more than just data ingestion; it equips your security team with a full suite of ready-to-use content, including: Data Connector, ASIM Parser, Analytic Rule Templates and Workbook.
With this solution, you can empower your SOC to leverage Morphisec's powerful threat prevention within a unified investigation and response workflow in Microsoft Sentinel.

[→ View full connector details](connectors/morphisecccf.md)

---

### [MuleSoft Cloudhub](connectors/mulesoft.md)

**Publisher:** MuleSoft

**Solution:** [Mulesoft](solutions/mulesoft.md)

**Tables (1):** `MuleSoft_Cloudhub_CL`

The [MuleSoft Cloudhub](https://www.mulesoft.com/platform/saas/cloudhub-ipaas-cloud-based-integration) data connector provides the capability to retrieve logs from Cloudhub applications using the Cloudhub API and more events into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/mulesoft.md)

---

## N

### [NC Protect](connectors/nucleuscyberncprotect.md)

**Publisher:** archTIS

**Solution:** [archTIS](solutions/archtis.md)

**Tables (1):** `NCProtectUAL_CL`

[NC Protect Data Connector (archtis.com)](https://info.archtis.com/get-started-with-nc-protect-sentinel-data-connector) provides the capability to ingest user activity logs and events into Microsoft Sentinel. The connector provides visibility into NC Protect user activity logs and events in Microsoft Sentinel to improve monitoring and investigation capabilities

[→ View full connector details](connectors/nucleuscyberncprotect.md)

---

### [NXLog AIX Audit](connectors/nxlogaixaudit.md)

**Publisher:** NXLog

**Solution:** [NXLogAixAudit](solutions/nxlogaixaudit.md)

**Tables (1):** `AIX_Audit_CL`

The [NXLog AIX Audit](https://docs.nxlog.co/refman/current/im/aixaudit.html) data connector uses the AIX Audit subsystem to read events directly from the kernel for capturing audit events on the AIX platform. This REST API connector can efficiently export AIX Audit events to Microsoft Sentinel in real time.

[→ View full connector details](connectors/nxlogaixaudit.md)

---

### [NXLog BSM macOS](connectors/nxlogbsmmacos.md)

**Publisher:** NXLog

**Solution:** [NXLog BSM macOS](solutions/nxlog-bsm-macos.md)

**Tables (1):** `BSMmacOS_CL`

The [NXLog BSM](https://docs.nxlog.co/refman/current/im/bsm.html) macOS data connector uses Sun's Basic Security Module (BSM) Auditing API to read events directly from the kernel for capturing audit events on the macOS platform. This REST API connector can efficiently export macOS audit events to Microsoft Sentinel in real-time.

[→ View full connector details](connectors/nxlogbsmmacos.md)

---

### [NXLog DNS Logs](connectors/nxlogdnslogs.md)

**Publisher:** NXLog

**Solution:** [NXLogDnsLogs](solutions/nxlogdnslogs.md)

**Tables (1):** `NXLog_DNS_Server_CL`

The NXLog DNS Logs data connector uses Event Tracing for Windows ([ETW](https://docs.microsoft.com/windows/apps/trace-processing/overview)) for collecting both Audit and Analytical DNS Server events. The [NXLog *im_etw* module](https://docs.nxlog.co/refman/current/im/etw.html) reads event tracing data directly for maximum efficiency, without the need to capture the event trace into an .etl file. This REST API connector can forward DNS Server events to Microsoft Sentinel in real time.

[→ View full connector details](connectors/nxlogdnslogs.md)

---

### [NXLog FIM](connectors/nxlogfim.md)

**Publisher:** NXLog

**Solution:** [NXLog FIM](solutions/nxlog-fim.md)

**Tables (1):** `NXLogFIM_CL`

The [NXLog FIM](https://docs.nxlog.co/refman/current/im/fim.html) module allows for the scanning of files and directories, reporting detected additions, changes, renames and deletions on the designated paths through calculated checksums during successive scans. This REST API connector can efficiently export the configured FIM events to Microsoft Sentinel in real time.

[→ View full connector details](connectors/nxlogfim.md)

---

### [NXLog LinuxAudit](connectors/nxloglinuxaudit.md)

**Publisher:** NXLog

**Solution:** [NXLog LinuxAudit](solutions/nxlog-linuxaudit.md)

**Tables (1):** `LinuxAudit_CL`

The [NXLog LinuxAudit](https://docs.nxlog.co/refman/current/im/linuxaudit.html) data connector supports custom audit rules and collects logs without auditd or any other user-space software. IP addresses and group/user IDs are resolved to their respective names making [Linux audit](https://docs.nxlog.co/userguide/integrate/linux-audit.html) logs more intelligible to security analysts. This REST API connector can efficiently export Linux security events to Microsoft Sentinel in real-time.

[→ View full connector details](connectors/nxloglinuxaudit.md)

---

### [Netclean ProActive Incidents](connectors/netclean-proactive-incidents.md)

**Publisher:** NetClean Technologies

**Solution:** [NetClean ProActive](solutions/netclean-proactive.md)

**Tables (1):** `Netclean_Incidents_CL`

This connector uses the Netclean Webhook (required) and Logic Apps to push data into Microsoft Sentinel Log Analytics

[→ View full connector details](connectors/netclean-proactive-incidents.md)

---

### [Netskope](connectors/netskope.md)

**Publisher:** Netskope

**Solution:** [Netskope](solutions/netskope.md)

**Tables (1):** `Netskope_CL`

The [Netskope Cloud Security Platform](https://www.netskope.com/platform) connector provides the capability to ingest Netskope logs and events into Microsoft Sentinel. The connector provides visibility into Netskope Platform Events and Alerts in Microsoft Sentinel to improve monitoring and investigation capabilities.

[→ View full connector details](connectors/netskope.md)

---

### [Netskope Alerts and Events](connectors/netskopealertsevents.md)

**Publisher:** Netskope

**Solution:** [Netskopev2](solutions/netskopev2.md)

**Tables (9):** `NetskopeAlerts_CL`, `NetskopeEventsApplication_CL`, `NetskopeEventsAudit_CL`, `NetskopeEventsConnection_CL`, `NetskopeEventsDLP_CL`, `NetskopeEventsEndpoint_CL`, `NetskopeEventsInfrastructure_CL`, `NetskopeEventsNetwork_CL`, `NetskopeEventsPage_CL`

Netskope Security Alerts and Events

[→ View full connector details](connectors/netskopealertsevents.md)

---

### [Netskope Data Connector](connectors/netskopedataconnector.md)

**Publisher:** Netskope

**Solution:** [Netskopev2](solutions/netskopev2.md)

**Tables (17):** `Netskope_WebTx_metrics_CL`, `alertscompromisedcredentialdata_CL`, `alertsctepdata_CL`, `alertsdlpdata_CL`, `alertsmalsitedata_CL`, `alertsmalwaredata_CL`, `alertspolicydata_CL`, `alertsquarantinedata_CL`, `alertsremediationdata_CL`, `alertssecurityassessmentdata_CL`, `alertsubadata_CL`, `eventsapplicationdata_CL`, `eventsauditdata_CL`, `eventsconnectiondata_CL`, `eventsincidentdata_CL`, `eventsnetworkdata_CL`, `eventspagedata_CL`

The [Netskope](https://docs.netskope.com/en/netskope-help/admin-console/rest-api/rest-api-v2-overview-312207/) data connector provides the following capabilities: 
 1. NetskopeToAzureStorage : 
 >* Get the Netskope Alerts and Events data from Netskope and ingest to Azure storage. 
 2. StorageToSentinel : 
 >* Get the Netskope Alerts and Events data from Azure storage and ingest to custom log table in log analytics workspace. 
 3. WebTxMetrics : 
 >* Get the WebTxMetrics data from Netskope and ingest to custom log table in log analytics workspace.


 For more details of REST APIs refer to the below documentations: 
 1. Netskope API documentation: 
> https://docs.netskope.com/en/netskope-help/admin-console/rest-api/rest-api-v2-overview-312207/ 
 2. Azure storage documentation: 
> https://learn.microsoft.com/azure/storage/common/storage-introduction 
 3. Microsoft log analytic documentation: 
> https://learn.microsoft.com/azure/azure-monitor/logs/log-analytics-overview

[→ View full connector details](connectors/netskopedataconnector.md)

---

### [Netskope Web Transactions Data Connector](connectors/netskopewebtransactionsdataconnector.md)

**Publisher:** Netskope

**Solution:** [Netskopev2](solutions/netskopev2.md)

**Tables (2):** `NetskopeWebtxData_CL`, `NetskopeWebtxErrors_CL`

The [Netskope Web Transactions](https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/) data connector provides the functionality of a docker image to pull the Netskope Web Transactions data from google pubsublite, process the data and ingest the processed data to Log Analytics. As part of this data connector two tables will be formed in Log Analytics, one for Web Transactions data and other for errors encountered during execution.


 For more details related to Web Transactions refer to the below documentation: 
 1. Netskope Web Transactions documentation: 
> https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/ 


[→ View full connector details](connectors/netskopewebtransactionsdataconnector.md)

---

### [Noname Security for Microsoft Sentinel](connectors/nonamesecuritymicrosoftsentinel.md)

**Publisher:** Noname Security

**Solution:** [NonameSecurity](solutions/nonamesecurity.md)

**Tables (1):** `NonameAPISecurityAlert_CL`

Noname Security solution to POST data into a Microsoft Sentinel SIEM workspace via the Azure Monitor REST API

[→ View full connector details](connectors/nonamesecuritymicrosoftsentinel.md)

---

### [NordPass](connectors/nordpass.md)

**Publisher:** NordPass

**Solution:** [NordPass](solutions/nordpass.md)

**Tables (1):** `NordPassEventLogs_CL`

Integrating NordPass with Microsoft Sentinel SIEM via the API will allow you to automatically transfer Activity Log data from NordPass to Microsoft Sentinel and get real-time insights, such as item activity, all login attempts, and security notifications.

[→ View full connector details](connectors/nordpass.md)

---

## O

### [Obsidian Datasharing Connector](connectors/obsidiandatasharing.md)

**Publisher:** Obsidian Security

**Solution:** [Obsidian Datasharing](solutions/obsidian-datasharing.md)

**Tables (2):** `ObsidianActivity_CL`, `ObsidianThreat_CL`

The Obsidian Datasharing connector provides the capability to read raw event data from Obsidian Datasharing in Microsoft Sentinel.

[→ View full connector details](connectors/obsidiandatasharing.md)

---

### [Okta Single Sign-On](connectors/oktasso.md)

**Publisher:** Okta

**Solution:** [Okta Single Sign-On](solutions/okta-single-sign-on.md)

**Tables (1):** `Okta_CL`

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) connector provides the capability to ingest audit and event logs from the Okta API into Microsoft Sentinel. The connector provides visibility into these log types in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

[→ View full connector details](connectors/oktasso.md)

---

### [Okta Single Sign-On](connectors/oktassov2.md)

**Publisher:** Microsoft

**Solution:** [Okta Single Sign-On](solutions/okta-single-sign-on.md)

**Tables (3):** `OktaV2_CL`, `Okta_CL`, `signIns`

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) data connector provides the capability to ingest audit and event logs from the Okta Sysem Log API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform and uses the Okta System Log API to fetch the events. The connector supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

[→ View full connector details](connectors/oktassov2.md)

---

### [Okta Single Sign-On (Polling CCP)](connectors/oktasso-polling.md)

**Publisher:** Okta

**Solution:** [Okta Single Sign-On](solutions/okta-single-sign-on.md)

**Tables (1):** `OktaNativePoller_CL`

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) connector provides the capability to ingest audit and event logs from the Okta API into Microsoft entinel. The connector provides visibility into these log types in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

[→ View full connector details](connectors/oktasso-polling.md)

---

### [Onapsis Defend Integration](connectors/onapsis.md)

**Publisher:** Onapsis Platform

**Solution:** [Onapsis Defend](solutions/onapsis-defend.md)

**Tables (1):** `Onapsis_Defend_CL`

Onapsis Defend Integration is aimed at forwarding alerts and logs collected and detected by Onapsis Platform into Microsoft Sentinel SIEM

[→ View full connector details](connectors/onapsis.md)

---

### [OneLogin IAM Platform (via Codeless Connector Framework)](connectors/oneloginiamlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [OneLoginIAM](solutions/oneloginiam.md)

**Tables (2):** `OneLoginEventsV2_CL`, `OneLoginUsersV2_CL`

The [OneLogin](https://www.onelogin.com/) data connector provides the capability to ingest common OneLogin IAM Platform events into Microsoft Sentinel through REST API by using OneLogin [Events API](https://developers.onelogin.com/api-docs/1/events/get-events) and OneLogin [Users API](https://developers.onelogin.com/api-docs/1/users/get-users). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/oneloginiamlogsccpdefinition.md)

---

### [OneTrust](connectors/onetrustpush.md)

**Publisher:** OneTrust

**Solution:** [OneTrust](solutions/onetrust.md)

**Tables (1):** `OneTrustMetadataV3_CL`

The OneTrust connector for Microsoft Sentinel provides the capability to have near real time visibility into where sensitive data has been located or remediated across across Google Cloud and other OneTrust supported data sources.

[→ View full connector details](connectors/onetrustpush.md)

---

### [Oracle Cloud Infrastructure (via Codeless Connector Framework)](connectors/oci-connector-ccp-definition.md)

**Publisher:** Microsoft

**Solution:** [Oracle Cloud Infrastructure](solutions/oracle-cloud-infrastructure.md)

**Tables (1):** `OCI_LogsV2_CL`

The Oracle Cloud Infrastructure (OCI) data connector provides the capability to ingest OCI Logs from [OCI Stream](https://docs.oracle.com/iaas/Content/Streaming/Concepts/streamingoverview.htm) into Microsoft Sentinel using the [OCI Streaming REST API](https://docs.oracle.com/iaas/api/#/streaming/streaming/20180418).

[→ View full connector details](connectors/oci-connector-ccp-definition.md)

---

### [Orca Security Alerts](connectors/orcasecurityalerts.md)

**Publisher:** Orca Security

**Solution:** [Orca Security Alerts](solutions/orca-security-alerts.md)

**Tables (1):** `OrcaAlerts_CL`

The Orca Security Alerts connector allows you to easily export Alerts logs to Microsoft Sentinel.

[→ View full connector details](connectors/orcasecurityalerts.md)

---

## P

### [Palo Alto Cortex XDR](connectors/cortexxdrdataconnector.md)

**Publisher:** Microsoft

**Solution:** [Cortex XDR](solutions/cortex-xdr.md)

**Tables (5):** `PaloAltoCortexXDR_Alerts_CL`, `PaloAltoCortexXDR_Audit_Agent_CL`, `PaloAltoCortexXDR_Audit_Management_CL`, `PaloAltoCortexXDR_Endpoints_CL`, `PaloAltoCortexXDR_Incidents_CL`

The [Palo Alto Cortex XDR](https://cortex-panw.stoplight.io/docs/cortex-xdr/branches/main/09agw06t5dpvw-cortex-xdr-rest-api) data connector allows ingesting logs from the Palo Alto Cortex XDR API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the Palo Alto Cortex XDR API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

[→ View full connector details](connectors/cortexxdrdataconnector.md)

---

### [Palo Alto Cortex Xpanse (via Codeless Connector Framework)](connectors/paloaltoexpanseccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Palo Alto Cortex Xpanse CCF](solutions/palo-alto-cortex-xpanse-ccf.md)

**Tables (1):** `CortexXpanseAlerts_CL`

The Palo Alto Cortex Xpanse data connector ingests alerts data into Microsoft Sentinel.

[→ View full connector details](connectors/paloaltoexpanseccpdefinition.md)

---

### [Palo Alto Networks Cortex XDR](connectors/paloaltonetworkscortex.md)

**Publisher:** Palo Alto Networks

**Solution:** [Palo Alto - XDR (Cortex)](solutions/palo-alto---xdr-(cortex).md)

**Tables (1):** `CommonSecurityLog`

The Palo Alto Networks Cortex XDR connector gives you an easy way to connect to your Cortex XDR logs with Microsoft Sentinel. This increases the visibility of your endpoint security. It will give you better ability to monitor your resources by creating custom Workbooks, analytics rules, Incident investigation, and evidence gathering.

[→ View full connector details](connectors/paloaltonetworkscortex.md)

---

### [Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework)](connectors/paloaltoprismacloudcspmccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [PaloAltoPrismaCloud](solutions/paloaltoprismacloud.md)

**Tables (2):** `PaloAltoPrismaCloudAlertV2_CL`, `PaloAltoPrismaCloudAuditV2_CL`

The Palo Alto Prisma Cloud CSPM data connector allows you to connect to your Palo Alto Prisma Cloud CSPM instance and ingesting Alerts (https://pan.dev/prisma-cloud/api/cspm/alerts/) & Audit Logs(https://pan.dev/prisma-cloud/api/cspm/audit-logs/) into Microsoft Sentinel.

[→ View full connector details](connectors/paloaltoprismacloudcspmccpdefinition.md)

---

### [Palo Alto Prisma Cloud CWPP (using REST API)](connectors/paloaltoprismacloudcwpp.md)

**Publisher:** Microsoft

**Solution:** [Palo Alto Prisma Cloud CWPP](solutions/palo-alto-prisma-cloud-cwpp.md)

**Tables (1):** `PrismaCloudCompute_CL`

The [Palo Alto Prisma Cloud CWPP](https://prisma.pan.dev/api/cloud/cwpp/audits/#operation/get-audits-incidents) data connector allows you to connect to your Palo Alto Prisma Cloud CWPP instance and ingesting alerts into Microsoft Sentinel. The data connector is built on Microsoft Sentinel's Codeless Connector Platform and uses the Prisma Cloud API to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

[→ View full connector details](connectors/paloaltoprismacloudcwpp.md)

---

### [Palo Alto Prisma Cloud CWPP (using REST API)](connectors/prismacloudcomputenativepoller.md)

**Publisher:** Microsoft

**Solution:** [Palo Alto Prisma Cloud CWPP](solutions/palo-alto-prisma-cloud-cwpp.md)

**Tables (1):** `PrismaCloudCompute_CL`

The [Palo Alto Prisma Cloud CWPP](https://prisma.pan.dev/api/cloud/cwpp/audits/#operation/get-audits-incidents) data connector allows you to connect to your Prisma Cloud CWPP instance and ingesting alerts into Microsoft Sentinel. The data connector is built on Microsoft Sentinel’s Codeless Connector Platform and uses the Prisma Cloud API to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

[→ View full connector details](connectors/prismacloudcomputenativepoller.md)

---

### [Pathlock Inc.: Threat Detection and Response for SAP](connectors/pathlock-tdnr.md)

**Publisher:** Pathlock Inc.

**Solution:** [Pathlock_TDnR](solutions/pathlock-tdnr.md)

**Tables (2):** `ABAPAuditLog`, `Pathlock_TDnR_CL`

The [Pathlock Threat Detection and Response (TD&R)](https://pathlock.com/products/cybersecurity-application-controls/) integration with **Microsoft Sentinel Solution for SAP** delivers unified, real-time visibility into SAP security events, enabling organizations to detect and act on threats across all SAP landscapes. This out-of-the-box integration allows Security Operations Centers (SOCs) to correlate SAP-specific alerts with enterprise-wide telemetry, creating actionable intelligence that connects IT security with business processes.

Pathlock’s connector is purpose-built for SAP and forwards only **security-relevant events by default**, minimizing data volume and noise while maintaining the flexibility to forward all log sources when needed. Each event is enriched with **business process context**, allowing Microsoft Sentinel Solution for SAP analytics to distinguish operational patterns from real threats and to prioritize what truly matters.

This precision-driven approach helps security teams drastically reduce false positives, focus investigations, and accelerate **mean time to detect (MTTD)** and **mean time to respond (MTTR)**. Pathlock’s library consists of more than 1,500 SAP-specific detection signatures across 70+ log sources, the solution uncovers complex attack behaviors, configuration weaknesses, and access anomalies.

By combining business-context intelligence with advanced analytics, Pathlock enables enterprises to strengthen detection accuracy, streamline response actions, and maintain continuous control across their SAP environments—without adding complexity or redundant monitoring layers.

[→ View full connector details](connectors/pathlock-tdnr.md)

---

### [Perimeter 81 Activity Logs](connectors/perimeter81activitylogs.md)

**Publisher:** Perimeter 81

**Solution:** [Perimeter 81](solutions/perimeter-81.md)

**Tables (1):** `Perimeter81_CL`

The Perimeter 81 Activity Logs connector allows you to easily connect your Perimeter 81 activity logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.

[→ View full connector details](connectors/perimeter81activitylogs.md)

---

### [Phosphorus Devices](connectors/phosphorus-polling.md)

**Publisher:** Phosphorus Inc.

**Solution:** [Phosphorus](solutions/phosphorus.md)

**Tables (1):** `Phosphorus_CL`

The Phosphorus Device Connector provides the capability to Phosphorus to ingest device data logs into Microsoft Sentinel through the Phosphorus REST API. The Connector provides visibility into the devices enrolled in Phosphorus. This Data Connector pulls devices information along with its corresponding alerts.

[→ View full connector details](connectors/phosphorus-polling.md)

---

### [Ping One (via Codeless Connector Framework)](connectors/pingoneauditlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [PingOne](solutions/pingone.md)

**Tables (1):** `PingOne_AuditActivitiesV2_CL`

This connector ingests **audit activity logs** from the PingOne Identity platform into Microsoft Sentinel using a Codeless Connector Framework.

[→ View full connector details](connectors/pingoneauditlogsccpdefinition.md)

---

### [Prancer Data Connector](connectors/prancerlogdata.md)

**Publisher:** Prancer

**Solution:** [Prancer PenSuiteAI Integration](solutions/prancer-pensuiteai-integration.md)

**Tables (1):** `prancer_CL`

The Prancer Data Connector has provides the capability to ingest Prancer (CSPM)[https://docs.prancer.io/web/CSPM/] and [PAC](https://docs.prancer.io/web/PAC/introduction/) data to process through Microsoft Sentinel. Refer to [Prancer Documentation](https://docs.prancer.io/web) for more information.

[→ View full connector details](connectors/prancerlogdata.md)

---

### [Premium Microsoft Defender Threat Intelligence](connectors/premiummicrosoftdefenderforthreatintelligence.md)

**Publisher:** Microsoft

**Solution:** [Threat Intelligence](solutions/threat-intelligence.md)

**Tables (3):** `ThreatIntelIndicators`, `ThreatIntelObjects`, `ThreatIntelligenceIndicator`

Microsoft Sentinel provides you the capability to import threat intelligence generated by Microsoft to enable monitoring, alerting and hunting. Use this data connector to import Indicators of Compromise (IOCs) from Premium Microsoft Defender Threat Intelligence (MDTI) into Microsoft Sentinel. Threat indicators can include IP addresses, domains, URLs, and file hashes, etc. Note: This is a paid connector. To use and ingest data from it, please purchase the "MDTI API Access" SKU from the Partner Center.

[→ View full connector details](connectors/premiummicrosoftdefenderforthreatintelligence.md)

---

### [Proofpoint On Demand Email Security (via Codeless Connector Platform)](connectors/proofpointccpdefinition.md)

**Publisher:** Proofpoint

**Solution:** [Proofpoint On demand(POD) Email Security](solutions/proofpoint-on-demand(pod)-email-security.md)

**Tables (2):** `ProofpointPODMailLog_CL`, `ProofpointPODMessage_CL`

Proofpoint On Demand Email Security data connector provides the capability to get Proofpoint on Demand Email Protection data, allows users to check message traceability, monitoring into email activity, threats,and data exfiltration by attackers and malicious insiders. The connector provides ability to review events in your org on an accelerated basis, get event log files in hourly increments for recent activity.

[→ View full connector details](connectors/proofpointccpdefinition.md)

---

### [Proofpoint TAP (via Codeless Connector Platform)](connectors/proofpointtapv2.md)

**Publisher:** Proofpoint

**Solution:** [ProofPointTap](solutions/proofpointtap.md)

**Tables (4):** `ProofPointTAPClicksBlockedV2_CL`, `ProofPointTAPClicksPermittedV2_CL`, `ProofPointTAPMessagesBlockedV2_CL`, `ProofPointTAPMessagesDeliveredV2_CL`

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

[→ View full connector details](connectors/proofpointtapv2.md)

---

## Q

### [QscoutAppEventsConnector](connectors/qscoutappeventsccfdefinition.md)

**Publisher:** Quokka

**Solution:** [Quokka](solutions/quokka.md)

**Tables (1):** `QscoutAppEvents_CL`

Ingest Qscout application events into Microsoft Sentinel

[→ View full connector details](connectors/qscoutappeventsccfdefinition.md)

---

### [Qualys VM KnowledgeBase](connectors/qualyskb.md)

**Publisher:** Qualys

**Solution:** [Qualys VM Knowledgebase](solutions/qualys-vm-knowledgebase.md)

**Tables (1):** `QualysKB_CL`

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) KnowledgeBase (KB) connector provides the capability to ingest the latest vulnerability data from the Qualys KB into Microsoft Sentinel. 

 This data can used to correlate and enrich vulnerability detections found by the [Qualys Vulnerability Management (VM)](https://docs.microsoft.com/azure/sentinel/connect-qualys-vm) data connector.

[→ View full connector details](connectors/qualyskb.md)

---

### [Qualys Vulnerability Management (via Codeless Connector Framework)](connectors/qualysvmlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [QualysVM](solutions/qualysvm.md)

**Tables (1):** `QualysHostDetectionV3_CL`

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) data connector provides the capability to ingest vulnerability host detection data into Microsoft Sentinel through the Qualys API. The connector provides visibility into host detection data from vulerability scans.

[→ View full connector details](connectors/qualysvmlogsccpdefinition.md)

---

## R

### [RSA ID Plus Admin Logs Connector](connectors/rsaidplus-adminglogs-connector.md)

**Publisher:** RSA

**Solution:** [RSAIDPlus_AdminLogs_Connector](solutions/rsaidplus-adminlogs-connector.md)

**Tables (1):** `RSAIDPlus_AdminLogs_CL`

The RSA ID Plus AdminLogs Connector provides the capability to ingest [Cloud Admin Console Audit Events](https://community.rsa.com/s/article/Cloud-Administration-Event-Log-API-5d22ba17) into Microsoft Sentinel using Cloud Admin APIs.

[→ View full connector details](connectors/rsaidplus-adminglogs-connector.md)

---

### [Radiflow iSID via AMA](connectors/radiflowisid.md)

**Publisher:** Radiflow

**Solution:** [Radiflow](solutions/radiflow.md)

**Tables (1):** `CommonSecurityLog`

iSID enables non-disruptive monitoring of distributed ICS networks for changes in topology and behavior, using multiple security packages, each offering a unique capability pertaining to a specific type of network activity

[→ View full connector details](connectors/radiflowisid.md)

---

### [Rapid7 Insight Platform Vulnerability Management Reports](connectors/insightvmcloudapi.md)

**Publisher:** Rapid7

**Solution:** [Rapid7InsightVM](solutions/rapid7insightvm.md)

**Tables (2):** `NexposeInsightVMCloud_assets_CL`, `NexposeInsightVMCloud_vulnerabilities_CL`

The [Rapid7 Insight VM](https://www.rapid7.com/products/insightvm/) Report data connector provides the capability to ingest Scan reports and vulnerability data into Microsoft Sentinel through the REST API from the  Rapid7 Insight platform (Managed in the cloud). Refer to [API documentation](https://docs.rapid7.com/insight/api-overview/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/insightvmcloudapi.md)

---

### [Red Canary Threat Detection](connectors/redcanarydataconnector.md)

**Publisher:** Red Canary

**Solution:** [Red Canary](solutions/red-canary.md)

**Tables (1):** `RedCanaryDetections_CL`

The Red Canary data connector provides the capability to ingest published Detections into Microsoft Sentinel using the Data Collector REST API.

[→ View full connector details](connectors/redcanarydataconnector.md)

---

### [Rubrik Security Cloud data connector](connectors/rubriksecuritycloudazurefunctions.md)

**Publisher:** Rubrik, Inc

**Solution:** [RubrikSecurityCloud](solutions/rubriksecuritycloud.md)

**Tables (4):** `Rubrik_Anomaly_Data_CL`, `Rubrik_Events_Data_CL`, `Rubrik_Ransomware_Data_CL`, `Rubrik_ThreatHunt_Data_CL`

The Rubrik Security Cloud data connector enables security operations teams to integrate insights from Rubrik's Data Observability services into Microsoft Sentinel. The insights include identification of anomalous filesystem behavior associated with ransomware and mass deletion, assess the blast radius of a ransomware attack, and sensitive data operators to prioritize and more rapidly investigate potential incidents.

[→ View full connector details](connectors/rubriksecuritycloudazurefunctions.md)

---

## S

### [SAP BTP](connectors/sapbtpauditevents.md)

**Publisher:** Microsoft

**Solution:** [SAP BTP](solutions/sap-btp.md)

**Tables (1):** `SAPBTPAuditLog_CL`

SAP Business Technology Platform (SAP BTP) brings together data management, analytics, artificial intelligence, application development, automation, and integration in one, unified environment.

[→ View full connector details](connectors/sapbtpauditevents.md)

---

### [SAP Enterprise Threat Detection, cloud edition](connectors/sapetdalerts.md)

**Publisher:** SAP

**Solution:** [SAP ETD Cloud](solutions/sap-etd-cloud.md)

**Tables (2):** `SAPETDAlerts_CL`, `SAPETDInvestigations_CL`

The SAP Enterprise Threat Detection, cloud edition (ETD) data connector enables ingestion of security alerts from ETD into Microsoft Sentinel, supporting cross-correlation, alerting, and threat hunting.

[→ View full connector details](connectors/sapetdalerts.md)

---

### [SAP LogServ (RISE), S/4HANA Cloud private edition](connectors/saplogserv.md)

**Publisher:** SAP SE

**Solution:** [SAP LogServ](solutions/sap-logserv.md)

**Tables (1):** `SAPLogServ_CL`

SAP LogServ is an SAP Enterprise Cloud Services (ECS) service aimed at collection, storage, forwarding and access of logs. LogServ centralizes the logs from all systems, applications, and ECS services used by a registered customer. 
 Main Features include:
Near Realtime Log Collection: With ability to integrate into Microsoft Sentinel as SIEM solution.
LogServ complements the existing SAP application layer threat monitoring and detections in Microsoft Sentinel with the log types owned by SAP ECS as the system provider. This includes logs like: SAP Security Audit Log (AS ABAP), HANA database, AS JAVA, ICM, SAP Web Dispatcher, SAP Cloud Connector, OS, SAP Gateway, 3rd party Database, Network, DNS, Proxy, Firewall

[→ View full connector details](connectors/saplogserv.md)

---

### [SAP S/4HANA Cloud Public Edition](connectors/saps4publicalerts.md)

**Publisher:** SAP

**Solution:** [SAP S4 Cloud Public Edition](solutions/sap-s4-cloud-public-edition.md)

**Tables (1):** `ABAPAuditLog`

The SAP S/4HANA Cloud Public Edition (GROW with SAP) data connector enables ingestion of SAP's security audit log into the Microsoft Sentinel Solution for SAP, supporting cross-correlation, alerting, and threat hunting. Looking for alternative authentication mechanisms? See [here](https://github.com/Azure-Samples/Sentinel-For-SAP-Community/tree/main/integration-artifacts).

[→ View full connector details](connectors/saps4publicalerts.md)

---

### [SINEC Security Guard](connectors/ssg.md)

**Publisher:** Siemens AG

**Solution:** [SINEC Security Guard](solutions/sinec-security-guard.md)

**Tables (1):** `SINECSecurityGuard_CL`

The SINEC Security Guard solution for Microsoft Sentinel allows you to ingest security events of your industrial networks from the [SINEC Security Guard](https://siemens.com/sinec-security-guard) into Microsoft Sentinel

[→ View full connector details](connectors/ssg.md)

---

### [SOC Prime Platform Audit Logs Data Connector](connectors/socprimeauditlogsdataconnector.md)

**Publisher:** Microsoft

**Solution:** [SOC Prime CCF](solutions/soc-prime-ccf.md)

**Tables (1):** `SOCPrimeAuditLogs_CL`

The [SOC Prime Audit Logs](https://help.socprime.com/en/articles/6265791-api) data connector allows ingesting logs from the SOC Prime Platform API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SOC Prime Platform API to fetch SOC Prime platform audit logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table, thus resulting in better performance.

[→ View full connector details](connectors/socprimeauditlogsdataconnector.md)

---

### [SaaS Security](connectors/valencesecurity.md)

**Publisher:** Valence Security

**Solution:** [Valence Security](solutions/valence-security.md)

**Tables (1):** `ValenceAlert_CL`

Connects the Valence SaaS security platform Azure Log Analytics via the REST API interface.

[→ View full connector details](connectors/valencesecurity.md)

---

### [SailPoint IdentityNow](connectors/sailpointidentitynow.md)

**Publisher:** SailPoint

**Solution:** [SailPointIdentityNow](solutions/sailpointidentitynow.md)

**Tables (2):** `SailPointIDN_Events_CL`, `SailPointIDN_Triggers_CL`

The [SailPoint](https://www.sailpoint.com/) IdentityNow data connector provides the capability to ingest [SailPoint IdentityNow] search events into Microsoft Sentinel through the REST API. The connector provides customers the ability to extract audit information from their IdentityNow tenant. It is intended to make it even easier to bring IdentityNow user activity and governance events into Microsoft Sentinel to improve insights from your security incident and event monitoring solution.

[→ View full connector details](connectors/sailpointidentitynow.md)

---

### [Salesforce Service Cloud (via Codeless Connector Framework)](connectors/salesforceservicecloudccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Salesforce Service Cloud](solutions/salesforce-service-cloud.md)

**Tables (1):** `SalesforceServiceCloudV2_CL`

The Salesforce Service Cloud data connector provides the capability to ingest information about your Salesforce operational events into Microsoft Sentinel through the REST API. The connector provides ability to review events in your org on an accelerated basis, get [event log files](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/event_log_file_hourly_overview.htm) in hourly increments for recent activity.

[→ View full connector details](connectors/salesforceservicecloudccpdefinition.md)

---

### [Samsung Knox Asset Intelligence](connectors/samsungdcdefinition.md)

**Publisher:** Samsung

**Solution:** [Samsung Knox Asset Intelligence](solutions/samsung-knox-asset-intelligence.md)

**Tables (6):** `Samsung_Knox_Application_CL`, `Samsung_Knox_Audit_CL`, `Samsung_Knox_Network_CL`, `Samsung_Knox_Process_CL`, `Samsung_Knox_System_CL`, `Samsung_Knox_User_CL`

Samsung Knox Asset Intelligence Data Connector lets you centralize your mobile security events and logs in order to view customized insights using the Workbook template, and identify incidents based on Analytics Rules templates.

[→ View full connector details](connectors/samsungdcdefinition.md)

---

### [SecurityBridge Solution for SAP](connectors/securitybridge.md)

**Publisher:** SecurityBridge Group GmbH

**Solution:** [SecurityBridge App](solutions/securitybridge-app.md)

**Tables (1):** `ABAPAuditLog`

SecurityBridge enhances SAP security by integrating seamlessly with Microsoft Sentinel, enabling real-time monitoring and threat detection across SAP environments. This integration allows Security Operations Centers (SOCs) to consolidate SAP security events with other organizational data, providing a unified view of the threat landscape . Leveraging AI-powered analytics and Microsoft’s Security Copilot, SecurityBridge identifies sophisticated attack patterns and vulnerabilities within SAP applications, including ABAP code scanning and configuration assessments . The solution supports scalable deployments across complex SAP landscapes, whether on-premises, in the cloud, or hybrid environments . By bridging the gap between IT and SAP security teams, SecurityBridge empowers organizations to proactively detect, investigate, and respond to threats, enhancing overall security posture.

[→ View full connector details](connectors/securitybridge.md)

---

### [SecurityBridge Threat Detection for SAP](connectors/securitybridgesap.md)

**Publisher:** SecurityBridge

**Solution:** [SecurityBridge App](solutions/securitybridge-app.md)

**Tables (1):** `SecurityBridgeLogs_CL`

SecurityBridge is the first and only holistic, natively integrated security platform, addressing all aspects needed to protect organizations running SAP from internal and external threats against their core business applications. The SecurityBridge platform is an SAP-certified add-on, used by organizations around the globe, and addresses the clients’ need for advanced cybersecurity, real-time monitoring, compliance, code security, and patching to protect against internal and external threats.This Microsoft Sentinel Solution allows you to integrate SecurityBridge Threat Detection events from all your on-premise and cloud based SAP instances into your security monitoring.Use this Microsoft Sentinel Solution to receive normalized and speaking security events, pre-built dashboards and out-of-the-box templates for your SAP security monitoring.

[→ View full connector details](connectors/securitybridgesap.md)

---

### [SecurityScorecard Cybersecurity Ratings](connectors/securityscorecardratingsazurefunctions.md)

**Publisher:** SecurityScorecard

**Solution:** [SecurityScorecard Cybersecurity Ratings](solutions/securityscorecard-cybersecurity-ratings.md)

**Tables (1):** `SecurityScorecardRatings_CL`

SecurityScorecard is the leader in cybersecurity risk ratings. The [SecurityScorecard](https://www.SecurityScorecard.com/) data connector provides the ability for Sentinel to import SecurityScorecard ratings as logs. SecurityScorecard provides ratings for over 12 million companies and domains using countless data points from across the internet. Maintain full awareness of any company's security posture and be able to receive timely updates when scores change or drop. SecurityScorecard ratings are updated daily based on evidence collected across the web.

[→ View full connector details](connectors/securityscorecardratingsazurefunctions.md)

---

### [SecurityScorecard Factor](connectors/securityscorecardfactorazurefunctions.md)

**Publisher:** SecurityScorecard

**Solution:** [SecurityScorecard Cybersecurity Ratings](solutions/securityscorecard-cybersecurity-ratings.md)

**Tables (1):** `SecurityScorecardFactor_CL`

SecurityScorecard is the leader in cybersecurity risk ratings. The [SecurityScorecard](https://www.SecurityScorecard.com/) Factors data connector provides the ability for Sentinel to import SecurityScorecard factor ratings as logs. SecurityScorecard provides ratings for over 12 million companies and domains using countless data points from across the internet. Maintain full awareness of any company's security posture and be able to receive timely updates when factor scores change or drop. SecurityScorecard factor ratings are updated daily based on evidence collected across the web.

[→ View full connector details](connectors/securityscorecardfactorazurefunctions.md)

---

### [SecurityScorecard Issue](connectors/securityscorecardissueazurefunctions.md)

**Publisher:** SecurityScorecard

**Solution:** [SecurityScorecard Cybersecurity Ratings](solutions/securityscorecard-cybersecurity-ratings.md)

**Tables (1):** `SecurityScorecardIssues_CL`

SecurityScorecard is the leader in cybersecurity risk ratings. The [SecurityScorecard](https://www.SecurityScorecard.com/) Issues data connector provides the ability for Sentinel to import SecurityScorecard issue data as logs. SecurityScorecard provides ratings for over 12 million companies and domains using countless data points from across the internet. Maintain full awareness of any company's security posture and be able to receive timely updates when new cybersecurity issues are discovered.

[→ View full connector details](connectors/securityscorecardissueazurefunctions.md)

---

### [Semperis Directory Services Protector](connectors/semperisdsp.md)

**Publisher:** SEMPERIS

**Solution:** [Semperis Directory Services Protector](solutions/semperis-directory-services-protector.md)

**Tables (1):** `SecurityEvent`

Semperis Directory Services Protector data connector allows for the export of its Windows event logs (i.e. Indicators of Exposure and Indicators of Compromise) to Microsoft Sentinel in real time.
It provides a data parser to manipulate the Windows event logs more easily. The different workbooks ease your Active Directory security monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

[→ View full connector details](connectors/semperisdsp.md)

---

### [SenservaPro (Preview)](connectors/senservapro.md)

**Publisher:** Senserva

**Solution:** [SenservaPro](solutions/senservapro.md)

**Tables (1):** `SenservaPro_CL`

The SenservaPro data connector provides a viewing experience for your SenservaPro scanning logs. View dashboards of your data, use queries to hunt & explore, and create custom alerts.

[→ View full connector details](connectors/senservapro.md)

---

### [SentinelOne](connectors/sentinelone.md)

**Publisher:** SentinelOne

**Solution:** [SentinelOne](solutions/sentinelone.md)

**Tables (1):** `SentinelOne_CL`

The [SentinelOne](https://www.sentinelone.com/) data connector provides the capability to ingest common SentinelOne server objects such as Threats, Agents, Applications, Activities, Policies, Groups, and more events into Microsoft Sentinel through the REST API. Refer to API documentation: `https://<SOneInstanceDomain>.sentinelone.net/api-doc/overview` for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/sentinelone.md)

---

### [SentinelOne](connectors/sentineloneccp.md)

**Publisher:** Microsoft

**Solution:** [SentinelOne](solutions/sentinelone.md)

**Tables (5):** `SentinelOneActivities_CL`, `SentinelOneAgents_CL`, `SentinelOneAlerts_CL`, `SentinelOneGroups_CL`, `SentinelOneThreats_CL`

The [SentinelOne](https://usea1-nessat.sentinelone.net/api-doc/overview) data connector allows ingesting logs from the SentinelOne API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SentinelOne API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

[→ View full connector details](connectors/sentineloneccp.md)

---

### [Seraphic Web Security](connectors/seraphicwebsecurity.md)

**Publisher:** Seraphic

**Solution:** [SeraphicSecurity](solutions/seraphicsecurity.md)

**Tables (1):** `SeraphicWebSecurity_CL`

The Seraphic Web Security data connector provides the capability to ingest [Seraphic Web Security](https://seraphicsecurity.com/) events and alerts into Microsoft Sentinel.

[→ View full connector details](connectors/seraphicwebsecurity.md)

---

### [Sevco Platform - Devices](connectors/sevcodevices.md)

**Publisher:** Sevco Security

**Solution:** [SevcoSecurity](solutions/sevcosecurity.md)

**Tables (1):** `Sevco_Devices_CL`

The Sevco Platform - Devices connector allows you to easily connect your Sevco Device Assets with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s assets and improves your security operation capabilities.

[For more information >​](https://docs.sev.co/docs/microsoft-sentinel-inventory)

[→ View full connector details](connectors/sevcodevices.md)

---

### [Silverfort Admin Console](connectors/silverfortama.md)

**Publisher:** Silverfort

**Solution:** [Silverfort](solutions/silverfort.md)

**Tables (1):** `CommonSecurityLog`

The [Silverfort](https://silverfort.com) ITDR Admin Console connector solution allows ingestion of Silverfort events and logging into Microsoft Sentinel.
 Silverfort provides syslog based events and logging using Common Event Format (CEF). By forwarding your Silverfort ITDR Admin Console CEF data into Microsoft Sentinel, you can take advantage of Sentinels's search & correlation, alerting, and threat intelligence enrichment on Silverfort data. 
 Please contact Silverfort or consult the Silverfort documentation for more information.

[→ View full connector details](connectors/silverfortama.md)

---

### [Slack](connectors/slackaudit.md)

**Publisher:** Slack

**Solution:** [SlackAudit](solutions/slackaudit.md)

**Tables (1):** `SlackAuditNativePoller_CL`

The [Slack](https://slack.com) data connector provides the capability to ingest [Slack Audit Records](https://api.slack.com/admins/audit-logs) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs#the_audit_event) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. This data connector uses Microsoft Sentinel native polling capability.

[→ View full connector details](connectors/slackaudit.md)

---

### [SlackAudit (via Codeless Connector Framework)](connectors/slackauditlogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [SlackAudit](solutions/slackaudit.md)

**Tables (1):** `SlackAuditV2_CL`

The SlackAudit data connector provides the capability to ingest [Slack Audit logs](https://api.slack.com/admins/audit-logs) into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs-call) for more information.

[→ View full connector details](connectors/slackauditlogsccpdefinition.md)

---

### [Snowflake (via Codeless Connector Framework)](connectors/snowflakelogsccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Snowflake](solutions/snowflake.md)

**Tables (10):** `SnowflakeLoad_CL`, `SnowflakeLogin_CL`, `SnowflakeMaterializedView_CL`, `SnowflakeQuery_CL`, `SnowflakeRoleGrant_CL`, `SnowflakeRoles_CL`, `SnowflakeTableStorageMetrics_CL`, `SnowflakeTables_CL`, `SnowflakeUserGrant_CL`, `SnowflakeUsers_CL`

The Snowflake data connector provides the capability to ingest Snowflake [Login History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history), [Query History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history), [User-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_users), [Role-Grant Logs](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles), [Load History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/load_history), [Materialized View Refresh History Logs](https://docs.snowflake.com/en/sql-reference/account-usage/materialized_view_refresh_history), [Roles Logs](https://docs.snowflake.com/en/sql-reference/account-usage/roles), [Tables Logs](https://docs.snowflake.com/en/sql-reference/account-usage/tables), [Table Storage Metrics Logs](https://docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics), [Users Logs](https://docs.snowflake.com/en/sql-reference/account-usage/users) into Microsoft Sentinel using the Snowflake SQL API. Refer to [Snowflake SQL API documentation](https://docs.snowflake.com/en/developer-guide/sql-api/reference) for more information.

[→ View full connector details](connectors/snowflakelogsccpdefinition.md)

---

### [Sonrai Data Connector](connectors/sonraidataconnector.md)

**Publisher:** Sonrai

**Solution:** [SonraiSecurity](solutions/sonraisecurity.md)

**Tables (1):** `Sonrai_Tickets_CL`

Use this data connector to integrate with Sonrai Security and get Sonrai tickets sent directly to Microsoft Sentinel.

[→ View full connector details](connectors/sonraidataconnector.md)

---

### [Sophos Cloud Optix](connectors/sophoscloudoptix.md)

**Publisher:** Sophos

**Solution:** [Sophos Cloud Optix](solutions/sophos-cloud-optix.md)

**Tables (1):** `SophosCloudOptix_CL`

The [Sophos Cloud Optix](https://www.sophos.com/products/cloud-optix.aspx) connector allows you to easily connect your Sophos Cloud Optix logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's cloud security and compliance posture and improves your cloud security operation capabilities.

[→ View full connector details](connectors/sophoscloudoptix.md)

---

### [Sophos Endpoint Protection](connectors/sophosep.md)

**Publisher:** Sophos

**Solution:** [Sophos Endpoint Protection](solutions/sophos-endpoint-protection.md)

**Tables (1):** `SophosEP_CL`

The [Sophos Endpoint Protection](https://www.sophos.com/en-us/products/endpoint-antivirus.aspx) data connector provides the capability to ingest [Sophos events](https://docs.sophos.com/central/Customer/help/en-us/central/Customer/common/concepts/Events.html) into Microsoft Sentinel. Refer to [Sophos Central Admin documentation](https://docs.sophos.com/central/Customer/help/en-us/central/Customer/concepts/Logs.html) for more information.

[→ View full connector details](connectors/sophosep.md)

---

### [Sophos Endpoint Protection (using REST API)](connectors/sophosendpointprotectionccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Sophos Endpoint Protection](solutions/sophos-endpoint-protection.md)

**Tables (2):** `SophosEPAlerts_CL`, `SophosEPEvents_CL`

The [Sophos Endpoint Protection](https://www.sophos.com/en-us/products/endpoint-antivirus.aspx) data connector provides the capability to ingest [Sophos events](https://developer.sophos.com/docs/siem-v1/1/routes/events/get) and [Sophos alerts](https://developer.sophos.com/docs/siem-v1/1/routes/alerts/get) into Microsoft Sentinel. Refer to [Sophos Central Admin documentation](https://docs.sophos.com/central/Customer/help/en-us/central/Customer/concepts/Logs.html) for more information.

[→ View full connector details](connectors/sophosendpointprotectionccpdefinition.md)

---

### [Squadra Technologies secRMM](connectors/squadratechnologiessecrmm.md)

**Publisher:** Squadra Technologies

**Solution:** [Squadra Technologies SecRmm](solutions/squadra-technologies-secrmm.md)

**Tables (1):** `secRMM_CL`

Use the Squadra Technologies secRMM Data Connector to push USB removable storage security event data into Microsoft Sentinel Log Analytics.

[→ View full connector details](connectors/squadratechnologiessecrmm.md)

---

### [StyxView Alerts (via Codeless Connector Platform)](connectors/styxviewendpointconnectordefinition.md)

**Publisher:** Styx Intelligence

**Solution:** [Styx Intelligence](solutions/styx-intelligence.md)

**Tables (1):** `StyxViewAlerts_CL`

The [StyxView Alerts](https://styxintel.com/) data connector enables seamless integration between the StyxView Alerts platform and Microsoft Sentinel. This connector ingests alert data from the StyxView Alerts API, allowing organizations to centralize and correlate actionable threat intelligence directly within their Microsoft Sentinel workspace.

[→ View full connector details](connectors/styxviewendpointconnectordefinition.md)

---

### [Syslog via AMA](connectors/syslogama.md)

**Publisher:** Microsoft

**Solution:** [Syslog](solutions/syslog.md)

**Tables (1):** `Syslog`

Syslog is an event logging protocol that is common to Linux. Applications will send messages that may be stored on the local machine or delivered to a Syslog collector. When the Agent for Linux is installed, it configures the local Syslog daemon to forward messages to the agent. The agent then sends the message to the workspace.

[Learn more >](https://aka.ms/sysLogInfo)

[→ View full connector details](connectors/syslogama.md)

---

### [Syslog via Legacy Agent](connectors/syslog.md)

**Publisher:** Microsoft

**Solution:** [Syslog](solutions/syslog.md)

**Tables (1):** `Syslog`

Syslog is an event logging protocol that is common to Linux. Applications will send messages that may be stored on the local machine or delivered to a Syslog collector. When the Agent for Linux is installed, it configures the local Syslog daemon to forward messages to the agent. The agent then sends the message to the workspace.

[Learn more >](https://aka.ms/sysLogInfo)

[→ View full connector details](connectors/syslog.md)

---

## T

### [Talon Insights](connectors/talonlogs.md)

**Publisher:** Talon Security

**Solution:** [Talon](solutions/talon.md)

**Tables (1):** `Talon_CL`

The Talon Security Logs connector allows you to easily connect your Talon events and audit logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.

[→ View full connector details](connectors/talonlogs.md)

---

### [Team Cymru Scout Data Connector](connectors/teamcymruscout.md)

**Publisher:** Team Cymru Scout

**Solution:** [Team Cymru Scout](solutions/team-cymru-scout.md)

**Tables (14):** `Cymru_Scout_Account_Usage_Data_CL`, `Cymru_Scout_Domain_Data_CL`, `Cymru_Scout_IP_Data_Communications_CL`, `Cymru_Scout_IP_Data_Details_CL`, `Cymru_Scout_IP_Data_Fingerprints_CL`, `Cymru_Scout_IP_Data_Foundation_CL`, `Cymru_Scout_IP_Data_OpenPorts_CL`, `Cymru_Scout_IP_Data_PDNS_CL`, `Cymru_Scout_IP_Data_Summary_Certs_CL`, `Cymru_Scout_IP_Data_Summary_Details_CL`, `Cymru_Scout_IP_Data_Summary_Fingerprints_CL`, `Cymru_Scout_IP_Data_Summary_OpenPorts_CL`, `Cymru_Scout_IP_Data_Summary_PDNS_CL`, `Cymru_Scout_IP_Data_x509_CL`

The [TeamCymruScout](https://scout.cymru.com/) Data Connector allows users to bring Team Cymru Scout IP, domain and account usage data in Microsoft Sentinel for enrichment.

[→ View full connector details](connectors/teamcymruscout.md)

---

### [Tenable Identity Exposure](connectors/tenableie.md)

**Publisher:** Tenable

**Solution:** [Tenable App](solutions/tenable-app.md)

**Tables (1):** `Tenable_IE_CL`

Tenable Identity Exposure connector allows Indicators of Exposure, Indicators of Attack and trailflow logs to be ingested into Microsoft Sentinel.The different work books and data parsers allow you to more easily manipulate logs and monitor your Active Directory environment.  The analytic templates allow you to automate responses regarding different events, exposures and attacks.

[→ View full connector details](connectors/tenableie.md)

---

### [Tenable Vulnerability Management](connectors/tenablevm.md)

**Publisher:** Tenable

**Solution:** [Tenable App](solutions/tenable-app.md)

**Tables (5):** `Tenable_VM_Asset_CL`, `Tenable_VM_Compliance_CL`, `Tenable_VM_Vuln_CL`, `Tenable_WAS_Asset_CL`, `Tenable_WAS_Vuln_CL`

The TVM data connector provides the ability to ingest Asset, Vulnerability, Compliance, WAS assets and WAS vulnerabilities data into Microsoft Sentinel using TVM REST APIs. Refer to [API documentation](https://developer.tenable.com/reference) for more information. The connector provides the ability to get data which helps to examine potential security risks, get insight into your computing assets, diagnose configuration problems and more

[→ View full connector details](connectors/tenablevm.md)

---

### [Tenable.ad](connectors/tenable.ad.md)

**Publisher:** Tenable

**Solution:** [TenableAD](solutions/tenablead.md)

**Tables (1):** `Tenable_ad_CL`

Tenable.ad connector allows to export Tenable.ad Indicators of Exposures, trailflow and Indicators of Attacks logs to Azure Sentinel in real time.
It provides a data parser to manipulate the logs more easily. The different workbooks ease your Active Directory monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

[→ View full connector details](connectors/tenable.ad.md)

---

### [Tenable.io Vulnerability Management](connectors/tenableioapi.md)

**Publisher:** Tenable

**Solution:** [TenableIO](solutions/tenableio.md)

**Tables (2):** `Tenable_IO_Assets_CL`, `Tenable_IO_Vuln_CL`

The [Tenable.io](https://www.tenable.com/products/tenable-io) data connector provides the capability to ingest Asset and Vulnerability data into Microsoft Sentinel through the REST API from the Tenable.io platform (Managed in the cloud). Refer to [API documentation](https://developer.tenable.com/reference) for more information. The connector provides the ability to get data which helps to examine potential security risks, get insight into your computing assets, diagnose configuration problems and more

[→ View full connector details](connectors/tenableioapi.md)

---

### [Tenant-based Microsoft Defender for Cloud](connectors/microsoftdefenderforcloudtenantbased.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Defender for Cloud](solutions/microsoft-defender-for-cloud.md)

**Tables (1):** `SecurityAlert`

Microsoft Defender for Cloud is a security management tool that allows you to detect and quickly respond to threats across Azure, hybrid, and multi-cloud workloads. This connector allows you to stream your MDC security alerts from Microsoft 365 Defender into Microsoft Sentinel, so you can can leverage the advantages of XDR correlations connecting the dots across your cloud resources, devices and identities and view the data in workbooks, queries and investigate and respond to incidents. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2269832&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/microsoftdefenderforcloudtenantbased.md)

---

### [TheHive Project - TheHive](connectors/thehiveprojectthehive.md)

**Publisher:** TheHive Project

**Solution:** [TheHive](solutions/thehive.md)

**Tables (1):** `TheHive_CL`

The [TheHive](http://thehive-project.org/) data connector provides the capability to ingest common TheHive events into Microsoft Sentinel through Webhooks. TheHive can notify external system of modification events (case creation, alert update, task assignment) in real time. When a change occurs in the TheHive, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://docs.thehive-project.org/thehive/legacy/thehive3/admin/webhooks/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/thehiveprojectthehive.md)

---

### [Theom](connectors/theom.md)

**Publisher:** Theom

**Solution:** [Theom](solutions/theom.md)

**Tables (1):** `TheomAlerts_CL`

Theom Data Connector enables organizations to connect their Theom environment to Microsoft Sentinel. This solution enables users to receive alerts on data security risks, create and enrich incidents, check statistics and trigger SOAR playbooks in Microsoft Sentinel

[→ View full connector details](connectors/theom.md)

---

### [Threat Intelligence Platforms](connectors/threatintelligence.md)

**Publisher:** Microsoft

**Solution:** [Threat Intelligence](solutions/threat-intelligence.md)

**Tables (4):** `CommonSecurityLog`, `ThreatIntelIndicators`, `ThreatIntelObjects`, `ThreatIntelligenceIndicator`

Microsoft Sentinel integrates with Microsoft Graph Security API data sources to enable monitoring, alerting, and hunting using your threat intelligence. Use this connector to send threat indicators to Microsoft Sentinel from your Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MindMeld, MISP, or other integrated applications. Threat indicators can include IP addresses, domains, URLs, and file hashes. For more information, see the [Microsoft Sentinel documentation >](https://go.microsoft.com/fwlink/p/?linkid=2223729&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/threatintelligence.md)

---

### [Threat Intelligence Upload API (Preview)](connectors/threatintelligenceuploadindicatorsapi.md)

**Publisher:** Microsoft

**Solution:** [Threat Intelligence](solutions/threat-intelligence.md)

**Tables (3):** `ThreatIntelIndicators`, `ThreatIntelObjects`, `ThreatIntelligenceIndicator`

Microsoft Sentinel offers a data plane API to bring in threat intelligence from your Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MineMeld, MISP, or other integrated applications. Threat indicators can include IP addresses, domains, URLs, file hashes and email addresses. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2269830&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/threatintelligenceuploadindicatorsapi.md)

---

### [Threat intelligence - TAXII](connectors/threatintelligencetaxii.md)

**Publisher:** Microsoft

**Solution:** [Threat Intelligence](solutions/threat-intelligence.md)

**Tables (3):** `ThreatIntelIndicators`, `ThreatIntelObjects`, `ThreatIntelligenceIndicator`

Microsoft Sentinel integrates with TAXII 2.0 and 2.1 data sources to enable monitoring, alerting, and hunting using your threat intelligence. Use this connector to send the supported STIX object types from TAXII servers to Microsoft Sentinel. Threat indicators can include IP addresses, domains, URLs, and file hashes. For more information, see the [Microsoft Sentinel documentation >](https://go.microsoft.com/fwlink/p/?linkid=2224105&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[→ View full connector details](connectors/threatintelligencetaxii.md)

---

### [Threat intelligence - TAXII Export (Preview)](connectors/threatintelligencetaxiiexport.md)

**Publisher:** Microsoft

**Solution:** [Threat Intelligence (NEW)](solutions/threat-intelligence-(new).md)

**Tables (1):** `ThreatIntelExportOperation`

Microsoft Sentinel integrates with TAXII 2.1 servers to enable exporting of your threat intelligence objects. Use this connector to send the supported STIX object types from Microsoft Sentinel to TAXII servers.

[→ View full connector details](connectors/threatintelligencetaxiiexport.md)

---

### [Trend Micro Cloud App Security](connectors/trendmicrocas.md)

**Publisher:** Trend Micro

**Solution:** [Trend Micro Cloud App Security](solutions/trend-micro-cloud-app-security.md)

**Tables (1):** `TrendMicroCAS_CL`

The [Trend Micro Cloud App Security](https://www.trendmicro.com/en_be/business/products/user-protection/sps/email-and-collaboration/cloud-app-security.html) data connector provides the capability to retrieve security event logs of the services that Cloud App Security protects and more events into Microsoft Sentinel through the Log Retrieval API. Refer to API [documentation](https://docs.trendmicro.com/en-us/enterprise/cloud-app-security-integration-api-online-help/supported-cloud-app-/log-retrieval-api/get-security-logs.aspx) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/trendmicrocas.md)

---

### [Trend Vision One](connectors/trendmicroxdr.md)

**Publisher:** Trend Micro

**Solution:** [Trend Micro Vision One](solutions/trend-micro-vision-one.md)

**Tables (4):** `TrendMicro_XDR_OAT_CL`, `TrendMicro_XDR_RCA_Result_CL`, `TrendMicro_XDR_RCA_Task_CL`, `TrendMicro_XDR_WORKBENCH_CL`

The [Trend Vision One](https://www.trendmicro.com/en_us/business/products/detection-response/xdr.html) connector allows you to easily connect your Workbench alert data with Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities. This gives you more insight into your organization's networks/systems and improves your security operation capabilities.

The Trend Vision One connector is supported in Microsoft Sentinel in the following regions: Australia East, Australia Southeast, Brazil South, Canada Central, Canada East, Central India, Central US, East Asia, East US, East US 2, France Central, Japan East, Korea Central, North Central US, North Europe, Norway East, South Africa North, South Central US, Southeast Asia, Sweden Central, Switzerland North, UAE North, UK South, UK West, West Europe, West US, West US 2, West US 3.

[→ View full connector details](connectors/trendmicroxdr.md)

---

## V

### [VMRayThreatIntelligence](connectors/vmray.md)

**Publisher:** VMRay

**Solution:** [VMRay](solutions/vmray.md)

**Tables (1):** `ThreatIntelligenceIndicator`

VMRayThreatIntelligence connector automatically generates and feeds threat intelligence for all submissions to VMRay, improving threat detection and incident response in Sentinel. This seamless integration empowers teams to proactively address emerging threats.

[→ View full connector details](connectors/vmray.md)

---

### [VMware Carbon Black Cloud](connectors/vmwarecarbonblack.md)

**Publisher:** VMware

**Solution:** [VMware Carbon Black Cloud](solutions/vmware-carbon-black-cloud.md)

**Tables (3):** `CarbonBlackAuditLogs_CL`, `CarbonBlackEvents_CL`, `CarbonBlackNotifications_CL`

The [VMware Carbon Black Cloud](https://www.vmware.com/products/carbon-black-cloud.html) connector provides the capability to ingest Carbon Black data into Microsoft Sentinel. The connector provides visibility into Audit, Notification and Event logs in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

[→ View full connector details](connectors/vmwarecarbonblack.md)

---

### [VMware Carbon Black Cloud via AWS S3](connectors/carbonblackawss3.md)

**Publisher:** Microsoft

**Solution:** [VMware Carbon Black Cloud](solutions/vmware-carbon-black-cloud.md)

**Tables (7):** `ASimAuthenticationEventLogs`, `ASimFileEventLogs`, `ASimNetworkSessionLogs`, `ASimProcessEventLogs`, `ASimRegistryEventLogs`, `CarbonBlack_Alerts_CL`, `CarbonBlack_Watchlist_CL`

The [VMware Carbon Black Cloud](https://www.vmware.com/products/carbon-black-cloud.html) via AWS S3 data connector provides the capability to ingest watchlist, alerts, auth and endpoints events via AWS S3 and stream them to ASIM normalized tables. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/carbonblackawss3.md)

---

### [VMware SD-WAN and SASE Connector](connectors/vmwaresdwan.md)

**Publisher:** VMware by Broadcom

**Solution:** [VMware SD-WAN and SASE](solutions/vmware-sd-wan-and-sase.md)

**Tables (4):** `VMware_CWS_DLPLogs_CL`, `VMware_CWS_Health_CL`, `VMware_CWS_Weblogs_CL`, `VMware_VECO_EventLogs_CL`

The [VMware SD-WAN & SASE](https://sase.vmware.com) data connector offers the capability to ingest VMware SD-WAN and CWS events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.vmware.com/apis/vmware-sase-platform/) for more information. The connector provides ability to get events which helps to examine potential network security issues, identify misconfigured network devices and monitor SD-WAN and SASE usage. If you have your own custom connector, make sure that the connector is deployed under an isolated Log Analytics Workspace first. In case of issues, questions or feature requests, please contact us via email on sase-siem-integration@vmware.com.

[→ View full connector details](connectors/vmwaresdwan.md)

---

### [Varonis Purview Push Connector](connectors/varonispurviewpush.md)

**Publisher:** Varonis

**Solution:** [Varonis Purview](solutions/varonis-purview.md)

**Tables (1):** `varonisresources_CL`

The [Varonis Purview](https://www.varonis.com/) connector provides the capability to sync resources from Varonis to Microsoft Purview.

[→ View full connector details](connectors/varonispurviewpush.md)

---

### [Varonis SaaS](connectors/varonissaas.md)

**Publisher:** Varonis

**Solution:** [VaronisSaaS](solutions/varonissaas.md)

**Tables (1):** `VaronisAlerts_CL`

Varonis SaaS provides the capability to ingest [Varonis Alerts](https://www.varonis.com/products/datalert) into Microsoft Sentinel.

Varonis prioritizes deep data visibility, classification capabilities, and automated remediation for data access. Varonis builds a single prioritized view of risk for your data, so you can proactively and systematically eliminate risk from insider threats and cyberattacks.

[→ View full connector details](connectors/varonissaas.md)

---

### [Vectra XDR](connectors/vectraxdr.md)

**Publisher:** Vectra

**Solution:** [Vectra XDR](solutions/vectra-xdr.md)

**Tables (6):** `Audits_Data_CL`, `Detections_Data_CL`, `Entities_Data_CL`, `Entity_Scoring_Data_CL`, `Health_Data_CL`, `Lockdown_Data_CL`

The [Vectra XDR](https://www.vectra.ai/) connector gives the capability to ingest Vectra Detections, Audits, Entity Scoring, Lockdown, Health and Entities data into Microsoft Sentinel through the Vectra REST API. Refer to the API documentation: `https://support.vectra.ai/s/article/KB-VS-1666` for more information.

[→ View full connector details](connectors/vectraxdr.md)

---

### [Veeam Data Connector (using Azure Functions)](connectors/veeamcustomtablesdataconnector.md)

**Publisher:** Veeam

**Solution:** [Veeam](solutions/veeam.md)

**Tables (6):** `VeeamAuthorizationEvents_CL`, `VeeamCovewareFindings_CL`, `VeeamMalwareEvents_CL`, `VeeamOneTriggeredAlarms_CL`, `VeeamSecurityComplianceAnalyzer_CL`, `VeeamSessions_CL`

Veeam Data Connector allows you to ingest Veeam telemetry data from multiple custom tables into Microsoft Sentinel.

The connector supports integration with Veeam Backup & Replication, Veeam ONE and Coveware platforms to provide comprehensive monitoring and security analytics. The data is collected through Azure Functions and stored in custom Log Analytics tables with dedicated Data Collection Rules (DCR) and Data Collection Endpoints (DCE).

**Custom Tables Included:**
- **VeeamMalwareEvents_CL**: Malware detection events from Veeam Backup & Replication
- **VeeamSecurityComplianceAnalyzer_CL**: Security & Compliance Analyzer results collected from Veeam backup infrastructure components
- **VeeamAuthorizationEvents_CL**: Authorization and authentication events
- **VeeamOneTriggeredAlarms_CL**: Triggered alarms from Veeam ONE servers
- **VeeamCovewareFindings_CL**: Security findings from Coveware solution
- **VeeamSessions_CL**: Veeam sessions

[→ View full connector details](connectors/veeamcustomtablesdataconnector.md)

---

### [VirtualMetric DataStream for Microsoft Sentinel](connectors/virtualmetricmssentinelconnector.md)

**Publisher:** VirtualMetric

**Solution:** [VirtualMetric DataStream](solutions/virtualmetric-datastream.md)

**Tables (1):** `CommonSecurityLog`

VirtualMetric DataStream connector deploys Data Collection Rules to ingest security telemetry into Microsoft Sentinel.

[→ View full connector details](connectors/virtualmetricmssentinelconnector.md)

---

### [VirtualMetric DataStream for Microsoft Sentinel data lake](connectors/virtualmetricmssentineldatalakeconnector.md)

**Publisher:** VirtualMetric

**Solution:** [VirtualMetric DataStream](solutions/virtualmetric-datastream.md)

**Tables (1):** `CommonSecurityLog`

VirtualMetric DataStream connector deploys Data Collection Rules to ingest security telemetry into Microsoft Sentinel data lake.

[→ View full connector details](connectors/virtualmetricmssentineldatalakeconnector.md)

---

### [VirtualMetric Director Proxy](connectors/virtualmetricdirectorproxy.md)

**Publisher:** VirtualMetric

**Solution:** [VirtualMetric DataStream](solutions/virtualmetric-datastream.md)

**Tables (1):** `CommonSecurityLog`

VirtualMetric Director Proxy deploys an Azure Function App to securely bridge VirtualMetric DataStream with Azure services including Microsoft Sentinel, Azure Data Explorer, and Azure Storage.

[→ View full connector details](connectors/virtualmetricdirectorproxy.md)

---

## W

### [WithSecure Elements API (Azure Function)](connectors/withsecureelementsviafunction.md)

**Publisher:** WithSecure

**Solution:** [WithSecureElementsViaFunction](solutions/withsecureelementsviafunction.md)

**Tables (1):** `WsSecurityEvents_CL`

WithSecure Elements is the unified cloud-based cyber security platform designed to reduce risk, complexity, and inefficiency.

Elevate your security from your endpoints to your cloud applications. Arm yourself against every type of cyber threat, from targeted attacks to zero-day ransomware.

WithSecure Elements combines powerful predictive, preventive, and responsive security capabilities - all managed and monitored through a single security center. Our modular structure and flexible pricing models give you the freedom to evolve. With our expertise and insight, you'll always be empowered - and you'll never be alone.

With Microsoft Sentinel integration, you can correlate [security events](https://connect.withsecure.com/api-reference/security-events#overview) data from the WithSecure Elements solution with data from other sources, enabling a rich overview of your entire environment and faster reaction to threats.

With this solution Azure Function is deployed to your tenant, polling periodically for the WithSecure Elements security events.

For more information visit our website at: [https://www.withsecure.com](https://www.withsecure.com).

[→ View full connector details](connectors/withsecureelementsviafunction.md)

---

### [Wiz](connectors/wiz.md)

**Publisher:** Wiz

**Solution:** [Wiz](solutions/wiz.md)

**Tables (6):** `WizAuditLogsV2_CL`, `WizAuditLogs_CL`, `WizIssuesV2_CL`, `WizIssues_CL`, `WizVulnerabilitiesV2_CL`, `WizVulnerabilities_CL`

The Wiz connector allows you to easily send Wiz Issues, Vulnerability Findings, and Audit logs to Microsoft Sentinel.

[→ View full connector details](connectors/wiz.md)

---

### [Workday User Activity](connectors/workdayccpdefinition.md)

**Publisher:** Microsoft

**Solution:** [Workday](solutions/workday.md)

**Tables (1):** `ASimAuditEventLogs`

The [Workday](https://www.workday.com/) User Activity data connector provides the capability to ingest User Activity Logs from [Workday API](https://community.workday.com/sites/default/files/file-hosting/restapi/index.html#privacy/v1/get-/activityLogging) into Microsoft Sentinel.

[→ View full connector details](connectors/workdayccpdefinition.md)

---

### [Workplace from Facebook](connectors/workplacefacebook.md)

**Publisher:** Facebook

**Solution:** [Workplace from Facebook](solutions/workplace-from-facebook.md)

**Tables (1):** `Workplace_Facebook_CL`

The [Workplace](https://www.workplace.com/) data connector provides the capability to ingest common Workplace events into Microsoft Sentinel through Webhooks. Webhooks enable custom integration apps to subscribe to events in Workplace and receive updates in real time. When a change occurs in Workplace, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://developers.facebook.com/docs/workplace/reference/webhooks) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/workplacefacebook.md)

---

## Z

### [Zero Networks Segment Audit](connectors/zeronetworkssegmentauditnativepoller.md)

**Publisher:** Zero Networks

**Solution:** [ZeroNetworks](solutions/zeronetworks.md)

**Tables (1):** `ZNSegmentAuditNativePoller_CL`

The [Zero Networks Segment](https://zeronetworks.com/) Audit data connector provides the capability to ingest Zero Networks Audit events into Microsoft Sentinel through the REST API. This data connector uses Microsoft Sentinel native polling capability.

[→ View full connector details](connectors/zeronetworkssegmentauditnativepoller.md)

---

### [ZeroFox CTI](connectors/zerofoxctidataconnector.md)

**Publisher:** ZeroFox

**Solution:** [ZeroFox](solutions/zerofox.md)

**Tables (20):** `ZeroFox_CTI_C2_CL`, `ZeroFox_CTI_advanced_dark_web_CL`, `ZeroFox_CTI_botnet_CL`, `ZeroFox_CTI_breaches_CL`, `ZeroFox_CTI_compromised_credentials_CL`, `ZeroFox_CTI_credit_cards_CL`, `ZeroFox_CTI_dark_web_CL`, `ZeroFox_CTI_discord_CL`, `ZeroFox_CTI_disruption_CL`, `ZeroFox_CTI_email_addresses_CL`, `ZeroFox_CTI_exploits_CL`, `ZeroFox_CTI_irc_CL`, `ZeroFox_CTI_malware_CL`, `ZeroFox_CTI_national_ids_CL`, `ZeroFox_CTI_phishing_CL`, `ZeroFox_CTI_phone_numbers_CL`, `ZeroFox_CTI_ransomware_CL`, `ZeroFox_CTI_telegram_CL`, `ZeroFox_CTI_threat_actors_CL`, `ZeroFox_CTI_vulnerabilities_CL`

The ZeroFox CTI data connectors provide the capability to ingest the different [ZeroFox](https://www.zerofox.com/threat-intelligence/) cyber threat intelligence alerts into Microsoft Sentinel.

[→ View full connector details](connectors/zerofoxctidataconnector.md)

---

### [ZeroFox Enterprise - Alerts (Polling CCF)](connectors/zerofoxalertsdefinition.md)

**Publisher:** ZeroFox Enterprise

**Solution:** [ZeroFox](solutions/zerofox.md)

**Tables (1):** `ZeroFoxAlertPoller_CL`

Collects alerts from ZeroFox API.

[→ View full connector details](connectors/zerofoxalertsdefinition.md)

---

### [Zimperium Mobile Threat Defense](connectors/zimperiummtdalerts.md)

**Publisher:** Zimperium

**Solution:** [Zimperium Mobile Threat Defense](solutions/zimperium-mobile-threat-defense.md)

**Tables (2):** `ZimperiumMitigationLog_CL`, `ZimperiumThreatLog_CL`

Zimperium Mobile Threat Defense connector gives you the ability to connect the Zimperium threat log with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's mobile threat landscape and enhances your security operation capabilities.

[→ View full connector details](connectors/zimperiummtdalerts.md)

---

### [Zoom Reports](connectors/zoom.md)

**Publisher:** Zoom

**Solution:** [ZoomReports](solutions/zoomreports.md)

**Tables (1):** `Zoom_CL`

The [Zoom](https://zoom.us/) Reports data connector provides the capability to ingest [Zoom Reports](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#tag/Reports) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developers.zoom.us/docs/api/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[→ View full connector details](connectors/zoom.md)

---

## Deprecated Connectors

The following **140 connector(s)** are deprecated:

### [[DEPRECATED] Cisco Secure Endpoint (AMP)](connectors/ciscosecureendpoint.md)

**Publisher:** Cisco

**Solution:** [Cisco Secure Endpoint](solutions/cisco-secure-endpoint.md)

**Tables (1):** `CiscoSecureEndpoint_CL`

The Cisco Secure Endpoint (formerly AMP for Endpoints) data connector provides the capability to ingest Cisco Secure Endpoint [audit logs](https://api-docs.amp.cisco.com/api_resources/AuditLog?api_host=api.amp.cisco.com&api_version=v1) and [events](https://api-docs.amp.cisco.com/api_actions/details?api_action=GET+%2Fv1%2Fevents&api_host=api.amp.cisco.com&api_resource=Event&api_version=v1) into Microsoft Sentinel.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/ciscosecureendpoint.md)

---

### [[DEPRECATED] Cloudflare](connectors/cloudflaredataconnector.md)

**Publisher:** Cloudflare

**Solution:** [Cloudflare](solutions/cloudflare.md)

**Tables (1):** `Cloudflare_CL`

The Cloudflare data connector provides the capability to ingest [Cloudflare logs](https://developers.cloudflare.com/logs/) into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare  documentation](https://developers.cloudflare.com/logs/logpush) for more information.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/cloudflaredataconnector.md)

---

### [[DEPRECATED] Google ApigeeX](connectors/apigeexdataconnector.md)

**Publisher:** Google

**Solution:** [Google Apigee](solutions/google-apigee.md)

**Tables (1):** `ApigeeX_CL`

The [Google ApigeeX](https://cloud.google.com/apigee/docs) data connector provides the capability to ingest ApigeeX audit logs into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/reference/v2/rest) for more information.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/apigeexdataconnector.md)

---

### [[DEPRECATED] Google Cloud Platform Cloud Monitoring](connectors/gcpmonitordataconnector.md)

**Publisher:** Google

**Solution:** [Google Cloud Platform Cloud Monitoring](solutions/google-cloud-platform-cloud-monitoring.md)

**Tables (1):** `GCP_MONITORING_CL`

The Google Cloud Platform Cloud Monitoring data connector provides the capability to ingest [GCP Monitoring metrics](https://cloud.google.com/monitoring/api/metrics_gcp) into Microsoft Sentinel using the GCP Monitoring API. Refer to [GCP Monitoring API documentation](https://cloud.google.com/monitoring/api/v3) for more information.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/gcpmonitordataconnector.md)

---

### [[DEPRECATED] Google Cloud Platform DNS](connectors/gcpdnsdataconnector.md)

**Publisher:** Google

**Solution:** [GoogleCloudPlatformDNS](solutions/googlecloudplatformdns.md)

**Tables (1):** `GCP_DNS_CL`

The Google Cloud Platform DNS data connector provides the capability to ingest [Cloud DNS query logs](https://cloud.google.com/dns/docs/monitoring#using_logging) and [Cloud DNS audit logs](https://cloud.google.com/dns/docs/audit-logging) into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/api) for more information.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/gcpdnsdataconnector.md)

---

### [[DEPRECATED] Google Cloud Platform IAM](connectors/gcpiamdataconnector.md)

**Publisher:** Google

**Solution:** [GoogleCloudPlatformIAM](solutions/googlecloudplatformiam.md)

**Tables (1):** `GCP_IAM_CL`

The Google Cloud Platform Identity and Access Management (IAM) data connector provides the capability to ingest [GCP IAM logs](https://cloud.google.com/iam/docs/audit-logging) into Microsoft Sentinel using the GCP Logging API. Refer to [GCP Logging API documentation](https://cloud.google.com/logging/docs/api) for more information.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/gcpiamdataconnector.md)

---

### [[DEPRECATED] Google Workspace (G Suite)](connectors/googleworkspacereportsapi.md)

**Publisher:** Google

**Solution:** [GoogleWorkspaceReports](solutions/googleworkspacereports.md)

**Tables (22):** `GWorkspace_ReportsAPI_access_transparency_CL`, `GWorkspace_ReportsAPI_admin_CL`, `GWorkspace_ReportsAPI_calendar_CL`, `GWorkspace_ReportsAPI_chat_CL`, `GWorkspace_ReportsAPI_chrome_CL`, `GWorkspace_ReportsAPI_context_aware_access_CL`, `GWorkspace_ReportsAPI_data_studio_CL`, `GWorkspace_ReportsAPI_drive_CL`, `GWorkspace_ReportsAPI_gcp_CL`, `GWorkspace_ReportsAPI_gplus_CL`, `GWorkspace_ReportsAPI_groups_CL`, `GWorkspace_ReportsAPI_groups_enterprise_CL`, `GWorkspace_ReportsAPI_jamboard_CL`, `GWorkspace_ReportsAPI_keep_CL`, `GWorkspace_ReportsAPI_login_CL`, `GWorkspace_ReportsAPI_meet_CL`, `GWorkspace_ReportsAPI_mobile_CL`, `GWorkspace_ReportsAPI_rules_CL`, `GWorkspace_ReportsAPI_saml_CL`, `GWorkspace_ReportsAPI_token_CL`, `GWorkspace_ReportsAPI_user_accounts_CL`, `GoogleWorkspaceReports_CL`

The [Google Workspace](https://workspace.google.com/) data connector provides the capability to ingest Google Workspace Activity events into Microsoft Sentinel through the REST API. The connector provides ability to get [events](https://developers.google.com/admin-sdk/reports/v1/reference/activities) which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems, track who signs in and when, analyze administrator activity, understand how users create and share content, and more review events in your org.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/googleworkspacereportsapi.md)

---

### [[DEPRECATED] Lookout](connectors/lookoutapi.md)

**Publisher:** Lookout

**Solution:** [Lookout](solutions/lookout.md)

**Tables (1):** `Lookout_CL`

The [Lookout](https://lookout.com) data connector provides the capability to ingest [Lookout](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide#commoneventfields) events into Microsoft Sentinel through the Mobile Risk API. Refer to [API documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) for more information. The [Lookout](https://lookout.com) data connector provides ability to get events which helps to examine potential security risks and more.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/lookoutapi.md)

---

### [[DEPRECATED] OneLogin IAM Platform](connectors/onelogin.md)

**Publisher:** OneLogin

**Solution:** [OneLoginIAM](solutions/oneloginiam.md)

**Tables (3):** `OneLoginEventsV2_CL`, `OneLoginUsersV2_CL`, `OneLogin_CL`

The [OneLogin](https://www.onelogin.com/) data connector provides the capability to ingest common OneLogin IAM Platform events into Microsoft Sentinel through Webhooks. The OneLogin Event Webhook API which is also known as the Event Broadcaster will send batches of events in near real-time to an endpoint that you specify. When a change occurs in the OneLogin, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://developers.onelogin.com/api-docs/1/events/webhooks) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/onelogin.md)

---

### [[DEPRECATED] Oracle Cloud Infrastructure](connectors/oraclecloudinfrastructurelogsconnector.md)

**Publisher:** Oracle

**Solution:** [Oracle Cloud Infrastructure](solutions/oracle-cloud-infrastructure.md)

**Tables (1):** `OCI_Logs_CL`

The Oracle Cloud Infrastructure (OCI) data connector provides the capability to ingest OCI Logs from [OCI Stream](https://docs.oracle.com/iaas/Content/Streaming/Concepts/streamingoverview.htm) into Microsoft Sentinel using the [OCI Streaming REST API](https://docs.oracle.com/iaas/api/#/streaming/streaming/20180418).

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/oraclecloudinfrastructurelogsconnector.md)

---

### [[DEPRECATED] Palo Alto Prisma Cloud CSPM](connectors/paloaltoprismacloud.md)

**Publisher:** Palo Alto

**Solution:** [PaloAltoPrismaCloud](solutions/paloaltoprismacloud.md)

**Tables (2):** `PaloAltoPrismaCloudAlert_CL`, `PaloAltoPrismaCloudAudit_CL`

The Palo Alto Prisma Cloud CSPM data connector provides the capability to ingest [Prisma Cloud CSPM alerts](https://prisma.pan.dev/api/cloud/cspm/alerts#operation/get-alerts) and [audit logs](https://prisma.pan.dev/api/cloud/cspm/audit-logs#operation/rl-audit-logs) into Microsoft sentinel using the Prisma Cloud CSPM API. Refer to [Prisma Cloud CSPM API documentation](https://prisma.pan.dev/api/cloud/cspm) for more information.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/paloaltoprismacloud.md)

---

### [[DEPRECATED] Qualys Vulnerability Management](connectors/qualysvulnerabilitymanagement.md)

**Publisher:** Qualys

**Solution:** [QualysVM](solutions/qualysvm.md)

**Tables (2):** `QualysHostDetectionV2_CL`, `QualysHostDetection_CL`

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) data connector provides the capability to ingest vulnerability host detection data into Microsoft Sentinel through the Qualys API. The connector provides visibility into host detection data from vulerability scans. This connector provides Microsoft Sentinel the capability to view dashboards, create custom alerts, and improve investigation 

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/qualysvulnerabilitymanagement.md)

---

### [[DEPRECATED] Salesforce Service Cloud](connectors/salesforceservicecloud.md)

**Publisher:** Salesforce

**Solution:** [Salesforce Service Cloud](solutions/salesforce-service-cloud.md)

**Tables (2):** `SalesforceServiceCloudV2_CL`, `SalesforceServiceCloud_CL`

The Salesforce Service Cloud data connector provides the capability to ingest information about your Salesforce operational events into Microsoft Sentinel through the REST API. The connector provides ability to review events in your org on an accelerated basis, get [event log files](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/event_log_file_hourly_overview.htm) in hourly increments for recent activity.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/salesforceservicecloud.md)

---

### [[DEPRECATED] Slack Audit](connectors/slackauditapi.md)

**Publisher:** Slack

**Solution:** [SlackAudit](solutions/slackaudit.md)

**Tables (1):** `SlackAudit_CL`

The [Slack](https://slack.com) Audit data connector provides the capability to ingest [Slack Audit Records](https://api.slack.com/admins/audit-logs) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs#the_audit_event) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/slackauditapi.md)

---

### [[DEPRECATED] Snowflake](connectors/snowflakedataconnector.md)

**Publisher:** Snowflake

**Solution:** [Snowflake](solutions/snowflake.md)

**Tables (1):** `Snowflake_CL`

The Snowflake data connector provides the capability to ingest Snowflake [login logs](https://docs.snowflake.com/en/sql-reference/account-usage/login_history.html) and [query logs](https://docs.snowflake.com/en/sql-reference/account-usage/query_history.html) into Microsoft Sentinel using the Snowflake Python Connector. Refer to [Snowflake  documentation](https://docs.snowflake.com/en/user-guide/python-connector.html) for more information.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/snowflakedataconnector.md)

---

### [[Deprecated] AI Analyst Darktrace via AMA](connectors/darktraceama.md)

**Publisher:** Darktrace

**Solution:** [AI Analyst Darktrace](solutions/ai-analyst-darktrace.md)

**Tables (1):** `CommonSecurityLog`

The Darktrace connector lets users connect Darktrace Model Breaches in real-time with Microsoft Sentinel, allowing creation of custom Dashboards, Workbooks, Notebooks and Custom Alerts to improve investigation.  Microsoft Sentinel's enhanced visibility into Darktrace logs enables monitoring and mitigation of security threats.

[→ View full connector details](connectors/darktraceama.md)

---

### [[Deprecated] AI Analyst Darktrace via Legacy Agent](connectors/darktrace.md)

**Publisher:** Darktrace

**Solution:** [AI Analyst Darktrace](solutions/ai-analyst-darktrace.md)

**Tables (1):** `CommonSecurityLog`

The Darktrace connector lets users connect Darktrace Model Breaches in real-time with Microsoft Sentinel, allowing creation of custom Dashboards, Workbooks, Notebooks and Custom Alerts to improve investigation.  Microsoft Sentinel's enhanced visibility into Darktrace logs enables monitoring and mitigation of security threats.

[→ View full connector details](connectors/darktrace.md)

---

### [[Deprecated] Akamai Security Events via AMA](connectors/akamaisecurityeventsama.md)

**Publisher:** Akamai

**Solution:** [Akamai Security Events](solutions/akamai-security-events.md)

**Tables (1):** `CommonSecurityLog`

Akamai Solution for Microsoft Sentinel provides the capability to ingest [Akamai Security Events](https://www.akamai.com/us/en/products/security/) into Microsoft Sentinel. Refer to [Akamai SIEM Integration documentation](https://developer.akamai.com/tools/integrations/siem) for more information.

[→ View full connector details](connectors/akamaisecurityeventsama.md)

---

### [[Deprecated] Akamai Security Events via Legacy Agent](connectors/akamaisecurityevents.md)

**Publisher:** Akamai

**Solution:** [Akamai Security Events](solutions/akamai-security-events.md)

**Tables (1):** `CommonSecurityLog`

Akamai Solution for Microsoft Sentinel provides the capability to ingest [Akamai Security Events](https://www.akamai.com/us/en/products/security/) into Microsoft Sentinel. Refer to [Akamai SIEM Integration documentation](https://developer.akamai.com/tools/integrations/siem) for more information.

[→ View full connector details](connectors/akamaisecurityevents.md)

---

### [[Deprecated] Apache HTTP Server](connectors/apachehttpserver.md)

**Publisher:** Apache

**Solution:** [ApacheHTTPServer](solutions/apachehttpserver.md)

**Tables (1):** `ApacheHTTPServer_CL`

The Apache HTTP Server data connector provides the capability to ingest [Apache HTTP Server](http://httpd.apache.org/) events into Microsoft Sentinel. Refer to [Apache Logs documentation](https://httpd.apache.org/docs/2.4/logs.html) for more information.

[→ View full connector details](connectors/apachehttpserver.md)

---

### [[Deprecated] Apache Tomcat](connectors/apachetomcat.md)

**Publisher:** Apache

**Solution:** [Tomcat](solutions/tomcat.md)

**Tables (1):** `Tomcat_CL`

The Apache Tomcat solution provides the capability to ingest [Apache Tomcat](http://tomcat.apache.org/) events into Microsoft Sentinel. Refer to [Apache Tomcat documentation](http://tomcat.apache.org/tomcat-10.0-doc/logging.html) for more information.

[→ View full connector details](connectors/apachetomcat.md)

---

### [[Deprecated] Aruba ClearPass via AMA](connectors/arubaclearpassama.md)

**Publisher:** Aruba Networks

**Solution:** [Aruba ClearPass](solutions/aruba-clearpass.md)

**Tables (1):** `CommonSecurityLog`

The [Aruba ClearPass](https://www.arubanetworks.com/products/security/network-access-control/secure-access/) connector allows you to easily connect your Aruba ClearPass with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities.

[→ View full connector details](connectors/arubaclearpassama.md)

---

### [[Deprecated] Aruba ClearPass via Legacy Agent](connectors/arubaclearpass.md)

**Publisher:** Aruba Networks

**Solution:** [Aruba ClearPass](solutions/aruba-clearpass.md)

**Tables (1):** `CommonSecurityLog`

The [Aruba ClearPass](https://www.arubanetworks.com/products/security/network-access-control/secure-access/) connector allows you to easily connect your Aruba ClearPass with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities.

[→ View full connector details](connectors/arubaclearpass.md)

---

### [[Deprecated] Atlassian Confluence Audit](connectors/confluenceauditapi.md)

**Publisher:** Atlassian

**Solution:** [AtlassianConfluenceAudit](solutions/atlassianconfluenceaudit.md)

**Tables (1):** `Confluence_Audit_CL`

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/confluenceauditapi.md)

---

### [[Deprecated] Awake Security via Legacy Agent](connectors/aristaawakesecurity.md)

**Publisher:** Arista Networks

**Solution:** [AristaAwakeSecurity](solutions/aristaawakesecurity.md)

**Tables (1):** `CommonSecurityLog`

The Awake Security CEF connector allows users to send detection model matches from the Awake Security Platform to Microsoft Sentinel. Remediate threats quickly with the power of network detection and response and speed up investigations with deep visibility especially into unmanaged entities including users, devices and applications on your network. The connector also enables the creation of network security-focused custom alerts, incidents, workbooks and notebooks that align with your existing security operations workflows. 

[→ View full connector details](connectors/aristaawakesecurity.md)

---

### [[Deprecated] Barracuda CloudGen Firewall](connectors/barracudacloudfirewall.md)

**Publisher:** Barracuda

**Solution:** [Barracuda CloudGen Firewall](solutions/barracuda-cloudgen-firewall.md)

**Tables (1):** `Syslog`

The Barracuda CloudGen Firewall (CGFW) connector allows you to easily connect your Barracuda CGFW logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/barracudacloudfirewall.md)

---

### [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](connectors/barracuda.md)

**Publisher:** Barracuda

**Solution:** [Barracuda WAF](solutions/barracuda-waf.md)

**Tables (3):** `Barracuda_CL`, `CommonSecurityLog`, `barracuda_CL`

The Barracuda Web Application Firewall (WAF) connector allows you to easily connect your Barracuda logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities.

[For more information >​](https://aka.ms/CEF-Barracuda)

[→ View full connector details](connectors/barracuda.md)

---

### [[Deprecated] Broadcom Symantec DLP via AMA](connectors/broadcomsymantecdlpama.md)

**Publisher:** Broadcom

**Solution:** [Broadcom SymantecDLP](solutions/broadcom-symantecdlp.md)

**Tables (1):** `CommonSecurityLog`

The [Broadcom Symantec Data Loss Prevention (DLP)](https://www.broadcom.com/products/cyber-security/information-protection/data-loss-prevention) connector allows you to easily connect your Symantec DLP with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s information, where it travels, and improves your security operation capabilities.

[→ View full connector details](connectors/broadcomsymantecdlpama.md)

---

### [[Deprecated] Broadcom Symantec DLP via Legacy Agent](connectors/broadcomsymantecdlp.md)

**Publisher:** Broadcom

**Solution:** [Broadcom SymantecDLP](solutions/broadcom-symantecdlp.md)

**Tables (1):** `CommonSecurityLog`

The [Broadcom Symantec Data Loss Prevention (DLP)](https://www.broadcom.com/products/cyber-security/information-protection/data-loss-prevention) connector allows you to easily connect your Symantec DLP with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization’s information, where it travels, and improves your security operation capabilities.

[→ View full connector details](connectors/broadcomsymantecdlp.md)

---

### [[Deprecated] Cisco Application Centric Infrastructure](connectors/ciscoaci.md)

**Publisher:** Cisco

**Solution:** [Cisco ACI](solutions/cisco-aci.md)

**Tables (1):** `Syslog`

[Cisco Application Centric Infrastructure (ACI)](https://www.cisco.com/c/en/us/solutions/collateral/data-center-virtualization/application-centric-infrastructure/solution-overview-c22-741487.html) data connector provides the capability to ingest [Cisco ACI logs](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/all/syslog/guide/b_ACI_System_Messages_Guide/m-aci-system-messages-reference.html) into Microsoft Sentinel.

[→ View full connector details](connectors/ciscoaci.md)

---

### [[Deprecated] Cisco Firepower eStreamer via AMA](connectors/ciscofirepowerestreamerama.md)

**Publisher:** Cisco

**Solution:** [Cisco Firepower EStreamer](solutions/cisco-firepower-estreamer.md)

**Tables (1):** `CommonSecurityLog`

eStreamer is a Client Server API designed for the Cisco Firepower NGFW Solution. The eStreamer client requests detailed event data on behalf of the SIEM or logging solution in the Common Event Format (CEF).

[→ View full connector details](connectors/ciscofirepowerestreamerama.md)

---

### [[Deprecated] Cisco Firepower eStreamer via Legacy Agent](connectors/ciscofirepowerestreamer.md)

**Publisher:** Cisco

**Solution:** [Cisco Firepower EStreamer](solutions/cisco-firepower-estreamer.md)

**Tables (1):** `CommonSecurityLog`

eStreamer is a Client Server API designed for the Cisco Firepower NGFW Solution. The eStreamer client requests detailed event data on behalf of the SIEM or logging solution in the Common Event Format (CEF).

[→ View full connector details](connectors/ciscofirepowerestreamer.md)

---

### [[Deprecated] Cisco Identity Services Engine](connectors/ciscoise.md)

**Publisher:** Cisco

**Solution:** [Cisco ISE](solutions/cisco-ise.md)

**Tables (1):** `Syslog`

The Cisco Identity Services Engine (ISE) data connector provides the capability to ingest [Cisco ISE](https://www.cisco.com/c/en/us/products/security/identity-services-engine/index.html) events into Microsoft Sentinel. It helps you gain visibility into what is happening in your network, such as who is connected, which applications are installed and running, and much more. Refer to [Cisco ISE logging mechanism documentation](https://www.cisco.com/c/en/us/td/docs/security/ise/2-7/admin_guide/b_ise_27_admin_guide/b_ISE_admin_27_maintain_monitor.html#reference_BAFBA5FA046A45938810A5DF04C00591) for more information.

[→ View full connector details](connectors/ciscoise.md)

---

### [[Deprecated] Cisco Meraki](connectors/ciscomeraki.md)

**Publisher:** Cisco

**Solution:** [CiscoMeraki](solutions/ciscomeraki.md)

**Tables (1):** `meraki_CL`

The [Cisco Meraki](https://meraki.cisco.com/) connector allows you to easily connect your Cisco Meraki (MX/MR/MS) logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/ciscomeraki.md)

---

### [[Deprecated] Cisco Secure Cloud Analytics](connectors/stealthwatch.md)

**Publisher:** Cisco

**Solution:** [Cisco Secure Cloud Analytics](solutions/cisco-secure-cloud-analytics.md)

**Tables (1):** `Syslog`

The [Cisco Secure Cloud Analytics](https://www.cisco.com/c/en/us/products/security/stealthwatch/index.html) data connector provides the capability to ingest [Cisco Secure Cloud Analytics events](https://www.cisco.com/c/dam/en/us/td/docs/security/stealthwatch/management_console/securit_events_alarm_categories/7_4_2_Security_Events_and_Alarm_Categories_DV_2_1.pdf) into Microsoft Sentinel. Refer to [Cisco Secure Cloud Analytics documentation](https://www.cisco.com/c/dam/en/us/td/docs/security/stealthwatch/system_installation_configuration/7_5_0_System_Configuration_Guide_DV_1_3.pdf) for more information.

[→ View full connector details](connectors/stealthwatch.md)

---

### [[Deprecated] Cisco Secure Email Gateway via AMA](connectors/ciscosegama.md)

**Publisher:** Cisco

**Solution:** [CiscoSEG](solutions/ciscoseg.md)

**Tables (1):** `CommonSecurityLog`

The [Cisco Secure Email Gateway (SEG)](https://www.cisco.com/c/en/us/products/security/email-security/index.html) data connector provides the capability to ingest [Cisco SEG Consolidated Event Logs](https://www.cisco.com/c/en/us/td/docs/security/esa/esa14-0/user_guide/b_ESA_Admin_Guide_14-0/b_ESA_Admin_Guide_12_1_chapter_0100111.html#con_1061902) into Microsoft Sentinel.

[→ View full connector details](connectors/ciscosegama.md)

---

### [[Deprecated] Cisco Secure Email Gateway via Legacy Agent](connectors/ciscoseg.md)

**Publisher:** Cisco

**Solution:** [CiscoSEG](solutions/ciscoseg.md)

**Tables (1):** `CommonSecurityLog`

The [Cisco Secure Email Gateway (SEG)](https://www.cisco.com/c/en/us/products/security/email-security/index.html) data connector provides the capability to ingest [Cisco SEG Consolidated Event Logs](https://www.cisco.com/c/en/us/td/docs/security/esa/esa14-0/user_guide/b_ESA_Admin_Guide_14-0/b_ESA_Admin_Guide_12_1_chapter_0100111.html#con_1061902) into Microsoft Sentinel.

[→ View full connector details](connectors/ciscoseg.md)

---

### [[Deprecated] Cisco UCS](connectors/ciscoucs.md)

**Publisher:** Cisco

**Solution:** [Cisco UCS](solutions/cisco-ucs.md)

**Tables (1):** `Syslog`

The [Cisco Unified Computing System (UCS)](https://www.cisco.com/c/en/us/products/servers-unified-computing/index.html) connector allows you to easily connect your Cisco UCS logs with Microsoft Sentinel This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/ciscoucs.md)

---

### [[Deprecated] Cisco Web Security Appliance](connectors/ciscowsa.md)

**Publisher:** Cisco

**Solution:** [CiscoWSA](solutions/ciscowsa.md)

**Tables (1):** `Syslog`

[Cisco Web Security Appliance (WSA)](https://www.cisco.com/c/en/us/products/security/web-security-appliance/index.html) data connector provides the capability to ingest [Cisco WSA Access Logs](https://www.cisco.com/c/en/us/td/docs/security/wsa/wsa_14-0/User-Guide/b_WSA_UserGuide_14_0/b_WSA_UserGuide_11_7_chapter_010101.html) into Microsoft Sentinel.

[→ View full connector details](connectors/ciscowsa.md)

---

### [[Deprecated] Citrix ADC (former NetScaler)](connectors/citrixadc.md)

**Publisher:** Citrix

**Solution:** [Citrix ADC](solutions/citrix-adc.md)

**Tables (1):** `Syslog`

The [Citrix ADC (former NetScaler)](https://www.citrix.com/products/citrix-adc/) data connector provides the capability to ingest Citrix ADC logs into Microsoft Sentinel. If you want to ingest Citrix WAF logs into Microsoft Sentinel, refer this [documentation](https://learn.microsoft.com/azure/sentinel/data-connectors/citrix-waf-web-app-firewall)

[→ View full connector details](connectors/citrixadc.md)

---

### [[Deprecated] Citrix WAF (Web App Firewall) via AMA](connectors/citrixwafama.md)

**Publisher:** Citrix Systems Inc.

**Solution:** [Citrix Web App Firewall](solutions/citrix-web-app-firewall.md)

**Tables (1):** `CommonSecurityLog`

 Citrix WAF (Web App Firewall) is an industry leading enterprise-grade WAF solution. Citrix WAF mitigates threats against your public-facing assets, including websites, apps, and APIs. From layer 3 to layer 7, Citrix WAF includes protections such as IP reputation, bot mitigation, defense against the OWASP Top 10 application threats, built-in signatures to protect against application stack vulnerabilities, and more. 

Citrix WAF supports Common Event Format (CEF) which is an industry standard format on top of Syslog messages . By connecting Citrix WAF CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

[→ View full connector details](connectors/citrixwafama.md)

---

### [[Deprecated] Citrix WAF (Web App Firewall) via Legacy Agent](connectors/citrixwaf.md)

**Publisher:** Citrix Systems Inc.

**Solution:** [Citrix Web App Firewall](solutions/citrix-web-app-firewall.md)

**Tables (1):** `CommonSecurityLog`

 Citrix WAF (Web App Firewall) is an industry leading enterprise-grade WAF solution. Citrix WAF mitigates threats against your public-facing assets, including websites, apps, and APIs. From layer 3 to layer 7, Citrix WAF includes protections such as IP reputation, bot mitigation, defense against the OWASP Top 10 application threats, built-in signatures to protect against application stack vulnerabilities, and more. 

Citrix WAF supports Common Event Format (CEF) which is an industry standard format on top of Syslog messages . By connecting Citrix WAF CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

[→ View full connector details](connectors/citrixwaf.md)

---

### [[Deprecated] Claroty via AMA](connectors/clarotyama.md)

**Publisher:** Claroty

**Solution:** [Claroty](solutions/claroty.md)

**Tables (1):** `CommonSecurityLog`

The [Claroty](https://claroty.com/) data connector provides the capability to ingest [Continuous Threat Detection](https://claroty.com/resources/datasheets/continuous-threat-detection) and [Secure Remote Access](https://claroty.com/industrial-cybersecurity/sra) events into Microsoft Sentinel.

[→ View full connector details](connectors/clarotyama.md)

---

### [[Deprecated] Claroty via Legacy Agent](connectors/claroty.md)

**Publisher:** Claroty

**Solution:** [Claroty](solutions/claroty.md)

**Tables (1):** `CommonSecurityLog`

The [Claroty](https://claroty.com/) data connector provides the capability to ingest [Continuous Threat Detection](https://claroty.com/resources/datasheets/continuous-threat-detection) and [Secure Remote Access](https://claroty.com/industrial-cybersecurity/sra) events into Microsoft Sentinel.

[→ View full connector details](connectors/claroty.md)

---

### [[Deprecated] Contrast Protect via AMA](connectors/contrastprotectama.md)

**Publisher:** Contrast Security

**Solution:** [Contrast Protect](solutions/contrast-protect.md)

**Tables (1):** `CommonSecurityLog`

Contrast Protect mitigates security threats in production applications with runtime protection and observability.  Attack event results (blocked, probed, suspicious...) and other information can be sent to Microsoft Microsoft Sentinel to blend with security information from other systems.

[→ View full connector details](connectors/contrastprotectama.md)

---

### [[Deprecated] Contrast Protect via Legacy Agent](connectors/contrastprotect.md)

**Publisher:** Contrast Security

**Solution:** [Contrast Protect](solutions/contrast-protect.md)

**Tables (1):** `CommonSecurityLog`

Contrast Protect mitigates security threats in production applications with runtime protection and observability.  Attack event results (blocked, probed, suspicious...) and other information can be sent to Microsoft Microsoft Sentinel to blend with security information from other systems.

[→ View full connector details](connectors/contrastprotect.md)

---

### [[Deprecated] CrowdStrike Falcon Endpoint Protection via AMA](connectors/crowdstrikefalconendpointprotectionama.md)

**Publisher:** CrowdStrike

**Solution:** [CrowdStrike Falcon Endpoint Protection](solutions/crowdstrike-falcon-endpoint-protection.md)

**Tables (1):** `CommonSecurityLog`

The [CrowdStrike Falcon Endpoint Protection](https://www.crowdstrike.com/endpoint-security-products/) connector allows you to easily connect your CrowdStrike Falcon Event Stream with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization's endpoints and improves your security operation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE:</span> This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/crowdstrikefalconendpointprotectionama.md)

---

### [[Deprecated] CrowdStrike Falcon Endpoint Protection via Legacy Agent](connectors/crowdstrikefalconendpointprotection.md)

**Publisher:** CrowdStrike

**Solution:** [CrowdStrike Falcon Endpoint Protection](solutions/crowdstrike-falcon-endpoint-protection.md)

**Tables (1):** `CommonSecurityLog`

The [CrowdStrike Falcon Endpoint Protection](https://www.crowdstrike.com/endpoint-security-products/) connector allows you to easily connect your CrowdStrike Falcon Event Stream with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization's endpoints and improves your security operation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE:</span> This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/crowdstrikefalconendpointprotection.md)

---

### [[Deprecated] CyberArk Enterprise Password Vault (EPV) Events via Legacy Agent](connectors/cyberark.md)

**Publisher:** Cyber-Ark

**Solution:** [CyberArk Enterprise Password Vault (EPV) Events](solutions/cyberark-enterprise-password-vault-(epv)-events.md)

**Tables (1):** `CommonSecurityLog`

CyberArk Enterprise Password Vault generates an xml Syslog message for every action taken against the Vault.  The EPV will send the xml messages through the Microsoft Sentinel.xsl translator to be converted into CEF standard format and sent to a syslog staging server of your choice (syslog-ng, rsyslog). The Log Analytics agent installed on your syslog staging server will import the messages into Microsoft Log Analytics. Refer to the [CyberArk documentation](https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/PASIMP/DV-Integrating-with-SIEM-Applications.htm) for more guidance on SIEM integrations.

[→ View full connector details](connectors/cyberark.md)

---

### [[Deprecated] CyberArk Privilege Access Manager (PAM) Events via AMA](connectors/cyberarkama.md)

**Publisher:** Cyber-Ark

**Solution:** [CyberArk Enterprise Password Vault (EPV) Events](solutions/cyberark-enterprise-password-vault-(epv)-events.md)

**Tables (1):** `CommonSecurityLog`

CyberArk Privilege Access Manager generates an xml Syslog message for every action taken against the Vault.  The PAM will send the xml messages through the Microsoft Sentinel.xsl translator to be converted into CEF standard format and sent to a syslog staging server of your choice (syslog-ng, rsyslog). The Log Analytics agent installed on your syslog staging server will import the messages into Microsoft Log Analytics. Refer to the [CyberArk documentation](https://docs.cyberark.com/privilege-cloud-standard/Latest/en/Content/Privilege%20Cloud/privCloud-connect-siem.htm) for more guidance on SIEM integrations.

[→ View full connector details](connectors/cyberarkama.md)

---

### [[Deprecated] Delinea Secret Server via AMA](connectors/delineasecretserverama.md)

**Publisher:** Delinea, Inc

**Solution:** [Delinea Secret Server](solutions/delinea-secret-server.md)

**Tables (1):** `CommonSecurityLog`

Common Event Format (CEF) from Delinea Secret Server 

[→ View full connector details](connectors/delineasecretserverama.md)

---

### [[Deprecated] Delinea Secret Server via Legacy Agent](connectors/delineasecretserver-cef.md)

**Publisher:** Delinea, Inc

**Solution:** [Delinea Secret Server](solutions/delinea-secret-server.md)

**Tables (1):** `CommonSecurityLog`

Common Event Format (CEF) from Delinea Secret Server 

[→ View full connector details](connectors/delineasecretserver-cef.md)

---

### [[Deprecated] Digital Guardian Data Loss Prevention](connectors/digitalguardiandlp.md)

**Publisher:** Digital Guardian

**Solution:** [Digital Guardian Data Loss Prevention](solutions/digital-guardian-data-loss-prevention.md)

**Tables (1):** `Syslog`

[Digital Guardian Data Loss Prevention (DLP)](https://digitalguardian.com/platform-overview) data connector provides the capability to ingest Digital Guardian DLP logs into Microsoft Sentinel.

[→ View full connector details](connectors/digitalguardiandlp.md)

---

### [[Deprecated] ESET PROTECT](connectors/esetprotect.md)

**Publisher:** ESET

**Solution:** [ESETPROTECT](solutions/esetprotect.md)

**Tables (1):** `Syslog`

This connector gathers all events generated by ESET software through the central management solution ESET PROTECT (formerly ESET Security Management Center). This includes Anti-Virus detections, Firewall detections but also more advanced EDR detections. For a complete list of events please refer to [the documentation](https://help.eset.com/protect_admin/latest/en-US/events-exported-to-json-format.html).

[→ View full connector details](connectors/esetprotect.md)

---

### [[Deprecated] Exabeam Advanced Analytics](connectors/exabeam.md)

**Publisher:** Exabeam

**Solution:** [Exabeam Advanced Analytics](solutions/exabeam-advanced-analytics.md)

**Tables (1):** `Syslog`

The [Exabeam Advanced Analytics](https://www.exabeam.com/ueba/advanced-analytics-and-mitre-detect-and-stop-threats/) data connector provides the capability to ingest Exabeam Advanced Analytics events into Microsoft Sentinel. Refer to [Exabeam Advanced Analytics documentation](https://docs.exabeam.com/) for more information.

[→ View full connector details](connectors/exabeam.md)

---

### [[Deprecated] ExtraHop Reveal(x) via AMA](connectors/extrahopnetworksama.md)

**Publisher:** ExtraHop Networks

**Solution:** [ExtraHop Reveal(x)](solutions/extrahop-reveal(x).md)

**Tables (1):** `CommonSecurityLog`

The ExtraHop Reveal(x) data connector enables you to easily connect your Reveal(x) system with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This integration gives you the ability to gain insight into your organization's network and improve your security operation capabilities.

[→ View full connector details](connectors/extrahopnetworksama.md)

---

### [[Deprecated] ExtraHop Reveal(x) via Legacy Agent](connectors/extrahopnetworks.md)

**Publisher:** ExtraHop Networks

**Solution:** [ExtraHop Reveal(x)](solutions/extrahop-reveal(x).md)

**Tables (1):** `CommonSecurityLog`

The ExtraHop Reveal(x) data connector enables you to easily connect your Reveal(x) system with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This integration gives you the ability to gain insight into your organization's network and improve your security operation capabilities.

[→ View full connector details](connectors/extrahopnetworks.md)

---

### [[Deprecated] F5 Networks via AMA](connectors/f5ama.md)

**Publisher:** F5 Networks

**Solution:** [F5 Networks](solutions/f5-networks.md)

**Tables (1):** `CommonSecurityLog`

The F5 firewall connector allows you to easily connect your F5 logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/f5ama.md)

---

### [[Deprecated] F5 Networks via Legacy Agent](connectors/f5.md)

**Publisher:** F5 Networks

**Solution:** [F5 Networks](solutions/f5-networks.md)

**Tables (1):** `CommonSecurityLog`

The F5 firewall connector allows you to easily connect your F5 logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/f5.md)

---

### [[Deprecated] FireEye Network Security (NX) via AMA](connectors/fireeyenxama.md)

**Publisher:** FireEye

**Solution:** [FireEye Network Security](solutions/fireeye-network-security.md)

**Tables (1):** `CommonSecurityLog`

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

[→ View full connector details](connectors/fireeyenxama.md)

---

### [[Deprecated] FireEye Network Security (NX) via Legacy Agent](connectors/fireeyenx.md)

**Publisher:** FireEye

**Solution:** [FireEye Network Security](solutions/fireeye-network-security.md)

**Tables (1):** `CommonSecurityLog`

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

[→ View full connector details](connectors/fireeyenx.md)

---

### [[Deprecated] Forcepoint CASB via AMA](connectors/forcepointcasbama.md)

**Publisher:** Forcepoint CASB

**Solution:** [Forcepoint CASB](solutions/forcepoint-casb.md)

**Tables (1):** `CommonSecurityLog`

The Forcepoint CASB (Cloud Access Security Broker) Connector allows you to automatically export CASB logs and events into Microsoft Sentinel in real-time. This enriches visibility into user activities across locations and cloud applications, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

[→ View full connector details](connectors/forcepointcasbama.md)

---

### [[Deprecated] Forcepoint CASB via Legacy Agent](connectors/forcepointcasb.md)

**Publisher:** Forcepoint CASB

**Solution:** [Forcepoint CASB](solutions/forcepoint-casb.md)

**Tables (1):** `CommonSecurityLog`

The Forcepoint CASB (Cloud Access Security Broker) Connector allows you to automatically export CASB logs and events into Microsoft Sentinel in real-time. This enriches visibility into user activities across locations and cloud applications, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

[→ View full connector details](connectors/forcepointcasb.md)

---

### [[Deprecated] Forcepoint CSG via AMA](connectors/forcepointcsgama.md)

**Publisher:** Forcepoint

**Solution:** [Forcepoint CSG](solutions/forcepoint-csg.md)

**Tables (1):** `CommonSecurityLog`

Forcepoint Cloud Security Gateway is a converged cloud security service that provides visibility, control, and threat protection for users and data, wherever they are. For more information visit: https://www.forcepoint.com/product/cloud-security-gateway

[→ View full connector details](connectors/forcepointcsgama.md)

---

### [[Deprecated] Forcepoint CSG via Legacy Agent](connectors/forcepointcsg.md)

**Publisher:** Forcepoint

**Solution:** [Forcepoint CSG](solutions/forcepoint-csg.md)

**Tables (1):** `CommonSecurityLog`

Forcepoint Cloud Security Gateway is a converged cloud security service that provides visibility, control, and threat protection for users and data, wherever they are. For more information visit: https://www.forcepoint.com/product/cloud-security-gateway

[→ View full connector details](connectors/forcepointcsg.md)

---

### [[Deprecated] Forcepoint NGFW via AMA](connectors/forcepointngfwama.md)

**Publisher:** Forcepoint

**Solution:** [Forcepoint NGFW](solutions/forcepoint-ngfw.md)

**Tables (1):** `CommonSecurityLog`

The Forcepoint NGFW (Next Generation Firewall) connector allows you to automatically export user-defined Forcepoint NGFW logs into Microsoft Sentinel in real-time. This enriches visibility into user activities recorded by NGFW, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

[→ View full connector details](connectors/forcepointngfwama.md)

---

### [[Deprecated] Forcepoint NGFW via Legacy Agent](connectors/forcepointngfw.md)

**Publisher:** Forcepoint

**Solution:** [Forcepoint NGFW](solutions/forcepoint-ngfw.md)

**Tables (1):** `CommonSecurityLog`

The Forcepoint NGFW (Next Generation Firewall) connector allows you to automatically export user-defined Forcepoint NGFW logs into Microsoft Sentinel in real-time. This enriches visibility into user activities recorded by NGFW, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

[→ View full connector details](connectors/forcepointngfw.md)

---

### [[Deprecated] ForgeRock Identity Platform](connectors/forgerock.md)

**Publisher:** ForgeRock Inc

**Solution:** [ForgeRock Common Audit for CEF](solutions/forgerock-common-audit-for-cef.md)

**Tables (1):** `CommonSecurityLog`

The ForgeRock Identity Platform provides a single common auditing framework. Extract and aggregate log data across the entire platform with common audit (CAUD) event handlers and unique IDs so that it can be tracked holistically. Open and extensible, you can leverage audit logging and reporting capabilities for integration with Microsoft Sentinel via this CAUD for CEF connector.

[→ View full connector details](connectors/forgerock.md)

---

### [[Deprecated] Fortinet FortiWeb Web Application Firewall via Legacy Agent](connectors/fortinetfortiweb.md)

**Publisher:** Microsoft

**Solution:** [Fortinet FortiWeb Cloud WAF-as-a-Service connector for Microsoft Sentinel](solutions/fortinet-fortiweb-cloud-waf-as-a-service-connector-for-microsoft-sentinel.md)

**Tables (1):** `CommonSecurityLog`

The [fortiweb](https://www.fortinet.com/products/web-application-firewall/fortiweb) data connector provides the capability to ingest Threat Analytics and events into Microsoft Sentinel.

[→ View full connector details](connectors/fortinetfortiweb.md)

---

### [[Deprecated] Fortinet via AMA](connectors/fortinetama.md)

**Publisher:** Fortinet

**Solution:** [Fortinet FortiGate Next-Generation Firewall connector for Microsoft Sentinel](solutions/fortinet-fortigate-next-generation-firewall-connector-for-microsoft-sentinel.md)

**Tables (1):** `CommonSecurityLog`

The Fortinet firewall connector allows you to easily connect your Fortinet logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/fortinetama.md)

---

### [[Deprecated] Fortinet via Legacy Agent](connectors/fortinet.md)

**Publisher:** Fortinet

**Solution:** [Fortinet FortiGate Next-Generation Firewall connector for Microsoft Sentinel](solutions/fortinet-fortigate-next-generation-firewall-connector-for-microsoft-sentinel.md)

**Tables (1):** `CommonSecurityLog`

The Fortinet firewall connector allows you to easily connect your Fortinet logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/fortinet.md)

---

### [[Deprecated] GitHub Enterprise Audit Log](connectors/githubecauditlogpolling.md)

**Publisher:** GitHub

**Solution:** [GitHub](solutions/github.md)

**Tables (1):** `GitHubAuditLogPolling_CL`

The GitHub audit log connector provides the capability to ingest GitHub logs into Microsoft Sentinel. By connecting GitHub audit logs into Microsoft Sentinel, you can view this data in workbooks, use it to create custom alerts, and improve your investigation process. 

 **Note:** If you intended to ingest GitHub subscribed events into Microsoft Sentinel, please refer to GitHub (using Webhooks) Connector from "**Data Connectors**" gallery.

<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/githubecauditlogpolling.md)

---

### [[Deprecated] GitLab](connectors/gitlab.md)

**Publisher:** Microsoft

**Solution:** [GitLab](solutions/gitlab.md)

**Tables (1):** `Syslog`

The [GitLab](https://about.gitlab.com/solutions/devops-platform/) connector allows you to easily connect your GitLab (GitLab Enterprise Edition - Standalone) logs with Microsoft Sentinel. This gives you more security insight into your organization's DevOps pipelines.

[→ View full connector details](connectors/gitlab.md)

---

### [[Deprecated] ISC Bind](connectors/iscbind.md)

**Publisher:** ISC

**Solution:** [ISC Bind](solutions/isc-bind.md)

**Tables (1):** `Syslog`

The [ISC Bind](https://www.isc.org/bind/) connector allows you to easily connect your ISC Bind logs with Microsoft Sentinel. This gives you more insight into your organization's network traffic data, DNS query data, traffic statistics and improves your security operation capabilities.

[→ View full connector details](connectors/iscbind.md)

---

### [[Deprecated] Illumio Core via AMA](connectors/illumiocoreama.md)

**Publisher:** Illumio

**Solution:** [Illumio Core](solutions/illumio-core.md)

**Tables (1):** `CommonSecurityLog`

The [Illumio Core](https://www.illumio.com/products/) data connector provides the capability to ingest Illumio Core logs into Microsoft Sentinel.

[→ View full connector details](connectors/illumiocoreama.md)

---

### [[Deprecated] Illumio Core via Legacy Agent](connectors/illumiocore.md)

**Publisher:** Illumio

**Solution:** [Illumio Core](solutions/illumio-core.md)

**Tables (1):** `CommonSecurityLog`

The [Illumio Core](https://www.illumio.com/products/) data connector provides the capability to ingest Illumio Core logs into Microsoft Sentinel.

[→ View full connector details](connectors/illumiocore.md)

---

### [[Deprecated] Illusive Platform via AMA](connectors/illusiveattackmanagementsystemama.md)

**Publisher:** illusive

**Solution:** [Illusive Platform](solutions/illusive-platform.md)

**Tables (1):** `CommonSecurityLog`

The Illusive Platform Connector allows you to share Illusive's attack surface analysis data and incident logs with Microsoft Sentinel and view this information in dedicated dashboards that offer insight into your organization's attack surface risk (ASM Dashboard) and track unauthorized lateral movement in your organization's network (ADS Dashboard).

[→ View full connector details](connectors/illusiveattackmanagementsystemama.md)

---

### [[Deprecated] Illusive Platform via Legacy Agent](connectors/illusiveattackmanagementsystem.md)

**Publisher:** illusive

**Solution:** [Illusive Platform](solutions/illusive-platform.md)

**Tables (1):** `CommonSecurityLog`

The Illusive Platform Connector allows you to share Illusive's attack surface analysis data and incident logs with Microsoft Sentinel and view this information in dedicated dashboards that offer insight into your organization's attack surface risk (ASM Dashboard) and track unauthorized lateral movement in your organization's network (ADS Dashboard).

[→ View full connector details](connectors/illusiveattackmanagementsystem.md)

---

### [[Deprecated] Infoblox Cloud Data Connector via AMA](connectors/infobloxclouddataconnectorama.md)

**Publisher:** Infoblox

**Solution:** [Infoblox Cloud Data Connector](solutions/infoblox-cloud-data-connector.md)

**Tables (1):** `CommonSecurityLog`

The Infoblox Cloud Data Connector allows you to easily connect your Infoblox BloxOne data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

[→ View full connector details](connectors/infobloxclouddataconnectorama.md)

---

### [[Deprecated] Infoblox Cloud Data Connector via Legacy Agent](connectors/infobloxclouddataconnector.md)

**Publisher:** Infoblox

**Solution:** [Infoblox Cloud Data Connector](solutions/infoblox-cloud-data-connector.md)

**Tables (1):** `CommonSecurityLog`

The Infoblox Cloud Data Connector allows you to easily connect your Infoblox BloxOne data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

[→ View full connector details](connectors/infobloxclouddataconnector.md)

---

### [[Deprecated] Infoblox NIOS](connectors/infobloxnios.md)

**Publisher:** Infoblox

**Solution:** [Infoblox NIOS](solutions/infoblox-nios.md)

**Tables (1):** `Syslog`

The [Infoblox Network Identity Operating System (NIOS)](https://www.infoblox.com/glossary/network-identity-operating-system-nios/) connector allows you to easily connect your Infoblox NIOS logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/infobloxnios.md)

---

### [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](connectors/infobloxsocinsightsdataconnector-legacy.md)

**Publisher:** Infoblox

**Solution:** [Infoblox](solutions/infoblox.md)

**Tables (1):** `CommonSecurityLog`

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 

This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the legacy Log Analytics agent.

**Microsoft recommends installation of Infoblox SOC Insight Data Connector via AMA Connector.** The legacy connector uses the Log Analytics agent which is about to be deprecated by **Aug 31, 2024,** and should only be installed where AMA is not supported.

 Using MMA and AMA on the same machine can cause log duplication and extra ingestion cost. [More details](https://learn.microsoft.com/en-us/azure/sentinel/ama-migrate).

[→ View full connector details](connectors/infobloxsocinsightsdataconnector-legacy.md)

---

### [[Deprecated] Ivanti Unified Endpoint Management](connectors/ivantiuem.md)

**Publisher:** Ivanti

**Solution:** [Ivanti Unified Endpoint Management](solutions/ivanti-unified-endpoint-management.md)

**Tables (1):** `Syslog`

The [Ivanti Unified Endpoint Management](https://www.ivanti.com/products/unified-endpoint-manager) data connector provides the capability to ingest [Ivanti UEM Alerts](https://help.ivanti.com/ld/help/en_US/LDMS/11.0/Windows/alert-c-monitoring-overview.htm) into Microsoft Sentinel.

[→ View full connector details](connectors/ivantiuem.md)

---

### [[Deprecated] JBoss Enterprise Application Platform](connectors/jbosseap.md)

**Publisher:** Red Hat

**Solution:** [JBoss](solutions/jboss.md)

**Tables (1):** `JBossLogs_CL`

The JBoss Enterprise Application Platform data connector provides the capability to ingest [JBoss](https://www.redhat.com/en/technologies/jboss-middleware/application-platform) events into Microsoft Sentinel. Refer to [Red Hat documentation](https://access.redhat.com/documentation/en-us/red_hat_jboss_enterprise_application_platform/7.0/html/configuration_guide/logging_with_jboss_eap) for more information.

[→ View full connector details](connectors/jbosseap.md)

---

### [[Deprecated] Juniper IDP](connectors/juniperidp.md)

**Publisher:** Juniper

**Solution:** [JuniperIDP](solutions/juniperidp.md)

**Tables (1):** `JuniperIDP_CL`

The [Juniper](https://www.juniper.net/) IDP data connector provides the capability to ingest [Juniper IDP](https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-overview.html) events into Microsoft Sentinel.

[→ View full connector details](connectors/juniperidp.md)

---

### [[Deprecated] Juniper SRX](connectors/junipersrx.md)

**Publisher:** Juniper

**Solution:** [Juniper SRX](solutions/juniper-srx.md)

**Tables (1):** `Syslog`

The [Juniper SRX](https://www.juniper.net/us/en/products-services/security/srx-series/) connector allows you to easily connect your Juniper SRX logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/junipersrx.md)

---

### [[Deprecated] McAfee Network Security Platform](connectors/mcafeensp.md)

**Publisher:** McAfee

**Solution:** [McAfee Network Security Platform](solutions/mcafee-network-security-platform.md)

**Tables (1):** `Syslog`

The [McAfee® Network Security Platform](https://www.mcafee.com/enterprise/en-us/products/network-security-platform.html) data connector provides the capability to ingest [McAfee® Network Security Platform events](https://docs.mcafee.com/bundle/network-security-platform-10.1.x-integration-guide-unmanaged/page/GUID-8C706BE9-6AC9-4641-8A53-8910B51207D8.html) into Microsoft Sentinel. Refer to [McAfee® Network Security Platform](https://docs.mcafee.com/bundle/network-security-platform-10.1.x-integration-guide-unmanaged/page/GUID-F7D281EC-1CC9-4962-A7A3-5A9D9584670E.html) for more information.

[→ View full connector details](connectors/mcafeensp.md)

---

### [[Deprecated] McAfee ePolicy Orchestrator (ePO)](connectors/mcafeeepo.md)

**Publisher:** McAfee

**Solution:** [McAfee ePolicy Orchestrator](solutions/mcafee-epolicy-orchestrator.md)

**Tables (1):** `Syslog`

The McAfee ePolicy Orchestrator data connector provides the capability to ingest [McAfee ePO](https://www.mcafee.com/enterprise/en-us/products/epolicy-orchestrator.html) events into Microsoft Sentinel through the syslog. Refer to [documentation](https://docs.mcafee.com/bundle/epolicy-orchestrator-landing/page/GUID-0C40020F-5B7F-4549-B9CC-0E017BC8797F.html) for more information.

[→ View full connector details](connectors/mcafeeepo.md)

---

### [[Deprecated] Microsoft Exchange Logs and Events](connectors/esi-exchangeadminauditlogevents.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Exchange Security - Exchange On-Premises](solutions/microsoft-exchange-security---exchange-on-premises.md)

**Tables (5):** `Event`, `ExchangeHttpProxy_CL`, `MessageTrackingLog_CL`, `SecurityEvent`, `W3CIISLog`

Deprecated, use the 'ESI-Opt' dataconnectors. You can stream all Exchange Audit events, IIS Logs, HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

[→ View full connector details](connectors/esi-exchangeadminauditlogevents.md)

---

### [[Deprecated] Microsoft Sysmon For Linux](connectors/microsoftsysmonforlinux.md)

**Publisher:** Microsoft

**Solution:** [Microsoft Sysmon For Linux](solutions/microsoft-sysmon-for-linux.md)

**Tables (2):** `Syslog`, `vimProcessCreateLinuxSysmon`

[Sysmon for Linux](https://github.com/Sysinternals/SysmonForLinux) provides detailed information about process creations, network connections and other system events.
[Sysmon for linux link:]. The Sysmon for Linux connector uses [Syslog](https://aka.ms/sysLogInfo) as its data ingestion method. This solution depends on ASIM to work as expected. [Deploy ASIM](https://aka.ms/DeployASIM) to get the full value from the solution.

[→ View full connector details](connectors/microsoftsysmonforlinux.md)

---

### [[Deprecated] MongoDB Audit](connectors/mongodb.md)

**Publisher:** MongoDB

**Solution:** [MongoDBAudit](solutions/mongodbaudit.md)

**Tables (1):** `MongoDBAudit_CL`

MongoDB data connector provides the capability to ingest [MongoDBAudit](https://www.mongodb.com/) into Microsoft Sentinel. Refer to [MongoDB documentation](https://www.mongodb.com/docs/manual/tutorial/getting-started/) for more information.

[→ View full connector details](connectors/mongodb.md)

---

### [[Deprecated] NGINX HTTP Server](connectors/nginxhttpserver.md)

**Publisher:** Nginx

**Solution:** [NGINX HTTP Server](solutions/nginx-http-server.md)

**Tables (1):** `NGINX_CL`

The NGINX HTTP Server data connector provides the capability to ingest [NGINX](https://nginx.org/en/) HTTP Server events into Microsoft Sentinel. Refer to [NGINX Logs documentation](https://nginx.org/en/docs/http/ngx_http_log_module.html) for more information.

[→ View full connector details](connectors/nginxhttpserver.md)

---

### [[Deprecated] Nasuni Edge Appliance](connectors/nasuniedgeappliance.md)

**Publisher:** Nasuni

**Solution:** [Nasuni](solutions/nasuni.md)

**Tables (2):** `Nasuni`, `Syslog`

The [Nasuni](https://www.nasuni.com/) connector allows you to easily connect your Nasuni Edge Appliance Notifications and file system audit logs with Microsoft Sentinel. This gives you more insight into activity within your Nasuni infrastructure and improves your security operation capabilities.

[→ View full connector details](connectors/nasuniedgeappliance.md)

---

### [[Deprecated] Netwrix Auditor via AMA](connectors/netwrixama.md)

**Publisher:** Netwrix

**Solution:** [Netwrix Auditor](solutions/netwrix-auditor.md)

**Tables (1):** `CommonSecurityLog`

Netwrix Auditor data connector provides the capability to ingest [Netwrix Auditor (formerly Stealthbits Privileged Activity Manager)](https://www.netwrix.com/auditor.html) events into Microsoft Sentinel. Refer to [Netwrix documentation](https://helpcenter.netwrix.com/) for more information.

[→ View full connector details](connectors/netwrixama.md)

---

### [[Deprecated] Netwrix Auditor via Legacy Agent](connectors/netwrix.md)

**Publisher:** Netwrix

**Solution:** [Netwrix Auditor](solutions/netwrix-auditor.md)

**Tables (1):** `CommonSecurityLog`

Netwrix Auditor data connector provides the capability to ingest [Netwrix Auditor (formerly Stealthbits Privileged Activity Manager)](https://www.netwrix.com/auditor.html) events into Microsoft Sentinel. Refer to [Netwrix documentation](https://helpcenter.netwrix.com/) for more information.

[→ View full connector details](connectors/netwrix.md)

---

### [[Deprecated] Nozomi Networks N2OS via AMA](connectors/nozominetworksn2osama.md)

**Publisher:** Nozomi Networks

**Solution:** [NozomiNetworks](solutions/nozominetworks.md)

**Tables (1):** `CommonSecurityLog`

The [Nozomi Networks](https://www.nozominetworks.com/) data connector provides the capability to ingest Nozomi Networks Events into Microsoft Sentinel. Refer to the Nozomi Networks [PDF documentation](https://www.nozominetworks.com/resources/data-sheets-brochures-learning-guides/) for more information.

[→ View full connector details](connectors/nozominetworksn2osama.md)

---

### [[Deprecated] Nozomi Networks N2OS via Legacy Agent](connectors/nozominetworksn2os.md)

**Publisher:** Nozomi Networks

**Solution:** [NozomiNetworks](solutions/nozominetworks.md)

**Tables (1):** `CommonSecurityLog`

The [Nozomi Networks](https://www.nozominetworks.com/) data connector provides the capability to ingest Nozomi Networks Events into Microsoft Sentinel. Refer to the Nozomi Networks [PDF documentation](https://www.nozominetworks.com/resources/data-sheets-brochures-learning-guides/) for more information.

[→ View full connector details](connectors/nozominetworksn2os.md)

---

### [[Deprecated] OSSEC via AMA](connectors/ossecama.md)

**Publisher:** OSSEC

**Solution:** [OSSEC](solutions/ossec.md)

**Tables (1):** `CommonSecurityLog`

OSSEC data connector provides the capability to ingest [OSSEC](https://www.ossec.net/) events into Microsoft Sentinel. Refer to [OSSEC documentation](https://www.ossec.net/docs) for more information.

[→ View full connector details](connectors/ossecama.md)

---

### [[Deprecated] OSSEC via Legacy Agent](connectors/ossec.md)

**Publisher:** OSSEC

**Solution:** [OSSEC](solutions/ossec.md)

**Tables (1):** `CommonSecurityLog`

OSSEC data connector provides the capability to ingest [OSSEC](https://www.ossec.net/) events into Microsoft Sentinel. Refer to [OSSEC documentation](https://www.ossec.net/docs) for more information.

[→ View full connector details](connectors/ossec.md)

---

### [[Deprecated] Onapsis Platform](connectors/onapsisplatform.md)

**Publisher:** Onapsis

**Solution:** [Onapsis Platform](solutions/onapsis-platform.md)

**Tables (1):** `CommonSecurityLog`

The Onapsis Connector allows you to export the alarms triggered in the Onapsis Platform into Microsoft Sentinel in real-time. This gives you the ability to monitor the activity on your SAP systems, identify incidents and respond to them quickly.

[→ View full connector details](connectors/onapsisplatform.md)

---

### [[Deprecated] OpenVPN Server](connectors/openvpn.md)

**Publisher:** OpenVPN

**Solution:** [OpenVPN](solutions/openvpn.md)

**Tables (1):** `Syslog`

The [OpenVPN](https://github.com/OpenVPN) data connector provides the capability to ingest OpenVPN Server logs into Microsoft Sentinel.

[→ View full connector details](connectors/openvpn.md)

---

### [[Deprecated] Oracle Database Audit](connectors/oracledatabaseaudit.md)

**Publisher:** Oracle

**Solution:** [OracleDatabaseAudit](solutions/oracledatabaseaudit.md)

**Tables (1):** `Syslog`

The Oracle DB Audit data connector provides the capability to ingest [Oracle Database](https://www.oracle.com/database/technologies/) audit events into Microsoft Sentinel through the syslog. Refer to [documentation](https://docs.oracle.com/en/database/oracle/oracle-database/21/dbseg/introduction-to-auditing.html#GUID-94381464-53A3-421B-8F13-BD171C867405) for more information.

[→ View full connector details](connectors/oracledatabaseaudit.md)

---

### [[Deprecated] Oracle WebLogic Server](connectors/oracleweblogicserver.md)

**Publisher:** Oracle

**Solution:** [OracleWebLogicServer](solutions/oracleweblogicserver.md)

**Tables (1):** `OracleWebLogicServer_CL`

OracleWebLogicServer data connector provides the capability to ingest [OracleWebLogicServer](https://docs.oracle.com/en/middleware/standalone/weblogic-server/index.html) events into Microsoft Sentinel. Refer to [OracleWebLogicServer documentation](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/index.html) for more information.

[→ View full connector details](connectors/oracleweblogicserver.md)

---

### [[Deprecated] Palo Alto Networks (Firewall) via AMA](connectors/paloaltonetworksama.md)

**Publisher:** Palo Alto Networks

**Solution:** [PaloAlto-PAN-OS](solutions/paloalto-pan-os.md)

**Tables (1):** `CommonSecurityLog`

The Palo Alto Networks firewall connector allows you to easily connect your Palo Alto Networks logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/paloaltonetworksama.md)

---

### [[Deprecated] Palo Alto Networks (Firewall) via Legacy Agent](connectors/paloaltonetworks.md)

**Publisher:** Palo Alto Networks

**Solution:** [PaloAlto-PAN-OS](solutions/paloalto-pan-os.md)

**Tables (1):** `CommonSecurityLog`

The Palo Alto Networks firewall connector allows you to easily connect your Palo Alto Networks logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/paloaltonetworks.md)

---

### [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](connectors/paloaltocdlama.md)

**Publisher:** Palo Alto Networks

**Solution:** [PaloAltoCDL](solutions/paloaltocdl.md)

**Tables (1):** `CommonSecurityLog`

The [Palo Alto Networks CDL](https://www.paloaltonetworks.com/cortex/cortex-data-lake) data connector provides the capability to ingest [CDL logs](https://docs.paloaltonetworks.com/strata-logging-service/log-reference/log-forwarding-schema-overview) into Microsoft Sentinel.

[→ View full connector details](connectors/paloaltocdlama.md)

---

### [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via Legacy Agent](connectors/paloaltocdl.md)

**Publisher:** Palo Alto Networks

**Solution:** [PaloAltoCDL](solutions/paloaltocdl.md)

**Tables (1):** `CommonSecurityLog`

The [Palo Alto Networks CDL](https://www.paloaltonetworks.com/cortex/cortex-data-lake) data connector provides the capability to ingest [CDL logs](https://docs.paloaltonetworks.com/strata-logging-service/log-reference/log-forwarding-schema-overview) into Microsoft Sentinel.

[→ View full connector details](connectors/paloaltocdl.md)

---

### [[Deprecated] PingFederate via AMA](connectors/pingfederateama.md)

**Publisher:** Ping Identity

**Solution:** [PingFederate](solutions/pingfederate.md)

**Tables (1):** `CommonSecurityLog`

The [PingFederate](https://www.pingidentity.com/en/software/pingfederate.html) data connector provides the capability to ingest [PingFederate events](https://docs.pingidentity.com/bundle/pingfederate-102/page/lly1564002980532.html) into Microsoft Sentinel. Refer to [PingFederate documentation](https://docs.pingidentity.com/bundle/pingfederate-102/page/tle1564002955874.html) for more information.

[→ View full connector details](connectors/pingfederateama.md)

---

### [[Deprecated] PingFederate via Legacy Agent](connectors/pingfederate.md)

**Publisher:** Ping Identity

**Solution:** [PingFederate](solutions/pingfederate.md)

**Tables (1):** `CommonSecurityLog`

The [PingFederate](https://www.pingidentity.com/en/software/pingfederate.html) data connector provides the capability to ingest [PingFederate events](https://docs.pingidentity.com/bundle/pingfederate-102/page/lly1564002980532.html) into Microsoft Sentinel. Refer to [PingFederate documentation](https://docs.pingidentity.com/bundle/pingfederate-102/page/tle1564002955874.html) for more information.

[→ View full connector details](connectors/pingfederate.md)

---

### [[Deprecated] PostgreSQL Events](connectors/postgresql.md)

**Publisher:** PostgreSQL

**Solution:** [PostgreSQL](solutions/postgresql.md)

**Tables (1):** `PostgreSQL_CL`

PostgreSQL data connector provides the capability to ingest [PostgreSQL](https://www.postgresql.org/) events into Microsoft Sentinel. Refer to [PostgreSQL documentation](https://www.postgresql.org/docs/current/index.html) for more information.

[→ View full connector details](connectors/postgresql.md)

---

### [[Deprecated] Proofpoint On Demand Email Security](connectors/proofpointpod.md)

**Publisher:** Proofpoint

**Solution:** [Proofpoint On demand(POD) Email Security](solutions/proofpoint-on-demand(pod)-email-security.md)

**Tables (4):** `ProofpointPODMessage_CL`, `ProofpointPOD_maillog_CL`, `ProofpointPOD_message_CL`, `maillog_CL`

Proofpoint On Demand Email Security data connector provides the capability to get Proofpoint on Demand Email Protection data, allows users to check message traceability, monitoring into email activity, threats,and data exfiltration by attackers and malicious insiders. The connector provides ability to review events in your org on an accelerated basis, get event log files in hourly increments for recent activity.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/proofpointpod.md)

---

### [[Deprecated] Proofpoint TAP](connectors/proofpointtap.md)

**Publisher:** Proofpoint

**Solution:** [ProofPointTap](solutions/proofpointtap.md)

**Tables (4):** `ProofPointTAPClicksBlocked_CL`, `ProofPointTAPClicksPermitted_CL`, `ProofPointTAPMessagesBlocked_CL`, `ProofPointTAPMessagesDelivered_CL`

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[→ View full connector details](connectors/proofpointtap.md)

---

### [[Deprecated] Pulse Connect Secure](connectors/pulseconnectsecure.md)

**Publisher:** Pulse Secure

**Solution:** [Pulse Connect Secure](solutions/pulse-connect-secure.md)

**Tables (1):** `Syslog`

The [Pulse Connect Secure](https://www.pulsesecure.net/products/pulse-connect-secure/) connector allows you to easily connect your Pulse Connect Secure logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Pulse Connect Secure with Microsoft Sentinel provides more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/pulseconnectsecure.md)

---

### [[Deprecated] RIDGEBOT - data connector for Microsoft Sentinel](connectors/ridgebotdataconnector.md)

**Publisher:** RidgeSecurity

**Solution:** [RidgeSecurity](solutions/ridgesecurity.md)

**Tables (1):** `CommonSecurityLog`

The RidgeBot connector lets users connect RidgeBot with Microsoft Sentinel, allowing creation of Dashboards, Workbooks, Notebooks and Alerts.

[→ View full connector details](connectors/ridgebotdataconnector.md)

---

### [[Deprecated] RSA® SecurID (Authentication Manager)](connectors/rsasecuridam.md)

**Publisher:** RSA

**Solution:** [RSA SecurID](solutions/rsa-securid.md)

**Tables (1):** `Syslog`

The [RSA® SecurID Authentication Manager](https://www.securid.com/) data connector provides the capability to ingest [RSA® SecurID Authentication Manager events](https://community.rsa.com/t5/rsa-authentication-manager/rsa-authentication-manager-log-messages/ta-p/630160) into Microsoft Sentinel. Refer to [RSA® SecurID Authentication Manager documentation](https://community.rsa.com/t5/rsa-authentication-manager/getting-started-with-rsa-authentication-manager/ta-p/569582) for more information.

[→ View full connector details](connectors/rsasecuridam.md)

---

### [[Deprecated] SonicWall Firewall via AMA](connectors/sonicwallfirewallama.md)

**Publisher:** SonicWall

**Solution:** [SonicWall Firewall](solutions/sonicwall-firewall.md)

**Tables (1):** `CommonSecurityLog`

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by SonicWall to allow event interoperability among different platforms. By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

[→ View full connector details](connectors/sonicwallfirewallama.md)

---

### [[Deprecated] SonicWall Firewall via Legacy Agent](connectors/sonicwallfirewall.md)

**Publisher:** SonicWall

**Solution:** [SonicWall Firewall](solutions/sonicwall-firewall.md)

**Tables (1):** `CommonSecurityLog`

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by SonicWall to allow event interoperability among different platforms. By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

[→ View full connector details](connectors/sonicwallfirewall.md)

---

### [[Deprecated] Sophos XG Firewall](connectors/sophosxgfirewall.md)

**Publisher:** Sophos

**Solution:** [Sophos XG Firewall](solutions/sophos-xg-firewall.md)

**Tables (1):** `Syslog`

The [Sophos XG Firewall](https://www.sophos.com/products/next-gen-firewall.aspx) allows you to easily connect your Sophos XG Firewall logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Sophos XG Firewall with Microsoft Sentinel provides more visibility into your organization's firewall traffic and will enhance security monitoring capabilities.

[→ View full connector details](connectors/sophosxgfirewall.md)

---

### [[Deprecated] Squid Proxy](connectors/squidproxy.md)

**Publisher:** Squid

**Solution:** [SquidProxy](solutions/squidproxy.md)

**Tables (1):** `SquidProxy_CL`

The [Squid Proxy](http://www.squid-cache.org/) connector allows you to easily connect your Squid Proxy logs with Microsoft Sentinel. This gives you more insight into your organization's network proxy traffic and improves your security operation capabilities.

[→ View full connector details](connectors/squidproxy.md)

---

### [[Deprecated] Symantec Endpoint Protection](connectors/symantecendpointprotection.md)

**Publisher:** Broadcom

**Solution:** [Symantec Endpoint Protection](solutions/symantec-endpoint-protection.md)

**Tables (1):** `Syslog`

The [Broadcom Symantec Endpoint Protection (SEP)](https://www.broadcom.com/products/cyber-security/endpoint/end-user/enterprise) connector allows you to easily connect your SEP logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/symantecendpointprotection.md)

---

### [[Deprecated] Symantec ProxySG](connectors/symantecproxysg.md)

**Publisher:** Symantec

**Solution:** [SymantecProxySG](solutions/symantecproxysg.md)

**Tables (1):** `Syslog`

The [Symantec ProxySG](https://www.broadcom.com/products/cyber-security/network/gateway/proxy-sg-and-advanced-secure-gateway) allows you to easily connect your Symantec ProxySG logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Symantec ProxySG with Microsoft Sentinel provides more visibility into your organization's network proxy traffic and will enhance security monitoring capabilities.

[→ View full connector details](connectors/symantecproxysg.md)

---

### [[Deprecated] Symantec VIP](connectors/symantecvip.md)

**Publisher:** Symantec

**Solution:** [Symantec VIP](solutions/symantec-vip.md)

**Tables (1):** `Syslog`

The [Symantec VIP](https://vip.symantec.com/) connector allows you to easily connect your Symantec VIP logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

[→ View full connector details](connectors/symantecvip.md)

---

### [[Deprecated] Trend Micro Apex One via AMA](connectors/trendmicroapexoneama.md)

**Publisher:** Trend Micro

**Solution:** [Trend Micro Apex One](solutions/trend-micro-apex-one.md)

**Tables (1):** `CommonSecurityLog`

The [Trend Micro Apex One](https://www.trendmicro.com/en_us/business/products/user-protection/sps/endpoint.html) data connector provides the capability to ingest [Trend Micro Apex One events](https://aka.ms/sentinel-TrendMicroApex-OneEvents) into Microsoft Sentinel. Refer to [Trend Micro Apex Central](https://aka.ms/sentinel-TrendMicroApex-OneCentral) for more information.

[→ View full connector details](connectors/trendmicroapexoneama.md)

---

### [[Deprecated] Trend Micro Apex One via Legacy Agent](connectors/trendmicroapexone.md)

**Publisher:** Trend Micro

**Solution:** [Trend Micro Apex One](solutions/trend-micro-apex-one.md)

**Tables (1):** `CommonSecurityLog`

The [Trend Micro Apex One](https://www.trendmicro.com/en_us/business/products/user-protection/sps/endpoint.html) data connector provides the capability to ingest [Trend Micro Apex One events](https://aka.ms/sentinel-TrendMicroApex-OneEvents) into Microsoft Sentinel. Refer to [Trend Micro Apex Central](https://aka.ms/sentinel-TrendMicroApex-OneCentral) for more information.

[→ View full connector details](connectors/trendmicroapexone.md)

---

### [[Deprecated] Trend Micro Deep Security via Legacy](connectors/trendmicro.md)

**Publisher:** Trend Micro

**Solution:** [Trend Micro Deep Security](solutions/trend-micro-deep-security.md)

**Tables (1):** `CommonSecurityLog`

The Trend Micro Deep Security connector allows you to easily connect your Deep Security logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's networks/systems and improves your security operation capabilities.

[→ View full connector details](connectors/trendmicro.md)

---

### [[Deprecated] Trend Micro TippingPoint via Legacy](connectors/trendmicrotippingpoint.md)

**Publisher:** Trend Micro

**Solution:** [Trend Micro TippingPoint](solutions/trend-micro-tippingpoint.md)

**Tables (1):** `CommonSecurityLog`

The Trend Micro TippingPoint connector allows you to easily connect your TippingPoint SMS IPS events with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's networks/systems and improves your security operation capabilities.

[→ View full connector details](connectors/trendmicrotippingpoint.md)

---

### [[Deprecated] Ubiquiti UniFi](connectors/ubiquitiunifi.md)

**Publisher:** Ubiquiti

**Solution:** [Ubiquiti UniFi](solutions/ubiquiti-unifi.md)

**Tables (1):** `Ubiquiti_CL`

The [Ubiquiti UniFi](https://www.ui.com/) data connector provides the capability to ingest [Ubiquiti UniFi firewall, dns, ssh, AP events](https://help.ui.com/hc/en-us/articles/204959834-UniFi-How-to-View-Log-Files) into Microsoft Sentinel.

[→ View full connector details](connectors/ubiquitiunifi.md)

---

### [[Deprecated] VMware ESXi](connectors/vmwareesxi.md)

**Publisher:** VMWare

**Solution:** [VMWareESXi](solutions/vmwareesxi.md)

**Tables (1):** `Syslog`

The [VMware ESXi](https://www.vmware.com/products/esxi-and-esx.html) connector allows you to easily connect your VMWare ESXi logs with Microsoft Sentinel This gives you more insight into your organization's ESXi servers and improves your security operation capabilities.

[→ View full connector details](connectors/vmwareesxi.md)

---

### [[Deprecated] VMware vCenter](connectors/vmwarevcenter.md)

**Publisher:** VMware

**Solution:** [VMware vCenter](solutions/vmware-vcenter.md)

**Tables (1):** `vcenter_CL`

The [vCenter](https://www.vmware.com/in/products/vcenter-server.html) connector allows you to easily connect your vCenter server logs with Microsoft Sentinel. This gives you more insight into your organization's data centers and improves your security operation capabilities.

[→ View full connector details](connectors/vmwarevcenter.md)

---

### [[Deprecated] Vectra AI Detect via AMA](connectors/aivectradetectama.md)

**Publisher:** Vectra AI

**Solution:** [Vectra AI Detect](solutions/vectra-ai-detect.md)

**Tables (1):** `CommonSecurityLog`

The AI Vectra Detect connector allows users to connect Vectra Detect logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives users more insight into their organization's network and improves their security operation capabilities.

[→ View full connector details](connectors/aivectradetectama.md)

---

### [[Deprecated] Vectra AI Detect via Legacy Agent](connectors/aivectradetect.md)

**Publisher:** Vectra AI

**Solution:** [Vectra AI Detect](solutions/vectra-ai-detect.md)

**Tables (1):** `CommonSecurityLog`

The AI Vectra Detect connector allows users to connect Vectra Detect logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives users more insight into their organization's network and improves their security operation capabilities.

[→ View full connector details](connectors/aivectradetect.md)

---

### [[Deprecated] Votiro Sanitization Engine Logs](connectors/votiro.md)

**Publisher:** Votiro

**Solution:** [Votiro](solutions/votiro.md)

**Tables (1):** `CommonSecurityLog`

The Votiro data connector allows you to easily connect your Votiro Event logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.  Using Votiro on Microsoft Sentinel will provide you more insights into the sanitization results of files.

[→ View full connector details](connectors/votiro.md)

---

### [[Deprecated] WatchGuard Firebox](connectors/watchguardfirebox.md)

**Publisher:** WatchGuard Technologies

**Solution:** [Watchguard Firebox](solutions/watchguard-firebox.md)

**Tables (1):** `Syslog`

WatchGuard Firebox (https://www.watchguard.com/wgrd-products/firewall-appliances and https://www.watchguard.com/wgrd-products/cloud-and-virtual-firewalls) is security products/firewall-appliances. Watchguard Firebox will send syslog to Watchguard Firebox collector agent.The agent then sends the message to the workspace.

[→ View full connector details](connectors/watchguardfirebox.md)

---

### [[Deprecated] WireX Network Forensics Platform via AMA](connectors/wirex-systems-nfpama.md)

**Publisher:** WireX_Systems

**Solution:** [WireX Network Forensics Platform](solutions/wirex-network-forensics-platform.md)

**Tables (1):** `CommonSecurityLog`

The WireX Systems data connector allows security professional to integrate with Microsoft Sentinel to allow you to further enrich your forensics investigations; to not only encompass the contextual content offered by WireX but to analyze data from other sources, and to create custom dashboards to give the most complete picture during a forensic investigation and to create custom workflows.

[→ View full connector details](connectors/wirex-systems-nfpama.md)

---

### [[Deprecated] WireX Network Forensics Platform via Legacy Agent](connectors/wirex-systems-nfp.md)

**Publisher:** WireX_Systems

**Solution:** [WireX Network Forensics Platform](solutions/wirex-network-forensics-platform.md)

**Tables (1):** `CommonSecurityLog`

The WireX Systems data connector allows security professional to integrate with Microsoft Sentinel to allow you to further enrich your forensics investigations; to not only encompass the contextual content offered by WireX but to analyze data from other sources, and to create custom dashboards to give the most complete picture during a forensic investigation and to create custom workflows.

[→ View full connector details](connectors/wirex-systems-nfp.md)

---

### [[Deprecated] WithSecure Elements via Connector](connectors/withsecureelementsviaconnector.md)

**Publisher:** WithSecure

**Solution:** [WithSecureElementsViaConnector](solutions/withsecureelementsviaconnector.md)

**Tables (1):** `CommonSecurityLog`

WithSecure Elements is a unified cloud-based cyber security platform.
By connecting WithSecure Elements via Connector to Microsoft Sentinel, security events can be received in Common Event Format (CEF) over syslog.
It requires deploying "Elements Connector" either on-prem or in cloud.
The Common Event Format (CEF) provides natively search & correlation, alerting and threat intelligence enrichment for each data log.

[→ View full connector details](connectors/withsecureelementsviaconnector.md)

---

### [[Deprecated] Zscaler Private Access](connectors/zscalerprivateaccess.md)

**Publisher:** Zscaler

**Solution:** [Zscaler Private Access (ZPA)](solutions/zscaler-private-access-(zpa).md)

**Tables (1):** `ZPA_CL`

The [Zscaler Private Access (ZPA)](https://help.zscaler.com/zpa/what-zscaler-private-access) data connector provides the capability to ingest [Zscaler Private Access events](https://help.zscaler.com/zpa/log-streaming-service) into Microsoft Sentinel. Refer to [Zscaler Private Access documentation](https://help.zscaler.com/zpa) for more information.

[→ View full connector details](connectors/zscalerprivateaccess.md)

---

### [[Deprecated] iboss via Legacy Agent](connectors/iboss.md)

**Publisher:** iboss

**Solution:** [iboss](solutions/iboss.md)

**Tables (1):** `CommonSecurityLog`

The [iboss](https://www.iboss.com) data connector enables you to seamlessly connect your Threat Console to Microsoft Sentinel and enrich your instance with iboss URL event logs. Our logs are forwarded in Common Event Format (CEF) over Syslog and the configuration required can be completed on the iboss platform without the use of a proxy. Take advantage of our connector to garner critical data points and gain insight into security threats.

[→ View full connector details](connectors/iboss.md)

---

### [[Deprecated] vArmour Application Controller via AMA](connectors/varmouracama.md)

**Publisher:** vArmour

**Solution:** [vArmour Application Controller](solutions/varmour-application-controller.md)

**Tables (1):** `CommonSecurityLog`

vArmour reduces operational risk and increases cyber resiliency by visualizing and controlling application relationships across the enterprise. This vArmour connector enables streaming of Application Controller Violation Alerts into Microsoft Sentinel, so you can take advantage of search & correlation, alerting, & threat intelligence enrichment for each log.

[→ View full connector details](connectors/varmouracama.md)

---

### [[Deprecated] vArmour Application Controller via Legacy Agent](connectors/varmourac.md)

**Publisher:** vArmour

**Solution:** [vArmour Application Controller](solutions/varmour-application-controller.md)

**Tables (1):** `CommonSecurityLog`

vArmour reduces operational risk and increases cyber resiliency by visualizing and controlling application relationships across the enterprise. This vArmour connector enables streaming of Application Controller Violation Alerts into Microsoft Sentinel, so you can take advantage of search & correlation, alerting, & threat intelligence enrichment for each log.

[→ View full connector details](connectors/varmourac.md)

---

