## Overview
The Microsoft Sentinel: Insider Risk Management Solution demonstrates the “better together” story between Microsoft Purview Insider Risk Management and Microsoft Sentinel. The solution includes (1) Workbook, (5) Hunting Queries, (5) Analytics Rules, and (1) Playbook. Insider risk management helps minimize internal risks by enabling you to detect, investigate, and act on malicious and inadvertent activities in your organization. Insider risk policies allow you to define the types of risks to identify and detect in your organization, including acting on cases and act on cases including the ability to escalate cases to Microsoft Advanced eDiscovery. Risk analysts in your organization can quickly take appropriate actions to make sure users are compliant with your organization's compliance standards. Insider risks come in various forms including both witting (intentional) and unwitting (unintentional).This workbook provides an automated visualization of Insider risk behavior cross walked to Microsoft security offerings. This solution is enhanced when integrated with complimentary Microsoft Offerings such as💡 [Microsoft Purview Insider Risk Management](https://docs.microsoft.com/microsoft-365/compliance/insider-risk-management-solution-overview), 💡 [Communications Compliance](https://docs.microsoft.com/microsoft-365/compliance/communication-compliance-solution-overview), 💡 [Microsoft Information Protection](https://docs.microsoft.com/microsoft-365/compliance/information-protection), 💡 [Advanced eDiscovery](https://docs.microsoft.com/microsoft-365/compliance/ediscovery), and 💡 [Microsoft Sentinel Notebooks](https://docs.microsoft.com/azure/sentinel/notebooks). This workbook enables Insider Risk Teams, SecOps Analysts, and MSSPs to gain situational awareness for insider risk management, UEBA, device indicators, physical access, and HR signals. This workbook is designed to augment staffing through automation, artificial intelligence, machine learning, query/alerting generation, and visualizations. For more information, see 💡 [Microsoft Purview Insider Risk Management](https://docs.microsoft.com/microsoft-365/compliance/insider-risk-management-solution-overview).

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoftPurviewInsiderRiskManagement%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoftPurviewInsiderRiskManagement%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/Images/InsiderRiskManagementBlack1.png?raw=true)

