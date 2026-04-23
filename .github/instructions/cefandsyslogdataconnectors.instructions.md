---
applyTo: "DataConnectors/**/*.json,Solutions/**/Data Connectors/**/*.json"
---

# CEF and Syslog Data Connectors Instructions

## Overview

This instruction file covers guidance for reviewing **Common Event Format (CEF)** and **Syslog** data connectors. These are standard ingestion methods for collecting security logs from network appliances and systems into Azure Sentinel.

**Applicability**: These instructions apply **only** to data connectors with the following dataTypes:
- **CEF connectors**: Must have `"dataTypes": [{"name": "CommonSecurityLog (DATATYPE_NAME)", ...}]`
- **Syslog connectors**: Must have `"dataTypes": [{"name": "Syslog (DATATYPE_NAME)", ...}]`

---

### Connector Types
- **CEF (Common Event Format)**: Industry-standard format on top of Syslog messages, used by security vendors for event interoperability
- **Syslog**: Standard event logging protocol common to Linux systems

---

## CEF Data Connector Review Guidelines

### Required Fields

When reviewing CEF data connector JSON files, ensure these fields are present and properly configured:

#### Basic Metadata
- **id**: Unique identifier (format: `ProviderNameApplianceName`)
- **title**: Display name (format: "PROVIDER NAME APPLIANCE NAME")
- **publisher**: Organization name
- **descriptionMarkdown**: Clear description explaining it's CEF format and benefits

#### Query Configuration
- **graphQueries**: Must include `metricName`, `legend`, and `baseQuery` with:
  - `CommonSecurityLog` table
  - Filter by `DeviceVendor == "PROVIDER NAME"`
  - Filter by `DeviceProduct == "APPLIANCE NAME"`

- **sampleQueries**: At least 1 example query with description and Kusto query
- **dataTypes**: Must reference CommonSecurityLog with format `CommonSecurityLog (DATATYPE_NAME)`

#### Connectivity Validation
- **connectivityCriterias**: Must use `IsConnectedQuery` type with CommonSecurityLog filters
- **lastDataReceivedQuery**: Query to check if data was received in last 7 days

#### Permissions
- **permissions.resourceProvider**: Must include:
  - `Microsoft.OperationalInsights/workspaces` with `read`, `write`, `delete` permissions
  - `Microsoft.OperationalInsights/workspaces/sharedKeys` with `action` permission

#### Availability
- **availability.status**: Should be `1` (available)
- **availability.isPreview**: Set to `true` or `false` as appropriate

---

## Syslog Data Connector Review Guidelines

### Required Fields

When reviewing Syslog data connector JSON files, ensure these fields are present:

#### Basic Metadata
- **id**: Unique identifier (format: `ProviderNameAppliance`)
- **title**: Display name (format: "PROVIDER NAME APPLIANCE NAME")
- **publisher**: Organization name
- **descriptionMarkdown**: Clear description of Syslog protocol and Linux agent

#### Additional Requirements Banner
- **additionalRequirementBanner**: Must reference the dependent Kusto Function parser
  - Format: "This data connector depends on a parser based on a Kusto Function to work as expected **[enter the Kusto Function alias]** which is deployed with the Azure Sentinel Solution."

#### Query Configuration
- **graphQueries**: `metricName`, `legend`, and `baseQuery` using DATATYPE_NAME custom table
- **sampleQueries**: At least 1 example query with description
- **dataTypes**: Format `Syslog (DATATYPE_NAME)` with `lastDataReceivedQuery`

#### Connectivity Validation
- **connectivityCriterias**: Must use `IsConnectedQuery` type with DATATYPE_NAME
- **lastDataReceivedQuery**: Must check DATATYPE_NAME table for recent data

#### Permissions
- **permissions.resourceProvider**: Must include:
  - `Microsoft.OperationalInsights/workspaces` with `write` and `delete` permissions

#### Availability
- **availability.status**: Should be `1` (available)
- **availability.isPreview**: Set appropriately

### Instruction Steps Validation

Syslog connectors must include these instruction steps:

1. **Parser Dependency Notice**
   - First step should state parser dependency
   - Must include link to Kusto Function on GitHub
   - Format: "This data connector depends on a parser based on a Kusto Function..."

