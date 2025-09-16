<#
Disclaimer:
This sample script is not supported under any Microsoft standard support program or service.
The sample script is provided AS IS without warranty of any kind. Microsoft further disclaims
all implied warranties including, without limitation, any implied warranties of merchantability
or of fitness for a particular purpose. The entire risk arising out of the use or performance of
the sample scripts and documentation remains with you. In no event shall Microsoft, its authors,
or anyone else involved in the creation, production, or delivery of the scripts be liable for any
damages whatsoever (including, without limitation, damages for loss of business profits, business
interruption, loss of business information, or other pecuniary loss) arising out of the use of or
inability to use the sample scripts or documentation, even if Microsoft has been advised of the
possibility of such damages
#>
<#
.Synopsis
    This script generates a csv file of the Exchange Configuration for Exchange Security Insight project.
.DESCRIPTION
    This script has to be scheduled to generate a CSV file of the Exchange configuration that will be imported into Sentinel by ALA Agent.
    Multiple Exchange Cmdlets are used to extract information.

.EXAMPLE
.INPUTS
    .\CollectExchSecIns.ps1
        
.OUTPUTS
    The output a csv file of collected data
.NOTES
    Developed by ksangui@microsoft.com and Nicolas Lepagnez (nilepagn@microsoft.com)

    Version : 7.6.0.1 - Released : 26/07/2024 - nilepagn
        - Adding Try-Catch on Get-AutomationVariable Test
        - Correct a bug on Get-LastVersion with Write-LogMessage

    Version : 7.6.0.0 - Released : 02/04/2024 - nilepagn
        - Adding possibility of storing USD logs in a storage instead of displaying them in the console
        - Adding a level of logs to display in the console
        - Adding a security when a Guid is given as TenantName to force column as String instead of Guid (PublicContent #9)
        - Correct a bug on downloading Beta Add-ons from Runbooks
        - Update how to calculate IsRunbook variable
        - Update Add-Ons Update system to operate in UTF8 no BOM without NewLine at the end of file

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

    ** For Previous version history, see Github page **
    
#>

Param (
    [String] $JSONFileCondiguration = ".\Config\CollectExchSecConfiguration.json",
    [System.Int32] $ClearFilesOlderThan = 7,
    [switch] $ForceOutputWithoutDate,
    [Parameter(Mandatory=$false,HelpMessage="Specify if a PowerhShell session is connected to an Exchange 2010")]
    $EPS2010=$false,
    [switch] $NoDateTracing, 
    [string] $InstanceName = "Default",
    [switch] $GetVersion,
    [string] $ReceivedTenantName,
    [switch] $IsOutsideAzureAutomation
)

$ESICollectorCurrentVersion = "7.6.0.1"
if ($GetVersion) {return $ESICollectorCurrentVersion}

$Script:SupportedConfigurationVersion = "2.4"

#region CapabilitiesManagement

    function Connect-ESIExchangeOnline
    {
        Param (
            $TenantName
        )

        $TempVerbosePreference = $VerbosePreference
        $VerbosePreference = "SilentlyContinue"

        if ($Global:isRunbook)
        {
            Connect-ExchangeOnline -ManagedIdentity -ShowBanner:$false -Organization $TenantName -Verbose:$false
        }
        else {
            Connect-ExchangeOnline -Verbose:$false
        }

        $VerbosePreference = $TempVerbosePreference

    }
        
    Function Get-ExchangeServerList
    {
        Param(
            $EPS2010,
            [switch] $Parallel,
            $ServerList = $null,
            [switch] $BypassTest
        )

        if ($BypassTest) {$Parallel = $false}

        if ($null -eq $ServerList)
        {
            $servers= get-exchangeserver | Where-Object {$_.serverrole -ne "EDGE"}
        }
        else 
        {
            Write-Host "Server list restricted to list in config file"
            $servers = @()
            foreach ($targetServer in $ServerList)
            {
                $servers += Get-ExchangeServer -Identity $targetServer
            }
        }

        #Check and Count theservers for each version
        $ExchangeServerConfig = [PSCustomObject]@{
                    ListSRVUp = @();
                    ListSRVDown = @();
                    exch2010 = @();
                    exch2013 = @();
                    exch2016 = @();
                    exch2019 = @();
                    $EPS2010 = $EPS2010
                }
        
        $servers = $servers | Sort-Object Name
        $JobList = @()

        foreach ($srv in $servers)
        {
            if (-not $BypassTest)
            {
                if (-not $Parallel) 
                {
                    Write-Host "Test server $srv"
                    $srvstatus = Test-Connection -ComputerName $srv -Protocol wsman -Quiet
                    if ($srvstatus)
                    {
                        $ExchangeServerConfig.ListSRVUp += $srv.name
                    }
                    else {
                        $ExchangeServerConfig.ListSRVDown += $srv.name
                    }
                }
                else
                {
                    $StartAnalysis = Get-Date
                    $countRunning = Get-Job -Name "TestConn*" | Where-Object {$_.State -eq "Running"}
                    while ($countRunning.Count -ge $script:MaxParallel)
                    {
                        if (((Get-Date) - $StartAnalysis).Minute -gt $Script:ParallelTimeout) 
                        {
                            $Timeout = $true; 
                            $countRunning | Stop-Job
                            break;
                        }
                        Write-Host "$($countRunning.count) jobs running, max $($script:MaxParallel) - Wait $($Script:ParralelPingWaitRunning) Seconds"
                        Start-Sleep -Seconds $Script:ParralelPingWaitRunning  
                        $countRunning = Get-Job -Name "TestConn*" | Where-Object {$_.State -eq "Running"}
                    }
                    
                    Write-Host "Test server $srv as job"
                    $JobList += Start-Job -ScriptBlock {$srvstatus = Test-Connection -ComputerName $args[0] -Protocol wsman -Quiet; return $srvstatus} -ArgumentList $srv -Name "TestConn$($srv.name)"
                }
            }
            else 
            { 
                Write-Host "Server availability check bypassed. Adding $($srv.name) as available"
                $ExchangeServerConfig.ListSRVUp += $srv.name 
            }

            If ($srv.AdminDisplayVersion -like "*14.*")
            {
                $ExchangeServerConfig.exch2010 += $srv.name
            }
            elseif ($srv.AdminDisplayVersion -like "*15.0*")
            {
                $ExchangeServerConfig.exch2013 += $srv.name
            }
            elseif ($srv.AdminDisplayVersion -like "*15.1*")
            {
                $ExchangeServerConfig.exch2016 += $srv.name
            }
            elseif ($srv.AdminDisplayVersion -like "*15.2*")
            {
                $ExchangeServerConfig.exch2019 += $srv.name
            }
        }

        if ($Parallel)
        {
            $DoneList = @()
            $NoJob = $false
            $StartAnalysis = Get-Date
            $Timeout = $false
            $runningJobs = $JobList.count

            Write-Host "Process Test Server Jobs"
            while ($runningJobs -gt 0 -and -not $Timeout)
            {
                if (((Get-Date) - $StartAnalysis).Minute -gt $Script:ParallelTimeout) {$Timeout = $true}
                $runningJobs = 0
                foreach ($job in $JobList)
                {
                    if ($job.Name -notin $DoneList)
                    {
                        $status = Get-Job $job.Id
                        $SrvName = $job.Name -replace 'TestConn',""

                        if ($status.State -eq "Running") 
                        {
                            if (-not $Timeout) { $runningJobs += 1 }
                            else {
                                Write-Host "Process $SrvName failed job due to Timeout"
                                $ExchangeServerConfig.ListSRVDown += $SrvName
                                $DoneList += $job.Name
                                Remove-Job $job
                            }
                        }
                        else
                        {
                            Write-Host "Process $SrvName completed job"
                            $Result = Receive-Job $job
                            if ($Result)
                            {
                                $ExchangeServerConfig.ListSRVUp += $SrvName
                            }
                            else {
                                $ExchangeServerConfig.ListSRVDown += $SrvName
                            }
                            $DoneList += $job.Name
                            Remove-Job $job
                        }
                    }
                }
                if ($runningJobs -gt 0)
                {
                    Write-Host "$runningJobs Test Server availability jobs running. Wait $($Script:ParralelPingWaitRunning) seconds"
                    Start-Sleep -Seconds $Script:ParralelPingWaitRunning
                }
            }
        }

        Write-Host "List of current servers that respond to ping" $ExchangeServerConfig.ListSRVUp -ForegroundColor magenta
        Write-Host "List of current servers that are unavailable" $ExchangeServerConfig.ListSRVDown -ForegroundColor red

        #Check if the parameter EPS2010 has set to true when launching the script or there is no Exchange server other than Exchange 2010. Some tasks will be adapt depending of powershell version
        If (($ExchangeServerConfig.exch2013+$ExchangeServerConfig.exch2016+$ExchangeServerConfig.exch2019) -eq 0  -or $EPS2010 -eq $true  )
        {
            $ExchangeServerConfig.EPS2010 = $true
        }
        return $ExchangeServerConfig
    }

    Function Get-ADInfo
    {
        #Check if the Active Directory module is install if not remote session to a DC

        #Retrieve AD info
        $forest = [System.DirectoryServices.ActiveDirectory.Forest]::GetCurrentForest()
        $forest_context = [System.DirectoryServices.ActiveDirectory.DirectoryContext]::new("forest",$forest)
        $gc= $forest.NamingRoleOwner.name
        $config = ([ADSI]"LDAP://RootDSE").configurationNamingContext.Value

        #for each of the domains get the netbios name and locate the closest DC
        $forest.Domains.Name | ForEach-Object `
        {
            $domain_name = $_
            $domain_context = [System.DirectoryServices.ActiveDirectory.DirectoryContext]::new("domain",$domain_name)
            $domain_dc_fqdn = ([System.DirectoryServices.ActiveDirectory.DomainController]::findOne($domain_context)).Name

            #Only the config partition has the netbios name of the domain
            $config = ([ADSI]"LDAP://RootDSE").configurationNamingContext.Value
            $config_search = [System.DirectoryServices.DirectorySearcher]::new("LDAP://CN=Partitions,$config","(&(dnsRoot=$domain_name)(systemFlags=3))","nETBIOSName",1)
            $domain_netbios = $($config_search.FindOne().Properties.netbiosname)
            $script:ht_domains[$domain_netbios] = @{
                    DCFQDN = $domain_dc_fqdn
                    DomainFQDN = $domain_name
                    #JustAdd
                    DomainDN = (Get-ADDomain $domain_context.name).DistinguishedName
                }
        }
        $installmodule = Get-Module -ListAvailable | select-string  "ActiveDirectory"
        if ($installmodule -notlike "*ActiveDirectory*")
        {
            $adsession = new-pssession -computername $gc
            Import-pssession -session $adsession -module ActiveDirectory
        }
        $forestDN =($forest.Schema| ForEach-Object {$_ -replace ("CN=Schema,CN=Configuration,","")})
        $SIDRoot=(Get-ADDomain $forestDN -Server $forest.RootDomain).domainSID.value
        Return $forest, $forestDN, $gc, $SIDRoot
    }

    function Set-ExchangeCapability
    {
        Write-LogMessage -Message ("Connect to Exchange with Type $($Script:ESIProcessingType) ...")
        try {
            Get-OrganizationConfig | Out-Null
        }
        catch
        {
            if ($Script:ESIProcessingType -like "Online")
            {
                Write-LogMessage -Message "Connect to Exchange Online"
                Connect-ESIExchangeOnline -TenantName $Script:TenantName

                $StartingCode = {
                    try {
                        Get-OrganizationConfig | Out-Null
                    }
                    catch
                    {
                        Connect-ESIExchangeOnline -TenantName $Script:TenantName
                    }
                }
        
                Set-ParallelStartingCode -InputStartingCode $StartingCode
            }
            else {
                . "$($Script:DefaultExchangeServerBinPath)\RemoteExchange.ps1";
                Connect-ExchangeServer -auto;

                $StartingCode = {
                    try {
                        Get-OrganizationConfig | Out-Null
                    }
                    catch
                    {
                        Connect-ExchangeServer -auto;
                    }
        
                    Set-ADServerSettings -ViewEntireForest $true
                }
        
                Set-ParallelStartingCode -InputStartingCode $StartingCode

                $script:ExchangeServerList = Get-ExchangeServerList -EPS2010 $EPS2010 -Parallel:$Script:ParallelProcessPerServer -ServerList $Script:ExplicitExchangeServerList -BypassTest:$script:BypassServerAvailabilityTest
            }
        }
    }

    function Set-MgGraphCapability
    {
        Write-LogMessage -Message ("Connect to MG Powershell Module with Type $($Script:ESIProcessingType) ...")
        Write-LogMessage -Message "Connect to Azure RM"

        if (-not $Global:AlreadyAzConnected)
        {
            # Ensures you do not inherit an AzContext in your runbook
            Disable-AzContextAutosave -Scope Process
            
            if ($isRunbook)
            {
                # Connect to Azure with system-assigned managed identity
                $AzureContext = (Connect-AzAccount -Identity).context
            }
            else {
                if ($Global:Interactive)
                {
                    Write-LogMessage -Message "Az Connect with Interactive Logon"
                    $AzureContext = (Connect-AzAccount).context
                }
                else {
                    Write-LogMessage -Message "Az Connect with Interactive Logon"
                    $AzureContext = (Connect-AzAccount -CertificateThumbprint $Script:MGGraphAzureRMCertificate -Tenant $Script:TenantName -ApplicationId $Script:MGGraphAzureRMAppId).context
                }
            }
            $Global:AlreadyAzConnected = $true
        }
        else {$AzureContext = Get-AzContext}

        #$AzureContext = Set-AzContext -SubscriptionName $AzureContext.Subscription -DefaultProfile $AzureContext
        $context = [Microsoft.Azure.Commands.Common.Authentication.Abstractions.AzureRmProfileProvider]::Instance.Profile.DefaultContext

        $ModuleGraphToken = [Microsoft.Azure.Commands.Common.Authentication.AzureSession]::Instance.AuthenticationFactory.Authenticate($context.Account, $context.Environment, $context.Tenant.Id.ToString(), $null, [Microsoft.Azure.Commands.Common.Authentication.ShowDialog]::Never, $null, "https://graph.microsoft.com")
        Select-MgProfile -Name "beta" 

        Connect-MgGraph -AccessToken $ModuleGraphToken.AccessToken
    }

    function Set-ADINFOSCapability
    {
        Write-LogMessage -Message ("Retrieve Environment information ...")

        $script:ExchOrgName = (Get-OrganizationConfig).Identity
        $script:GCRoot = (Get-ADServerSettings).DefaultGlobalCatalog

        $ADInfo = Get-ADInfo
        $script:ForestName = $ADInfo[0]
        $script:ForestDN = $ADInfo[1]
        $script:gc = $ADInfo[2]
        $script:sidroot = $ADInfo[3]

        if ([String]::IsNullOrEmpty($Script:ESIEnvironmentIdentification)) {$Script:ESIEnvironmentIdentification = $script:ForestName}
    }

    function Set-IISCapability
    {
        Import-Module WebAdministration
        $Script:DefaultIISLogPath = (Get-WebConfigurationProperty "/system.applicationHost/sites/siteDefaults" -name logfile.directory).Value
        
        if (-not $Script:GetDomainSet)
        {
            $Execution = @()
            $Object = New-Object PSObject
            $Object | Add-Member Noteproperty -Name IISEnvironmentName -value $Script:ESIEnvironmentIdentification
            $Execution += $Object

            $Object = New-Result -Section "ESIEnvironment" -PSCmdL "Get-Domain" -CmdletResult $Execution -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID

            $Script:GetDomainSet = $true
            $Script:Results["Default"] += $Object
        }
    }

    function Set-ParallelStartingCode
    {
        Param ($InputStartingCode)

        if ($null -eq $Script:ExchangeStartingCode) {$Script:ExchangeStartingCode = [ScriptBlock]::Create($InputStartingCode.ToString())}
        else {
            $Script:ExchangeStartingCode = [ScriptBlock]::Create($InputStartingCode.ToString() + $Script:ExchangeStartingCode.ToString())
        }
    }

    function Set-Capabilities
    {
        Param(
            $CapabilitiesList = @('OP', 'ADINFOS')
        )

        $script:CapabilityLoaded = @()

        foreach ($Capability in $CapabilitiesList)
        {
            if ($Capability -eq 'OL' -and $Script:ESIProcessingType -notlike "Online") { continue; }
            if ($Capability -eq 'MGGRAPH' -and $Script:ESIProcessingType -notlike "Online") { continue; }
            if ($Capability -eq 'OP' -and $Script:ESIProcessingType -like "Online") { continue; }
            if ($Capability -eq 'ADINFOS' -and $Script:ESIProcessingType -like "Online") { continue; }
            
            Write-LogMessage -Message "Loading capability $Capability ..."

            switch ($Capability)
            {
                "OL"
                {
                    Set-ExchangeCapability
                    $script:CapabilityLoaded += "OL"
                    $script:CapabilityLoaded += "Exchange"
                }
                "OP"
                {
                    Set-ExchangeCapability

                    Write-LogMessage -Message ("Set Exchange View Entire Forest ...")
                    Set-ADServerSettings -ViewEntireForest $true

                    $script:CapabilityLoaded += "OP"
                    $script:CapabilityLoaded += "Exchange"
                }
                "MGGRAPH"
                {
                    Set-MgGraphCapability
                    $script:CapabilityLoaded += "MGGRAPH"
                }
                "ADINFOS"
                {
                    Set-ADINFOSCapability
                    $script:CapabilityLoaded += "ADINFOS"
                }
                "IIS"
                {
                    Set-IISCapability
                    $script:CapabilityLoaded += "IIS"
                }
                default
                {
                    Write-LogMessage "Impossible to load the capability $Capability, not supported"
                    throw "Impossible to load the capability $Capability, not supported"
                }
            }
        }

        if ($Script:ExportDomainsInformation -and ('OL' -in $CapabilitiesList -or 'OP' -in $CapabilitiesList))
        {
            Write-LogMessage -Message ("Launch Domain Information ...")
            if ($Script:ESIProcessingType -notlike "Online")
            {
                $Execution = @()
                foreach ($domain in $script:ht_domains.Keys)
                {
                    $Object = New-Object PSObject
                    $Object | Add-Member Noteproperty -Name Name -value $script:ht_domains[$domain].DCFQDN
                    $Object | Add-Member Noteproperty -Name DomainNetBios -value $domain
                    $Object | Add-Member Noteproperty -Name DCFQDN -value $script:ht_domains[$domain].DCFQDN
                    $Object | Add-Member Noteproperty -Name DomainFQDN -value $script:ht_domains[$domain].DomainFQDN
                    $Object | Add-Member Noteproperty -Name DomainDN -value $script:ht_domains[$domain].DomainDN
                    $Object | Add-Member Noteproperty -Name LinkedForest -value $script:ForestName
                    $Object | Add-Member Noteproperty -Name LinkedExchangeOrgName -value $script:ExchOrgName
                    $Object | Add-Member Noteproperty -Name LinkedForestDN -value $script:ForestName

                    $Execution += $Object
                }

                $Object = New-Result -Section "ESIEnvironment" -PSCmdL "Get-Domain" -CmdletResult $Execution -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID
            }
            else {
                <# Send tenant name #>
                $Execution = @()
                $Object = New-Object PSObject
                $Object | Add-Member Noteproperty -Name TenantName -value $script:TenantName
                $Execution += $Object

                $Object = New-Result -Section "ESIEnvironment" -PSCmdL "Get-Domain" -CmdletResult $Execution -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID
            }

            $Script:GetDomainSet = $true
            $Script:Results["Default"] += $Object
        }
    }

#endregion CapabilitiesManagement

#region Time Management

    function New-LastLaunchTimeObject
    {
        Param (
            [switch] $SpecificFunction,
            $FunctionName,
            $LastDateTracking
        )

        $Object = New-Object PSObject
        
        if ($SpecificFunction)
        {
            $Object | Add-Member Noteproperty -Name FunctionName -value $FunctionName
        }
        else {
            $Object | Add-Member Noteproperty -Name Tracking -value @()
        }

        $Object | Add-Member Noteproperty -Name LastDateTracking -value $LastDateTracking
        
        return $object
    }

    function Get-LastLaunchTime
    {
        Param(
            [switch] $SpecificFunction,
            [string] $FunctionName,
            [switch] $Reset,
            [string] $resetType = $null,
            [string] $SpecificFormat = $null
        )

        if ($Global:isRunbook)
        {
            if ($Global:InstanceName -ne "Default") {$ContentDate = Get-AutomationVariable -Name "LastDateTracking-$($Global:InstanceName)"}
            else { $ContentDate = Get-AutomationVariable -Name LastDateTracking }

            if ($ContentDate -like "Never")
            {
                $ContentDate = $null
            }
        }
        else {
            $fileName = "DateTracking.esi"

            if ($Global:InstanceName -ne "Default") { $fileName = "DateTracking-$($Global:InstanceName).esi"}

            if (Test-Path ((Split-Path $outputpath) + "\$fileName"))
            {
                $ContentDate = Get-Content ((Split-Path $outputpath) + "\$fileName")
            }
            else {
                $ContentDate = $null
            }
        }  

        if ($Reset -eq $true -or [string]::IsNullOrEmpty($ContentDate)) { $reset = $true }

        if ($SpecificFunction)
        {
            $SpecificDate = $null
            try{
                try {
                    $JSonContent = $ContentDate | ConvertFrom-Json -ErrorAction Stop
                    $Script:LastDateTrackingJSonContent = $JSonContent
                    $SpecificFunctionDate = $JsonContent.Tracking | Where-Object { $_.FunctionName -eq $FunctionName }
                }
                catch {
                    Write-LogMessage -Message "Impossible to read the file $fileName, in the new format" -Level Warning -NoOutput
                    $Script:LastDateTrackingJSonContent = $null
                    $SpecificFunctionDate = $null
                }

                if ($Reset -eq $True -or $null -eq $SpecificFunctionDate `
                    -or [String]::IsNullOrEmpty($SpecificFunctionDate.LastDateTracking) `
                    -or $SpecificFunctionDate.LastDateTracking -like "Never")
                {
                    # if resetType start with "SpecificDate" or "Current-AddDays" or "Current-AddMonths" or "Current-AddYears" or "Current-AddHours" or "Current-AddMinutes" or "Current-AddSeconds" then extract value inside []
                    if ($resetType -like "SpecificDate*" -or $resetType -like "Current-Add*")
                    {
                        $resetType = $resetType.Substring(0,$resetType.IndexOf("]"))
                        $resetValue = $resetType.Substring($resetType.IndexOf("[")+1)
                        $resetType = $resetType.Substring(0,$resetType.IndexOf("["))

                        #if resetType start with "Current-Add" then extract the unit after "Add"
                        if ($resetType -like "Current-Add*")
                        {
                            $resetUnit = $resetType.Substring($resetType.IndexOf("-Add")+4)
                            $resetType = "Current-Add"
                        }
                        else {
                            Write-LogMessage "Impossible to find the unit to add to the current date in the parameter $resetType" -NoOutput -Level Error
                            $resetType = "Standard"
                        }
                    }
                    
                    switch ($resetType)
                    {
                        "CurrentDate"{
                            $SpecificDate = (Get-Date)
                        }
                        "LastDateOfScript"{
                            #Start from last date stored in the file for the script
                            $SpecificDate = $script:LastDateTracking
                        }
                        "Standard"{
                            #Apply the same rule as the script : Current date minus "DefaultDurationTracking" parameter in days
                            $SpecificDate = (Get-Date).AddDays($Script:DefaultDurationTracking * -1)
                        }
                        "SpecificDate"{
                            #Start from a specific date specified in the parameter "YourDate"
                            try {
                                #try convert the value to a date
                                $SpecificDate = Get-Date $resetValue
                            }
                            catch {
                                Write-LogMessage -Message "Impossible to convert the value $resetValue to a date, Standard method will be used" -NoOutput -Level Error
                                $SpecificDate = (Get-Date).AddDays($Script:DefaultDurationTracking * -1)
                            }
                        }
                        "Current-Add"{
                            #Start from current date plus/minus a number of days specified in the parameter "YourNumber"
                            #Try to convert the value to an integer
                            try{
                                $resetValue = [int]$resetValue

                                switch ($resetUnit)
                                {
                                    "Days" { $SpecificDate = (Get-Date).AddDays($resetValue) }
                                    "Months" { $SpecificDate = (Get-Date).AddMonths($resetValue) }
                                    "Years" { $SpecificDate = (Get-Date).AddYears($resetValue) }
                                    "Hours" { $SpecificDate = (Get-Date).AddHours($resetValue) }
                                    "Minutes" { $SpecificDate = (Get-Date).AddMinutes($resetValue) }
                                    "Seconds" { $SpecificDate = (Get-Date).AddSeconds($resetValue) }
                                    default { 
                                        Write-LogMessage -Message "The value $resetUnit is not a valid unit to add to a date, Standard method will be used" -NoOutput -Level Error
                                        $SpecificDate = (Get-Date).AddDays($Script:DefaultDurationTracking * -1) 
                                    }
                                }

                            }
                            catch{
                                Write-LogMessage -Message "Impossible to convert the value $resetValue to an integer, Standard method will be used" -NoOutput -Level Error
                                $SpecificDate = (Get-Date).AddDays($Script:DefaultDurationTracking * -1)
                            }
                        }
                        default { $SpecificDate = (Get-Date).AddDays($Script:DefaultDurationTracking * -1) }
                    }
                    
                    if ($null -ne $SpecificFunctionDate) 
                    { 
                        $SpecificFunctionDate.LastDateTracking = $SpecificDate
                    }
                    else { $SpecificDate = (Get-Date).AddDays($Script:DefaultDurationTracking * -1) }
                }
                else {
                    $SpecificDate = Get-Date $SpecificFunctionDate.LastDateTracking
                }

                if (-not [String]::IsNullOrEmpty($SpecificFormat))
                {
                    $SpecificDate = $SpecificDate.ToString($SpecificFormat)
                }
            }
            catch
            {
                Write-LogMessage -Message "Impossible to generate a date using DateStorage specification. Error : $($_.Exception.Message)" -Level Warning -NoOutput
                $Script:LastDateTrackingJSonContent = $null
                $SpecificDate = (Get-Date).AddDays($Script:DefaultDurationTracking * -1)
            }

            return $SpecificDate
        }
        else {

            if ($reset)
            {
                $script:LastDateTracking = (Get-Date).AddDays($Script:DefaultDurationTracking * -1)
            }
            else {
                try{
                    $JSonContent = $ContentDate | ConvertFrom-Json -ErrorAction Stop
                    $Script:LastDateTrackingJSonContent = $JSonContent

                    if ([String]::IsNullOrEmpty($JSonContent.LastDateTracking) -or $JSonContent.LastDateTracking -like "Never")
                    {
                        $script:LastDateTracking = (Get-Date).AddDays($Script:DefaultDurationTracking * -1)
                    }
                    else {
                        $script:LastDateTracking = Get-Date $JSonContent.LastDateTracking
                    }
                }
                catch
                {
                    Write-LogMessage -Message "Impossible to read the file $fileName, in the new format, trying the old one" -Level Warning
                    $Script:LastDateTrackingJSonContent = $null

                    try{
                        $script:LastDateTracking = Get-Date $ContentDate
                    }
                    catch {
                        Write-LogMessage -Message "Impossible to find the date in file. Set date as beginning cycle" -Level Warning
                        $script:LastDateTracking = (Get-Date).AddDays($Script:DefaultDurationTracking * -1)
                    }
                }
            }
        }
    }

    function Set-CurrentLaunchTime
    {
        Param(
            [switch] $SpecificFunction,
            [string] $FunctionName,
            $DateSuffix,
            [string] $SpecificFormat,
            [switch] $Save
        )

        if ($null -eq $Script:LastDateTrackingJSonContent)
        {
            $Script:LastDateTrackingJSonContent = New-LastLaunchTimeObject -LastDateTracking $script:LastDateTracking
        }

        if ($SpecificFunction)
        {
            if (-not [string]::IsNullOrEmpty($SpecificFormat))
            {
                $DateSuffix = $DateSuffix.ToString($SpecificFormat)
            }
            
            $SpecificFunctionDate = $Script:LastDateTrackingJSonContent.Tracking | Where-Object { $_.FunctionName -eq $FunctionName }

            if ($null -eq $SpecificFunctionDate)
            {
                $SpecificFunctionDate = New-LastLaunchTimeObject -SpecificFunction -FunctionName $FunctionName -LastDateTracking $DateSuffix
                $Script:LastDateTrackingJSonContent.Tracking += $SpecificFunctionDate
            }
            else {
                $SpecificFunctionDate.LastDateTracking = $DateSuffix
            }
        }
        else {
            $Script:LastDateTrackingJSonContent.LastDateTracking = $DateSuffix
        }

        if ($save)
        {
            $JSNToSave = $Script:LastDateTrackingJSonContent | ConvertTo-Json
            if ($Global:isRunbook)
            {
                if ($Global:InstanceName -ne "Default") {Set-AutomationVariable -Name "LastDateTracking-$($Global:InstanceName)" -Value $JSNToSave.ToString()}
                else { Set-AutomationVariable -Name LastDateTracking -Value $JSNToSave.ToString() }
            }
            else 
            { 
                if ($Global:InstanceName -ne "Default") {
                    $JSNToSave | Set-ESIContent ((Split-Path $outputpath) + "\DateTracking-$($Global:InstanceName).esi")
                }
                else { $JSNToSave | Set-ESIContent ((Split-Path $outputpath) + "\DateTracking.esi") }
            }
        }
    }

#endregion Time Management

#region Log and file Management
    function Write-LogMessage {
        [CmdletBinding()]
        param (
            [Parameter(Mandatory=$true)]
            [string]
            $Message,
            [Parameter(Mandatory=$false)]
            [string]
            $Category="General",
            [Parameter(Mandatory=$false)]
            [ValidateSet("Info","Warning","Error","Verbose")]
            [string]
            $Level="Info",
            [switch] $NoOutput
        )
        $line = "$(Get-Date -f 'yyyy/MM/dd HH:mm:ss')`t$Level`t$Category`t$Message"
        Set-Variable -Name UDSLogs  -Value "$UDSLogs`n$line" -Scope Script
        if($NoOutput -or $Global:DeactivateWriteOutput){
            if ($script:FASTVerboseLevel) { Write-Verbose $line }
            else{
                Write-Host $line
            }
        }else{
            Write-Output $line
        }
        switch ($Level) {
            "Verbose" {
                if ($script:FASTVerboseLevel) { Write-Verbose "[VERBOSE] $Category :`t$Message" }
            }
            "Info" {
                Write-Information "[INFO] $Category :`t$Message"
            }
            "Warning" {
                Write-Warning "$Category :`t$Message"
            }
            "Error" {
                Write-Error "$Category :`t$Message"
            }
            Default {}
        }    
    }

    function Set-ESIContent{
        [CmdletBinding()]
        param(
            [Parameter(Mandatory=$true, ValueFromPipeline=$true) ]
            [string]
            $Content,
            [Parameter(Mandatory=$true)]
            [string]
            $Path
        )
    
        if ($PSVersionTable.PSVersion.Major -ge 7)
        {
            # PowerShell 7 and higher
            $Content | Set-Content -Path $Path -NoNewline -Encoding utf8NoBOM
        }
        else
        {
            # Powershell 5.1
            $Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
            #[System.IO.File]::WriteAllLines($Path, $Content, $Utf8NoBomEncoding) Prefer WriteAllText as it doesn't add newline at the end of the file
            [System.IO.File]::WriteAllText($Path, $Content, $Utf8NoBomEncoding)
        }
    }

    function Get-UDSLogs
    {
        [CmdletBinding()]
        param()

        return $Script:UDSLogs
    }

    function Invoke-UDSLogProcessor
    {
        $LogProcessorOutput = "`n`n**** UDS Log Processor ****"
        if ($script:DeactivateUDSLogs)
        {
            $LogProcessorOutput += "`nLogs deactivated"
        }
        else {
            if ($script:UDSLogControl)
            {
                $LogProcessorOutput += "`nUDS Log Control activated"
                if ($null -eq $Script:UDSLogProcessor -or $Script:UDSLogProcessor.Count -eq 0)
                {
                    $LogProcessorOutput += "`nNo processor defined"
                }
                else {
                    $LogProcessorOutput += "`n$($Script:UDSLogProcessor.Count) UDS Processor(s) defined"
                }
            }
            else {
                $LogProcessorOutput += "`nUDS Log Control deactivated"

                $OutputProcessor = @{
                    LogStorageType = "Output"
                }

                $LogProcessorOutput += "`nAdd Output processor"

                $Script:UDSLogProcessor = @($OutputProcessor)
            }

            foreach($ProcessorEntry in $Script:UDSLogProcessor)
            {
                
                try {
                    $LogProcessorOutput += "`nInvoke processor $($ProcessorEntry.LogStorageType)"
                    switch($ProcessorEntry.LogStorageType)
                    {
                        "Output"
                        {
                            $LogProcessorOutput += "`n**************** LOGS **********************"
                            $LogProcessorOutput += Get-UDSLogs
                            $LogProcessorOutput += "`n**************** END LOGS **********************`n"
                        }
                        "File"
                        {
                            if ($Global:isRunbook)
                            {
                                $LogProcessorOutput += "`nUDS File processor not available in Runbook"
                            }
                            else {
                                if ([System.IO.Path]::IsPathRooted($ProcessorEntry.LogStoragePath))
                                {
                                    $UDSLogPath = $ProcessorEntry.LogStoragePath
                                }
                                else
                                {
                                    $UDSLogPath = $Script:scriptFolder + "\" + $ProcessorEntry.LogStoragePath
                                }
                                
                                if (-not (Test-Path $UDSLogPath))
                                {
                                    $LogProcessorOutput += "`nCreate folder $UDSLogPath"
                                    New-Item -ItemType Directory -Path $UDSLogPath
                                }

                                CleanFiles -ScriptLogPath $UDSLogPath -ClearFilesOlderThan $ProcessorEntry.LogStorageRetentionDays

                                # Generate Filename using Prefix, ScriptInstanceID and Date
                                $UDSLogFileName = "$($ProcessorEntry.Prefix)-$($Script:ScriptInstanceID)-$(Get-Date -f 'yyyyMMdd').log"

                                $LogProcessorOutput += "`nWrite logs to $UDSLogPath\$UDSLogFileName"
                                $UDSLogs | Out-File -FilePath "$UDSLogPath\$UDSLogFileName"
                            }
                        }
                        "AzureStorageAccount"
                        {
                            $ExecutionImpossible = $false
                            if (-not (Get-Module -Name Az.Storage -ListAvailable))
                            {
                                $LogProcessorOutput += "`nUDS Azure Storage Account module not available"
                                $ExecutionImpossible = $true
                            }
                            elseif (-not (Get-Command -Name Connect-AzAccount -Module Az.Accounts -ErrorAction SilentlyContinue))
                            {
                                $LogProcessorOutput += "`nUDS Azure Storage Account module not available"
                                $ExecutionImpossible = $true
                            }

                            if (-not $Global:isRunbook)
                            {
                                if ($ProcessorEntry.ConnectionType -like "ManagedIdentity")
                                {
                                    $LogProcessorOutput += "`nUDS Azure Storage Account Managed Identity not available"
                                    $ExecutionImpossible = $true
                                }
                            }
                            
                            if (-not $ExecutionImpossible)
                            {                            
                                try
                                {
                                    switch ($ProcessorEntry.ConnexionType) {
                                        "ManagedIdentity" { 
                                            # BEGIN: Authenticate with Managed Identity
                                            $ResultAccount = Connect-AzAccount -Identity -Tenant $ProcessorEntry.TenantID
                                            # END: Authenticate with Managed Identity
                                        }
                                        "Certificate" { 
                                            # BEGIN: Authenticate with Certificate
                                            $ResultAccount = Connect-AzAccount -CertificateThumbprint $ProcessorEntry.CertificateThumbprint -ApplicationId $ProcessorEntry.ApplicationID -Tenant $ProcessorEntry.TenantId -ServicePrincipal
                                            # END: Authenticate with Certificate
                                        }
                                        Default 
                                        {   
                                            $LogProcessorOutput += "`nNAuthentication type $($ProcessorEntry.ConnexionType) not implemented yet"
                                            Throw "nAuthentication type $($ProcessorEntry.ConnexionType) not implemented yet"
                                        }
                                    }

                                    if ($null -eq $ResultAccount)
                                    {
                                        Throw "Impossible to authenticate to Azure Storage Account"
                                    }
                                    else {
                                        $LogProcessorOutput += "`nUDS Azure Storage Account processor authenticated"
                                    }

                                    
                                    # BEGIN: Create a new blob client
                                    $context = New-AzStorageContext -StorageAccountName $ProcessorEntry.StorageAccountName -UseConnectedAccount
                                    # END: Create a new blob client

                                    # BEGIN: Create a new container if it doesn't exist
                                    $container = Get-AzStorageContainer -Context $context -Name $ProcessorEntry.StorageBlobContainer
                                    if ($null -eq $container) {
                                        $container = New-AzStorageContainer -Name $ProcessorEntry.StorageBlobContainer -Context $context
                                    }
                                    # END: Create a new container if it doesn't exist

                                    # BEGIN: Create a new blob and upload the logs
                                    if ($null -ne $ProcessorEntry.Prefix)
                                    {
                                        $blobName = "$($ProcessorEntry.Prefix)-$($Script:ScriptInstanceID)-$(Get-Date -f 'yyyyMMdd').log"
                                    }
                                    else
                                    {
                                        $blobName = "$($Script:ScriptInstanceID)-$(Get-Date -f 'yyyyMMdd').log"
                                    }

                                    $Filename = "$($env:TEMP)\$blobName"
                                    Set-ESIContent -Path $Filename -Content (Get-UDSLogs)
                                    Set-AzStorageBlobContent -File $Filename -Container $container.Name -Blob $blobName -Context $context
                                    
                                    Remove-Item $Filename -ErrorAction SilentlyContinue
                                    
                                    $LogProcessorOutput += "`nUDS Logs written to Azure Storage Account: $($ProcessorEntry.StorageAccountName) - Container: $($ProcessorEntry.StorageBlobContainer) - Blob: $blobName"
                                }
                                catch {
                                    $LogProcessorOutput += "`nError during UDS Azure Storage Account processor"
                                    $LogProcessorOutput += "`n$($_.Exception.Message) - $($_.Exception.ItemName) - $($_.Exception.InvocationInfo.PositionMessage) - $($_.Exception.InvocationInfo.ScriptLineNumber) - $($_.Exception.InvocationInfo.OffsetInLine) - $($_.Exception.InvocationInfo.Line)"
                                    Write-Warning "Error during UDS Azure Storage Account processor"
                                    Write-Warning "$($_.Exception.Message) - $($_.Exception.ItemName) - $($_.Exception.InvocationInfo.PositionMessage) - $($_.Exception.InvocationInfo.ScriptLineNumber) - $($_.Exception.InvocationInfo.OffsetInLine) - $($_.Exception.InvocationInfo.Line)"
                                }
                            }
                            else {
                                $LogProcessorOutput += "`nUDS Azure Storage Account processor not executed, missing PS Module or bad context"
                            }
                        }
                        Default
                        {
                            $LogProcessorOutput += "`nUnknown processor type"
                        }
                    }
                }
                catch {
                    $LogProcessorOutput += "`nError during processor $($ProcessorEntry.LogStorageType)"
                    $LogProcessorOutput += "`n$($_.Exception.Message)"
                    Write-Warning "Error during UDS processor $($ProcessorEntry.LogStorageType)"
                    Write-Warning "$($_.Exception.Message)"
                }
                
            }
        }

        $LogProcessorOutput += "`n**** END UDS Log Processor ****"

        return $LogProcessorOutput
    }

    function CleanFiles
    {
        Param(
            $ClearFilesOlderThan,
            $ScriptLogPath,
            $outputpath = $null
        )

        $DirectoryList = @()
        $DirectoryList += $ScriptLogPath
        if ($null -ne $outputpath) { $DirectoryList += (Split-Path $outputpath) }

        Write-LogMessage "`t ..Cleaning Report and log files older than $ClearFilesOlderThan days."
        $MaxDate = (Get-Date).AddDays($ClearFilesOlderThan*-1)

        $OtherOldFiles = @()
        $FileList = @()
        if ($DirectoryList.count -gt 0)
        {
            foreach ($dir in $DirectoryList)
            {
                if (Test-Path $dir)
                {
                    $OtherPathObj = Get-Item -Path $dir
                    $OtherFiles = $OtherPathObj.GetFiles()
                    $OtherOldFiles = $OtherFiles | Where-Object {$_.LastWriteTime -le $MaxDate}
                    Write-LogMessage ("`t`t There is "+ $OtherFiles.Count + " existing files in $dir with "+ $OtherOldFiles.Count +" files older than $MaxDate.")
                }
                elseif (Test-Path ($scriptFolder + "\" + $dir))
                {
                    $OtherPathObj = Get-Item -Path $dir
                    $OtherFiles = $OtherPathObj.GetFiles()
                    $OtherOldFiles = $OtherFiles | Where-Object {$_.LastWriteTime -le $MaxDate}
                    Write-LogMessage ("`t`t There is "+ $OtherFiles.Count + " existing files in $dir with "+ $OtherOldFiles.Count +" files older than $MaxDate.")
                }
                $FileList += $OtherOldFiles
            }
        }

        $NbRemove = 0
        foreach ($File in $FileList)
        {
            Remove-Item $File.FullName
            $NbRemove += 1
            Write-LogMessage ("`t`t`t File "+ $File.Name + " Removed.")
        }
        
        Write-LogMessage ("`t`t $NbRemove Files Removed for cleaning process.")
    }

#endregion Log and file Management

#region Sentinel Upload Management

    function Invoke-ESIWebRequest
    {
        Param(
            $Uri
        )

        $object = $null

        if ($script:Useproxy)
        {
            $object = (Invoke-WebRequest -Uri $Uri -UseBasicParsing -Proxy $Script:ProxyUrl).Content
        }
        else
        {
            $object = (Invoke-WebRequest -Uri $Uri -UseBasicParsing).Content
        }

        return $object
    }

    function Get-OutputOptions
    {
        Param(
            $OutputName
        )

        $OutputOptions = New-Object PSObject
        $OutputOptions | Add-Member Noteproperty -Name OutputName -value $OutputName
        $OutputOptions | Add-Member Noteproperty -Name OutputSentinelAPI -value $null
        $OutputOptions | Add-Member Noteproperty -Name OutputFileName -value $null
        $OutputOptions | Add-Member Noteproperty -Name IsPartial -value $false
        $OutputOptions | Add-Member Noteproperty -Name AlreadyBackuped -value $false

        if ($OutputName -match '_Page')
        {
            $OutputOptions.IsPartial = $true
            if ($OutputName -match '_Page_SentDuringExecution')
            {
                $OutputOptions.AlreadyBackuped = $true
                $OutputName = $OutputName -replace '_Page_SentDuringExecution',''
            }
            else
            {
                $OutputName = $OutputName -replace '_Page',''
            }
        }
        
        if ($OutputName -eq "Default") {
            if ($Script:InstanceName -ne "Default") 
            {
                if ([string]::IsNullOrEmpty($Script:InstanceConfiguration.OutputName)) 
                { 
                    $TargetOutputName = $script:outputpath -replace '.csv',"-$($Script:InstanceName).csv"
                    $OutputOptions.OutputFileName = $Script:InstanceName 
                }
                else 
                { 
                    $OutputOptions.OutputFileName = $Script:InstanceConfiguration.OutputName

                    if ($OutputOptions.OutputFileName -notmatch ".csv$")
                    {
                        $OutputOptions.OutputFileName = $OutputOptions.OutputFileName + ".csv"
                    }

                    $OutputOptions.OutputSentinelAPI = $Script:InstanceConfiguration.OutputName
                }
            }
            else { $OutputOptions.OutputFileName = $script:outputpath }
        }
        else {
            $OutputOptions.OutputFileName = $OutputName
        }

        if ($OutputName -match '//')
        {
            $TargetOutput = $OutputName -split '//'
            $OutputOptions.OutputFileName = $TargetOutput[0]
            $OutputOptions.OutputSentinelAPI = $TargetOutput[1]
        }        

        return $OutputOptions
    }

    function Start-LogBackup
    {
        Param(
            $OutputName,
            [switch] $PartialData,
            $PartialDataName,
            [switch] $PartialDataRawFormat,
            $RawData
        )

        if ($Script:SentinelLogCollector.ActivateLogUpdloadToSentinel)
        {
            Start-LogsInjestion -OutputName $OutputName -PartialData:$PartialData -PartialDataName $PartialDataName -PartialDataRawFormat:$PartialDataRawFormat -RawData $RawData
        }

        if (-not $Script:SentinelLogCollector.ActivateLogUpdloadToSentinel -or $Script:SentinelLogCollector.TogetherMode)
        {
            Save-LogsToCSV -OutputName $OutputName -PartialData:$PartialData -PartialDataName $PartialDataName -PartialDataRawFormat:$PartialDataRawFormat -RawData $RawData
        }
    }

    function Start-LogsInjestion
    {
        Param(
            $OutputName,
            [switch] $PartialData,
            $PartialDataName,
            [switch] $PartialDataRawFormat,
            $RawData
        )

        Write-LogMessage -Message "Injection into Azure Sentinel"

        if ($PartialDataRawFormat)
        {
            $ProcessedData = $RawData
        }
        elseif ($PartialData)
        {
            $ProcessedData = $script:Results[$OutputName][$PartialDataName]
        }
        else {
            $ProcessedData = $script:Results[$OutputName]
        }

        $OutputOptions = Get-OutputOptions -OutputName $OutputName
        $OutputSentinelAPI = $OutputOptions.OutputSentinelAPI

        try
        {   
            $ResultInjsonFormat = $ProcessedData | ConvertTo-Json -Compress
            $Global:InjectionTest += $ProcessedData
        }
        catch
        {
            throw("Input data cannot be converted into a JSON object. Please make sure that the input data is a standard PowerShell table")
        }

        if ([String]::IsNullOrEmpty($OutputSentinelAPI)) {$OutputSentinelAPI = $Script:SentinelLogCollector.LogTypeName}

        if ($Script:InstanceConfiguration.FileFilterType -match "Categorize" -and [String]::IsNullOrEmpty($Script:InstanceConfiguration.OutputName))
        {
            $OutputSentinelAPI  = $OutputSentinelAPI -replace 'ESI', "ESI-$($Script:InstanceConfiguration.Category)-"
        }

        $ResultLength = [System.Text.Encoding]::UTF8.GetBytes($ResultInjsonFormat).Length
        $contentDivision = [math]::Ceiling($ResultLength / ($Script:MaximalSentinelPacketSizeMb *1024*1024))

        if ($contentDivision -le 1)
        {
            Write-LogMessage -Message ("Upload payload size is less than $($Script:MaximalSentinelPacketSizeMb)Mb. It will be sent in 1 segment")
            # Submit the data to the API endpoint
            Post-LogAnalyticsData -customerId $Script:SentinelLogCollector.WorkspaceId `
            -sharedKey $Script:SentinelLogCollector.WorkspaceKey `
            -body ([System.Text.Encoding]::UTF8.GetBytes($ResultInjsonFormat)) `
            -logType $OutputSentinelAPI
        }
        else {
            
            Write-LogMessage -Message ("Upload payload size is " + ($ResultLength/1024/1024).ToString("#.#") + "Mb, greater than $($Script:MaximalSentinelPacketSizeMb)Mb. It will be sent in $contentDivision segments")

            $maxCount = [math]::Floor($ProcessedData.Count / $contentDivision)

            $maxSegmentCount = $maxCount
            $CounterStart = 0
            $exitNextTime = $false
            while ($exitNextTime -eq $false)
            {
                if ($maxSegmentCount -ge $ProcessedData.Count)
                {
                    $maxSegmentCount = $ProcessedData.Count
                    $exitNextTime = $true
                }
                
                Write-LogMessage -Message ("Sending Segment $CounterStart to $maxSegmentCount")

                $TempTable = @()
                for ($Counter = $CounterStart; $Counter -lt $maxSegmentCount; $Counter++)
                {
                    $TempTable += $ProcessedData[$Counter]
                }

                $CounterStart = $maxSegmentCount
                $maxSegmentCount += $maxCount

                $ResultInjsonFormat = $TempTable | ConvertTo-Json -Compress

                Write-LogMessage -Message ("Sending payload : $ResultInjsonFormat")

                try {
                    # Submit the data to the API endpoint
                    Post-LogAnalyticsData -customerId $Script:SentinelLogCollector.WorkspaceId `
                    -sharedKey $Script:SentinelLogCollector.WorkspaceKey `
                    -body ([System.Text.Encoding]::UTF8.GetBytes($ResultInjsonFormat)) `
                    -logType $OutputSentinelAPI
                }
                catch {
                    Write-LogMessage -Message ("Error sending to Sentinel. $_") -Level Error
                }
                
            }
        }
    }

    function Save-LogsToCSV
    {
        Param(
            $OutputName,
            [switch] $PartialData,
            $PartialDataName,
            [switch] $PartialDataRawFormat,
            $RawData
        )

        Write-LogMessage -Message "CSV Creation"

        if ($PartialDataRawFormat)
        {
            $ProcessedData = $RawData
        }
        elseif ($PartialData)
        {
            $ProcessedData = $script:Results[$OutputName][$PartialDataName]
        }
        else {
            $ProcessedData = $script:Results[$OutputName]
        }

        $OutputOptions = Get-OutputOptions -OutputName $OutputName
        $OutputFileName = $OutputOptions.OutputFileName


        if ($PartialData -or $PartialDataRawFormat)
        {
            if ([String]::IsNullOrEmpty($PartialDataName))
            {
                $Guid = [guid]::NewGuid().ToString()
                $OutputFileName = $OutputFileName -replace ".csv", "-$Guid.csv"
            }
            else
            {
                $OutputFileName = $OutputFileName -replace ".csv", "-$PartialDataName.csv"
            }
        }

        $outputdirectorypath = Split-Path $script:outputpath

        # If $OutputFileName does not end with .csv, add it
        if ($OutputFileName -notmatch ".csv$")
        {
            $OutputFileName = $OutputFileName + ".csv"
        }

        if ((-not $ForceOutputWithoutDate -or $null -eq $ForceOutputWithoutDate) -and $OutputFileName -notmatch "-$DateSuffixForFile.csv")
        {
            $OutputFileName = $OutputFileName -replace ".csv", "-$DateSuffixForFile.csv"
        }
        if ([String]::IsNullOrEmpty((Split-Path $OutputFileName))) {$OutputFileName = $outputdirectorypath+ "\" + $OutputFileName}
        $ProcessedData | Export-Csv -Path $OutputFileName -NoTypeInformation
    }

    Function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
    {
        $xHeaders = "x-ms-date:" + $date
        $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource

        $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
        $keyBytes = [Convert]::FromBase64String($sharedKey)

        $sha256 = New-Object System.Security.Cryptography.HMACSHA256
        $sha256.Key = $keyBytes
        $calculatedHash = $sha256.ComputeHash($bytesToHash)
        $encodedHash = [Convert]::ToBase64String($calculatedHash)
        $authorization = 'SharedKey {0}:{1}' -f $customerId,$encodedHash
        return $authorization
    }

    Function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType)
    {
        $method = "POST"
        $contentType = "application/json"
        $resource = "/api/logs"
        $TimeStampField = [DateTime]::UtcNow
        $rfc1123date = [DateTime]::UtcNow.ToString("r")
        $contentLength = $body.Length
        $signature = Build-Signature `
            -customerId $customerId `
            -sharedKey $sharedKey `
            -date $rfc1123date `
            -contentLength $contentLength `
            -method $method `
            -contentType $contentType `
            -resource $resource
        $uri = "https://" + $customerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"

        $headers = @{
            "Authorization" = $signature;
            "Log-Type" = $logType;
            "x-ms-date" = $rfc1123date;
            "time-generated-field" = $TimeStampField;
        }

        #validate that payload data does not exceed limits
        if ($body.Length -gt (31.9 *1024*1024))
        {
            throw("Upload payload is too big and exceed the 32Mb limit for a single upload. Please reduce the payload size. Current payload size is: " + ($body.Length/1024/1024).ToString("#.#") + "Mb")
        }

        Write-LogMessage -Message ("Upload payload size is " + ($body.Length/1024).ToString("#.#") + "Kb")

        try {
            if ($Useproxy)
            {
                $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing -Proxy $Script:ProxyUrl
            }
            else {
                $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
            }
        }
        catch {
            if ($_.Exception.Message.startswith('The remote name could not be resolved'))
            {
                throw ("Error - data could not be uploaded. Might be because workspace ID or private key are incorrect")
            }

            throw ("Error - data could not be uploaded: " + $_.Exception.Message)
        }
        
        # Present message according to the response code
        if ($response.StatusCode -eq 200) 
        { Write-LogMessage  "200 - Data was successfully uploaded" }
        else
        { throw ("Server returned an error response code:" + $response.StatusCode)}
    }
#endregion Sentinel Upload Management

#region Dynamic Cmdlet Management

    #Function to construc list of cmdlet to execute
    function New-Entry
    {
        Param (
            [Parameter(Mandatory=$True)] [String] $Section,
            [Parameter(Mandatory=$True)] [String] $PSCmdL,
            [Parameter(Mandatory=$False)] $Select = @(),
            [Parameter(Mandatory=$False)] [String] $OutputStream = "Default",
            [Parameter(Mandatory=$False)] [String] $TransformationFunction = $null,
            [Parameter(Mandatory=$False)] [Switch] $TransformationForeach,
            [Parameter(Mandatory=$False)] [Switch] $ProcessPerServer,
            [Parameter(Mandatory=$False)] [Switch] $Norunspace,
            [Parameter(Mandatory=$False)] [PSCustomObject] $PaginationInformation = $null,
            [Parameter(Mandatory=$False)] [PSCustomObject] $DateStorageInformation = $null
        )

        $Object = New-Object PSObject
        $Object | Add-Member Noteproperty -Name Section -value $Section
        $Object | Add-Member Noteproperty -Name PSCmdL -value $PSCmdL
        $Object | Add-Member Noteproperty -Name OutputStream -value $OutputStream
        $Object | Add-Member Noteproperty -Name Select -value $Select
        $Object | Add-Member Noteproperty -Name TransformationFunction -value $TransformationFunction
        $Object | Add-Member Noteproperty -Name TransformationForeach -value $TransformationForeach
        $Object | Add-Member Noteproperty -Name ProcessPerServer -value $ProcessPerServer
        $Object | Add-Member Noteproperty -Name Norunspace -value $Norunspace
        $Object | Add-Member Noteproperty -Name PaginationInformation -value $PaginationInformation
        $Object | Add-Member Noteproperty -Name DateStorageInformation -value $DateStorageInformation
        
        return $Object
    }

    #Function to create an object with information about pagination
    function New-Pagination
    {
        Param (
            [Parameter(Mandatory=$False)] [switch] $PaginationActivated,
            [Parameter(Mandatory=$False)] [Int] $PageSize = 1000,
            [Parameter(Mandatory=$False)] [Int] $MaxPage = 1000,
            [Parameter(Mandatory=$False)] [switch] $PartialDataUpload,
            [Parameter(Mandatory=$False)] [switch] $StorePagesInMemory
        )

        $Object = New-Object PSObject
        $Object | Add-Member Noteproperty -Name PaginationActivated -value $PaginationActivated
        $Object | Add-Member Noteproperty -Name PageSize -value $PageSize
        $Object | Add-Member Noteproperty -Name MaxPage -value $MaxPage
        $Object | Add-Member Noteproperty -Name PartialDataUpload -value $PartialDataUpload
        $Object | Add-Member Noteproperty -Name StorePagesInMemory -value $StorePagesInMemory
        
        return $Object
    }

    #Function to create an object with information about date
    function New-DateStorage
    {
        Param (
            [Parameter(Mandatory=$False)] [switch] $DateStorageActivated,
            [Parameter(Mandatory=$False)] [String] $DateAttribute,
            [Parameter(Mandatory=$False)] 
                [ValidateSet("LastDate", "StartDateScript", "DateFromAttribute")] 
                [String] $DateStorageMode = "LastDate",
            [Parameter(Mandatory=$False)] $LastDateTracking,
            [Parameter(Mandatory=$False)] $SpecificFormat
        )

        if ($DateStorageMode -eq "DateFromAttribute" -and [String]::IsNullOrEmpty($DateAttribute))
        {
            throw ("Error - DateAttribute must be specified when DateStorageMode is DateFromAttribute")
        }

        $Object = New-Object PSObject
        $Object | Add-Member Noteproperty -Name DateStorageActivated -value $DateStorageActivated
        $Object | Add-Member Noteproperty -Name DateAttribute -value $DateAttribute
        $Object | Add-Member Noteproperty -Name DateStorageMode -value $DateStorageMode
        $Object | Add-Member Noteproperty -Name LastDateTracking -value $LastDateTracking
        $Object | Add-Member Noteproperty -Name SpecificFormat -value $SpecificFormat
        
        return $Object
    }

    #Function to construct the output file which depend on the section currently processing
    Function GetCmdletExec
    {
        Param(
            $Section,
            $PSCmdL,
            $Select = $null,
            $TransformationFunction = $null,
            [switch] $TransformationForeach,
            $TargetServer = $null,
            [switch] $SaveDate,
            $SaveDateAttribute = $null,
            $Entry,
            [switch] $PaginationExecution
        )

        if ($null -ne $Entry.PaginationInformation -and $Entry.PaginationInformation.PaginationActivated) {

            Write-LogMessage -Message ("`tPagination data for $($Entry.Section) added for Execution") -NoOutput

            $PaginationExecution = $true
            $EntryOutStream = $Entry.OutputStream + "_Page"
            $ProcessMaxPage = $Entry.PaginationInformation.MaxPage
            $ProcessPageSize = $Entry.PaginationInformation.PageSize

            if ($Entry.PaginationInformation.PartialDataUpload)
            {
                $EntryOutStream = $EntryOutStream + "_SentDuringExecution"
            }

        }
        else {
            Write-LogMessage -Message ("`tNo Pagination information found for $($Entry.Section)") -NoOutput
            $EntryOutStream = $Entry.OutputStream
            $ProcessMaxPage = 1
            $ProcessPageSize = 0
        }

        $ProcessPage = 1
        $ProcessLoop = $true
        $EntryList = @{}
        $PaginationErrorCount = 0

        while ($ProcessLoop -and $ProcessPage -le $ProcessMaxPage)
        {
            Write-LogMessage -Message ("`t`tLaunch collection $inc on $($FunctionList.count) - Page $ProcessPage") -NoOutput

            $EntrySuboutputPage =  "$($Section)_Page_$($ProcessPage)"

            if ($null -ne $targetServer) {
                $EntrySuboutputPage = $EntrySuboutputPage + "_$TargetServer"
            }

            $EntryList[$EntrySuboutputPage] = @()

            if ($PaginationExecution) {
                if ($PSCmdL -match "#Pagination#") 
                {
                    $EntryCmdlet = $PSCmdL -replace "#Pagination#", " -PageSize $ProcessPageSize -Page $ProcessPage"
                }
                else {
                    $EntryCmdlet = $PSCmdL + " -PageSize $ProcessPageSize -Page $ProcessPage"
                }
            }
            else {
                $EntryCmdlet = $PSCmdL
            }

            try {
                if ([String]::IsNullOrEmpty($TargetServer))
                {
                    Write-LogMessage -Message ("`tLaunch collection of $Section - $EntryCmdlet - Global Configuration ...")  -NoOutput
                    $PSCmdLResult = Invoke-Expression $EntryCmdlet
                }
                else
                {
                    Write-LogMessage -Message ("`tLaunch collection of $Section - $EntryCmdlet - Per Server Configuration for $TargetServer ...")  -NoOutput
                    $PSCmdL = $EntryCmdlet -replace "#TargetServer#", $TargetServer
                    $PSCmdLResult = Invoke-Expression $PSCmdL
                }

                if (-not [String]::IsNullOrEmpty($TransformationFunction))
                {
                    if ($TransformationForeach)
                    {
                        $ExecutionForEach = @()
                        $intMax = $PSCmdLResult.Count
                        $inc = 0
                        foreach ($resultObject in $PSCmdLResult)
                        {
                            $inc++
                            Write-LogMessage -Message ("`tTransform Foreach $inc/$intMax - $Section - $EntryCmdlet - With function $TransformationFunction")  -NoOutput
                            $ExecutionForEach += Invoke-Expression ("$TransformationFunction -ObjectInput " + '$resultObject')
                        }
                        $Execution = $ExecutionForEach
                    }
                    else {
                        Write-LogMessage -Message ("`tTransform $Section - $EntryCmdlet - With function $TransformationFunction")  -NoOutput
                        $Execution = Invoke-Expression ("$TransformationFunction -ObjectInput " + '$PSCmdLResult')
                    }   
                }
                else 
                {
                    $Execution = $PSCmdLResult
                }

                if ($SaveDate)
                {
                    Write-LogMessage -Message ("`tSave Date $Section - $EntryCmdlet - With attribute $SaveDateAttribute")  -NoOutput
                    $MostRecentObject = $Execution | Select-Object -ExpandProperty $SaveDateAttribute | Sort-Object -Descending | Select-Object -First 1
                    Set-CurrentLaunchTime -SpecificFunction -FunctionName $Section -DateSuffix $MostRecentObject.$SaveDateAttribute
                }

                if (-not [String]::IsNullOrEmpty($select))
                {
                    Write-LogMessage -Message ("`tSelect Attribute $Section - $EntryCmdlet - With list $select")  -NoOutput
                    $Execution = $Execution | Select-Object $select | Sort-Object $select[0]
                }

                if ($null -ne $Execution) {
                    Write-LogMessage -Message ("`t`t Generate Result ...")  -NoOutput
                    $Object = New-Result -Section $Section -PSCmdL $EntryCmdlet -CmdletResult $Execution -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID -ServerProcessed $TargetServer
                }
                else {
                    Write-LogMessage -Message ("`t`t Generate empty result ...")  -NoOutput
                    $Object = New-Result -Section $Section -PSCmdL $EntryCmdlet -EmptyCmdlet -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID -ServerProcessed $TargetServer
                }
            }
            catch {
                $Object = New-Result -Section $Section -PSCmdL $EntryCmdlet -ErrorText $_.Exception -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID -ServerProcessed $TargetServer
                Write-LogMessage -Message ("`t`t Error during data collection - $($_.Exception)")  -NoOutput -Level Error
                
                if ($script:PaginationErrorThreshold -le $PaginationErrorCount)
                {
                    Write-LogMessage -Message ("`t`t`t Error treshold reached at page $EntrySuboutputPage - Error $PaginationErrorCount of $($script:PaginationErrorThreshold) - Stop pagination for the Section")  -NoOutput -Level Error
                    $ProcessLoop = $false
                }
                else {
                    $PaginationErrorCount++
                }

            }

            if ($PaginationExecution -and $Entry.PaginationInformation.PartialDataUpload)
            {
                try {
                    $Goaway = Start-LogBackup -PartialDataRawFormat -RawData $Object -OutputName $EntryOutStream -PartialDataName $EntrySuboutputPage
                }
                catch {
                    $Object = New-Result -Section $Section -PSCmdL $EntryCmdlet -ErrorText $_.Exception -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID -ServerProcessed $TargetServer
                    $Script:Results["Default"] += $Object
                    Write-LogMessage -Message ("`t`t Error during partial data backup, error injected in Default result table - $($_.Exception)")  -NoOutput -Level Error
                }
                
            }
            
            if (-not $PaginationExecution -or $Entry.PaginationInformation.StorePagesInMemory)
            {
                $EntryList[$EntrySuboutputPage] += $Object
            }

            if ($null -eq $Object.count -or $Object.count -lt $ProcessPageSize) { $ProcessLoop = $false }

            $ProcessPage++
            if ($Script:MaxPageNumber -gt 0 -and $ProcessPage -gt $Script:MaxPageNumber) {
                Write-LogMessage -Message ("`t`t Max authorized number of page processed. $ProcessPage / $($Script:MaxPageNumber). Protection activated on page processing")  -NoOutput -Level Warning
                $ProcessLoop = $false
            }

        }
        
        Write-LogMessage -Message ("`tEnd Cmdlet Collection")  -NoOutput

        if (-not $PaginationExecution)
        {
            return $Object
        }
        else {
            return $EntryList
        }
    }

    function New-Result
    {
        Param (
            [Parameter(Mandatory=$True)] [String] $Section,
            [Parameter(Mandatory=$True)] [String] $PSCmdL,
            [Parameter(Mandatory=$True,ParameterSetName = 'Success')] $CmdletResult,
            [Parameter(Mandatory=$True,ParameterSetName = 'Empty')] [switch] $EmptyCmdlet,
            [Parameter(Mandatory=$True,ParameterSetName = 'Failure')] $ErrorText,
            [Parameter(Mandatory=$False)] [String] $ServerProcessed = $null,
            [Parameter(Mandatory=$False)] [String] $EntryDate = $null,
            [Parameter(Mandatory=$False)] [String] $ScriptInstanceID = $null
        )

        if ([String]::IsNullOrEmpty($EntryDate)) { $EntryDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"}

        $ObjectList = @()

        if ($EmptyCmdlet -or -not [String]::IsNullOrEmpty($ErrorText))
        {
            $Object = New-Object PSObject
            $Object | Add-Member Noteproperty -Name GenerationInstanceID -value $ScriptInstanceID
            $Object | Add-Member Noteproperty -Name ESIEnvironment -value $Script:ESIEnvironmentIdentification
            $Object | Add-Member Noteproperty -Name EntryDate -value $EntryDate
            $Object | Add-Member Noteproperty -Name Section -value $Section
            $Object | Add-Member Noteproperty -Name PSCmdL -value $PSCmdL
            $Object | Add-Member Noteproperty -Name Name -value $null
            $Object | Add-Member Noteproperty -Name Identity -value $null
            $Object | Add-Member Noteproperty -Name IdentityString -value $null
            $Object | Add-Member Noteproperty -Name WhenCreated -value $null
            $Object | Add-Member Noteproperty -Name WhenChanged -value $null

            if (-not [String]::IsNullOrEmpty($ServerProcessed))
            {
                $Object | Add-Member Noteproperty -Name ProcessedByServer -value $ServerProcessed
            }
        
            if ($EmptyCmdlet)
            {
                $Object | Add-Member Noteproperty -Name ExecutionResult -value "EmptyResult"
                $Object | Add-Member Noteproperty -Name rawData -value "{'Error':'EmptyResult'}"
            }
            else {
                $Object | Add-Member Noteproperty -Name ExecutionResult -value "Error"
                $ErrorText = $ErrorText -replace "`r`n", " "
                $Object | Add-Member Noteproperty -Name rawData -value "{'Error':'ExecutionException','ErrorDetail':'$ErrorText'}"
            }
            $ObjectList += $Object
        }
        else {
            $inc = 0
            foreach ($Entry in $CmdletResult)
            {
                $inc++

                $NamedEntry = $null
                if ($null -ne $Entry.Name) { $NamedEntry = $Entry.Name}
                elseif ($null -ne $Entry.Identity) { $NamedEntry = $Entry.Identity}
                elseif ($null -ne $Entry.MemberPath) { $NamedEntry = $Entry.MemberPath}

                Write-LogMessage -Message ("`t`t Generate result $inc/$($CmdletResult.count) ...")  -NoOutput
                Write-LogMessage -Message ("`t`t`t Result : ($NamedEntry) ... ") -NoOutput
                $Object = New-Object PSObject
                $Object | Add-Member Noteproperty -Name GenerationInstanceID -value $ScriptInstanceID
                $Object | Add-Member Noteproperty -Name ESIEnvironment -value $Script:ESIEnvironmentIdentification
                $Object | Add-Member Noteproperty -Name EntryDate -value $EntryDate
                $Object | Add-Member Noteproperty -Name Section -value $Section
                $Object | Add-Member Noteproperty -Name PSCmdL -value $PSCmdL
                $Object | Add-Member Noteproperty -Name Name -value $Entry.Name
                $Object | Add-Member Noteproperty -Name Identity -value $Entry.Identity
                $Object | Add-Member Noteproperty -Name IdentityString -value $NamedEntry
                $Object | Add-Member Noteproperty -Name WhenCreated -value $Entry.WhenCreated
                $Object | Add-Member Noteproperty -Name WhenChanged -value $Entry.WhenChanged
                $Object | Add-Member Noteproperty -Name ExecutionResult -value "Success"

                if ($null -ne $Object.IdentityString.Name) {$Object.IdentityString = $Object.IdentityString.Name}

                if (-not [String]::IsNullOrEmpty($ServerProcessed))
                {
                    $Object | Add-Member Noteproperty -Name ProcessedByServer -value $ServerProcessed
                }
            
                # Compile other Attributes
                $Object | Add-Member Noteproperty -Name rawData -value ($Entry | ConvertTo-Json -Compress)

                $ObjectList += $Object
            }
        }

        
        return $ObjectList
    }

#endregion Dynamic Cmdlet Management

#region Multithreading Management

    function New-JobEntry
    {
        Param (
            [Parameter(Mandatory=$True)] $Entry,
            [Parameter(Mandatory=$True)] $Job,
            [Parameter(Mandatory=$True)] $JobName,
            [Parameter(Mandatory=$True)] $RealCmdlet,
            [Parameter(Mandatory=$false)] $TargetServer = "",
            [Parameter(Mandatory=$True)] $PSInstance,
            [Parameter(Mandatory=$true)] $RunspaceName,
            [Parameter(Mandatory=$True)] $EntryOutStream,
            [Parameter(Mandatory=$false)][switch] $IsPaginated,
            [Parameter(Mandatory=$false)] $EntrySuboutputPage = $null
        )

        $Object = New-Object PSObject
        $Object | Add-Member Noteproperty -Name Entry -value $Entry
        $Object | Add-Member Noteproperty -Name Job -value $Job
        $Object | Add-Member Noteproperty -Name JobName -value $JobName
        $Object | Add-Member Noteproperty -Name TargetServer -value $TargetServer
        $Object | Add-Member Noteproperty -Name RealCmdlet -value $RealCmdlet
        $Object | Add-Member Noteproperty -Name PSInstance -value $PSInstance
        $Object | Add-Member Noteproperty -Name RunspaceName -value $RunspaceName
        $Object | Add-Member Noteproperty -Name EntryOutStream -value $EntryOutStream
        $Object | Add-Member Noteproperty -Name IsPaginated -value $IsPaginated
        $Object | Add-Member Noteproperty -Name EntrySuboutputPage -value $EntrySuboutputPage
        return $Object
    }

    Function processParallel
    {
        Param (
            [Parameter(Mandatory=$True)] $Entry,
            $TargetServer = $null,
            [Parameter(Mandatory=$True)] $EntryCmdlet, 
            [Parameter(Mandatory=$True)] $EntryOutStream,
            [Parameter(Mandatory=$false)][switch] $IsPaginated,
            [Parameter(Mandatory=$false)] $EntrySuboutputPage = $null
        )

        $AvailableRunspaceName = WaitAndProcess -FindAvailableSlots

        if ($null -eq $AvailableRunspaceName)
        {
            throw "Impossible to find an available runspace to launch the function"
        }

        $Section = $Entry.Section
        $PSCmdL = $EntryCmdlet

        if ([String]::IsNullOrEmpty($TargetServer))
        {
            Write-LogMessage -Message ("`tLaunch collection of $Section - $PSCmdL - Global Configuration ...") -NoOutput
            $jobName = $section
        }
        else
        {
            Write-LogMessage -Message ("`tLaunch collection of $Section - $PSCmdL - Per Server Configuration for $TargetServer ...") -NoOutput
            $PSCmdL = $PSCmdL -replace "#TargetServer#", $TargetServer
            $jobName = "$section-$TargetServer"
        }


        $Script:RunspaceResults.$AvailableRunspaceName.RunningExecution = $PSCmdL
        $ExecutionCode = {
            $RunspaceResults.$ESIRunspaceName.JobStatus = "Running"
            try
            {
                Write-Host "Launching Expression $($RunspaceResults.$ESIRunspaceName.RunningExecution)"
                $RunspaceResults.$ESIRunspaceName.JobResult = Invoke-Expression $RunspaceResults.$ESIRunspaceName.RunningExecution -ErrorAction Stop

                Write-Host "Updating JobStatus"
                $RunspaceResults.$ESIRunspaceName.JobStatus = "DataAvailable"
            }
            catch {
                Write-Host "Error $_"
                $RunspaceResults.$ESIRunspaceName.JobStatus = "Failed"
                $RunspaceResults.$ESIRunspaceName.JobResult = $_
            }
        }

        $PSinstance = $Script:RunspaceResults.$AvailableRunspaceName.PSInstance
        $PSinstance.AddScript($ExecutionCode) | Out-null

        $Job = $PSinstance.BeginInvoke()
        $script:RunningProcesses += New-JobEntry -Entry $Entry -Job $Job -JobName $jobName -TargetServer $TargetServer -RealCmdlet $PSCmdL -PSInstance $PSinstance -RunspaceName $AvailableRunspaceName -EntryOutStream $EntryOutStream -EntrySuboutputPage $EntrySuboutputPage -IsPaginated:$PaginationExecution
        $Script:RunspaceResults.AvailableRunspaces--
    }

    function WaitAndProcess
    {
        Param(
            [switch] $FindAvailableSlots
        )

        if ($FindAvailableSlots)
        {
            $MaxCount = $script:MaxParallel
        }
        else {$MaxCount = 0}

        $StartAnalysis = Get-Date
        $Timeout = $false

        $Iteration1 = 0
        $Iteration2 = 0

        while ($script:RunningProcesses.count -ge $MaxCount -and $script:RunningProcesses.count -gt 0)
        {
            Write-LogMessage -Message "Max running job raised - $Iteration1 - $Iteration2" -NoOutput
            # Find terminated processes
            for ($i = 0; $i -lt $script:RunningProcesses.count; $i++)
            {
                $RunspaceName = $script:RunningProcesses[$i].RunspaceName
                #$jobStatus = $Script:RunspaceResults.$RunspaceName.JobStatus
                #if ($jobStatus.State -ne "Running")
                if ($script:RunningProcesses[$i].job.IsCompleted)
                {
                    Write-LogMessage -Message "Completed job found. Launch of Transformation and result process on $($script:RunningProcesses[$i].JobName)" -NoOutput
                    $Script:RunspaceResults.$RunspaceName.PSInstance.EndInvoke($script:RunningProcesses[$i].job)
                    processTransformationAndResult -JobEntry $script:RunningProcesses[$i]
                    $script:RunningProcesses.RemoveAt($i)
                    $Script:RunspaceResults.$RunspaceName.JobStatus = "Ready"
                    $Script:RunspaceResults.$RunspaceName.ExecutionHistory += $Script:RunspaceResults.$RunspaceName.RunningExecution
                    $Script:RunspaceResults.$RunspaceName.RunningExecution = $null
                    $Script:RunspaceResults.$RunspaceName.JobResult = $null
                    $Script:RunspaceResults.$RunspaceName.PSInstance.Commands.Clear()
                    $Script:RunspaceResults.$RunspaceName.PSInstance.Streams.ClearStreams()
                    $i--
                    $Script:RunspaceResults.AvailableRunspaces++
                }
            }

            # Wait if condition not satisfied
            if ($script:RunningProcesses.count -ge $MaxCount -and $script:RunningProcesses.count -gt 0)
            {
                Write-LogMessage -Message "Impossible to reduce quantity of running job, wait $($Script:ParralelWaitRunning) seconds to retry." -NoOutput
                Start-Sleep -Seconds $Script:ParralelWaitRunning
                $Iteration1++
            }

            $Iteration2++

            if (((Get-Date) - $StartAnalysis).Minute -gt $Script:ParallelTimeout) {$Timeout = $true; break;}
        }

        if ($Timeout)
        {
            Write-LogMessage -Message "Timeout, entries not processed" -NoOutput
            for ($i = 0; $i -lt $script:RunningProcesses.count; $i++)
            {
                #$job = $script:RunningProcesses[$i]
                $RunspaceName = $script:RunningProcesses[$i].RunspaceName
                $Script:RunspaceResults.$RunspaceName.PSInstance.EndInvoke($script:RunningProcesses[$i].job)
                processTransformationAndResult -JobEntry $script:RunningProcesses[$i] -Timeout
                $script:RunningProcesses.RemoveAt($i)
                $Script:RunspaceResults.$RunspaceName.JobStatus = "Ready"
                $Script:RunspaceResults.$RunspaceName.ExecutionHistory += $Script:RunspaceResults.$RunspaceName.RunningExecution
                $Script:RunspaceResults.$RunspaceName.RunningExecution = $null
                $Script:RunspaceResults.$RunspaceName.JobResult = $null
                $Script:RunspaceResults.$RunspaceName.PSInstance.Commands.Clear()
                $Script:RunspaceResults.$RunspaceName.PSInstance.Streams.ClearStreams()
                $i--
                $Script:RunspaceResults.AvailableRunspaces++
            }
        }

        if ($FindAvailableSlots)
        {
            foreach ($RunpaceKey in $Script:Runspaces.Keys)
            {
                if ($Script:RunspaceResults.$RunpaceKey.JobStatus -like "Ready")
                {
                    if ($Script:Runspaces.$RunpaceKey.RunspaceStateInfo.State -notlike "Opened" -and $Script:Runspaces.$RunpaceKey.RunspaceAvailability -notlike "Available")
                    {
                        Write-LogMessage -Message "Bad runspace found. Removed from available slots. Runspace $RunpaceKey, State $($Script:Runspaces.$RunpaceKey.State) and Availability $($Script:Runspaces.$RunpaceKey.Availability)" -NoOutput
                        $Script:RunspaceResults.$RunpaceKey.JobStatus = "FailedRunspace"
                    }
                    else 
                    {                    
                        Write-LogMessage -Message "Runspace avalaible found : $RunpaceKey" -NoOutput
                        $Script:RunspaceResults.$RunpaceKey.JobStatus = "Assigned"
                        return $RunpaceKey
                    }
                }
            }
        }
    }

    function processTransformationAndResult
    {
        Param(
            [Parameter(Mandatory=$True)] $JobEntry,
            [switch] $Timeout
        )

        $RunspaceName = $JobEntry.RunspaceName
        $PSCmdLResult = $Script:RunspaceResults.$RunspaceName.JobResult
        $jobStatus = $Script:RunspaceResults.$RunspaceName.JobStatus
        #$PSCmdLResultFromJob = $JobEntry.PSInstance.EndInvoke($JobEntry.Job)
        $TransformationForeach = $JobEntry.Entry.TransformationForeach
        $TransformationFunction = $JobEntry.Entry.TransformationFunction
        $Section = $JobEntry.Entry.Section
        $PSCmdL = $JobEntry.RealCmdlet
        $select = $JobEntry.Entry.select
        $TargetServer = $JobEntry.TargetServer
        
        if ($JobEntry.Entry.DateStorageInformation.DateStorageActivated -and $JobEntry.Entry.DateStorageInformation.DateStorageMode -eq "DateFromAttribute")
        {
            $SaveDate = $True
            $DateStorageAttribute = $JobEntry.Entry.DateStorageInformation.DateAttribute
        }
        else
        {
            $SaveDate = $False
        }

        try
        {
            
            Write-LogMessage -Message "##### Instance Results #####"  -NoOutput
            if (-not [string]::IsNullOrEmpty($JobEntry.PSInstance.Streams.Verbose)) 
            {   
                Write-LogMessage -Message "## Verbose" -NoOutput -Level Verbose
                Write-LogMessage -Message $JobEntry.PSInstance.Streams.Verbose -NoOutput -Level Verbose
                Write-LogMessage -Message "## ---- `n" -NoOutput -Level Verbose
            }
            
            if (-not [string]::IsNullOrEmpty($JobEntry.PSInstance.Streams.Information)) 
            { 
                Write-LogMessage -Message "## Information" -NoOutput
                Write-LogMessage -Message $JobEntry.PSInstance.Streams.Information -NoOutput
                Write-LogMessage -Message "## ---- `n" -NoOutput
            }

            if (-not [string]::IsNullOrEmpty($JobEntry.PSInstance.Streams.Warning)) 
            { 
                Write-LogMessage -Message "## Warning" -NoOutput -Level Warning
                Write-LogMessage -Message $JobEntry.PSInstance.Streams.Warning -NoOutput -Level Warning
                Write-LogMessage -Message "## ---- `n" -NoOutput -Level Warning
            }

            if (-not [string]::IsNullOrEmpty($JobEntry.PSInstance.Streams.Error)) 
            { 
                Write-LogMessage -Message "## Error" -NoOutput -Level Warning
                Write-LogMessage -Message $JobEntry.PSInstance.Streams.Error -NoOutput -Level Warning
                Write-LogMessage -Message "## ---- `n" -NoOutput -Level Warning
            }

            if ($Timeout) { throw "Parallel Timeout, $($Script:ParallelTimeout)"}

            if ($jobStatus -eq "Failed")
            {
                throw $PSCmdLResult
            }

            if (-not [String]::IsNullOrEmpty($TransformationFunction))
            {
                if ($TransformationForeach)
                {
                    $ExecutionForEach = @()
                    $intMax = $PSCmdLResult.Count
                    $inc = 0
                    foreach ($resultObject in $PSCmdLResult)
                    {
                        $inc++
                        Write-LogMessage -Message ("`tTransform Foreach $inc/$intMax - $Section - $PSCmdL - With function $TransformationFunction") -NoOutput
                        $ExecutionForEach += Invoke-Expression ("$TransformationFunction -ObjectInput " + '$resultObject')
                    }
                    $Execution = $ExecutionForEach
                }
                else {
                    Write-LogMessage -Message ("`tTransform $Section - $PSCmdL - With function $TransformationFunction") -NoOutput
                    $Execution = Invoke-Expression ("$TransformationFunction -ObjectInput " + '$PSCmdLResult')
                }   
            }
            else 
            {
                $Execution = $PSCmdLResult
            }

            if ($SaveDate)
            {
                Write-LogMessage -Message ("`tSave Date $Section - $PSCmdL - With attribute $DateStorageAttribute")  -NoOutput
                $MostRecentObject = $Execution | Select-Object -ExpandProperty $DateStorageAttribute | Sort-Object -Descending | Select-Object -First 1
                Set-CurrentLaunchTime -SpecificFunction -FunctionName $Section -DateSuffix $MostRecentObject.$DateStorageAttribute
            }

            if (-not [String]::IsNullOrEmpty($select))
            {
                Write-LogMessage -Message ("`tSelect Attribute $Section - $PSCmdL - With list $select") -NoOutput
                $Execution = $Execution | Select-Object $select | Sort-Object $select[0]
            }

            if ($null -ne $Execution) {
                Write-LogMessage -Message ("`t`t Generate Result (Parallel) ... ") -NoOutput
                $Object = New-Result -Section $Section -PSCmdL $PSCmdL -CmdletResult $Execution -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID -ServerProcessed $TargetServer
            }
            else {
                Write-LogMessage -Message ("`t`t Generate empty result ...") -NoOutput
                $Object = New-Result -Section $Section -PSCmdL $PSCmdL -EmptyCmdlet -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID -ServerProcessed $TargetServer
            }
        }
        catch {
            $Object = New-Result -Section $Section -PSCmdL $PSCmdL -ErrorText $_.Exception -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID -ServerProcessed $TargetServer
            Write-LogMessage -Message ("`t`t Error during data collection - $($_.Exception)") -NoOutput -Level Warning
        }

        if ($JobEntry.IsPaginated -eq $true)
        {
            if ($JobEntry.Entry.PaginationInformation)
            {
                if ($JobEntry.Entry.PaginationInformation.PartialDataUpload)
                {
                    $Script:Results[$JobEntry.EntryOutStream][$EntrySuboutputPage] += $Object
                    Start-LogBackup -PartialData -PartialDataName $EntrySuboutputPage  -OutputName $JobEntry.EntryOutStream
                    if (-not $JobEntry.Entry.PaginationInformation.StorePagesInMemory) {$Script:Results[$JobEntry.EntryOutStream][$EntrySuboutputPage] = $null}
                }
                else {
                    $Script:Results[$JobEntry.EntryOutStream][$EntrySuboutputPage] += $Object
                }
                
            }
        }
        else {
            $Script:Results[$JobEntry.EntryOutStream] += $Object
        }
        
    }
        
    function CreateRunspaces
    {
        Param(
            $NumberRunspace
        )
        
        $Script:RunspaceResults = [hashtable]::Synchronized(@{})
        $Script:RunspaceResults.AvailableRunspaces = 0

        $JobList = @()
        Write-Host "Launching Runspace creation ..."

        for ($i = 0; $i -lt $NumberRunspace; $i++)
        {
            
            $RunspaceName = "Runspace$i"
            Write-Host "Creation of Runspace $RunspaceName"

            $iss = [InitialSessionState]::CreateDefault()
            $iss.ApartmentState = "STA"
            $iss.ThreadOptions = "ReuseThread"
            $iss.ImportPSModule("$($Script:DefaultExchangeServerBinPath)\RemoteExchange.ps1")
            
            $Script:RunspaceResults.$RunspaceName = New-Object PSObject
            $Script:RunspaceResults.$RunspaceName | Add-Member Noteproperty -Name JobResult -value $Null
            $Script:RunspaceResults.$RunspaceName | Add-Member Noteproperty -Name JobStatus -value "Ready"
            $Script:RunspaceResults.$RunspaceName | Add-Member Noteproperty -Name ExecutionHistory -value @()
            $Script:RunspaceResults.$RunspaceName | Add-Member Noteproperty -Name RunningExecution -value $null
            $Script:RunspaceResults.$RunspaceName | Add-Member Noteproperty -Name PSInstance -value $null
            
            $Script:Runspaces.$RunspaceName = [runspacefactory]::CreateRunspace($iss)
            $Script:Runspaces.$RunspaceName.ApartmentState = "STA"
            $Script:Runspaces.$RunspaceName.ThreadOptions = "ReuseThread"
            $Script:Runspaces.$RunspaceName.Open()
            $Script:Runspaces.$RunspaceName.SessionStateProxy.SetVariable("ESIRunspaceName",$RunspaceName)
            $Script:Runspaces.$RunspaceName.SessionStateProxy.SetVariable("RunspaceResults",$Script:RunspaceResults)
            
            $PSinstance = [powershell]::Create().AddScript($Script:ExchangeStartingCode)
            $PSinstance.Runspace = $Script:Runspaces.$RunspaceName

            $Script:RunspaceResults.$RunspaceName.PSInstance = $PSinstance

            $JobList += @{"PSInstance"=$PSinstance; "Job"=$PSinstance.BeginInvoke(); "Finished"=$false}
        }

        $Iteration = 0
        $IsFinished = $false

        Write-Host "Monitoring Runspace creation ..."
        while (-not $IsFinished)
        {
            $Running = $false
            foreach ($job in $JobList)
            {
                if (-not $job.Finished -and -not $job.Job.IsCompleted)
                {
                    $running = $true;
                    continue
                }
                else {
                    
                    if (-not $job.Finished) 
                    { 
                        $Script:RunspaceResults.AvailableRunspaces++ 
                    
                        $job.PSInstance.EndInvoke($job.Job)
                        $job.PSInstance.Commands.Clear()
                        $job.PSInstance.Streams.ClearStreams()
                        $job.Finished=$true
                    }
                }
            }

            if (-not $Running) { $IsFinished = $true; break;}

            if ($Iteration -gt 100) {
                throw "Impossible to create Runspaces after 1000 seconds"
            }
            
            Write-Host "Runspace creation running, waiting 10 seconds ... "
            Start-Sleep -Seconds 10
            $Iteration++
        }

        Write-Host "$NumberRunspace Runspaces created"
    }

    function CloseRunspaces
    {
        foreach ($RunKey in $Script:Runspaces.Keys)
        {
            $Script:RunspaceResults.$RunKey.PSInstance.Dispose()

            $Script:Runspaces[$RunKey].Close()
            $Script:Runspaces[$RunKey].Dispose()
        }
    }

#endregion Multithreading Management

#region Business Functions

    #Retrieve group member, retrieve information for local user, call Function GetInfo and GetAllData
    Function GetDetails
    {
        Param(
            $TargetObject,
            $Level,
            $ParentgroupI
        )

        $MyObject = new-Object PSCustomObject
        $MyObject | Add-Member -MemberType NoteProperty -Name "Parentgroup" -Value $ParentgroupI
        $MyObject | Add-Member -MemberType NoteProperty -Name "Level" -Value $Level
        $MyObject | Add-Member -MemberType NoteProperty -Name "ObjectClass" -Value $TargetObject.objectClass
        $MyObject | Add-Member -MemberType NoteProperty -Name "MemberPath" -Value $TargetObject.Name
        $MyObject | Add-Member -MemberType NoteProperty -Name "ObjectGuid" -Value $TargetObject.ObjectGuid
        if ($TargetObject.objectClass -like "User")
        {
            try {
                $DN=[string]$TargetObject
                if ($script:GUserArray.keys -notcontains $DN)
                {
                    try {
                        $User = Get-ADUser $TargetObject.SAMAccountName -server ($DN.Substring($dn.IndexOf("DC=")) -replace ",DC=","." -replace "DC=") -Properties SamAccountName,Name,GivenName,Enabled,homemdb,LastLogonDate,PasswordLastSet,DistinguishedName,CanonicalName,UserPrincipalName | Select-Object SamAccountName,Name,GivenName,Enabled,homemdb,LastLogonDate,PasswordLastSet,DistinguishedName,CanonicalName,UserPrincipalName
                    }
                    catch {
                        Write-LogMessage -Message "Impossible to retrive user $($TargetObject.SAMAccountName), try without homemdb" -NoOutput -Level Warning
                        $User = Get-ADUser $TargetObject.SAMAccountName -server ($DN.Substring($dn.IndexOf("DC=")) -replace ",DC=","." -replace "DC=") -Properties SamAccountName,Name,GivenName,Enabled,LastLogonDate,PasswordLastSet,DistinguishedName,CanonicalName,UserPrincipalName | Select-Object SamAccountName,Name,GivenName,Enabled,homemdb,LastLogonDate,PasswordLastSet,DistinguishedName,CanonicalName,UserPrincipalName
                    
                    }
                    If ($Null -ne $User.homeMDB)
                    {
                        $HasMbx = "True"
                    }
                    Else
                    {
                        $HasMbx = "False"
                    }
                    
                    $script:GUserArray[$User.DistinguishedName] = @{
                            UDN = $User.DistinguishedName
                            USamAccountName = $User.SamAccountName
                            ULastLogonDate = $User.LastLogonDate
                            UPasswordLastSet = $User.PasswordLastSet
                            UEnabled = $User.Enabled
                            UHasMbx=$HasMbx
                            UCanonicalName = $User.CanonicalName
                            UUPN = $User.UserPrincipalName
                        }
                }
                $MyObject | Add-Member -MemberType NoteProperty -Name "DN" -Value $script:GUserArray[$DN].UDN
                $MyObject | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $script:GUserArray[$DN].ULastLogonDate
                $MyObject | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $script:GUserArray[$DN].UPasswordLastSet
                $MyObject | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $script:GUserArray[$DN].UEnabled
                $MyObject | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $script:GUserArray[$DN].USamAccountName
                $MyObject | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $script:GUserArray[$DN].UCanonicalName
                $MyObject | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $script:GUserArray[$DN].UUPN
                $MyObject | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $script:GUserArray[$DN].UHasMbx
                # Has to be NULL
                $MyObject | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
            }
            catch {
                Write-LogMessage -Message "Impossible to retrive user $($TargetObject.SAMAccountName), bad request" -NoOutput -Level Warning

                $tdomain = $DN.Substring($dn.IndexOf("DC=")) -replace ",DC=","." -replace "DC="
                $MyObject | Add-Member -MemberType NoteProperty -Name "DN" -Value "Impossible to retrieve the user, unable to read domain $tdomain"
                $MyObject | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $TargetObject.SAMAccountName
                $MyObject | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $null
                # Has to be NULL
                $MyObject | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
            }
        }
        elseif ($TargetObject.objectClass -like "Group")
        {
            $MyObject | Add-Member -MemberType NoteProperty -Name "Members" -Value $null

            # Has to be NULL
            $MyObject | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "DN" -Value $null
        }
        else
        {
            # Has to be NULL
            $MyObject | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "DN" -Value $null
        }
        return $MyObject
    }

    #Retrieve group member

    function Get-ESIADGroupMember
    {
        Param (
            $Identity,
            $Server
        )

        return (GetMember -TargetName $Identity -dnsrvobj $Server)
    }

    Function GetMember
    {
        Param (
            $TargetObject,
            $TargetName,
            $dnsrvobj
        )

        if (-not [String]::IsNullOrEmpty($TargetName))
        {
            $TargetSamAccountName = $TargetName
            $DN="BySamAccountName-$TargetName"
        }
        else {
            $TargetSamAccountName = $TargetObject.SamAccountName 
            $DN=[string]$TargetObject
        }
 
        if ($script:GGroupArray.keys -notcontains $DN)
        {
            try {
                $list = Get-ADGroupMember $TargetSamAccountName -server $dnsrvobj
            }
            catch {
                Write-LogMessage -Message "Impossible to retreive member using Get-ADGroupMember for $TargetSamAccountName" -NoOutput -Level Warning
                if ($dnsrvobj -notmatch "3268" -and $dnsrvobj -notmatch "3269")
                {
                    $gctarget = $dnsrvobj + ":3268"
                }
                else { $gctarget = $dnsrvobj }
                
                $Templist = (Get-ADGroup $TargetSamAccountName -server $dnsrvobj).Members
                $list = @()
                foreach ($obj in $TempList)
                {
                    try {
                        $list += Get-ADObject $obj -Server $gctarget
                    }
                    catch {
                        Write-LogMessage -Message "Impossible to get Object Info on $gctarget for $obj" -NoOutput -Level Warning
                
                        $list += [PSCustomObject]@{
                            Name = $obj
                            DistinguishedName = $obj
                        }
                    }
                }
            }
            $script:GGroupArray[$DN]=$list
        }
        else {
            $list = $script:GGroupArray[$DN]
        }

        return $List
    }

    #Create the MemberPath value
    Function GenerateMembersDetail
    {
        Param (
            $ResultTable,
            $Name
        )

        foreach ($Result in $ResultTable)
        {
            $Result.MemberPath = $Name + "\" + $Result.MemberPath
        }
        return $ResultTable
    }

    #Call Function to retrieve group member and user spceific information and Function to create the MemberPath
    Function GetInfo
    {
        Param (
            $ObjectInput,
            $Level = $null,
            $parentgroup,
            $DirectParentDN,
            [switch] $loop
        )

        if ($null -ne $level)
        {
            $Level++
        }
        else
        {
            $level = 0
            $entry = $ObjectInput.DistinguishedName
            $DN=($entry.Substring($entry.IndexOf("DC=")))
            $parentgroup =  ($entry.split(","))[0].replace("CN=","")
        }

        $InfoTable = @()

        #Call Function to create member path parameter
        $InfoResult = GetDetails -TargetObject $ObjectInput -Level $Level -Parentgroup $parentgroup
        $InfoTable += $InfoResult

        if ($loop)
        {
            Write-LogMessage -Message "`t`t Loop detected between $DirectParentDN and $($ObjectInput.DistinguishedName)" -Level Warning -NoOutput
            $InfoResult.MemberPath +=  " - LOOP DETECTED"
        }

        if ($ObjectInput.ObjectClass -like "Group" -and -not $loop)
        {
            $InfoResult.DN = $ObjectInput.DistinguishedName

            #Call Function to retrieve group content
            $dnsrv= (($ObjectInput.DistinguishedName).Substring(($ObjectInput.DistinguishedName).IndexOf("DC=")) -replace ",DC=","." -replace "DC=")
            $list = GetMember -TargetObject $ObjectInput -dnsrvobj $dnsrv

            Write-LogMessage -Message "`t`t Verify Members list size less than $($Script:MaximalSentinelFieldMemberListSizeKb)-5" -Level Verbose -NoOutput
            
            if ($null -ne $list)
            {
                $ResultInjsonFormat = $list | ConvertTo-Json -Compress
                $ResultLength = [System.Text.Encoding]::UTF8.GetBytes($ResultInjsonFormat).Length
                
                $contentDivision = [math]::Ceiling($ResultLength / (($Script:MaximalSentinelFieldMemberListSizeKb - 5) *1024))
            }
            else { $contentDivision = 1 }

            if ($contentDivision -le 1) { $InfoResult.Members = $list }
            else 
            { 
                $InfoResult.Members = "TOO Many Members for tracking them in Log Analytics member field. 30Kb. Find members by MemberPath" 
                Write-LogMessage -Message "`t`t TOO Many Members for tracking them in Log Analytics member field. Size : $ResultLength - Content Division : $contentDivision" -Level Warning -NoOutput
            }

            if ($level -gt 50)
            {
                Write-LogMessage -Message "`t`t LEVEL 50, Possible Loop between groups." -Level Warning -NoOutput
                $InfoResult.MemberPath +=  " - Possible Loop on groups"
            }
            else {
                foreach ($member in $list)
                {
                    if ($member.DistinguishedName -like $DirectParentDN)
                    {
                        $ResultTable = GetInfo -ObjectInput $member -Level $Level -Parentgroup $parentgroup -DirectParentDN $ObjectInput.DistinguishedName -loop
                        $ResultTable = GenerateMembersDetail -ResultTable $ResultTable -Name $ObjectInput.Name
                        $InfoTable += $ResultTable
                    }
                    else {
                        $ResultTable = GetInfo -ObjectInput $member -Level $Level -Parentgroup $parentgroup -DirectParentDN $ObjectInput.DistinguishedName
                        $ResultTable = GenerateMembersDetail -ResultTable $ResultTable -Name $ObjectInput.Name
                        $InfoTable += $ResultTable
                    }
                }
            }
        }

        if ($ObjectInput.ObjectClass -like "ManagementRoleAssignment")
        {         
            #Call Function to retrieve group content
            $dnsrv= $ObjectInput.RoleAssignee.DomainId
            $AssigneeObject = Get-ADObject $ObjectInput.RoleAssignee.DistinguishedName -Server $dnsrv -Properties SAMAccountName
            $ResultTable = GetInfo -ObjectInput $AssigneeObject -Level $Level -Parentgroup $ObjectInput.Name -DirectParentDN $ObjectInput.DistinguishedName
            $ResultTable = GenerateMembersDetail -ResultTable $ResultTable -Name $ObjectInput.Name -ParentgroupI $parentgroup
            $InfoTable += $ResultTable
        }

        return $InfoTable
    }

    Function GetO365Details
    {
        Param(
            $TargetObject,
            $Level,
            $ParentgroupI
        )

        $MyObject = new-Object PSCustomObject
        $MyObject | Add-Member -MemberType NoteProperty -Name "Parentgroup" -Value $ParentgroupI
        $MyObject | Add-Member -MemberType NoteProperty -Name "Level" -Value $Level
        $MyObject | Add-Member -MemberType NoteProperty -Name "ObjectClass" -Value $TargetObject.objectClass
        $MyObject | Add-Member -MemberType NoteProperty -Name "MemberPath" -Value $TargetObject.Name
        $MyObject | Add-Member -MemberType NoteProperty -Name "ObjectGuid" -Value $TargetObject.ObjectGuid
        if ($TargetObject.AdditionalProperties.'@odata.type' -like "#microsoft.graph.user")
        {
            try {
                $Id=$TargetObject.Id
                if ($script:GUserArray.keys -notcontains $Id)
                {
                    try {
                        $User = Get-MgUser -UserId $TargetObject.Id -Property AccountEnabled,UserPrincipalName, LastPasswordChangeDateTime, Mail, MailNickname, OnPremisesDistinguishedName, OnPremisesSamAccountName, PasswordPolicies, PasswordProfile, UserType, SignInActivity
                    }
                    catch {
                        Write-LogMessage -Message "Impossible to retreive user $($TargetObject.Id)" -NoOutput -Level Warning
                    }
					
					$UserExchangeInfo = Get-Recipient $User.UserPrincipalName
					
                    If ($UserExchangeInfo.RecipientType -like "*Mailbox")
                    {
                        $HasMbx = "True"
                    }
                    Else
                    {
                        $HasMbx = "False"
                    }
                    
                    $script:GUserArray[$User.Id] = @{
                            UDN = $User.OnPremisesDistinguishedName
                            USamAccountName = $User.MailNickname
                            ULastLogonDate = $User.SignInActivity.LastSignInDateTime
                            UPasswordLastSet = $User.LastPasswordChangeDateTime
                            UEnabled = $User.AccountEnabled
                            UHasMbx=$HasMbx
                            UUPN = $User.UserPrincipalName
							UserType = $User.UserType
                        }
                }
                $MyObject | Add-Member -MemberType NoteProperty -Name "DN" -Value $script:GUserArray[$DN].UDN
                $MyObject | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $script:GUserArray[$DN].ULastLogonDate
                $MyObject | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $script:GUserArray[$DN].UPasswordLastSet
                $MyObject | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $script:GUserArray[$DN].UEnabled
                $MyObject | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $script:GUserArray[$DN].USamAccountName
                $MyObject | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $script:GUserArray[$DN].UUPN
                $MyObject | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $script:GUserArray[$DN].UHasMbx
                # Has to be NULL
                $MyObject | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
            }
            catch {
                Write-LogMessage -Message "Impossible to retrive user $($TargetObject.AdditionalProperties.userPrincipalName), bad request" -NoOutput -Level Warning

                $MyObject | Add-Member -MemberType NoteProperty -Name "DN" -Value "Impossible to retrieve the user, unable to read id $($TargetObject.Id)"
                $MyObject | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
                $MyObject | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $TargetObject.AdditionalProperties.userPrincipalName
                $MyObject | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $null
                # Has to be NULL
                $MyObject | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
            }
        }
        elseif ($TargetObject.AdditionalProperties.'@odata.type' -like "#microsoft.graph.group")
        {
            $MyObject | Add-Member -MemberType NoteProperty -Name "Members" -Value $null

            # Has to be NULL
            $MyObject | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "DN" -Value $null
        }
        else
        {
            # Has to be NULL
            $MyObject | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $null
            $MyObject | Add-Member -MemberType NoteProperty -Name "DN" -Value $null
        }
        return $MyObject
    }

    #Call Function to retrieve group member and user spceific information and Function to create the MemberPath
    Function GetO365Info
    {
        Param (
            $ObjectInput,
            $Level = $null,
            $parentgroup
        )

        if ($null -ne $level)
        {
            $Level++
        }
        else
        {
            $level = 0
            $entry = $ObjectInput.Id
            $parentgroup =  "AzureAD"
        }

        $InfoTable = @()

        #Call Function to create member path parameter
        $InfoResult = GetO365Details -TargetObject $ObjectInput -Level $Level -Parentgroup $parentgroup
        $InfoTable += $InfoResult
        if ($ObjectInput.Gettype().Name -like "MicrosoftGraphGroup1" -or $ObjectInput.AdditionalProperties.'@odata.type' -like "#microsoft.graph.group")
        {
            #Call Function to retrieve group content
            $list = Get-MgGroupMember -GroupId $ObjectInput.Id

            Write-LogMessage -Message "`t`t Verify Members list size less than $($Script:MaximalSentinelFieldMemberListSizeKb)-5" -Level Verbose -NoOutput
            $ResultInjsonFormat = $list | ConvertTo-Json -Compress
            $ResultLength = [System.Text.Encoding]::UTF8.GetBytes($ResultInjsonFormat).Length

            $contentDivision = [math]::Ceiling($ResultLength / (($Script:MaximalSentinelFieldMemberListSizeKb - 5) *1024))

            if ($contentDivision -le 1) { $InfoResult.Members = $list }
            else 
            { 
                $InfoResult.Members = "TOO Many Members for tracking them in Log Analytics member field. 30Kb. Find members by MemberPath" 
                Write-LogMessage -Message "`t`t TOO Many Members for tracking them in Log Analytics member field. Size : $ResultLength - Content Division : $contentDivision" -Level Warning -NoOutput
            }

            foreach ($member in $list)
            {
                $ResultTable = GetO365Info -ObjectInput $member -Level $Level -Parentgroup $parentgroup
                $ResultTable = GenerateMembersDetail -ResultTable $ResultTable -Name $ObjectInput.DisplayName
                $InfoTable += $ResultTable
            }
        }

        return $InfoTable
    }

    Function GetWMILocalAdmins
    {
        Param (
        $ObjectInput
        )

        $TheObject = $ObjectInput.List
        $srv = $ObjectInput.Srv

        $ObjectList = @()

        $TheObject2 = new-Object PSCustomObject
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "Parentgroup" -Value "$srv\Local Administrators"
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "Level" -Value 0
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "ObjectClass" -Value "Local Group"
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "MemberPath" -Value "Local Administrators"
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "ObjectGuid" -Value $null
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "DN" -Value $null
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "Members" -Value $ObjectInput.List
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $null
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $null
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $null
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $null
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value "Administrators"
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
        $TheObject2 | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $null

        $ObjectList += $TheObject2

        foreach ($entry in $TheObject)
        {
            if($entry.split(";")[0] -like "*Win32_UserAccount*" -and $entry.split(";")[1] -like "$srv\*"  )
            {
                #For Local User in the Local Administrators group
                $TheObject2 = new-Object PSCustomObject
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "Parentgroup" -Value "$srv\Local Administrators"
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "Level" -Value 1
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "ObjectClass" -Value "Local User"
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "ObjectGuid" -Value $null
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "MemberPath" -Value ($entry.split(";"))[1].split("\")[1]
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "DN" -Value $null
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $null
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $null
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $null
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $null
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value ($entry.split(";"))[1]
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $null
                $TheObject2 | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $null
            }
            elseif($entry.split(";")[0] -like "*Win32_UserAccount*")
            {
                $DomUser=$entry.split(";")[1]
                if ($ht_domains.Keys -contains $DomUser.Split("\")[0])
                {
                    $DN = ($script:GUserArray.GetEnumerator() | Where-Object{$_.value.USamAccountName -like $entry.split(";")[1].split("\")[1]}).key
                    if ($script:GUserArray.keys -notcontains $DN)
                    {
                        $User = Get-ADUser $DomUser.Split("\")[1] -Server $script:ht_domains[$DomUser.Split("\")[0]].DCFQDN -Properties SamAccountName,Name,GivenName,Enabled,homemdb,LastLogonDate,PasswordLastSet,DistinguishedName,CanonicalName,UserPrincipalName | Select-Object SamAccountName,Name,GivenName,Enabled,homemdb,LastLogonDate,PasswordLastSet,DistinguishedName,CanonicalName,UserPrincipalName
                        If ($Null -ne $User.homeMDB)
                        {
                            $HasMbx = "True"
                        }
                        Else
                        {
                            $HasMbx = "False"
                        }
                        
                        $script:GUserArray[$User.DistinguishedName] = @{
                                UDN = $User.DistinguishedName
                                USamAccountName = $User.SamAccountName
                                ULastLogonDate = $User.LastLogonDate
                                UPasswordLastSet = $User.PasswordLastSet
                                UEnabled = $User.Enabled
                                UHasMbx=$HasMbx
                                UCanonicalName = $User.CanonicalName
                                UUPN = $User.UserPrincipalName
                            }
                        $DN = $User.DistinguishedName
                    }
                    $TheObject2 = new-Object PSCustomObject
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "Parentgroup" -Value "$srv\Local Administrators"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "Level" -Value 1
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "ObjectClass" -Value "user"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "MemberPath" -Value ($entry.split(";"))[1]
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value $script:GUserArray[$DN].ULastLogonDate
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value $script:GUserArray[$DN].UPasswordLastSet
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "Enabled" -Value $script:GUserArray[$DN].UEnabled
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value $script:GUserArray[$DN].UHasMbx
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "DN" -Value $script:GUserArray[$DN].UDN
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value $script:GUserArray[$DN].USamAccountName
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value $script:GUserArray[$DN].UCanonicalName
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value $script:GUserArray[$DN].UUPN
                }
                else
                {
                    #User from another Forest, Information can't be retrieve
                    $TheObject2 = new-Object PSCustomObject
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "Parentgroup" -Value "$srv\Local Administrators"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "Level" -Value 1
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "ObjectClass" -Value "Trusted Forest User"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "MemberPath" -Value ($entry.split(";"))[1].split("\")[1]
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "DN" -Value $null
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "Members" -Value $null
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "LastLogon" -Value "N/A"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "LastPwdSet" -Value "N/A"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "Enabled" -Value "N/A"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "HasMbx" -Value "N/A"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "SamAccountName" -Value "N/A"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "CanonicalName" -Value "N/A"
                    $TheObject2 | Add-Member -MemberType NoteProperty -Name "UserPrincipalName" -Value "N/A"
                }
            }
            else {
                $dn=(Get-ADDomain ($entry.split(";"))[1].split("\")[0]).DistinguishedName
                $entry=($entry.split(";"))[1].split("\")[1]
                $DNobj=($DN.Substring($dn.IndexOf("DC=")) -replace ",DC=","." -replace "DC=")
                $GroupObject = Get-ADGroup -filter 'Name -eq $entry' -server $DNobj
                $TheObject2 = GetInfo -ObjectInput $GroupObject -Level 0 -Parentgroup "$srv\Local Administrators"
            }
            $ObjectList += $TheObject2
        }

        return $ObjectList
    }

#Endregion Business Functions

#region Configuration Loading

    function Check-ScriptUpdate
    {
        $script:VersionNotToDate = $false

        if ($script:UpdateVersionCheckingDeactivated) 
        { 
            Write-LogMessage "Update Version Checking Deactivated" -Level Info 
        }
        
        $CurrentVersion = $ESICollectorCurrentVersion
        
        [int] $InternalVersionCurentFile = $CurrentVersion -replace "\.",""
        if ($InternalVersionCurentFile -lt 1000) {
            $InternalVersionCurentFile = $InternalVersionCurentFile * 10
        }

        try {
            $VersionTracking = Invoke-ESIWebRequest -Uri "https://aka.ms/ESICollectorVersionVerification"

            $VersionTracking = $VersionTracking | ConvertFrom-Json

            [int] $InternalTargetVersion = $VersionTracking.LatestVersion -replace "\.",""

            if ($InternalTargetVersion -gt $InternalVersionCurentFile) {
                $script:VersionNotToDateMessage = "Current version : $CurrentVersion - New version : $($VersionTracking.LatestVersion)"
                Write-LogMessage "********** New version of the script available. $($script:VersionNotToDateMessage)" -Level Warning
                $script:VersionNotToDate = $true
            }
            else
            {
                Write-LogMessage "Script is up to date. Version : $CurrentVersion" -Level Info
            }

        }
        catch {
            Write-LogMessage "Unable to get version tracking file from https://aka.ms/ESICollectorVersionVerification. Exception $($_.Exception); Fatal Error" -Level Error
            return $null
        }
    }

    function LoadConfiguration 
    {
        Param (
            $configurationFile,
            [switch] $VariableFromAzureAutomation,
            $ReceivedTenantName,
            $InstanceName = "Default"
        )

        try
        {
            if ($VariableFromAzureAutomation)
            {
                $jsonConfig = Get-AutomationVariable -Name GlobalConfiguration -ErrorAction Stop
                $jsonConfig = $jsonConfig | ConvertFrom-Json
                $script:TenantName = Get-AutomationVariable -Name TenantName -ErrorAction Stop
            }
            else {
                $jsonConfig = Get-Content $configurationFile | ConvertFrom-Json
                if (-not [String]::IsNullOrEmpty($ReceivedTenantName)) { $script:TenantName = $ReceivedTenantName}
                else { $script:TenantName = $Global:TenantName }
            }

            #Verify that the version of configuration file is greater than supported version
            if ($jsonConfig.SolutionMetadata.JSonVersion -lt $script:SupportedConfigurationVersion)
            {
                Write-LogMessage -Message "Configuration file version $($jsonConfig.SolutionMetadata.JSonVersion) is outdated. Features could not work correctly. Supported version is $($script:SupportedConfigurationVersion)" -Level Warning
            }
                
            [int] $Script:ParallelTimeout = $jsonConfig.Global.ParallelTimeoutMinutes # Minutes
            [int] $script:MaxParallel = $jsonConfig.Global.MaxParallelRunningJobs
            $Script:ParallelProcessPerServer = [Convert]::ToBoolean($jsonConfig.Global.PerServerParallelProcessing)
            $Script:GlobalParallelProcess = [Convert]::ToBoolean($jsonConfig.Global.GlobalParallelProcessing)
            [int] $Script:DefaultDurationTracking = $jsonConfig.Global.DefaultDurationTracking
            $Script:ESIProcessingType = $jsonConfig.Global.ESIProcessingType
            if ($Script:ESIProcessingType -notin ('Online', 'On-Premises'))
            {
                Write-LogMessage -Message "Processing $($Script:ESIProcessingType) not in authorized list : 'Online', 'On-Premises'. Unable to continue" -Level Error
                throw "Processing $($Script:ESIProcessingType) not in authorized list : 'Online', 'On-Premises', 'All'. Unable to continue"
            }
            if ($Script:ESIProcessingType -like "Online" -and [String]::IsNullOrEmpty($script:TenantName)) 
            { 
                Write-LogMessage -Message 'No Tenant Name in an Online Configuration. Tenant name is mandatory. By passing as parameter to the script of setting global value $Global:TenantName'  -Level Error
                throw 'No Tenant Name in an Online Configuration. Tenant name is mandatory. By passing as parameter to the script of setting global value $Global:TenantName' 
            }

            $Script:ESIEnvironmentIdentification = $jsonConfig.Global.EnvironmentIdentification
            if (-not [String]::IsNullOrEmpty($script:TenantName) -and [String]::IsNullOrEmpty($Script:ESIEnvironmentIdentification))
            {
                $Script:ESIEnvironmentIdentification = $script:TenantName
            }

            # Verify that $Script:ESIEnvironmentIdentification is not a GUID. If it's the case, add "GUID-" at the beginning of the string
            $testGuid = [System.Guid]::Empty
            if
            (
                [Guid]::TryParse($Script:ESIEnvironmentIdentification, [ref]$testGuid)
            )
            {
                $Script:ESIEnvironmentIdentification = "GUID-" + $Script:ESIEnvironmentIdentification
            }

            if (($VariableFromAzureAutomation -or $Script:ESIProcessingType -like "Online") -and ($Script:ParallelProcessPerServer -or $Script:GlobalParallelProcess))
            {
                Write-LogMessage -Level Warning -Message "Impossible to use Multithreading in an Azure Automation or for Exchange Online. Multithreading automatically deactivated"
                $Script:ParallelProcessPerServer = $false
                $Script:GlobalParallelProcess = $false
            }

            if ([string]::IsNullOrEmpty($jsonConfig.Output.DefaultOutputFile) -and -not $Global:isRunbook) {throw "No Output file in config, mandatory"} else {$Script:outputpath = $jsonConfig.Output.DefaultOutputFile}
            if (-not [string]::IsNullOrEmpty($jsonConfig.Output.ExportDomainsInformation))
            {
                $Script:ExportDomainsInformation = [Convert]::ToBoolean($jsonConfig.Output.ExportDomainsInformation)
            }
            else
            {
                $Script:ExportDomainsInformation = $false
            }


            [int] $Script:ParralelWaitRunning
            if ($null -eq $jsonConfig.Advanced.ParralelWaitRunning) {[int] $Script:ParralelWaitRunning = 60} else {[int] $Script:ParralelWaitRunning = $jsonConfig.Advanced.ParralelWaitRunning}
            if ($null -eq $jsonConfig.Advanced.ParralelPingWaitRunning) {[int] $Script:ParralelPingWaitRunning = $Script:ParralelWaitRunning} else {[int] $Script:ParralelPingWaitRunning = $jsonConfig.Advanced.ParralelPingWaitRunning}

            if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.OnlyExplicitActivation)) 
            {   
                $Script:OnlyExplicitActivation = [Convert]::ToBoolean($jsonConfig.Advanced.OnlyExplicitActivation)
            }
            else { $Script:OnlyExplicitActivation = $false }

            if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.Beta)) 
            {   
                $Script:BetaActivated = [Convert]::ToBoolean($jsonConfig.Advanced.Beta)
            }
            else { $Script:BetaActivated = $false }

            if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.BypassServerAvailabilityTest)) 
            {   
                $Script:BypassServerAvailabilityTest = [Convert]::ToBoolean($jsonConfig.Advanced.BypassServerAvailabilityTest)
            }
            else { $Script:BypassServerAvailabilityTest = $false }

            if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.ExplicitExchangeServerList)) 
            {   
                $Script:ExplicitExchangeServerList = $jsonConfig.Advanced.ExplicitExchangeServerList
            }
            else { $Script:ExplicitExchangeServerList = $null }

            if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.ExchangeServerBinPath)) 
            {   
                $Script:DefaultExchangeServerBinPath = $jsonConfig.Advanced.ExchangeServerBinPath
            }
            else { $Script:DefaultExchangeServerBinPath = "c:\\Program Files\\Microsoft\\Exchange Server\\V15\\bin" }

            if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.FunctionsListInline)) 
            {   
                $Script:FunctionsListInline = [Convert]::ToBoolean($jsonConfig.Advanced.FunctionsListInline)
            }
            else 
            {  
                if ($Script:ESIProcessingType -like "Online") {$Script:FunctionsListInline = $true } 
                else {$Script:FunctionsListInline = $false}
            }

            if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.FunctionsListWithoutInternet)) 
            {   
                $Script:FunctionsListWithoutInternet = [Convert]::ToBoolean($jsonConfig.Advanced.FunctionsListWithoutInternet)
            }
            else { $Script:FunctionsListWithoutInternet = $true }

            if (-not [String]::IsNullOrEmpty($jsonConfig.Advanced.Useproxy)) {
                $script:Useproxy = [Convert]::ToBoolean($jsonConfig.Advanced.Useproxy)
                if ($Useproxy) { 
                    if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.ProxyUrl)) {$script:ProxyUrl = $jsonConfig.Advanced.ProxyUrl} 
                    else { Throw "URL Proxy is needed when UseProxy is activated"}
                }
            } 
            else {
                $script:Useproxy = $false
            }

            if (-not [string]::IsNullOrEmpty($jsonConfig.Advanced.UpdateVersionCheckingDeactivated)) 
            {   
                $Script:UpdateVersionCheckingDeactivated = [Convert]::ToBoolean($jsonConfig.Advanced.UpdateVersionCheckingDeactivated)
            }
            else { $Script:UpdateVersionCheckingDeactivated = $false }

            

            if ($null -eq $jsonConfig.Advanced.MaximalSentinelPacketSizeMb) {
                $script:MaximalSentinelPacketSizeMb = 31.9
            } 
            else {
                if ($jsonConfig.Advanced.MaximalSentinelPacketSizeMb -ge 32)
                {
                    Write-LogMessage -Message "Packet size $($jsonConfig.Advanced.MaximalSentinelPacketSizeMb) greater than 31.9Kb. Maximum size for Sentinel is 31.9Kb."
                    $script:MaximalSentinelPacketSizeMb = 31.9
                }
                else
                {
                    [int] $Script:MaximalSentinelPacketSizeMb = $jsonConfig.Advanced.MaximalSentinelPacketSizeMb - 0.1
                }
            }

            if ($null -eq $jsonConfig.Advanced.PaginationErrorThreshold) {
                $script:PaginationErrorThreshold = 10
            } 
            else {
                if ($jsonConfig.Advanced.PaginationErrorThreshold -ge 100)
                {
                    Write-LogMessage -Message "Pägination error threshold $($jsonConfig.Advanced.PaginationErrorThreshold) greater than 100. Maximum number is 100."
                    $script:PaginationErrorThreshold = 10
                }
                else
                {
                    [int] $Script:PaginationErrorThreshold = $jsonConfig.Advanced.PaginationErrorThreshold
                }
            }

            if ($null -ne $jsonConfig.Advanced.LogVerboseActivated)
            {
                $script:FASTVerboseLevel = [Convert]::ToBoolean($jsonConfig.Advanced.LogVerboseActivated)
            }
            else {$script:FASTVerboseLevel = $true}

            if ($null -ne $jsonConfig.Advanced.DeactivateUDSLogs)
            {
                $script:DeactivateUDSLogs = [Convert]::ToBoolean($jsonConfig.Advanced.DeactivateUDSLogs)
            }
            else {$script:DeactivateUDSLogs = $false}

            if ($null -ne $jsonConfig.Advanced.UDSLogProcessor)
            {
                $script:UDSLogControl = $true
                $script:UDSLogProcessor = @()
                foreach ($entry in $jsonConfig.Advanced.UDSLogProcessor)
                {
                    if ([Convert]::ToBoolean($Entry.Activated))
                    {
                        $LogStorageEntry = New-Object PSObject
                        $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "LogStorageType" -Value $entry.StorageType
                        $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "LogStoragePath" -Value $entry.StoragePath
                        if (-not [String]::IsNullOrEmpty($entry.LogStorageRetentionDays)) { $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "LogStorageRetentionDays" -Value ([Convert]::ToInt32($entry.LogStorageRetentionDays)) }
                        else { $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "LogStorageRetentionDays" -Value 30 }

                        $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "Prefix" -Value $entry.Prefix
                        $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "StorageURL" -Value $entry.StorageURL


                        if (-not [String]::IsNullOrEmpty($entry.StorageAccountName)) { $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "StorageAccountName" -Value $entry.StorageAccountName }
                        if (-not [String]::IsNullOrEmpty($entry.StorageBlobContainer)) { $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "StorageBlobContainer" -Value $entry.StorageBlobContainer }
                        if (-not [String]::IsNullOrEmpty($entry.ConnexionType)) { $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "ConnexionType" -Value $entry.ConnexionType }
                        
                        if ($entry.ConnexionType -like "Certificate")
                        {
                            if ([String]::IsNullOrEmpty($entry.TenantId) -or [String]::IsNullOrEmpty($entry.ApplicationID) -or [String]::IsNullOrEmpty($entry.ApplicationID))
                            {
                                Write-LogMessage -Message "Certificate connexion type selected but missing information. Impossible to continue" -Level Error
                                throw "Certificate connexion type selected but missing information. Impossible to continue"
                            }

                            if (-not [String]::IsNullOrEmpty($entry.TenantId)) { $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "TenantId" -Value $entry.TenantId }
                            if (-not [String]::IsNullOrEmpty($entry.ApplicationID)) { $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "ApplicationID" -Value $entry.ApplicationID }
                            if (-not [String]::IsNullOrEmpty($entry.CertificateThumbprint)) { $LogStorageEntry | Add-Member -MemberType NoteProperty -Name "CertificateThumbprint" -Value $entry.CertificateThumbprint }
                        }

                        $script:UDSLogProcessor += $LogStorageEntry
                    }
                    
                }
            }
            else {$script:UDSLogControl = $false}


            if ($null -ne $jsonConfig.MGGraphAPIConnection) {
                $Script:MGGraphAzureRMCertificate = $jsonConfig.MGGraphAPIConnection.MGGraphAzureRMCertificate
                $Script:MGGraphAzureRMAppId = $jsonConfig.MGGraphAPIConnection.MGGraphAzureRMAppId
            }
            else {
                $Script:MGGraphAzureRMCertificate = "Unknown"
                $Script:MGGraphAzureRMAppId = "Unknown"
            }

            if ($null -ne $jsonConfig.InstanceConfiguration) {
                if ($null -ne $jsonConfig.InstanceConfiguration.$InstanceName)
                {
                    $Script:InstanceConfiguration = New-Object PSObject
                    $Script:InstanceConfiguration | Add-Member Noteproperty -Name InstanceName -value $InstanceName
                    if ($null -eq $jsonConfig.InstanceConfiguration.$InstanceName.All)
                    {
                        Throw "Instance Name $InstanceName needs configuration of 'All' parameter, this is mandatory. Impossible to continue"
                    }
                    else
                    {
                        $InstanceAllValue = [Convert]::ToBoolean($jsonConfig.InstanceConfiguration.$InstanceName.All)
                        if ($InstanceAllValue)
                        {
                            $Script:InstanceConfiguration | Add-Member Noteproperty -Name FileFilterType -value "All"
                            $Script:InstanceConfiguration | Add-Member Noteproperty -Name FileFilterList -value @()
                        }
                        else {
                            if ($Script:FunctionsListWithoutInternet -and $Script:FunctionsListInline)
                            {
                                Throw "For Instance Name $InstanceName selected execution is not compatible with the Audit Function Inline mode. This is mandatory. Impossible to continue"
                            }

                            if ((
                                    $null -eq $jsonConfig.InstanceConfiguration.$InstanceName.SelectedAddons -or 
                                    $jsonConfig.InstanceConfiguration.$InstanceName.SelectedAddons -isnot [array]
                                ) -and 
                                (
                                    $null -eq $jsonConfig.InstanceConfiguration.$InstanceName.FileteredAddons -or 
                                    $jsonConfig.InstanceConfiguration.$InstanceName.FileteredAddons -isnot [array]
                                ))
                            {
                                Throw "Instance Name $InstanceName needs configuration of 'SelectedAddons' parameter or 'FileteredAddons' parameter as 'All' value is False, this is mandatory. Impossible to continue"
                            }

                            $Script:InstanceConfiguration | Add-Member Noteproperty -Name FileFilterType -value "Restricted"

                            if ($null -ne $jsonConfig.InstanceConfiguration.$InstanceName.SelectedAddons -and $jsonConfig.InstanceConfiguration.$InstanceName.SelectedAddons -is [array]) 
                            {
                                $Script:InstanceConfiguration.FileFilterType += "-Filtered"
                                $Script:InstanceConfiguration | Add-Member Noteproperty -Name FileFilterList -value $jsonConfig.InstanceConfiguration.$InstanceName.SelectedAddons
                            }

                            if ($null -ne $jsonConfig.InstanceConfiguration.$InstanceName.FileteredAddons -and $jsonConfig.InstanceConfiguration.$InstanceName.FileteredAddons -is [array])  
                            {
                                $Script:InstanceConfiguration.FileFilterType += "-Ignored"
                                $Script:InstanceConfiguration | Add-Member Noteproperty -Name FileIgnoreList -value $jsonConfig.InstanceConfiguration.$InstanceName.FileteredAddons
                            }
                        }

                        if (-not [String]::IsNullOrEmpty($jsonConfig.InstanceConfiguration.$InstanceName.Category)) {
                            $Script:InstanceConfiguration.FileFilterType += "-Categorized"
                            $Script:InstanceConfiguration | Add-Member Noteproperty -Name Category -value $jsonConfig.InstanceConfiguration.$InstanceName.Category
                        }

                        if (-not [String]::IsNullOrEmpty($jsonConfig.InstanceConfiguration.$InstanceName.Capabilities)) {
                            $Script:InstanceConfiguration | Add-Member Noteproperty -Name Capabilities -value ($jsonConfig.InstanceConfiguration.$InstanceName.Capabilities -split '\|')
                        }

                        if (-not [String]::IsNullOrEmpty($jsonConfig.InstanceConfiguration.$InstanceName.OutputName)) {
                            $Script:InstanceConfiguration | Add-Member Noteproperty -Name OutputName -value $jsonConfig.InstanceConfiguration.$InstanceName.OutputName
                        }
                    }
                }
                else {
                    Throw "Instance Name $InstanceName not found in configuration. Impossible to continue"
                }
            }
            else {
                $Script:InstanceConfiguration = New-Object PSObject
                $Script:InstanceConfiguration | Add-Member Noteproperty -Name InstanceName -value "Default"
                $Script:InstanceConfiguration | Add-Member Noteproperty -Name FileFilterType -value "All"
                $Script:InstanceConfiguration | Add-Member Noteproperty -Name FileFilterList -value @()
                $Script:InstanceConfiguration | Add-Member Noteproperty -Name FileIgnoreList -value @()
                $Script:InstanceConfiguration | Add-Member Noteproperty -Name Capabilities -value @('OL', 'OP', 'MGPGRAH')
            }


            $Script:AuditFunctionsFilesList = $jsonConfig.AuditFunctionsFiles
            $Script:JSonAuditFunctionList = $jsonConfig.AuditFunctions

            if (-not [string]::IsNullOrEmpty($jsonConfig.LogCollection))
            {
                $Script:SentinelLogCollector = New-Object PSObject
                if (-not [string]::IsNullOrEmpty($jsonConfig.LogCollection))
                {
                    $Script:SentinelLogCollector | Add-Member Noteproperty -Name ActivateLogUpdloadToSentinel -value ([Convert]::ToBoolean($jsonConfig.LogCollection.ActivateLogUpdloadToSentinel))
                }
                else {
                    $Script:SentinelLogCollector | Add-Member Noteproperty -Name ActivateLogUpdloadToSentinel -value $false
                }
                $Script:SentinelLogCollector | Add-Member Noteproperty -Name WorkspaceId -value $jsonConfig.LogCollection.WorkspaceId
                $Script:SentinelLogCollector | Add-Member Noteproperty -Name WorkspaceKey -value $jsonConfig.LogCollection.WorkspaceKey
                $Script:SentinelLogCollector | Add-Member Noteproperty -Name LogTypeName -value $jsonConfig.LogCollection.LogTypeName
                $Script:SentinelLogCollector | Add-Member Noteproperty -Name TogetherMode -value ([Convert]::ToBoolean($jsonConfig.LogCollection.TogetherMode))

                if ($Script:SentinelLogCollector.ActivateLogUpdloadToSentinel)
                {
                    if ([string]::IsNullOrEmpty($Script:SentinelLogCollector.WorkspaceId) -or
                    [string]::IsNullOrEmpty($Script:SentinelLogCollector.WorkspaceKey) -or
                    [string]::IsNullOrEmpty($Script:SentinelLogCollector.LogTypeName))
                    {
                        throw "Sentinel Log Collector configuration is activated and contains wrong values."
                    }
                }

                if (-not [string]::IsNullOrEmpty($Script:InstanceConfiguration.OutputName))
                {
                    $Script:SentinelLogCollector.LogTypeName = $Script:InstanceConfiguration.OutputName
                }
                elseif ($Script:ESIProcessingType -like "Online" -and -not $Script:SentinelLogCollector.LogTypeName.startswith("ESIExchangeOnline"))
                {
                    $Script:SentinelLogCollector.LogTypeName -replace "ESIExchangeConfig", "ESIExchangeOnlineConfig"
                }
            }

        }
        catch
        {
            Write-LogMessage -Message "Impossible to process configuration - Exception: $($_.Exception.Message) `n StackTrace: $($_.ScriptStackTrace) `n PositionMessage: $($_.InvocationInfo.PositionMessage)" -Level Error
            throw $_
        }
    }

    function LoadAuditFunctionsFromInternetRepository
    {
        Param (
            $ProcessingType,
            [switch] $Beta
        )

        if (-not $Global:isRunbook )
        {
            $NewAddonCache = $false

            # Verify the cache directory exists
            $scriptFolder = $Script:scriptFolder
            $ScriptAddonCachePath = $scriptFolder + '\Config\Add-Ons\OnlineCache\'
            $GithubSourcePath = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/%23%20-%20General%20Content/Operations/ESICollector-Addons"

            if ($Beta)
            {
                $GithubSourcePath += "/Beta"
            }

            if ($Script:InstanceConfiguration.FileFilterType -match "Categorize")
            {
                $ScriptAddonCachePath += "Categories\$($Script:InstanceConfiguration.Category)\"
                $GithubSourcePath += "/Categories/$($Script:InstanceConfiguration.Category)/"
            }

            Push-Location ($scriptFolder);
            if (! (Test-Path $ScriptAddonCachePath)) { $NewAddonCache = $true; mkdir $ScriptAddonCachePath -Force | Out-Null }
            
            # Verify if cache empty
            if ($NewAddonCache) { $CacheEmpty = $true; $files = $null}
            else 
            {
                $files = Get-ChildItem -Path $ScriptAddonCachePath -Filter "ESICollector-*.json" 
                if ($null -eq $files -or $files.count -le 0) {$CacheEmpty = $True}
                else {$CacheEmpty = $false}

                if (-not $CacheEmpty)
                {
                    if (Test-Path ($ScriptAddonCachePath + "ESIChecksumFiles.json"))
                    {
                        $ChecksumContent = Get-Content ($ScriptAddonCachePath + "ESIChecksumFiles.json") | ConvertFrom-Json
                        if ($ChecksumContent.Files.Count -ne $files.count)
                        {
                            Write-LogMessage -Message "Invalidate cache because incoherence in number of files - Theory : $($ChecksumContent.Files.Count) / Real : $($files.count)" -NoOutput -Level Warning; 
                            Get-ChildItem -Path $ScriptAddonCachePath | Remove-Item
                            $CacheEmpty = $True
                        }
                        else {
                            foreach ($checksumfile in $ChecksumContent.Files)
                            {
                                if ((Get-FileHash -Path ($ScriptAddonCachePath + $checksumfile.FileName) -Algorithm SHA256).Hash -ne $checksumfile.FileCheckSum)
                                {
                                    Write-LogMessage -Message "Invalidate cache because cached file modified outside authorized method ($($checksumfile.FileName))" -NoOutput -Level Warning; 
                                    Get-ChildItem -Path $ScriptAddonCachePath | Remove-Item
                                    $CacheEmpty = $True
                                    break;
                                }
                            }
                        }
                    }
                    else {
                        Write-LogMessage -Message "Invalidate cache because ESIChecksumFiles.json not present" -NoOutput -Level Warning; 
                        Get-ChildItem -Path $ScriptAddonCachePath | Remove-Item
                        $CacheEmpty = $True
                    }
                }
            }

            # Retrieve File Checksum list
            
            try {
                if ($Useproxy)
                {
                    $WebResult = invoke-WebRequest -Uri "$GithubSourcePath/ESIChecksumFiles.json" -UseBasicParsing -Proxy $Script:ProxyUrl
                }
                else
                {
                    $WebResult = invoke-WebRequest -Uri "$GithubSourcePath/ESIChecksumFiles.json" -UseBasicParsing
                }
            }
            catch {
                Write-LogMessage -Message "Impossible to retrieve files from Online Github. Error : $($_.Exception)" -NoOutput -Level Warning; 

                if ($CacheEmpty)
                {
                    Throw "Impossible to load Audit Functions, Critical for collection. Error :" + $_
                }
                else {
                    Write-LogMessage -Message "Impossible to retrieve files from Online Github. Cached files will be used" -NoOutput -Level Warning; 
                    return LoadAuditFunctions -ProcessingType $ProcessingType -FromAddOnFolder -TargetAddOnFolder $ScriptAddonCachePath
                }
            }
            
            # If not empty, check each file from checksum list
            if (-not $CacheEmpty)
            {
                $localHash = Get-FileHash -Path $ScriptAddonCachePath + "ESIChecksumFiles.json" -Algorithm SHA256

                $stringAsStream = [System.IO.MemoryStream]::new()
                $writer = [System.IO.StreamWriter]::new($stringAsStream)
                $writer.write($WebResult.Content)
                $writer.Flush()
                $stringAsStream.Position = 0
                $onlineHash = Get-FileHash -InputStream $stringAsStream -Algorithm SHA256

                if ($localHash.Hash -ne $onlineHash.Hash)
                {
                    Write-LogMessage -Message "New online content. Cache invalidation to update content" -NoOutput; 
                    Get-ChildItem -Path $ScriptAddonCachePath | Remove-Item
                    $CacheEmpty = $True
                }
            }

            if ($CacheEmpty) 
            {
                Write-LogMessage -Message "Update Cache Content" -NoOutput; 
                $WebResult.Content | Set-ESIContent -Path ($ScriptAddonCachePath + "ESIChecksumFiles.json")
                $OnlineFiles = $WebResult.Content | ConvertFrom-Json

                # Add all file in the list
                foreach ($OnlineFile in $OnlineFiles.Files)
                {
                    $uri = "$GithubSourcePath/$($OnlineFile.FileName)"
                    try {
                        if ($Useproxy)
                        {
                            $WebResult = invoke-WebRequest -Uri $uri -UseBasicParsing -Proxy $Script:ProxyUrl
                        }
                        else
                        {
                            $WebResult = invoke-WebRequest -Uri $uri -UseBasicParsing
                        }
                    }
                    catch {
                        Write-LogMessage -Message "Impossible to retrieve file $($OnlineFile.FileName) from Online Github. Error : $($_.Exception)" -NoOutput -Level Warning; 
                        Throw "Impossible to load Audit Functions, Critical for collection. Error :" + $_
                    }
                    $WebResult.Content | Set-ESIContent -Path ($ScriptAddonCachePath + $OnlineFile.FileName)
                }
            }

            # Call LoadFunction
            return LoadAuditFunctions -ProcessingType $ProcessingType -FromAddOnFolder -TargetAddOnFolder $ScriptAddonCachePath
        }
        else {
            return LoadAuditFunctionsForRunBook -ProcessingType $ProcessingType -Beta:$Beta
        }
    }

    function LoadAuditFunctionsForRunBook
    {
        Param (
            $ProcessingType,
            [switch] $Beta
        )

        # Process in Memory without storage
        # Retrieve File Checksum list
        $GithubSourcePath = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/%23%20-%20General%20Content/Operations/ESICollector-Addons"
        
        if ($Beta)
        {
            $GithubSourcePath += "/Beta"
        }

        Write-LogMessage "Filter $($Script:InstanceConfiguration.FileFilterType) - Category $($Script:InstanceConfiguration.Category)" -NoOutput

        if ($Script:InstanceConfiguration.FileFilterType -match "Categorize")
        {
            $GithubSourcePath += "/Categories/$($Script:InstanceConfiguration.Category)/"
        }
        
        try {
            if ($Useproxy)
            {
                $WebResult = invoke-WebRequest -Uri "$GithubSourcePath/ESIChecksumFiles.json" -UseBasicParsing -Proxy $Script:ProxyUrl
            }
            else
            {
                $WebResult = invoke-WebRequest -Uri "$GithubSourcePath/ESIChecksumFiles.json" -UseBasicParsing 
            }
        }   
        catch {
            Write-LogMessage -Message "Impossible to retrieve files from Online Github. Error : $($_.Exception)" -NoOutput -Level Warning; 
            Throw "Impossible to load Audit Functions, Critical for collection. Error :" + $_
        }

        # Retrieve all list
        $OnlineFiles = $WebResult.Content | ConvertFrom-Json
        $AuditFunctionList = @()

        foreach ($OnlineFile in $OnlineFiles.Files)
        {
            $FileToIgnore = $false;
            foreach ($AFFile in $Script:AuditFunctionsFilesList)
            {
                if ($AFFile.Filename -like $OnlineFile.FileName -and $AFFile.Deactivated) 
                {
                    Write-LogMessage "Add-on Audit function file $($AFFile.Filename) deactivated" -NoOutput
                    $FileToIgnore = $true
                    break;
                }
            }

            if (-not $FileToIgnore -and $Script:InstanceConfiguration.FileFilterType -match "Filtered")
            {
                if ($OnlineFile.FileName -notin $Script:InstanceConfiguration.FileFilterList)
                {
                    Write-LogMessage "Add-on Audit function file $($OnlineFile.FileName) not in selected Add-Ons of the Instance $($Script:InstanceConfiguration.InstanceName)" -NoOutput
                    $FileToIgnore = $true
                }
            }

            if (-not $FileToIgnore -and $Script:InstanceConfiguration.FileFilterType -match "Ignored")
            {
                if ($OnlineFile.FileName -in $Script:InstanceConfiguration.FileIgnoreList)
                {
                    Write-LogMessage "Add-on Audit function file $($OnlineFile.FileName) in Ignored Add-Ons of the Instance $($Script:InstanceConfiguration.InstanceName)" -NoOutput
                    $FileToIgnore = $true
                }
            }

            if ($FileToIgnore) {continue;}
            
            $uri = "$GithubSourcePath/$($OnlineFile.FileName)"
            try {
                if ($Useproxy)
                {
                    $WebResult = invoke-WebRequest -Uri $uri -UseBasicParsing -Proxy $Script:ProxyUrl
                }
                else {
                    $WebResult = invoke-WebRequest -Uri $uri -UseBasicParsing
                }
            }
            catch {
                Write-LogMessage -Message "Impossible to retrieve file $($OnlineFile.FileName) from Online Github. Error : $($_.Exception)" -NoOutput -Level Warning; 
                Throw "Impossible to load Audit Functions, Critical for collection. Error :" + $_
            }
            $OnlineAuditFunctionsFile = $WebResult.Content | ConvertFrom-Json
            Write-LogMessage -Message "Nb Audit Functions found :$($OnlineAuditFunctionsFile.AuditFunctions.count) for $($OnlineFile.FileName)" -NoOutput -Level Info;
            $AuditFunctionList += $OnlineAuditFunctionsFile.AuditFunctions 
        }

        Write-LogMessage -Message "Audit Functions loaded from Online Github " -NoOutput -Level Info;

        # Call LoadFunction
        return LoadAuditFunctions -AuditFunctionList $AuditFunctionList -ProcessingType "Online"
    }

    function LoadAuditFunctions
    {
        Param (
            $AuditFunctionList,
            $ProcessingType,
            [switch] $FromAddOnFolder,
            $TargetAddOnFolder = "./Config/Add-Ons/"
        )

        $ForbiddenVerb = @(
            "Set", "New", "Remove", "Add", "Clear", "Copy", "Move", "Rename", "Reset", "Unlock", "Edit", "Import", "Merge", "Mount",
            "Restore", "Save", "Update", "Start", "Stop", "Uninstall", "Unregister"
        )

        $pattern = "(?<cmdlet>(#Verbs#)-[A-Za-z0-9]+) "
        $pattern = $pattern -replace "#Verbs#", ($ForbiddenVerb -join "|")

        $Replacements = @{
            "#LastDateTracking#" = $script:LastDateTracking; 
            "#ScriptLaunchedDate#" = $Script:DateSuffix; 
            "#ForestDN#" = $script:ForestDN; 
            "#ForestName#" = $script:ForestName; 
            "#ExchOrgName#" = $script:ExchOrgName; 
            "#GCRoot#" = $script:GCRoot;
            "#GCServer#" = $script:gc;
            "#SIDRoot#" = $script:sidroot;
            "#IISLogPath#" = $Script:DefaultIISLogPath;
        }

        if ($FromAddOnFolder)
        {
            if ($Script:InstanceConfiguration.FileFilterType -match "Categorize" -and $TargetAddOnFolder -notlike "*Categories*")
            {
                $TargetAddOnFolder += "Categories/$($Script:InstanceConfiguration.Category)/"
            }

            if (-not (Test-Path $TargetAddOnFolder))
            { 
                throw "Impossible to continue as $TargetAddOnFolder is not valid"
            }

            $files = Get-ChildItem -Path $TargetAddOnFolder -Filter "ESICollector-*.json"
            $AuditFunctionList = @()
            foreach($file in $files) 
            { 
                $FileToIgnore = $false;
                foreach ($AFFile in $Script:AuditFunctionsFilesList)
                {
                    if ($AFFile.Filename -like $file.Name -and $AFFile.Deactivated) 
                    {
                        Write-LogMessage "Add-on Audit function file $($AFFile.Filename) deactivated" -NoOutput
                        $FileToIgnore = $true
                        break;
                    }
                }

                if (-not $FileToIgnore -and $Script:InstanceConfiguration.FileFilterType -match "Filtered")
                {
                    if ($file.Name -notin $Script:InstanceConfiguration.FileFilterList)
                    {
                        Write-LogMessage "Add-on Audit function file $($file.Name) not in selected Add-Ons of the Instance $($Script:InstanceConfiguration.InstanceName)" -NoOutput
                        $FileToIgnore = $true
                    }
                }

                if (-not $FileToIgnore -and $Script:InstanceConfiguration.FileFilterType -match "Ignored")
                {
                    if ($file.Name -in $Script:InstanceConfiguration.FileIgnoreList)
                    {
                        Write-LogMessage "Add-on Audit function file $($file.Name) in Ignored Add-Ons of the Instance $($Script:InstanceConfiguration.InstanceName)" -NoOutput
                        $FileToIgnore = $true
                    }
                }

                if ($FileToIgnore) {continue;}

                $content = Get-Content -Path $file.FullName | ConvertFrom-Json;
                $AuditFunctionList += $content.AuditFunctions 
            }
        }


        $FunctionListFromConfig = @()
        foreach ($AuditFunction in $AuditFunctionList)
        {
            if (-not [string]::IsNullOrEmpty($AuditFunction.Deactivated)) 
            {   
                $FunctionDeactivated = [Convert]::ToBoolean($AuditFunction.Deactivated)
                if ($FunctionDeactivated) { Write-LogMessage -Message "Function $($AuditFunction.Section) Deactivated" -NoOutput; continue;}
            }

            $FunctionProcessingCategory = $AuditFunction.ProcessingCategory
            if ([string]::IsNullOrEmpty($FunctionProcessingCategory)) {$FunctionProcessingCategory = 'On-Premises'}

            if ($FunctionProcessingCategory -notlike "All" -and $FunctionProcessingCategory -notlike $ProcessingType)
            {
                Write-LogMessage -Message "Function $($AuditFunction.Section) with Processing Category $FunctionProcessingCategory is not compatible with current processing $ProcessingType" -NoOutput; 
                continue;
            }

            if ($Script:OnlyExplicitActivation)
            {
                if (-not [string]::IsNullOrEmpty($AuditFunction.ExplicitActivation)) 
                {   
                    $FunctionExpliciallyActivated = [Convert]::ToBoolean($AuditFunction.ExplicitActivation)
                    if (-not $FunctionExpliciallyActivated) 
                    { 
                        Write-LogMessage -Message "Function $($AuditFunction.Section) not explicitaly activated and ExplicitActivation flag present" -NoOutput; 
                        continue;
                    }
                    else {
                        Write-LogMessage -Message "Function $($AuditFunction.Section) explicitaly activated and ExplicitActivation flag present / Will be launched" -NoOutput;
                    }
                }
                else
                {
                    Write-LogMessage -Message "Function $($AuditFunction.Section) not explicitaly activated and ExplicitActivation flag present" -NoOutput; 
                    continue;
                }
            }

            if ($AuditFunction.Cmdlet -imatch $pattern)
            {
                Write-LogMessage -Message "Function $($AuditFunction.Section) contains a forbidden verb $Verb on cmdlet $($Matches['cmdlet']). Collection aborted due to security issue" -NoOutput -Level Error; 
                throw "Function $($AuditFunction.Section) contains a forbidden verb $Verb on cmdlet $($Matches['cmdlet']). Collection aborted due to security issue";
            }

            $TargetCmdlet = $AuditFunction.Cmdlet
            foreach ($ReplaceKey in $Replacements.Keys)
            {
                $TargetCmdlet = $TargetCmdlet -replace $ReplaceKey, $Replacements[$ReplaceKey]
            }

            if ([string]::IsNullOrEmpty($AuditFunction.ProcessPerServer)) {$TargetProcessPerServer = $false}
            else {$TargetProcessPerServer = [Convert]::ToBoolean($AuditFunction.ProcessPerServer)}

            if ([string]::IsNullOrEmpty($AuditFunction.TransformationForeach)) {$TransformationForeach = $false}
            else {$TransformationForeach = [Convert]::ToBoolean($AuditFunction.TransformationForeach)}

            if ([string]::IsNullOrEmpty($AuditFunction.PropertySelection)) {$TargetSelect = @("*")} else { $TargetSelect = $AuditFunction.PropertySelection}
            
            if (-not [string]::IsNullOrEmpty($AuditFunction.CustomExpressionForSelection) -or $AuditFunction.CustomExpressionForSelection.count -gt 0) 
            {
                foreach ($CustomExp in $AuditFunction.CustomExpressionForSelection)
                {
                    $TargetSelect += @{Name=$CustomExp.Name; Expression=[ScriptBlock]::Create($CustomExp.Expression)}
                }
            }

            if ([string]::IsNullOrEmpty($AuditFunction.NoRunspace)) {$NoRunspace = $false } else { $NoRunspace = [Convert]::ToBoolean($AuditFunction.NoRunspace)}

            if ([string]::IsNullOrEmpty($AuditFunction.OutputStream)) {$TargetOutputStream = "Default"}
            else {$TargetOutputStream = $AuditFunction.OutputStream}

            if ($null -ne $AuditFunction.PaginationInformation)
            {
                try {
                    $PartialDataUpload = [Convert]::ToBoolean($AuditFunction.PaginationInformation.PartialDataUpload)
                    $StorePagesInMemory = [Convert]::ToBoolean($AuditFunction.PaginationInformation.StorePagesInMemory)
                    $PaginationInformation = New-Pagination -PaginationActivated:$true -PageSize $AuditFunction.PaginationInformation.PageSize -MaxPage $AuditFunction.PaginationInformation.MaxPage -PartialDataUpload:$PartialDataUpload -StorePagesInMemory:$StorePagesInMemory
                }
                catch {
                    Write-LogMessage -Message "Function $($AuditFunction.Section) contains an invalid PaginationInformation $($AuditFunction.PaginationInformation) / Collection aborted due to security issue" -NoOutput -Level Error; 
                    throw "Function $($AuditFunction.Section) contains an invalid PaginationInformation $($AuditFunction.PaginationInformation) / Collection aborted due to security issue"
                }
            }
            else { $PaginationInformation = $null }

            if ($null -ne $AuditFunction.DateStorageInformation)
            {
                try {
                    $DateReset = [Convert]::ToBoolean($AuditFunction.DateStorageInformation.DateReset)
                    $LastDate = Get-LastLaunchTime -SpecificFunction -FunctionName $AuditFunction.Section `
                         -Reset:$DateReset -resetType $AuditFunction.DateStorageInformation.ResetType `
                         -SpecificFormat $AuditFunction.DateStorageInformation.DateStorageFormat
                    $DateStorageInformation = New-DateStorage -DateStorageActivated:$true `
                        -DateStorageMode $AuditFunction.DateStorageInformation.DateStorageMode -LastDateTracking $LastDate `
                        -SpecificFormat $AuditFunction.DateStorageInformation.DateStorageFormat
                }
                catch {
                    Write-LogMessage -Message "Function $($AuditFunction.Section) contains an invalid DateStorageInformation $($AuditFunction.$DateStorageInformation) / Collection aborted due to security issue" -NoOutput -Level Error; 
                    throw "Function $($AuditFunction.Section) contains an invalid DateStorageInformation $($AuditFunction.$DateStorageInformation) / Collection aborted due to security issue"
                }
            }
            else { $DateStorageInformation = $null }

            $FunctionListFromConfig += New-Entry -Section $AuditFunction.Section -PSCmdL $TargetCmdlet -Select $TargetSelect -TransformationFunction $AuditFunction.TransformationFunction -ProcessPerServer:$TargetProcessPerServer  -TransformationForeach:$TransformationForeach -OutputStream $TargetOutputStream -Norunspace:$NoRunspace -PaginationInformation $PaginationInformation -DateStorageInformation $DateStorageInformation
        }

        return $FunctionListFromConfig
    }

