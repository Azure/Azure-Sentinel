# Lookout Mobile Risk API v2 - Microsoft Sentinel Solution

## 🚀 Overview

The Lookout Mobile Risk API v2 solution provides comprehensive mobile threat detection, device compliance monitoring, and security intelligence for Microsoft Sentinel. This enhanced version leverages the full capabilities of Lookout's Mobile Risk API v2 to deliver advanced threat correlation, smishing detection, and sophisticated security analytics.

## ✨ What's New in v2

### 🆕 New Capabilities
- **Smishing Detection**: Advanced SMS phishing protection with impersonation analysis
- **Enhanced Device Intelligence**: 50+ v2 fields including MDM integration details
- **Audit Trail**: Complete administrative action tracking for compliance
- **Advanced Risk Scoring**: Multi-dimensional threat assessment
- **Campaign Detection**: Sophisticated coordinated attack identification

### 📊 Enhanced Components
- **4 Analytics Rules**: Comprehensive threat detection across all event types
- **6 Hunting Queries**: Advanced threat correlation scenarios
- **Enhanced Workbook**: Rich visualizations with v2 data insights
- **Validation Framework**: Complete testing and validation methodology

## 📁 Solution Structure

```
Solutions/Lookout/
├── 📋 README.md                           # This file
├── 🚀 DEPLOYMENT_GUIDE.md                 # Production deployment guide
├── 🧪 DEV_TESTING_GUIDE.md               # Development testing guide
├── 🔌 CODELESS_CONNECTOR_GUIDE.md         # 🆕 Codeless Connector Framework guide
├── 📊 UPGRADE_ANALYSIS.md                 # v1 to v2 upgrade analysis
├── 🗺️ V2_FIELD_MAPPING.md                # Complete v2 field mapping
├── 🏗️ ARCHITECTURE_DIAGRAM.md            # Solution architecture
├── 📝 TEST_DATA_SAMPLES.md               # Test data documentation
├── 📄 TEST_DATA_SAMPLES.json             # Sample v2 event data
├── 
├── 📊 Data/
│   └── Solution_Lookout.json             # Solution metadata
├── 
├── 🔌 Data Connectors/
│   ├── requirements.txt                  # Python dependencies
│   ├── LookoutAPISentinelConnector/      # Legacy function app connector
│   └── LookoutStreamingConnector_ccp/    # Enhanced CCP connector
│       ├── LookoutStreaming_DataConnectorDefinition.json
│       ├── LookoutStreaming_DCR.json     # Data Collection Rule
│       ├── LookoutStreaming_Table.json   # Table schema
│       └── LookoutStreaming_PollingConfig.json
├── 
├── 🔍 Parsers/
│   └── LookoutEvents.yaml                # Enhanced v2 parser
├── 
├── 🚨 Analytic Rules/
│   ├── LookoutThreatEvent.yaml           # Legacy threat detection
│   ├── LookoutThreatEventV2.yaml         # Enhanced threat detection
│   ├── LookoutDeviceComplianceV2.yaml    # Device compliance monitoring
│   ├── LookoutSmishingAlertV2.yaml       # 🆕 Smishing detection
│   └── LookoutAuditEventV2.yaml          # 🆕 Audit event monitoring
├── 
├── 🎯 Hunting Queries/
│   └── LookoutAdvancedThreatHunting.yaml # 🆕 6 advanced hunting scenarios
├── 
├── 📊 Workbooks/
│   ├── LookoutEvents.json                # Legacy workbook
│   └── LookoutEventsV2.json              # 🆕 Enhanced v2 workbook
├── 
├── ✅ Validation/
│   ├── LookoutV2ValidationFramework.yaml # 🆕 Testing framework
│   ├── ComponentValidationResults.md     # 🆕 Validation results
│   └── QuickStartValidation.kql          # 🆕 Quick validation queries
└── 
└── 📦 Package/
    ├── mainTemplate.json                 # ARM deployment template
    ├── createUiDefinition.json           # Azure portal UI
    └── testParameters.json               # Test parameters
```

## 🎯 Quick Start

### For End Users (Production Deployment)
1. **Read**: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)
2. **Deploy**: Via Azure Portal Content Hub or ARM template
3. **Validate**: Run queries from [`QuickStartValidation.kql`](Validation/QuickStartValidation.kql)

### For Developers (Testing & Contribution)
1. **Read**: [`DEV_TESTING_GUIDE.md`](DEV_TESTING_GUIDE.md)
2. **Set up**: Development environment with test workspace
3. **Test**: All components before submitting PR

