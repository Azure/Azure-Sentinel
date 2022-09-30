# Tagging at ingestion time

Tagging each record with additional information can be extremely useful to add context and ease the resolution of security incidents. We have seen this feature being used by customers that need to identify each record with the owning entity/team. Another use case is adding more info about an event, for example, adding a text description to an event ID.

## Enriching an event with additional meaningful information

In this case we add context to the event. This example, tags all events with the type of IP address in the *SrcAddress* field.

```kusto
source 
| extend Int_Ext_IP_CF = case(toint(case(substring(SrcAddr,0,3) contains '.', substring(SrcAddr,0,2), substring(SrcAddr,0,3))) >100, 'Internal IP', 'External IP')
```

As you can see, we check if the first octet in the source IP address is greated than 100, in which case we tag it as internal.

Deploy this DCR:

[![Deploy this DCR to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FTransformations-Library%2FTagging%2FEnrichmentDCR.json)

## Translating a value into a customer’s business related value

Here we two things: extract contents from a dynamic (json) field intoa separate fields and using internal information to add company division names.

```kusto
let divisions = parse_json('{"US": "HQ-WW","IL": "CyberEMEA"}');
source
| extend division_CF = divisions[Location], city_CF = tostring(LocationDetails.city) | extend countryOrRegion_CF = tostring(LocationDetails.countryOrRegion) | extend state_CF = tostring(LocationDetails.state)
```

As you can see, we start by creating a collection of JSON key value pairs, which we then use to populate the division custom field. The rest of the custom fields are extracted from an existing JSON field in the original record. This will avoid additional effort when querying these logs as part of investigations.