# Standard Tables in Microsoft Sentinel mapping for Scuba and Streams.
$standardStreamMapping = @()

  # key is the Data connector poller StreamName and value is the DCR file streamName
  # Example: For GCP audit, data connector poller file, 'StreamName' should be 'SENTINEL_GCP_AUDIT_LOGS' and in dcr file 'stream' should be 'Microsoft-GCPAuditLogs'. Here SENTINEL_GCP_AUDIT_LOGS is used for Scuba and for table Microsoft-GCPAuditLogs is used.

$standardStreamMapping += @{ Key = 'SENTINEL_GCP_FIREWALL_LOGS'; Value = 'Microsoft-GCPFirewallLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_GCP_AUDIT_LOGS'; Value = 'Microsoft-GCPAuditLogs'}

# Function to check if a key exists in the array of hashtables
function GetKeyValue {
  param (
      [string]$key
  )

  # Iterate through each hashtable in the array
  foreach ($pair in $standardStreamMapping) {
      # Explicitly check if the 'Key' property matches the key you're looking for
      if ($pair["Key"] -eq $key) {
          return $pair["Value"]  # Key found
      }
  }

  return $null  # Key not found
}