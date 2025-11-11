# Netskope Microsoft Sentinel Solution
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