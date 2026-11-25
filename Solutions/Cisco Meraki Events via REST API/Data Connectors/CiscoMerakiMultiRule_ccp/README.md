# Cisco Meraki Air Marshal ingestion

The Air Marshal collector lists an organization's wireless networks and calls
`/networks/{networkId}/wireless/airMarshal` for each network. Cisco's scan results
do not include the network ID.

The collector retains the parent network record as `network` and the child scan
results as `expand`. The CCF nested `MvExpandTransformer` emits one row per scan
result with its parent network attached. The Air Marshal DCR input stream therefore
contains two dynamic columns, `network` and `expand`.

The DCR maps `network.id` to `NetworkId`, preserves `expand.types` as the dynamic
`Types` array, and converts `firstSeen`, `lastSeen`, and `wiredLastSeen` from Unix
epoch seconds to UTC datetimes. `TimeGenerated` uses the converted `LastSeen`,
falling back to ingestion time when it is absent. Other event timestamps remain
null when absent.

All classifications are retained, including empty arrays; ingestion does not
filter out unclassified SSIDs. For example, query classified results with:

```kusto
CiscoMerakiAirMarshalEvents
| where Types has_any ("rogue", "spoof")
| project TimeGenerated, NetworkId, Ssid, Types, FirstSeen, LastSeen, WiredLastSeen
```

## Updating existing installations

Deploy the updated Air Marshal table schema, DCR, and polling configuration
together. The joined input shape is not compatible with the previous flat DCR
input stream. Updating only the saved-search alias or table schema does not fix
collection. Existing ingested rows with missing values are not repaired by this
change.

After updating, verify new scan results from multiple networks, including the
same SSID in different networks. Each result must retain its own `NetworkId`,
classification array, and converted timestamps. Also verify networks with no
scan results do not produce event rows.

References:

- [Cisco Air Marshal API](https://developer.cisco.com/meraki/api-v1/get-network-wireless-air-marshal/)
- [CCF nested API polling](https://learn.microsoft.com/azure/sentinel/isv/custom-connector-nested-api-polling)
