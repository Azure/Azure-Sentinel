# Changelog for ASimNetworkSessionCrowdStrikeFalconDataReplicator.yaml

## Version 0.1.0

- (2026-10-26) Initial creation of the CrowdStrike Falcon Data Replicator Network Session parser for CrowdStrike_Network_Events_CL - [PR #15438](https://github.com/Azure/Azure-Sentinel/pull/15438)
- Normalize IPv4 and IPv6 connection, accept, listen, close, raw-bind, and firewall-match events; exclude firewall-rule configuration and local-address removal events.
- Use event_simpleName as the authoritative event type and map available endpoint, process, user, interface, and ICMP fields, including columns empty in the initial samples.
- Preserve undocumented numeric firewall actions and source-only metadata when pack is enabled; do not infer TCP flags from ConnectionFlags.
- Preserve one output record per source record without enrichment, aggregation, or row expansion.
