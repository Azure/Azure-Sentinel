using System;
using System.Reflection;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.IncidentRelation.Models;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;
using Microsoft.Extensions.Configuration;

namespace AzureSentinel_ManagementAPI.IncidentRelation
{
    class IncidentRelationController
    {
        private readonly AzureSentinelApiConfiguration[] azureConfigs;
        private readonly AuthenticationService authenticationService;
        private const string Domain = "https://management.azure.com";
        private bool cliMode;

        public IncidentRelationController(
            AzureSentinelApiConfiguration[] azureConfig,
            IConfigurationRoot rawConfig,
            AuthenticationService authenticationService
        )
        {
            azureConfigs = azureConfig;
            this.authenticationService = authenticationService;
            cliMode = rawConfig.GetValue<bool>("Climode");
        }

        /// <summary>
        /// Create an incident relation for a single instance, connecting incident and bookmark
        /// </summary>
        /// <param name="incidentId"></param>
        /// <param name="bookmarkId"></param>
        /// <returns></returns>
        public async Task<string> CreateIncidentRelation(string incidentId, string bookmarkId, int insId)
        {
            try
            {
                var payload = new RelationPayload
                {
                    PropertiesPayload = new RelationPropertiesPayload
                    {
                        RelatedResourceId = $"{azureConfigs[insId].BaseUrl}/bookmarks/{bookmarkId}"
                    }
                };

                var relationId = Guid.NewGuid().ToString();
                var url =
                $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}/relations/{relationId}?api-version={azureConfigs[insId].PreviewApiVersion}";

                var serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
                {
                    NullValueHandling = NullValueHandling.Ignore,
                    ContractResolver = new DefaultContractResolver
                    {

                        NamingStrategy = new CamelCaseNamingStrategy()
                    }
                });

                var request = new HttpRequestMessage(HttpMethod.Put, url)
                {
                    Content = new StringContent(serialized, Encoding.UTF8, "application/json")
                };
                await authenticationService.AuthenticateRequest(request, insId);

                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode) return await response.Content.ReadAsStringAsync();