2. **Install and Onboard Agent for Linux**
   - Must clarify agent installation on separate machine from log source
   - Must state "Syslog logs are collected only from **Linux** agents"
   - Should provide choices for agent installation:
     - Azure Linux Virtual Machine (with InstallAgent type: InstallAgentOnLinuxVirtualMachine)
     - Non-Azure Linux Machine (with InstallAgent type: InstallAgentOnLinuxNonAzure)
   - Use `InstructionStepsGroup` for nested installation options

3. **Configure Log Collection**
   - Instructions for selecting facilities and severities
   - Reference to workspace advanced settings
   - Step-by-step: Configuration → Data → Syslog
   - Must include link to Syslog settings (linkType: OpenSyslogSettings)

---

## File and Naming Conventions

### Filename Validation
-  File must be named in format: `ProviderNameApplianceName.json`
  - Example: `PaloAltoNetworksFirewall.json`, `CiscoASA.json`
  - Must reflect both provider and appliance name
  - No special characters, spaces, or hyphens

### Provider and Product Name Validation
-  Validate PROVIDER NAME and APPLIANCE NAME actually exist
  - Perform web search to confirm provider and product are current
  - Flag if provider was acquired or product was renamed (e.g., BlueCoat → Symantec)
  - Verify product is still actively maintained/supported
  - Check official vendor documentation for current naming

---

## DATATYPE_NAME Validation

### Format Requirements
-  DATATYPE_NAME must NOT contain spaces
  - ✅ Correct: `PaloAltoNetworksTraffic`, `CiscoASAConnections`
  - ❌ Incorrect: `Palo Alto Networks Traffic`, `Cisco ASA Connections`

### Naming Convention
-  DATATYPE_NAME should represent:
  - Provider name (with no spaces)
  - Appliance name (with no spaces)
  - Type of data (optional but recommended for clarity)
  - Result: Descriptive short name that clearly identifies the data source
  - Example: `CiscoASASecurityEvents` (Cisco + ASA + Events)

### Format by Connector Type
- **CEF**: Must be `CommonSecurityLog (DATATYPE_NAME)` 
  - Example: `"name": "CommonSecurityLog (PaloAltoNetworksTraffic)"`
- **Syslog**: Must be `Syslog (DATATYPE_NAME)`
  - Example: `"name": "Syslog (CiscoASALogs)"`

---

## ID, Title, Publisher, and Description Validation

### ID Field Validation
-  Must be in format: `ProviderNameApplianceName`
  - Example: `PaloAltoNetworksFirewall`, `CiscoASA`
  - No spaces, special characters, or hyphens
  - Must match filename (without .json extension)
  - Should match values used in title and publisher

### Title Field Validation
-  Must be in format: `PROVIDER NAME APPLIANCE NAME`
  - Example: `Palo Alto Networks Firewall`, `Cisco ASA`
  - Use proper spacing and capitalization
  - Each word should be capitalized
  - Should be human-readable display name

### Publisher Field Validation
-  Must be: `PROVIDER NAME`
  - Example: `Palo Alto Networks`, `Cisco`
  - Should match the provider portion of the title
  - Typically matches vendor organization name

### Description Markdown Validation
-  Must provide meaningful explanation covering:
  - What data the data connector brings in (specific data sources, events, logs)
  - What format the data is in (CEF, Syslog, raw JSON, etc.)
  - Link to appliance/product documentation for setup/configuration
  - Benefits of ingesting this data into Azure Sentinel
  - Example: Clear business value and technical context

---

## Template Comparison

### Template Matching Requirement
-  Compare the submitted JSON with the relevant template:
  - For CEF: Use CEF template as baseline
  - For Syslog: Use Syslog template as baseline

### Property Comparison (Except Instructions)
-  Compare all properties and values against template
  - Structure must align with template structure
  - All required properties from template must be present
  - Property naming must match template exactly (case-sensitive)
  - Values should follow template patterns (except for connector-specific customizations)

### Instruction Comparison
-  Instructions may be customized per connector
  - Validate instructions are grammatically correct
  - Validate instructions are specific to the appliance/provider
  - Instructions should reference product-specific documentation
  - Instructions should be clear and actionable
  - Check for spelling mistakes and grammatical errors

---

## Link Validation

### General Link Requirements
- ✅ All documentation links must be valid and accessible
- ✅ GitHub repository links must use correct raw content URLs
- ✅ All URLs must be reachable at submission time

