import json
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parsers_dir = os.path.join(base_dir, "Parsers")
    os.makedirs(parsers_dir, exist_ok=True)

    parser_kql = """// DentiSystemsThreats ASIM Parser Function
// Usage: DentiSystemsThreats
let DentiSystemsThreatEvents = view () {
    DENTIGRIDThreats_CL
    | extend EventVendor = 'DentiSystems', EventProduct = 'DentiGrid', EventProductVersion = '1.0'
    | extend EventStartTime = TimeGenerated, EventEndTime = TimeGenerated
    | extend EventType = 'ThreatIntel', EventSeverity = tostring(coalesce(Severity_s, tostring(Severity_d), 'Medium'))
    | extend SrcIpAddr = coalesce(SourceIP_s, tostring(column_ifexists('ip_s', '')))
    | extend SrcGeoCountry = coalesce(SourceCountry_s, tostring(column_ifexists('country_s', '')))
    | extend SrcGeoCity = coalesce(SourceCity_s, tostring(column_ifexists('city_s', '')))
    | extend DstPortNumber = toint(coalesce(DestinationPort_d, toint(column_ifexists('port_d', 0))))
    | extend NetworkProtocol = coalesce(Protocol_s, tostring(column_ifexists('protocol_s', '')))
    | extend ThreatSignature = coalesce(Signature_s, tostring(column_ifexists('signature_s', '')))
    | extend TargetNodeId = coalesce(NodeID_s, tostring(column_ifexists('node_id_s', '')))
    | extend TargetUrl = coalesce(URL_s, tostring(column_ifexists('url_s', '')))
    | extend HttpMethod = coalesce(Method_s, tostring(column_ifexists('method_s', '')))
    | extend RawPayload = coalesce(Payload_s, tostring(column_ifexists('payload_s', '')))
    | extend IngestionPlatform = coalesce(Platform_s, 'DENTIGRID')
};
DentiSystemsThreatEvents
"""

    with open(os.path.join(parsers_dir, "DentiSystems_ASIM_Parser.kql"), "w", encoding="utf-8") as f:
        f.write(parser_kql)
    print(f"Wrote {os.path.join(parsers_dir, 'DentiSystems_ASIM_Parser.kql')}")

if __name__ == "__main__":
    main()
