# Microsoft 365 Audit Data Connectors

This solution includes two Codeless Connector Framework (CCF) data connectors for Microsoft 365 Audit logs.

## Connectors

### 1. Microsoft 365 Audit General
- **Content Type**: Audit.General
- **Purpose**: Collects general Office 365 audit events including user activities, admin operations, and security events
- **API Endpoint**: Office 365 Management Activity API
- **Polling Interval**: 5 minutes
- **Authentication**: OAuth 2.0 via Microsoft Entra ID Application

### 2. Microsoft 365 Audit DLP
- **Content Type**: Audit.DLP
- **Purpose**: Collects Data Loss Prevention (DLP) policy events and violations
- **API Endpoint**: Office 365 Management Activity API
- **Polling Interval**: 5 minutes
- **Authentication**: OAuth 2.0 via Microsoft Entra ID Application

## Data Destination

Both connectors send data to a single custom table: **M365AuditGeneral_CL**

The table schema supports all event types from both Audit.General and Audit.DLP content types.

## Connector Definitions

The connector resources are fully defined in the ARM template (`Package/mainTemplate.json`) using the Codeless Connector Framework. No additional JSON files are required for CCF-based connectors.

## Prerequisites

- Log Analytics workspace with Microsoft Sentinel enabled
- Microsoft Entra ID application with permissions:
  - ActivityFeed.Read
  - ActivityFeed.ReadDlp
- Office 365 Audit Log Search enabled
- **Office 365 Management Activity API subscription enabled** for both content types:
  - Audit.General
  - Audit.DLP
  
  > **Important**: You must start a subscription to the Office 365 Management Activity API for each content type before the connectors can retrieve data. This is done via API call to `/subscriptions/start` endpoint for each content type. Without an active subscription, the API will not return any audit events.

## Configuration

Connectors are configured during solution deployment via the Content Hub installation wizard. Required parameters:
- Microsoft Entra ID Tenant ID
- Microsoft Entra ID Application (Client) ID
- Microsoft Entra ID Application Client Secret

