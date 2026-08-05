# Netskope Web Transactions Solution for Microsoft Sentinel

## Overview
This solution enables ingestion of Netskope Web Transaction logs into Microsoft Sentinel for security monitoring, threat detection, and compliance analysis.

## Contents

### Data Connectors
- **NetskopeWebTxConnector** - Codeless Connector Platform (CCP) connector using Azure Blob Storage and Event Grid

### Workbooks
- **Netskope Web Transactions** - Comprehensive visualization including:
  - User Activity Analysis
  - Application & Category Usage
  - Geographic Traffic Analysis
  - HTTP Methods & Status Codes
  - Client Information (OS, browser, device)
  - Threat Protection (malware detections, severity, engine results)
  - Endpoint Posture (device classification, OS family, Netskope client versions)
  - Process Activity (top processes and parent processes)
  - Identity & Authentication (authenticated users, authorization groups)
  - Action Analysis (actions, action reasons, remote destination country)
  - SSL Errors & Bypass Events
  - Data Quality Monitoring

### Analytics Rules (10 Rules)
1. **Impossible Travel Detection** - Users accessing from multiple countries within 1 hour
2. **Excessive Downloads Detection** - Spike vs 7-day baseline analysis
3. **Unsanctioned/Risky Cloud App Access** - Shadow IT detection
4. **New Risky App vs Baseline** - First-seen risky applications
5. **Large Data Upload (DLP)** - Potential data exfiltration
6. **Policy Violations** - Repeated or critical policy blocks
7. **Anomalous User Behavior** - High volume from unmanaged devices
8. **Personal Cloud Storage Usage** - Shadow IT storage apps
9. **Suspicious Network Context** - Unusual IPs/Geo/Ports
10. **Data Movement Tracking** - Upload/Download monitoring

## Prerequisites
- Microsoft Sentinel workspace
- Azure Blob Storage account with Netskope Web Transaction logs
- Event Grid System Topic on the storage account
- Appropriate RBAC permissions

## Deployment
1. Deploy the Data Connector ARM template
2. Configure blob container settings
3. Deploy Analytics Rules
4. Import the Workbook

## Log Table
`NetskopeWebTransactions_CL` — ingested via the connector's Data Collection Rule (DCR) transform. A Kusto Function parser, **NetskopeWebtx**, is included to project the full Web Transaction field set with friendly names.

## Version
3.0.1
