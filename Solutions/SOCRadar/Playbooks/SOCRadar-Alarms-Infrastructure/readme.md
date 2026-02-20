# SOCRadar Alarms Infrastructure

Creates the Log Analytics custom table and Data Collection Rule for storing SOCRadar alarm data.

## Resources Created

- **Data Collection Endpoint** (SOCRadar-DCE)
- **Custom Table** (SOCRadar_Alarms_CL) with alarm fields
- **Data Collection Rule** (SOCRadar-Alarms-DCR)

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| WorkspaceName | Log Analytics Workspace Name | Required |
| TableRetentionDays | Data retention (30-730 days) | 90 |

## Deploy

Deploy this before enabling the Alarms Table feature in the Import playbook.