### aka.ms Short Links
-  Special attention to aka.ms links:
  - Validate aka.ms links resolve correctly
  - Check if files have been moved or modified in the repository
  - If link is to GitHub file, verify file still exists at that location
  - If link breaks, request updated link
  - Follow Easy Access Link Guide formatting standards
  - Create easy access links for: parser, azuredeploy, functionapp, functioncode

### Product Documentation Links
- Should reference official vendor documentation
- Links must be current (not archived or deprecated pages)
- For setup/configuration instructions, ensure they match current product version

---

## Query Validation

### Syntax Validation - All Query Types
-  Validate each query is syntactically correct:
  - Graph queries: Must be valid Kusto Query Language
  - Connectivity queries: Must be valid Kusto Query Language
  - Sample queries: Must be valid Kusto Query Language
  - Run queries through KQL validator if available
  - Ensure table names are correct (CommonSecurityLog for CEF, custom table for Syslog)

### CEF Query Specifics
- All queries must filter by:
  - `DeviceVendor == "PROVIDER NAME"` 
  - `DeviceProduct == "APPLIANCE NAME"`
- Verify case-sensitive matching of vendor and product names

### Syslog Query Specifics
- All queries must reference the custom DATATYPE_NAME table
- Verify table name uses exact DATATYPE_NAME (no spaces)
- Ensure queries validate DATATYPE_NAME table receives data

### Placeholder Validation
- All `{0}`, `{1}` placeholders must be defined in `fillWith` arrays
- Placeholders must be correctly positioned
- Example: `{0}` maps to first fillWith item in sequence

---

## Parser and Kusto Function Requirements

### For Syslog Connectors
-  Parser/Kusto Function dependency is mandatory:
  - Kusto Function must exist and be deployed with the solution
  - Parser must be called out in dataTypes Notes:
    - Add note explaining parser is required
    - Include reference to Kusto Function name/alias
  - **additionalRequirementBanner** must be filled:
    - Format: `"This data connector depends on a parser based on a Kusto Function to work as expected **[Kusto Function Alias]** which is deployed with the Azure Sentinel Solution."`
    - Must include direct link to parser/function on Azure Sentinel GitHub

### For All Data Connectors with Parser Dependencies
-  Parser dependency must be called out in:
  - First instruction step with parser reference
  - Notes section (if applicable)
  - additionalRequirementBanner field with GitHub link
  - Description markdown (recommended)
- Parser must be validated for:
  - Existence in repository
  - Correct filename format and location
  - Functional correctness (tested with sample data)

---

## Permissions Validation

### Permission Structure
-  Must match exactly with the relevant template
- Each permission entry must include:
  - `provider`: Resource provider name
  - `permissionsDisplayText`: Clear description of permissions
  - `providerDisplayName`: Friendly name
  - `scope`: Scope level (Workspace, etc.)
  - `requiredPermissions`: Boolean flags for required actions

### CEF vs Syslog Differences
- **CEF**: Typically requires more permissions (read/write/delete for workspace + action for shared keys)
- **Syslog**: Typically requires fewer permissions (write/delete for workspace only)

### Permission Validation
- ✅ All listed permissions are necessary for the data connector
- ✅ No missing permissions compared to template
- ✅ No extra permissions beyond what's required
- ✅ Permission descriptions are clear and user-friendly

---

## Spelling and Grammar Validation

### All Text Fields
-  Check all text in JSON for spelling and grammatical mistakes:
  - descriptionMarkdown
  - All instruction step descriptions
  - All instruction step titles
  - connectivityCriteria descriptions
  - Sample query descriptions
  - Notes and badges
  - additionalRequirementBanner text

### Specific Checks
- ✅ Proper capitalization (product names, provider names)
- ✅ Correct punctuation in all descriptions
- ✅ No redundant or confusing wording
- ✅ Consistent terminology throughout
- ✅ Professional tone and language
- ✅ Numbers and versions formatted consistently

---

## Common Validation Rules for Both

### JSON Structure
- ✅ Valid JSON format (no trailing commas, proper escaping)
- ✅ All required fields present and non-empty
- ✅ No undefined or null values for critical fields

### Query Validation
- ✅ Kusto queries must be syntactically correct
- ✅ All placeholders (`{0}`, `{1}`) are properly defined in fillWith arrays
- ✅ Table names exist (CommonSecurityLog for CEF, custom table for Syslog)
- ✅ Field references are accurate (DeviceVendor, DeviceProduct for CEF)

