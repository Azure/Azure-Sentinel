#Create-Snapshot
This playbook will create a snapshot from an Azure VM.

The Logic App uses a Managed System Identity to authenticate and authorize against management.azure.com to create the Snapshot. Be sure to turn on the System Assigned Identity in the Logic App.

The playbook queries LogAnalytics and uses the ResourceID to identify the VM.

#Warning
To create a snapshot of a VM, the resourceID is used to identify it.
Because the ResourceID is not in the original data we receive from Sentinel, we need to execute the original query which generates this result.
This means that, if 2 alerts where created within the last 15 minutes, a VM might be snapshotted twice.