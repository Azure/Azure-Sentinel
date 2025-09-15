# Lookout Mobile Risk API v2 Field Mapping Specification

## Current Table Schema vs Required v2 Schema

### Current LookoutMtdV2_CL Schema
```json
{
  "TimeGenerated": "datetime",
  "id": "string",
  "enterprise_guid": "string", 
  "actor_device_guid": "string",
  "created_time": "datetime",
  "log_type": "string",
  "change_type": "string",
  "device": "dynamic",
  "threat": "dynamic",
  "audit": "dynamic",
  "smishing_alert": "dynamic",
  "target": "dynamic",
  "actor": "dynamic"
}
```

### Enhanced v2 Schema Requirements

#### Core Event Fields
| Field Name | Type | Source | Description |
|------------|------|--------|-------------|
| `TimeGenerated` | datetime | System | Azure Sentinel timestamp |
| `id` | string | `$.id` | Event unique identifier |
| `enterprise_guid` | string | `$.enterprise_guid` | Enterprise identifier |
| `created_time` | datetime | `$.created_time` | Event creation time |
| `event_type` | string | `$.type` | Event type (DEVICE/THREAT/AUDIT/SMISHING_ALERT) |
| `change_type` | string | `$.change_type` | Change operation type |

#### Device Fields (Extracted from device object)
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `device_guid` | string | `$.device.guid` | Device unique identifier |
| `device_activated_at` | datetime | `$.device.activated_at` | Device activation timestamp |
| `device_activation_status` | string | `$.device.activation_status` | Current activation status |
| `device_checkin_time` | datetime | `$.device.checkin_time` | Last device check-in |
| `device_customer_id` | string | `$.device.customer_device_id` | Customer device identifier |
| `device_deactivated_at` | datetime | `$.device.deactivated_at` | Device deactivation timestamp |
| `device_group_guid` | string | `$.device.device_group_guid` | Device group identifier |
| `device_platform` | string | `$.device.platform` | Device platform (iOS/Android) |
| `device_os_version` | string | `$.device.os_version` | Operating system version |
| `device_manufacturer` | string | `$.device.manufacturer` | Device manufacturer |
| `device_model` | string | `$.device.model` | Device model |
| `device_email_address` | string | `$.device.email_address` | Associated email address |

#### Client Application Fields
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `client_lookout_sdk_version` | string | `$.device.client.lookout_sdk_version` | Lookout SDK version |
| `client_ota_version` | string | `$.device.client.ota_version` | OTA version |
| `client_package_name` | string | `$.device.client.package_name` | Client package name |
| `client_package_version` | string | `$.device.client.package_version` | Client package version |

#### MDM Integration Fields
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `mdm_connector_id` | int | `$.device.details.mdm_connector_id` | MDM connector ID |
| `mdm_connector_uuid` | string | `$.device.details.mdm_connector_uuid` | MDM connector UUID |
| `mdm_external_id` | string | `$.device.details.external_id` | External MDM identifier |

#### Threat Fields (Extracted from threat object)
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `threat_id` | string | `$.threat.id` | Threat unique identifier |
| `threat_type` | string | `$.threat.type` | Threat classification type |
| `threat_action` | string | `$.threat.action` | Threat action (DETECTED/BLOCKED) |
| `threat_severity` | string | `$.threat.severity` | Threat severity level |
| `threat_classifications` | string | `$.threat.classifications` | Threat classifications |
| `threat_assessments` | string | `$.threat.assessments` | Threat assessments |
| `threat_description` | string | `$.threat.description` | Threat description |
| `threat_application_name` | string | `$.threat.application_name` | Associated application |
| `threat_package_name` | string | `$.threat.package_name` | Associated package |
| `threat_package_sha` | string | `$.threat.package_sha` | Package SHA hash |
| `threat_file_name` | string | `$.threat.file_name` | Associated file name |
| `threat_file_path` | string | `$.threat.path` | File path |
| `threat_pcp_reporting_reason` | string | `$.threat.pcp_reporting_reason` | PCP reporting reason |
| `threat_pcp_device_response` | string | `$.threat.pcp_device_response` | PCP device response |

#### Audit Fields (Extracted from audit object)
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `audit_type` | string | `$.audit.type` | Audit event type |
| `audit_attribute_changes` | dynamic | `$.audit.attribute_changes` | Attribute change details |

#### Actor Fields (Extracted from actor object)
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `actor_type` | string | `$.actor.type` | Actor type |
| `actor_guid` | string | `$.actor.guid` | Actor identifier |
| `actor_device_guid` | string | `$.actor.guid` | Actor device GUID (legacy) |

