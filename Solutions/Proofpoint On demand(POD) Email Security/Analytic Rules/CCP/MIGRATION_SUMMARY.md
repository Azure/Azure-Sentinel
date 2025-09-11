# ProofpointPOD Analytics Rules Migration Summary

## Overview
This document summarizes the migration of ProofpointPOD analytics rules from the legacy Azure Functions connector to the new Codeless Connector Platform (CCP) connector.

## Key Changes

### Table Name Changes
- **Old (Azure Functions):** `ProofpointPOD_message_CL` 
- **New (CCP):** `ProofpointPODMessage_CL`

### Data Connector Changes
- **Old Connector ID:** `ProofpointPOD`
- **New Connector ID:** `ProofpointPODEmailSecurity_CCP`

### Field Access Changes
The new CCP connector stores data in dynamic columns rather than flattened fields:

| Old Field Access | New Field Access |
|------------------|------------------|
| `EventType == 'message'` | Not needed (table is message-specific) |
| `NetworkDirection == 'outbound'` | `tostring(filter.routeDirection) == 'outbound'` |
| `SrcUserUpn` | `tostring(envelope.from)` |
| `DstUserUpn` | `tostring(envelope.rcpts)` |

## Migrated Analytics Rules

### 1. ProofpointPOD CCP - Possible data exfiltration to private email

**Purpose:** Detects when sender sent email to the non-corporate domain and recipient's username is the same as sender's username.

**Key Changes:**
- Updated table name to `ProofpointPODMessage_CL`
- Updated connector ID to `ProofpointPODEmailSecurity_CCP`
- Updated field access patterns to use dynamic objects
- Maintained same detection logic and entity mappings

**File:** `/Analytic Rules/CCP/ProofpointPOD_CCP_DataExfiltrationToPrivateEmail.yaml`

## Migration Notes

1. **Table Structure:** The CCP connector uses a more structured approach with dynamic columns (`envelope`, `filter`, `msg`, etc.) rather than flattened fields.

2. **Data Access:** Fields are accessed using dynamic object notation (e.g., `envelope.from` instead of direct field names).

3. **Event Type Filtering:** The old connector required filtering by `EventType == 'message'`, but the new CCP connector has separate tables for different event types.

4. **Backward Compatibility:** The old analytics rules will continue to work with the legacy Azure Functions connector until it's deprecated.

## Testing Recommendations

1. Deploy the new CCP connector alongside the existing one
2. Test the new analytics rules with actual data
3. Compare detection results between old and new rules
4. Gradually migrate detection rules once validated
5. Monitor for any false positives or missing detections

## Future Work

Additional analytics rules can be migrated following the same pattern:
- Update table names
- Update connector IDs  
- Update field access patterns
- Test thoroughly before deployment
