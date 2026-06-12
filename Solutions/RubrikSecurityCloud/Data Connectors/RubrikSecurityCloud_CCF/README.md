# Rubrik Security Cloud Backup Status Connector for Microsoft Sentinel

A production-ready Microsoft Sentinel data connector that integrates Rubrik Security Cloud (RSC) backup and compliance data with security events, enabling security teams to correlate backup health with security incidents and detect ransomware indicators through backup anomalies.

## 🎯 Overview

The **Rubrik Security Cloud Backup Status connector** is built using **Microsoft's Codeless Connector Framework (CCF)** and collects comprehensive backup and compliance data for Azure VMs from RSC's GraphQL API, ingesting 49 attributes per VM including compliance status, snapshot counts, storage metrics, SLA assignments, and data reduction statistics into the `RubrikProtectionStatus_CL` table in Microsoft Sentinel. This enables security teams to correlate backup health with Sentinel security alerts and incidents through correlation queries that join security events with backup status based on asset identifiers, allowing them to identify potential ransomware indicators through backup anomalies such as sudden compliance failures, missing snapshots, unusual storage consumption patterns, or failed backup jobs that coincide with suspicious security events. By automatically correlating backup telemetry with security data, analysts can quickly determine if a compromised asset has recent, clean backups available for recovery, assess the blast radius of an attack, and detect sophisticated attack patterns that specifically target backup infrastructure to prevent recovery.

## ✨ Key Features

### Data Collection
- **Comprehensive VM Attributes**: 49+ backup and compliance fields per Azure VM
- **Real-time Compliance Monitoring**: Track SLA domain compliance status
- **Snapshot Analytics**: Counts, timestamps, and storage metrics
- **Storage Efficiency**: Data reduction ratios and storage consumption
- **Customizable Polling**: Configurable data collection intervals

### Security Correlation
- **Security Alert Integration**: Join backup data with SecurityAlert events
- **Incident Correlation**: Identify compromised assets with backup issues
- **Ransomware Detection**: Detect backup anomalies coinciding with security events
- **Recovery Readiness**: Quickly assess if clean backups exist for compromised assets
- **Attack Pattern Detection**: Identify attacks targeting backup infrastructure

### Built on Microsoft CCF
- **Native Sentinel Integration**: Appears as a standard data connector in Sentinel UI
- **OAuth2 Authentication**: Secure service account authentication with RSC
- **Automated Deployment**: ARM template-based infrastructure provisioning
- **UI-Driven Configuration**: Configure credentials through Sentinel portal
- **Health Monitoring**: Built-in connector health checks

## 📋 Prerequisites

### Rubrik Security Cloud
- Active RSC subscription
- Service account with read permissions for:
  - Snappable objects (VMs, databases, filesets)
  - SLA domains and policies
  - Cluster information
  - Snapshot and backup data
- RSC URL (e.g., `https://your-org.my.rubrik.com`)
- Client ID and Client Secret from service account

### Microsoft Azure
- Microsoft Sentinel workspace
- Log Analytics workspace connected to Sentinel
- Contributor permissions on the resource group
- Azure subscription with sufficient quota

## 🚀 Quick Start

### 1. Create RSC Service Account

1. Navigate to RSC Console: `https://your-org.my.rubrik.com`
2. Go to **Settings → Users & Roles → Service Accounts**
3. Click **Add Service Account**
4. Configure:
   - **Name**: `Sentinel-Backup-Monitor`
   - **Role**: `Read-Only Admin` or `Viewer`
5. Download the JSON credentials file
6. Note the `client_id` and `client_secret` values

### 2. Deploy the Connector

#### Option A: Azure Portal (Recommended for Production)

1. Navigate to **Microsoft Sentinel → Data connectors**
2. Search for "Rubrik Security Cloud Backup Status"
3. Click **Open connector page**
4. Fill in the configuration:
   - **RSC URL**: `https://your-org.my.rubrik.com`
   - **Client ID**: From service account credentials
   - **Client Secret**: From service account credentials
5. Click **Connect**

#### Option B: PowerShell Deployment (For Testing/POC)

```powershell
# Clean up any existing deployment
pwsh -File cleanup-rsc-connector.ps1

# Deploy the connector
New-AzResourceGroupDeployment `
    -ResourceGroupName 'your-resource-group' `
    -TemplateFile 'rsc-complete-arm-template.json' `
    -workspace 'your-workspace-name' `
    -workspace-location 'West US 2' `
    -RSCUrl 'https://your-org.my.rubrik.com' `
    -ClientId 'client|your-client-id' `
    -ClientSecret 'your-client-secret' `
    -Verbose
```

### 3. Verify Data Ingestion

Wait 5-10 minutes for initial data collection, then run:

