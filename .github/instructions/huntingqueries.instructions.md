---
applyTo: "Hunting Queries/**/*.yaml,Hunting Queries/**/*.yml,Solutions/**/Hunting Queries/*.yaml,**/Hunting Queries/*.yaml"
---

# Hunting Queries Instructions

## Overview

Hunting Queries are YAML files that define proactive search queries in Microsoft Sentinel to identify threats, anomalous patterns, and potential security incidents that may not trigger automated detections. These queries empower security analysts to uncover hidden threats, investigate suspicious activities, and discover new attack patterns through interactive exploration of security data.

## Validation Rules for PR Reviews

### Field-Based Validation Reference

#### **id** (Unique Identifier)
- **Required**: Yes
- **Format**: Standard GUID format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (any valid hex digits)
- **Validation**: `/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/`
- **Rules**:
  - Must be unique across all hunting queries
  - Should never be reused
  - Generated using proper GUID generators (PowerShell `New-GUID`, online GUID generators, etc.)
  - **Note**: Accepts any valid GUID format (not strictly UUID v4 variant bits)
  - Valid formats include GUIDs starting with any hex digit in any position
- **Valid Examples**: 
  - `85421f18-2de4-42ff-9ef4-058924dcb1bf` ✅
  - `d1234567-89ab-cdef-0123-456789abcdef` ✅
  - `a0000000-0000-0000-0000-000000000000` ✅

#### **name** (Hunting Query Name)
- **Required**: Yes
- **Format**: Sentence case label
- **Constraints**: Target 50 characters when possible; Hard limit 100 characters
- **Capitalization**: Sentence case (capitalize first word and proper nouns only)
- **Punctuation**: Do NOT end with a period
- **Rules**:
  - Should clearly describe what threat or pattern the query searches for
  - Should indicate the threat actor activity, malicious behavior, or anomaly being hunted
  - Start with vendor/product name when applicable
  - Use specific, descriptive language rather than generic terms
  - Avoid ambiguous terms; be clear about the data source or entity being investigated
- **Naming Pattern Recommendations**:
  - For threat hunting: "[Threat/Vendor] - [Type of Activity]"
  - For pattern detection: "[Pattern Description]"
  - For anomaly detection: "[Anomalous Behavior Description]"
- **Valid Examples**: 
  - `Cisco Cloud Security - Possible connection to C2` ✅
  - `Multiple failed login attempts from single IP` ✅
  - `Unusual outbound traffic patterns` ✅
- **Invalid Examples**: 
  - `Threat Hunting Query` ❌ (too generic)
  - `Unknown Activity.` ❌ (ends with period)
  - `suspicious behavior` ❌ (not sentence case)

#### **description** (Query Description)
- **Required**: Yes
- **Format**: Comprehensive narrative text (max 255 characters)
- **Opening**: Should start with action-oriented verbs such as "Calculate", "Identify", "Searches for", "Detects", "Finds", "Analyzes"
- **Length**: Should be 1-3 sentences maximum
- **Rules**:
  - Is NOT a copy of the name field - must provide additional context
  - Should explain the hunting methodology or pattern being searched
  - Can reference specific metrics or thresholds used in the query (e.g., "Higher values may indicate beaconing")
  - Can explain the rationale for the hunt (e.g., "C2 servers reply with the same data")
  - Do NOT describe implementation details (query language, operators)
  - Use clear, non-technical language when possible
- **What to Include**:
  - Purpose of the hunt
  - What anomaly or pattern indicates success
  - Why this pattern matters for threat detection
  - Key metrics or thresholds if relevant
- **What NOT to do** (too vague or too technical):
  - ❌ "Queries for unusual activity"
  - ❌ "Uses Kusto Query Language to aggregate BytesIn metrics by source and destination IP pairs"
- **Instead do this** (specific and clear):
  - ✅ "Calculate the count of BytesIn per Source-Destination pair over 12/24 hours. Higher values may indicate beaconing. C2 servers reply with the same data, making BytesIn value the same."

