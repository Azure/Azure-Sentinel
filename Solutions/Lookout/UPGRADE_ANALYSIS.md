# Lookout Mobile Risk API v2 Upgrade Analysis

## Current State Analysis

### Existing Implementation
- **Current API Version**: Using Mobile Risk API v2 streaming endpoint (`/mra/stream/v2/events`)
- **Table Schema**: `LookoutMtdV2_CL` with limited field set (11 columns)
- **Data Ingestion**: Codeless Connector Platform (CCP) with basic field mapping
- **Parser**: Legacy parser targeting `Lookout_CL` table with v1 field structure

### Current Field Coverage
**Currently Captured Fields:**
- `id` (string)
- `enterprise_guid` (string) 
- `actor_device_guid` (string) - derived from actor.guid
- `created_time` (datetime)
- `log_type` (string) - derived from type
- `change_type` (string)
- `device` (dynamic)
- `threat` (dynamic)
- `audit` (dynamic)
- `smishing_alert` (dynamic)
- `target` (dynamic)
- `actor` (dynamic)

## API v2 Enhanced Capabilities

### Event Types Supported
- **DEVICE**: Device management and status events
- **THREAT**: Security threat detection events
- **AUDIT**: Administrative and configuration audit events
- **SMISHING_ALERT**: SMS phishing detection events

### Enhanced Field Schema (From API Documentation)
**Device Object Fields:**
- `activated_at` (string)
- `activation_status` (string)
- `checkin_time` (string)
- `client` object with:
  - `lookout_sdk_version` (string)
  - `ota_version` (string)
  - `package_name` (string)
  - `package_version` (string)
- `customer_device_id` (string)
- `deactivated_at` (string)
- `details` object with:
  - `external_id` (string)
  - `mdm_connector_id` (number)
  - `mdm_connector_uuid` (string)
- `device_group_guid` (string)
- `device_permissions` array
- `device_settings` object
- Additional device metadata fields

**Threat Object Fields:**
- Enhanced threat classification
- Detailed threat assessment data
- Risk scoring information
- Threat mitigation status

**Audit Object Fields:**
- `attribute_changes` array with:
  - `from` (string)
  - `name` (string)
  - `to` (string)
- `type` (string)
- Administrative action details

## Gap Analysis

### Missing Field Mappings
1. **Device Management Fields**: activation_status, checkin_time, device_permissions
2. **Client Information**: SDK versions, package details
3. **MDM Integration**: connector IDs and external references
4. **Enhanced Threat Data**: Detailed classifications and assessments
5. **Audit Trail Details**: Granular attribute change tracking
6. **Smishing Alert Data**: SMS threat detection specifics

### Parser Limitations
- Current parser targets legacy `Lookout_CL` table
- Limited field extraction from dynamic objects
- No support for new v2 event types
- Missing normalization for enhanced security fields

### Analytics and Visualization Gaps
- Analytics rules use legacy field names
- Workbooks don't leverage enhanced threat intelligence
- No hunting queries for new event types
- Limited correlation capabilities with enhanced data

## Recommended Architecture

### Data Flow Enhancement
```
API v2 Events → Enhanced DCR Transformation → Expanded Table Schema → Updated Parser → Enhanced Analytics
```

### Backward Compatibility Strategy
- Maintain existing `LookoutMtdV2_CL` table structure
- Add new fields without breaking existing queries
- Update parser to support both legacy and enhanced field access
- Provide migration path for existing analytics rules

## Implementation Priority

### Phase 1: Core Infrastructure
1. Expand table schema with all v2 fields
2. Update DCR transformations for comprehensive field extraction
3. Enhance parser for v2 field support

### Phase 2: Analytics Enhancement
1. Update existing analytics rules
2. Create new threat detection rules using v2 fields
3. Enhance workbook visualizations

### Phase 3: Advanced Features
1. Create hunting queries for new event types
2. Implement advanced correlation rules
3. Add comprehensive error handling and validation

## Security and Compliance Considerations

### Enhanced Security Fields
- Detailed threat classifications for better risk assessment
- Device compliance status tracking
- Administrative audit trail for governance
- SMS phishing detection for communication security

### Data Retention and Privacy
- Ensure new fields comply with data retention policies
- Implement appropriate data masking for sensitive fields
- Maintain audit trail for compliance requirements