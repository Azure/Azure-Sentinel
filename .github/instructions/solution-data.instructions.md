---
applyTo: "Solutions/**/Data/Solution_*.json"
---

# Solution Data File Instructions

## Overview

Solution_*.json files (located in `Solutions/{SolutionName}/Data/` directories) define the complete structure and components of Microsoft Sentinel solutions. These files serve as the blueprint for solution packaging, specifying all included security content, metadata, and deployment configurations.

## Advanced Solution Data Validation

### Required Structure Validation
All Solution_*.json files must contain these mandatory fields:
- `Name`: Solution display name (must match folder name conventions)
- `Author`: Author information with contact details
- `Logo`: Solution logo as HTML img tag with proper dimensions
- `Description`: Comprehensive solution description with proper formatting
- `BasePath`: Path to solution directory (any format acceptable - absolute, relative, or repo-relative)
- `Version`: Semantic version number (format: X.Y.Z)
- `Metadata`: Must always be "SolutionMetadata.json" (fixed value)
- `TemplateSpec`: Boolean indicating ARM template spec usage
- `Is1PConnector`: Boolean indicating first-party connector status

### Solution Naming Standards
```json
{
  "Name": "Microsoft Entra ID",           // ✅ Proper product name
  "Name": "CiscoSEG",                     // ✅ Vendor product abbreviation
  "Name": "Auth0",                        // ✅ Simple product name
  "Name": "cisco-seg-solution"            // ❌ Should match display name
}
```

**Naming Requirements:**
- Use official product/vendor names when possible
- Match the solution folder name (converted appropriately)
- **Only alphanumeric characters (a-z, A-Z, 0-9) and spaces allowed**
- No special characters including hyphens, underscores, dots, or symbols
- Maximum length: 100 characters
- Must be unique across all solutions

### Author Information Standards
```json
{
  "Author": "Microsoft - support@microsoft.com",                    // ✅ Microsoft solutions
  "Author": "Recorded Future Premier Integrations - support@recordedfuture.com", // ✅ Partner solutions
  "Author": "Community Contributor - username@domain.com",          // ✅ Community solutions
  "Author": "Microsoft"                                            // ❌ Missing contact info
}
```

**Author Format Requirements:**
- Format: `{Organization/Individual} - {email}`
- Valid email address required
- For Microsoft solutions: use "Microsoft - support@microsoft.com"
- For partner solutions: include partner organization name and support email
- For community: include contributor identification

### Logo Specifications
```json
{
  "Logo": "<img src=\"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/cisco-logo-72px.svg\" width=\"75px\" height=\"75px\">"
}
```

**Logo Requirements:**
- Must be valid HTML `<img>` tag
- Use GitHub raw URLs for consistency
- Standard dimensions: 75px x 75px
- Supported formats: SVG (preferred), PNG, JPG
- Logo must be stored in repository (no external dependencies)
- Path format: `https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/{filename}`

### Description Content Standards

#### Comprehensive Description Pattern
```json
{
  "Description": "The [Product Name](https://vendor.com/product) solution for Microsoft Sentinel provides the capability to ingest [specific data types](https://docs-link) into your Microsoft Sentinel workspace.\n\n**Underlying Microsoft Technologies used:**\n\nThis solution takes a dependency on the following technologies, and some of these dependencies either may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs:\n\na. [Technology 1](https://docs.microsoft.com/link)\n\nb. [Technology 2](https://azure.microsoft.com/services/link)"
}
```

**Description Requirements:**
- Start with solution overview including vendor/product links
- Explain primary capabilities and data ingestion
- Include "Underlying Microsoft Technologies used" section
- List all Azure dependencies with documentation links
- Include Preview disclaimer when applicable
- Use proper Markdown formatting
- Maximum length: 1000 characters

### Metadata Field Standards
```json
{
  "Metadata": "SolutionMetadata.json"
}
```

**Metadata Requirements:**
- **Must always be exactly "SolutionMetadata.json"** (fixed value, no variables)
- This references the metadata configuration file located in the solution's Data directory
- No alternative values or naming conventions are permitted
- Used to standardize metadata handling across all solutions
- Explain primary capabilities and data ingestion
- Include "Underlying Microsoft Technologies used" section
- List all Azure dependencies with documentation links
- Include Preview disclaimer when applicable
- Use proper Markdown formatting
- Maximum length: 2000 characters

## Solution Component Validation

