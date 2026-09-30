**AI Governance Reference Data
**This folder contains public sample/reference data used by the AI Governance community workbook.

**Files
**`ai_domains.csv`
A best-effort catalogue of commonly used AI providers, products, domains, service classifications, and optional process metadata. The workbook uses this file to enrich Microsoft Defender telemetry and identify recognised AI services.
The catalogue is reference data only. It is not a customer policy source and does not indicate that a service is approved, blocked, licensed, deployed, or currently in use.

**Purpose
**A workbook loads this file with KQL `externaldata()` from the public raw GitHub URL. It provides a shared baseline that customers can optionally extend or override with local data, such as a Microsoft Sentinel watchlist.
The public catalogue intentionally sets `Sanctioned` to `FALSE` for every row. Approval/sanctioning is customer-specific and should be defined locally or selected in the workbook.

**Schema
**| Column | Type | Description |
|---|---|---|
| `Provider` | `string` | Organisation providing the AI service. |
| `Product` | `string` | Product or service name. |
| `Domain` | `string` | Hostname/domain used as an observation indicator. Blank is allowed for process-only entries. Values should not include `https://`, URL paths, or wildcard characters. |
| `Category` | `string` | Broad delivery/interface category such as `Web`, `API`, `Developer`, `Desktop`, `Image`, `Video`, or `Audio`. |
| `Sanctioned` | `bool` | Public sample value. Always `FALSE`; customer policy should be defined locally. |
| `RiskType` | `string` | Functional/service classification used by the workbook, for example `Chat`, `API`, `Developer`, `Document`, `Image`, `Video`, or `Audio`. Despite the historical column name, this is not a risk severity rating. |
| `SourceURL` | `string` | Public vendor or product documentation used as a reference for the entry. |
| `ProcessName` | `string` | Optional executable/process name used for endpoint process matching. |
| `ProcessProductName` | `string` | Optional product-name metadata used to strengthen process matching. |
| `ProcessPublisher` | `string` | Optional publisher/company metadata used to strengthen process matching. |
`RiskType` terminology
`RiskType` is retained for workbook schema compatibility. Values such as `Chat` describe the type of AI service or interaction, not whether the service is high, medium, or low risk.
A future schema revision may rename this field to something clearer such as `ServiceType` or `UsageType`. Until then, consumers should not interpret `RiskType` as a security risk score.

**Matching guidance
**Domain values are indicators, not exhaustive vendor allowlists.
Vendors can use multiple hostnames, CDNs, regional endpoints, APIs, and supporting services.
A network connection to a listed domain indicates observed communication with that service; it does not prove what data was submitted or how the service was used.
Process metadata is best-effort and may vary by operating system, packaging method, application version, or endpoint telemetry.
Where a product cannot be represented reliably by a hostname, `Domain` may be blank and process metadata can be used instead.

**Data owner
**AI Governance community workbook maintainers.
Changes should be reviewed through the normal pull-request process for the repository.

**Sources and licence
**The catalogue is curated from publicly available vendor/product information. Where practical, each row includes an official vendor or documentation URL in `SourceURL` to support review and future maintenance.
This sample data is intended to be distributed under the same licence as the parent repository unless the repository specifies otherwise. Product names and trademarks remain the property of their respective owners.
Update cadence
Expected review cadence: monthly, with out-of-cycle updates when material product, domain, or process changes are identified.
Because AI services change quickly, consumers should treat the catalogue as best-effort reference data rather than a complete or authoritative vendor endpoint list.

**Data handling
**This file must contain public reference data only. Do not add:
customer names or tenant identifiers;
user, device, or other telemetry-derived data;
credentials, API keys, tokens, or secrets;
personal data;
confidential or otherwise sensitive information.
Customer-specific additions, policy decisions, and sanctioned/approved service states should be stored locally, for example in a customer-owned Microsoft Sentinel watchlist.
Notable maintenance notes
`Sanctioned` is deliberately `FALSE` for all public rows.
`Microsoft Foundry` is used as the current product name for the service previously known as Azure AI Foundry.
GitHub Copilot entries represent useful domain indicators; GitHub publishes a broader and changing network allowlist, so these rows are not intended to replace that documentation.
OpenAI Codex is represented as a developer service without a URL-path value in `Domain`; URL paths should not be stored in the domain field.
`ChatGPT Classic` and `Claude Code` are process-oriented entries and therefore have a blank `Domain`.