```kql
RubrikProtectionStatus_CL
| where TimeGenerated > ago(1h)
| take 10
```

## 📊 Data Schema

The connector creates the `RubrikProtectionStatus_CL` custom table with 52 columns:

| Category | Fields |
|----------|--------|
| **Identity** | AssetId, AssetName, ObjectType, ObjectState, Fid, OrgId, OrgName |
| **Protection** | ProtectionStatus, ComplianceStatus, ArchivalComplianceStatus, ReplicationComplianceStatus |
| **Snapshots** | LastSnapshot, LatestArchivalSnapshot, LatestReplicationSnapshot, TotalSnapshots, LocalSnapshots, ArchiveSnapshots, ReplicaSnapshots, MissedSnapshots |
| **Storage** | LocalStorage, ArchiveStorage, ReplicaStorage, LogicalBytes, PhysicalBytes, UsedBytes, TransferredBytes |
| **Efficiency** | DataReduction, LogicalDataReduction, LocalEffectiveStorage |
| **SLA/Cluster** | SlaDomainName, ClusterName, Location, WorkloadOrgName |
| **Timestamps** | TimeGenerated, ProtectedOn, PullTime, LastSnapshot |

See [RSC-README.md](RSC-README.md) for complete schema documentation.

## 🔍 Sample Queries

### Basic Compliance Monitoring
```kql
RubrikProtectionStatus_CL
| where ComplianceStatus != "IN_COMPLIANCE"
| summarize count() by SlaDomainName, ComplianceStatus
| order by count_ desc
```

### Security Alert Correlation
```kql
SecurityAlert
| where TimeGenerated > ago(7d)
| extend HostEntities = parse_json(Entities)
| mv-expand Entity = HostEntities
| where Entity.Type == "host"
| extend HostName = tostring(Entity.HostName)
| join kind=leftouter (
    RubrikProtectionStatus_CL
    | where TimeGenerated > ago(1d)
    | summarize arg_max(TimeGenerated, *) by AssetName
) on $left.HostName == $right.AssetName
| where isnotempty(ComplianceStatus)
| project 
    AlertTime = TimeGenerated,
    AlertName,
    AlertSeverity,
    HostName,
    ComplianceStatus,
    LastSnapshot,
    MissedSnapshots
```

### Ransomware Risk Assessment
```kql
SecurityAlert
| where TimeGenerated > ago(24h)
| where AlertSeverity in ("High", "Medium")
| extend HostName = tostring(parse_json(Entities)[0].HostName)
| join kind=inner (
    RubrikProtectionStatus_CL
    | where ComplianceStatus != "IN_COMPLIANCE" or MissedSnapshots > 3
) on $left.HostName == $right.AssetName
| project 
    AlertTime = TimeGenerated,
    AlertName,
    HostName,
    ComplianceStatus,
    MissedSnapshots,
    LastSnapshot,
    RiskLevel = "CRITICAL - Compromised asset with backup issues"
```

## 📁 Repository Structure

```
├── rsc-complete-arm-template.json          # Complete POC ARM template (recommended for testing)
├── rsc-ccf-solution-proper.json            # Production Solution template (for Sentinel UI)
├── cleanup-rsc-connector.ps1               # Cleanup script for redeployment
├── RSC-README.md                           # Detailed RSC connector documentation
├── RSC-TESTING-GUIDE.md                    # Testing and validation guide
├── DEPLOYMENT-GUIDE.md                     # Step-by-step deployment instructions
│
├── KQL Queries
│   ├── security-alerts-with-rubrik-correlation.kql    # Security alert correlation
│   ├── incident-backup-correlation-queries.kql        # Incident correlation queries
│   ├── hunting-queries-security-backup.kql            # Threat hunting queries
│   ├── analytics-rules-security-backup.kql            # Detection rules
│   ├── workbook-security-backup-dashboard.kql         # Workbook visualizations
│   └── rsc-sample-queries.kql                         # Basic RSC queries
│
├── PowerShell Scripts
│   ├── deploy-rsc-ccf-solution.ps1        # Deploy Solution template
│   ├── test-rsc-api.ps1                   # Test RSC API connectivity
│   ├── verify-deployment.ps1              # Verify deployment status
│   └── get-workspace-info.ps1             # Get workspace configuration
│
└── Additional Templates
    ├── rsc-data-collection-rule.json      # Standalone DCR template
    ├── rsc-table-schema.json              # Table schema definition
    └── sentinel-incidents-connector-template.json  # Incidents connector
```

## 🔧 Configuration

### Polling Interval
The connector polls RSC every 5 minutes by default. To customize:

