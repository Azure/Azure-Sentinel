# Microsoft 365 Audit General & DLP Solution - Release Notes

## Version 1.0.0 (January 2026)

### Initial Release

This is the first public release of the Microsoft 365 Audit General & DLP solution for Microsoft Sentinel.

#### Features

**Data Connectors**
- Microsoft 365 Audit.General connector using Codeless Connector Framework (CCF)
- Microsoft 365 Audit.DLP connector using Codeless Connector Framework (CCF)
- OAuth 2.0 authentication with Microsoft 365 Management Activity API
- Automatic data ingestion with configurable polling intervals

**Data Collection**
- Custom Log Analytics table: `M365AuditGeneral_CL` (stores both Audit.General and Audit.DLP events)
- Data Collection Rules (DCR) for efficient ingestion
- Data Collection Endpoints (DCE) for secure data flow

**Schema Support**
- Full support for Office 365 Management Activity API schema
- 300+ audit fields mapped and ingested
- Dynamic column handling for schema evolution
- Proper data type mapping (string, int, bool, datetime)

#### Prerequisites

- Microsoft Sentinel workspace
- Azure AD application with the following API permissions:
  - `Office 365 Management APIs` - `ActivityFeed.Read`
  - `Office 365 Management APIs` - `ActivityFeed.ReadDlp`
- Microsoft 365 subscription with appropriate audit logging enabled
- Subscription must be started for audit events (see documentation)

#### Deployment

The solution deploys the following resources:
- Data Collection Endpoint (DCE)
- Data Collection Rule (DCR)
- Custom Log Analytics Table (M365AuditGeneral_CL)
- Two Data Connector Definitions (Audit.General and Audit.DLP)

#### Known Issues

None at this time.

#### Support

This is a community-supported solution. For issues or questions:
- Open an issue on [GitHub](https://github.com/Azure/Azure-Sentinel/issues)
- Tag with `Microsoft 365 Audit General & DLP`


