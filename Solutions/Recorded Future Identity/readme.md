
<img src="./Playbooks/images/logo.png" alt="RecordedFuture logo" width="50%"/>

Link to [Recorded Future main readme](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/readme.md)
# Recorded Future Identity Solution 

Recorded Future Identity Intelligence enables security and IT teams to detect identity compromises. 

Recorded Future automates the collection, analysis, and production of identity intelligence from a vast range of sources. 

You can incorporate identity intelligence into automated workflows that regularly monitor for compromised credentials and take immediate action using Recorded Future Identity data and Microsoft Entra ID.

There are many ways organizations can utilize Recorded Future Identity Intelligence. The Azure Logic Apps in this Solution provided as examples and are a quick introduction to some of those ways. 

These playbooks include several actions that can be coordinated, or used separately. 

They include:

1. Searches for compromised workforce or external customer users
1. Looking up existing users and saving the compromised user data to a Log file
1. Confirming high risk Microsoft Entra ID (EntraID) users
1. Adding a compromised user to an EntraID security group

[Installation guide](Playbooks/readme.md)


These playbooks and actions are designed to meet the following use cases:

1. **My Organization ("Workforce" use case)** 

Organizations seeking to proactively protect their own employees from account takeovers and prevent outside third parties from using employee credentials to gain access to sensitive company information can use the Identity Intelligence module in two ways:
- on a periodic basis, query Recorded Future identity intelligence (via "Credential Search" Action) for any "new" employee credentials that may have been exposed.
- when suspicious employee behavior is noticed (e.g. logins from uncommon geographic locations, or large downloads of information during non business hours), query Recorded Future identity intelligence (via "Credential Lookup" Action) to check if that user has had credentials exposed in prior dumps or malware logs.

Possible remediation include password resets, user privilege revocation, and user quarantining.  Advanced teams may also choose to flag users suspected of takeover by a threat actor to track usage through their system.

 
2. **Customer ("External" use case)**

Organizations that provide their customers with online services via a web-based login can use the Identity Intelligence module to assess whether their customers are at risk of fraudulent use by a third party.  Suggested work flows include:
- on a periodic basis, query Recorded Future identity intelligence (via "Credential Search" Action) for any compromised credentials that may have been exposed. 
- during account creation, use the Identity Intelligence module (via "Credential Lookup" Action) to check whether the username and/or username/password pair are previously compromised.
- during account login, check the Identity Intelligence module (via "Credential Lookup" Action) for whether the username/password pair is compromised.

Possible remediation include requiring a password reset, or temporarily locking down the account and requesting the user contact customer service for a user re-authentication process.


 [Installation guide](Playbooks/readme.md)
