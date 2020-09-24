# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"


# Main
$stroageAccount 
$personalAccessToken = $env:personalAccessToken
Write-Host $personalAccessToken
#Get Orgs
#For Each Org Get Repos
#For Each Repo in Org
#get audit entries
# Get Repo Logs
#Get vuln alerts
