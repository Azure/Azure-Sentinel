---
applyTo: "Detections/**/*.yaml,Detections/**/*.yml,Solutions/**/Analytic Rules/*.yaml,**/Analytic Rules/*.yaml"
---

# Analytic Rules (Detection Rules) Instructions

## Overview

Analytic Rules are YAML files that define scheduled queries to detect threats, suspicious activities, and security incidents in Microsoft Sentinel. These rules serve as the core detection logic for security operations, automatically creating alerts and incidents when suspicious patterns are identified in ingested data.

## Validation Rules for PR Reviews

### Field-Based Validation Reference

#### **id** (Unique Identifier)
- **Required**: Yes (all rule types)
- **Format**: Standard GUID format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (any valid hex digits)
- **Validation**: `/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/`
- **Rules**:
  - Must be unique across all rules
  - Should never be reused
  - Generated using proper GUID generators (PowerShell `New-GUID`, online GUID generators, etc.)
  - **Note**: Accepts any valid GUID format (not strictly UUID v4 variant bits)
  - Valid formats include GUIDs starting with any hex digit in any position (e.g., `d` in 4th group is valid)
- **Valid Examples**: 
  - `e46c5588-e643-4a60-a008-5ba9a4c84328` ✅
  - `d1234567-89ab-cdef-0123-456789abcdef` ✅ (4th group starting with 'd' is valid)
  - `a0000000-0000-0000-0000-000000000000` ✅ (any position can have any hex digit)

#### **name** (Rule Name)
- **Required**: Yes (all rule types)
- **Format**: Sentence case label
- **Constraints**: Target 50 characters when possible; Hard limit 100 characters
- **Capitalization**: Sentence case (capitalize first word and proper nouns only)
- **Punctuation**: Do NOT end with a period
- **Rules**:
  - Should clearly convey what the detection is about without reading full description
  - Make clear which entities are performing suspicious activities on which datatype
  - Start with vendor/product name when applicable
  - Avoid generic terms; use specific, descriptive language
  - Can use `alertDetailsOverride` to provide dynamic names for better analyst context

**Terms to Avoid vs. Use Instead**:
| Avoid | Use Instead |
|-------|-------------|
| IP | IPAddress |
| Execute | Run |
| Suspicious, Suspect | Unexpected, Anomalous, Rare |

- **Valid Examples**: 
  - `Multiple failed logon attempts from single IP` ✅
  - `Unusual volume of DNS queries from host` ✅
  - `Impossible travel alert` ✅
- **Invalid Examples**: 
  - `Suspicious Activity` ❌ (too generic)
  - `Bad Login` ❌ (too vague)
  - `Suspicious Activity.` ❌ (ends with period)

#### **description** (Rule Description)
- **Required**: Yes (all rule types)
- **Format**: Comprehensive narrative text (max 255 characters)
- **Opening**: Must start with "This query searches for" or "Identifies"
- **Length**: Should be maximum 5 sentences
- **Rules**:
  - Is NOT a copy of the name field - must be more descriptive
  - Details the purpose of the query with references such as EventID explanations or URL references
  - Can use `alertDetailsOverride` for dynamic descriptions to help analysts understand alerts faster
  - Do NOT describe the data source (connector or datatype)
  - Do NOT provide technical explanation for query language used
  - Use standard English capitalization

**What NOT to do** (too vague or too technical):
- ❌ "Detects scanning activity"
- ❌ "Identifies clients with high reverse DNS count carrying out scanning activity. Alert is generated if the IP performing such reverse DNS lookups was not seen doing so in the preceding 7-day period"

**Instead do this** (specific and clear):
- ✅ "This query identifies IP addresses performing a high rate of reverse DNS lookups and has not been seen doing this lookup in the previous 7 days"

#### **severity** (Alert Severity)
- **Required**: Yes for Detections only
- **Valid Values**: `Low`, `Medium`, `High`, `Informational`
- **Invalid Values**: `Critical` ❌ (not a valid severity level)
- **Definition**: The level of impact on a target environment caused by the activity the analytic is triggered on should it be a true positive
- **Guidelines**:
  - **High**: Activity identified provides threat actor with wide-ranging access to conduct actions on environment or is triggered by impact on environment. Immediate response required.
  - **Medium**: Threat actor could perform some impact on environment with this activity, but limited in scope or requires additional activity. Prompt investigation needed.
  - **Low**: Immediate impact is minimal; threat actor needs to conduct multiple steps before achieving impact. Monitoring recommended.
  - **Informational**: May not represent direct security threat but may be of interest for follow-up investigation or add context/situational awareness to analyst. No immediate action needed.
- **Additional Notes**:
  - Severity level defaults are not a guarantee of current or environment impact level
  - This applies only to Azure Sentinel analytic templates
  - Can use `alertDetailsOverride` to provide dynamic severity based on actual query outcome