1. Edit the ARM template
2. Modify `queryWindowInMin` parameter in the connector configuration
3. Recommended range: 5-60 minutes depending on environment size

### Rate Limiting
- **Default**: 5 queries per second
- **Modify**: Adjust `rateLimitQPS` in the template
- **Note**: RSC has built-in rate limiting

### Data Retention
- **Analytics Tier**: 4 days (hot, interactive queries)
- **Data Lake Tier**: 26 days (warm/cold, cost-effective)
- **Total Retention**: 30 days
- **Modify**: Update table retention settings in Log Analytics

## 🛠️ Troubleshooting

### Common Issues

#### 1. Connector Shows "Disconnected"
```kql
// Check last data ingestion
RubrikProtectionStatus_CL
| summarize LastData = max(TimeGenerated)
| extend MinutesAgo = datetime_diff('minute', now(), LastData)
```
**Solution**: Verify RSC credentials, check DCR health, review Azure Activity Log

#### 2. OAuth Authentication Failures
**Error**: `401 Unauthorized`
**Solution**:
- Verify client ID and secret are correct
- Check service account is active in RSC
- Ensure service account has read permissions

#### 3. No Data After Deployment
**Checklist**:
- ✅ Wait 5-10 minutes for initial poll
- ✅ Verify RSC URL is correct (include `https://`)
- ✅ Check Data Collection Rule is active
- ✅ Review connector health in Sentinel UI
- ✅ Check Azure Activity Log for errors

#### 4. GraphQL Query Errors
**Error**: `400 Bad Request`
**Solution**:
- Verify GraphQL query syntax in template
- Check RSC API version compatibility
- Test query directly in RSC GraphQL explorer

### Validation Queries

```kql
// Check data freshness
RubrikProtectionStatus_CL
| summarize
    LastData = max(TimeGenerated),
    RecordCount = count(),
    UniqueAssets = dcount(AssetName)
| extend MinutesAgo = datetime_diff('minute', now(), LastData)

// Validate data quality
RubrikProtectionStatus_CL
| summarize
    ValidAssets = countif(isnotempty(AssetId)),
    ValidClusters = countif(isnotempty(ClusterName)),
    ValidSnapshots = countif(TotalSnapshots >= 0),
    TotalRecords = count()
| extend QualityRate = round((ValidAssets * 100.0) / TotalRecords, 2)
```

## 📈 Use Cases

### 1. Ransomware Detection
Identify security alerts on assets with backup anomalies:
- Sudden compliance failures
- Missing snapshots during attack timeframe
- Unusual storage consumption patterns
- Failed backup jobs coinciding with security events

### 2. Recovery Readiness Assessment
For any security incident, quickly determine:
- Does the compromised asset have recent backups?
- Are the backups compliant with SLA policies?
- When was the last clean backup taken?
- Are backups available in multiple locations?

### 3. Attack Blast Radius Analysis
Correlate security incidents with backup infrastructure:
- Identify all affected assets and their backup status
- Determine which assets can be recovered
- Prioritize incident response based on backup availability
- Detect attacks specifically targeting backup systems

### 4. Compliance Reporting
Generate audit reports combining security and backup data:
- Assets with security alerts and backup non-compliance
- Protection coverage across security zones
- Backup SLA compliance for critical assets
- Recovery time objectives (RTO) validation

## 📚 Documentation

- **[RSC-README.md](RSC-README.md)** - Detailed connector documentation and API reference
- **[DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)** - Step-by-step deployment instructions
- **[RSC-TESTING-GUIDE.md](RSC-TESTING-GUIDE.md)** - Testing and validation procedures
- **[workbook-visualization-guide.md](workbook-visualization-guide.md)** - Workbook creation guide

## 🔗 Additional Resources

- **Rubrik Security Cloud**: [docs.rubrik.com](https://docs.rubrik.com/)
- **Microsoft Sentinel**: [Data Connectors Guide](https://docs.microsoft.com/azure/sentinel/connect-data-sources)
- **Codeless Connector Framework**: [CCF Documentation](https://docs.microsoft.com/azure/sentinel/create-codeless-connector)
- **KQL Reference**: [Kusto Query Language](https://docs.microsoft.com/azure/data-explorer/kusto/query/)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💡 Support

This is a community-supported connector. For assistance:

- **RSC API Issues**: Check Rubrik documentation and support
- **Azure Deployment**: Review Azure Activity Log and deployment outputs
- **Data Ingestion**: Validate DCR configuration and table schema
- **Query Performance**: Optimize KQL queries for your dataset size

## 🎯 Quick Links

- [Deploy Now](#-quick-start)
- [Sample Queries](#-sample-queries)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)

---

**Built with Microsoft's Codeless Connector Framework (CCF) for seamless Sentinel integration**
