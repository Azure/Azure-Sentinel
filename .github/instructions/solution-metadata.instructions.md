---
applyTo: "Solutions/**/SolutionMetadata.json"
---

# Solution Metadata Instructions

## Advanced Solution Metadata Validation

### Required Structure Validation
All SolutionMetadata.json files must contain these mandatory fields:
- `publisherId`: Must match approved publisher identifiers (see validation rules)
- `offerId`: Must follow naming convention (see validation rules)
- `firstPublishDate`: Must be in ISO 8601 format (YYYY-MM-DD)
- `providers`: Array of provider names (typically ["Microsoft"])
- `categories`: Must contain `domains` array with valid domain categories
- `support`: Complete support information structure

### Category Domain Validation
Valid domain categories include. For detailed category definitions, refer to: https://learn.microsoft.com/en-us/azure/sentinel/sentinel-solutions#categories-for-microsoft-sentinel-out-of-the-box-content-and-solutions
```json
{
  "categories": {
    "domains": [
      "Application",                           // Web, server-based, SaaS, database, communications, or productivity service
      "Cloud Provider",                        // Cloud service
      "Cloud Security",                        // Cloud security service
      "Compliance",                            // Compliance product, services, and protocols
      "DevOps",                                // Development operations tools and services
      "Identity",                              // Identity service providers and integrations
      "Internet of Things (IoT)",              // IoT, operational technology (OT) devices, and infrastructure, industrial control services
      "IT Operations",                         // Products and services managing IT
      "Migration",                             // Migration enablement products and services
      "Networking",                            // Network products, services, and tools
      "Platform",                              // Microsoft Sentinel generic or framework components, Cloud infrastructure, and platform
      "Security",                              // General security products
      "Security - 0-day Vulnerability",        // Specialized solutions for zero-day vulnerability attacks
      "Security - Automation (SOAR)",          // Security automations, SOAR (Security Operations and Automated Responses), security operations, and incident response products and services
      "Security - Cloud Security",             // CASB (Cloud Access Service Broker), CWPP (cloud workload protection platforms), CSPM (cloud security posture management), and other cloud security products and services
      "Security - Information Protection",     // Information protection and document protection products and services
      "Security - Insider Threat",             // Insider threat and user and entity behavioral analytics (UEBA) for security products and services
      "Security - Network",                    // Security network devices, firewall, NDR (network detection and response), NIDP (network intrusion and detection prevention), and network packet capture
      "Security - Others",                     // Other security products and services with no other clear category
      "Security - Threat Intelligence",        // Threat intelligence platforms, feeds, products, and services
      "Security - Threat Protection",          // Threat protection, email protection, extended detection and response (XDR), and endpoint protection products and services
      "Security - Vulnerability Management",   // Vulnerability management products and services
      "Storage",                               // File stores and file sharing products and services
      "Training and Tutorials",                // Training, tutorials, and onboarding assets
      "User Behavior (UEBA)"                   // User behavior analytics products and services
    ]
  }
}
```

### Industry Vertical Categories Validation
Valid industry vertical categories include (optional field). For detailed category definitions, refer to: https://learn.microsoft.com/en-us/azure/sentinel/sentinel-solutions#industry-vertical-categories
```json
{
  "categories": {
    "verticals": [
      "Aeronautics",     // Products, services, and content specific for the aeronautics industry
      "Education",       // Products, services, and content specific for the education industry
      "Finance",         // Products, services, and content specific for the finance industry
      "Healthcare",      // Products, services, and content specific for the healthcare industry
      "Manufacturing",   // Products, services, and content specific for the manufacturing industry
      "Retail",          // Products, services, and content specific for the retail industry
      "Software"         // Products, services, and content specific for the software industry
    ]
  }
}
```
**Note:** The `verticals` field is optional. If not applicable to your solution, omit this field entirely from the categories object.

### Advanced Metadata Patterns

