# MicrosoftPurviewInsiderRiskManagement

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft 365 Insider Risk Management](../connectors/officeirm.md)

**Publisher:** Microsoft

Microsoft 365 Insider Risk Management is a compliance solution in Microsoft 365 that helps minimize internal risks by enabling you to detect, investigate, and act on malicious and inadvertent activities in your organization. Risk analysts in your organization can quickly take appropriate actions to make sure users are compliant with your organization's compliance standards.



Insider risk policies allow you to:



-   define the types of risks you want to identify and detect in your organization.

-   decide on what actions to take in response, including escalating cases to Microsoft Advanced eDiscovery if needed.



This solution produces alerts that can be seen by Office customers in the Insider Risk Management solution in Microsoft 365 Compliance Center.

[Learn More](https://aka.ms/OfficeIRMConnector) about Insider Risk Management.



These alerts can be imported into Microsoft Sentinel with this connector, allowing you to see, investigate, and respond to them in a broader organizational threat context. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223721&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [template_OfficeIRM.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Data%20Connectors/template_OfficeIRM.JSON) |

[→ View full connector details](../connectors/officeirm.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityAlert` | [Microsoft 365 Insider Risk Management](../connectors/officeirm.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.6       | 07-04-2025                     | Updated ConnectivityCriteria Type in **Data Connector**.				   |
| 3.0.5       | 10-04-2024                     | Updated Entity Mappings InsiderRiskyAccessByApplication.yaml             |
| 3.0.4       | 07-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID. |
| 3.0.3       | 10-10-2023                     | Updated **Workbook** template to replace the datatype InformationProtectionLogs_CL to MicrosoftPurviewInformationProtection                                                                                     |
| 3.0.2       | 04-10-2023                     | Updated **Workbook** template to fix Signinlogs datatype                 |
| 3.0.1       | 20-09-2023                     | Updated **Workbook** template to fix the invaild json issue              |
| 3.0.0       | 17-07-2023                     | Updating **Analytic Rules** with grouping configuration(Single Alert)    |
|             |                                |                                                                          |

[← Back to Solutions Index](../solutions-index.md)
