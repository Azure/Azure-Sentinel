"""Build fixture-only KQL tests. No workspace creation, ingestion or deployment."""

import argparse
import copy
import csv
import datetime
import json
from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[4]
PARSERS = ROOT / "Parsers" / "ASimEmailEvent" / "Parsers"
PRODUCT = "Proofpoint On Demand Email Security"
COLUMNS = {
    "TimeGenerated": "datetime", "eventTime": "datetime", "guid": "string",
    "connection": "dynamic", "envelope": "dynamic", "msg": "dynamic",
    "pps": "dynamic", "metadata": "dynamic", "filter": "dynamic",
    "msgParts": "dynamic",
}


def literal(value, kind):
    if kind == "datetime":
        return "datetime(" + (value or "null") + ")"
    if kind == "dynamic":
        return "dynamic(" + json.dumps(value, ensure_ascii=True) + ")"
    return json.dumps(value, ensure_ascii=True)


def definition(filename, name=None, injected=""):
    document = yaml.safe_load((PARSERS / filename).read_text(encoding="utf-8"))
    parameters = []
    for parameter in document.get("ParserParams", []):
        default = parameter.get("Default")
        text = parameter["Name"] + ":" + parameter["Type"]
        if default is not None:
            if parameter["Type"] == "string":
                text += "=" + json.dumps(default)
            else:
                text += "=" + (str(default).lower() if isinstance(default, bool) else str(default))
        parameters.append(text)
    return (
        "let " + (name or document["ParserName"]) + "=("
        + ",".join(parameters) + "){\n" + injected
        + document["ParserQuery"] + "\n};\n"
    )


def fixture_rows():
    source = ROOT / "Sample Data" / "Custom" / "ProofpointPOD_message_CL.json"
    rows = []
    for record in json.loads(source.read_text(encoding="utf-8")):
        event_time = datetime.datetime.fromisoformat(record["ts"]).astimezone(
            datetime.timezone.utc
        )
        rows.append({
            **{key: record.get(key) for key in COLUMNS if key not in ("TimeGenerated", "eventTime")},
            "eventTime": event_time.isoformat(),
            "TimeGenerated": (event_time + datetime.timedelta(hours=1)).isoformat(),
        })
    base = {
        "TimeGenerated": "2026-01-02T00:00:00Z",
        "eventTime": "2026-01-01T00:00:00Z",
        "guid": "synthetic-base",
        "connection": {"ip": "192.0.2.10", "protocol": "smtp:smtp", "country": "US"},
        "envelope": {"from": "bounce@sender.example", "rcpts": ["recipient@dest.example"]},
        "msg": {
            "parsedAddresses": {
                "from": ["author@sender.example"],
                "to": ["recipient@dest.example", "second@dest.example"],
                "cc": ["copy@dest.example"], "bcc": ["hidden@dest.example"],
            },
            "normalizedHeader": {
                "subject": ["Subject boundary"],
                "reply-to": ["Reply Person <reply@sender.example>"],
            },
            "sizeBytes": 2048, "lang": "en",
        },
        "pps": {"agent": "mx.proofpoint.example", "version": "test", "cid": "synthetic"},
        "metadata": {},
        "filter": {
            "routeDirection": "inbound", "disposition": "continue",
            "modules": {
                "spf": {"result": "pass"},
                "dkimv": [{"result": "pass", "domain": "sender.example"}],
                "dmarc": {"filterdResult": "pass"},
            },
        },
        "msgParts": [],
    }
    synthetic = [base]
    for name, action in (("reject", "reject"), ("quarantine", "quarantine"),
                         ("discard", "discard"), ("unknown", "future-action")):
        row = copy.deepcopy(base)
        row["guid"] = "synthetic-" + name
        row["filter"]["disposition"] = action
        synthetic.append(row)
    for name in ("ipv6", "near-prefix", "auth", "missing", "malformed", "multiple",
                 "scalar", "before", "after", "invalid-arrays"):
        row = copy.deepcopy(base)
        row["guid"] = "synthetic-" + name
        if name == "ipv6":
            row["connection"]["ip"] = "2001:db8::1"
        elif name == "near-prefix":
            row["connection"]["ip"] = "192.0.20.40"
        elif name == "auth":
            row["filter"]["routeDirection"] = "outbound"
            row["filter"]["modules"] = {
                "spf": {"result": "softfail"},
                "dkimv": [{"result": "temperror", "domain": "sender.example"}],
                "dmarc": {"filterdResult": "fail"},
            }
        elif name == "missing":
            row.update(msg=None, envelope=None, pps=None, connection=None, filter=None)
        elif name == "malformed":
            row["eventTime"] = None
            row["msg"] = "not-an-object"
            row["connection"]["ip"] = "not-an-ip"
        elif name == "multiple":
            row["msg"]["parsedAddresses"]["from"].append("second@sender.example")
            row["msg"]["sizeBytes"] = -1
            row["filter"]["modules"]["dkimv"].append({"result": "fail"})
        elif name == "scalar":
            row["msg"]["parsedAddresses"]["to"] = "scalar@dest.example"
            row["filter"]["routeDirection"] = "unrecognized"
            row["filter"]["modules"]["spf"]["result"] = "future-result"
        elif name == "before":
            row["eventTime"] = "2025-12-31T23:59:59Z"
        elif name == "after":
            row["eventTime"] = "2026-01-01T00:00:01Z"
        elif name == "invalid-arrays":
            row["msg"]["parsedAddresses"].update({
                "from": [{"address": "author@sender.example"}],
                "to": [7, {"address": "recipient@dest.example"}],
                "cc": ["copy@dest.example", False],
                "bcc": [None],
            })
        synthetic.append(row)
    return rows, synthetic