### Data Connectors
```json
{
  "Data Connectors": [
    "Data Connectors/Auth0_FunctionApp.json",                    // ✅ Function App connector
    "Data Connectors/Connector_Cisco_SEG_CEF.json",            // ✅ CEF connector
    "Solutions/Product/Data Connectors/template_Product.json"   // ✅ Full path for nested solutions
  ]
}
```

**Data Connector Requirements:**
- Array of relative file paths from BasePath
- Files must exist in solution directory structure
- Supported connector types: Function App, CEF, REST API, Native Polling
- Path format: `Data Connectors/{ConnectorName}.json`
- File naming convention: descriptive and consistent

### Analytics Rules (Detection Rules)
```json
{
  "Analytic Rules": [
    "Analytic Rules/CiscoSEGDLPViolation.yaml",
    "Analytic Rules/CiscoSEGMaliciousAttachmentNotBlocked.yaml",
    "Analytic Rules/CiscoSEGMultipleLargeEmails.yaml"
  ]
}
```

**Analytics Rules Requirements:**
- All files must be in YAML format
- Descriptive naming reflecting threat/technique
- Path format: `Analytic Rules/{RuleName}.yaml`
- Rules must follow detection rule schema standards
- MITRE ATT&CK mappings required

### Hunting Queries
```json
{
  "Hunting Queries": [
    "Hunting Queries/CiscoSEGDroppedInMails.yaml",
    "Hunting Queries/CiscoSEGFailedDKIMFailure.yaml",
    "Hunting Queries/CiscoSEGInsecureProtocol.yaml"
  ]
}
```

**Hunting Query Requirements:**
- YAML format for consistency
- Focus on proactive threat hunting scenarios
- Path format: `Hunting Queries/{QueryName}.yaml`
- Must include proper KQL syntax validation

### Workbooks
```json
{
  "Workbooks": [
    "Workbooks/CiscoSEG.json",
    "Workbooks/SOCProcessFramework.json",
    "Workbooks/Building_a_SOCLargeStaff.json"
  ]
}
```

**Workbook Requirements:**
- JSON format Azure Workbook templates
- Path format: `Workbooks/{WorkbookName}.json`
- Must be valid Azure Workbook ARM templates
- Include proper data source bindings

### Parsers
```json
{
  "Parsers": [
    "Parsers/Auth0.txt",
    "Parsers/CiscoSEGEvent.txt"
  ]
}
```

**Parser Requirements:**
- Text files containing KQL functions
- Path format: `Parsers/{ParserName}.txt`
- Follow ASIM (Advanced Security Information Model) when applicable
- Proper parameter handling and optimization

### Playbooks
```json
{
  "Playbooks": [
    "Playbooks/Get-SOCActions/azuredeploy.json",
    "Playbooks/RecordedFuture-ImportToSentinel/RecordedFuture-ImportToSentinel.json"
  ]
}
```

**Playbook Requirements:**
- ARM template JSON files for Logic Apps
- Path format: `Playbooks/{PlaybookName}/{PlaybookName}.json` or `Playbooks/{PlaybookName}/azuredeploy.json`
- Must be valid Azure Logic App ARM templates
- Include proper connector dependencies

### Watchlists
```json
{
  "Watchlists": [
    "Watchlists/SOC-Contacts/SOCcontacts.json",
    "Watchlists/SOC-Recommended-Actions/SocRA.json",
    "Watchlists/LastPass-Users/LastPassUsers.json"
  ]
}
```

**Watchlist Requirements:**
- JSON format watchlist templates
- Path format: `Watchlists/{WatchlistName}/{WatchlistName}.json`
- Must include proper schema and sample data
- Descriptive naming for purpose clarity

## Advanced Configuration Properties

### Version Management
```json
{
  "Version": "2.0.0"        // ✅ Semantic versioning
}
```

**Version Requirements:**
- Semantic versioning format: MAJOR.MINOR.PATCH
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes
- Must align with solution evolution

### Template Specification Configuration
```json
{
  "TemplateSpec": true,     // ✅ Enable ARM Template Specs (recommended)
  "TemplateSpec": false     // ✅ Legacy ARM template deployment
}
```

### First-Party Connector Designation
```json
{
  "Is1PConnector": true,    // ✅ Microsoft-maintained connectors
  "Is1PConnector": false    // ✅ Partner/community connector
}
```

