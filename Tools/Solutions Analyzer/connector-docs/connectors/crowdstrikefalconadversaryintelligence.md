# CrowdStrike Falcon Adversary Intelligence 

| | |
|----------|-------|
| **Connector ID** | `CrowdStrikeFalconAdversaryIntelligence` |
| **Publisher** | CrowdStrike |
| **Tables Ingested** | [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md) |
| **Connector Definition Files** | [CrowdStrikeFalconAdversaryIntelligence_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeFalconAdversaryIntelligence/CrowdStrikeFalconAdversaryIntelligence_FunctionApp.json) |

The [CrowdStrike](https://www.crowdstrike.com/) Falcon Indicators of Compromise connector retrieves the Indicators of Compromise from the Falcon Intel API and uploads them [Microsoft Sentinel Threat Intel](https://learn.microsoft.com/en-us/azure/sentinel/understand-threat-intelligence).

[← Back to Connectors Index](../connectors-index.md)
