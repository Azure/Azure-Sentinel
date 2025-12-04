# TacitRed Compromised Credentials for Microsoft Sentinel

## Overview

The **TacitRed Compromised Credentials** solution provides real-time detection and monitoring of compromised user credentials, domain takeovers, and identity-based threats. This solution integrates TacitRed's threat intelligence into Microsoft Sentinel using a CCF (Codeless Connector Framework) data connector.

## What's Included

### Data Connectors: 1
- **TacitRed CCF Connector**: Ingests compromised credential findings from TacitRed API
  - Custom table: `TacitRed_Findings_CL`
  - Polling interval: 6 hours
  - Data retention: Per workspace configuration

### Analytics Rules: 1
- **Repeat Compromise Detection**: Identifies users compromised multiple times within 7 days
  - Severity: High
  - MITRE ATT&CK: T1110 (Brute Force), T1078 (Valid Accounts)
  - Frequency: Hourly
  - Creates incidents with account entity mapping

### Workbooks: 1
- **TacitRed Compromised Credentials**: Comprehensive visualization dashboard
  - Compromise detection timeline
  - Key metrics (total findings, avg confidence, unique users/domains)
  - High-risk users (repeat compromises)
  - Most affected domains
  - Finding types distribution

## Prerequisites

- Microsoft Sentinel workspace
- TacitRed API key (obtain from TacitRed admin console)
- Contributor permissions on the resource group
- Microsoft Sentinel Contributor role

## Deployment

### Option 1: Azure Portal (Recommended)
1. Navigate to Microsoft Sentinel > Content Hub
2. Search for "TacitRed Compromised Credentials"
3. Click **Install**
4. Follow the deployment wizard
5. Enter your TacitRed API key when prompted

### Option 2: ARM Template
```powershell
az deployment group create \
  --resource-group <your-rg> \
  --template-file mainTemplate.json \
  --parameters workspace=<workspace-name> \
               tacitRedApiKey=<your-api-key> \
               deployAnalytics=true \
               deployWorkbooks=true \
               deployConnectors=true
```

## Post-Deployment Configuration

### 1. Verify Data Connector
1. Navigate to **Microsoft Sentinel > Data connectors**
2. Find **TacitRed Compromised Credentials**
3. Verify status shows "Connected"
4. Check for data ingestion:
   ```kql
   TacitRed_Findings_CL
   | where TimeGenerated > ago(1h)
   | take 10
   ```

### 2. Enable Analytics Rule
1. Navigate to **Microsoft Sentinel > Analytics**
2. Find **TacitRed - Repeat Compromise Detection**
3. Verify rule is **Enabled**
4. Customize thresholds if needed

### 3. Access Workbook
1. Navigate to **Microsoft Sentinel > Workbooks**
2. Open **TacitRed Compromised Credentials**
3. Select time range and explore visualizations

## Data Schema

### TacitRed_Findings_CL Table
| Column | Type | Description |
|--------|------|-------------|
| `TimeGenerated` | datetime | Ingestion timestamp |
| `email_s` | string | Compromised email address |
| `domain_s` | string | Associated domain |
| `findingType_s` | string | Type of compromise |
| `confidence_d` | int | Confidence score (0-100) |
| `firstSeen_t` | datetime | First detection time |
| `lastSeen_t` | datetime | Last detection time |
| `source_s` | string | Intelligence source |
| `severity_s` | string | Severity level |
| `status_s` | string | Finding status |

## Sample Queries

### High Confidence Compromises (Last 7 Days)
```kql
TacitRed_Findings_CL
| where TimeGenerated >= ago(7d)
| where confidence_d >= 80
| project TimeGenerated, email_s, domain_s, confidence_d, findingType_s
| order by confidence_d desc
```

### Compromised Users by Domain
```kql
TacitRed_Findings_CL
| where TimeGenerated >= ago(30d)
| summarize CompromisedUsers = dcount(email_s) by domain_s
| order by CompromisedUsers desc
| take 20
```

### Repeat Compromises
```kql
TacitRed_Findings_CL
| where TimeGenerated >= ago(7d)
| summarize CompromiseCount = count() by email_s
| where CompromiseCount >= 2
| order by CompromiseCount desc
```

## Troubleshooting

### No Data Ingestion
1. Verify API key is correct
2. Check Data Collection Rule status
3. Review deployment logs in Azure Portal
4. Verify TacitRed API endpoint is accessible

### Analytics Rule Not Triggering
1. Ensure sufficient data exists (minimum 2 findings per user)
2. Check rule query period (default: 7 days)
3. Verify rule is enabled
4. Review rule execution history

### Workbook Shows No Data
1. Confirm data connector is active
2. Adjust time range parameter
3. Run sample queries to verify data availability

## Support

- **TacitRed Support**: support@tacitred.com
- **Documentation**: https://www.tacitred.com/docs
- **Microsoft Sentinel**: https://docs.microsoft.com/azure/sentinel

## Version History

- **1.0.0** (2025-01-01): Initial release
  - CCF data connector
  - Repeat Compromise analytics rule
  - Compromised Credentials workbook

## License

This solution is provided by TacitRed. Contact TacitRed for licensing information.