#### **requiredDataConnectors** (Data Sources)
- **Required**: Yes
- **Type**: Array of objects with `connectorId` and `dataTypes`
- **Format**: Structured list of connector specifications
- **Rules**:
  - `connectorId`: ID of the data connector required for query to function (e.g., `1PasswordCCPDefinition`)
  - `dataTypes`: List of data types the query depends on (table names or Kusto function/parser names)
  - Empty array `[]` is acceptable if query uses multiple sources or has flexible data source requirements
  - Must reflect actual data being queried (tables or parsers)
- **Valid Examples**: 
  - `[]` ✅ (flexible sources)
  - Complex example: Data types can reference Kusto functions (like `Syslog`, `CommonEventFormat`) or parsers instead of table names
- **Important Note**:
  - If query operates on a Kusto function/parser (not a table), `dataTypes` should list the function/parser name, not the underlying table name
  - Examples: `Syslog`, `CommonEventFormat`, `_CL` tables, or custom parsers

#### **tactics** (MITRE ATT&CK Tactics)
- **Required**: Yes
- **Framework Version**: ATT&CK Framework v16 Supported 
- **Reference**: https://attack.mitre.org/versions/v16/matrices/enterprise/
- **Type**: Array of strings
- **Format**: PascalCase without spaces
- **Rules**:
  - Names MUST NOT have any spaces (use PascalCase)
  - Maximum 5 tactics per query
  - Must align with the threat behavior being hunted
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
- **Required**: Yes
- **Framework Version**: ATT&CK Framework v16 Supported
- **Reference**: https://attack.mitre.org/versions/v16/techniques/enterprise/
- **Type**: Array of strings
- **Format**: `T####` (technique) or `T####.###` (sub-technique)
- **Pattern**: `/^T\d{4}(\.\d{3})?$/`
- **Rules**:
  - MUST match MITRE ATT&CK Techniques or Sub-techniques exactly
  - Prefer sub-techniques when they better describe the hunting focus (e.g., `T1071.001` for HTTPS C2 communication)
  - Maximum 10 techniques per query
  - Must align with listed tactics
  - Invalid formats: `1071` ❌, `T1071.001.002` ❌ (too many sub-technique levels)
- **Valid Examples**: 
  - `T1071` (Application Layer Protocol) ✅
  - `T1071.001` (HTTPS C2) ✅
  - `T1595.003` (Reverse DNS) ✅
- **PR Review Feedback Format**: When reporting invalid techniques, include the MITRE reference in the comment:
  - **IMPORTANT - Techniques Feedback:** When providing feedback on techniques (e.g., invalid technique ID or incorrect format), **ALWAYS include reference to:** https://attack.mitre.org/versions/v16/techniques/enterprise/
  - ✅ *Example feedback format:* "The technique 'T1071' is valid. For a comprehensive list of all techniques and sub-techniques, refer to: https://attack.mitre.org/versions/v16/techniques/enterprise/"

#### **query** (KQL Hunting Query)
- **Required**: Yes
- **Character Limit**: Maximum 10,000 characters
- **Reference**: https://learn.microsoft.com/en-us/kusto/query/best-practices?view=microsoft-fabric
- **Rules**:
  - Must be valid KQL syntax
  - Should use meaningful filtering and aggregation to help analysts identify threats
  - Must return results that can be easily analyzed by security professionals
  - Should be optimized for performance and clarity
  - Include comments explaining complex logic when needed
  - Each line must have at least one space at the beginning (two spaces recommended for readability)
  - Must return all available entity fields for mapping purposes
  - Sanitize results to provide only necessary investigation properties