#endregion Configuration Loading

$InformationPreference = "Continue"
$start = Get-Date
$DateSuffixForFile = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$DateSuffix = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"
$Global:isRunbook = if (-not $IsOutsideAzureAutomation) 
    {
        if (!($null -eq (Get-Command "Get-AutomationVariable" -ErrorAction SilentlyContinue)))
        {
            try {
                $TestVariable = Get-AutomationVariable -Name TenantName -ErrorAction SilentlyContinue
            }
            catch {
                $TestVariable = $null
            }

            if ($null -eq (Get-Module -Name Orchestrator* -ErrorAction SilentlyContinue) -and $null -eq $TestVariable)
            {
                $false
            }
            else {$true}
        }
        else {$false}
    } else {$false}
$Global:InstanceName = $InstanceName
$Script:MaximalSentinelFieldMemberListSizeKb = 20
$Script:MaxPageNumber = 1000
$Script:Runspaces = @{}
$script:ht_domains = @{}
$script:GUserArray=@{}
$script:GGroupArray=@{}
$Script:Results = @{}
$Script:Results["Default"] = @()
$Global:InjectionTest = @()
$Script:UDSLogs = $null

# Force TLS1.2 to make sure we can download from HTTPS
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (-not $Global:isRunbook )
{
    $scriptFolder = Split-Path -Parent $MyInvocation.MyCommand.Definition
    $Script:scriptFolder = $scriptFolder
    $ScriptLogPath = $scriptFolder + '\Logs'

    Push-Location ($scriptFolder);
    if (! (Test-Path $ScriptLogPath)) { mkdir $ScriptLogPath }

    if ($InstanceName -ne "Default") { $ScriptLogFile = "$ScriptLogPath\ScriptLog-$InstanceName-$DateSuffixForFile.log" }
    else { $ScriptLogFile = "$ScriptLogPath\ScriptLog-$DateSuffixForFile.log" }
    Start-Transcript -Path $ScriptLogFile

    CleanFiles -ScriptLogPath $ScriptLogPath -ClearFilesOlderThan $ClearFilesOlderThan
}

