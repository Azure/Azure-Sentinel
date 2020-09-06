using Microsoft.Azure.Sentinel.KustoServices.Contract;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Xunit;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests
{
    public class KqlValidationTests
    {
        private readonly IKqlQueryValidator _queryValidator;
        //TODO: read from configuration
        private readonly static IEnumerable<string> WhiteListTemplateIds = new string[] { "f948a32f-226c-4116-bddd-d95e91d97eb9", "39198934-62a0-4781-8416-a81265c03fd6", "3533f74c-9207-4047-96e2-0eb9383be587", "9fb57e58-3ed8-4b89-afcf-c8e786508b1c", "24f8c234-d1ff-40ec-8b73-96b17a3a9c1c", "d6491be0-ab2d-439d-95d6-ad8ea39277c5", "0914adab-90b5-47a3-a79f-7cdcac843aa7", "06a9b845-6a95-4432-a78b-83919b28c375", "57e56fc9-417a-4f41-a579-5475aea7b8ce", "155f40c6-610d-497d-85fc-3cf06ec13256", "f2dd4a3a-ebac-4994-9499-1a859938c947", "884be6e7-e568-418e-9c12-89229865ffde", "e27dd7e5-4367-4c40-a2b7-fcd7e7a8a508", "0558155e-4556-447e-9a22-828f2a7de06b", "34663177-8abf-4db1-b0a4-5683ab273f44", "a9956d3a-07a9-44a6-a279-081a85020cae" };
        private static readonly string DetectionPath = DetectionsYamlFilesTestData.GetDetectionPath();
        public KqlValidationTests()
        {
            _queryValidator = new KqlQueryValidatorBuilder()
               .WithSentinelDefaultTableSchemas()
               .WithCustomTableSchema(GetCustomLogsSchemas()) //TODO Get Custom schema from files
               .Build();
        }

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void validate_detectionqueries_succeed(string detectionsYamlFileName)
        {
            var detectionsYamlFile = Directory.GetFiles(DetectionPath, detectionsYamlFileName, SearchOption.AllDirectories).Single();
            var yaml = File.ReadAllText(detectionsYamlFile);
            var deserializer = new DeserializerBuilder().Build();
            var res = deserializer.Deserialize<dynamic>(yaml);
            string queryStr = res["query"];
            string id = res["id"];

            //we ignore so known issues
            if (WhiteListTemplateIds.Contains(id))
            {
                return;
            }

            var validationRes = _queryValidator.ValidateSyntax(queryStr);

            Assert.True(validationRes.IsValid, validationRes.IsValid ? string.Empty : validationRes.Diagnostics.Select(d => d.Message).ToList().Aggregate((s1, s2) => s1 + "," + s2));
        }

        private TableSchema[] GetCustomLogsSchemas()
        {
            return new TableSchema[] {
                     new TableSchema
                     {
                        Name = "Okta_CL",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "eventType_s" , Type = "String"},
                                new Property { Name = "outcome_reason_s" , Type = "String"},
                                new Property { Name = "client_ipAddress_s" , Type = "String"},
                                new Property { Name = "published_t" , Type = "DateTime"},
                                new Property { Name = "client_ipAddress_s" , Type = "String"},
                                new Property { Name = "client_geographicalContext_city_s" , Type = "String"},
                                new Property { Name = "client_geographicalContext_country_s" , Type = "String"},
                                new Property { Name = "outcome_result_s" , Type = "String"},
                                new Property { Name = "actor_alternateId_s" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "eset_CL",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "event_type_s" , Type = "String"},
                                new Property { Name = "username_s" , Type = "String"},
                                new Property { Name = "object_uri_s" , Type = "String"},
                                new Property { Name = "hostname_s" , Type = "String"},
                                new Property { Name = "ipv4_s" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "InfobloxNIOS",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "ProcessName" , Type = "String"},
                                new Property { Name = "ResponseCode" , Type = "String"},
                                new Property { Name = "Log_Type" , Type = "String"},
                                new Property { Name = "Client_IP" , Type = "String"},
                       }
                    },
                      new TableSchema
                     {
                        Name = "AzureDiagnostics",
                        Properties = new Property[]
                       {
                                new Property { Name = "TenantId", Type = "String"},
                                new Property { Name = "TimeGenerated", Type = "DateTime"},
                                new Property { Name = "ResourceId", Type = "String"},
                                new Property { Name = "Category", Type = "String"},
                                new Property { Name = "ResourceGroup", Type = "String"},
                                new Property { Name = "SubscriptionId", Type = "String"},
                                new Property { Name = "ResourceProvider", Type = "String"},
                                new Property { Name = "Resource", Type = "String"},
                                new Property { Name = "ResourceType", Type = "String"},
                                new Property { Name = "OperationName", Type = "String"},
                                new Property { Name = "ResultType", Type = "String"},
                                new Property { Name = "CorrelationId", Type = "String"},
                                new Property { Name = "ResultDescription", Type = "String"},
                                new Property { Name = "Tenant_g", Type = "String"},
                                new Property { Name = "JobId_g", Type = "String"},
                                new Property { Name = "RunbookName_s", Type = "String"},
                                new Property { Name = "StreamType_s", Type = "String"},
                                new Property { Name = "Caller_s", Type = "String"},
                                new Property { Name = "requestUri_s", Type = "String"},
                                new Property { Name = "Level", Type = "String"},
                                new Property { Name = "DurationMs", Type = "bigint"},
                                new Property { Name = "CallerIPAddress", Type = "String"},
                                new Property { Name = "OperationVersion", Type = "String"},
                                new Property { Name = "ResultSignature", Type = "String"},
                                new Property { Name = "id_s", Type = "String"},
                                new Property { Name = "status_s", Type = "String"},
                                new Property { Name = "LogicalServerName_s", Type = "String"},
                                new Property { Name = "Message", Type = "String"},
                                new Property { Name = "clientInfo_s", Type = "String"},
                                new Property { Name = "httpStatusCode_d", Type = "real"},
                                new Property { Name = "identity_claim_appid_g", Type = "String"},
                                new Property { Name = "identity_claim_http_schemas_microsoft_com_identity_claims_objectidentifier_g", Type = "String"},
                                new Property { Name = "userAgent_s", Type = "String"},
                                new Property { Name = "ruleName_s", Type = "String"},
                                new Property { Name = "identity_claim_http_schemas_xmlsoap_org_ws_2005_05_identity_claims_upn_s", Type = "String"},
                                new Property { Name = "systemId_g", Type = "String"},
                                new Property { Name = "isAccessPolicyMatch_b", Type = "bool"},
                                new Property { Name = "EventName_s", Type = "String"},
                                new Property { Name = "httpMethod_s", Type = "String"},
                                new Property { Name = "subnetId_s", Type = "String"},
                                new Property { Name = "type_s", Type = "String"},
                                new Property { Name = "instanceId_s", Type = "String"},
                                new Property { Name = "macAddress_s", Type = "String"},
                                new Property { Name = "vnetResourceGuid_g", Type = "String"},
                                new Property { Name = "direction_s", Type = "String"},
                                new Property { Name = "subnetPrefix_s", Type = "String"},
                                new Property { Name = "primaryIPv4Address_s", Type = "String"},
                                new Property { Name = "conditions_sourcePortRange_s", Type = "String"},
                                new Property { Name = "priority_d", Type = "real"},
                                new Property { Name = "conditions_destinationPortRange_s", Type = "String"},
                                new Property { Name = "conditions_destinationIP_s", Type = "String"},
                                new Property { Name = "conditions_None_s", Type = "String"},
                                new Property { Name = "conditions_sourceIP_s", Type = "String"},
                                new Property { Name = "httpVersion_s", Type = "String"},
                                new Property { Name = "matchedConnections_d", Type = "real"},
                                new Property { Name = "startTime_t", Type = "DateTime"},
                                new Property { Name = "endTime_t", Type = "DateTime"},
                                new Property { Name = "DatabaseName_s", Type = "String"},
                                new Property { Name = "clientIP_s", Type = "String"},
                                new Property { Name = "host_s", Type = "String"},
                                new Property { Name = "requestQuery_s", Type = "String"},
                                new Property { Name = "sslEnabled_s", Type = "String"},
                                new Property { Name = "clientPort_d", Type = "real"},
                                new Property { Name = "httpStatus_d", Type = "real"},
                                new Property { Name = "receivedBytes_d", Type = "real"},
                                new Property { Name = "sentBytes_d", Type = "real"},
                                new Property { Name = "timeTaken_d", Type = "real"},
                                new Property { Name = "resultDescription_ErrorJobs_s", Type = "String"},
                                new Property { Name = "resultDescription_ChildJobs_s", Type = "String"},
                                new Property { Name = "identity_claim_http_schemas_microsoft_com_identity_claims_scope_s", Type = "String"},
                                new Property { Name = "workflowId_s", Type = "String"},
                                new Property { Name = "resource_location_s", Type = "String"},
                                new Property { Name = "resource_workflowId_g", Type = "String"},
                                new Property { Name = "resource_resourceGroupName_s", Type = "String"},
                                new Property { Name = "resource_subscriptionId_g", Type = "String"},
                                new Property { Name = "resource_runId_s", Type = "String"},
                                new Property { Name = "resource_workflowName_s", Type = "String"},
                                new Property { Name = "_schema_s", Type = "String"},
                                new Property { Name = "correlation_clientTrackingId_s", Type = "String"},
                                new Property { Name = "properties_sku_Family_s", Type = "String"},
                                new Property { Name = "properties_sku_Name_s", Type = "String"},
                                new Property { Name = "properties_tenantId_g", Type = "String"},
                                new Property { Name = "properties_enabledForDeployment_b", Type = "bool"},
                                new Property { Name = "code_s", Type = "String"},
                                new Property { Name = "resultDescription_Summary_MachineId_s", Type = "String"},
                                new Property { Name = "resultDescription_Summary_ScheduleName_s", Type = "String"},
                                new Property { Name = "resultDescription_Summary_Status_s", Type = "String"},
                                new Property { Name = "resultDescription_Summary_StatusDescription_s", Type = "String"},
                                new Property { Name = "resultDescription_Summary_MachineName_s", Type = "String"},
                                new Property { Name = "resultDescription_Summary_TotalUpdatesInstalled_d", Type = "real"},
                                new Property { Name = "resultDescription_Summary_RebootRequired_b", Type = "bool"},
                                new Property { Name = "resultDescription_Summary_TotalUpdatesFailed_d", Type = "real"},
                                new Property { Name = "resultDescription_Summary_InstallPercentage_d", Type = "real"},
                                new Property { Name = "resultDescription_Summary_StartDateTimeUtc_t", Type = "DateTime"},
                                new Property { Name = "resource_triggerName_s", Type = "String"},
                                new Property { Name = "resultDescription_Summary_InitialRequiredUpdatesCount_d", Type = "real"},
                                new Property { Name = "properties_enabledForTemplateDeployment_b", Type = "bool"},
                                new Property { Name = "resultDescription_Summary_EndDateTimeUtc_s", Type = "String"},
                                new Property { Name = "resultDescription_Summary_DurationInMinutes_s", Type = "String"},
                                new Property { Name = "resource_originRunId_s", Type = "String"},
                                new Property { Name = "properties_enabledForDiskEncryption_b", Type = "bool"},
                                new Property { Name = "resource_actionName_s", Type = "String"},
                                new Property { Name = "correlation_actionTrackingId_g", Type = "String"},
                                new Property { Name = "resultDescription_Summary_EndDateTimeUtc_t", Type = "DateTime"},
                                new Property { Name = "resultDescription_Summary_DurationInMinutes_d", Type = "real"},
                                new Property { Name = "conditions_protocols_s", Type = "String"},
                                new Property { Name = "identity_claim_ipaddr_s", Type = "String"},
                                new Property { Name = "ElasticPoolName_s", Type = "String"},
                                new Property { Name = "identity_claim_http_schemas_microsoft_com_claims_authnmethodsreferences_s", Type = "String"},
                                new Property { Name = "RunOn_s", Type = "String"},
                                new Property { Name = "query_hash_s", Type = "String"},
                                new Property { Name = "SourceSystem", Type = "String"},
                                new Property { Name = "MG", Type = "String"},
                                new Property { Name = "ManagementGroupName", Type = "String"},
                                new Property { Name = "Computer", Type = "String"},
                                new Property { Name = "requestBytes_s", Type = "String"},
                                new Property { Name = "responseBytes_s", Type = "String"},
                                new Property { Name = "socketIp_s", Type = "String"},
                                new Property { Name = "timeTaken_s", Type = "String"},
                                new Property { Name = "securityProtocol_s", Type = "String"},
                                new Property { Name = "endpoint_s", Type = "String"},
                                new Property { Name = "rulesEngineMatchNames_s", Type = "String"},
                                new Property { Name = "backendHostname_s", Type = "String"},
                                new Property { Name = "isReceivedFromClient_b", Type = "bool"},
                                new Property { Name = "httpStatusCode_s", Type = "String"},
                                new Property { Name = "httpStatusDetails_s", Type = "String"},
                                new Property { Name = "pop_s", Type = "String"},
                                new Property { Name = "cacheStatus_s", Type = "String"},
                                new Property { Name = "socketIP_s", Type = "String"},
                                new Property { Name = "policy_s", Type = "String"},
                                new Property { Name = "trackingReference_s", Type = "String"},
                                new Property { Name = "policyMode_s", Type = "String"},
                                new Property { Name = "details_matches_s", Type = "String"},
                                new Property { Name = "identity_claim_http_schemas_xmlsoap_org_ws_2005_05_identity_claims_name_s", Type = "String"},
                                new Property { Name = "resource_sourceTriggerHistoryName_s", Type = "String"},
                                new Property { Name = "secretProperties_attributes_enabled_b", Type = "bool"},
                                new Property { Name = "addedAccessPolicy_TenantId_g", Type = "String"},
                                new Property { Name = "addedAccessPolicy_ObjectId_g", Type = "String"},
                                new Property { Name = "addedAccessPolicy_Permissions_keys_s", Type = "String"},
                                new Property { Name = "addedAccessPolicy_Permissions_secrets_s", Type = "String"},
                                new Property { Name = "addedAccessPolicy_Permissions_certificates_s", Type = "String"},
                                new Property { Name = "properties_enableRbacAuthorization_b", Type = "bool"},
                                new Property { Name = "retryHistory_s", Type = "String"},
                                new Property { Name = "properties_networkAcls_bypass_s", Type = "String"},
                                new Property { Name = "properties_networkAcls_defaultAction_s", Type = "String"},
                                new Property { Name = "ruleGroup_s", Type = "String"},
                                new Property { Name = "transactionId_s", Type = "String"},
                                new Property { Name = "originalHost_s", Type = "String"},
                                new Property { Name = "error_code_s", Type = "String"},
                                new Property { Name = "error_message_s", Type = "String"},
                                new Property { Name = "clientIp_s", Type = "String"},
                                new Property { Name = "clientPort_s", Type = "String"},
                                new Property { Name = "ruleSetType_s", Type = "String"},
                                new Property { Name = "ruleSetVersion_s", Type = "String"},
                                new Property { Name = "ruleId_s", Type = "String"},
                                new Property { Name = "action_s", Type = "String"},
                                new Property { Name = "site_s", Type = "String"},
                                new Property { Name = "details_message_s", Type = "String"},
                                new Property { Name = "details_data_s", Type = "String"},
                                new Property { Name = "details_file_s", Type = "String"},
                                new Property { Name = "details_line_s", Type = "String"},
                                new Property { Name = "hostname_s", Type = "String"},
                                new Property { Name = "correlation_clientTrackingId_g", Type = "String"},
                                new Property { Name = "tags__type_s", Type = "String"},
                                new Property { Name = "msg_s", Type = "String"},
                                new Property { Name = "tags_LogicAppsCategory_s", Type = "String"},
                                new Property { Name = "Type", Type = "String"},
                                new Property { Name = "_ResourceId", Type = "String"}
                       }
                    },
                       new TableSchema
                     {
                        Name = "ProofPointTAPMessagesDelivered_CL",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "threatsInfoMap_s" , Type = "Dynamic"},
                                new Property { Name = "messageParts_s" , Type = "Dynamic"},
                                new Property { Name = "sender_s" , Type = "String"},
                                new Property { Name = "senderIP_s" , Type = "String"},
                                new Property { Name = "recipient_s" , Type = "String"},
                                new Property { Name = "subject_s" , Type = "String"},
                                new Property { Name = "threatType" , Type = "String"},
                                new Property { Name = "classification" , Type = "String"},
                                new Property { Name = "filename" , Type = "String"},
                       }
                    },
                            new TableSchema
                     {
                        Name = "PulseConnectSecure",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "Messages" , Type = "String"},
                                new Property { Name = "User" , Type = "String"},
                                new Property { Name = "Computer" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "ProofPointTAPClicksPermitted_CL",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "threatsInfoMap_s" , Type = "String"},
                                new Property { Name = "messageParts_s" , Type = "String"},
                                new Property { Name = "sender_s" , Type = "String"},
                                new Property { Name = "senderIP_s" , Type = "String"},
                                new Property { Name = "recipient_s" , Type = "String"},
                                new Property { Name = "subject_s" , Type = "String"},
                                new Property { Name = "clickTime_t" , Type = "DateTime"},
                                new Property { Name = "url_s" , Type = "String"},
                                new Property { Name = "classification_s" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "QualysHostDetection_CL",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "Detections_s" , Type = "Dynamic"},
                                new Property { Name = "NetBios_s" , Type = "String"},
                                new Property { Name = "IPAddress" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "SophosXGFirewall",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "Log_Type" , Type = "String"},
                                new Property { Name = "Status" , Type = "String"},
                                new Property { Name = "Src_IP" , Type = "String"},
                                new Property { Name = "Dst_Port" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "SymantecProxySG",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "sc_filter_result" , Type = "String"},
                                new Property { Name = "c_ip" , Type = "String"},
                                new Property { Name = "cs_host" , Type = "String"},
                                new Property { Name = "cs_categories" , Type = "Dynamic"},
                                new Property { Name = "sc_filter_result" , Type = "String"},
                                new Property { Name = "cs_userdn" , Type = "String"},
                                new Property { Name = "Computer" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "SymantecVIP",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "RADIUSAuth" , Type = "String"},
                                new Property { Name = "ClientIP" , Type = "String"},
                                new Property { Name = "User" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "CarbonBlackNotifications_CL",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "threatHunterInfo_time_d" , Type = "DateTime"},
                                new Property { Name = "threatHunterInfo_score_d" , Type = "Int"},
                                new Property { Name = "threatHunterInfo_reportName_s" , Type = "String"},
                                new Property { Name = "deviceInfo_deviceName_s" , Type = "String"},
                                new Property { Name = "deviceInfo_internalIpAddress_s" , Type = "String"},
                                new Property { Name = "deviceInfo_externalIpAddress_s" , Type = "String"},
                       }
                    },
                     new TableSchema
                     {
                        Name = "CarbonBlackEvents_CL",
                        Properties = new Property[]
                       {
                                new Property { Name = "TimeGenerated" , Type = "DateTime"},
                                new Property { Name = "eventTime_d" , Type = "DateTime"},
                                new Property { Name = "targetApp_effectiveReputation_s" , Type = "String"},
                                new Property { Name = "deviceDetails_deviceName_s" , Type = "String"},
                                new Property { Name = "deviceDetails_deviceIpAddress_s" , Type = "String"},
                                new Property { Name = "processDetails_fullUserName_s" , Type = "String"},
                                new Property { Name = "processDetails_targetName_s" , Type = "String"},
                       }
                    },
            };
        }
    }

}

