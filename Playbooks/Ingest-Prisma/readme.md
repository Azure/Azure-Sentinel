# Ingest-Prisma
author: Nathan Swift

This Logic App connector will act as a Webhook listener, Prisma can then send an array of events to it and it will send the events to Azure Sentinel - Prisma_CL  

When setting up Prisma you will see the field "Auth Token", this field is not required to connect Prisma. Only copy the complete HTTP Listener URL into the Prisma Webhook URL field.

Once the Prisma Webhook Listener has been configure, in the Alert/Alert Rules section of Prisma, you will need to enable the Webhook to receive the new alerts.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIngest-Prisma%2FAzuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIngest-Prisma%2Fazuredeploy.json)

**Additional Post Install Notes:**


Prisma configuration can be found: https://docs.paloaltonetworks.com/prisma/prisma-cloud/prisma-cloud-admin/configure-external-integrations-on-prisma-cloud/integrate-prisma-cloud-with-webhooks.html
Prisma webhook implementation details can be found here: https://techcommunity.microsoft.com/t5/azure-sentinel/connecting-prisma-to-sentinel/m-p/1408693
