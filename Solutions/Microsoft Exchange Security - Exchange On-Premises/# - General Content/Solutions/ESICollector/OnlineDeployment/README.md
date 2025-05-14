# ExchSecIns

## Permissions

    Exchange Organization Management for the scheduled account that collect information

## Access

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

## Script details

**.Synopsis**
    This script generates a csv file of the Exchange Configuration for Exchange Security Insight project.
**.DESCRIPTION**
    This script has to be scheduled to generate a CSV file of the Exchange configuration that will be imported into Sentinel by ALA Agent.
    Multiple Exchange Cmdlets are used to extract information.

**.EXAMPLE**
**.INPUTS**
    .\CollectExchSecIns.ps1
        
**.OUTPUTS**
    The output a csv file of collected data or uploading on Azure Log Analytics
**.NOTES**
    Developed by ksangui@microsoft.com and Nicolas Lepagnez
    
    Version : 7.6.0.1 - Released : 26/07/2024 - nilepagn
        - Adding Try-Catch on Get-AutomationVariable Test
        - Correct a bug on Get-LastVersion with Write-LogMessage
        - 
    Version : 7.6.0.0 - Released : 02/04/2024 - nilepagn
        - Adding possibility of storing USD logs in a storage instead of displaying them in the console
        - Adding a level of logs to display in the console
        - Adding a security when a Guid is given as TenantName to force column as String instead of Guid (PublicContent #9)

    Version : 7.5.2.2 - Released : 05/11/2023 - nilepagn
        - Correct a bug when Parallelisation is disabled and a PerServer function is called.

    Version : 7.5.2.1 - Released : 24/09/2023 - nilepagn
        - Implement an IdentityString for ESIEnvironment Section to be sure that the ESIExchangeConfig table is correctly created in Sentinel

    Version : 7.5.2 - Released : 17/08/2023 - nilepagn
        - Implement a minimal config version
        - Correct multiple bugs on regex configuration filteging and categorization
        - Enhancement of the Audit function loop by adding protection on malformed data
        - Possibiltiy to launch the Collector for Microsoft Online from a server instead of a Runbook
        - Adding a "ResetType" on the DateStorageInformation Section to be able to start on a specific date if needed. Possible values : 
            "CurrentDate" : Start from current date
            "LastDateOfScript" : Start from last date stored in the file for the script
            "Standard" : "Apply the same rule as the script : Current date minus "DefaultDurationTracking" parameter in days
            "SpecificDate[YourDate]" : Start from a specific date specified in the parameter "YourDate"
            "Current-AddUnit[YourNumber]" : Start from current date plus/minus a number of unit (replace unit by Days, months, Years, hours, minutes, seconds as desired) specified in the parameter "YourNumber"
        - In the very little case where 'Get-AutomationVariable' is an existing function outside Azure Automation, we check the precense of a module Orchestrator*. We now offer the possibility to force execution outside Azure Automation by passing the switch IsOutsideAzureAutomation for script execution.

    Version : 7.5.1.1 - Released : 12/07/2023 - nilepagn
        - Correct a bug IdentityString information.

    Version : 7.5.1 - Released : 12/07/2023 - nilepagn
        - Correct a bug on cache search for Get-Member.
        - Adding variable IdentityString in returned results to standardize between on-premises and online
        - Adding DN of Groups to collect
        - Introduction of Pagination System
            New parameters available for a section :
                "PaginationInformation":{
                    "PaginationActivated":"true",
                    "PageSize":5000,
                    "MaxPage":1,
                    "PartialDataUpload":"true",
                    "StorePagesInMemory":"true"
                }
        - Introduction of Date stored by Section
            "DateStorageInformation":{
				"DateStorageActivated":"true",
				"DateAttribute":"date",
				"DateStorageMode":"LastDate", => Possible values : LastDate, StartDateScript, DateFromAttribute (Attribute name in DateAttribute)
				"DateReset":"true"
			}
        - Introduction of partial saving during execution in Microsoft Sentinel (Via parameter "PartialDataUpload" in PaginationInformation)
            => Data are uploaded in Microsoft Sentinel each time a page is completed.
        - Introduce a new category OnlineMessageTracking allowing you to collect information about Message Tracking in Exchange Online on Microsoft Sentinel


    Version : 7.5.0 - Released : 05/02/2023 - nilepagn
        - Correct a bug excluding tests with Processing Type "Online" on a Runbook execution.
        - Limit size of Members of a group to 25Kb when saved inline with the Group information. Entire member list can be retrieved using the memberpath.

    Version : 7.4.2 - Released : 28/12/2022 - nilepagn
        - Implementation of ManagedIdentity for Exchange Online instead of RunAs Account using the new PS Module 3.0.0 of ExchangeOnline

    Version : 7.4.1 - Released : 28/12/2022 - nilepagn
        - Adding logs for Azure Upload
        - Enhancements on Group and user cache
        - Allow to force specific functions to be excluded from parallelism.

    Version : 7.4 - Released : NOT RELEASED - nilepagn
        - Complete Get-Group when Get-ADGroupMember not available
        - Get-ESIADGroupMember for external usage that can use Get-ADGroupMember or Get-ADGroup
        - Avoid Loop in GetInfo with members of groups.
        - Add a Group cache to avoid to many retreival

    Version : 7.3.2 - Released : 09/12/2022 - nilepagn
        - Correct a bug when Without Internet and using Folder Add-ons
        - Parametize the Max packet size sent to Sentinel
        - 
    Version : 7.3.1 - Released : 28/11/2022 - nilepagn
        - Adding Version information for Script, used by updater to update script
        - Correct a bug when Configuration cannot be loaded during Azure Automation execution
        - Failover when Get-ADGroupMember doesn't work by using (Get-ADGroup).Members
        - Possibility to use a Proxy for Invoke Web Requests (Proxy without authentication)

    Version : 7.3 - Released : 03/11/2022 - nilepagn
        - Adding TLS1.2 capability
        - Adding a Beta mode for Add-Ons download from public repository
        - Adding a segmentation less than 32Mb for Sentinel Upload.
        - Adding property ProcessedByServer in each result processed by a specific server.

    Version : 7.2 - Released : 18/10/2022 - nilepagn
        - Adding a system of capabilities for Instances. 
            Implemented capabilities: OL = ExchangeOnline, OP = Exchange On-Premises, ADINFOS = Forest/Domain information, MGGRAPH = Graph API PS Module, IIS = IIS Module
        - Creation of a ConfigCoherence Script calculating checksum of all files
        - Implementing more complex setup file that creates the task and multiple instances
        - Completing the instance capability by implementing a Category system
            => First category created : IIS IoC that use IIS Capability to find string in files.
        Finalizing the implementation of Checksum in AuditFunctions. LF end-of-file technique needs to be used due to Github content storage    
    

    Version : 7.1 - Released : 06/10/2022 - nilepagn
        - ESI Collector retrieve Online configuration by default.
        - ESI Collector verify Checksum of files and download Online version in case of bad validation (Issue known invalidating cache each time)
        - Multiple Instance capability added in beginning version 7.1
        - Internal GetO365Info implemented for retreiving Group Membership like AD
            => MGGraph module is needed. Permission for Microsoft Graph needed : "group.read.all","user.read.all", "AuditLog.Read.All"

    Version : 7.0 - Released : 03/10/2022 - nilepagn
        - Protect ESI-Collector executing "destructive" cmdlets by controlling the Cmdlets in AuditFunctions for forbidden verbs
        - Split Audit Functions into a system of add-on files more evolutive to be able to quicky add a new file with new functions.
        - Prepare the ability to retrieve Add-On files from Internet
        - Prepare the ability to check a checksum of AuditFunctions.

    Version : 6.5 - Released : 27/09/2022 - nilepagn
        - Correction of bug on retrieving Exchange Servers
        - Adding ESIEnvironment Information to correlate Configuration with logs in Sentinel

    Version : 6.4 - Released : 22/09/2022 - nilepagn
        - Filtering EDGE Servers that can't be analyzed
        - Correcting a bug on Custom Select Fields
        - Adding possibility to generate information for a specific Sentinel API Table. Add '//' in OutputStream of the function. Like "myfile.csv//SpecificSentinelTable"

    Version : 6.3 - Released : 19/09/2022 - nilepagn
        - Correct bug on AD Requests on a multi-domain environment
        - Add the processing of the JobStatus type "Error" during transformation
        - Changes how Errors from jobs are displayed in logs : Display as warning to doesn't throw error
        - Add a correct error processing when user domain doesn't have the homeMBD attribute
        - Modify the end of script to correctly ends the logging

    Version : 6.2.2 - Released : 12/09/2022 - Ksangui
        -Add Get-inboundConnecot and Get OutboungConnector for Online

    Version : 6.2.1 - Released : 10/09/2022 - nilepagn
        - Possibility to display TargetServer on Select (It was a regression from 4.x version)

    Version : 6.2 - Released : ? - nilepagn
        - Possibility to use Log Analytics API and CSV in same time.

    Version : 6.1.1 - Released : 24/08/2022 - nilepagn
        - Correcting bug on multithreading.
        - Version published on On-Premises testing environment and validated.

    Version : 6.1 - Released : 24/08/2022 - nilepagn
        - Adding ESIEnvironment column in entries adding the possibility to audit multiple On-Premises and Online Exchange configuration

    Version : 6.0.1 - Released : 24/08/2022 - nilepagn
        - Bug on Write-LogMessage during function loading.
        
    Version : 6.0 - Released : 24/08/2022 - nilepagn
        - Merge of On-Premises version and Cloud Version of ESI Collector
        - Deactivate the possibility to launch multi-threading in Azure Automation
        - Add "ESIProcessingType":"Online" in Global Section of JSON File. The value can be "Online" or "On-Premises"
        - Add "ProcessingCategory":"All" for Audit Functions. The value can be "All", "Online" or "On-Premises"
        - Reorganization of functions in the code by category

    Version : 5.0 - Released : 24/08/2022 - nilepagn
        - Version Cloud with autonomous Azure Log Monitor loading. No more dependant of a script.
        - Be able to work on an Azure Automation Runbook
        - Connect Exchange Online to retrieve Information

    Version : 4.2 - Released : 15/08/2022 - Nilepagn
        - Adding an automous Sentinel log upload mechanism to be able to be independant from Log Analytics Agents.
            The Upload-AzMonitorLog Script is needed and can be installed here : https://www.powershellgallery.com/packages/Upload-AzMonitorLog
            The system needs to be explicitally enabled in the config file with the Sentinel Workspace Id and Workspace

    Version : 4.1 - Released : 15/08/2022 - Nilepagn
        - Testing Function transfert into JSON File
        - Adding possibility to activate only specific function of to deactivate a specific function
            => "Deactivated":"false" on function level
            => "OnlyExplicitActivation":"True" on "Advanced" level + "ExplicitActivation":"true" on function level
        - Adding Default Exchange Path on JSON Config
        - Transforming all the parallelism system to use Runspace on multi-threading
        - Adding the possibility to explicitally fill Exchange Server list to use
        - Insert multiple variables that can be used on functions : 
            "#LastDateTracking#" = $script:LastDateTracking; 
            "#ForestDN#" = $script:ForestDN; 
            "#ForestName#" = $script:ForestName; 
            "#ExchOrgName#" = $script:ExchOrgName; 
            "#GCRoot#" = $script:GCRoot;
            "#GCServer#" = $script:gc;
            "#SIDRoot#" = $script:sidroot;

    Version : 4.0 - Released : 02/08/2022 - Nilepagn
        - Transfering Configuration of functions in the JSON File [NOT TESTED]
    Version : 3.0 - Released : 27/03/2022 - Nilepagn
        - Refactorization for parallelism in function execution.
        - Possibility to redirect result on another file
        - Possibility to use a date of last execution.
        - Configuration file creation for variables
    Version : 2.8 - Released : 24/06/2022
        - Add Exch CU/SU
    Version : 2.7 - Released : 24/03/2022
        - Add Search-MailboxAuditlog
        - Add DatabaseAvailabilityGroup
    Version : 2.6 - Released : 17/03/2022
        - Add ReceiveConnector : AuthMecnismstring and Permissions Group string
        - ExchangeServer : AdminDisplayVersion
        -Transport Rule SentoString,CopytoString,RedirecttoString,BlindCopyToString
    Version : 2.5 - Released : 17/03/2022
        - Add Logon and Last PwdSet as String for ADGroup
        - Correct bug on ParentGroup
    Version : 2.4 - Released : 16/03/2022
        - Bug on Local Administrators group with Domain user
        - Add Service Status of POP and IMAP
    Version : 2.3 - Released : 10/03/2022
        - Add Select Expression on few attributes where String is needed. Like User, Rights
    Version : 2.2 - Released : 24/02/2022
        - Adding Business Logic to process Management Role direct assignments
    Version : 2.1 - Released : 11/02/2022
        - Adding Business Logic to process WMI User/Group Information
        - Correct a bug on Transform for each object switch
        - Align Member object properties to have same information
    Version : 2.0 - Released : 11/02/2022
        - Adding Tranformation Function possibility before injecting data
        - Adding Group Hierarchy Calculation
    Version : 1.3 - Released : 04/01/2021
        - Adding Exchange Server information
        - Adding Mailbox Database Information
        - Correct Bug on Section Name where Space at the end was present
    Version : 1.2 - Released : 31/12/2021
        - Modify header of the file to add script information.
        - Adding Logs generation
        - Adding a Cleaning function for log and data csv file
        - Adding CSV file with date
        - Introduce a Configuration Instance ID and a Generation Date in CSV

    Version : 1.1 - Released : 10/12/2021
        - Generates only 1 CSV file with standard column for all cmdlets
