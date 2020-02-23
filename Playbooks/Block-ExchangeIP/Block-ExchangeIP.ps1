Param
(
  [Parameter (Mandatory= $true)]
  [String] $IPToBeBlocked
)

Import-Module 'C:\Program Files\Microsoft\Exchange Server\V15\bin\RemoteExchange.ps1'; Connect-ExchangeServer -auto -ClientApplication:ManagementShell

Add-IPBlockListEntry -IPAddress $IPToBeBlocked