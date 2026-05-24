Markdown
# Fortinet FortiNDR Cloud KQL Log Parser Installation

This parser normalizes and unpacks dynamic log entries sent via Data Collection Rules into structured, queryable data columns matching your Microsoft Sentinel dashboards.

## Installation Instructions

1. Log in to the Azure Portal and navigate to your **Log Analytics Workspace** (or Microsoft Sentinel Workspace).
2. On the left navigation pane under the **General** section, click on **Logs**.
3. Copy the entire query block below and paste it into the clean query editor sheet.
4. Click on the **Save** button dropdown on the top toolbar and select **Save as function**.
5. Configure the function parameters exactly as shown:
   * **Function Name:** `Fortinet_FortiNDR_Cloud`
   * **Function Alias:** `Fortinet_FortiNDR_Cloud`
   * **Category:** `Microsoft Sentinel Parser`
6. Click **Save**. 

*(Note: The function alias will take up to 10-15 minutes to register natively inside your workspace across related workbook visualization panels).*

## KQL Query Block

```kql
let FortiNDR_Cloud_suricata_view = view () {
    FortinetFortiNdrCloudRaw_CL
    | where LogTypeSuffix == "suricata"
    | extend parsed = parse_json(RawData)
    | extend
        su_timestamp=tostring(parsed.timestamp),
        su_uuid=tostring(parsed.uuid),
        su_event_type=tostring(parsed.event_type),
        su_customer_id=tostring(parsed.customer_id),
        su_sensor_id=tostring(parsed.sensor_id),
        su_source=tostring(parsed.source),
        su_src_ip=tostring(parsed.src_ip),
        su_src_port=todouble(parsed.src_port),
        su_dst_ip=tostring(parsed.dest_ip),
        su_dst_port=todouble(parsed.dest_port),
        su_proto=tostring(parsed.proto),
        su_sig_id=todouble(parsed.alert_signature_id),
        su_signature=tostring(parsed.alert_signature),
        su_category=tostring(parsed.alert_category),
        su_severity=todouble(parsed.alert_severity),
        su_confidence=todouble(parsed.alert_confidence),
        su_flow_id=tostring(parsed.flow_id),
        su_tx_id=todouble(parsed.tx_id),
        su_app_proto=tostring(parsed.app_proto),
        su_action=tostring(parsed.alert_action),
        su_class=tostring(parsed.alert_class)
    | project
        su_timestamp,
        su_uuid,
        su_event_type,
        su_customer_id,
        su_sensor_id,
        su_source,
        su_src_ip,
        su_src_port,
        su_dst_ip,
        su_dst_port,
        su_proto,
        su_sig_id,
        su_signature,
        su_category,
        su_severity,
        su_confidence,
        su_flow_id,
        su_tx_id,
        su_app_proto,
        su_action,
        su_class,
        Type="FortiNDR_Cloud_suricata"
};
let FortiNDR_Cloud_observation_view = view () {
    FortinetFortiNdrCloudRaw_CL
    | where LogTypeSuffix == "observation"
    | extend parsed = parse_json(RawData)
    | extend
        ob_timestamp=tostring(parsed.timestamp),
        ob_uuid=tostring(parsed.uuid),
        ob_event_type=tostring(parsed.event_type),
        ob_customer_id=tostring(parsed.customer_id),
        ob_sensor_id=tostring(parsed.sensor_id),
        ob_source=tostring(parsed.source),
        ob_src_ip=tostring(parsed.src_ip),
        ob_src_port=todouble(parsed.src_port),
        ob_dst_ip=tostring(parsed.dest_ip),
        ob_dst_port=todouble(parsed.dest_port),
        ob_proto=tostring(parsed.proto),
        ob_type=tostring(parsed.observation_type),
        ob_summary=tostring(parsed.observation_summary),
        ob_details=tostring(parsed.observation_details),
        ob_session_id=tostring(parsed.session_id)
    | project
        ob_timestamp,
        ob_uuid,
        ob_event_type,
        ob_customer_id,
        ob_sensor_id,
        ob_source,
        ob_src_ip,
        ob_src_port,
        ob_dst_ip,
        ob_dst_port,
        ob_proto,
        ob_type,
        ob_summary,
        ob_details,
        ob_session_id,
        Type="FortiNDR_Cloud_observation"
};
let FortiNDR_Cloud_detection_view = view () {
    FortinetFortiNdrCloudRaw_CL
    | where LogTypeSuffix == "detections"
    | extend parsed = parse_json(RawData)
    | extend
        de_device_ip=tostring(parsed.device_ip),
        de_last_seen=tostring(parsed.last_seen),
        de_status=tostring(parsed.status),
        de_rule_name=tostring(parsed.rule_name),
        de_severity=tostring(parsed.severity),
        de_confidence=tostring(parsed.confidence),
        de_resolved_by=tostring(parsed.resolved_by),
        de_resolution=tostring(parsed.resolution),
        de_resolution_comment=tostring(parsed.resolution_comment),
        de_date_resolved=tostring(parsed.date_resolved),
        de_rule_uuid=tostring(parsed.rule_uuid),
        de_created=tostring(parsed.created),
        de_updated=tostring(parsed.updated),
        de_first_seen=tostring(parsed.first_seen),
        de_muted=tostring(parsed.muted),
        de_rule_muted=tostring(parsed.rule_muted),
        de_mute_comment=tostring(parsed.mute_comment),
        de_muted_by=tostring(parsed.muted_by),
        de_date_muted=tostring(parsed.date_muted),
        de_indicators=tostring(parsed.indicators),
        de_sensor_id=tostring(parsed.sensor_id),
        de_account_id=tostring(parsed.account_id),
        de_uuid=tostring(parsed.uuid),
        de_username=tostring(parsed.username),
        de_hostname=tostring(parsed.hostname),
        de_category=tostring(parsed.rule_category),
        de_event_count=todouble(parsed.event_count),
        de_events=tostring(parsed.events),
        de_primary_attack_id=tostring(parsed.rule_primary_attack_id),
        de_secondary_attack_id=tostring(parsed.rule_secondary_attack_id),
        de_rule_url=tostring(parsed.rule_url)
    | project
        de_device_ip,
        de_event_count,
        de_events,
        de_indicators,
        de_last_seen,
        de_status,
        de_rule_name,
        de_severity,
        de_confidence,
        de_resolved_by,
        de_resolution,
        de_resolution_comment,
        de_date_resolved,
        de_rule_uuid,
        de_category,
        de_created,
        de_updated,
        de_first_seen,
        de_muted,
        de_rule_muted,
        de_mute_comment,
        de_muted_by,
        de_date_muted,
        de_sensor_id,
        de_account_id,
        de_uuid,
        de_username,
        de_hostname,
        de_primary_attack_id,
        de_secondary_attack_id,
        de_rule_url,
        Type="FortiNDR_Cloud_detections"
};
union isfuzzy=true FortiNDR_Cloud_suricata_view, FortiNDR_Cloud_observation_view, FortiNDR_Cloud_detection_view