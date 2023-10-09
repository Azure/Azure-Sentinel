#Create-Snapshot
This playbook will create a snapshot from an Azure VM.

The Logic App uses a Managed System Identity to authenticate and authorize against management.azure.com to create the Snapshot. Be sure to turn on the System Assigned Identity in the Logic App.

The playbook queries LogAnalytics and uses the ResourceID to identify the VM.
The query should map the VM name to the HostCustomEntity in order to identify the right machine to create a snapshot for.