#### Target Fields (Extracted from target object)
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `target_type` | string | `$.target.type` | Target type |
| `target_guid` | string | `$.target.guid` | Target identifier |
| `target_email_address` | string | `$.target.email_address` | Target email |
| `target_platform` | string | `$.target.platform` | Target platform |
| `target_os_version` | string | `$.target.os_version` | Target OS version |
| `target_manufacturer` | string | `$.target.manufacturer` | Target manufacturer |
| `target_model` | string | `$.target.model` | Target model |

#### Smishing Alert Fields
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `smishing_alert_id` | string | `$.smishing_alert.id` | Smishing alert ID |
| `smishing_alert_type` | string | `$.smishing_alert.type` | Alert type |
| `smishing_alert_severity` | string | `$.smishing_alert.severity` | Alert severity |
| `smishing_alert_description` | string | `$.smishing_alert.description` | Alert description |

#### Device Permissions (Array)
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `device_permissions` | dynamic | `$.device.device_permissions` | Device permissions array |

#### Device Settings
| Field Name | Type | Source Path | Description |
|------------|------|-------------|-------------|
| `device_settings` | dynamic | `$.device.device_settings` | Device configuration settings |

## DCR Transformation Logic

### KQL Transformation for Enhanced Field Extraction
```kql
source 
| extend 
    // Core fields
    event_type = tostring(type),
    actor_device_guid = tostring(actor.guid),
    log_type = tostring(type),
    
    // Device fields
    device_guid = tostring(device.guid),
    device_activated_at = todatetime(device.activated_at),
    device_activation_status = tostring(device.activation_status),
    device_checkin_time = todatetime(device.checkin_time),
    device_customer_id = tostring(device.customer_device_id),
    device_deactivated_at = todatetime(device.deactivated_at),
    device_group_guid = tostring(device.device_group_guid),
    device_platform = tostring(device.platform),
    device_os_version = tostring(device.os_version),
    device_manufacturer = tostring(device.manufacturer),
    device_model = tostring(device.model),
    device_email_address = tostring(device.email_address),
    
    // Client fields
    client_lookout_sdk_version = tostring(device.client.lookout_sdk_version),
    client_ota_version = tostring(device.client.ota_version),
    client_package_name = tostring(device.client.package_name),
    client_package_version = tostring(device.client.package_version),
    
    // MDM fields
    mdm_connector_id = toint(device.details.mdm_connector_id),
    mdm_connector_uuid = tostring(device.details.mdm_connector_uuid),
    mdm_external_id = tostring(device.details.external_id),
    
    // Threat fields
    threat_id = tostring(threat.id),
    threat_type = tostring(threat.type),
    threat_action = tostring(threat.action),
    threat_severity = tostring(threat.severity),
    threat_classifications = tostring(threat.classifications),
    threat_assessments = tostring(threat.assessments),
    threat_description = tostring(threat.description),
    threat_application_name = tostring(threat.application_name),
    threat_package_name = tostring(threat.package_name),
    threat_package_sha = tostring(threat.package_sha),
    threat_file_name = tostring(threat.file_name),
    threat_file_path = tostring(threat.path),
    threat_pcp_reporting_reason = tostring(threat.pcp_reporting_reason),
    threat_pcp_device_response = tostring(threat.pcp_device_response),
    
    // Audit fields
    audit_type = tostring(audit.type),
    
    // Actor fields
    actor_type = tostring(actor.type),
    actor_guid = tostring(actor.guid),
    
    // Target fields
    target_type = tostring(target.type),
    target_guid = tostring(target.guid),
    target_email_address = tostring(target.email_address),
    target_platform = tostring(target.platform),
    target_os_version = tostring(target.os_version),
    target_manufacturer = tostring(target.manufacturer),
    target_model = tostring(target.model),
    
    // Smishing fields
    smishing_alert_id = tostring(smishing_alert.id),
    smishing_alert_type = tostring(smishing_alert.type),
    smishing_alert_severity = tostring(smishing_alert.severity),
    smishing_alert_description = tostring(smishing_alert.description),
    
    // Set TimeGenerated
    TimeGenerated = todatetime(created_time)
```

## Backward Compatibility Considerations

### Legacy Field Mapping
- Maintain existing dynamic object fields (`device`, `threat`, `audit`, etc.)
- Preserve current field names for existing queries
- Add new extracted fields alongside existing structure

### Migration Strategy
1. **Phase 1**: Add new fields without removing existing ones
2. **Phase 2**: Update parsers to use both legacy and new field names
3. **Phase 3**: Gradually migrate analytics rules to use new fields
4. **Phase 4**: Deprecate legacy field access patterns (optional)

## Validation Requirements

### Data Type Validation
- Ensure datetime fields parse correctly
- Validate string field lengths and formats
- Check dynamic object structure integrity

### Field Population Testing
- Verify all event types populate appropriate fields
- Test null/empty value handling
- Validate array and object field extraction

### Performance Considerations
- Monitor DCR transformation performance with expanded field set
- Optimize KQL queries for new field structure
- Consider indexing strategy for frequently queried fields