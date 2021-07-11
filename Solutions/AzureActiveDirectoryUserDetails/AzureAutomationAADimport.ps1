<#   
The MIT License (MIT)

Copyright (c) 2015 Microsoft Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#>



<#   
Script      : AzureAutomationAADLAEnrichment
Author      : Chris Boehm
Version     : 1.3.0
Description : The script will pull your AAD information, format the data into JSON and import the data into a custom table within Log Analytics.
Required Modules: = OMSIngestionAPI, AzureAD

Note: Ran into an issue with Azure Automation converting too many objecting into JSON format, had to make it do 10 at a time in order for Azure Automation to not fail.

#>


#$ErrorActionPreference = "Stop"
$connectionName = "AzureRunAsConnection"
try
{
    # Get the connection "AzureRunAsConnection "
    $servicePrincipalConnection=Get-AutomationConnection -Name $connectionName         
 
    "Logging in to Azure Active Directory"
 
    Connect-AzureAD `
        -TenantId $servicePrincipalConnection.TenantId `
        -ApplicationId $servicePrincipalConnection.ApplicationId `
        -CertificateThumbprint $servicePrincipalConnection.CertificateThumbprint 
}
catch {
    if (!$servicePrincipalConnection)
    {
        $ErrorMessage = "Connection $connectionName not found."
        throw $ErrorMessage
    } else{
        Write-Error -Message $_.Exception
        throw $_.Exception
    }
} 

$CustomerID = 'WORKSPACE ID'
$SharedKey = 'WORKSPACE PRIMARY KEY'
$logType = 'TABLE NAME'
$UsersCollected = Get-AzureADUser -All $True
$TotalCount = $UsersCollected.count

# Example of ingesting data all at the same time
#$JSONUser = ConvertTo-Json $UsersCollected -Compress -ErrorAction Stop 
#$TimeStampfield = Get-date
#Send-OMSAPIIngestionFile -customerId $customerId -sharedKey $sharedKey -body $JSONUser -logType $logType -TimeStampField $Timestampfield -Verbose



# Example of ingestiing data 10 at a time into Log Analytics
For ($number = 0; $number -le $TotalCount; $number+=10) 
{ 
$TimeStampfield = Get-date
$TopNumber = $number+10
$JSONUser += ConvertTo-Json $UsersCollected[$number..$TopNumber] -Compress -ErrorAction Stop
Send-OMSAPIIngestionFile -customerId $customerId -sharedKey $sharedKey -body $JSONUser -logType $logType -TimeStampField $Timestampfield -Verbose
}




