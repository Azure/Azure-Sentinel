# Microsoft 365 Audit General & DLP Solution v1.0.0

**Author**: Marko Lauren

This solution provides **two codeless connectors (CCF)** for ingesting Microsoft 365 audit logs from the Office 365 Management Activity API into Microsoft Sentinel:
- **Microsoft 365 Audit.General** - General audit logs (29 specialty workloads)
- **Microsoft 365 Audit.DLP** - Data Loss Prevention events

## Overview

These connectors use the **Office 365 Management Activity API** to retrieve Microsoft 365 audit logs into a shared **304-column schema** covering **30 specialty workload types**:

- **Audit.General connector**: 29 specialty workloads (Copilot, Power BI, Viva suite, Security & Compliance, eDiscovery, Sentinel platform, etc.)
- **Audit.DLP connector**: Data loss prevention (DLP) events in Microsoft Purview available for Exchange Online, Endpoint(devices), and SharePoint and OneDrive.

**Schema Design:** This connector follows the official [Office 365 Management Activity API Schema](https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema) as documented by Microsoft. All field names, types, and structures are mapped directly from the API schema to ensure compatibility and accuracy.

## Content Types Coverage

The Office 365 Management Activity API organizes audit data into different content types:
- **Audit.AzureActiveDirectory** - Azure AD/Entra ID events (sign-ins, directory changes)
- **Audit.Exchange** - Exchange Online events (email, mailbox access)
- **Audit.SharePoint** - SharePoint/OneDrive events (file operations)
- **Audit.General** ✅ - All other Microsoft 365 workloads not in the above (covered by this solution)
- **DLP.All** ✅ - DLP events only for all workloads (covered by this solution)

### Audit.General Connector Scope

**✅ Included (29 specialty workload schemas):**
- **Copilot & AI**: Microsoft 365 Copilot interactions, AI Agent operations, Copilot scheduled prompts
- **Power Platform**: Power BI (dashboards, datasets, reports), Microsoft Forms
- **Collaboration**: Viva Engage (Yammer), Project for the web
- **Viva Suite**: Viva Insights, Viva Goals, Viva Glint, Viva Pulse
- **Security & Compliance**: Microsoft Defender for Office 365, Attack Simulation & Training, User Submissions, Automated Investigation & Response (AIR), Hygiene Events, Quarantine, Security & Compliance Alerts, Security & Compliance Center operations
- **Information Protection**: MIP Label, Encrypted Message Portal
- **eDiscovery**: eDiscovery case management, search, export, and hold operations
- **Cloud Management**: Backup/Restore operations (Policy, Task, Item schemas)
- **Security Tools**: Microsoft Edge WebContentFiltering
- **Microsoft Sentinel**: Sentinel Data Lake operations (Notebooks, Jobs, KQL queries, Lake onboarding, AI Tools, Graph operations)
- **Infrastructure**: Places Directory, Data Center Security (Base & Cmdlet schemas)

**❌ Excluded (have dedicated Microsoft Sentinel connectors or filtered):**
- Microsoft Teams (filtered RecordType=25, dedicated connector exists)
- Dynamics 365 (filtered RecordType=21 & 278, dedicated connector exists)
- Microsoft Purview Information Protection (filtered RecordType=71,72,75,82,83,84,93,94,95,96,97, dedicated connector exists)
- SharePoint/OneDrive (dedicated connector exists)
- Exchange (dedicated connector exists)
- Microsoft Entra ID (dedicated connector exists)

### Audit.DLP Connector Scope

**✅ Included (All DLP events):**
- **RecordType 11** - ComplianceDLPSharePoint (DLP events in SharePoint and OneDrive)
- **RecordType 13** - ComplianceDLPExchange (DLP events in Exchange via Unified DLP Policy)
- **RecordType 33** - ComplianceDLPSharePointClassification (DLP classification in SharePoint)
- **RecordType 63** - DLPEndpoint (Endpoint DLP events)
- **RecordType 99** - OnPremisesFileShareScannerDlp (Scanning for sensitive data on file shares)
- **RecordType 100** - OnPremisesSharePointScannerDlp (Scanning for sensitive data in SharePoint)
- **RecordType 107** - ComplianceDLPExchangeClassification (Exchange DLP classification events)
- **RecordType 187** - PowerPlatformAdminDlp (Microsoft Power Platform DLP - Preview)

