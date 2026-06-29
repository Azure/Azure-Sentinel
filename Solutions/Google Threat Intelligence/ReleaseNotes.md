| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.2.3       | 04-06-2026                     | - Added **Data Connector** *GTI Relevance System Alerts* (Azure Function App, Log Ingestion API). <br/>- Added **Parser** *GTIRelevanceSystemAlerts*. <br/>- Added **Analytics Rules**: GTI High Relevance Alerts, GTI High & Critical Priority Alerts, GTI Data Leak Alerts, GTI Initial Access Broker Alerts, GTI Insider Threat Alerts, GTI Relevance System Alerts Incident by Alert ID. <br/>- Added Custom **Connector** manual prerequisite for Playbooks. |
| 3.2.2       | 02-12-2025                     | - Included new Analytics Rules and Hunting Queries to improve detection capabilities and support proactive investigation. <br/>- Filtering threat lists<br/>- Migrating to Upload STIX Objects |
| 3.2.1       | 25-08-2025                     | Fix IoC Stream ingestion bug for results with more than 40 items due to a cursor iteration error. |
| 3.2.0       | 20-05-2025                     | New **Playbook** added *IoC Stream Threat Intelligence*.<br/> Added x-tool header in **Playbook** Customer Connector. |
| 3.1.0       | 29-01-2025                     | New *Threat Intelligence Ingestion* **Playbook** added. |
| 3.0.0       | 05-12-2024                     | Initial Solution Release.                       |
