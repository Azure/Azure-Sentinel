# Lookout Mobile Risk API v2 - Microsoft Sentinel Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying and validating the enhanced Lookout Mobile Risk API v2 solution in Microsoft Sentinel.

## Prerequisites

### Microsoft Sentinel Requirements
- **Microsoft Sentinel Workspace**: Active Log Analytics workspace with Sentinel enabled
- **Permissions**: 
  - Microsoft Sentinel Contributor role
  - Log Analytics Contributor role
  - Workbook Contributor role
- **Resource Requirements**:
  - Minimum 1GB daily ingestion capacity
  - Data retention policy configured (recommended: 90+ days)

### Lookout Requirements
- **Lookout Enterprise Account**: Active Lookout Mobile Endpoint Security subscription
- **API Access**: Mobile Risk API v2 credentials
- **Network Access**: Outbound HTTPS connectivity to Lookout APIs
- **Data Sources**: Mobile devices enrolled in Lookout management

## Deployment Methods

### Method 1: Azure Portal Deployment (Recommended)

#### Step 1: Deploy from Content Hub
1. **Navigate to Microsoft Sentinel**
   ```
   Azure Portal → Microsoft Sentinel → [Your Workspace] → Content Hub
   ```

2. **Search for Lookout Solution**
   ```
   Search: "Lookout"
   Filter: Solutions
   ```

3. **Install Lookout Solution**
   - Click on "Lookout" solution
   - Click "Install"
   - Review components and dependencies
   - Click "Create"

#### Step 2: Configure Data Connector
1. **Navigate to Data Connectors**
   ```
   Microsoft Sentinel → Configuration → Data connectors
   ```

2. **Configure Lookout Streaming Connector**
   - Search for "Lookout"
   - Select "Lookout Streaming Connector (CCP)"
   - Click "Open connector page"
   - Follow configuration wizard

3. **Required Configuration Parameters**
   ```json
   {
     "lookout_api_endpoint": "https://api.lookout.com/v2",
     "client_id": "your-client-id",
     "client_secret": "your-client-secret",
     "enterprise_guid": "your-enterprise-guid",
     "polling_interval": "5m",
     "log_level": "INFO"
   }
   ```

### Method 2: ARM Template Deployment

#### Step 1: Prepare ARM Template
```bash
# Clone the Azure Sentinel repository
git clone https://github.com/Azure/Azure-Sentinel.git
cd Azure-Sentinel/Solutions/Lookout
```

#### Step 2: Deploy via Azure CLI
```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Deploy the solution
az deployment group create \
  --resource-group "your-resource-group" \
  --template-file "Package/mainTemplate.json" \
  --parameters \
    workspace="your-sentinel-workspace" \
    location="your-region"
```

#### Step 3: Deploy via PowerShell
```powershell
# Connect to Azure
Connect-AzAccount

# Set context
Set-AzContext -SubscriptionId "your-subscription-id"

# Deploy template
New-AzResourceGroupDeployment `
  -ResourceGroupName "your-resource-group" `
  -TemplateFile "Package/mainTemplate.json" `
  -workspace "your-sentinel-workspace" `
  -location "your-region"
```

## Component Validation Steps

### Step 1: Verify Data Ingestion

#### Check Data Connector Status
```kql
// Verify data connector is receiving data
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| summarize count() by bin(TimeGenerated, 5m)
| render timechart
```

#### Validate Event Types
```kql
// Check all event types are being ingested
LookoutEvents
| where TimeGenerated > ago(24h)
| summarize count() by EventType
| render piechart
```

#### Verify Field Extraction
```kql
// Validate v2 field extraction
LookoutEvents
| where TimeGenerated > ago(1h)
| where EventType == "THREAT"
| project TimeGenerated, ThreatId, ThreatType, ThreatSeverity, 
          DeviceGuid, DevicePlatform, DeviceEmailAddress
| take 10
```

### Step 2: Test Analytics Rules

#### Enable Analytics Rules
1. **Navigate to Analytics**
   ```
   Microsoft Sentinel → Analytics → Rule templates
   ```

2. **Enable Lookout Rules**
   - Search for "Lookout"
   - Enable each rule:
     - ✅ Lookout - High Severity Mobile Threats Detected (v2)
     - ✅ Lookout - Device Compliance and Security Status Changes (v2)
     - ✅ Lookout - Critical Smishing and Phishing Alerts (v2)
     - ✅ Lookout - Critical Audit and Policy Changes (v2)

#### Validate Rule Triggering
```kql
// Check if analytics rules are triggering
SecurityAlert
| where TimeGenerated > ago(24h)
| where AlertName contains "Lookout"
| summarize count() by AlertName, AlertSeverity
```

### Step 3: Validate Workbooks

#### Import Enhanced Workbook
1. **Navigate to Workbooks**
   ```
   Microsoft Sentinel → Workbooks → Templates
   ```

2. **Deploy Lookout Workbooks**
   - Search for "Lookout"
   - Deploy both workbooks:
     - ✅ Lookout Events (Legacy)
     - ✅ Lookout Events V2 (Enhanced)

