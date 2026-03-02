# Versasec CMS Data Connector

<img src="https://versasec.com/wp-content/uploads/2025/09/versasec-logo.png" alt="drawing" width="20%"/><br>

This solution ingests Versasec CMS system logs into Microsoft Sentinel using a REST API poller (CCF).

### Authentication methods this connector supports

* Api Key authentication (X-VSECCMS-AUTHTICKET)

### Configurations steps
Users will be required to provide the **Management URL**, **API Base Path** and **API Token** when configuring the connector.


## Actions supported by the connector

The connector supports ingesting the following log types from Versasec CMS:
* **System Logs** (Stored in table `VersasecCmsSysLogs_CL`)
* **Error Logs** (Stored in table `VersasecCmsErrorLogs_CL`)