#### **status** (Deployment Status)
- **Required**: Yes (all rule types)
- **Valid Values**: `Available`, `InPreview`, `Deprecated`
- **Rules**:
  - `Available`: Production-ready rules
  - `InPreview`: Beta/testing rules
  - `Deprecated`: Legacy rules being phased out

#### **kind** (Rule Type)
- **Required**: Yes (all rule types)
- **Valid Values**: `Scheduled`, `Fusion`, `MicrosoftSecurityIncidentCreation`, `MLBehaviorAnalytics`, `NRT`
- **Determines**: Required fields for specific rule type
- **Rules**:
  - Each kind has specific field requirements
  - Cannot mix fields from different kinds
  - Validation must account for kind-specific requirements

#### **version** (Semantic Version)
- **Required**: Yes (all rule types)
- **Format**: Semantic versioning `X.Y.Z`
- **Pattern**: `/^\d+\.\d+\.\d+$/`
- **Example**: `1.2.3` ✅

#### **tactics** (MITRE ATT&CK Tactics)
- **Required**: Yes (all rule types)
- **Framework Version**: ATT&CK Framework v16 Supported
- **Reference**: https://attack.mitre.org/versions/v16/matrices/enterprise/
- **Type**: Array of strings
- **Format**: PascalCase without spaces
- **Rules**:
  - Names MUST NOT have any spaces (use PascalCase)
  - Maximum 5 tactics per rule
  - Must align with detected behavior
  - Can use `alertDetailsOverride` to provide dynamic tactics based on query outcome
  - Invalid format: `"Initial Access"` ❌ (should be `InitialAccess`)
  - Common misspellings to avoid: `"Reconnaisance"` ❌ (correct: `Reconnaissance`), `"Resource Development"` ❌ (correct: `ResourceDevelopment`)
- **Valid Tactics** (14 total - MITRE ATT&CK v16 Enterprise): 
  - `Reconnaissance`, `ResourceDevelopment`, `InitialAccess`, `Execution`
  - `Persistence`, `PrivilegeEscalation`, `DefenseEvasion`, `CredentialAccess`
  - `Discovery`, `LateralMovement`, `Collection`, `CommandAndControl`
  - `Exfiltration`, `Impact`
- **PR Review Feedback Format**: When reporting invalid tactics, include the MITRE reference in the comment:
  - **IMPORTANT - Tactics Feedback:** When providing feedback on tactics (e.g., incorrect spelling like "Reconnaisance" instead of "Reconnaissance"), **ALWAYS include reference to:** https://attack.mitre.org/versions/v16/matrices/enterprise/
  - ✅ *Example feedback format:* "The tactic 'Reconnaisance' is misspelled. The correct keyword is 'Reconnaissance'. Please refer to the MITRE ATT&CK v16 enterprise matrix: https://attack.mitre.org/versions/v16/matrices/enterprise/ for the complete list of valid tactics."

#### **relevantTechniques** (MITRE ATT&CK Techniques)
- **Required**: Yes (all rule types)
- **Framework Version**: ATT&CK Framework v16 Supported
- **Reference**: https://attack.mitre.org/versions/v16/techniques/enterprise/
- **Type**: Array of strings
- **Format**: `T####` (technique) or `T####.###` (sub-technique)
- **Pattern**: `/^T\d{4}(\.\d{3})?$/`
- **Rules**:
  - MUST match MITRE ATT&CK Techniques or Sub-techniques exactly
  - Prefer sub-techniques when they better describe the detection (e.g., `T1078.001`)
  - Maximum 10 techniques per rule
  - Must align with tactics
  - Invalid formats: `1078` ❌, `T1078.001.002` ❌ (too many sub-technique levels)
  - Each technique should support at least one tactic mapped to the rule
- **Valid Examples**: `T1078`, `T1078.001`, `T1595.003`, `T1190` ✅
- **PR Review Feedback Format**: When reporting invalid techniques, include the MITRE reference in the comment:
  - **IMPORTANT - Techniques Feedback:** When providing feedback on techniques (e.g., invalid technique ID or incorrect format), **ALWAYS include reference to:** https://attack.mitre.org/versions/v16/techniques/enterprise/
  - ✅ *Example feedback format:* "The technique 'T1078' is valid, but ensure it aligns with your tactic. For a comprehensive list of all techniques and sub-techniques, refer to: https://attack.mitre.org/versions/v16/techniques/enterprise/"

#### **query** (KQL Detection Query)
- **Required**: Yes for `Scheduled` and `NRT` rules
- **Required**: No for `Fusion`, `MLBehaviorAnalytics`, `MicrosoftSecurityIncidentCreation`
- **Reference**: https://learn.microsoft.com/kusto/query/best-practices
- **Rules**:
  - Must be valid KQL syntax
  - Should include filtering for performance
  - For NRT: Must include recent time filter like `ago(5m)`
  - Well-structured and maintainable
  - Include early filtering to reduce data processing
