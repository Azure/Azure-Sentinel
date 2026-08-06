"""Dummy-data test mirroring vimAuditEventFivetranAuditTrail KQL mapping.

Python reimplementation of the parser's normalisation + dedupe logic, run over
sample Fivetran_AuditTrail_CL rows to assert ASIM AuditEvent conformance before a
live ASimSchemaTester/ASimDataTester run. Mirrors the pattern of the ASIM-vNext
test/test_parsers.py harness. Run: python test_audittrail_parser.py
"""

MANDATORY = [
    "EventCount", "EventStartTime", "EventEndTime", "EventType", "EventResult",
    "EventProduct", "EventVendor", "EventSchema", "EventSchemaVersion", "Dvc",
    "Operation", "Object",
]
ALLOWED_EVENTTYPE = {
    "Set", "Read", "Create", "Delete", "Execute", "Install", "Clear",
    "Enable", "Disable", "Initialize", "Start", "Stop", "Other",
}


def _event_type(action: str) -> str:
    a = action.lower()
    if any(k in a for k in ("create", "add", "insert")):
        return "Create"
    if any(k in a for k in ("delete", "remove", "drop")):
        return "Delete"
    if any(k in a for k in ("pause", "disable")):
        return "Disable"
    if any(k in a for k in ("resume", "enable")):
        return "Enable"
    if any(k in a for k in ("edit", "update", "alter", "change", "modify", "set")):
        return "Set"
    if any(k in a for k in ("read", "view", "access", "get")):
        return "Read"
    return "Other"


def _object_type(prim_type: str) -> str:
    p = prim_type.lower()
    if any(k in p for k in ("connector", "connection", "destination")):
        return "Cloud Resource"
    if any(k in p for k in ("user", "team", "role", "account", "membership")):
        return "Directory Service Object"
    return "Other"


def normalise(rows):
    # Dedupe by id keeping latest TimeGenerated (mirrors arg_max(TimeGenerated,*) by id).
    latest = {}
    for r in rows:
        cur = latest.get(r["id"])
        if cur is None or r["TimeGenerated"] > cur["TimeGenerated"]:
            latest[r["id"]] = r
    out = []
    for r in latest.values():
        out.append({
            "EventCount": 1,
            "EventStartTime": r["captured_at"],
            "EventEndTime": r["captured_at"],
            "Operation": r["action"],
            "EventType": _event_type(r["action"]),
            "EventResult": "Success",
            "EventProduct": "Fivetran Platform",
            "EventVendor": "Fivetran",
            "EventSchema": "AuditEvent",
            "EventSchemaVersion": "0.1.2",
            "Dvc": "Fivetran",
            "Object": r["primary_resource_id"] or r["primary_resource_type"] or "Unknown",
            "ObjectType": _object_type(r["primary_resource_type"]),
            "ActorUserId": r["user_id"],
            "ActorUsername": r["user_id"] or "Unknown",
            "OldValue": r["old_values"],
            "NewValue": r["new_values"],
            "EventOriginalUid": r["id"],
        })
    return out


SAMPLE = [
    {"id": "a1", "TimeGenerated": "2026-07-20T01:00:00Z", "captured_at": "2026-07-20T01:00:00Z",
     "user_id": "u_100", "action": "CREATE_CONNECTION", "interaction_method": "api",
     "primary_resource_type": "connection", "primary_resource_id": "c_55",
     "secondary_resource_type": "", "secondary_resource_id": "", "old_values": "{}", "new_values": '{"name":"pg"}'},
    {"id": "a2", "TimeGenerated": "2026-07-20T02:00:00Z", "captured_at": "2026-07-20T02:00:00Z",
     "user_id": "u_101", "action": "DELETE_DESTINATION", "interaction_method": "ui",
     "primary_resource_type": "destination", "primary_resource_id": "d_9",
     "secondary_resource_type": "", "secondary_resource_id": "", "old_values": '{"x":1}', "new_values": "{}"},
    {"id": "a3", "TimeGenerated": "2026-07-20T03:00:00Z", "captured_at": "2026-07-20T03:00:00Z",
     "user_id": "u_102", "action": "EDIT_ROLE_PERMISSION", "interaction_method": "api",
     "primary_resource_type": "role", "primary_resource_id": "r_3",
     "secondary_resource_type": "connector_type", "secondary_resource_id": "postgres",
     "old_values": '{"perm":"read"}', "new_values": '{"perm":"admin"}'},
    # Duplicate of a1 from a compaction rewrite, later TimeGenerated -> must dedupe to one.
    {"id": "a1", "TimeGenerated": "2026-07-21T05:00:00Z", "captured_at": "2026-07-20T01:00:00Z",
     "user_id": "u_100", "action": "CREATE_CONNECTION", "interaction_method": "api",
     "primary_resource_type": "connection", "primary_resource_id": "c_55",
     "secondary_resource_type": "", "secondary_resource_id": "", "old_values": "{}", "new_values": '{"name":"pg"}'},
]


def main():
    checks = 0
    result = normalise(SAMPLE)

    assert len(result) == 3, f"dedupe failed: expected 3 unique ids, got {len(result)}"
    checks += 1

    by_id = {r["EventOriginalUid"]: r for r in result}
    assert by_id["a1"]["EventType"] == "Create"
    checks += 1
    assert by_id["a2"]["EventType"] == "Delete"
    checks += 1
    assert by_id["a3"]["EventType"] == "Set"
    checks += 1
    assert by_id["a1"]["ObjectType"] == "Cloud Resource"
    checks += 1
    assert by_id["a3"]["ObjectType"] == "Directory Service Object"
    checks += 1
    assert by_id["a3"]["NewValue"] == '{"perm":"admin"}'
    checks += 1
    assert by_id["a2"]["ActorUserId"] == "u_101"
    checks += 1

    for r in result:
        for f in MANDATORY:
            assert f in r and r[f] not in (None, ""), f"missing mandatory {f}"
        assert r["EventResult"] == "Success"
        assert r["EventType"] in ALLOWED_EVENTTYPE, r["EventType"]
    checks += 1

    print(f"OK - {checks} check groups passed over {len(result)} normalised rows")


if __name__ == "__main__":
    main()