## Polling Behavior

**Polling Interval:** The connector polls the Office 365 Management API every **5 minutes** by default.

## Data Schema

Both connectors ingest data into the **shared** `M365AuditGeneral_CL` custom table with **304 columns** covering **30 workload schemas** (29 from Audit.General + 1 DLP schema).

### Core Common Fields (14 fields)

| Field | Type | Description |
|-------|------|-------------|
| TimeGenerated | datetime | The time when the event was ingested into Sentinel |
| Id | string | Unique identifier for the audit record |
| RecordType | int | The type of operation indicated by the record |
| CreationTime | datetime | The date and time in UTC when the user performed the activity |
| Operation | string | The name of the user or admin activity |
| UserId | string | The UPN of the user who performed the action |
| Workload | string | The Microsoft 365 service (e.g., PowerBI, MicrosoftForms, Yammer) |
| ClientIP | string | The IP address of the device that was used |
| ResultStatus | string | Indicates whether the action was successful |
| ObjectId | string | The name/path of the object that was modified |
| UserType | int | The type of user that performed the operation |
| UserKey | string | An alternative ID for the user |
| OrganizationId | string | The GUID for your Microsoft 365 tenant |
| Scope | string | Whether the event was from hosted M365 or on-premises |

### Workload-Specific Fields (290 additional fields)

The schema includes dedicated typed columns for 30 specialty workloads:

- **Copilot & AI Agents** (10 fields): CopilotEventData (dynamic), AgentId, AgentName, AgentType, etc.
- **Project for the web** (3 fields): ProjectEntity, ProjectAction, OnBehalfOfResId
- **eDiscovery** (19 fields): Case management, searches, holds, review sets, exports, queries
- **Security & Compliance Center** (8 fields): Cmdlet operations, parameters, version info
- **Security & Compliance Alerts** (12 fields): Alert management, policies, statuses, entities
- **Viva Engage (Yammer)** (16 fields): Messages, files, groups, network operations
- **Microsoft Defender for Office 365** (27 fields): Threat detection, email verdicts, attachments, delivery actions
- **Attack Simulation & Training** (15 fields): Campaigns, techniques, user training events
- **Submission** (12 fields): User and admin submissions, triage, notifications
- **Automated Investigation & Response (AIR)** (20 fields): Investigation details, actions, approvals, entities
- **Hygiene Events** (5 fields): Listing/delisting events and audit information
- **Power BI** (10 fields): Apps, dashboards, datasets, reports, workspaces, sharing
- **Viva Insights** (3 fields): User role and operation details
- **Quarantine** (4 fields): Request types, sources, release operations
- **Microsoft Forms** (6 fields): Form management, user types, activity parameters
- **MIP Label** (8 fields): Sensitivity labeling for email messages
- **Encrypted Message Portal** (8 fields): Message access authentication and operations
- **Reports** (1 field): Generic report operations
- **Compliance Connector** (10 fields): Third-party data connector import operations
- **SystemSync & Data Lake** (5 fields): Data store operations and exports
- **Viva Glint** (7 fields): Survey management and platform controls
- **Viva Goals** (10 fields): Organization and user activity tracking
- **Viva Pulse** (3 fields): EventName, PulseId, EventDetails
- **Backup/Restore** (17 fields): Policy, task, and item-level backup/restore operations
- **Edge WebContentFiltering** (3 fields): URL browsing and domain tracking
- **Copilot Scheduled Prompts** (4 fields): Scheduled automation execution
- **Places Directory** (3 fields): Workplace location management
- **Data Center Security Base** (1 field): DataCenterSecurityEventType
- **Data Center Security Cmdlet** (9 fields): ElevationTime, ElevationApprover, ElevationApprovedTime, ElevationRequestId, ElevationRole, ElevationDuration, GenericInfo, StartTime, EffectiveOrganization
- **Microsoft Sentinel Data Lake** (42 fields): Notebooks, Jobs, KQL queries, AI Tools, Graph operations, lake onboarding
- **DLP (Data Loss Prevention)** (6 fields): SharePointMetaData, ExchangeMetaData, EndpointMetaData, ExceptionInfo, PolicyDetails, SensitiveInfoDetectionIsIncluded

