# RSAIDPlus_AdminLogs_Connector

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | RSA Support Team |
| **Support Tier** | Partner |
| **Support Link** | [https://community.rsa.com/](https://community.rsa.com/) |
| **Categories** | domains,verticals |
| **First Published** | 2025-10-14 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [RSA ID Plus Admin Logs Connector](../connectors/rsaidplus-adminglogs-connector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`RSAIDPlus_AdminLogs_CL`](../tables/rsaidplus-adminlogs-cl.md) | [RSA ID Plus Admin Logs Connector](../connectors/rsaidplus-adminglogs-connector.md) | Analytics |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [RSA ID Plus - Locked Administrator Account Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector/Analytic%20Rules/RSAIDPlus_AdminLockoutAlert.yaml) | Medium | Impact, CredentialAccess | [`RSAIDPlus_AdminLogs_CL`](../tables/rsaidplus-adminlogs-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SendEmailonRSAIDPlusAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector/Playbooks/SendEmailOnRSAIDPlusAlert/azuredeploy.json) | Sends an email notification when an RSA ID Plus analytic rule triggers. This playbook can be linked ... | - |

## Additional Documentation

> 📄 *Source: [RSAIDPlus_AdminLogs_Connector/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector/README.md)*

# RSA ID Plus Admin Logs Connector
## Overview
The RSA ID Plus Admin Logs Data Connector enables seamless integration between RSA ID Plus and Microsoft Sentinel.
This connector ingests Admin Events logs from RSA ID Plus Cloud Administration Console using the RSA Admin API and stores them securely in your Azure Log Analytics (ALA) workspace.
These logs can then be used for monitoring, analysis, and threat detection within Microsoft Sentinel.

## Features
### Log Ingestion
- Collect RSA ID Plus Admin Events
- Provides visibility into administrative actions and potential security incidents. 

### Analytic Rule
- This package includes an analytic rule that detects when an Administrator is locked out. 
- When triggered, this rule generates an alert in Sentinel for further investigation. 
- This rule serves as an example - custom analytic rules can be created to detect other specific admin activities or specific patterns as needed. 

### Playbook (Automation)
- A Logic App Playbook is included in this package. 
- The playbook can be configured to send an email notification whenever an alert (e.g. admin account lockout) is generated. 
- By default, this Playbook is not linked to the analytic rule. However, customers can manually link it to any rule according to their operational requirements. 

## Deployment
1. Deploy the connector through Azure Portal under your Microsoft Sentinel instance. 
2. Configure the connector (Instructions are provided in the connector UI).
3. Verify that the logs are being ingested into your Log Analytics workspace. 
4. Optionally, enable the analytic rule for admin account lockout detections. 
5. Optionally, link the provided Playbook to an analytic rule to enable automated email alerts.

## Customization
- Modify or create new analytic rules in Sentinel to detect different admin activities.
- Update or create new Playbook to include actions such as Teams notification, ServiceNow ticket creation, or integration with other workflows.

## Summary
This connector provides a ready-to-use integration between RSA ID Plus Cloud Administration Console Events and Microsoft Sentinel offering: 
- Simplified log ingestion
- Predefined security analytics
- Optional automation through Playbooks.

Together, these components help security teams gain visibility, detect threats and respond quickly to critical admin-level activities.

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     |
|-------------|--------------------------------|----------------------------------------|
| 3.0.1		  | 23-10-2025					   | Updating offerId 						|
| 3.0.0       | 14-10-2025                     | Initial Solution Release.              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