### Base Path Configuration
```json
{
  "BasePath": "C:\\GitHub\\Azure-Sentinel\\Solutions\\Auth0",        // ✅ Absolute path
  "BasePath": "/home/user/repos/Azure-Sentinel/Solutions/Auth0",     // ✅ Relative or absolute path
  "BasePath": "Solutions/Auth0"                                       // ✅ Any path format acceptable
}
```

**Important:** BasePath can use any path format (absolute, relative etc.). But preferably use Absolute paths in the format of `C:\\GitHub\\Azure-Sentinel\\Solutions\\{SolutionName}` for consistency and to avoid path resolution issues during build and validation processes.

## Validation Rules for PR Reviews

### 1. **Component File Existence Validation**
```typescript
function validateComponentFiles(solutionData: SolutionData, basePath: string): ValidationResult {
  const results = [];
  
  // Validate all referenced files exist
  ['Data Connectors', 'Analytic Rules', 'Hunting Queries', 'Workbooks', 'Parsers', 'Playbooks', 'Watchlists'].forEach(componentType => {
    if (solutionData[componentType]) {
      solutionData[componentType].forEach(filePath => {
        const fullPath = path.join(basePath, filePath);
        results.push({
          component: componentType,
          file: filePath,
          exists: fs.existsSync(fullPath)
        });
      });
    }
  });
  
  return results;
}
```

### 2. **Naming Consistency Validation**
```typescript
function validateNamingConsistency(solutionData: SolutionData, folderName: string): ValidationResult {
  const normalizedFolderName = folderName.replace(/[^a-zA-Z0-9]/g, '');
  const normalizedSolutionName = solutionData.Name.replace(/[^a-zA-Z0-9]/g, '');
  
  return {
    namesMatch: normalizedFolderName.toLowerCase() === normalizedSolutionName.toLowerCase(),
    folderName,
    solutionName: solutionData.Name
  };
}
```

### 3. **Logo URL Validation**
```typescript
function validateLogoUrl(logoHtml: string): ValidationResult {
  const srcMatch = logoHtml.match(/src="([^"]+)"/);
  if (!srcMatch) return { valid: false, reason: 'No src attribute found' };
  
  const url = srcMatch[1];
  const isGitHubRaw = url.startsWith('https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/');
  const hasDimensions = logoHtml.includes('width=') && logoHtml.includes('height=');
  
  return {
    valid: isGitHubRaw && hasDimensions,
    url,
    isGitHubRaw,
    hasDimensions
  };
}
```

### 4. **Author Format Validation**
```typescript
function validateAuthorFormat(author: string): ValidationResult {
  const authorRegex = /^(.+?)\s*-\s*([^@\s]+@[^@\s]+\.[^@\s]+)$/;
  const match = author.match(authorRegex);
  
  return {
    valid: !!match,
    organization: match?.[1]?.trim(),
    email: match?.[2]?.trim(),
    format: author
  };
}
```

## Quality Assurance Patterns

### Comprehensive Solution Validation
```typescript
interface SolutionQuality {
  completeness: number;           // 0-100% based on included components
  consistency: boolean;           // Naming and path consistency
  standardsCompliance: boolean;   // Follows all standards
  componentIntegrity: boolean;    // All referenced files exist
  documentationQuality: number;   // Description and metadata quality
}
```

### Component Distribution Analysis
```typescript
interface ComponentAnalysis {
  dataConnectors: number;
  analyticRules: number;
  huntingQueries: number;
  workbooks: number;
  parsers: number;
  playbooks: number;
  watchlists: number;
  isComprehensive: boolean;       // Has multiple component types
  focusArea: string;              // Primary security domain
}
```

## Common PR Review Issues

### ❌ **Missing Required Fields**
```json
{
  "Name": "TestSolution",
  // Missing Author, Description, BasePath, Version, Metadata, TemplateSpec, Is1PConnector
}
```

### ❌ **Invalid Author Format**
```json
{
  "Author": "Microsoft",          // Should be "Microsoft - support@microsoft.com"
  "Author": "john@email.com"      // Should be "John Doe - john@email.com"
}
```

### ❌ **Malformed Logo HTML**
```json
{
  "Logo": "logo.svg",             // Should be full HTML img tag
  "Logo": "<img src=\"logo.svg\">" // Missing dimensions and GitHub URL
}
```

### ❌ **Invalid File References**
```json
{
  "Data Connectors": [
    "NonexistentConnector.json",   // File doesn't exist
    "/Data Connectors/Auth0.json"  // Shouldn't start with slash
  ]
}
```

