Param
(
  [Parameter (Mandatory= $true)]
  [String] $IPToBeBlocked
)

Add-PSSnapin Microsoft.Exchange.Management.PowerShell.SnapIn

Add-IPBlockListEntry -IPAddress $IPToBeBlocked
