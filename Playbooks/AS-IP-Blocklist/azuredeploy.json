{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "metadata": {
        "comments": "This playbook is intended to be run from Microsoft Sentinel. Based upon Alert Rule Criteria, it will grab the IP address from MicrosoftAlerts and add them to a Microssoft Azure Conditional Access Named Locations list, signifying compromised IP addresses.",
        "author": "Accelerynt"
    },
    "parameters": {
        "PlaybookName": {
            "defaultValue": "AS-IP-Blocklist",
            "type": "String"
        },
        "NamedLocationsListName": {
            "type": "String",
            "metadata": {
                "description": "Name of the Microsoft Azure Named Locations list that will hold the ips"
            }
        },
        "NamedLocationsListID": {
            "type": "String",
            "metadata": {
                "description": "ID of the Microsoft Azure Named Locations list that will hold the ips"
            }
        },
        "AppRegistrationID": {
            "type": "String",
            "metadata" : {
                "description" : "Name of the Key Vault that stores the App Registration Secret"
            }
        },
        "AppRegistrationTenant": {
            "type": "String",
            "metadata" : {
                "description" : "Name of the Key Vault that stores the App Registration Secret"
            }
        },
        "KeyVaultName": {
            "type": "String",
            "metadata" : {
                "description" : "Name of the Key Vault that stores the App Registration Secret"
            }
        },
        "SecretName": {
            "type": "String",
            "metadata": {
                "description": "Name of Key Vault Secret that contains the value of the App Registration Secret"
            }
        }
    },
    "variables": {
        "azuresentinel": "[concat('azuresentinel-', parameters('PlaybookName'))]",
        "keyvault": "[concat('keyvault-', parameters('PlaybookName'))]"
    },
    "resources": [
        {
            "type": "Microsoft.Web/connections",
            "apiVersion": "2016-06-01",
            "name": "[variables('azuresentinel')]",
            "location": "[resourceGroup().location]",
            "properties": {
                "displayName": "[parameters('PlaybookName')]",
                "customParameterValues": {
                },
                "api": {
                    "id": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/azuresentinel')]"
                }
            }
        },
        {
            "type": "Microsoft.Web/connections",
            "apiVersion": "2016-06-01",
            "name": "[variables('keyvault')]",
            "location": "[resourceGroup().location]",
            "properties": {
                "displayName": "[parameters('PlaybookName')]",
                "parameterValueType": "Alternative",
                "alternativeParameterValues": {
                    "vaultName": "[parameters('KeyVaultName')]"
                },
                "customParameterValues": {
                },
                "api": {
                    "id": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/keyvault')]"
                }
            }
        },
        {
            "type": "Microsoft.Logic/workflows",
            "apiVersion": "2017-07-01",
            "name": "[parameters('PlaybookName')]",
            "location": "[resourceGroup().location]",
            "identity": {
                "type": "SystemAssigned"
            },
            "dependsOn": [
                "[resourceId('Microsoft.Web/connections', variables('azuresentinel'))]",
                "[resourceId('Microsoft.Web/connections', variables('keyvault'))]"
            ],
            "properties": {
                "state": "Enabled",
                "definition": {
                    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {
                        "$connections": {
                            "defaultValue": {},
                            "type": "Object"
                        }
                    },
                    "triggers": {
                        "Microsoft_Sentinel_incident": {
                            "type": "ApiConnectionWebhook",
                            "inputs": {
                                "body": {
                                    "callback_url": "@{listCallbackUrl()}"
                                },
                                "host": {
                                    "connection": {
                                        "name": "@parameters('$connections')['azuresentinel']['connectionId']"
                                    }
                                },
                                "path": "/incident-creation"
                            }
                        }
                    },
                    "actions": {
                        "Condition_-_Alert_Contains_IPs": {
                            "actions": {
                                "For_Each_-_Alert_IP": {
                                    "foreach": "@body('Entities_-_Get_IPs')?['IPs']",
                                    "actions": {
                                        "Append_to_String_Variable_-_JSON_Body": {
                                            "runAfter": {},
                                            "type": "AppendToStringVariable",
                                            "inputs": {
                                                "name": "Json Body",
                                                "value": " \n{\n         \"@odata.type\": \"#microsoft.graph.iPv4CidrRange\",\n          \"cidrAddress\": \"@{concat(items('For_Each_-_Alert_IP')?['Address'], '/32')}\"\n },"
                                            }
                                        }
                                    },
                                    "runAfter": {},
                                    "type": "Foreach"
                                },
                                "HTTP-_Add_IP_to_Named_Locations_List": {
                                    "runAfter": {
                                        "For_Each_-_Alert_IP": [
                                            "Succeeded"
                                        ]
                                    },
                                    "type": "Http",
                                    "inputs": {
                                        "authentication": {
                                            "audience": "https://graph.microsoft.com",
                                            "clientId": "[parameters('AppRegistrationID')]",
                                            "secret": "[parameters('SecretName')]",
                                            "tenant": "[parameters('AppRegistrationTenant')]",
                                            "type": "ActiveDirectoryOAuth"
                                        },
                                        "body": "@concat(substring(variables('Json Body'), 0, lastIndexOf(variables('Json Body'), ',')), decodeUriComponent('%0A'),']', decodeUriComponent('%0A'), '}')",
                                        "headers": {
                                            "Content-type": "application/json"
                                        },
                                        "method": "PATCH",
                                        "uri": "[concat('https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations/', parameters('NamedLocationsListID'))]"
                                    }
                                }
                            },
                            "runAfter": {
                                "Entities_-_Get_IPs": [
                                    "Succeeded"
                                ]
                            },
                            "expression": {
                                "and": [
                                    {
                                        "greater": [
                                            "@length(body('Entities_-_Get_IPs')?['IPs'])",
                                            0
                                        ]
                                    }
                                ]
                            },
                            "type": "If"
                        },
                        "Entities_-_Get_IPs": {
                            "runAfter": {
                                "For_Each_-_Existing_IP": [
                                    "Succeeded"
                                ]
                            },
                            "type": "ApiConnection",
                            "inputs": {
                                "body": "@triggerBody()?['object']?['properties']?['relatedEntities']",
                                "host": {
                                    "connection": {
                                        "name": "@parameters('$connections')['azuresentinel']['connectionId']"
                                    }
                                },
                                "method": "post",
                                "path": "/entities/ip"
                            }
                        },
                        "For_Each_-_Existing_IP": {
                            "foreach": "@body('Parse_JSON')?['ipRanges']",
                            "actions": {
                                "Append_to_string_variable": {
                                    "runAfter": {},
                                    "type": "AppendToStringVariable",
                                    "inputs": {
                                        "name": "Json Body",
                                        "value": "\n@{items('For_Each_-_Existing_IP')},\n"
                                    }
                                }
                            },
                            "runAfter": {
                                "Initialize_Variable_-_JSON_Body": [
                                    "Succeeded"
                                ]
                            },
                            "type": "Foreach"
                        },
                        "HTTP_-_Get_Previous_List_Values": {
                            "runAfter": {},
                            "type": "Http",
                            "inputs": {
                                "authentication": {
                                    "audience": "https://graph.microsoft.com",
                                    "clientId": "[parameters('AppRegistrationID')]",
                                    "secret": "[parameters('SecretName')]",
                                    "tenant": "[parameters('AppRegistrationTenant')]",
                                    "type": "ActiveDirectoryOAuth"
                                },
                                "method": "GET",
                                "uri": "[concat('https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations/', parameters('NamedLocationsListID'))]"
                            },
                            "description": "PATCH (and also PUT) method has been observed to overwrite an entire existing list with new values, and POST is not accepted at this endpoint. This GET step is necessary top preserve the preexisting values."
                        },
                        "Initialize_Variable_-_JSON_Body": {
                            "runAfter": {
                                "Parse_JSON": [
                                    "Succeeded"
                                ]
                            },
                            "type": "InitializeVariable",
                            "inputs": {
                                "variables": [
                                    {
                                        "name": "Json Body",
                                        "type": "string",
                                        "value": "[concat('{\n\"@odata.type\": \"#microsoft.graph.ipNamedLocation\",\n\"displayName\": \"', parameters('NamedLocationsListName'), '\",\n\"isTrusted\": false,\n \"ipRanges\": [')]"
                                    }
                                ]
                            }
                        },
                        "Parse_JSON": {
                            "runAfter": {
                                "HTTP_-_Get_Previous_List_Values": [
                                    "Succeeded"
                                ]
                            },
                            "type": "ParseJson",
                            "inputs": {
                                "content": "@body('HTTP_-_Get_Previous_List_Values')",
                                "schema": {
                                    "properties": {
                                        "@@odata.context": {
                                            "type": "string"
                                        },
                                        "@@odata.type": {
                                            "type": "string"
                                        },
                                        "createdDateTime": {
                                            "type": "string"
                                        },
                                        "displayName": {
                                            "type": "string"
                                        },
                                        "id": {
                                            "type": "string"
                                        },
                                        "ipRanges": {
                                            "items": {
                                                "properties": {
                                                    "@@odata.type": {
                                                        "type": "string"
                                                    },
                                                    "cidrAddress": {
                                                        "type": "string"
                                                    }
                                                },
                                                "required": [
                                                    "@@odata.type",
                                                    "cidrAddress"
                                                ],
                                                "type": "object"
                                            },
                                            "type": "array"
                                        },
                                        "isTrusted": {
                                            "type": "boolean"
                                        },
                                        "modifiedDateTime": {
                                            "type": "string"
                                        }
                                    },
                                    "type": "object"
                                }
                            }
                        }
                    },
                    "outputs": {}
                },
                "parameters": {
                    "$connections": {
                        "value": {
                            "azuresentinel": {
                                "connectionId": "[resourceId('Microsoft.Web/connections', variables('azuresentinel'))]",
                                "connectionName": "[variables('azuresentinel')]",
                                "id": "[concat('/subscriptions/', subscription().subscriptionId,'/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/azuresentinel')]"
                            },
                            "keyvault": {
                                "connectionId": "[resourceId('Microsoft.Web/connections', variables('keyvault'))]",
                                "connectionName": "[variables('keyvault')]",
                                "id": "[concat('/subscriptions/', subscription().subscriptionId,'/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/keyvault')]",
                                "connectionProperties": {
                                    "authentication": {
                                        "type": "ManagedServiceIdentity"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ]
}
