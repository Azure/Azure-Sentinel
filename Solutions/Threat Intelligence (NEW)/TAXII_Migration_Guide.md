# Microsoft Sentinel TAXII Connector Migration Guide

This guide provides step-by-step instructions for migrating from the old TAXII data connector to the new TAXII data connector in Microsoft Sentinel.

## Overview
Both old and new TAXII connectors use the same table (`ThreatIntelligenceIndicator`) for storing threat intelligence data. The source of the data is distinguished by the `SourceSystem` field within the table.

## Migration Steps

### 1. Prepare for Migration
- Document your existing TAXII server URLs and collection IDs
- Note down any custom workbooks or analytics rules that use TAXII data
- Verify you have the necessary permissions (Security Admin or Global Admin)

### 2. Remove the Old TAXII Connector
1. Navigate to Microsoft Sentinel > Data Connectors
2. Find the old TAXII connector in the list
3. Select it and click "Delete" or "Disconnect"
4. Wait for the disconnection to complete

### 3. Install the New TAXII Connector
1. Navigate to Microsoft Sentinel > Data Connectors
2. Search for "TAXII" and select the new TAXII connector
3. Click "Open connector page"
4. Configure the connector with your TAXII server details:
   - TAXII 2.0 or 2.1 API Root URL
   - Collection ID
   - Username/Password (if required)
5. Click "Connect"

### 4. Verify the Migration
1. Check data ingestion in the `ThreatIntelligenceIndicator` table using the following KQL query:
   ```kql
   ThreatIntelligenceIndicator
   | where TimeGenerated > ago(24h)
   | where SourceSystem == "TAXII"
   | summarize Count=count(), LastRecord=max(TimeGenerated)
   | extend Status = iif(LastRecord < ago(2h), "Not Receiving", "Receiving")
   ```
   This query will:
   - Show indicators from the last 24 hours
   - Filter for TAXII-sourced indicators
   - Display the count of indicators and latest record
   - Indicate if data is currently being received (within last 2 hours)

2. For detailed indicator information, use:
   ```kql
   ThreatIntelligenceIndicator
   | where TimeGenerated > ago(24h)
   | where SourceSystem == "TAXII"
   | project TimeGenerated, Description, ThreatType, Activity, ConfidenceScore,
             NetworkIP, NetworkDestinationIP, EmailSourceIpAddress,
             URL, FileHashValue, FileHashType
   ```

3. Test any custom workbooks or analytics rules that use TAXII data

### 5. Post-Migration Checks
- Confirm indicators are being received from your TAXII server
- Validate that your analytics rules are working as expected
- Check that your workbooks are displaying data correctly

## Important Notes
- No data migration is needed as both connectors use the same table
- Existing threat indicators remain in the `ThreatIntelligenceIndicator` table
- There is no downtime for existing indicators during migration

### Understanding the SourceSystem Field
The `SourceSystem` field in the `ThreatIntelligenceIndicator` table identifies the origin of each indicator. Common values include:

- `"TAXII"` - Indicators from the TAXII connector (new)
- `"ThreatIntelligenceTaxii"` - Indicators from the legacy TAXII connector (old)
- `"SecurityGraph"` - Indicators from Microsoft Graph Security API
- `"Azure Sentinel"` - Indicators from other Microsoft Sentinel sources
- `"Microsoft Sentinel"` - Indicators from Microsoft Sentinel internal processes

To filter data by source, use the `SourceSystem` field in your queries:
```kql
// For new TAXII connector data
ThreatIntelligenceIndicator
| where SourceSystem == "TAXII"

// For legacy TAXII connector data
ThreatIntelligenceIndicator
| where SourceSystem == "ThreatIntelligenceTaxii"
```

## Troubleshooting
If you encounter issues:
1. Check the connector's health status
2. Verify TAXII server connectivity
3. Confirm credentials are correct
4. Review connector logs for any error messages

## Additional Resources
- [Microsoft Sentinel Documentation](https://docs.microsoft.com/azure/sentinel)
- [TAXII Connector Documentation](https://docs.microsoft.com/azure/sentinel/connect-threat-intelligence-taxii)