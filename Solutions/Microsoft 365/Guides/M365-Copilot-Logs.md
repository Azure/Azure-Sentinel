# Microsoft 365 Copilot Logs Integration Guide

This guide explains how to ingest and analyze Microsoft 365 Copilot logs in Microsoft Sentinel using the existing Microsoft 365 data connector.

## Overview

Microsoft 365 Copilot audit events are available through the Office 365 Management Activity API and can be ingested into Microsoft Sentinel using the existing **Microsoft 365** data connector. No additional data connector is required.

## Prerequisites

- Microsoft 365 E5 or Copilot for Microsoft 365 license
- Microsoft Sentinel workspace with Microsoft 365 data connector enabled
- Appropriate permissions to configure data connectors and access audit logs

## Supported Copilot Events

The following Microsoft 365 Copilot events are available for ingestion:

### Copilot Activity Events
- **CopilotInteraction**: User interactions with Copilot across Microsoft 365 applications
- **CopilotResponse**: Copilot response generation and delivery
- **CopilotQuery**: User queries submitted to Copilot
- **CopilotContentAccess**: Content accessed by Copilot for response generation

### Available Workloads
- **Microsoft Teams**: Copilot interactions in Teams chat and meetings
- **Outlook**: Copilot assistance with email composition and summarization
- **Word**: Document assistance and content generation
- **PowerPoint**: Presentation creation and enhancement
- **Excel**: Data analysis and formula assistance
- **OneNote**: Note-taking and content organization assistance

## Configuration Steps

### 1. Enable Microsoft 365 Data Connector

If you haven't already enabled the Microsoft 365 data connector:

1. In Microsoft Sentinel, go to **Data connectors**
2. Search for "Microsoft 365" and select the connector
3. Click **Open connector page**
4. Click **Connect** and follow the authentication prompts
5. Select the following data types:
   - **Exchange** (for Outlook Copilot events)
   - **SharePoint** (for document-related Copilot events)
   - **Teams** (for Teams Copilot events)

### 2. Verify Copilot Events Ingestion

After configuration, verify that Copilot events are being ingested:

```kql
// Check for general Copilot activity
OfficeActivity
| where Operation contains "Copilot"
| take 10

// Check specific Copilot workloads
OfficeActivity
| where OfficeWorkload in ("MicrosoftTeams", "Exchange", "SharePoint", "OneDrive")
| where Operation contains "Copilot" or ExtendedProperties contains "Copilot"
| summarize Count = count() by OfficeWorkload, Operation
| sort by Count desc
```

## Sample Queries

### Monitor Copilot Usage Patterns

```kql
// Copilot usage by workload over time
OfficeActivity
| where Operation contains "Copilot"
| summarize UsageCount = count() by bin(TimeGenerated, 1h), OfficeWorkload
| render timechart
```

### Analyze Copilot User Activity

```kql
// Top users interacting with Copilot
OfficeActivity
| where Operation contains "Copilot"
| summarize CopilotInteractions = count() by UserId, OfficeWorkload
| top 20 by CopilotInteractions
```

### Detect Unusual Copilot Activity

```kql
// Detect high-volume Copilot usage that might indicate automation
let threshold = 100;
OfficeActivity
| where Operation contains "Copilot"
| where TimeGenerated > ago(1h)
| summarize CopilotQueries = count() by UserId
| where CopilotQueries > threshold
| join kind=inner (
    OfficeActivity
    | where Operation contains "Copilot"
    | where TimeGenerated > ago(1h)
) on UserId
| project TimeGenerated, UserId, Operation, OfficeWorkload, CopilotQueries
| sort by CopilotQueries desc
```

### Track Copilot Content Access

```kql
// Monitor what content Copilot is accessing
OfficeActivity
| where Operation contains "Copilot" and Operation contains "Access"
| extend FileName = tostring(OfficeObjectId)
| summarize AccessCount = count() by FileName, UserId, OfficeWorkload
| top 50 by AccessCount
```

## Data Schema

Copilot events in the `OfficeActivity` table include these key fields:

| Field | Description | Example Values |
|-------|-------------|----------------|
| Operation | The Copilot operation performed | "CopilotInteraction", "CopilotQuery", "CopilotResponse" |
| OfficeWorkload | The Microsoft 365 application | "MicrosoftTeams", "Exchange", "SharePoint" |
| UserId | User performing the action | "user@contoso.com" |
| ClientIP | IP address of the client | "192.168.1.100" |
| UserAgent | Client application information | "Mozilla/5.0..." |
| ExtendedProperties | Additional Copilot-specific data | JSON with query text, response metadata |

## Workbook Integration

To visualize Copilot usage data:

1. Go to **Workbooks** in Microsoft Sentinel
2. Create a new workbook or modify the existing "Office 365" workbook
3. Add queries for Copilot metrics:
   - Usage trends by application
   - Top users and departments
   - Content access patterns
   - Security insights

## Analytic Rules

Consider creating analytic rules for:

- **Excessive Copilot Usage**: Detect users with unusually high Copilot interaction volumes
- **Suspicious Content Access**: Monitor access to sensitive documents through Copilot
- **Off-Hours Activity**: Detect Copilot usage during unusual hours
- **Failed Authentication**: Monitor failed attempts to access Copilot services

## Troubleshooting

### No Copilot Events Appearing

1. **Verify Licensing**: Ensure users have appropriate Copilot licenses
2. **Check Permissions**: Verify admin permissions for audit log access
3. **Audit Log Retention**: Confirm audit logs are being retained (Admin Center > Compliance > Audit)
4. **Connector Configuration**: Ensure all required workloads are enabled in the data connector

### Filtering Out Noise

```kql
// Filter out automated/system Copilot activities
OfficeActivity
| where Operation contains "Copilot"
| where UserType == "Regular"  // Exclude service accounts
| where UserId !contains "system"
| where UserId !contains "service"
```

## Additional Resources

- [Microsoft 365 Audit Log Schema](https://docs.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema)
- [Microsoft Sentinel Microsoft 365 Data Connector Documentation](https://docs.microsoft.com/en-us/azure/sentinel/connect-office-365)
- [Microsoft 365 Copilot Security and Privacy](https://docs.microsoft.com/en-us/microsoft-365-copilot/security)

## Support

For issues with Copilot log ingestion:
1. Check the Microsoft 365 data connector status
2. Verify audit log configuration in Microsoft 365 Admin Center
3. Contact support through the Azure portal