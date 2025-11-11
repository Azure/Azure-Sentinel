# Exchange Security Insights Collectors

**Synopsis**
    This script generates a photography of the Exchange Configuration for Microsoft Exchange Security solution for Microsoft Sentinel.
**DESCRIPTION**
    This script has to be scheduled once a day at minimum to generate a snapshot of the Exchange configuration that will be imported into Microsoft Sentinel by using Log Analytics APIs.

    Multiple Exchange Cmdlets and Active-Directory/Microsoft Graph cmdlets are used to extract information that will be used by Microsoft Exchange Security for Microsoft Sentinel to create a secure posture in your Exchange On-Premises/Online environment.

    Parameters are described in the Configuration file. Explanation of the parameters is available in the [the Parameters description document](./Parameters.md)

## On-Premises Collector

### Mandatory Permissions

The account used to launch the script has to be Organization Management.

  > The collector has to read Active-Directory groups and members, especially "Administrative" groups in 'Microsoft Exchange Security Groups' Organization Units.

  > The collector must be able to contact every Exchange Server in WMI and in Remote PowerShell.

(Normally the Organization Management group allow the above rights excepted if you have brake inheritance in AD or made custom **unsupported** hardening between Exchange Servers.)

USD Logs (Summary of logs of the Collector) :

  > If the USD Logs storage is AzureStorageAccount, the ManagedIdentity or the created Entra ID Application needs to have the Storage Blob Data Contributor role at minimum to be able to write logs in the storage account.

### Network Access

    **Internet**
    
        Direct Access to the following URLs or by using a proxy
        If a proxy is used, configuration has to be done in .\Config\CollectExchSecConfiguration.json file
        Attention, Explicit Authentication is not supported.

        URLs :
            https://*.ods.opinsights.azure.com
            https://raw.githubusercontent.com

    **Exchange Servers**
        
        The script needs accessing to all Exchange Servers using Remote PowerShell and WMI

    **Active Directory**

        The script needs accessing to Domain Controllers using the Active-Directory Management Shell

## Online Collector

### Mandatory Permissions

Permissions are added to the Managed Identity of the Automation accounts that you create at the installation. A script was created to help you assigning permissions for Microsoft Graph and Exchange Online API.

Microsoft Graph Permissions :

  > The collector needs Groups.Read permission to be able to retrieve groups that have rights in Exchange Online for audit.

  > The collector needs Users.Read permission to be able to retrieve members of group information

  > The collector needs Auditing.Read permission to be able to retrieve the last Sign-in date in the infrastructure for permission audit


Exchange Online permissions :

  > The collector has to have Exchange.ManageAsApp permission to be able to connect to Exchange. [learn more](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2?view=exchange-ps)

  > The collector must be **Global Reader** or **Security Reader** at minimum to be able to read Exchange Online configuration. This permission has to assigned manually after Managed account creation. [learn more on available roles for ManageAsApp permission](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2?view=exchange-ps#assign-microsoft-entra-roles-to-the-application)

USD Logs (Summary of logs of the Collector) :

  > If the USD Logs storage is AzureStorageAccount, the ManagedIdentity or the created Entra ID Application needs to have the Storage Blob Data Contributor role at minimum to be able to write logs in the storage account.
