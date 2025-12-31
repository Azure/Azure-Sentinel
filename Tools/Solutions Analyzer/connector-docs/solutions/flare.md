# Flare

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Flare |
| **Support Tier** | Partner |
| **Support Link** | [https://flare.io/company/contact/](https://flare.io/company/contact/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Flare](../connectors/flare.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Firework_CL`](../tables/firework-cl.md) | [Flare](../connectors/flare.md) | Analytics, Workbooks |

## Content Items

This solution includes **11 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 9 |
| Workbooks | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Flare Cloud bucket result](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlareCloudBucket.yaml) | Medium | Reconnaissance | [`Firework_CL`](../tables/firework-cl.md) |
| [Flare Darkweb result](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlareDarkweb.yaml) | Medium | Reconnaissance | [`Firework_CL`](../tables/firework-cl.md) |
| [Flare Google Dork result found](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlareDork.yaml) | Medium | Reconnaissance | [`Firework_CL`](../tables/firework-cl.md) |
| [Flare Host result](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlareHost.yaml) | Medium | Reconnaissance | [`Firework_CL`](../tables/firework-cl.md) |
| [Flare Infected Device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlareInfectedDevice.yaml) | Medium | CredentialAccess | [`Firework_CL`](../tables/firework-cl.md) |
| [Flare Leaked Credentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlareCredentialLeaks.yaml) | Medium | CredentialAccess | [`Firework_CL`](../tables/firework-cl.md) |
| [Flare Paste result](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlarePaste.yaml) | Medium | Reconnaissance | [`Firework_CL`](../tables/firework-cl.md) |
| [Flare SSL Certificate result](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlareSSLcert.yaml) | Medium | ResourceDevelopment | [`Firework_CL`](../tables/firework-cl.md) |
| [Flare Source Code found](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Analytic%20Rules/FlareSourceCode.yaml) | Medium | Reconnaissance | [`Firework_CL`](../tables/firework-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [FlareSystemsFireworkOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Workbooks/FlareSystemsFireworkOverview.json) | [`Firework_CL`](../tables/firework-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [credential-warning](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Playbooks/credential-warning/azuredeploy.json) | This playbook monitors all data received from Firework looking for leaked credentials (email:passwor... | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
