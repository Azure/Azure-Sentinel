# Get-AlertEntitiesEnrichment

author: Sebastien Molendijk - Microsoft

This playbook allows you to enrich your alerts entities using solutions like:

- Azure Active Directory
- Azure Active Directory Identity Protection
- Microsoft Cloud App Security
- Microsoft Defender for Endpoints (MDATP)

### Additional resources

- Complete explanation and demonstration of this playbook in [this video](https://youtu.be/YZr-New3yCI).
- [Registering a service principal in Azure AD](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#register-an-application-with-azure-ad-and-create-a-service-principal)
- [Microsoft Graph permissions reference](https://docs.microsoft.com/graph/permissions-reference)
- [Create an MCAS API token](https://docs.microsoft.com/cloud-app-security/api-tokens)
- [Defender Advanced Hunting API](https://docs.microsoft.com/windows/security/threat-protection/microsoft-defender-atp/run-advanced-query-api)

<br>

## Details

The main playbook (_Get-AlertEntitiesEnrichment_) calls other playbooks, acting as functions, which return details per entity type:

- **UserEnrichment**: returns a JSON per user entiy containing the properties below:

```
{
    "accountEnabled": true,
    "adminRoles": [
        {
            "description": "Can read security information and reports, and manage configuration in Azure AD and Office 365.",
            "displayName": "Security Administrator",
            "id": "123456-b126-40b2-bd5b-6091b380977d",
            "isBuiltIn": true,
            "isEnabled": true,
            "resourceScopes": [
                "/"
            ]
        }
    ],
    "authMethodsMfa": [
        "email",
        "mobilePhone"
    ],
    "businessPhones": null,
    "city": "Pittsburgh",
    "companyName": "MyCompany",
    "country": null,
    "createdDateTime": "2019-03-09T13:11:05Z",
    "department": "Marketing",
    "devices": {
        "aadDevices": [
            {
                "Manufacturer": "Microsoft Corporation",
                "Model": "Virtual Machine",
                "accountEnabled": true,
                "approximateLastSignInDateTime": "2020-09-16T10:12:33Z",
                "complianceExpirationDateTime": null,
                "deviceId": "123456-a6ad-4050-89d5-0c17ea12be78",
                "displayName": "MEGAN-PC",
                "id": "123456-a07c-429e-ab10-c0e02255f7f9",
                "isCompliant": false,
                "isManaged": true,
                "onPremisesLastSyncDateTime": null,
                "onPremisesSyncEnabled": null,
                "operatingSystem": "Windows",
                "operatingSystemVersion": "10.0.18363.1082",
                "profileType": "RegisteredDevice",
                "trustType": "AzureAd"
            }
        ],
        "mdatpDevices": [
            {
                "DeviceName": "megan-pc",
                "DeviceId": "123456a6ad405089d50c17ea12be78",
                "IPAddressHistory": [
                    "45.131.4.20",
                    "45.132.193.33"
            }
        ]
    },
    "displayName": "Megan Bowens",
    "employeeId": null,
    "givenName": "Megan",
    "id": "123456789-40e3-9359-6c106522db19",
    "isMfaRegistered": true,
    "isSsprRegistered": true,
    "jobTitle": "Marketing Manager",
    "locationsUsage": [
        {
            "activities": "2555",
            "country": "BE",
            "lastActivity": "2020-09-25T12:45:00Z",
            "percentageTotalActivities": "78"
        },
        {
            "activities": "425",
            "country": "US",
            "lastActivity": "2020-09-25T12:25:06Z",
            "percentageTotalActivities": "22"
        }
    ],
    "mail": "MeganB@seccxp.ninja",
    "mailboxInboxRules": [
        {
            "id": "AQAAAW80H1A=",
            "displayName": ".",
            "sequence": 2,
            "isEnabled": true,
            "hasError": false,
            "isReadOnly": false,
            "conditions": {
                "bodyOrSubjectContains": [
                    "payment, tax, visa, credit,bank"
                ]
            },
            "exceptions": {
                "sentCcMe": true
            },
            "actions": {
                "stopProcessingRules": true,
                "forwardTo": [
                    {
                        "emailAddress": {
                            "name": "notme@gmail.com",
                            "address": "notme@gmail.com"
                        }
                    }
                ],
                "moveToFolder": "RSS Feeds"
            }
        }
    ],
    "mailboxOofEnabled": true,
    "mailboxOofMessage": "<div>\r\n<div></div>\r\n<div></div>\r\n<div>Dear mail sender,</div>\r\n<div><br>\r\n</div>\r\n<div>I'm currently travelling abroad wit limited access to my mailbox.</div>\r\n<div>Thank you for your understanding.</div>\r\n<div><br>\r\n</div>\r\n<div>Megan</div>\r\n</div>",
    "manager": {
        "displayName": "Julian Isla",
        "id": "123456789-8fdf-4217-865b-e084cb7214f1",
        "jobTitle": "Marketing VP",
        "mail": "JulianI@xyz.com",
        "mobilePhone": null,
        "userPrincipalName": "JulianI@xyz.com"
    },
    "mobilePhone": null,
    "officeLocation": null,
    "onPremisesDistinguishedName": "CN=MeganB,CN=Users,DC=xyz,DC=lan",
    "onPremisesDomainName": "xyz.lan",
    "onPremisesLastSyncDateTime": "2020-06-02T17:21:21Z",
    "onPremisesSamAccountName": "MeganB",
    "onPremisesSecurityIdentifier": "S-1-5-21-11111111-2311428937-3957907789-1110",
    "onPremisesSyncEnabled": true,
    "postalCode": "15212",
    "preferredLanguage": en-us,
    "refreshTokensValidFromDateTime": "2020-06-02T13:46:30Z",
    "riskLevel": "medium",
    "riskState": "atRisk",
    "riskDetail": "none",
    "riskLastUpdatedDateTime": "2020-09-25T11:04:28.2358719Z",
    "ssprActivities": [],
    "state": "PA",
    "streetAddress": "30 Isabella St., Second Floor",
    "surname": "Bowens",
    "threatScore": 152,
    "threatScoreHistory": {},
    "userPrincipalName": "MeganB@xyz.com"
}

```

<br>

## Requirements

This playbook uses an API token to obtain the user's MCAS profile and an AAD service principal, with the required permissions below, to query the relevant Microsoft Graph and Defender endpoints.

<br>

### Scope: User

| Logic App action         | API             | Endpoint                                   | AAD Required Permission    |
| ------------------------ | --------------- | ------------------------------------------ | -------------------------- |
| Get_user_details         | Microsoft Graph | /users/{user UPN}                          | User.Read.All              |
| Get_user_manager         | Microsoft Graph | /users/{user UPN}/manager                  | User.Read.All              |
| Get_user_MFA-SSPR_status | Microsoft Graph | /reports/credentialUserRegistrationDetails | Reports.Read.All           |
| Get_user_AAD_risk_status | Microsoft Graph | /riskyUsers/{user AAD object Id}           | IdentityRiskyUser.Read.All |

<br>

### Scope: Devices

| Logic App action       | API                | Endpoint                       | AAD Required Permission |
| ---------------------- | ------------------ | ------------------------------ | ----------------------- |
| Get_user_owned_devices | Microsoft Graph    | /users/{user UPN}/ownedDevices | Directory.Read.All      |
| Advanced_Hunting       | WindowsDefenderAtp | /advancedqueries/run           | AdvancedQuery.Read.All  |

<br>

### Scope: Group membership

| Logic App action       | API             | Endpoint                                  | AAD Required Permission                |
| ---------------------- | --------------- | ----------------------------------------- | -------------------------------------- |
| Check_group_membership | Microsoft Graph | /users/{user UPN}/checkMemberGroups       | User.Read.All and GroupMember.Read.All |
| Get_user_admin_roles   | Microsoft Graph | /roleManagement/directory/roleAssignments | Directory.Read.All                     |
| Get_role_details       | Microsoft Graph | /roleManagement/directory/roleAssignments | Directory.Read.All                     |

<br>

### Scope: User changes

| Logic App action                   | API             | Endpoint                            | AAD Required Permission |
| ---------------------------------- | --------------- | ----------------------------------- | ----------------------- |
| Get_user_password_reset_activities | Microsoft Graph | /reports/userCredentialUsageDetails | Reports.Read.All        |

<br>

### Scope: Mailbox

| Logic App action     | API             | Endpoint                                         | AAD Required Permission |
| -------------------- | --------------- | ------------------------------------------------ | ----------------------- |
| Get_user_inbox_rules | Microsoft Graph | /users/{user UPN}/mailFolders/inbox/messageRules | MailboxSettings.Read    |
| Get_user_OOF         | Microsoft Graph | /users/{user UPN}/getMailTips                    | Mail.Read               |

<br>

### Scope: Mcas Profile

| Logic App action          | API      | Endpoint                                  | AAD Required Permission |
| ------------------------- | -------- | ----------------------------------------- | ----------------------- |
| Get_user_locations_habits | MCAS API | /cas/api/v1/activities_locations/by_user/ |                         |
| Get_mcas_user_profile     | MCAS API | /cas/api/v1/entities/                     |                         |

<br>

## Deployment

You can use the **Deploy.ps1** script, after updating the required parameters in the provided **parameters.json** file, or use the buttons below.

<br>

**UserEnrichment:**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-AlertEntitiesEnrichment%2FUserEnrichment.template.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-AlertEntitiesEnrichment%2FUserEnrichment.template.json)

**Get-AlertEntitiesEnrichment (requires UserEnrichment to be deployed first):**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-AlertEntitiesEnrichment%2FGet-AlertEntitiesEnrichment.json_)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-AlertEntitiesEnrichment%2FGet-AlertEntitiesEnrichment.json)