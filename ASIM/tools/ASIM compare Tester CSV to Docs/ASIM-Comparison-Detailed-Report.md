# ASIM Schema Comparison Report

Comparison of CSV field definitions with documentation.

## Executive Summary

| Metric | Count |
|--------|-------|
| Schemas Compared | 12 |
| Total Fields Missing in Docs (Errors) | 0 |
| Total Fields Missing in Docs (Warnings) | 19 |
| Total Fields Missing in CSV | 1 |
| Total Type Mismatches (Errors) | 0 |
| Total Class Mismatches (Errors) | 0 |
| Total Warnings | 45 |

### Warning Categories

Warnings are issues that are known limitations or expected based on documentation patterns:

- **SpecificIDsDocumentedCentrally**: User ID fields (e.g., *UserAadId, *UserSid) are documented in a central location
- **LogicalTypeNotInDocs**: CSV has a logical type but docs show the physical type - logical type should be added to docs
- **ComplexAliasNotSupported**: Field is marked as Alias in docs but ASIM tester doesn't support complex aliases
- **ConditionalNotSupported**: Field is marked as Conditional in docs but ASIM tester doesn't support conditional class logic

## Schema-by-Schema Analysis

### AlertEvent

**Doc File:** `normalization-schema-alert.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 96 |
| Doc Fields | 96 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 0 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 0 |

### AuditEvent

**Doc File:** `normalization-schema-audit.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 132 |
| Doc Fields | 130 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 2 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 5 |

#### Warnings

**ComplexAliasNotSupported:**
- `Dst` (CSV=Recommended, Doc=Alias)
- `Src` (CSV=Recommended, Doc=Alias)

**ConditionalNotSupported:**
- `ValueType` (CSV=Optional, Doc=Conditional)

**SpecificIDsDocumentedCentrally:**
- `ActorUserAadId` (string, Optional)
- `ActorUserSid` (string, Optional)


### Authentication

**Doc File:** `normalization-schema-authentication.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 135 |
| Doc Fields | 135 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 0 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 3 |

#### Warnings

**ComplexAliasNotSupported:**
- `Dst` (CSV=Recommended, Doc=Alias)
- `LogonTarget` (CSV=Optional, Doc=Alias)
- `User` (CSV=Optional, Doc=Alias)


### Common

**Doc File:** `normalization-common-fields.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 43 |
| Doc Fields | 43 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 0 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 1 |

#### Warnings

**ComplexAliasNotSupported:**
- `Dvc` (CSV=Mandatory, Doc=Alias)


### DhcpEvent

**Doc File:** `normalization-schema-dhcp.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 102 |
| Doc Fields | 102 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 0 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 1 |

#### Warnings

**ComplexAliasNotSupported:**
- `Src` (CSV=Recommended, Doc=Alias)


### Dns

**Doc File:** `normalization-schema-dns.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 149 |
| Doc Fields | 145 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 4 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 8 |

#### Warnings

**ComplexAliasNotSupported:**
- `Dst` (CSV=Recommended, Doc=Alias)
- `Src` (CSV=Mandatory, Doc=Alias)

**ConditionalNotSupported:**
- `ThreatField` (CSV=Optional, Doc=Conditional)

**LogicalTypeNotInDocs:**
- `DnsQuery` (CSV=RecommendedDnsDomain, Doc=String)

**SpecificIDsDocumentedCentrally:**
- `SrcUserAWSId` (string, Optional)
- `SrcUserAadId` (string, Optional)
- `SrcUserOktaId` (string, Optional)
- `SrcUserSid` (string, Optional)


### FileEvent

**Doc File:** `normalization-schema-file-event.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 136 |
| Doc Fields | 133 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 4 |
| Missing in CSV | 1 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 8 |

#### Fields Missing in CSV

- `URL`

#### Warnings

**ComplexAliasNotSupported:**
- `Src` (CSV=Optional, Doc=Alias)

**ConditionalNotSupported:**
- `Rule` (CSV=Alias, Doc=Conditional)

**LogicalTypeNotInDocs:**
- `HttpUserAgent` (CSV=Useragent, Doc=String)
- `NetworkApplicationProtocol` (CSV=Protocol, Doc=String)

**SpecificIDsDocumentedCentrally:**
- `ActorUpn` (string, Optional)
- `ActorUserAadId` (string, Optional)
- `ActorUserPuid` (string, Optional)
- `ActorUserSid` (string, Optional)


### NetworkSession

**Doc File:** `normalization-schema-network.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 172 |
| Doc Fields | 172 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 0 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 2 |

#### Warnings

**ComplexAliasNotSupported:**
- `Dst` (CSV=Recommended, Doc=Alias)
- `Src` (CSV=Recommended, Doc=Alias)


### ProcessEvent

**Doc File:** `normalization-schema-process-event.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 150 |
| Doc Fields | 144 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 6 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 7 |

#### Warnings

**ConditionalNotSupported:**
- `Rule` (CSV=Alias, Doc=Conditional)

**SpecificIDsDocumentedCentrally:**
- `ActorUserAadId` (string, Optional)
- `ActorUserSid` (string, Optional)
- `ActorUserUpn` (string, Optional)
- `TargetUserAadId` (string, Optional)
- `TargetUserSid` (string, Optional)
- `TargetUserUpn` (string, Optional)


### RegistryEvent

**Doc File:** `normalization-schema-registry-event.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 79 |
| Doc Fields | 79 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 0 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 1 |

#### Warnings

**ConditionalNotSupported:**
- `Rule` (CSV=Alias, Doc=Conditional)


### UserManagement

**Doc File:** `normalization-schema-user-management.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 116 |
| Doc Fields | 113 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 3 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 4 |

#### Warnings

**ConditionalNotSupported:**
- `Rule` (CSV=Alias, Doc=Conditional)

**SpecificIDsDocumentedCentrally:**
- `ActorUserAadId` (string, Optional)
- `ActorUserSid` (string, Optional)
- `TargetUserUid` (string, Optional)


### WebSession

**Doc File:** `normalization-schema-web.md`

| Metric | Count |
|--------|-------|
| CSV Fields | 205 |
| Doc Fields | 205 |
| Missing in Doc (Errors) | 0 |
| Missing in Doc (Warnings) | 0 |
| Missing in CSV | 0 |
| Type Mismatches (Errors) | 0 |
| Class Mismatches (Errors) | 0 |
| Warnings | 5 |

#### Warnings

**ComplexAliasNotSupported:**
- `Dst` (CSV=Mandatory, Doc=Alias)
- `Src` (CSV=Recommended, Doc=Alias)

**ConditionalNotSupported:**
- `ThreatField` (CSV=Optional, Doc=Conditional)

**EnumerationNotSupported:**
- `HttpRequestMethod` (CSV=string, Doc=Enumerated)

**LogicalTypeNotInDocs:**
- `HttpUserAgent` (CSV=Useragent, Doc=String)