try {
    LoadConfiguration -configurationFile $JSONFileCondiguration -VariableFromAzureAutomation:$Global:isRunbook -InstanceName $InstanceName -ReceivedTenantName $ReceivedTenantName -ErrorAction Stop
}
catch {
    Write-LogMessage -Message "Configuration not loaded. Impossible to continue - Exception: $($_.Exception.Message) `n StackTrace: $($_.ScriptStackTrace) `n PositionMessage: $($_.InvocationInfo.PositionMessage)"
    if (-not $Global:isRunbook ) { Stop-Transcript }
    throw "Fatal Error, unable to continue - Exception: $($_.Exception.Message) `n StackTrace: $($_.ScriptStackTrace) `n PositionMessage: $($_.InvocationInfo.PositionMessage)"
    return -1
}

Check-ScriptUpdate

$ScriptInstanceID = ([Guid]::NewGuid()).Guid
Write-LogMessage -Message "Launching Exchange Configuration Collector Script, with ID $ScriptInstanceID for Instance $InstanceName on date $DateSuffix"


if (-not $NoDateTracing)
{
    Get-LastLaunchTime
}

Write-LogMessage -Message "Launching Capability analysis"
Set-Capabilities -CapabilitiesList $Script:InstanceConfiguration.Capabilities

Write-LogMessage -Message "Launching Runspace ..."
if ($Script:ParallelProcessPerServer -or $Script:GlobalParallelProcess) {
    CreateRunspaces -NumberRunspace $Script:MaxParallel
}

