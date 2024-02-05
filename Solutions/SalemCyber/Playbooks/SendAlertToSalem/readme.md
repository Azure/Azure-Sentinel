# Send Alerts to Salem Playbook Guide

## Overview

This playbook is designed to make it simple to send new Microsoft Sentinel alerts to Salem for investigation.  This playbook will forward alerts to the EventHub instance in the Salem managed resource group.

## Prerequisites

- Have an active Salem application installed in Azure.  The Salem app can be found in the [Azure Marketplace](https://portal.azure.com/#view/Microsoft_Azure_Marketplace/GalleryItemDetailsBladeNopdl/id/saleminc1627928803559.salemcyber)

## Pre-deployment

### Update Event Hub network settings

Collect the Salem Event Hub send key.  This value will be required during playbook deployment and will enable the playbook to forward new Microsoft Sentinel Alerts to Salem.

The key from the 'alerts' EventHub namespace in the Salem EventHub.  You can find this key in the Azure portal for the event hub resource in the Salem managed resource group.  The key will already exist, however, you can generate a new key if you wish.  If you do create a new key, ensure the key has 'send' permissions.

## Post Deployment

### Authorize the API connection

When deploying the playbook, a new API connection resource was created and needs to be authorized.

1. Find the API connections created by deploying the Defender APT integration.  The API connections will be called 'Salem-MicrosoftSentinel' and 'Salem-DefenderATP'

## Update Event Hub network settings

The Salem Event Hub has default network rules that may prevent this playbook from connecting.  One way to allow network traffic to the Event Hub is to update the Event Hub network settings to allow inbound connections from the IP addresses associated with the region in which you deploy the playbook.  You can find the IP ranges based on the region you deployed this playbook, [here](https://learn.microsoft.com/en-us/connectors/common/outbound-ip-addresses#azure-logic-apps)

The Event Hub used by Salem is located in the Salem managed resource group.  You can find this resource group in the overview page of the Salem application.

It is also possible to use vNet integration or private endpoints to communicate between the playbook and the Salem Event Hub

## Get Help

For support, contact [support@salemcyber.com](mailto:support@salemcyber.com)