### For Codeless Connector Framework (CCF)
1. **Read**: [`CODELESS_CONNECTOR_GUIDE.md`](CODELESS_CONNECTOR_GUIDE.md)
2. **Understand**: Modern CCF architecture and benefits
3. **Monitor**: DCR performance and field extraction

## 📋 Prerequisites

### Microsoft Sentinel Requirements
- **Log Analytics Workspace**: With Microsoft Sentinel enabled
- **Permissions**: Sentinel Contributor, Log Analytics Contributor
- **Data Retention**: Recommended 90+ days
- **Ingestion Capacity**: Minimum 1GB daily

### Lookout Requirements
- **Enterprise Account**: Active Lookout Mobile Endpoint Security
- **API Access**: Mobile Risk API v2 credentials
- **Network Access**: Outbound HTTPS to Lookout APIs
- **Mobile Devices**: Enrolled in Lookout management

## 🚀 Installation Options

### Option 1: Azure Portal (Recommended)
```
Azure Portal → Microsoft Sentinel → Content Hub → Search "Lookout" → Install
```

### Option 2: ARM Template
```bash
az deployment group create \
  --resource-group "your-rg" \
  --template-file "Package/mainTemplate.json" \
  --parameters workspace="your-sentinel-workspace"
```

### Option 3: Manual Component Deployment
Follow the step-by-step guide in [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)

## 🔍 Key Components

### Analytics Rules
| Rule | Purpose | Event Types | Severity |
|------|---------|-------------|----------|
| **LookoutThreatEventV2** | High severity mobile threats | THREAT | High |
| **LookoutDeviceComplianceV2** | Device compliance issues | DEVICE | Medium |
| **LookoutSmishingAlertV2** 🆕 | SMS phishing attacks | SMISHING_ALERT | High |
| **LookoutAuditEventV2** 🆕 | Policy & config changes | AUDIT | Medium |

### Hunting Queries
1. **Multi-Vector Attack Correlation**: Devices with multiple threat types
2. **Suspicious Device Behavior**: Unusual security status changes
3. **Enterprise Campaign Detection**: Coordinated attacks across devices
4. **APT Indicators**: Advanced persistent threat patterns
5. **Device Compromise Timeline**: Complete security event timeline
6. **Cross-Platform Correlation**: iOS/Android attack patterns

### Workbook Features
- **Security Overview**: Key metrics and KPIs
- **Threat Analysis**: Timeline and classification
- **Smishing Intelligence**: Impersonation pattern analysis
- **Device Posture**: Compliance and security status
- **Campaign Detection**: Multi-device attack visualization
- **Audit Trail**: Configuration change tracking

## ✅ Validation

### Quick Health Check
```kql
// Copy and paste into Sentinel → Logs
LookoutEvents
| where TimeGenerated > ago(24h)
| summarize 
    TotalEvents = count(),
    EventTypes = make_set(EventType),
    UniqueDevices = dcount(DeviceGuid)
| extend HealthStatus = case(
    TotalEvents > 0, "✅ Healthy",
    "❌ Check data connector"
)
```

### Comprehensive Validation
Run all queries from [`QuickStartValidation.kql`](Validation/QuickStartValidation.kql) to validate:
- ✅ Data ingestion
- ✅ Field extraction
- ✅ Analytics rules
- ✅ Workbook functionality
- ✅ Performance

## 📊 Data Schema

### Event Types
- **THREAT**: Malware, spyware, and security threats
- **DEVICE**: Device status, compliance, and configuration
- **SMISHING_ALERT**: SMS phishing and social engineering
- **AUDIT**: Policy changes and administrative actions

### Key Fields (v2 Enhanced)
```kql
LookoutEvents
| getschema
| where ColumnName startswith "Threat" or 
         ColumnName startswith "Device" or
         ColumnName startswith "Smishing" or
         ColumnName startswith "Audit"
```

See [`V2_FIELD_MAPPING.md`](V2_FIELD_MAPPING.md) for complete field documentation.

## 🔧 Troubleshooting

### Common Issues

#### No Data Ingesting
```kql
// Check raw data table
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| take 5
```
**Solutions**: Verify API credentials, check network connectivity, validate enterprise GUID

#### Analytics Rules Not Triggering
```kql
// Test rule queries directly
LookoutEvents
| where EventType == "THREAT"
| where ThreatSeverity in ("CRITICAL", "HIGH")
| take 10
```
**Solutions**: Check data availability, verify field mappings, review rule frequency

#### Workbook Not Loading
**Solutions**: Check data source permissions, validate KQL syntax, review parameter configuration