- **KQL Best Practices** (from Microsoft Kusto documentation):
  - **Reduce data processing**: Apply `where` operator immediately after table references to filter early and reduce dataset size
  - **Use efficient string operators**: Prefer `has` (token-level search) over `contains` (substring search); use `==` (case-sensitive) over `=~`
  - **Optimize filters**: Apply datetime filters first (most efficient), then string/dynamic filters (ordered by selectivity), then numeric filters
  - **Avoid common mistakes**: Don't use wildcard `*` for full table scans; don't use `tolower()` on large datasets (use `=~` instead); don't create redundant columns for filtering
  - **Use materialization wisely**: Use `materialize()` for `let` statements referenced multiple times; extract fields from dynamic objects at ingestion time if querying millions of rows
  - **Limit unbounded queries**: Always use `limit [small number]` or `count` during development to avoid processing gigabytes of unexpected data
  - **Refer to complete guide**: https://learn.microsoft.com/kusto/query/best-practices

#### **queryFrequency** (Execution Frequency)
- **Required**: Yes for `Scheduled` rules only
- **Type**: Timespan string in KQL format (e.g., `1h`, `5m`, `1d`)
- **Range**: Can run as frequently as every 5 minutes to as infrequently as every 2 weeks
- **Rules**:
  - Must be less than or equal to `queryPeriod`
  - If `queryPeriod >= 2d`, then `queryFrequency` must NOT be less than 1h (1h minimum for performance)
  - 1h minimum is only exception for High severity detections with longer periods
  - Customer can adjust lower if they see fit, but default should not impact performance
- **Performance Recommendations**:
  - **5-15m**: Critical real-time detections
  - **1h-4h**: Most detection scenarios
  - **1d+**: Baseline analysis, trend detection

#### **queryPeriod** (Data Analysis Window)
- **Required**: Yes for `Scheduled` rules only
- **Type**: Timespan string in KQL format (e.g., `1h`, `14d`)
- **Maximum**: 14 days (technical limitation)
- **Rules**:
  - Any learning or reference period MUST be included within this time
  - Must be >= `queryFrequency`
  - Recommended maximum: 14 days (performance can be impacted beyond this)
  - Must be expressed in KQL TimeSpan Format
- **Invalid Example**: `queryFrequency: 1h, queryPeriod: 30m` ❌ (period cannot be less than frequency)

#### **triggerOperator** (Threshold Comparison)
- **Required**: Yes for `Scheduled` rules only
- **Type**: String operator
- **Valid Values**: `gt` (Greater Than), `lt` (Less Than), `eq` (Equal To)
- **Description**: Indicates the mechanism that triggers the alert (e.g., greater than a count of 6)
- **Rules**:
  - Only `gt`, `lt`, and `eq` are supported
  - Used with `triggerThreshold` to determine alert firing
  - Combined with threshold value to define alert trigger condition

#### **triggerThreshold** (Alert Threshold Value)
- **Required**: Yes for `Scheduled` rules only
- **Type**: Integer
- **Valid Range**: 0 to 10,000
- **Description**: The threshold count related to the mechanism that triggers the alert
- **Rules**:
  - Combined with `triggerOperator` to trigger alerts
  - If operator is `gt` (Greater Than) and threshold is 1, alert triggers if query results > 1
  - Must be meaningful for the detection context

#### **requiredDataConnectors** (Data Source Dependencies)
- **Required**: Yes for `Scheduled` and `NRT` rules
- **Type**: Array of connector objects
- **Structure**:
  ```yaml
  requiredDataConnectors:
    - connectorId: CiscoDuoSecurity
      dataTypes:
        - CiscoDuo
    - connectorId: AzureActiveDirectory
      dataTypes:
        - SigninLogs
        - AuditLogs
  ```
- **Rules**:
  - Must include all connectors required for query execution
  - Specify exact data types needed
  - Use official connector IDs

#### **entityMappings** (Entity Extraction)
- **Required**: Yes for Detections
- **Type**: Array of entity mapping objects
- **Maximum Limits**:
  - Up to 10 entity mappings per template
  - Up to 3 field mappings (identifiers) per entity mapping
- **Format**:
  ```yaml
  entityMappings:
    - entityType: Account
      fieldMappings:
        - identifier: FullName
          columnName: AccountCustomEntity
        - identifier: Name
          columnName: AccountName
    - entityType: Host
      fieldMappings:
        - identifier: FullName
          columnName: HostCustomEntity
  ```
- **Valid Entity Types** (case-sensitive) - 20 types:
  - `Account`, `Host`, `IP`, `URL`, `Malware`, `File`, `FileHash`, `Process`, `CloudApplication`, `DNS`, `AzureResource`, `RegistryKey`, `RegistryValue`, `SecurityGroup`, `IoTDevice`, `Mailbox`, `MailCluster`, `MailMessage`, `SubmissionMail`, `SentinelEntities`