#### Test Workbook Functionality
1. **Open Lookout Events V2 Workbook**
2. **Verify Data Population**:
   - Security Overview Metrics
   - Threat Timeline
   - Smishing Analysis
   - Device Posture
   - Campaign Detection
   - Audit Trail

### Step 4: Execute Hunting Queries

#### Import Hunting Queries
1. **Navigate to Hunting**
   ```
   Microsoft Sentinel → Hunting → Queries
   ```

2. **Import Custom Queries**
   - Copy queries from `LookoutAdvancedThreatHunting.yaml`
   - Create new hunting queries for each scenario

#### Test Hunting Scenarios
```kql
// Multi-Vector Attack Correlation
let timeWindow = 24h;
let threatEvents = LookoutEvents
| where TimeGenerated > ago(timeWindow)
| where EventType == "THREAT"
| where ThreatSeverity in ("CRITICAL", "HIGH")
| summarize 
    ThreatTypes = make_set(ThreatType),
    ThreatCount = count()
    by DeviceGuid;
// ... (rest of query from hunting file)
```

## Validation Checklist

### ✅ Data Ingestion Validation
- [ ] Data connector configured and active
- [ ] All event types (THREAT, DEVICE, SMISHING_ALERT, AUDIT) ingesting
- [ ] V2 fields extracting correctly
- [ ] Data volume within expected ranges

### ✅ Analytics Rules Validation
- [ ] All 4 v2 analytics rules enabled
- [ ] Rules triggering on test data
- [ ] Incidents created with correct severity
- [ ] Entity mappings populated
- [ ] Custom details accurate

### ✅ Workbook Validation
- [ ] Both workbooks deployed successfully
- [ ] V2 workbook displays enhanced visualizations
- [ ] All parameters functioning
- [ ] Data filtering working correctly
- [ ] Performance acceptable (<2 min load time)

### ✅ Hunting Queries Validation
- [ ] All 6 hunting scenarios imported
- [ ] Queries execute without errors
- [ ] Results returned within 10 minutes
- [ ] Data correlation working correctly

### ✅ Performance Validation
- [ ] Query performance within thresholds
- [ ] Data ingestion latency acceptable
- [ ] Workbook responsiveness good
- [ ] No resource constraints

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: No Data Ingesting
**Symptoms**: Empty LookoutMtdV2_CL table
**Solutions**:
1. Verify API credentials
2. Check network connectivity
3. Validate enterprise GUID
4. Review data connector logs

#### Issue: Analytics Rules Not Triggering
**Symptoms**: No SecurityAlert records
**Solutions**:
1. Verify rule query syntax
2. Check data availability
3. Validate field mappings
4. Review rule frequency settings

#### Issue: Workbook Not Loading
**Symptoms**: Blank or error in workbook
**Solutions**:
1. Check data source permissions
2. Verify KQL query syntax
3. Validate parameter configuration
4. Review workspace connectivity

#### Issue: Poor Performance
**Symptoms**: Slow query execution
**Solutions**:
1. Optimize time ranges
2. Add appropriate filters
3. Review data volume
4. Consider query optimization

## Monitoring and Maintenance

### Daily Monitoring
```kql
// Daily data ingestion check
LookoutEvents
| where TimeGenerated > ago(1d)
| summarize 
    EventCount = count(),
    UniqueDevices = dcount(DeviceGuid),
    EventTypes = make_set(EventType)
| extend HealthStatus = case(
    EventCount > 1000, "Healthy",
    EventCount > 100, "Warning",
    "Critical"
)
```

### Weekly Health Check
```kql
// Weekly analytics rule effectiveness
SecurityAlert
| where TimeGenerated > ago(7d)
| where AlertName contains "Lookout"
| summarize 
    TotalAlerts = count(),
    HighSeverity = countif(AlertSeverity == "High"),
    MediumSeverity = countif(AlertSeverity == "Medium")
| extend EffectivenessScore = round(todouble(HighSeverity) / todouble(TotalAlerts) * 100, 2)
```

### Monthly Review
- Review false positive rates
- Analyze threat trends
- Update hunting queries
- Optimize rule thresholds
- Review compliance metrics

## Support and Resources

### Documentation
- [Lookout API Documentation](https://enterprise.support.lookout.com/hc/articles/115002741773-Mobile-Risk-API-Guide)
- [Microsoft Sentinel Documentation](https://docs.microsoft.com/azure/sentinel/)
- [KQL Reference](https://docs.microsoft.com/azure/data-explorer/kusto/query/)

### Support Channels
- **Lookout Support**: [Lookout Support Portal](https://www.lookout.com/support)
- **Microsoft Support**: Azure Support Portal
- **Community**: Microsoft Sentinel GitHub Repository

### Additional Resources
- Lookout Mobile Risk API v2 Field Mapping: `V2_FIELD_MAPPING.md`
- Test Data Samples: `TEST_DATA_SAMPLES.json`
- Validation Framework: `LookoutV2ValidationFramework.yaml`
- Component Validation Results: `ComponentValidationResults.md`

---

**Next Steps**: After successful deployment, proceed with the validation checklist and begin monitoring your enhanced mobile security posture with the comprehensive Lookout v2 capabilities.