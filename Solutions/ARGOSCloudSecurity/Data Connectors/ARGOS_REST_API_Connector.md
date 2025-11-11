# Connect your ARGOS Cloud Security to Azure Sentinel

ARGOS Cloud Security connector allows you to easily connect all your ARGOS Cloud Security security solution logs with your Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. In addition this integration allows you to correlate your ARGOS Cloud Security events to other events that are happening in your environment. Integration between ARGOS Cloud Security and Azure Sentinel makes use of REST API.

> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel. This can be different to the geographic location of your ARGOS Cloud Security subscription.

## Configure and connect ARGOS Cloud Security

ARGOS Cloud Security can integrate and export detections directly to Azure Sentinel.

1. In the Azure Sentinel portal, click Data connectors and select ARGOS Cloud Security and then Open connector page.
2. Either follow the instructions on the [ARGOS Resources](https://www.argos-security.io/resources#integrations) page on how to configure the integration or if you are already logged in to ARGOS then head to the [Sentinel integration page](https://app.argos-security.io/account/sentinel) and configure it right away.

## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs ARGOS_CL.
To use the relevant schema in Log Analytics for the ARGOS Cloud Security, search for ARGOS_CL.

## Validate connectivity

It may take up to 20 minutes until your logs start to appear in Log Analytics.

## Next steps

In this document, you learned how to connect ARGOS Cloud Security to Azure Sentinel.