#### Multi-Domain Solutions
```json
{
  "categories": {
    "domains": [
      "Identity",
      "Security - Automation (SOAR)",
      "Security - Threat Protection"
    ],
    "verticals": [
      "Healthcare",
      "Finance",
      "Retail"
    ]
  }
}
```

#### Enterprise Solution Metadata
```json
{
  "publisherId": "azuresentinel",
  "offerId": "azure-sentinel-solution-enterprise-security",
  "firstPublishDate": "2024-01-15",
  "version": "2.1.0",
  "displayName": "Enterprise Security Solution",
  "description": "Comprehensive enterprise security monitoring and response",
  "providers": ["Microsoft"],
  "categories": {
    "domains": [
      "Security - Threat Protection",
      "Security - Automation (SOAR)",
      "IT Operations"
    ]
  },
  "support": {
    "tier": "Microsoft",
    "name": "Microsoft Corporation",
    "email": "support@microsoft.com",
    "link": "https://support.microsoft.com/",
    "escalationContact": "azuresentinel-support@microsoft.com"
  },
  "dependencies": {
    "operator": "AND",
    "criteria": [
      {
        "kind": "DataConnector",
        "contentId": "AzureActiveDirectory",
        "version": ">=2.0.0"
      }
    ]
  },
  "metadata": {
    "source": {
      "kind": "Community",
      "name": "Microsoft Sentinel Community",
      "url": "https://github.com/Azure/Azure-Sentinel"
    },
    "author": {
      "name": "Microsoft Sentinel Team",
      "email": "azuresentinel@microsoft.com"
    },
    "compatibility": {
      "minimumSentinelVersion": "2023.04.01",
      "maximumSentinelVersion": "2025.12.31"
    }
  }
}
```

## Validation Rules for PR Reviews

### 1. **Publisher ID Validation**
```regex
publisherId: ^[a-z][a-z0-9]{0,49}$
```
- Must start with a letter (a-z)
- Can contain **lowercase letters and digits** (a-z, 0-9) - digits are permitted
- **No special characters, spaces, hyphens, underscores, or dots allowed**
- Maximum length: 50 characters
- Must match one of the approved publisher IDs or be pre-approved custom ID

**Approved Publisher IDs:**
- `azuresentinel` - Official Microsoft Sentinel solutions
- `microsoftsentinelcommunity` - Community-contributed solutions
- Custom publisher IDs must be pre-approved

**Valid Publisher ID Examples with Digits:**
- ✅ `azuresentinel` (approved)
- ✅ `microsoftsentinelcommunity` (approved)
- ✅ `mycompanypublisher` (alphanumeric only)
- ✅ `armic1668090987837` (letters and digits allowed)
- ✅ `sentinel2024` (digits can appear after letters)
- ✅ `publisher123abc` (mixed letters and digits)

**Invalid Examples:**
- ❌ `azure-sentinel` (contains hyphen)
- ❌ `microsoft_sentinel` (contains underscore)
- ❌ `sentinel.community` (contains dot)
- ❌ `sentinel@microsoft` (contains special character)

**Validation Checks:**
```typescript
function validatePublisherId(publisherId: string): ValidationResult {
  const isValid = /^[a-z][a-z0-9]{0,49}$/.test(publisherId);
  const hasSpecialChars = /[^a-z0-9]/.test(publisherId);
  const startsWithLetter = /^[a-z]/.test(publisherId);
  const lengthValid = publisherId.length <= 50;
  
  return {
    valid: isValid,
    errors: [
      !startsWithLetter && 'Publisher ID must start with a letter',
      hasSpecialChars && 'Publisher ID contains invalid special characters. Only alphanumeric characters (a-z, 0-9) are allowed',
      !lengthValid && 'Publisher ID exceeds maximum length of 50 characters',
      !['azuresentinel', 'microsoftsentinelcommunity'].includes(publisherId) && 'Custom publisher ID not recognized. Must be pre-approved'
    ].filter(Boolean)
  };
}
```

### 2. **Offer ID Validation**

**Conditional Rules Based on Support Tier:**

