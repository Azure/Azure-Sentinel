# SOCRadar Alarm Import

Imports SOCRadar XTI platform alarms into Microsoft Sentinel as incidents.

Deploying this playbook also provisions the Data Collection Endpoint, the `SOCRadar_Alarms_CL` and `SOCRadarAuditLog_CL` custom log tables, the associated Data Collection Rules, and the role assignments required by the Logic App's managed identity. No separate infrastructure deployment is needed.

## Features

- Paginated alarm fetching (100 per page)
- Duplicate detection via Microsoft Sentinel API
- Severity and status mapping
- Optional closed alarm import with classification
- Automatic tagging (SOCRadar, alarm type, sub type)
- Field truncation for large alarms
- Optional audit logging

## Prerequisites

- SOCRadar XTI Platform API Key
- Microsoft Sentinel workspace
- Managed Identity with Microsoft Sentinel Responder role (default, Contributor optional)

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSOCRadar%2FPlaybooks%2FSOCRadar-Alarm-Import%2Fazuredeploy.json)

You can also install this playbook via **Microsoft Sentinel Content Hub**.
