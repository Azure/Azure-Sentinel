# IsMalicious: enrich incident IP entities

This community Logic Apps playbook enriches up to `MaxIPsPerIncident` IP entities
per Sentinel incident (default 10, configurable from 1 to 50) using the
IsMalicious `/check` API and writes an incident comment.
The comment contains server verdict, risk score, separate confidence, blocklist
hits, evidence reasons, contradictions, freshness, observed time, review flags
and a report URL. It performs no containment or automatic blocking.

This complements Sentinel's built-in TAXII ingestion. It does not install a
second feed connector or constitute a certified Content Hub solution.

## Prerequisites and deployment

- Microsoft Sentinel workspace and permission to deploy Logic Apps/API connections.
- IsMalicious account with API access/quota: [API documentation](https://ismalicious.com/api-docs).
- Complete `X-API-KEY` credential, Base64 of `apiKey:apiSecret`. The raw API key
  alone is insufficient. Treat the encoded credential as a secret.

Deploy `azuredeploy.json` as a custom ARM template in the desired resource group.
The workflow uses the `Microsoft.Logic/workflows` resource API `2019-05-01`;
its workflow definition schema remains `2016-06-01`.
`IsMaliciousCredential` is a secure-string deployment/workflow parameter.
Set `MaxIPsPerIncident` between 1 and 50, based on your account quota.
The workflow is **Disabled by default** so it cannot issue requests before setup.

After deployment:

1. Assign the playbook's system-assigned managed identity permission to read
   incident entities and add incident comments (Microsoft Sentinel Responder
   on the workspace, subject to your RBAC policy). The Sentinel API connection
   uses managed identity authentication, matching the repository's
   [incident-trigger template](../.template/incident-trigger/azuredeploy.json).
2. Grant the Microsoft Sentinel service account the Microsoft Sentinel Automation
   Contributor role on the playbook resource group and associate the playbook
   with an incident automation rule. Follow
   [Sentinel playbook permissions](https://learn.microsoft.com/azure/sentinel/automation/automate-responses-with-playbooks#extra-permissions-required-for-microsoft-sentinel-to-run-playbooks).
3. Verify the trigger/connection in the designer, enable the workflow and run it
   on a test incident before enabling the automation rule.
4. Restrict rule scope and the IP cap before production use. Each IP uses one
   API lookup; only the first configured number of entities is checked. The
   incident comment states this cap rather than implying complete coverage.

## Failure and interpretation

Lookups run sequentially with no automatic retry. The action declares a
30-second WDL/asynchronous-action limit. This is not a verified 30-second
HTTP socket deadline; Azure's HTTP connector/platform timeout also applies.
This avoids a burst of requests or repeated charges after rate limiting.
A failed HTTP request, timeout, non-JSON body or malformed response adds an
explicit unknown/error row. The failure row reads the action status and optional
HTTP status code safely even when the HTTP action has no outputs. Finalization
runs after successful, failed, timed-out or skipped loops, and the comment
identifies entity/loop statuses so a partial lookup is not presented as complete.
Authentication errors (401/403), quota/rate limits (429) and transient server
failures must be corrected and retried deliberately.

`evidence.verdict` comes from the server. Missing optional scores remain empty,
not zero. Risk and confidence are separate columns. Context source rows are
not counted as detections. Full reasons and contradictions remain visible;
`malicious: false` is not converted into a safe verdict.

The HTTP action hides its inputs/outputs in run history to protect credentials.
Only selected non-credential response fields enter the incident comment.
No API key, response headers or full upstream error bodies are written there.

## Validation

`python -m unittest discover -s tests -v` runs local structural/security tests.
These validate the template and failure paths; they do not replace an Azure
ARM deployment and Sentinel incident test. A live Azure deployment, connection
authorization and incident run remain required before this playbook is used in
production. No live Sentinel execution is claimed by this submission.

### Deployment and test-incident acceptance checks

Run these checks in an existing non-production Sentinel workspace, using an
isolated test incident and an IsMalicious credential with sufficient quota.
Follow [Run playbooks manually](https://learn.microsoft.com/azure/sentinel/automation/run-playbooks)
to select the incident and invoke the playbook after deployment and permission
setup. Do not activate a production automation rule during validation.

| Check | Expected result and evidence to retain |
| --- | --- |
| ARM deployment | Both the API connection and workflow deploy successfully. Record the deployment name, provisioning status and template commit. The workflow initially stays Disabled. |
| Identity and connection | Confirm the SystemAssigned identity, the workspace role assignment and a healthy Sentinel API connection before enabling the test workflow. |
| Single-IP incident | The run retrieves the incident IP, completes the lookup and writes one incident comment with verdict, separate risk/confidence, evidence and a report URL. Record the incident ID, run ID and redacted comment. |
| IP cap | On an incident with more IP entities than `MaxIPsPerIncident`, only the configured number is looked up. The comment states the cap. |
| No IP entities | The run issues no IsMalicious lookup and finishes with an empty results table. |
| Authentication failure | Use an invalid credential only in the isolated test deployment. The incident comment reports an unknown/error row rather than a safe verdict. Restore the valid credential afterward. |
| Credential safety | Verify that `Check_IP` inputs and outputs are hidden in run history and that neither the comment nor exported evidence contains the credential. |

Record actual results alongside these expectations. Redact credentials and
customer data before sharing evidence. ARM/schema checks alone do not satisfy
the live deployment and incident-run requirements.