- **Entity Type Identifiers** (valid identifiers for each type per Azure Sentinel docs):
  - **Account**: Name, FullName, NTDomain, DnsDomain, UPNSuffix, Sid, AadTenantId, AadUserId, PUID, IsDomainJoined, DisplayName, ObjectGuid, CloudAppAccountId, IsAnonymized
    - *Strong identifiers*: Name+UPNSuffix, AadUserId, Sid, Sid+Host, Name+NTDomain, Name+NTDomain+Host, Name+DnsDomain, PUID, ObjectGuid
  - **Host**: DnsDomain, NTDomain, HostName, FullName, NetBiosName, AzureID, OMSAgentID, OSFamily, OSVersion, IsDomainJoined
    - *Strong identifiers*: HostName+NTDomain, HostName+DnsDomain, NetBiosName+NTDomain, NetBiosName+DnsDomain, AzureID, OMSAgentID
  - **IP**: Address, AddressScope
    - *Strong identifiers*: Address (if global), Address+AddressScope (if private)
  - **URL**: Url
    - *Strong identifiers*: Url (if absolute)
  - **File**: Directory, Name, AlternateDataStreamName
    - *Strong identifiers*: Name+Directory
  - **FileHash**: Algorithm, Value
    - *Strong identifiers*: Algorithm+Value
  - **Process**: ProcessId, CommandLine, ElevationToken, CreationTimeUtc, ImageFile
    - *Strong identifiers*: Host+ProcessId+CreationTimeUtc, Host+ParentProcessId+CreationTimeUtc+CommandLine, Host+ProcessId+CreationTimeUtc+ImageFile
  - **CloudApplication**: AppId, SaasId, Name, InstanceName, InstanceId
    - *Strong identifiers*: AppId, Name, AppId+InstanceName, Name+InstanceName
  - **DNS**: DomainName, DnsServerIp, HostIpAddress
    - *Strong identifiers*: DomainName+DnsServerIp+HostIpAddress
  - **AzureResource**: ResourceId, SubscriptionId
    - *Strong identifiers*: ResourceId
  - **RegistryKey**: Hive, Key
    - *Strong identifiers*: Hive+Key
  - **RegistryValue**: Name, Value, ValueType, Key, Host
    - *Strong identifiers*: Key+Name
  - **SecurityGroup**: DistinguishedName, SID, ObjectGuid
    - *Strong identifiers*: DistinguishedName, SID, ObjectGuid
  - **Malware**: Name, Category
    - *Strong identifiers*: Name+Category
  - **IoTDevice**: DeviceId, IoTHub, DeviceName, Owners, DeviceType
    - *Strong identifiers*: IoTHub+DeviceId
  - **Mailbox**: MailboxPrimaryAddress, DisplayName, Upn, AadId, RiskLevel, ExternalDirectoryObjectId
    - *Strong identifiers*: MailboxPrimaryAddress
  - **MailCluster**: Query, Source, NetworkMessageIds, Threats, MailCount
    - *Strong identifiers*: Query+Source
  - **MailMessage**: Recipient, Sender, Subject, NetworkMessageId, SenderIP, ReceivedDate
    - *Strong identifiers*: NetworkMessageId+Recipient
  - **SubmissionMail**: SubmissionId, NetworkMessageId, Recipient, Submitter, Timestamp
    - *Strong identifiers*: SubmissionId+NetworkMessageId+Recipient+Submitter
  - **SentinelEntities**: Entities (custom entities list)

- **Rules**:
  - At least one entity mapping required
  - Entity type MUST match exactly (case-sensitive)
  - Identifiers MUST match property names for the entity type (case-sensitive)
  - Column name referenced for `columnName` must be an output from the query
  - Use "CustomEntity" suffix for naming convention when possible
  - Use `FullName` as identifier for both Account and Host (special mapping)

#### **productFilter** (Security Product Filter)
- **Required**: Yes for `MicrosoftSecurityIncidentCreation` rules only
- **Type**: String
- **Valid Examples**: `Microsoft Cloud App Security`, `Microsoft Defender for Office 365`
- **Rules**:
  - Required only for this rule kind
  - Should not appear in other rule types

---

### Advanced Configuration Options

#### **customDetails** (Optional)
- **Optional**: Yes
- **Type**: Key-value pairs (property name → column name)
- **Maximum**: 20 custom details per template
- **Purpose**: Surface event data in alerts for immediate visibility in security incidents
- **Format**:
  ```yaml
  customDetails:
    EventCount: EventCount
    IPs: ComputerIP
    Computers: Computer
    # Up to 20 custom details
  ```