**Total Schema**: 304 columns utilizing 61% of Azure table capacity (500 column limit), leaving 39% headroom for future Microsoft API additions.

**Note**: DLP events from the DLP connector can be identified by filtering on `RecordType in (11, 13, 33, 63, 99, 100, 107, 187)`.

## Architecture

The solution creates a complete dual-connector data ingestion pipeline with **shared infrastructure**:

### Deployed Resources:
- **Data Collection Endpoint (DCE)**: `dce-{workspacename}-m365auditgeneral` - Shared network endpoint for secure data ingestion
- **Data Collection Rule (DCR)**: `dcr-{workspacename}-m365auditgeneral` - Shared data stream definition with transformation logic and filtering
- **Custom Table**: `M365AuditGeneral_CL` - Shared Log Analytics table with 304 structured columns covering 30 workload schemas
- **Audit.General Data Connector**: RestApiPoller for Audit.General content type
- **Audit.DLP Data Connector**: RestApiPoller for DLP.All content type

Both connectors share the same DCE, DCR, and table - differing only in the API endpoint they poll (contentType=Audit.General vs contentType=DLP.All).

### Data Flow:

1. **Authentication**: 
   - Connector uses OAuth 2.0 client credentials flow
   - Authenticates with your Entra ID app registration
   - Token endpoint uses subscription's tenant ID automatically

2. **First API Call** (Content Blob Metadata):
   - Polls: `https://manage.office.com/api/v1.0/{tenantId}/activity/feed/subscriptions/content?contentType=Audit.General`
   - Returns: Array of content blobs with `contentUri`, `contentId`, `contentType`, `contentCreated`
   - Frequency: Every 5 minutes

3. **Nested URL Extraction**:
   - KQL parser extracts `contentUri` from each blob metadata
   - Generates dynamic API endpoints for second-step calls

4. **Second API Calls** (Actual Audit Events):
   - Fetches from each `contentUri` (e.g., `https://manage.office.com/api/v1.0/{tenantId}/activity/feed/audit/...`)
   - Returns: Array of actual audit event records with full details

5. **Data Transformation**:
   - DCR applies KQL transform: `source | where RecordType != 21 and RecordType != 278 and RecordType != 25 and RecordType != 71 and RecordType != 72 and RecordType != 75 and RecordType != 82 and RecordType != 83 and RecordType != 84 and RecordType != 93 and RecordType != 94 and RecordType != 95 and RecordType != 96 and RecordType != 97`
   - **Intelligent filtering**: Excludes Dynamics 365 (RecordTypes 21, 278), Teams (RecordType 25), and Microsoft Purview Information Protection (RecordTypes 71, 72, 75, 82, 83, 84, 93, 94, 95, 96, 97) events to avoid duplication with dedicated connectors
   - **Automatic type mapping**: DCR engine handles type conversions based on schema declarations
   - Projects 304 structured columns across 30 workload schemas

6. **Ingestion**:
   - Transformed data sent to custom table via DCE
   - Data appears in `M365AuditGeneral_CL` within minutes

## References

- [Office 365 Management Activity API Reference](https://docs.microsoft.com/office/office-365-management-api/office-365-management-activity-api-reference)
- [Office 365 Management Activity API Schema](https://docs.microsoft.com/office/office-365-management-api/office-365-management-activity-api-schema)
- [Microsoft Sentinel Codeless Connector Platform (CCP)](https://learn.microsoft.com/azure/sentinel/create-codeless-connector)
- [Azure Monitor Data Collection Rules](https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview)
- [Microsoft Entra ID App Registrations](https://learn.microsoft.com/entra/identity-platform/quickstart-register-app)