## Getting Started
1️⃣ [Onboard Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)<br>
2️⃣ [Onboard Microsoft Purview Insider Risk Management](https://docs.microsoft.com/microsoft-365/compliance/insider-risk-management-configure)<br>
3️⃣ [Enable the Insider Risk Management Connector](https://docs.microsoft.com/azure/sentinel/data-connectors-reference#microsoft-365-insider-risk-management-irm-preview)<br>
4️⃣ [Enable User Entity Behavior Analytics](https://docs.microsoft.com/azure/sentinel/enable-entity-behavior-analytics)<br> 
5️⃣ [Configure Watchlist via SearchKey Columns](https://docs.microsoft.com/azure/sentinel/watchlists)<br> 

## [Recommended Microsoft Sentinel Roles](https://docs.microsoft.com/azure/sentinel/roles) / [Recommended Microsoft Defender for Cloud Roles](https://docs.microsoft.com/azure/defender-for-cloud/permissions#roles-and-allowed-actions)
| <strong> Roles </strong> | <strong> Rights </strong> | 
|:--|:--|
|Security Reader | View Workbooks, Analytics, Hunting, Security Recommendations |
|Security Contributor| Deploy/Modify Workbooks, Analytics, Hunting Queries, Apply Security Recommendations |
|Automation Contributor| Deploy/Modify Playbooks & Automation Rules |

## Recommended Enrichments
This workbook leverages numerous 1st/3rd Party, Cloud, and Multi-Cloud offerings. While only Microsoft Sentinel is mandatory for this solution, the following offerings provide enrichments:<br>

✳️ [Microsoft Purview Insider Risk Management](https://docs.microsoft.com/microsoft-365/compliance/insider-risk-management-solution-overview)<br>
✳️ [Microsoft Purview Communications Compliance](https://docs.microsoft.com/microsoft-365/compliance/communication-compliance-solution-overview)<br>
✳️ [Microsoft Purview Information Protection](https://docs.microsoft.com/microsoft-365/compliance/information-protection)<br>
✳️ [Microsoft Purview eDiscovery](https://docs.microsoft.com/microsoft-365/compliance/ediscovery)<br>
✳️ [Microsoft Sentinel Notebooks](https://docs.microsoft.com/azure/sentinel/notebooks)<br>
✳️ [Microsoft Defender for Endpoint](https://www.microsoft.com/microsoft-365/security/endpoint-defender)<br>
✳️ [Microsoft Defender for Identity](https://www.microsoft.com/microsoft-365/security/identity-defender)<br>
✳️ [Microsoft Defender for Cloud Apps](https://www.microsoft.com/microsoft-365/enterprise-mobility-security/cloud-app-security)<br>
✳️ [Microsoft 365 Defender](https://www.microsoft.com/microsoft-365/security/microsoft-365-defender) <br>
✳️ [Microsoft Defender for Office 365](https://www.microsoft.com/microsoft-365/security/office-365-defender)<br>
✳️ [Microsoft Entra ID](https://azure.microsoft.com/services/active-directory/)<br>

## Workbook
The Microsoft Insider Risk Management Workbook integrates telemetry from 25+ Microsoft security products to provide actionable insights into insider risk management. Reporting tools provide “Go to Alert” links to provide deeper integration between products and a simplified user experience for exploring alerts. A filter set provides custom reporting for Guide, Subscription, Workspace, and Time. The workbook can be exported as a PDF or print report via the Print Workbooks feature. Content sections include Overviews, Insider Risk Management, Watchlist, and User Forensics. The Overview tab provides recommendations for building insider risk program architectures. The Insider Risk tab provides alert reporting by both insider risk scenarios such as Sensitive Data Leaks, Security Violations, and MITRE ATT&CK® tactics. The Watchlist tab provides filtering by Microsoft Sentinel Watchlists and the User Forensics tab collects logging telemetry by user. The user experience includes designing insider risk management architectures and streamlining telemetry from all users > watchlist > specific users while transitioning to Microsoft Purview Insider Risk Management to investigate/resolve activity of interest.

## Print/Export Report
1️⃣ Set Background Theme: Settings > Appearance > Theme: Azure > Apply<br>
2️⃣ Print/Export Report: More Content Actions (...) > Print Content<br>
3️⃣ Settings: Layout (Landscape), Pages (All), Print (One Sided), Scale (60), Pages Per Sheet (1), Quality (1,200 DPI), Margins (None) > Print<br>

## Analytics Rules
### 1) Insider Risk_High User Security Alert Correlations
This alert joins SecurityAlerts from Microsoft Products with SecurityIncidents from Microsoft Sentinel and Microsoft Purview Defender. This join allows for identifying patterns in user principal names associated with respective security alerts. A machine learning function (Basket) is leveraged with a .001 threshold. Basket finds all frequent patterns of discrete attributes (dimensions) in the data. It returns the frequent patterns passed the frequency threshold. This query evaluates UserPrincipalName for patterns in SecurityAlerts and Reporting Security Tools. This query can be further tuned/configured for higher confidence percentages, security products, or alert severities pending the needs of the organization. There is an option for configuration of correlations against Microsoft Sentinel watchlists. For more information on the basket plugin, see [basket plugin](https://docs.microsoft.com/azure/data-explorer/kusto/query/basketplugin).<br>
### 2) Insider Risk_High User Security Incidents Correlations
This alert joins SecurityAlerts to SecurityIncidents to associate Security Alerts and Incidents with user accounts. This aligns all Microsoft Alerting Products with Microsoft Incident Generating Products (Microsoft Sentinel, Microsoft 365 Defender) for a count of user security incidents over time. The default threshold is 5 security incidents, and this is customizable per the organization's requirements. Results include UserPrincipalName (UPN), SecurityIncident, LastIncident, ProductName, LastObservedTime, and Previous Incidents. There is an option for configuration of correlations against Microsoft Sentinel watchlists. For more information, see [Investigate incidents with Microsoft Sentinel]( https://docs.microsoft.com/azure/sentinel/investigate-cases).<br>
### 3) Insider Risk_Microsoft Purview Insider Risk Management Alert Observed
This alert is triggered when a Microsoft Purview Insider Risk Management alert is received in Microsoft Sentinel via the Microsoft Purview Insider Risk Management Connector. The alert extracts usernames from security alerts to provide UserPrincipalName, Alert Name, Reporting Product Name, Status, Alert Link, Previous Alerts Links, Time Generated. There is an option for configuration of correlations against Microsoft Sentinel watchlists. For more information, see [Learn about insider risk management in Microsoft 365](https://docs.microsoft.com/microsoft-365/compliance/insider-risk-management).<br>
### 4) Insider Risk_Sensitive Data Access Outside Organizational Geo-location
This alert joins Azure Information Protection Logs (InformationProtectionLogs_CL) with Microsoft Entra ID Sign in Logs (SigninLogs) to provide a correlation of sensitive data access by geo-location. Results include User Principal Name, Label Name, Activity, City, State, Country/Region, and Time Generated. Recommended configuration is to include (or exclude) Sign in geo-locations (City, State, Country and/or Region) for trusted organizational locations. There is an option for configuration of correlations against Microsoft Sentinel watchlists. Accessing sensitive data from a new or unauthorized geo-location warrants further review. For more information see [Sign-in logs in Microsoft Entra ID: Location Filtering](https://docs.microsoft.com/azure/active-directory/reports-monitoring/concept-sign-ins).<br>
### 5) Insider Risk_Risky User Access By Application
This alert evaluates Microsoft Entra ID Sign in risk via Machine Learning correlations in the basket operator. The basket threshold is adjustable, and the default is set to .01. There is an optional configuration to configure the percentage rates. The correlations are designed to leverage machine learning to identify patterns of risky user application access. There is an option for configuration of correlations against Microsoft Sentinel watchlists. For more information, see [Tutorial: Use risk detections for user sign-ins to trigger Azure AD Multi-Factor Authentication or password changes](https://docs.microsoft.com/azure/active-directory/authentication/tutorial-risk-based-sspr-mfa).<br>

## Hunting Queries
### 1) Insider Risk_Entity Anomaly Followed by IRM Alert
This query joins Microsoft Sentinel UEBA with Microsoft Purview Insider Risk Management Alerts. There is also an option for configuration of correlations against watchlists. For more information, see https://docs.microsoft.com/azure/sentinel/watchlists.<br>
### 2) Insider Risk_Internet Service Provider Anomaly followed by Data Exfiltration
This query joins UEBA to Security Alerts from Microsoft products for a correlation of Internet Service Provider anomalies to data exfiltration (watchlist options). For more information, see https://docs.microsoft.com/azure/sentinel/watchlists.<br>
### 3) Insider Risk_Multiple Entity-Based Anomalies
This query returns entity counts by anomaly and user principal name including ranges for start/end time observed (watchlists configurable). For more information, see https://docs.microsoft.com/azure/sentinel/watchlists.<br>
### 4) Insider Risk_Possible Sabotage
This query correlates users with entity anomalies, security alerts, and delete/remove actions for identification of possible sabotage activities (watchlists configurable). For more information, see https://docs.microsoft.com/azure/sentinel/watchlists.<br>
### 5) Insider Risk_Sign In Risk Followed By Sensitive Data Access
This query correlates a risky user sign ins with access to sensitive data classified by data loss prevention capabilities (watchlist configurable). For more information, see https://docs.microsoft.com/azure/sentinel/watchlists.<br>

## Playbook
This solution includes the Notify-Insider Risk Management Team playbook. Playbooks are a Security Orchestration, Automation, & Response (SOAR) capability to automate manual tasks. This playbook should be configured as an automation action with the Insider Risk Management Analytics Rules. Upon triggering an Analytic Rule, this playbook captures respective details and both emails and posts a message in a Teams chat to the Insider Risk Management team. This automation increases response times while reducing the need to return to the workbook for monitoring. 