- **Rules**:
  - Column name must be an output from the query
  - Enables faster triaging, investigation, and response
  - More info: [Surface Custom Details in Alerts](https://docs.microsoft.com/en-us/azure/sentinel/surface-custom-details-in-alerts)

#### **alertDetailsOverride** (Optional)
- **Optional**: Yes
- **Purpose**: Provide dynamic values for alert name, description, tactics, and severity
- **Limits**:
  - Maximum 3 parameters per name or description
  - Name: max 256 characters
  - Description: max 5000 characters
  - Column names in braces must match exactly (no leading/trailing whitespace)
- **Format**:
  ```yaml
  alertDetailsOverride:
    alertDisplayNameFormat: "rule {{columnName1}} display name"
    alertDescriptionFormat: "rule {{columnName2}} display name"
    alertTacticsColumnName: dynamicTactic
    alertSeverityColumnName: dynamicSeverity
  ```
- **Rules**:
  - Allows same rule to generate different incidents with different severity
  - Can include variable information like entity names to help analysts
  - Column names must be output fields from the detection query

#### **eventGroupingSettings** (Optional)
- **Optional**: Yes
- **Purpose**: Control alert aggregation behavior
- **Valid Values**: `SingleAlert` (default) or `AlertPerResult`
- **Format**:
  ```yaml
  eventGroupingSettings:
    aggregationKind: SingleAlert      # Single alert for all query results
    # OR
    aggregationKind: AlertPerResult   # One alert per query result
  ```
- **Rules**:
  - Use `AlertPerResult` when each result should create separate alert
  - Useful for multi-source alert rules or when individual results need tracking

#### **incidentConfiguration** (Optional)
- **Optional**: Yes
- **Purpose**: Configure incident creation and grouping behavior
- **Format**:
  ```yaml
  incidentConfiguration:
    createIncident: true
    groupingConfiguration:
      enabled: true
      reopenClosedIncident: false
      lookbackDuration: 5m
      matchingMethod: Selected
      groupByEntities: []
      groupByAlertDetails: []
      groupByCustomDetails:
        - WorkbenchID
  ```
- **Rules**:
  - `createIncident`: Enable/disable incident creation
  - `groupingConfiguration`: Group alerts into incidents by specified criteria
  - `lookbackDuration`: How far back to look for related alerts
  - `matchingMethod`: How to match alerts (Selected, AllEntities)

#### **suppressionEnabled** & **suppressionDuration** (Optional)
- **Optional**: Yes
- **Purpose**: Suppress duplicate or similar alerts
- **Format**:
  ```yaml
  suppressionEnabled: false              # Disabled by default
  suppressionDuration: 5h                # Suppress for 5 hours
  ```
- **Rules**:
  - Use to reduce alert fatigue
  - Works with trigger conditions to determine suppression behavior
  - Common durations: 1h, 5h, 1d

#### **tags** (Optional)
- **Optional**: Yes
- **Purpose**: Add metadata about the rule for organization and filtering
- **Format**:
  ```yaml
  tags:
    - Schema: WebSession
      SchemaVersion: 0.2.6
    - ConnectorId: CustomConnector
  ```
- **Rules**:
  - Can include ASIM schema compliance information
  - Can reference connector associations
  - Useful for categorizing and filtering rules

#### **alertRuleTemplateName** (Optional)
- **Optional**: Yes
- **Type**: String (usually null)
- **Purpose**: Reference to template this rule was created from
- **Default**: null

#### **sentinelEntitiesMappings** (Optional)
- **Optional**: Yes
- **Purpose**: Include all entities identified in alert
- **Format**:
  ```yaml
  sentinelEntitiesMappings:
    - columnName: Entities
  ```
- **Rules**:
  - Uses entities from SecurityAlert schema
  - Provides list of all identified entities in alert

---

### Comprehensive Validation Functions

```typescript
function validateAnalyticRuleByField(rule: AnalyticRule): ValidationResult {
  const validationResults = {
    id: validateIdField(rule.id),
    name: validateNameField(rule.name),
    description: validateDescriptionField(rule.description),
    severity: validateSeverityField(rule.severity),
    status: validateStatusField(rule.status),
    kind: validateKindField(rule.kind),
    version: validateVersionField(rule.version),
    tactics: validateTacticsField(rule.tactics),
    relevantTechniques: validateTechniquesField(rule.relevantTechniques),
    query: validateQueryField(rule.query, rule.kind),
    queryFrequency: validateQueryFrequencyField(rule.queryFrequency, rule.kind),
    queryPeriod: validateQueryPeriodField(rule.queryPeriod, rule.queryFrequency, rule.kind),
    triggerOperator: validateTriggerOperatorField(rule.triggerOperator, rule.kind),
    triggerThreshold: validateTriggerThresholdField(rule.triggerThreshold, rule.kind),
    requiredDataConnectors: validateDataConnectorsField(rule.requiredDataConnectors, rule.kind),
    entityMappings: validateEntityMappingsField(rule.entityMappings),
    productFilter: validateProductFilterField(rule.productFilter, rule.kind)
  };
  
  return validationResults;
}

// Individual field validators
function validateIdField(id: string): FieldValidation {
  const guidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
  return {
    field: 'id',
    required: true,
    valid: guidPattern.test(id),
    format: 'GUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)',
    errors: !guidPattern.test(id) ? ['Invalid GUID format'] : []
  };
}

function validateNameField(name: string): FieldValidation {
  return {
    field: 'name',
    required: true,
    valid: name && name.length > 0 && name.length <= 100,
    format: 'Non-empty string, max 100 characters',
    errors: [
      !name ? 'Name cannot be empty' : null,
      name?.length > 100 ? 'Name exceeds 100 characters' : null,
      name?.match(/^(Suspicious|Bad|Unusual|Anomal|Generic)/) ? 'Name appears too generic' : null
    ].filter(Boolean)
  };
}

function validateSeverityField(severity: string): FieldValidation {
  const validSeverities = ['Low', 'Medium', 'High', 'Informational'];
  return {
    field: 'severity',
    required: true,
    valid: validSeverities.includes(severity),
    format: 'One of: Low, Medium, High, Informational',
    validValues: validSeverities,
    errors: !validSeverities.includes(severity) ? [`Invalid severity: ${severity}`] : []
  };
}

function validateTacticsField(tactics: string[]): FieldValidation {
  const validTactics = [
    'Reconnaissance', 'ResourceDevelopment', 'InitialAccess', 'Execution',
    'Persistence', 'PrivilegeEscalation', 'DefenseEvasion', 'CredentialAccess',
    'Discovery', 'LateralMovement', 'Collection', 'CommandAndControl',
    'Exfiltration', 'Impact'
  ];
  const errors: string[] = [];
  
  if (!tactics || tactics.length === 0) errors.push('At least one tactic required');
  if ((tactics?.length || 0) > 5) errors.push('Maximum 5 tactics allowed');
  
  tactics?.forEach(tactic => {
    if (!validTactics.includes(tactic)) {
      errors.push(`Invalid tactic: ${tactic}`);
    }
  });
  
  return {
    field: 'tactics',
    required: true,
    valid: errors.length === 0,
    format: 'Array of valid MITRE ATT&CK tactics (max 5)',
    validValues: validTactics,
    count: tactics?.length || 0,
    errors
  };
}

function validateTechniquesField(techniques: string[]): FieldValidation {
  const techniquePattern = /^T\d{4}(\.\d{3})?$/;
  const errors: string[] = [];
  
  if (!techniques || techniques.length === 0) errors.push('At least one technique required');
  if ((techniques?.length || 0) > 10) errors.push('Maximum 10 techniques allowed');
  
  techniques?.forEach(technique => {
    if (!techniquePattern.test(technique)) {
      errors.push(`Invalid technique format: ${technique} (should be T#### or T####.###)`);
    }
  });
  
  return {
    field: 'relevantTechniques',
    required: true,
    valid: errors.length === 0,
    format: 'Array of MITRE ATT&CK technique IDs (T#### or T####.###, max 10)',
    count: techniques?.length || 0,
    errors
  };
}

