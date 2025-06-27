
<img src="./Playbooks/images/logo.png" alt="RecordedFuture logo" width="50%"/>

Link to [Recorded Future main readme](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/readme.md)
# Recorded Future Identity Solution

Recorded Future Identity Intelligence enables security and IT teams to detect identity compromises.

Recorded Future automates the collection, analysis, and production of identity intelligence from a vast range of sources.

You can incorporate identity intelligence into automated workflows that regularly monitor for compromised credentials and take immediate action using Recorded Future Identity data and Microsoft Entra ID.

There are many ways organizations can utilize Recorded Future Identity Intelligence. The Azure Logic Apps in this Solution provided as examples and are a quick introduction to some of those ways.

These playbooks include several actions that can be coordinated, or used separately.

They include:

1. Ingest novel identity exposures for specified domains
1. Adding a compromised user to an Entra ID security group
1. Confirming high risk Microsoft Entra ID users
1. Looking up existing users and saving the compromised user data to a Log file

[Installation guide](Playbooks/readme.md)



### **Identity exposure ingestion**

The **recommended** playbook workflow relies on Recorded Future Playbook Alerts, where organizations configure domains to monitor for Novel Identity exposures, which can be automatically ingested and acted upon.

This playbook workflow focuses on the following actions:
- Ingesting Novel Identity Exposures
- Verifies that users exist in Entra ID
- Place the compromised users in a security group
- If possible, confirm user as risky within Entra ID
- (Optional) - Save detailed identity exposure information to Log Analytics Workspace (LAW)
- (Optional) - Create a Microsoft Sentinel incident for triage and further investigation
- Update corresponding Recorded Future Playbook Alert with remediation

Other possible remediations include password resets, user privilege revocation, and user quarantining. Advanced teams may also choose to flag users suspected of takeover by a threat actor to track usage through their system.

### Identity lookup
An alternative workflow exists, that in some cases might fit organizational needs to a higher degree.

These playbooks and actions are designed to meet the following use cases:

1. **My Organization ("Workforce" use case)**

- when suspicious employee behavior is noticed (e.g. logins from uncommon geographic locations, or large downloads of information during non business hours), query Recorded Future identity intelligence (via "Credential Lookup" Action) to check if that user has had credentials exposed in prior dumps or malware logs.

Possible remediation include password resets, user privilege revocation, and user quarantining.  Advanced teams may also choose to flag users suspected of takeover by a threat actor to track usage through their system.


2. **Customer ("External" use case)**

Organizations that provide their customers with online services via a web-based login can use the Identity Intelligence module to assess whether their customers are at risk of fraudulent use by a third party.  Suggested work flows include:
- during account creation, use the Identity Intelligence module (via "Credential Lookup" Action) to check whether the username and/or username/password pair are previously compromised.
- during account login, check the Identity Intelligence module (via "Credential Lookup" Action) for whether the username/password pair is compromised.

Possible remediation include requiring a password reset, or temporarily locking down the account and requesting the user contact customer service for a user re-authentication process.


 [Installation guide](Playbooks/readme.md)