- **KQL Best Practices for Hunting Queries**:
  - **Reduce data processing**: Apply `where` operator immediately after table references to filter early and reduce dataset size
  - **Use efficient string operators**: Prefer `has` (token-level search) over `contains` (substring search); use `==` (case-sensitive) over `=~`
  - **Optimize filters**: Apply datetime filters first (most efficient), then string/dynamic filters (ordered by selectivity), then numeric filters
  - **Return actionable results**: Use `summarize`, `extend`, and `project` to create output that helps analysts understand the threat
  - **Avoid common mistakes**: Don't use wildcard `*` for full table scans; don't use `tolower()` on large datasets (use `=~` instead)
  - **Use materialization wisely**: Use `materialize()` for `let` statements referenced multiple times; extract fields from dynamic objects at ingestion time if querying millions of rows
  - **Limit for testing**: Always use `limit [small number]` or `count` during development to avoid processing gigabytes of unexpected data
  - **Refer to complete guide**: https://learn.microsoft.com/en-us/kusto/query/best-practices?view=microsoft-fabric
- **Query Structure Recommendations**:
  - Define variables with `let` statements for readability and maintainability (use human-readable names)
  - Use meaningful column names in output
  - Sort results by most relevant indicators (e.g., highest count, most recent)
  - Use `extend` to add context or calculated fields
  - Include enrichment fields that help analysts investigate (e.g., `IPCustomEntity`, `AccountCustomEntity`)
  - Use `| summarize` with `StartTime = max(TimeGenerated), EndTime = min(TimeGenerated)` when needed
  - Always use `StartTime` and `EndTime` field names (not `StartTimeUtc` or `EndTimeUtc`)
  - Include at least one primary entity: `Host`, `Account`, or `IP`
  - Avoid time filters shorter than 1 day unless specifically required
  - For baselining/historical comparison, include time-bounded filter like `| where TimeGenerated >= ago(lookback)`
  - Avoid time frames longer than 14 days due to performance impact
  - Add comments on separate lines (not at end of query statements)
- **Common Hunting Query Patterns**:
  - Aggregation: Group by entity and count occurrences
  - Anomaly detection: Compare current behavior against historical baseline
  - Pattern matching: Identify specific sequences of events
  - Volume analysis: Detect unusually high or low data volumes
  - Statistical outliers: Find entities that deviate from normal behavior
- **Example Structure**:
  ```kql
  let timeframe = 1d;
  TableName
  | where TimeGenerated > ago(timeframe)
  | where [filtering conditions]
  | summarize count() by [grouping columns]
  | sort by count_ desc
  | extend Message = "Description of finding"
  | extend IPCustomEntity = [ip field]
  ```

