# Tanium-AddComment

## Overview
This playbook will enable Tanium to data to be commented to a specific incident inside of Azure.

## Prerequisites
Requests should be sent to this logic app with the below json schema:
```
{
    "properties": {
        "arm_id": {
            "type": "string"
        },
        "message": {
            "type": "string"
        }
    },
    "type": "object"
}
```

## Post-Deployment Instructions
After deploying the playbook, you must authorize the connections leveraged.

1. Visit the playbook resource.
2. Under "Development Tools" (located on the left), click "API Connections".
3. Ensure each connection has been authorized.
