# Recorded Future Alerts

More information about Recorded Future Intelligence Solution for Microsoft Sentinel can be found in the main [readme](../readme.md).

## RecordedFuture-Alert-Importer
Type: Alerting\
Included in Recorded Future Intelligence Solution: Yes\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md#connectors-authorization) section. 

Retrieves Alerts and stores them in a custom log in the Log Analytic Workspace. More information on [Alerts](https://support.recordedfuture.com/hc/en-us/articles/115002151327-Setting-up-Event-Alerts) (requires login)

The Alert importer playbook also creates incidents when receiving alerts. Its possible to turn off incident generation by setting the logic app parameter create_incident to false

![](../Images/2023-08-09-18-05-46.png)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FAlerts%2FRecordedFuture-Alert-Importer%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FAlerts%2FRecordedFuture-Alert-Importer%2Fazuredeploy.json)


## RecordedFuture-Playbook-Alert-Importer
Type: Alerting\
Included in Recorded Future Intelligence Solution: Yes\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](#connectors-authorization) section. 

Retrieves Playbook Alerts and stores them in a custom log in the Log Analytic Workspace. More information on [Playbook Alerts](https://support.recordedfuture.com/hc/en-us/articles/13152506878739-Playbook-Alerting-Rules-) (requires login)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FAlerts%2FRecordedFuture-Playbook-Alert-Importer%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FAlerts%2FRecordedFuture-Playbook-Alert-Importer%2Fazuredeploy.json)