### Instruction Steps
- ✅ Clear, actionable steps with proper numbering
- ✅ Security best practices mentioned (sudo, permissions)
- ✅ Realistic timeframes for data ingestion (e.g., 20 minutes)
- ✅ Proper formatting for code/command instructions

### Links and References
- ✅ All documentation links are valid
- ✅ GitHub repository links use correct raw content URLs
- ✅ References to external resources are current

### Permissions
- ✅ Workspace permissions are correctly scoped
- ✅ Required permissions match the connector type (CEF requires more permissions for shared keys)
- ✅ Permission descriptions are clear and complete

---

## Review Checklist

### File and Naming
- [ ]  Filename is in format `ProviderNameApplianceName.json`
- [ ]  PROVIDER NAME and APPLIANCE NAME are validated to exist (web search performed)
- [ ]  Provider not defunct or rebranded without acknowledgment

### Identifiers and Naming
- [ ]  `id` is in format `ProviderNameApplianceName` (no spaces)
- [ ]  `title` is in format `PROVIDER NAME APPLIANCE NAME`
- [ ]  `publisher` is `PROVIDER NAME`
- [ ]  DATATYPE_NAME contains no spaces and represents provider + appliance + data type
- [ ] CEF format: `"name": "CommonSecurityLog (DATATYPE_NAME)"`
- [ ] Syslog format: `"name": "Syslog (DATATYPE_NAME)"`

### Description and Metadata
- [ ] `descriptionMarkdown` explains what data is collected, in what format, with link to vendor docs
- [ ] All required metadata fields present (especially if metadata section exists)
- [ ] Metadata `id` is GUID and unique
- [ ] Metadata `support` object has email and/or link

### Template Compliance
- [ ]  JSON structure matches relevant template (CEF or Syslog)
- [ ]  All required properties from template are present
- [ ]  Property values align with template (except instructions)
- [ ]  Permissions match template exactly

### Link Validation
- [ ]  All aka.ms links tested and resolving correctly
- [ ]  GitHub links checked for moved/modified files
- [ ] All external documentation links are valid and current
- [ ] Product documentation links reference current product version
- [ ] Easy access links created for parser/azuredeploy/functionapp as applicable

### Query Validation
- [ ]  All graph queries are syntactically correct Kusto
- [ ]  All connectivity queries are syntactically correct Kusto
- [ ]  All sample queries are syntactically correct Kusto
- [ ] CEF: Queries filter by DeviceVendor and DeviceProduct correctly
- [ ] Syslog: Queries reference correct custom DATATYPE_NAME table
- [ ] All placeholders (`{0}`, `{1}`) are defined in fillWith arrays

### Permissions
- [ ]  CEF permissions include workspace (read, write, delete) + sharedKeys (action)
- [ ]  Syslog permissions include workspace (write, delete)
- [ ] Permissions match template exactly
- [ ] Permission descriptions are clear and complete

### Instructions
- [ ]  Instructions are grammatically correct and properly spelled
- [ ]  Instructions are specific to the appliance and reference product documentation
- [ ] CEF: Instructions include Linux agent config, CEF forwarding, validation, machine security
- [ ] Syslog: Instructions include parser notice, Linux agent install, log collection config
- [ ] Instruction steps are clear and actionable
- [ ] All scripts/commands are properly formatted

### Parser/Kusto Function (for Syslog)
- [ ]  Syslog connectors have parser/Kusto Function dependency called out
- [ ] `additionalRequirementBanner` is filled with link to Kusto Function
- [ ] Parser is referenced in dataTypes Notes
- [ ] First instruction step mentions parser dependency

### Spelling and Grammar
- [ ]  All text fields checked for spelling and grammatical errors
- [ ] Consistent terminology throughout
- [ ] Proper capitalization of product/provider names
- [ ] Professional tone and language

### Data Type Validation
- [ ]  DATATYPE_NAME has no spaces
- [ ]  DATATYPE_NAME represents provider, appliance, and data type
- [ ] DATATYPE_NAME is consistent across all references
- [ ] Correct format for connector type (CommonSecurityLog, Syslog, _CL suffix for REST API, etc.)

### Availability and Status
- [ ] `availability.status` is set to `1` (available)
- [ ] `availability.isPreview` set appropriately (true/false)