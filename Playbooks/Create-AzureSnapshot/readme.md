This playbook will create a snapshot from an Azure VM.

The Logic App uses a Managed System Identity to authenticate and authorize against management.azure.com to create the Snapshot. Be sure to turn on the System Assigned Identity in the Logic App.

The KQL query which triggers this Logic Apps should specify "ResourceId" as the HostCustomEntity.