function validateQueryFrequencyField(frequency: string, kind: string): FieldValidation {
  const isRequired = ['Scheduled'].includes(kind);
  if (!isRequired) {
    return {
      field: 'queryFrequency',
      required: false,
      valid: true,
      format: 'Timespan (e.g., 5m, 1h)',
      errors: []
    };
  }
  
  const errors: string[] = [];
  if (!frequency) errors.push('queryFrequency required for Scheduled rules');
  
  const minutes = parseTimespan(frequency);
  if (minutes < 5) errors.push('Minimum frequency: 5 minutes');
  
  return {
    field: 'queryFrequency',
    required: isRequired,
    valid: errors.length === 0,
    format: 'Timespan (e.g., 5m, 1h, 1d), minimum 5m',
    errors
  };
}

function validateQueryPeriodField(period: string, frequency: string, kind: string): FieldValidation {
  const isRequired = ['Scheduled'].includes(kind);
  if (!isRequired) {
    return {
      field: 'queryPeriod',
      required: false,
      valid: true,
      format: 'Timespan (e.g., 1h, 14d)',
      errors: []
    };
  }
  
  const errors: string[] = [];
  if (!period) errors.push('queryPeriod required for Scheduled rules');
  
  const periodMinutes = parseTimespan(period);
  const frequencyMinutes = parseTimespan(frequency);
  
  if (periodMinutes < 5) errors.push('Minimum period: 5 minutes');
  if (periodMinutes < frequencyMinutes) errors.push('Period cannot be less than frequency');
  if (periodMinutes / frequencyMinutes > 168) errors.push('Period ratio exceeds maximum (1 week)');
  
  return {
    field: 'queryPeriod',
    required: isRequired,
    valid: errors.length === 0,
    format: 'Timespan >= queryFrequency',
    errors
  };
}