#### For Microsoft Tier Solutions:
```regex
offerId: ^azure-sentinel-solution-[a-z0-9-]+$
```
- Must start with `azure-sentinel-solution-`
- Use kebab-case for solution name portion
- Must match the solution folder name (normalized to kebab-case)
- No spaces, special characters, or uppercase letters
- Maximum length: 50 characters

**Valid Examples:**
- ✅ `azure-sentinel-solution-microsoft-entra-id`
- ✅ `azure-sentinel-solution-crowdstrike-falcon`
- ✅ `azure-sentinel-solution-my-custom-app`

**Invalid Examples:**
- ❌ `AzureSentinel-Solution-EntraID` (wrong casing)
- ❌ `azure-sentinel-solution-microsoft_entra_id` (underscores not allowed)
- ❌ `azure-sentinel-solution-Microsoft Entra ID` (spaces and uppercase)

**Offer ID Consistency Check:**
The offer ID must match the solution folder structure:
- Folder: `Solutions/Microsoft Entra ID/`
- Expected Offer ID: `azure-sentinel-solution-microsoft-entra-id`

#### For Partner or Community Tier Solutions:
- Offer ID must contain the keyword `sentinel` (case-insensitive)
- Can use any other valid string format with 'sentinel' included
- Must be alphanumeric (can include special characters like hyphens, underscores)
- Maximum length: 50 characters
- Should be unique and descriptive of the solution

**Valid Examples:**
- ✅ `partner-sentinel-app-v1` (contains 'sentinel')
- ✅ `community-sentinel_custom_solution` (contains 'sentinel')
- ✅ `sentinel-my-app-connector` (contains 'sentinel')
- ✅ `ThirdPartyApp_Sentinel_Integration` (contains 'sentinel')
- ✅ `sentinel.custom.solution.name` (contains 'sentinel')

**Invalid Examples:**
- ❌ `partner-solution-app-v1` (missing 'sentinel' keyword)
- ❌ `community_custom_solution` (missing 'sentinel' keyword)

**Validation Logic:**
```typescript
function validateOfferId(offerId: string, tier: string): ValidationResult {
  const maxLength = offerId.length <= 50;
  
  if (tier === 'Microsoft') {
    // Strict Microsoft tier format
    const microsoftFormat = /^azure-sentinel-solution-[a-z0-9-]+$/.test(offerId);
    return {
      valid: microsoftFormat && maxLength,
      errors: [
        !microsoftFormat && 'Microsoft tier requires format: azure-sentinel-solution-[kebab-case]',
        !maxLength && 'Offer ID exceeds maximum length of 50 characters'
      ].filter(Boolean)
    };
  } else if (tier === 'Partner' || tier === 'Community') {
    // Flexible format for Partner and Community tiers, must contain 'sentinel'
    const hasValidChars = /^[a-zA-Z0-9\-_.]+$/.test(offerId);
    const containsSentinel = offerId.toLowerCase().includes('sentinel');
    return {
      valid: hasValidChars && maxLength && containsSentinel,
      errors: [
        !hasValidChars && 'Offer ID contains invalid characters',
        !maxLength && 'Offer ID exceeds maximum length of 50 characters',
        !containsSentinel && 'Offer ID must contain the keyword "sentinel"'
      ].filter(Boolean)
    };
  }
}
```

### 3. **Date Format Validation**
```regex
firstPublishDate: ^\\d{4}-\\d{2}-\\d{2}$
```
- Must be valid ISO 8601 date format (YYYY-MM-DD)
- **Cannot be a future date** - Must be less than or equal to today's date (CRITICAL)
- Should align with actual solution creation date

