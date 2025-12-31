# Netskopev2

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Netskope |
| **Support Tier** | Partner |
| **Support Link** | [https://www.netskope.com/services#support](https://www.netskope.com/services#support) |
| **Categories** | domains |
| **First Published** | 2024-03-18 |
| **Last Updated** | 2024-03-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [Netskope Alerts and Events](../connectors/netskopealertsevents.md)
- [Netskope Data Connector](../connectors/netskopedataconnector.md)
- [Netskope Web Transactions Data Connector](../connectors/netskopewebtransactionsdataconnector.md)

## Tables Reference

This solution uses **32 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`NetskopeAlerts_CL`](../tables/netskopealerts-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | Workbooks |
| [`NetskopeEventsApplication_CL`](../tables/netskopeeventsapplication-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | Workbooks |
| [`NetskopeEventsAudit_CL`](../tables/netskopeeventsaudit-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | - |
| [`NetskopeEventsConnection_CL`](../tables/netskopeeventsconnection-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | - |
| [`NetskopeEventsDLP_CL`](../tables/netskopeeventsdlp-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | - |
| [`NetskopeEventsEndpoint_CL`](../tables/netskopeeventsendpoint-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | - |
| [`NetskopeEventsInfrastructure_CL`](../tables/netskopeeventsinfrastructure-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | - |
| [`NetskopeEventsNetwork_CL`](../tables/netskopeeventsnetwork-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | - |
| [`NetskopeEventsPage_CL`](../tables/netskopeeventspage-cl.md) | [Netskope Alerts and Events](../connectors/netskopealertsevents.md) | - |
| [`NetskopeWebTransactions_CL`](../tables/netskopewebtransactions-cl.md) | - | Workbooks |
| [`NetskopeWebtxData_CL`](../tables/netskopewebtxdata-cl.md) | [Netskope Web Transactions Data Connector](../connectors/netskopewebtransactionsdataconnector.md) | Workbooks |
| [`NetskopeWebtxErrors_CL`](../tables/netskopewebtxerrors-cl.md) | [Netskope Web Transactions Data Connector](../connectors/netskopewebtransactionsdataconnector.md) | Analytics |
| [`Netskope_Alerts_CL`](../tables/netskope-alerts-cl.md) | - | Workbooks |
| [`Netskope_Events_CL`](../tables/netskope-events-cl.md) | - | Workbooks |
| [`Netskope_WebTX_CL`](../tables/netskope-webtx-cl.md) | - | Workbooks |
| [`Netskope_WebTx_metrics_CL`](../tables/netskope-webtx-metrics-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertscompromisedcredentialdata_CL`](../tables/alertscompromisedcredentialdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertsctepdata_CL`](../tables/alertsctepdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertsdlpdata_CL`](../tables/alertsdlpdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertsmalsitedata_CL`](../tables/alertsmalsitedata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertsmalwaredata_CL`](../tables/alertsmalwaredata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertspolicydata_CL`](../tables/alertspolicydata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertsquarantinedata_CL`](../tables/alertsquarantinedata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertsremediationdata_CL`](../tables/alertsremediationdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertssecurityassessmentdata_CL`](../tables/alertssecurityassessmentdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`alertsubadata_CL`](../tables/alertsubadata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`eventsapplicationdata_CL`](../tables/eventsapplicationdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | Workbooks |
| [`eventsauditdata_CL`](../tables/eventsauditdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`eventsconnectiondata_CL`](../tables/eventsconnectiondata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`eventsincidentdata_CL`](../tables/eventsincidentdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`eventsnetworkdata_CL`](../tables/eventsnetworkdata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |
| [`eventspagedata_CL`](../tables/eventspagedata-cl.md) | [Netskope Data Connector](../connectors/netskopedataconnector.md) | - |

## Content Items

This solution includes **37 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 30 |
| Workbooks | 4 |
| Playbooks | 2 |
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Netskope - WebTransaction Error Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Analytic%20Rules/NetskopeWebTxErrors.yaml) | Medium | Execution | [`NetskopeWebtxErrors_CL`](../tables/netskopewebtxerrors-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [NetskopeCCFWebtxDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Workbooks/NetskopeCCFWebtxDashboard.json) | [`NetskopeWebTransactions_CL`](../tables/netskopewebtransactions-cl.md) |
| [NetskopeCCPDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Workbooks/NetskopeCCPDashboard.json) | [`NetskopeAlerts_CL`](../tables/netskopealerts-cl.md)<br>[`NetskopeEventsApplication_CL`](../tables/netskopeeventsapplication-cl.md) |
| [NetskopeCEDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Workbooks/NetskopeCEDashboard.json) | [`Netskope_Alerts_CL`](../tables/netskope-alerts-cl.md)<br>[`Netskope_Events_CL`](../tables/netskope-events-cl.md)<br>[`Netskope_WebTX_CL`](../tables/netskope-webtx-cl.md) |
| [NetskopeDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Workbooks/NetskopeDashboard.json) | [`NetskopeWebtxData_CL`](../tables/netskopewebtxdata-cl.md)<br>[`eventsapplicationdata_CL`](../tables/eventsapplicationdata-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [NetskopeDataConnectorsTriggerSync](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Playbooks/NetskopeDataConnectorsTriggerSync/azuredeploy.json) | Playbook to sync timer trigger of all Netskope data connectors. | - |
| [NetskopeWebTxErrorEmail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Playbooks/NetskopeWebTxErrorEmail/azuredeploy.json) | This playbook sends email when Netskope Web Transaction data connector error is detected. | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AlertsCompromisedCredential](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsCompromisedCredential.yaml) | - | - |
| [AlertsCtep](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsCtep.yaml) | - | - |
| [AlertsDLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsDLP.yaml) | - | - |
| [AlertsMalsite](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsMalsite.yaml) | - | - |
| [AlertsMalware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsMalware.yaml) | - | - |
| [AlertsPolicy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsPolicy.yaml) | - | - |
| [AlertsQuarantine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsQuarantine.yaml) | - | - |
| [AlertsRemediation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsRemediation.yaml) | - | - |
| [AlertsSecurityAssessment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsSecurityAssessment.yaml) | - | - |
| [AlertsUba](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/AlertsUba.yaml) | - | - |
| [EventIncident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/EventIncident.yaml) | - | - |
| [EventsApplication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/EventsApplication.yaml) | - | - |
| [EventsAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/EventsAudit.yaml) | - | - |
| [EventsConnection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/EventsConnection.yaml) | - | - |
| [EventsNetwork](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/EventsNetwork.yaml) | - | - |
| [EventsPage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/EventsPage.yaml) | - | - |
| [NetskopeAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeAlerts.yaml) | - | - |
| [NetskopeCCFWebTransactions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeCCFWebTransactions.yaml) | - | - |
| [NetskopeCEAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeCEAlerts.yaml) | - | - |
| [NetskopeCEEventsApplication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeCEEventsApplication.yaml) | - | - |
| [NetskopeCEWebTransactions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeCEWebTransactions.yaml) | - | - |
| [NetskopeEventsApplication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeEventsApplication.yaml) | - | - |
| [NetskopeEventsAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeEventsAudit.yaml) | - | - |
| [NetskopeEventsConnection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeEventsConnection.yaml) | - | - |
| [NetskopeEventsDLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeEventsDLP.yaml) | - | - |
| [NetskopeEventsEndpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeEventsEndpoint.yaml) | - | - |
| [NetskopeEventsInfrastructure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeEventsInfrastructure.yaml) | - | - |
| [NetskopeEventsNetwork](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeEventsNetwork.yaml) | - | - |
| [NetskopeEventsPage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeEventsPage.yaml) | - | - |
| [NetskopeWebTransactions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Parsers/NetskopeWebTransactions.yaml) | - | - |

## Additional Documentation

> 📄 *Source: [Netskopev2/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/README.md)*

## Quick Links
- **Alerts & Events (CCF):** [Sending Alerts and Events to Microsoft Sentinel using the Codeless Connector Platform](https://community.netskope.com/discussions-37/sending-alerts-and-events-to-microsoft-sentinel-using-the-codeless-connector-platform-6910)
- **Web Transactions (CCF):** [Integration: Web Transactions from Netskope Log Streaming to Microsoft Sentinel](https://community.netskope.com/discussions-37/integration-web-transactions-from-netskope-log-streaming-to-microsoft-sentinel-7646)
- **Netskope Log Streaming Connector Documentation:** [View Documentation](https://docs.netskope.com/en/log-streaming/)



## Overview
The **Netskope Microsoft Sentinel Solution** integrates Netskope logs (events, alerts, and WebTransactions) into **Microsoft Sentinel** for centralized monitoring and investigation.  

> **Note:** Work to update this solution is currently **in progress**. For any questions, please contact **tech-alliances@netskope.com**.

---

## Contents

### Data Connectors
1. **NetskopeAlertsEvents_RestAPI_CCP** *(Recommended)*  
   Fetches alerts and events from Netskope using Microsoft's Codeless Connector Framework.
2. **NetskopeDataConnector** *(Deprecated)*  
   Azure Functions–based data connector to fetch alerts and events from Netskope.
3. **NetskopeWebTransactionsDataConnector** *(Deprecated)*  
   Docker–based data connector to fetch Netskope WebTx logs.

> **Note:** Installation steps for each data connector are available on their respective **UI pages** within Microsoft Sentinel.

### Workbook
> **Note:** The workbook is only compatible with the **Azure Functions–based data connector** data, and **not** compatible with **NetskopeAlertsEvents_RestAPI_CCP** or **Netskope CE** data.

### Parsers
> **Note:** The parsers are only compatible with the **Azure Functions–based data connector** data, and **not** compatible with **NetskopeAlertsEvents_RestAPI_CCP** or **Netskope CE** data.

---

## Support
- [tech-alliances@netskope.com](mailto:tech-alliances@netskope.com)
- [Netskope Documentation](https://docs.netskope.com)
- [Microsoft Sentinel Documentation](https://learn.microsoft.com/azure/sentinel)

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.2       | 31-10-2025                     | Added Dropdown in CCF UI page for data ingestion |
| 3.1.1       | 15-10-2025                     | Added CCF WebTx Parser and Dashboard      |
| 3.1.0       | 12-08-2025                     | Added **Parsers** and **Dashboards** for **CCP** and **CE** Data. |
| 3.0.3       | 08-04-2025                     | Updated index value of api endpoint in **CCP Data Connector** poller files. |
| 3.0.2       | 30-05-2024                     | Updated python packages of Netskope **Data Connector**. |
| 3.0.1       | 03-05-2024                     | Repackaged for **Parser** issue fix on reinstall.                    |
| 3.0.0       | 03-04-2024                     | Initial Solution Release.                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