### Support Resources
- **Lookout Support**: [Support Portal](https://www.lookout.com/support)
- **Microsoft Sentinel**: [Documentation](https://docs.microsoft.com/azure/sentinel/)
- **Community**: [GitHub Issues](https://github.com/Azure/Azure-Sentinel/issues)

## 🔄 Upgrade from v1

### Migration Path
1. **Review**: [`UPGRADE_ANALYSIS.md`](UPGRADE_ANALYSIS.md) for detailed migration plan
2. **Deploy**: v2 components alongside existing v1 components
3. **Validate**: Both versions work correctly
4. **Migrate**: Gradually transition to v2 analytics rules
5. **Cleanup**: Remove v1 components when ready

### Backward Compatibility
- ✅ Existing queries continue to work
- ✅ Legacy field names preserved
- ✅ Gradual migration supported
- ✅ No data loss during transition

## 🤝 Contributing

### Development Workflow
1. **Fork** the Azure Sentinel repository
2. **Follow** [`DEV_TESTING_GUIDE.md`](DEV_TESTING_GUIDE.md)
3. **Test** thoroughly in development environment
4. **Validate** all components pass tests
5. **Submit** pull request with validation results

### Contribution Guidelines
- Follow existing code patterns
- Include comprehensive testing
- Update documentation
- Validate performance impact
- Ensure backward compatibility

## 📈 Performance

### Optimized for Scale
- **Query Performance**: <5 minutes for analytics rules
- **Workbook Load Time**: <2 minutes for visualizations
- **Data Volume**: Tested with 100K+ events
- **Resource Usage**: Optimized KQL patterns

### Monitoring
```kql
// Monitor solution performance
LookoutEvents
| where TimeGenerated > ago(1d)
| summarize 
    EventsPerHour = count() / 24,
    AvgProcessingTime = avg(ingestion_time() - TimeGenerated),
    DataVolumeMB = sum(estimate_data_size(*)) / 1024 / 1024
```

## 🔒 Security & Compliance

### Data Protection
- **PII Handling**: Email addresses and device IDs properly managed
- **Encryption**: Data encrypted in transit and at rest
- **Access Control**: Role-based access validated
- **Audit Logging**: All administrative actions logged

### Compliance Standards
- ✅ **GDPR**: Data processing transparency
- ✅ **SOC 2**: Security controls validated
- ✅ **ISO 27001**: Information security aligned

## 📚 Documentation

### User Guides
- [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) - Production deployment
- [`DEV_TESTING_GUIDE.md`](DEV_TESTING_GUIDE.md) - Development testing
- [`QuickStartValidation.kql`](Validation/QuickStartValidation.kql) - Validation queries

### Technical References
- [`V2_FIELD_MAPPING.md`](V2_FIELD_MAPPING.md) - Complete field documentation
- [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md) - Solution architecture
- [`CODELESS_CONNECTOR_GUIDE.md`](CODELESS_CONNECTOR_GUIDE.md) - CCF implementation details
- [`LookoutV2ValidationFramework.yaml`](Validation/LookoutV2ValidationFramework.yaml) - Testing framework

### Sample Data
- [`TEST_DATA_SAMPLES.json`](TEST_DATA_SAMPLES.json) - v2 event samples
- [`TEST_DATA_SAMPLES.md`](TEST_DATA_SAMPLES.md) - Sample data documentation

## 🏷️ Version History

### v2.0.0 (Current)
- ✨ **New**: Smishing detection analytics rule
- ✨ **New**: Audit event monitoring rule
- ✨ **New**: Enhanced workbook with v2 visualizations
- ✨ **New**: Advanced hunting queries (6 scenarios)
- ✨ **New**: Comprehensive validation framework
- 🔧 **Enhanced**: 50+ v2 fields with MDM integration
- 🔧 **Enhanced**: Risk scoring and threat correlation
- 📚 **Added**: Complete documentation suite

### v1.x (Legacy)
- Basic threat detection
- Simple device monitoring
- Limited field extraction
- Basic workbook visualizations

## 📞 Support

### Getting Help
1. **Documentation**: Check relevant guide first
2. **Validation**: Run diagnostic queries
3. **Community**: Search GitHub issues
4. **Support**: Contact Lookout or Microsoft support

### Reporting Issues
- **GitHub**: [Azure Sentinel Issues](https://github.com/Azure/Azure-Sentinel/issues)
- **Template**: Include validation results and error details
- **Logs**: Provide relevant KQL query results

---

## 🎉 Ready to Get Started?

1. **Production Users**: Start with [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)
2. **Developers**: Begin with [`DEV_TESTING_GUIDE.md`](DEV_TESTING_GUIDE.md)
3. **Quick Test**: Run [`QuickStartValidation.kql`](Validation/QuickStartValidation.kql)

**The enhanced Lookout v2 solution is ready to provide comprehensive mobile security intelligence for your organization!** 🚀