[System.Collections.ArrayList] $script:RunningProcesses = @()

if (-not $Global:isRunbook)
{
    Write-Host ("Create/Validate Output file path")
    if (-not (Test-Path (Split-Path $script:outputpath))) {mkdir (Split-Path $script:outputpath)}
    if (-not $ForceOutputWithoutDate -or $null -eq $ForceOutputWithoutDate)
    {
        $script:outputpath = $script:outputpath -replace ".csv", "-$DateSuffixForFile.csv"
    }
}

if (-not $Script:FunctionsListWithoutInternet)
{
    $FunctionList = LoadAuditFunctionsFromInternetRepository -ProcessingType $Script:ESIProcessingType -Beta:$Script:BetaActivated
}
else {
    $FunctionList = LoadAuditFunctions -AuditFunctionList $Script:JSonAuditFunctionList -ProcessingType $Script:ESIProcessingType -FromAddOnFolder:(-not $Script:FunctionsListInline)
}

Write-LogMessage -Message ("Launch Data collection ...")
$inc = 1

Write-LogMessage -Message ("Launch Audit Function loop Collection ...")
foreach ($Entry in $FunctionList)
{
    if ([string]::IsNullOrEmpty($Entry.Section)) 
    { 
        try {
            Write-LogMessage -Message ("`tNo Section found for $($Entry.ToString()) / Collection aborted for this object due to security issue, continue to next object") -NoOutput -Level Error;
        }
        catch {
            Write-LogMessage -Message ("`tNo Section found and Entry format can't be displayed for analysis / Collection aborted for this object due to security issue, continue to next object") -NoOutput -Level Error;
        }
        $inc++
        continue
    }
    
    Write-LogMessage -Message ("`tLaunch collection $inc on $($FunctionList.count) for $($Entry.Section)")

    $PaginationExecution = $false
    if ($null -ne $Entry.PaginationInformation -and $Entry.PaginationInformation.PaginationActivated) {

        Write-LogMessage -Message ("`tPagination information found for $($Entry.Section) $($Entry.PaginationInformation)")

        $PaginationExecution = $true
        $EntryOutStream = $Entry.OutputStream + "_Page"

        if ($Entry.PaginationInformation.PartialDataUpload)
        {
            $EntryOutStream = $EntryOutStream + "_SentDuringExecution"
        }

    }
    else {
        Write-LogMessage -Message ("`tNo Pagination information found for $($Entry.Section)")
        $EntryOutStream = $Entry.OutputStream
    }

    if ($Entry.DateStorageInformation.DateStorageActivated -and $Entry.DateStorageInformation.DateStorageMode -eq "DateFromAttribute")
    {
        $SaveDate = $True
        $DateStorageAttribute = $Entry.DateStorageInformation.DateAttribute
    }
    else {
        $SaveDate = $False
    }

    if ($EntryOutStream -notin $Script:Results.Keys) {
        Write-LogMessage -Message ("`tCreating Output Table for $($EntryOutStream)")
        if ($PaginationExecution) {
            $Script:Results[$EntryOutStream] = @{}
        }
        else {
            $Script:Results[$EntryOutStream] = @()
        }
    }

    $EntryCmdlet = $Entry.PSCmdL

    if ($EntryCmdlet -match "#LastDateOfSection#" -and $Entry.DateStorageInformation.DateStorageActivated) 
    {
        $EntryCmdlet = $EntryCmdlet -replace "#LastDateOfSection#", $Entry.DateStorageInformation.LastDateTracking
    }

    if ($Entry.ProcessPerServer)
    {
        if ($script:CapabilityLoaded -notcontains "OP") {
            Write-LogMessage -Message ("`tImpossible to launch a Per Server action without OP capability") -Level Warning
            $ErrorMessage = "`tImpossible to launch a Per Server action without OP capability"
            
            $Script:Results[$EntryOutStream] += New-Result -Section $Entry.Section -PSCmdL $EntryCmdlet -ErrorText $ErrorMessage -EntryDate $Script:DateSuffix -ScriptInstanceID $Script:ScriptInstanceID
            continue;
        }

        foreach ($ExchangeServer in $script:ExchangeServerList.ListSRVUp)
        {
            if (($Script:ParallelProcessPerServer -or $Script:GlobalParallelProcess) -and $Entry.NoRunpace -eq $false -and -not $PaginationExecution) {
                processParallel -Entry $Entry -TargetServer $ExchangeServer -EntryCmdlet $EntryCmdlet -EntryOutStream $EntryOutStream -EntrySuboutputPage $EntrySuboutputPage -IsPaginated:$PaginationExecution
            }
            else {
                if ($PaginationExecution -and ($Script:ParallelProcessPerServer -or $Script:GlobalParallelProcess))
                {
                    Write-LogMessage -Message ("`tParallel process for pagination not supported, fallback to sequential process for the section $($Entry.Section)") -Level Warning
                }
                
                $Script:Results[$EntryOutStream] += GetCmdletExec -Section $Entry.Section -PSCmdL $EntryCmdlet -Select $Entry.Select -TransformationFunction $Entry.TransformationFunction -TargetServer $ExchangeServer -TransformationForeach:$Entry.TransformationForeach -SaveDate:$SaveDate -SaveDateAttribute $DateStorageAttribute -Entry $Entry -PaginationExecution:$PaginationExecution
            }
        }  
    }
    else
    {
        if ($Script:GlobalParallelProcess -and $Entry.NoRunpace -eq $false -and -not $PaginationExecution) {
            processParallel -Entry $Entry -EntryCmdlet $EntryCmdlet -EntryOutStream $EntryOutStream -EntrySuboutputPage $EntrySuboutputPage -IsPaginated:$PaginationExecution
        }
        else {
            if ($PaginationExecution -and ($Script:ParallelProcessPerServer -or $Script:GlobalParallelProcess))
            {
                Write-LogMessage -Message ("`tParallel process for pagination not supported, fallback to sequential process for the section $($Entry.Section)") -Level Warning
            }

            $Script:Results[$EntryOutStream] += GetCmdletExec -Section $Entry.Section -PSCmdL $EntryCmdlet -Select $Entry.Select -TransformationFunction $Entry.TransformationFunction -TransformationForeach:$Entry.TransformationForeach  -SaveDate:$SaveDate -SaveDateAttribute $DateStorageAttribute -Entry $Entry -PaginationExecution:$PaginationExecution

        }
    }

    if ($Entry.DateStorageInformation.DateStorageActivated -and -not $SaveDate)
    {
        switch ($Entry.DateStorageInformation.DateStorageMode)
        {
            "LastDate" {
                Set-CurrentLaunchTime -SpecificFunction -FunctionName $Entry.Section -DateSuffix (Get-Date -Format "yyyy-MM-dd HH:mm:ss K")
            }
            "StartDateScript" {
                Set-CurrentLaunchTime -SpecificFunction -FunctionName $Entry.Section -DateSuffix $Script:DateSuffix
            }
        }
    }

    $inc++
}