#### **entityMappings** (Entity Type Mapping)
- **Required**: Yes
- **Purpose**: Enriches query output with essential information for investigative processes and remedial actions
- **Rules**:
  - Each template can have up to 10 entity mappings
  - Each entity mapping can have up to 3 field mappings (identifiers)
  - Must reference entity types and identifiers from [Entity mapping table](https://learn.microsoft.com/en-us/azure/sentinel/entities-reference#entity-types-and-identifiers)
- **Common Entity Types**: `Account`, `Host`, `IP`, `DNS`, `File`, `FileHash`, `Mailbox`, `MailMessage`, `URL`, `Process`, `RegistryKey`, `RegistryValue`
- **Example Structure**:
  ```yaml
  entityMappings:
  - entityType: Account
    fieldMappings:
      - identifier: FullName
        columnName: AccountCustomEntity
  - entityType: Host
    fieldMappings:
      - identifier: FullName
        columnName: HostCustomEntity
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: ClientIP
  ```
- **Query Requirements**: Must include `extend` statements to create mapped columns in output
- **Example**:
  ```kql
  | extend IPCustomEntity = SrcIpAddr
  | extend HostCustomEntity = SrcHostname
  | extend AccountCustomEntity = UserPrincipalName
  ```

#### **customDetails** (Custom Details for Alert Context)
- **Required**: No (recommended for enhanced analyst context)
- **Purpose**: Integrates event data into alerts for faster triaging, investigation, and response
- **Rules**:
  - Key/value pairs of property and column names
  - Maximum 20 custom details per template
  - Column names must match output columns from query
- **Example**:
  ```yaml
  customDetails:
    SourceIP: SrcIpAddr
    DestinationIP: DstIpAddr
    EventCount: count_
    FirstSeen: min_TimeGenerated
    LastSeen: max_TimeGenerated
  ```

#### **version** (Semantic Version)
- **Required**: Yes
- **Format**: Semantic versioning `X.Y.Z`
- **Pattern**: `/^\d+\.\d+\.\d+$/`
- **Rules**:
  - `X` = major version (breaking changes)
  - `Y` = minor version (new features)
  - `Z` = patch version (bug fixes)
  - Saved with template when customers create hunting query from template
  - New versions trigger notifications in UX
- **Example**: `1.0.0`, `1.2.3`, `2.1.5` ✅

#### **metadata** (Metadata Information - Required for Standalone Files)
- **Required**: Yes (for standalone hunting queries in `Hunting Queries/` folder); No (for queries in `Solutions/**/Hunting Queries/`)
- **Purpose**: Provides source, author, support tier, and category information for standalone hunting queries
- **Type**: Object with nested properties
- **Structure**:
  ```yaml
  metadata:
    source:
      kind: Community        # or "Microsoft" for official queries
    author:
      name: Author Name
    support:
      tier: Community        # or "Microsoft" for official support
    categories:
      domains: [ "Category Name" ]
  ```
- **Rules**:
  - **Required for standalone files** in root `Hunting Queries/` folder (matches pattern `Hunting Queries/**/*.yaml`)
  - **Not required** for queries in Solutions folder (`Solutions/**/Hunting Queries/*.yaml`)
  - `source.kind`: Typically `Community` or `Microsoft`
  - `author.name`: Name of the query author or organization
  - `support.tier`: Support level - `Community` or `Microsoft`
  - `categories.domains`: Array of domain/category classifications from the valid domains list

#### **Valid Domain Categories** (for `categories.domains`)
- Application
- Cloud Provider
- Cloud Security
- Compliance
- DevOps
- Identity
- Internet of Things (IoT)
- IT Operations
- Migration
- Networking
- Platform
- Security
- Security - 0-day Vulnerability
- Security - Automation (SOAR)
- Security - Cloud Security
- Security - Information Protection
- Security - Insider Threat
- Security - Network
- Security - Others
- Security - Threat Intelligence
- Security - Threat Protection
- Security - Vulnerability Management
- Storage
- Training and Tutorials
- User Behavior (UEBA)

- **Valid Examples**: 
  ```yaml
  metadata:
    source:
      kind: Community
    author:
      name: Alex
    support:
      tier: Community
    categories:
      domains: [ "Security - Others" ]
  ```
  ```yaml
  metadata:
    source:
      kind: Microsoft
    author:
      name: Microsoft Sentinel Team
    support:
      tier: Microsoft
    categories:
      domains: [ "Security - Threat Intelligence", "Security - Threat Protection" ]
  ```
- **Invalid Examples** (for standalone files):
  - Missing `metadata` section ❌
  - Incomplete metadata (missing `author` or `support`) ❌

## File Structure Example

```yaml
id: 85421f18-2de4-42ff-9ef4-058924dcb1bf
name: Cisco Cloud Security - Possible connection to C2
description: |
  Calculate the count of BytesIn per Source-Destination pair over 12/24 hours. Higher values may indicate beaconing. C2 servers reply with the same data, making BytesIn value the same.
requiredDataConnectors: []
tactics:
  - CommandAndControl
relevantTechniques:
  - T1071
query: |
  let timeframe = 1d;
  Cisco_Umbrella
  | where EventType == "proxylogs"
  | where TimeGenerated > ago(timeframe)
  | summarize count() by SrcIpAddr, DstIpAddr, SrcBytes
  | sort by count_ desc
  | extend Message = "Possible communication with C2"
  | extend IPCustomEntity = SrcIpAddr
entityMappings:
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: SrcIpAddr
customDetails:
  SourceIP: SrcIpAddr
  DestinationIP: DstIpAddr
  BytesSent: SrcBytes
  EventCount: count_
version: 1.0.0
metadata:
  source:
    kind: Community
  author:
    name: Alex
  support:
    tier: Community
  categories:
    domains: [ "Security - Others" ]
```

## Quality Standards

### Required Elements Checklist
- [ ] Unique, valid GUID for `id`
- [ ] Clear, descriptive `name` (target 50 characters, max 100)
- [ ] Comprehensive `description` explaining the hunting methodology (1-3 sentences, under 255 chars)
- [ ] Accurate `requiredDataConnectors` with `connectorId` and `dataTypes`, or empty array `[]`
- [ ] Valid MITRE ATT&CK v16 `tactics` (PascalCase, no spaces, max 5)
- [ ] Valid MITRE ATT&CK v16 `relevantTechniques` (T#### or T####.### format, max 10)
- [ ] Valid, optimized KQL `query` (max 10,000 characters) that returns meaningful results
- [ ] `entityMappings` section with proper entity types and field mappings
- [ ] `extend` statements in query to create mapped columns (required for entityMappings)
- [ ] `customDetails` for enhanced analyst context (recommended)
- [ ] Semantic `version` in X.Y.Z format (required)
- [ ] `metadata` section (required for standalone files in `Hunting Queries/` folder; not required in `Solutions/**/Hunting Queries/`)

### Common Issues and How to Fix Them

| Issue | Example | Fix |
|-------|---------|-----|
| Generic name | "Threat Hunt Query" | Use specific threat/pattern: "Cisco Cloud Security - Possible connection to C2" |
| Name too long | "Very long descriptive query name that exceeds 50 characters" | Shorten to ~50 chars: "Possible C2 connection to IP" |
| Description too vague | "Searches for activity" | Add specific metric or pattern: "Calculate BytesIn per IP pair to identify beaconing" |
| Invalid tactic casing | `command and control` or `CommandControl` | Use correct format: `CommandAndControl` |
| Missing entityMappings | Query has results but no entity config | Add entityMappings section with entity types |
| Entity columns missing | entityMappings defined but columns don't exist | Add `\| extend IPCustomEntity = SrcIpAddr` |
| Query exceeds limit | KQL over 10,000 characters | Move static lists to watchlist or custom function |
| Unoptimized query | Queries full table without early filtering | Add `where` immediately after table reference |
| Missing version | No version field in YAML | Add `version: 1.0.0` at end of file |
| Missing metadata (standalone) | Standalone file without metadata section | Add metadata block with source, author, support, and categories |
| Incomplete metadata | Missing author or support tier | Ensure all metadata fields are present: source.kind, author.name, support.tier, categories.domains |
| Comment placement | Code comments at end of lines | Place comments on separate lines |
| Missing entity fields | Query doesn't return all mapped fields | Ensure output includes all fields referenced in entityMappings |

## Submission Guidelines

1. **Naming & Documentation**: Ensure query name (≤50 chars) and description clearly convey hunting value
2. **MITRE Alignment**: Verify tactics and techniques match https://attack.mitre.org/versions/v16/ 
3. **Field Validation**: Include all required fields: `id`, `name`, `description`, `requiredDataConnectors`, `tactics`, `relevantTechniques`, `query`, `entityMappings`, `version`
4. **KQL Validation**: 
   - Test query in Microsoft Sentinel environment; ensure it runs without errors
   - Ensure query doesn't exceed 10,000 character limit
   - Verify all entity columns defined in entityMappings exist in query output
5. **Entity Mappings**: Define proper `entityMappings` section; ensure query includes corresponding `extend` statements
6. **Performance**: Query should complete in reasonable time; use early filtering and limits during development
7. **Context**: Provide sufficient description so analysts understand why this hunt matters
8. **Unique ID**: Verify query ID is unique (never reuse GUIDs)
9. **Version**: Include semantic version starting at `1.0.0` for new queries
10. **Folder Structure**: Name subfolders after the table being queried (e.g., `AzureDevOpsAuditing` folder for queries on `AzureDevOpsAuditing` table)
11. **Entity Fields**: Ensure query returns at least one primary entity (`Host`, `Account`, or `IP`) and all fields used in entityMappings