### ❌ **Inconsistent Naming**
```json
{
  // Folder: Solutions/Microsoft Entra ID/
  "Name": "Azure Active Directory"    // Should be "Microsoft Entra ID" to match folder
}
```

### ❌ **Invalid Version and TemplateSpec Combination**
```json
{
  "Version": "3.0.0",
  "TemplateSpec": true              // ❌ Version 3.*.* must have TemplateSpec = false
}
```

**Correction:**
```json
{
  "Version": "3.0.0",
  "TemplateSpec": false             // ✅ Correct for version 3.x.x
}
```

## Best Practices for Solution Data Files

### 1. **Component Organization**
- Group related analytics rules logically
- Use consistent naming conventions across components
- Ensure file paths are relative to BasePath
- Validate all referenced files exist

### 2. **Description Quality**
- Start with clear solution overview
- Include vendor/product documentation links
- List all Azure service dependencies
- Use proper Markdown formatting
- Include cost and preview disclaimers

### 3. **Metadata Consistency**
- Ensure solution name matches folder structure
- Align version numbers across all components
- Maintain consistent author information
- Use appropriate connector classification

### 4. **Component Completeness**
- Include data connectors for ingestion
- Provide analytics rules for detection
- Add hunting queries for investigation
- Include workbooks for visualization
- Add parsers for data normalization when needed

### 5. **File Path Standards**
- Use forward slashes in JSON (even on Windows)
- Maintain consistent directory structure
- Use descriptive file names
- Avoid spaces and special characters in paths

## Automated Validation Framework

### Schema Validation
```typescript
const solutionDataSchema = {
  required: ['Name', 'Author', 'Logo', 'Description', 'BasePath', 'Version', 'Metadata', 'TemplateSpec', 'Is1PConnector'],
  properties: {
    Name: { type: 'string', maxLength: 100, pattern: '^[a-zA-Z0-9 ]+$' },
    Author: { type: 'string', pattern: '^.+ - .+@.+\\..+$' },
    Logo: { type: 'string', pattern: '<img src="https://raw\\.githubusercontent\\.com/Azure/Azure-Sentinel/master/.+" width="75px" height="75px">' },
    Description: { type: 'string', maxLength: 5000 },
    Metadata: { type: 'string', enum: ['SolutionMetadata.json'] },
    Version: { type: 'string', pattern: '^\\d+\\.\\d+\\.\\d+$' },
    TemplateSpec: { type: 'boolean' },
    Is1PConnector: { type: 'boolean' }
  },
  conditionalRules: {
    templateSpecVersion3: {
      condition: (data) => data.Version && data.Version.startsWith('3.'),
      validation: (data) => data.TemplateSpec === false,
      message: 'Version 3.*.* solutions must have TemplateSpec set to false'
    }
  }
};
```

### Version and TemplateSpec Compatibility
```typescript
function validateVersionTemplateSpecCompatibility(solutionData: SolutionData): ValidationResult {
  const version = solutionData.Version;
  const majorVersion = parseInt(version.split('.')[0]);
  
  // Version 3.x.x must have TemplateSpec = false
  if (majorVersion === 3 && solutionData.TemplateSpec !== false) {
    return {
      valid: false,
      error: 'Version 3.*.* solutions must have TemplateSpec set to false',
      version: version,
      templateSpec: solutionData.TemplateSpec
    };
  }
  
  return { valid: true };
}
```

### File Integrity Validation
```typescript
function validateSolutionIntegrity(solutionPath: string): ValidationResult {
  const solutionData = JSON.parse(fs.readFileSync(path.join(solutionPath, 'Data', 'Solution_*.json')));
  const basePath = solutionData.BasePath;
  
  return {
    requiredFieldsPresent: validateRequiredFields(solutionData),
    componentFilesExist: validateComponentFiles(solutionData, basePath),
    namingConsistent: validateNamingConsistency(solutionData, path.basename(solutionPath)),
    authorFormatValid: validateAuthorFormat(solutionData.Author),
    logoUrlValid: validateLogoUrl(solutionData.Logo),
    versionValid: validateVersion(solutionData.Version),
    metadataAligned: validateMetadataAlignment(solutionPath)
  };
}
```

These comprehensive validation rules enable automated quality assurance for Solution_Data files, ensuring consistency, completeness, and standards compliance across all Microsoft Sentinel solutions in the repository.