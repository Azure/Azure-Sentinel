# RecordedFuture - Ukraine Detection (IPs and Domains connnncted to Ukraine Russia conflict)
author: Oskar Börjesson, Recorded Future

These playbook leverage the Recorded Future API to automate the import of the Recorded Future Risklists with [Ukraine Rusian Conflict riskt lists](https://support.recordedfuture.com/hc/en-us/articles/4484981411475-Resource-Center-on-the-Ukraine-Conflict), as tiIndicators, into the ThreatIntelligenceIndicator table, for detection (alerting) purposes in Azure Sentinel.  For additional information please visit [Recorded Future](https://www.recordedfuture.com/integrations/azure/).

# Dependencies
These playbooks use the ThreatIntelligenceIndicator table in Microsoft Graph Security.  Hence a successful deployment requires both Microsoft Graph Security, as well as Azure Sentinel, to enable the ThreatIntelligenceIndicator table.  In addition, this playbook uses a managed identity to access the API. You will need to add the playbook to the subscriptions or management group with Security Reader Role.

# Installation order
Due to internal Microsoft Logic Apps dependencies, you must deploy the first the playbook, **RecordedFuture_Ukraine_Detection_ImportToSentinel**, _before_ the indicatorprocessor playbook, **RecordedFuture_Ukraine_Detection_IndicatorProcessor**.


Links to deploy the RecordedFuture_Ukraine_Detection_ImportToSentinel playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_Ukraine_Detection%2FRecordedFuture_Ukraine_Detection_ImportToSentinel.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_Ukraine_Detection%2FRecordedFuture_Ukraine_Detection_ImportToSentinel.json)

Links to deploy the RecordedFuture_Ukraine_Detection_IndicatorProcessor playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_Ukraine_Detection%2FRecordedFuture_Ukraine_Detection_IndicatorProcessor.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_Ukraine_Detection%2FRecordedFuture_Ukraine_Detection_IndicatorProcessor.json)