# BeyondTrust Privilege Management Cloud Solution Release Notes

## Version 1.0.0 - Initial Release (October 2025)

### Features

**Data Connector:**
- Azure Function-based data connector for BeyondTrust Privilege Management Cloud
- Automated collection of Activity Audit logs (administrative and configuration activities)
- Automated collection of Client Event logs (endpoint security events in ECS format)
- OAuth 2.0 client credentials flow authentication
- Stateful processing with checkpoint management to prevent duplicate ingestion
- Configurable polling intervals (default: 15 min for audits, 5 min for events)
- Support for multiple hosting plans: Consumption (Y1), Flex Consumption (FC1), and Elastic Premium (EP1-3)
- Data ingested into custom Log Analytics tables:
  - `BeyondTrustPM_ActivityAudits_CL` - Management activities and policy changes
  - `BeyondTrustPM_ClientEvents_CL` - Endpoint security events

**Workbooks:**
- BeyondTrust PM Cloud Overview workbook with visualizations for:
  - Activity audits over time
  - Client events over time
  - Event distribution by severity
  - Top users and actions
  - Recent security events

### Prerequisites

- BeyondTrust PM Cloud tenant with API access enabled
- OAuth Client Credentials for BeyondTrust PM Cloud Management API
- Azure Log Analytics workspace configured for Microsoft Sentinel
- Azure subscription with permissions to deploy Azure Functions

### Deployment

This solution includes:
1. Data connector definition for Microsoft Sentinel Content Hub
2. Workbook for visualizing BeyondTrust PM Cloud data
3. ARM template for deploying the Azure Function infrastructure

Please refer to the solution documentation for complete deployment instructions.

### Known Issues

None at this time.

### Support

For support, contact BeyondTrust at mysupport@beyondtrust.com or visit https://www.beyondtrust.com/