function validateEntityMappingsField(entityMappings: EntityMapping[]): FieldValidation {
  const validEntityTypes = [
    'Account', 'Host', 'IP', 'URL', 'Malware', 'File', 'FileHash', 'Process',
    'CloudApplication', 'DNS', 'AzureResource', 'RegistryKey', 'RegistryValue',
    'SecurityGroup', 'IoTDevice', 'Mailbox', 'MailCluster', 'MailMessage',
    'SubmissionMail', 'SentinelEntities'
  ];
  const errors: string[] = [];
  
  if (!entityMappings || entityMappings.length === 0) {
    errors.push('At least one entity mapping required');
  }
  
  entityMappings?.forEach((mapping, idx) => {
    if (!validEntityTypes.includes(mapping.entityType)) {
      errors.push(`Entity ${idx}: Invalid entity type "${mapping.entityType}"`);
    }
    if (!mapping.fieldMappings || mapping.fieldMappings.length === 0) {
      errors.push(`Entity ${idx}: Must have fieldMappings`);
    }
  });
  
  return {
    field: 'entityMappings',
    required: true,
    valid: errors.length === 0,
    format: 'Array of entity mapping objects with valid entity types',
    validEntityTypes,
    count: entityMappings?.length || 0,
    errors
  };
}
```

## Quality Assurance Guidelines

### Detection Quality Considerations
```typescript
interface DetectionQuality {
  completeness: string;              // Are all essential fields present and meaningful?
  mitreAlignment: string;           // Do MITRE mappings accurately reflect the detection?
  queryDesign: string;              // Is the query well-structured and maintainable?
  entityRelevance: string;          // Are extracted entities valuable for investigation?
  documentationClarity: string;     // Is the purpose and usage clear?
  practicalValue: string;           // Does this detection provide actionable security value?
}
```

### Detection Coverage Analysis
```typescript
interface DetectionCoverage {
  dataSourcesRequired: string[];     // Required data connectors
  mitreMapping: {
    tactics: string[];
    techniques: string[];
  };
  severityDistribution: {
    high: number;
    medium: number;
    low: number;
    informational: number;
  };
  detectionFrequency: string;        // Real-time/Hourly/Daily
  entityTypes: string[];             // Mapped entity types
}
```

## Common Review Considerations

### 💡 **Field Completeness**
```yaml
name: "Suspicious Activity"
description: "Detects bad things"
# Consider: Are essential fields present? Is the information meaningful?
```

### 💡 **Unique Identification**
```yaml
id: "invalid-guid-format"           # Consider: Is this a proper unique identifier?
```

### 💡 **Descriptive Naming**
```yaml
name: "Suspicious Login"            # Consider: "Multiple Failed Login Attempts from Single IP" - more specific
```

### ❌ **Incorrect MITRE Mapping**
```yaml
tactics:
  - "Initial Access"                # Should be "InitialAccess" (no spaces)
relevantTechniques:
  - "1078"                         # Should be "T1078"
```

### ❌ **Invalid Query Timing**
```yaml
queryFrequency: 1h
queryPeriod: 30m                   # Period cannot be less than frequency
```

### ❌ **Missing Entity Mappings**
```yaml
query: |
  SecurityEvent
  | where EventID == 4625
  | extend AccountCustomEntity = Account
# Missing entityMappings section
```

### ❌ **Unoptimized KQL Query**
```yaml
query: |
  SecurityEvent                    # Should filter early
  | summarize count() by Account
  | where EventID == 4625         # Filter should be applied earlier
```

### ❌ **Incorrect Kind-Specific Configuration**
```yaml
# NRT rule with scheduling fields (should not have these)
kind: NRT
queryFrequency: 5m                 # ❌ NRT rules don't use scheduling
queryPeriod: 5m                    # ❌ NRT rules don't use periods
query: |
  SecurityEvent | where EventID == 4625
```

```yaml
# Fusion rule with custom query (should not have query)
kind: Fusion
query: |                           # ❌ Fusion rules are managed by AI
  SecurityEvent | where EventID == 4625
```

```yaml
# MicrosoftSecurityIncidentCreation without productFilter
kind: MicrosoftSecurityIncidentCreation
# Missing: productFilter field is required
query: |                           # ❌ Should not have custom query
  SecurityEvent | where EventID == 4625
```

```yaml
# Scheduled rule without required timing fields
kind: Scheduled
query: |
  SecurityEvent | where EventID == 4625