**Valid Examples:**
- ✅ `2024-01-15` (past date)
- ✅ `YYYY-MM-DD` (today's date or earlier)

**Invalid Examples:**
- ❌ `2030-10-20` (future date)
- ❌ `16/05/2022` (wrong format)
- ❌ `2025-13-45` (invalid month/day)

**CRITICAL: Copilot Review Requirement**
- Copilot must call this validation function for every SolutionMetadata.json review.
- If the function returns an error about a future date, Copilot must output a comment like:
  - ❌ "firstPublishDate is set to 2030-10-20, which is a future date. It must not be in the future (today is YYYY-MM-DD)."

### 4. **Provider Validation**
```json
{
  "providers": ["Microsoft"]  // Must be array, not string
}
```
- Must be an array, not a string
- Valid providers: "Microsoft", "Community", approved third-party names
- Case-sensitive matching required

### 5. **Support Structure Validation**
```json
{
  "support": {
    "tier": "Microsoft",           // Required: Must be exactly "Microsoft", "Community", or "Partner" (CASE-SENSITIVE)
    "name": "string",             // Required: Support organization name
    "email": "valid-email",       // Required: Valid email format
    "link": "valid-url"           // Required: Valid HTTPS URL that is workable/accessible
  }
}
```

**Support Tier Requirements (CASE-SENSITIVE):**
- ✅ `"tier": "Microsoft"` (correct casing)
- ✅ `"tier": "Community"` (correct casing)
- ✅ `"tier": "Partner"` (correct casing)
- ❌ `"tier": "microsoft"` (lowercase - INVALID)
- ❌ `"tier": "partner"` (lowercase - INVALID)
- ❌ `"tier": "community"` (lowercase - INVALID)

### 6. **Support Link Validation**
```regex
link: ^https:\/\/[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=]+$
```
- Must be a valid HTTPS URL (HTTP not allowed)
- Must be a working/accessible URL
- Must point to actual support resources:
  - Microsoft solutions: Should point to official Microsoft support pages (e.g., `https://support.microsoft.com/`)
  - Partner solutions: Should point to partner's support page or product documentation
  - Community solutions: Should point to GitHub repository, community forum, or documentation site
- URL must not contain spaces or invalid characters
- URL should be verified to be accessible and not return 404 or timeout errors

**Valid Examples:**
- ✅ `https://support.microsoft.com/`
- ✅ `https://github.com/Azure/Azure-Sentinel/issues`
- ✅ `https://docs.microsoft.com/azure/sentinel/`
- ✅ `https://vendor.com/support`

**Invalid Examples:**
- ❌ `http://support.microsoft.com/` (HTTP instead of HTTPS)
- ❌ `support@microsoft.com` (Email address, not URL)
- ❌ `https://` (Incomplete URL)
- ❌ `https://broken-link-that-does-not-exist.xyz/404` (Non-existent/broken link)

## Common PR Review Issues

### ❌ **Invalid Publisher ID (Special Characters)**
```json
{
  "publisherId": "azure-sentinel",  // Invalid: contains hyphen
  "offerId": "azure-sentinel-solution-test"
}
```
**Error**: Publisher ID must contain only alphanumeric characters (a-z, 0-9). Hyphens, underscores, and other special characters are not allowed.

**Correction:**
```json
{
  "publisherId": "azuresentinel",   // Valid: alphanumeric only
  "offerId": "azure-sentinel-solution-test"
}
```

### ❌ **Incorrect Publisher ID**
```json
{
  "publisherId": "microsoft",  // Should be "azuresentinel"
  "offerId": "EntraID"        // Should follow naming convention
}
```

### ❌ **Invalid Date Format**
```json
{
  "firstPublishDate": "16/05/2022"  // Should be "2022-05-16"
}
```

### ❌ **Missing Required Fields**
```json
{
  "publisherId": "azuresentinel",
  // Missing offerId, firstPublishDate, providers, categories, support
}
```

### ❌ **Invalid Category Domain**
```json
{
  "categories": {
    "domains": ["Authentication"]  // Should be "Identity"
  }
}
```

## Automated Validation Patterns

### Schema Validation
```typescript
const metadataSchema = {
  required: ['publisherId', 'offerId', 'firstPublishDate', 'providers', 'categories', 'support'],
  properties: {
    publisherId: { 
      pattern: '^[a-z][a-z0-9]{0,49}$',
      description: 'Must start with letter, contain only lowercase letters and digits (a-z, 0-9). Approved: "azuresentinel", "microsoftsentinelcommunity", or pre-approved custom IDs'
    },
    offerId: { 
      type: 'string',
      description: 'Format depends on support.tier. See conditionalRules for tier-specific patterns'
    },
    firstPublishDate: { format: 'date', description: 'ISO 8601 format (YYYY-MM-DD), must not be a future date' },
    providers: { type: 'array', items: { type: 'string' } },
    support: {
      type: 'object',
      properties: {
        tier: { enum: ['Microsoft', 'Partner', 'Community'], description: 'Support tier (case-sensitive)' },
        name: { type: 'string' },
        email: { format: 'email' },
        link: { format: 'url', pattern: '^https://' }
      }
    }
  },
  conditionalRules: {
    offerIdByTier: {
      condition: (data) => data.support && data.support.tier,
      validation: (data) => {
        if (data.support.tier === 'Microsoft') {
          // Microsoft tier: must follow strict format
          return /^azure-sentinel-solution-[a-z0-9-]+$/.test(data.offerId);
        } else if (data.support.tier === 'Partner' || data.support.tier === 'Community') {
          // Partner/Community tier: flexible format but must contain 'sentinel' keyword
          const hasValidChars = /^[a-zA-Z0-9\-_.]+$/.test(data.offerId);
          const containsSentinel = data.offerId.toLowerCase().includes('sentinel');
          const lengthValid = data.offerId.length <= 50;
          return hasValidChars && containsSentinel && lengthValid;
        }
        return true;
      },
      message: (data) => {
        if (data.support.tier === 'Partner' || data.support.tier === 'Community') {
          if (!data.offerId.toLowerCase().includes('sentinel')) {
            return `offerId must contain the keyword "sentinel" for ${data.support.tier} tier`;
          }
        }
        return `offerId must follow tier-specific rules. Tier: ${data.support.tier}`;
      }
    },
    publisherIdValidation: {
      condition: (data) => data.publisherId,
      validation: (data) => {
        const approved = ['azuresentinel', 'microsoftsentinelcommunity'];
        const isApproved = approved.includes(data.publisherId);
        const isValidFormat = /^[a-z][a-z0-9]{0,49}$/.test(data.publisherId);
        return isValidFormat && (isApproved || isCustomPreApproved(data.publisherId));
      },
      message: 'publisherId must be approved or pre-approved custom ID'
    },
    futureDate: {
      condition: (data) => data.firstPublishDate,
      validation: (data) => new Date(data.firstPublishDate) <= new Date(),
      message: 'firstPublishDate cannot be in the future'
    }
  }
};
```

### Consistency Validation
```typescript
function validateConsistency(metadata: SolutionMetadata, folderPath: string): ValidationResult {
  const folderName = path.basename(folderPath);
  // Normalize: lowercase, replace non-alphanumeric runs with single dash, trim repeated dashes
  const normalizedFolder = folderName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')     // Replace any non-alphanumeric runs with single dash
    .replace(/^-+|-+$/g, '');         // Trim leading/trailing dashes
  const expectedOfferId = `azure-sentinel-solution-${normalizedFolder}`;
  
  return {
    offerIdMatches: metadata.offerId === expectedOfferId,
    publisherValid: ['azuresentinel', 'microsoftsentinelcommunity'].includes(metadata.publisherId),
    dateValid: new Date(metadata.firstPublishDate) <= new Date(),
    supportComplete: validateSupportStructure(metadata.support)
  };
}
```

## Best Practices for Solution Metadata

1. **Consistent Naming**: Ensure offer ID matches solution folder name
2. **Accurate Dates**: Use actual first publish date, not future dates
3. **Complete Support Info**: Always include all support structure fields
4. **Appropriate Categories**: Choose domains that accurately represent the solution
5. **Version Management**: Update metadata when solution capabilities change
6. **Documentation Alignment**: Ensure metadata matches solution documentation