def tester_definition(name):
    path = ROOT / "ASIM" / "dev" / "ASimTester"
    document = yaml.safe_load((path / "Testers" / (name + ".yaml")).read_text())
    fields = ["ColumnName", "ColumnType", "Class", "Schema", "LogicalType",
              "ListOfValues", "AliasedField", "DynamicType", "ArrayValuesType"]
    records = []
    with (path / "ASimTester.csv").open(encoding="utf-8-sig") as stream:
        for record in csv.DictReader(stream):
            if record["Schema"] in ("EmailEvent", "Common"):
                record["AliasedField"] = record["Aliased"]
                records.append(",".join(json.dumps(record.get(key, "")) for key in fields))
    table = "datatable(" + ",".join(key + ":string" for key in fields) + ")[\n"
    table += ",\n".join(records) + "\n]"
    pattern = (
        r'externaldata\s*\([^)]*\)\s*\[\s*@"https://raw\.githubusercontent\.com/'
        r'Azure/Azure-Sentinel/master/ASIM/dev/ASimTester/ASimTester\.csv"\s*\]'
        r'\s*with\s*\(format="csv",\s*IgnoreFirstRecord=true\)'
    )
    body, replacements = re.subn(pattern, lambda match: table, document["ParserQuery"])
    if replacements != 1:
        raise ValueError("Tester schema substitution did not match exactly once")
    signature = "T:(ColumnName:string,ColumnType:string)" if name == "ASimSchemaTester" else "T:(*)"
    return "let " + name + "=(" + signature + ",selected_schema:string=''){\n" + body + "\n};\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grafana-datasource-uid")
    parser.add_argument("--grafana-database")
    args = parser.parse_args()
    if bool(args.grafana_datasource_uid) != bool(args.grafana_database):
        parser.error("Supply both Grafana datasource UID and database, or neither")
    args.output.mkdir(parents=True, exist_ok=True)
    public, synthetic = fixture_rows()
    rows = public + synthetic
    fixture = "let ProofpointPODMessage_CL=datatable("
    fixture += ",".join(key + ":" + kind for key, kind in COLUMNS.items()) + ")[\n"
    fixture += ",\n".join(
        ",".join(literal(row.get(key), kind) for key, kind in COLUMNS.items())
        for row in rows
    ) + "\n];\n"
    definitions = "".join(definition(name + ".yaml") for name in (
        "ASimEmailEventProofpointPOD", "vimEmailEventProofpointPOD",
        "vimEmailEventEmpty", "ASimEmailEvent", "imEmailEvent",
    ))
    watchlist = (
        "let _GetWatchlist=(name:string){"
        "datatable(SearchKey:string,SourceSpecificParser:string)[]};\n"
    )
    prelude = fixture + watchlist + definitions
    checks = []

    def check(name, expression):
        checks.append("print Test=" + json.dumps(name) + ",Passed=coalesce((" + expression + "),false)")

    def row(name):
        return '(P | where EventOriginalUid == "synthetic-' + name + '")'

    def value(name, column):
        return "toscalar(" + row(name) + "| project " + column + ")"

    check("one_row_per_source_record", "toscalar(P|count)==" + str(len(rows)))
    check("parameterless_filtered_parity", "toscalar(P|extend H=hash_sha256(tostring(pack_all()))|project EventOriginalUid,H|join kind=fullouter (V|extend H=hash_sha256(tostring(pack_all()))|project EventOriginalUid,H) on EventOriginalUid|where H!=H1 or isempty(EventOriginalUid) or isempty(EventOriginalUid1)|count)==0")
    check("header_sender_not_envelope_sender", value("base", "EmailFromAddress") + '=="author@sender.example" and ' + value("base", "EmailMailFromAddress") + '=="bounce@sender.example"')
    check("header_recipient_array_retained", "toscalar(" + row("base") + '|project tostring(EmailToRecipients))==\'["recipient@dest.example","second@dest.example"]\'')
    check("subject_and_reply_to", value("base", "EmailSubject") + '=="Subject boundary" and ' + value("base", "EmailReplyToAddress") + '=="reply@sender.example"')
    check("event_time_not_ingestion_time", value("base", "EventStartTime") + "==datetime(2026-01-01) and " + value("base", "TimeGenerated") + "==datetime(2026-01-02)")
    check("continue_is_not_delivery", value("base", "DvcAction") + '=="NA" and ' + value("base", "EventResult") + '=="NA" and ' + value("base", "EventType") + '=="EmailInspection"')
    for name, action in (("reject", "Blocked"), ("quarantine", "Quarantined"),
                         ("discard", "Deleted"), ("unknown", "NA")):
        check("action_" + name, value(name, "DvcAction") + "==" + json.dumps(action))
    check("authentication_enums", value("auth", "EmailSpfResult") + '=="SoftFail" and ' + value("auth", "EmailDkimResult") + '=="TemporaryError" and ' + value("auth", "EmailDmarcResult") + '=="Fail"')
    check("missing_objects_keep_row", "toscalar(" + row("missing") + "|count)==1 and " + value("missing", "Dvc") + "==" + json.dumps(PRODUCT))
    check("malformed_input_is_flagged", value("malformed", "EventMessage") + ' has "Invalid" and isempty(' + value("malformed", "SrcIpAddr") + ") and isnull(" + value("malformed", "EventStartTime") + ")")
    check("ambiguous_values_not_guessed", "isempty(" + value("multiple", "EmailFromAddress") + ") and isempty(" + value("multiple", "EmailDkimResult") + ") and isnull(" + value("multiple", "EmailSizeBytes") + ")")
    check("scalar_recipient_normalized", "toscalar(" + row("scalar") + '|project tostring(EmailToRecipients))==\'["scalar@dest.example"]\'')
    check("unknown_direction_and_auth", value("scalar", "EmailDirection") + '=="Unknown" and isempty(' + value("scalar", "EmailSpfResult") + ") and " + value("scalar", "EmailSpfOriginalResult") + '=="future-result"')
    check("invalid_recipient_arrays_flagged", "toscalar(" + row("invalid-arrays") + '|project array_length(EmailToRecipients)+array_length(EmailCCRecipients)+array_length(EmailBCCRecipients))==0 and ' + value("invalid-arrays", "EventMessage") + ' has "Invalid"')
    check("pack_default_empty", "toscalar(P|where array_length(bag_keys(AdditionalFields))!=0|count)==0")
    check("pack_retains_source_detail", 'toscalar(ASimEmailEventProofpointPOD(pack=true)|where EventOriginalUid=="synthetic-base"|project tostring(AdditionalFields.envelope.from))=="bounce@sender.example"')
    filters = [
        ("sender", 'emailfromaddress_has_any=dynamic(["author@sender.example"])', 'EmailFromAddress has_any(dynamic(["author@sender.example"]))'),
        ("recipient_cc", 'emailrecipient_has_any=dynamic(["copy@dest.example"])', 'tostring(EmailCCRecipients) has_any(dynamic(["copy@dest.example"]))'),
        ("recipient_bcc", 'emailrecipient_has_any=dynamic(["hidden@dest.example"])', 'tostring(EmailBCCRecipients) has_any(dynamic(["hidden@dest.example"]))'),
        ("subject", 'emailsubject_has_any=dynamic(["boundary"])', 'EmailSubject has_any(dynamic(["boundary"]))'),
        ("direction", 'emaildirection_in=dynamic(["outbound"])', 'EmailDirection =~ "outbound"'),
        ("location", 'emaildeliverylocation_in=dynamic(["Quarantine"])', 'EmailDeliveryLocation == "Quarantine"'),
        ("time_inclusive", "starttime=datetime(2026-01-01),endtime=datetime(2026-01-01)", "EventStartTime==datetime(2026-01-01)"),
        ("ipv4_prefix", 'ipaddr_has_any_prefix=dynamic(["192.0.2."])', 'SrcIpAddr startswith "192.0.2."'),
        ("ipv6_prefix", 'ipaddr_has_any_prefix=dynamic(["2001:DB8:"])', 'SrcIpAddr startswith "2001:db8:"'),
        ("result_na", 'eventresult="NA"', 'EventResult=="NA"'),
    ]
    for name, arguments, condition in filters:
        expected = "P|where " + condition
        actual = "vimEmailEventProofpointPOD(" + arguments + ")"
        check("filter_" + name, "toscalar(" + actual + "|count)==toscalar(" + expected + "|count) and toscalar(" + expected + "|count)>0 and toscalar(" + actual + "|where not(" + condition + ")|count)==0")
    check("nonmatching_result_empty", 'toscalar(vimEmailEventProofpointPOD(eventresult="Success")|count)==0')
    check("ip_regex_characters_literal", 'toscalar(vimEmailEventProofpointPOD(ipaddr_has_any_prefix=dynamic(["192.0.2.["]))|count)==0')
    check("combined_filters", 'toscalar(vimEmailEventProofpointPOD(emaildirection_in=dynamic(["Outbound"]),emailfromaddress_has_any=dynamic(["author@sender.example"]),ipaddr_has_any_prefix=dynamic(["192.0.2."]))|count)==1')
    check("normalized_unifying_query", 'toscalar(imEmailEvent(emaildirection_in=dynamic(["Outbound"]))|count)==toscalar(P|where EmailDirection=="Outbound"|count)')
    check("parameterless_unifying_query", "toscalar(ASimEmailEvent()|count)==" + str(len(rows)))
    behavior = (
        prelude + "let P=materialize(ASimEmailEventProofpointPOD());\n"
        + "let V=materialize(vimEmailEventProofpointPOD());\nunion\n("
        + "),\n(".join(checks) + ")\n| order by Test asc"
    )
    disabled = (
        'let _GetWatchlist=(name:string){datatable(SearchKey:string,SourceSpecificParser:string)'
        '["ExcludeimEmailEvent","_Im_EmailEvent_ProofpointPOD"]};\n'
    )
    disabled_definition = definition("imEmailEvent.yaml", "DisabledSource", disabled)
    disabled_regular = definition(
        "ASimEmailEvent.yaml", "DisabledRegular",
        'let _GetWatchlist=(name:string){datatable(SearchKey:string,SourceSpecificParser:string)'
        '["ExcludeASimEmailEvent","_ASim_EmailEvent_ProofpointPOD"]};\n',
    )
    disabled_all = definition(
        "imEmailEvent.yaml", "DisabledAll",
        'let _GetWatchlist=(name:string){datatable(SearchKey:string,SourceSpecificParser:string)'
        '["Any","Any"]};\n',
    )
    behavior = behavior.replace("let P=materialize", disabled_definition + "let P=materialize", 1)
    behavior += '\n'
    jobs = [
        {"name": "behavior", "query": behavior},
        {"name": "schema", "query": prelude + tester_definition("ASimSchemaTester") + 'union (ASimEmailEventProofpointPOD()|getschema|invoke ASimSchemaTester("EmailEvent")|extend Variant="regular"),(vimEmailEventProofpointPOD()|getschema|invoke ASimSchemaTester("EmailEvent")|extend Variant="filtered")'},
        {"name": "data", "query": prelude + tester_definition("ASimDataTester") + 'union (ASimEmailEventProofpointPOD()|invoke ASimDataTester("EmailEvent")|extend Variant="regular"),(vimEmailEventProofpointPOD()|invoke ASimDataTester("EmailEvent")|extend Variant="filtered")'},
        {"name": "data_public", "query": prelude + tester_definition("ASimDataTester") + 'union (ASimEmailEventProofpointPOD()|where EventOriginalUid !startswith "synthetic-"|invoke ASimDataTester("EmailEvent")|extend Variant="regular"),(vimEmailEventProofpointPOD()|where EventOriginalUid !startswith "synthetic-"|invoke ASimDataTester("EmailEvent")|extend Variant="filtered")'},
        {"name": "exclusion", "query": prelude + disabled_definition + disabled_regular + disabled_all + 'print FilteredSourceRows=toscalar(DisabledSource()|count),RegularSourceRows=toscalar(DisabledRegular()|count),GlobalRows=toscalar(DisabledAll()|count)'},
        {"name": "data_negative", "query": prelude + tester_definition("ASimDataTester") + 'ASimEmailEventProofpointPOD()|where EventOriginalUid=="synthetic-base"|extend EmailToRecipients=dynamic([1])|invoke ASimDataTester("EmailEvent")|where Result startswith "(0)"|summarize Detected=count()'},
    ]
    (args.output / "queries.json").write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    runners = []
    for job in jobs:
        (args.output / (job["name"] + ".kql")).write_text(job["query"], encoding="utf-8")
        if not args.grafana_datasource_uid:
            continue
        runner = """async (page) => {
          const config = CONFIG;
          const job = JOB;
          return await page.evaluate(async ({job, config}) => {
            const started = performance.now();
            const response = await fetch('/api/ds/query', {
              method: 'POST', headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({
                queries: [{database: config.database,
                  datasource: {type: 'grafana-azure-data-explorer-datasource', uid: config.uid},
                  pluginVersion: '6.2.0', query: job.query, querySource: 'raw',
                  queryType: 'KQL', rawMode: true, refId: 'A', resultFormat: 'table',
                  intervalMs: 3600000, maxDataPoints: 1000}],
                from: '1788220800000', to: '1790812799999'
              })
            });
            const result = {job: job.name, observedUtc: new Date().toISOString(),
              durationMs: Math.round(performance.now()-started),
              httpStatus: response.status, response: await response.json()};
            globalThis.__podValidationResults = globalThis.__podValidationResults || {};
            globalThis.__podValidationResults[job.name] = result;
            const body = result.response.results?.A;
            return {job: job.name, httpStatus: result.httpStatus, durationMs: result.durationMs,
              status: body?.status, error: body?.error, message: result.response.message,
              frames: body?.frames?.map(f => ({
                fields: f.schema.fields.map(c => ({name:c.name,type:c.type})),
                values: f.data.values
              }))};
          }, {job, config});
        }"""
        runner = runner.replace("CONFIG", json.dumps({
            "database": args.grafana_database, "uid": args.grafana_datasource_uid
        }), 1).replace("JOB", json.dumps(job, ensure_ascii=True), 1)
        runners.append(runner)
        (args.output / ("run_" + job["name"] + ".js")).write_text(runner, encoding="utf-8")
    if runners:
        (args.output / "run_all.js").write_text(
            "async (page) => { const runners=[" + ",\n".join(runners)
            + "]; const results=[]; for (const run of runners) results.push(await run(page)); return results; }",
            encoding="utf-8",
        )
    sample_path = ROOT / "Sample Data" / "ASIM" / ("Proofpoint_" + PRODUCT + "_EmailEvent_IngestedLogs.csv")
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    with sample_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        for record in public:
            writer.writerow({key: json.dumps(record[key], ensure_ascii=True) if kind == "dynamic" else record[key] for key, kind in COLUMNS.items()})
    provenance = {
        "public_records": len(public), "synthetic_records": len(synthetic),
        "checks": len(checks),
        "source": "Sample Data/Custom/ProofpointPOD_message_CL.json",
        "transformation": "Current DCR ts -> eventTime projection. TimeGenerated is a synthetic eventTime + 1 hour, not a production ingestion timestamp.",
        "synthetic_purpose": "Exercise mapping decisions and boundaries, not prove which vendor outcomes occur in production.",
        "live_customer_data": False,
    }
    (args.output / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(json.dumps(provenance))


if __name__ == "__main__":
    main()