# Missing: queryFrequency, queryPeriod, triggerOperator, triggerThreshold
```

## Best Practices for Analytic Rules

### 1. **Detection Logic Philosophy**
- **Actionability**: Design detections that provide clear, investigatable alerts
- **Balance**: Consider the trade-off between detection coverage and false positive rates
- **Context**: Incorporate environmental context and baseline behavior when possible
- **Evolution**: Design rules that can adapt to changing threat landscapes
- **Validation**: Consider how the detection logic can be tested and validated

### 2. **Query Design Principles**
- **Efficiency**: Structure queries to process data effectively
- **Maintainability**: Write queries that are easy to understand and modify
- **Scalability**: Consider performance impact on large data volumes
- **Reliability**: Design queries that work consistently across different data conditions
- **Testing**: Validate query logic against known scenarios

### 3. **MITRE ATT&CK Integration**
- **Precision**: Map to specific techniques that reflect actual detected behavior
- **Accuracy**: Ensure tactics and techniques align with the detection purpose
- **Currency**: Keep mappings updated with evolving MITRE framework
- **Documentation**: Explain the reasoning behind technique selections
- **Granularity**: Prefer sub-techniques when they better describe the detection

### 4. **Entity Strategy**
- **Relevance**: Extract entities that add investigative value
- **Consistency**: Follow naming conventions that support automation
- **Completeness**: Include identifiers that enable effective pivoting
- **Relationships**: Consider how entities relate to each other in the context
- **Standards**: Align with established entity models when possible

### 5. **Documentation Excellence**
- **Clarity**: Write descriptions that clearly explain the threat being detected
- **Context**: Provide background on why this detection is valuable
- **Guidance**: Include investigation tips and expected false positive scenarios
- **References**: Link to relevant threat intelligence or security research
- **Maintenance**: Keep documentation current as threats evolve

## Advanced Detection Patterns

### Behavioral Analytics
```yaml
query: |
  // Detect anomalous user behavior using time series analysis
  let lookback = 14d;
  let threshold = 3.0; // Standard deviations from normal
  
  SigninLogs
  | where TimeGenerated >= ago(lookback)
  | make-series LoginCount = count() on TimeGenerated step 1h by UserPrincipalName
  | extend (anomalies, score, baseline) = series_decompose_anomalies(LoginCount, threshold)
  | mv-expand TimeGenerated, LoginCount, anomalies, score, baseline
  | where anomalies > 0
```

### Threat Intelligence Integration
```yaml
query: |
  // Correlate network traffic with threat intelligence feeds
  let TI_Indicators = ThreatIntelligenceIndicator
      | where TimeGenerated >= ago(30d)
      | where Active == true
      | where NetworkIP != ""
      | project NetworkIP, ThreatType, Description;
  
  CommonSecurityLog
  | join kind=inner TI_Indicators on $left.DestinationIP == $right.NetworkIP
  | project TimeGenerated, SourceIP, DestinationIP, ThreatType, Description
```

### Multi-Stage Detection
```yaml
query: |
  // Detect multi-stage attack progression
  let Stage1 = SecurityEvent
      | where EventID == 4625 // Failed logon
      | project TimeGenerated, Account, WorkstationName, IpAddress;
  
  let Stage2 = SecurityEvent
      | where EventID == 4624 // Successful logon
      | project TimeGenerated, Account, WorkstationName, IpAddress;
  
  Stage1
  | join kind=inner Stage2 on Account, IpAddress
  | where Stage2.TimeGenerated > Stage1.TimeGenerated
  | where Stage2.TimeGenerated - Stage1.TimeGenerated < 1h
```

## Automated Validation Framework

### Schema Validation
```typescript
const analyticRuleSchema = {
  required: ['id', 'name', 'description', 'severity', 'status', 'requiredDataConnectors', 
             'queryFrequency', 'queryPeriod', 'triggerOperator', 'triggerThreshold',
             'tactics', 'relevantTechniques', 'query', 'entityMappings', 'version', 'kind'],
  properties: {
    id: { type: 'string', pattern: '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' },
    severity: { enum: ['Low', 'Medium', 'High', 'Informational'] },
    status: { enum: ['Available', 'InPreview', 'Deprecated'] },
    kind: { enum: ['Scheduled', 'Fusion', 'MicrosoftSecurityIncidentCreation', 'MLBehaviorAnalytics', 'NRT'] },
    version: { pattern: '^\\d+\\.\\d+\\.\\d+$' }
  }
};
```

### Comprehensive Rule Validation
```typescript
function validateAnalyticRule(rulePath: string): ValidationResult {
  const rule = parseYAML(fs.readFileSync(rulePath));
  
  return {
    structureValid: validateYAMLStructure(rule),
    kindValid: validateRuleKind(rule),
    mitreValid: validateMITREMapping(rule),
    timingValid: validateQueryTiming(rule), // Only for Scheduled/NRT rules
    entityMappingValid: validateEntityMappings(rule),
    queryValid: rule.query ? validateKQLSyntax(rule.query) : { valid: true, reason: 'No query required for this kind' },
    performanceOptimized: rule.query ? analyzeQueryPerformance(rule.query) : { optimized: true },
    documentationComplete: validateDocumentation(rule)
  };
}
```

These comprehensive validation rules enable automated quality assurance for Analytic Rules, ensuring consistency, accuracy, and effectiveness across all Microsoft Sentinel detections in the repository.