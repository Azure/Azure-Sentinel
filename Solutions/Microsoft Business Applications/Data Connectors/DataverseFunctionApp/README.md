# Dataverse Security Data Collector

This legacy Azure Function App collects Dataverse security and inventory entities
into the `DataverseUsers_CL`, `DataverseRoles_CL`,
`DataverseUserRoleCollections_CL`, `DataverseBusinessUnits_CL`,
`DataverseTeams_CL`, `DataverseTeamRoleCollections_CL`, and
`DataverseTeamMembers_CL` tables. It is separate from the CCF Dataverse activity
connector, which writes to `DataverseActivity`.

## Pagination fix

Collector version 1.1.1 uses `requests.Session` instead of HTTPX for Dataverse
requests. It follows each `@odata.nextLink` without parsing or rebuilding its
encoded `$skiptoken`, including when an intermediate page has no records.
Request failures propagate so an incomplete traversal is not treated as a
successful collection.

The existing deployment template references the published Function App ZIP
through `https://aka.ms/sentinel-dataverse-functionapp-v2`. The ZIP retains the
`dataversefunction110.zip` filename so that deployment reference does not change.
Updating repository source alone does not update an already deployed Function
App. This pagination fix does not upgrade the Python runtime or establish a
customer recovery.

## Offline regression tests

From this directory, with `requests` installed, run:

```powershell
python -B -m unittest discover -s tests -v
```

To run the same suite with the Requests dependency shipped in the deployment ZIP:

```powershell
python -B -c "import sys, unittest; sys.path.insert(0, r'dataversefunction110.zip\.python_packages\lib\site-packages'); unittest.main(module=None, argv=['unittest', 'discover', '-s', 'tests', '-v'])"
```

The tests exercise real Requests URL preparation while mocking only transport.
They cover nested encoded continuation URLs, multiple pages, empty pages,
authorization and timeout propagation, and later-page HTTP and timeout failures.
They also check that the source and dependency manifest in the deployment ZIP
match the checked-in files.

No Azure credentials or customer environment are used. These tests do not
replace a live Dataverse multi-page collection and ingestion check.
