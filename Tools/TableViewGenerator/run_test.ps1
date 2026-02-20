$WorkspaceId = "60d381d4-e3ea-4553-ad97-047d10b0025b"
$ResourceId = "/subscriptions/0eb3b434-e9c0-4b6e-9fca-72bc3b0e2a90/resourceGroups/luna-ccp-0/providers/Microsoft.OperationalInsights/workspaces/0-luna-uk-south"
$Tables = "AWSCloudTrail"

python "$PSScriptRoot\deploy_table_views.py" -w $WorkspaceId -r $ResourceId -t $Tables --dry-run
