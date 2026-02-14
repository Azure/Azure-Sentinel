# SOCRadar Alarm Import

Imports SOCRadar XTI platform alarms into Microsoft Sentinel as incidents.

## Features

- Paginated alarm fetching (100 per page)
- Duplicate detection via Sentinel API
- Severity and status mapping
- Optional closed alarm import with classification
- Automatic tagging (SOCRadar, alarm type, sub type)
- Field truncation for large alarms
- Optional audit logging

## Prerequisites

- SOCRadar XTI Platform API Key
- Microsoft Sentinel workspace
- Managed Identity with Sentinel Contributor role

## Deployment

Deploy via the main SOCRadar solution or standalone using the Deploy to Azure button in the main repository.