                var error = await response.Content.ReadAsStringAsync();
                var formatted = JsonConvert.DeserializeObject(error);
                throw new WebException("Error calling the API: \n" +
                                       JsonConvert.SerializeObject(formatted, Formatting.Indented));
            }
            catch (Exception ex)
            {
                throw new Exception("Something went wrong: \n" + ex.Message);
            }
        }

        /// <summary>
        /// Delete an incident relation by id
        /// </summary>
        /// <param name="incidentId"></param>
        /// <param name="relationId"></param>
        /// <returns></returns>
        public async Task<string> DeleteIncidentRelation(string incidentId, string relationId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}/relations/{relationId}?api-version={azureConfigs[insId].PreviewApiVersion}";

                var request = new HttpRequestMessage(HttpMethod.Delete, url);
                await authenticationService.AuthenticateRequest(request, insId);

                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode) return await response.Content.ReadAsStringAsync();
                
                if (response.StatusCode == HttpStatusCode.NotFound)
                    throw new Exception("Not found, please create a new incident relation first...");

                var error = await response.Content.ReadAsStringAsync();
                var formatted = JsonConvert.DeserializeObject(error);
                throw new WebException("Error calling the API: \n" +
                                       JsonConvert.SerializeObject(formatted, Formatting.Indented));
            }
            catch (Exception ex)
            {
                throw new Exception("Something went wrong: \n" + ex.Message);
            }
        }

        /// <summary>
        /// Get an incident relation by id
        /// </summary>
        /// <param name="incidentId"></param>
        /// <param name="relationId"></param>
        /// <returns></returns>
        public async Task GetIncidentRelationByName(string incidentId, string relationId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}/relations/{relationId}?api-version={azureConfigs[insId].PreviewApiVersion}";
                var request = new HttpRequestMessage(HttpMethod.Get, url);
                await authenticationService.AuthenticateRequest(request, insId);
                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode)
                {
                    string res = await response.Content.ReadAsStringAsync();
                    JObject value = JsonConvert.DeserializeObject<JObject>(res);

                    Console.WriteLine(JsonConvert.SerializeObject(value, Formatting.Indented));

                    var resources = new JObject();
                    resources.Add("incidentRelationId", relationId);

                    var properties = value["properties"];
                    var relatedResourceId = properties != null ? properties["relatedResourceId"] : null;
                    var resourceDataStr = string.Empty;

                    if (relatedResourceId != null)
                    {
                        var resourceType = properties["relatedResourceType"].ToString();

                        if (resourceType == "Microsoft.SecurityInsights/bookmarks")
                        {
                            var resourceUrl = $"{Domain}{relatedResourceId}?api-version={azureConfigs[insId].ApiVersion}";
                            var resourcerequest = new HttpRequestMessage(HttpMethod.Get, resourceUrl);
                            await authenticationService.AuthenticateRequest(resourcerequest, insId);
                            var resourceHttp = new HttpClient();
                            var resourceRes = await resourceHttp.SendAsync(resourcerequest);

                            if (resourceRes.IsSuccessStatusCode)
                            {
                                resourceDataStr = await resourceRes.Content.ReadAsStringAsync();
                            }
                        }
                        else if (resourceType == "Microsoft.SecurityInsights/entities")
                        {
                            var resourceUrl = $"{Domain}{relatedResourceId}/expand?api-version={azureConfigs[insId].PreviewApiVersion}";
                            var resourceKind = properties["relatedResourceKind"].ToString();
                            var expansionId = GetExpansionId(resourceKind);
                            var payload = new RelationEntityPayload
                            {
                                ExpansionId = expansionId
                            };

                            var serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
                            {
                                NullValueHandling = NullValueHandling.Ignore,
                                ContractResolver = new DefaultContractResolver
                                {
                                    NamingStrategy = new CamelCaseNamingStrategy()
                                }
                            });

                            var resourcerequest = new HttpRequestMessage(HttpMethod.Post, resourceUrl)
                            {
                                Content = new StringContent(serialized, Encoding.UTF8, "application/json")
                            };
                            await authenticationService.AuthenticateRequest(resourcerequest, insId);
                            var resourceHttp = new HttpClient();
                            var resourceRes = await resourceHttp.SendAsync(resourcerequest);

                            if (resourceRes.IsSuccessStatusCode)
                            {
                                resourceDataStr = await resourceRes.Content.ReadAsStringAsync();
                            }
                        }

                        if (resourceDataStr != string.Empty)
                        {
                            JObject resourceData = JsonConvert.DeserializeObject<JObject>(resourceDataStr);
                            resources.Merge(resourceData);
                        }
                    }

                    Console.WriteLine("related resources:");
                    var serializedResources = JsonConvert.SerializeObject(resources, Formatting.Indented);
                    Console.WriteLine(serializedResources);
                    Utils.WriteJsonStringToFile($"GetIncidentRelationByNameResources_{azureConfigs[insId].InstanceName}.json",
                        cliMode, serializedResources, false);

                    return;
                }

                var error = await response.Content.ReadAsStringAsync();
                var formatted = JsonConvert.DeserializeObject(error);
                throw new WebException("Error calling the API: \n" +
                                       JsonConvert.SerializeObject(formatted, Formatting.Indented));
            }
            catch (Exception ex)
            {
                throw new Exception("Something went wrong: \n" + ex.Message);
            }
        }

        /// <summary>
        /// Get all incident relations under an incident, and get all entities under the incident
        /// </summary>
        /// <param name="incidentId"></param>
        /// <returns></returns>
        public async Task GetEntitiesforIncident(string incidentId, int insId)
        {
            await GetIncidentRelationsAndEntities(incidentId, EntityKind.SecurityAlert, true, insId);
        }

        /// <summary>
        /// Get all incident relations under an incident, and get all entities under the incident
        /// </summary>
        /// <param name="incidentId"></param>
        /// <returns></returns>
        public async Task GetIncidentEntitiesbyEntityType(string incidentId, int insId)
        {
            // Console.WriteLine(Utils.GetString("Select_Entity_Kind"));
            var entityKind = Utils.SelectKind<EntityKind>();
            await GetIncidentRelationsAndEntities(incidentId, entityKind, false, insId);
        }

        /// <summary>
        /// Get all incident relations and entities under an incident
        /// </summary>
        /// <param name="incidentId"></param>
        /// <param name="entityKind"></param>
        /// <param name="allKind"></param>
        /// <returns></returns>
        public async Task GetIncidentRelationsAndEntities(string incidentId, EntityKind entityKind, bool allKind, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}/relations?api-version={azureConfigs[insId].PreviewApiVersion}";
                var request = new HttpRequestMessage(HttpMethod.Get, url);
                await authenticationService.AuthenticateRequest(request, insId);
                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode)
                {
                    string res = await response.Content.ReadAsStringAsync();
                    JObject result = JsonConvert.DeserializeObject<JObject>(res);
                    var values = result["value"] as JArray;

                    if (values == null)
                    {
                        values = new JArray();
                    }

                    int callTimes = 1;

                    while (result.ContainsKey("nextLink") && callTimes < 100)
                    {
                        try
                        {
                            var nextLink = result["nextLink"].ToString();
                            request = new HttpRequestMessage(HttpMethod.Get, nextLink);
                            await authenticationService.AuthenticateRequest(request, insId);
                            var nextResponse = await http.SendAsync(request);

                            if (nextResponse.IsSuccessStatusCode)
                            {
                                var newRes = await nextResponse.Content.ReadAsStringAsync();
                                JObject newResult = JsonConvert.DeserializeObject<JObject>(newRes);
                                result = newResult;
                                var newValues = result["value"] as JArray;

                                if (newValues == null)
                                {
                                    newValues = new JArray();
                                }

                                foreach (var v in newValues)
                                {
                                    values.Add(v);
                                }

                                callTimes++;
                            }
                            else
                            {
                                var err = await response.Content.ReadAsStringAsync();
                                Console.WriteLine("Error calling the nextLink: \n" + err);
                                break;
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("Error in parsing nextLink: \n" + ex.Message);
                            break;
                        }
                    }

                    var resources = new JArray();
                    foreach (JToken value in values)
                    {
                        var properties = value["properties"];
                        var relatedResourceId = properties != null ? properties["relatedResourceId"] : null;
                        var resourceDataStr = string.Empty;

                        if (relatedResourceId != null)
                        {
                            var resourceType = properties["relatedResourceType"].ToString();

                            if (resourceType == "Microsoft.SecurityInsights/bookmarks" && (allKind || entityKind == EntityKind.Bookmark))
                            {
                                var resourceUrl = $"{Domain}{relatedResourceId}?api-version={azureConfigs[insId].ApiVersion}";
                                var resourcerequest = new HttpRequestMessage(HttpMethod.Get, resourceUrl);
                                await authenticationService.AuthenticateRequest(resourcerequest, insId);
                                var resourceHttp = new HttpClient();
                                var resourceRes = await resourceHttp.SendAsync(resourcerequest);

                                if (resourceRes.IsSuccessStatusCode)
                                {
                                    resourceDataStr = await resourceRes.Content.ReadAsStringAsync();
                                }
                            }
                            else if (resourceType == "Microsoft.SecurityInsights/entities")
                            {
                                var resourceUrl = $"{Domain}{relatedResourceId}/expand?api-version={azureConfigs[insId].PreviewApiVersion}";
                                var resourceKind = properties["relatedResourceKind"].ToString();

                                var expansionId = GetExpansionId(resourceKind);
                                var payload = new RelationEntityPayload
                                {
                                    ExpansionId = expansionId
                                };

                                var serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
                                {
                                    NullValueHandling = NullValueHandling.Ignore,
                                    ContractResolver = new DefaultContractResolver
                                    {
                                        NamingStrategy = new CamelCaseNamingStrategy()
                                    }
                                });

                                var resourcerequest = new HttpRequestMessage(HttpMethod.Post, resourceUrl)
                                {
                                    Content = new StringContent(serialized, Encoding.UTF8, "application/json")
                                };
                                await authenticationService.AuthenticateRequest(resourcerequest, insId);
                                var resourceHttp = new HttpClient();
                                var resourceRes = await resourceHttp.SendAsync(resourcerequest);

                                if (resourceRes.IsSuccessStatusCode)
                                {
                                    resourceDataStr = await resourceRes.Content.ReadAsStringAsync();
                                }
                            }

                            if (resourceDataStr != string.Empty)
                            {
                                JObject resourceData = JsonConvert.DeserializeObject<JObject>(resourceDataStr);
                                if (resourceType == "Microsoft.SecurityInsights/bookmarks" && allKind)
                                {
                                    resources.Add(resourceData);
                                }
                                else
                                {
                                    var resourceValue = resourceData["value"];
                                    var entities = resourceValue != null ? resourceValue["entities"] : null;
                                    if (entities != null)
                                    {
                                        foreach (var entity in entities)
                                        {
                                            if (allKind || entity["kind"].ToString() == entityKind.ToString())
                                            {
                                                resources.Add(entity);
                                            }
                                        }
                                    }
                                }

                            }
                        }
                    }

                    Utils.WriteJsonStringToFile($"GetIncidentRelations_{azureConfigs[insId].InstanceName}.json",
                        cliMode, JsonConvert.SerializeObject(values, Formatting.Indented), false);

                    Console.WriteLine(JsonConvert.SerializeObject(values, Formatting.Indented));
                    Console.WriteLine(Utils.GetString("Related_Entities"));
                    var serializedResources = JsonConvert.SerializeObject(resources, Formatting.Indented);
                    Console.WriteLine(serializedResources);
                    var fileNamePrefix = allKind ? "GetEntitiesforIncident" : $"GetIncidentEntitiesbyEntityType_{entityKind.ToString()}";
                    Utils.WriteJsonStringToFile($"{fileNamePrefix}_{azureConfigs[insId].InstanceName}.json", cliMode,
                        serializedResources, false);
                    return;
                }

                var error = await response.Content.ReadAsStringAsync();
                var formatted = JsonConvert.DeserializeObject(error);
                throw new WebException("Error calling the API: \n" +
                                       JsonConvert.SerializeObject(formatted, Formatting.Indented));
            }
            catch (Exception ex)
            {
                throw new Exception("Something went wrong: \n" + ex.Message);
            }
        }

        /// <summary>
        /// Get entities expansion id by kind
        /// </summary>
        /// <param name="kind"></param>
        /// <returns></returns>
        private string GetExpansionId(string kind)
        {
            switch (kind)
            {
                case "SecurityAlert":
                    return "98b974fd-cc64-48b8-9bd0-3a209f5b944b";
                case "Bookmark":
                    return "27f76e63-c41b-480f-bb18-12ad2e011d49";
                case "Account":
                    return "a77992f3-25e9-4d01-99a4-5ff606cc410a";
                case "AzureResource":
                    return "4a014a1b-c5a1-499f-9f54-3f7b99b0a675";
                case "CloudApplication":
                    return "f74ad13a-ae93-47b9-8782-b1142b95d046";
                case "DnsResolution":
                    return "80218599-45b4-4402-95cc-86f9929dd43d";
                case "File":
                    return "0f0bccef-4512-4530-a866-27056a39dcd6";
                case "FileHash":
                    return "b6eaa3ad-e69b-437e-9c13-bb5273dd34ab";
                case "Host":
                    return "055a5692-555f-42bd-ac17-923a5a9994ed";
                case "Ip":
                    return "58c1516f-b78a-4d78-9e71-77c40849c27b";
                case "Malware":
                    return "b8407195-b9a3-4565-bf08-7b23e5c57e3a";
                case "Process":
                    return "63a4fa2f-f89d-4cf5-96a2-cb2479e49731";
                case "RegistryKey":
                    return "d788cd65-a7ef-448e-aa34-81185ac0e611";
                case "RegistryValue":
                    return "3a45a7e3-80e0-4e05-84db-b97bd1ae452b";
                case "Url":
                    return "7b61d5e2-4b66-40a7-bb0f-9145b445104e";
                case "IoTDevice":
                    return "4daeed0e-0e74-4f2d-990c-a958210e9dd7";
                default:
                    return string.Empty;
            }
        }
    }
}
