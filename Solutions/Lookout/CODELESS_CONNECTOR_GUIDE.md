# Lookout Mobile Risk API v2 - Codeless Connector Framework Guide

## 🎯 Overview

The Lookout Mobile Risk API v2 solution leverages Microsoft's **Codeless Connector Framework (CCF)** for modern, efficient data ingestion. This guide provides specific information about the CCF implementation and how to work with it.

## 🏗️ Codeless Connector Framework Benefits

### **Modern Architecture (Pre-existing)**
- ✅ **Log Ingestion API**: Replaces deprecated HTTP Data Collector API
- ✅ **Data Collection Rules (DCR)**: Advanced data transformation and enrichment
- ✅ **Enhanced Performance**: Optimized ingestion pipeline
- ✅ **Better Reliability**: Built-in retry mechanisms and error handling

### **Advanced Features (Pre-existing)**
- ✅ **Field Transformation**: KQL-based data transformation at ingestion
- ✅ **Data Enrichment**: Add computed fields and metadata
- ✅ **Schema Validation**: Automatic data type validation
- ✅ **Cost Optimization**: Efficient data processing and storage

## 📁 CCF Components in Lookout Solution

### Pre-existing CCF Implementation
```
Data Connectors/LookoutStreamingConnector_ccp/
├── LookoutStreaming_DataConnectorDefinition.json  # CCF connector definition (existing)
├── LookoutStreaming_DCR.json                      # Data Collection Rule (existing)
├── LookoutStreaming_Table.json                    # Target table schema (existing)
└── LookoutStreaming_PollingConfig.json            # Polling configuration (existing)
```

**Note**: The CCF implementation was already present in the Lookout solution. Our v2 enhancements build upon this existing modern architecture.

### Component Details

#### 1. Data Connector Definition
**File**: `LookoutStreaming_DataConnectorDefinition.json`
- Defines the connector UI and configuration
- Specifies API endpoints and authentication
- Configures polling intervals and data sources

#### 2. Data Collection Rule (DCR)
**File**: `LookoutStreaming_DCR.json`
- **Key Feature**: Transforms raw Lookout API data into structured fields
- Extracts 50+ v2 fields from nested JSON objects
- Applies data type conversions and validation
- Enriches data with computed fields

#### 3. Table Schema
**File**: `LookoutStreaming_Table.json`
- Defines the `LookoutMtdV2_CL` table structure
- Specifies field types and constraints
- Optimizes for query performance

#### 4. Polling Configuration
**File**: `LookoutStreaming_PollingConfig.json`
- Configures API polling behavior
- Sets retry policies and error handling
- Defines data freshness requirements

## 🔧 Working with the CCF Implementation

### Viewing Current Configuration

#### Check Connector Status
```kql
// View connector health and status
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| summarize 
    LastIngestion = max(TimeGenerated),
    RecordCount = count(),
    DataSizeMB = round(sum(estimate_data_size(*)) / 1024.0 / 1024.0, 2)
| extend HealthStatus = case(
    LastIngestion > ago(15m), "✅ Healthy",
    LastIngestion > ago(1h), "⚠️ Warning", 
    "❌ Critical"
)
```

#### Validate DCR Transformation
```kql
// Check if DCR is properly extracting v2 fields
LookoutEvents
| where TimeGenerated > ago(1h)
| extend FieldExtractionStatus = case(
    isnotempty(ThreatId) and EventType == "THREAT", "✅ Threat fields extracted",
    isnotempty(DeviceGuid) and EventType == "DEVICE", "✅ Device fields extracted", 
    isnotempty(SmishingAlertId) and EventType == "SMISHING_ALERT", "✅ Smishing fields extracted",
    isnotempty(AuditType) and EventType == "AUDIT", "✅ Audit fields extracted",
    "⚠️ Field extraction issues"
)
| summarize count() by FieldExtractionStatus
```

### Configuration Management

#### API Key Configuration
The CCF connector requires proper API key configuration:

1. **Navigate to Data Connectors**
   ```
   Microsoft Sentinel → Configuration → Data connectors → Lookout Mobile Threat Detection Connector
   ```

2. **Configure API Settings**
   - **API Key**: Your Lookout Mobile Risk API v2 key
   - **Enterprise GUID**: Your Lookout enterprise identifier
   - **Polling Interval**: Recommended 5-15 minutes
   - **Log Level**: INFO for production, DEBUG for troubleshooting

#### Monitoring CCF Performance
```kql
// Monitor CCF connector performance
LookoutMtdV2_CL
| where TimeGenerated > ago(24h)
| extend IngestionDelay = ingestion_time() - TimeGenerated
| summarize 
    AvgDelayMinutes = avg(IngestionDelay) / 1m,
    MaxDelayMinutes = max(IngestionDelay) / 1m,
    RecordsPerHour = count() / 24
| extend PerformanceStatus = case(
    AvgDelayMinutes < 5, "✅ Excellent",
    AvgDelayMinutes < 15, "⚠️ Acceptable",
    "❌ Poor - Check connector"
)
```

## 🔄 DCR Transformation Logic

### Enhanced Field Extraction
The DCR performs sophisticated field extraction from Lookout's nested JSON:

```kql
// Example DCR transformation logic (simplified)
source 
| extend 
    // Core event fields
    EventType = tostring(type),
    EventId = tostring(id),
    EnterpriseGuid = tostring(enterprise_guid),
    
    // Device fields from nested object
    DeviceGuid = tostring(device.guid),
    DevicePlatform = tostring(device.platform),
    DeviceSecurityStatus = tostring(device.security_status),
    DeviceEmailAddress = tostring(device.email_address),
    
    // Threat fields from nested object  
    ThreatId = tostring(threat.id),
    ThreatType = tostring(threat.type),
    ThreatSeverity = tostring(threat.severity),
    ThreatClassifications = tostring(threat.classifications),
    
    // Smishing fields (v2 new capability)
    SmishingAlertId = tostring(smishing_alert.id),
    SmishingAlertType = tostring(smishing_alert.type),
    SmishingAlertSeverity = tostring(smishing_alert.severity),
    
    // Audit fields (v2 new capability)
    AuditType = tostring(audit.type),
    AuditAttributeChanges = audit.attribute_changes,
    
    // MDM integration fields
    MDMConnectorId = toint(device.details.mdm_connector_id),
    MDMExternalId = tostring(device.details.external_id),
    
    // Set proper timestamp
    TimeGenerated = todatetime(created_time)
```

## 🚀 Deployment via CCF

### Azure Portal Deployment
The CCF connector appears in the Microsoft Sentinel Content Hub:

1. **Content Hub Installation**
   ```
   Microsoft Sentinel → Content Hub → Search "Lookout" → Install
   ```

2. **Automatic CCF Setup**
   - DCR automatically created
   - Table schema deployed
   - Connector definition installed
   - Polling configuration applied

### Manual CCF Configuration
If needed, you can manually configure the CCF components:

```bash
# Deploy DCR
az monitor data-collection-rule create \
  --resource-group "your-rg" \
  --name "LookoutMtdV2-DCR" \
  --rule-file "LookoutStreaming_DCR.json"

# Deploy table schema
az monitor log-analytics workspace table create \
  --resource-group "your-rg" \
  --workspace-name "your-workspace" \
  --name "LookoutMtdV2_CL" \
  --columns-file "LookoutStreaming_Table.json"
```

## 🔧 Troubleshooting CCF Issues

### Common CCF Problems

#### Issue: No Data Ingesting
```kql
// Check DCR processing status
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| take 5
```

**Solutions**:
1. Verify API key is correct
2. Check enterprise GUID
3. Validate network connectivity
4. Review DCR configuration

#### Issue: Field Extraction Problems
```kql
// Check raw vs. parsed data
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| project TimeGenerated, RawData
| take 5

// Compare with parsed data
LookoutEvents  
| where TimeGenerated > ago(1h)
| project TimeGenerated, EventType, DeviceGuid, ThreatId
| take 5
```

**Solutions**:
1. Validate DCR transformation logic
2. Check JSON structure changes
3. Review parser function
4. Update field mappings

#### Issue: Performance Problems
```kql
// Monitor DCR performance
LookoutMtdV2_CL
| where TimeGenerated > ago(24h)
| summarize 
    RecordsPerHour = count() / 24,
    AvgSizeKB = avg(estimate_data_size(*)) / 1024
| extend PerformanceIssue = case(
    RecordsPerHour < 10, "Low volume - check API",
    AvgSizeKB > 100, "Large records - optimize DCR",
    "Normal"
)
```

**Solutions**:
1. Optimize DCR transformation
2. Adjust polling frequency
3. Review data volume
4. Check resource allocation

## 📊 CCF vs Legacy Comparison

### Migration Benefits
| Feature | Legacy HTTP Collector | CCF Implementation |
|---------|----------------------|-------------------|
| **API** | HTTP Data Collector (deprecated) | Log Ingestion API (modern) |
| **Transformation** | Client-side parsing | Server-side DCR |
| **Performance** | Basic | Optimized |
| **Reliability** | Manual retry logic | Built-in resilience |
| **Cost** | Higher processing overhead | Optimized ingestion |
| **Maintenance** | Manual updates required | Automatic updates |

### Backward Compatibility
- ✅ Existing queries continue to work
- ✅ Same table name (`LookoutMtdV2_CL`)
- ✅ Enhanced field extraction
- ✅ Improved performance

## 🎯 Best Practices for CCF

### Configuration Optimization
1. **Polling Frequency**: 5-15 minutes for most environments
2. **Data Retention**: Configure based on compliance requirements
3. **Error Handling**: Monitor and alert on ingestion failures
4. **Performance**: Regular monitoring of ingestion metrics

### Monitoring and Maintenance
```kql
// Daily CCF health check
LookoutMtdV2_CL
| where TimeGenerated > ago(1d)
| summarize 
    TotalRecords = count(),
    UniqueDevices = dcount(column_ifexists("device_guid_s", "")),
    IngestionGaps = countif(TimeGenerated < ago(1h)),
    DataQuality = countif(isnotempty(column_ifexists("id_s", "")))
| extend HealthScore = round((DataQuality * 100.0) / TotalRecords, 1)
```

### Security Considerations
- 🔐 **API Key Management**: Store securely in Key Vault
- 🔐 **Network Security**: Use private endpoints if available
- 🔐 **Access Control**: Implement least privilege access
- 🔐 **Audit Logging**: Monitor connector configuration changes

## 📚 Additional Resources

### Microsoft Documentation
- [Codeless Connector Framework](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector)
- [Data Collection Rules](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/data-collection-rule-overview)
- [Log Ingestion API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)

### Lookout Resources
- [Mobile Risk API Documentation](https://enterprise.support.lookout.com/hc/articles/115002741773-Mobile-Risk-API-Guide)
- [API v2 Migration Guide](https://enterprise.support.lookout.com/hc/articles/api-v2-migration)

---

**The Lookout solution's CCF implementation provides a modern, efficient, and reliable data ingestion pipeline that fully leverages Microsoft's latest connector framework capabilities.**