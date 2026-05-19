# BitSight Risk Findings CCF Data Connector
* [Introduction](#Introduction)
* [Description](#Description)
* [Folders](#Folders)
* [Prerequisites](#Prerequisites)
* [Configuration](#Configuration)
* [Installing for the users](#Installing-for-the-users)
* [Installing for testing](#Installing-for-testing)

## Introduction<a name="Introduction"></a>

This folder contains the CCF-based ARM artifacts for the reduced BitSight Risk Findings data connector. The connector focuses on a limited set of BitSight risk vectors and ingests only normalized **WARN** and **BAD** findings into Microsoft Sentinel.

## Description<a name="Description"></a>

The BitSight Risk Findings CCF Data Connector supports targeted evidence-based cyber risk monitoring by bringing selected BitSight finding data into Microsoft Sentinel through the **Microsoft Sentinel Codeless Connector Framework (CCF)**.

This package covers the following monitoring factors:

1. Botnet Infections
2. Spam Propagation
3. Malware Servers
4. Unsolicited Communications
5. Potentially Exploited
6. TLS/SSL Certificates
7. Patching Cadence
8. Mobile Software
9. Open Ports
10. File Sharing

The initial implementation ingests only **WARN** and **BAD** findings. **FAIR** findings can be added later by updating the DCR transform and, if needed, the sample queries.

## Folders<a name="Folders"></a>

1. `bitsight-risk-findings-connection-template.json` - Connection template that creates the custom table, DCE, DCR, and ten `RestApiPoller` connections for one BitSight company.
2. `bitsight-risk-findings-connector-definition.json` - Microsoft Sentinel connector definition template used to expose the BitSight Risk Findings connector in the Data Connectors gallery.
3. `bitsight-risk-findings-connection-template.parameters.json` - Sample parameters for the connection template.
4. `bitsight-risk-findings-connector-definition.parameters.json` - Sample parameters for the connector definition template.
5. `BitsightRiskFindings.kql` - Sample KQL queries for validation and operational monitoring.
6. `README.md` - Deployment and configuration guidance.
7. `ReleaseNotes.md` - Package change history.

## Prerequisites<a name="Prerequisites"></a>

1. A valid BitSight API Token is required.
2. A Microsoft Sentinel workspace is required.
3. The monitored BitSight company GUID must be known in advance.
4. The Template Spec for the connection template must be published before deploying the connector definition template.

## Configuration<a name="Configuration"></a>

### STEP 1 - BitSight API Token

Obtain a valid BitSight API token from the BitSight portal. The connector uses the BitSight token in an Authorization header equivalent to BitSight Basic authentication.

### STEP 2 - Publish the connection template as a Template Spec

Publish `bitsight-risk-findings-connection-template.json` as an Azure Template Spec. Example values:

- Template Spec Name: `bitsight-risk-findings-connection-template`
- Template Spec Version: `1.0.0`

### STEP 3 - Deploy the connector definition template

Deploy `bitsight-risk-findings-connector-definition.json` into the same resource group as the Log Analytics workspace. Recommended values:

- Workspace Name: your Log Analytics workspace name
- Template Spec Name: `bitsight-risk-findings-connection-template`
- Template Spec Version: `1.0.0`
- Publisher: `Obrela`
- Connector Definition Name: `bitsight-risk-findings-ccf`

### STEP 4 - Connect one BitSight company

Open the BitSight Risk Findings connector in Microsoft Sentinel and provide:

- BitSight API token
- BitSight company GUID
- BitSight company display name

Each **Connect** action deploys one monitored company and creates ten `RestApiPoller` connections, one per monitored BitSight risk vector.

## Installing for the users<a name="Installing-for-the-users"></a>

After the connector definition is deployed, the connector appears in the Microsoft Sentinel **Data connectors** gallery.

i. Go to **Microsoft Sentinel -> Data Connectors**

ii. Open **BitSight Risk Findings (via Codeless Connector Framework)**

iii. Enter the BitSight API token, company GUID, and company display name.

iv. Click **Connect**

The connection template will deploy:

- `BitsightRiskFindings_CL`
- `bitsight-risk-findings-dce`
- `bitsight-risk-findings-dcr`
- ten `RestApiPoller` data connectors for the selected BitSight risk vectors

To monitor an additional company, repeat the **Connect** action with a different company GUID and display name.

## Installing for testing<a name="Installing-for-testing"></a>

1. Publish the connection template as a Template Spec.
2. Deploy the connector definition template with the sample parameter file and adjust values as needed.
3. Open the BitSight connector page in Sentinel and run **Connect** for a test company.
4. Validate ingestion with the sample KQL file.

Example quick checks:

```kusto
BitsightRiskFindings_CL | take 10
```

```kusto
BitsightRiskFindings_CL
| summarize arg_max(TimeGenerated, *) by finding_uid
| where normalized_risk_state in ("warn", "bad")
| count
```

## Notes

- This reduced package is designed for **explicit company GUID input**. It does not perform runtime portfolio discovery.
- The package is intentionally limited to the ten agreed monitoring factors and **WARN/BAD** findings only.
- If **FAIR** findings are needed later, update the DCR transform filter and the related documentation.

This version configures CCF paging to follow the BitSight `links.next` value returned in findings responses.

This version configures BitSight findings paging with `$.links.next` and the `offset` query parameter, which matches the CCF NextPageUrl runtime requirements for this API pattern.

This version uses BitSight findings pagination through the documented `limit` and `offset` query parameters, implemented in CCF with `pagingType: Offset`.