if ($Script:ParallelProcessPerServer -or $Script:GlobalParallelProcess) {
    WaitAndProcess
}

Write-LogMessage -Message ("Launch CSV Creation / Sentinel Payload uploading ...")

foreach ($OutputName in $Script:Results.Keys)
{
    $OutputOptions = Get-OutputOptions -OutputName $OutputName
    
    if ($OutputOptions.IsPartial)
    {
        if ($OutputOptions.AlreadyBackuped)
        {
            Write-LogMessage -Message ("`tPartial Output $OutputName already processed, skipping ...")
            continue;
        }
        else {
            foreach ($SubpageKey in $Script:Results[$OutputName].Keys)
            {
                Start-LogBackup -PartialData -PartialDataName $SubpageKey -OutputName $OutputName
            }
        }
    }
    else {

        if ($Script:Results[$OutputName].count -gt 0) { Start-LogBackup -OutputName $OutputName }
    }    
}

if (-not $NoDateTracing)
{
    Set-CurrentLaunchTime -DateSuffix $Script:DateSuffix -Save
}

Write-LogMessage -Message ("Exchange Configuration Collector script finished`n`n")
Write-Output (Invoke-UDSLogProcessor)

if ($Script:VersionNotToDate)
{
    Write-LogMessage "********** New version of the script available. $Script:VersionNotToDateMessage)" -Level Warning
}

$end = Get-Date
Write-LogMessage -Message "Execution done. Time elapsed: $(($end-$start).TotalSeconds)s"
Write-LogMessage -Message "Execution done. Time elapsed: $(($end-$start).TotalSeconds)s" -Level Warning

if ($Script:ParallelProcessPerServer -or $Script:GlobalParallelProcess) {
    WaitAndProcess
    Write-LogMessage -Message ("Close Created Runspaces")
	CloseRunspaces
}
if (-not $Global:isRunbook )
{
    Stop-Transcript
}
