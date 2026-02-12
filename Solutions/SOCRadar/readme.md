# SOCRadar for Microsoft Sentinel

Bidirectional integration between SOCRadar XTI Platform and Microsoft Sentinel.

## Overview

This solution provides automated alarm import from SOCRadar to Microsoft Sentinel and bidirectional sync for closed incidents.

## Components

### Playbooks

- **SOCRadar-Alarm-Import** - Imports SOCRadar alarms as Sentinel incidents with severity mapping, deduplication, and optional audit logging
- **SOCRadar-Alarm-Sync** - Syncs closed Sentinel incidents back to SOCRadar with classification mapping

### Workbook

- **SOCRadar Integration Dashboard** - Analytics dashboard with alarm severity distribution, timeline, top alarm types, and audit log monitoring

### Hunting Queries

- **SOCRadar Alarm Overview** - Summary of alarms by severity and type
- **SOCRadar Critical Alarms** - High/Critical alarms not yet closed
- **SOCRadar Alarm Trends** - Week-over-week alarm trend analysis
- **SOCRadar Incident Correlation** - Match alarms with Sentinel incidents
- **SOCRadar Audit Analysis** - Import/sync operation monitoring

## Prerequisites

- SOCRadar XTI Platform account with API access
- Microsoft Sentinel workspace
- Managed Identity permissions (auto-assigned during deployment)

## Deployment

Click "Deploy to Azure" from the Content Hub solution page.

## Post-Deployment

1. Both Logic Apps deploy with Managed Identity - no manual authorization needed
2. Role assignments are created automatically
3. First run starts after 3-minute delay (Azure AD propagation)
4. Default polling: every 5 minutes

## Support

- Email: integration@socradar.io
- Documentation: https://docs.socradar.io
