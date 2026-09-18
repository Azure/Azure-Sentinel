# QCrypton PQC Scanner — Function App Test Evidence

## Function App Exception / Approval

| Item | Status | Notes |
|------|--------|-------|
| Function App exception request | TODO | Provide exception ID or approval reference if the solution uses a Function App that requires an exception from the standard Sentinel connector pattern. |
| Partner approval | TODO | Confirm partner (QCrypton, Inc.) has been approved for Function App usage in the Sentinel marketplace. |

## Deployment Test Results

| Test | Result | Evidence |
|------|--------|----------|
| ARM template validation (arm-ttk) | TODO | Run `Test-AzTemplate` against `SaaS/deploy/azuredeploy.json` and paste output or screenshot. |
| Function App deployment | TODO | Deploy to a test resource group and confirm the Function App starts successfully. Add screenshot to `images/functionapp-deploy-success.png`. |
| Application settings configured | TODO | Confirm all required app settings (`MARKETPLACE_CLIENT_ID`, `MARKETPLACE_CLIENT_SECRET`, `API_KEY_VAULT_URL`) are populated. |

## Invocation Test Results

| Test | Result | Evidence |
|------|--------|----------|
| Landing page renders | TODO | Navigate to the Function App landing-page URL and confirm the SaaS activation page loads. Add screenshot to `images/landing-page.png`. |
| Webhook handler responds | TODO | Send a test webhook payload and confirm a 200 response. Paste `curl` output or screenshot. |
| Marketplace API key provisioning | TODO | Confirm that a successful SaaS subscription results in an API key being stored in Key Vault. |

## Ingestion Test Results

| Test | Result | Evidence |
|------|--------|----------|
| Data connector configured | TODO | Enable the QCryptonPQCScanner CCP connector in a Sentinel workspace with a valid API key. |
| PQReadiness_CL table populated | TODO | Run `PQReadiness_CL | take 10` in Log Analytics and confirm rows appear. Add screenshot to `images/ingestion-results.png`. |
| Analytic rules fire on test data | TODO | Confirm at least one analytic rule generates an incident from ingested test findings. |
| Workbook renders | TODO | Open the PQ Readiness workbook and confirm charts populate with ingested data. Add screenshot to `images/workbook-render.png`. |

---

> **Note:** Replace each `TODO` with `PASS` / `FAIL` and attach evidence (screenshots in `images/` or inline text). Include this evidence in the pull request description when submitting.
