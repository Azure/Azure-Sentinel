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

namespace AzureSentinel_ManagementAPI.IncidentRelation
{
    class IncidentRelationController
    {
        private readonly AzureSentinelApiConfiguration[] azureConfigs;
        private readonly AuthenticationService authenticationService;
        private const string Domain = "https://management.azure.com";

        public IncidentRelationController(
            AzureSentinelApiConfiguration[] azureConfig,
            AuthenticationService authenticationService
        )
        {
            azureConfigs = azureConfig;
            this.authenticationService = authenticationService;
        }

        /// <summary>
        /// Create an incident relation for a single instance, connecting incident and bookmark
        /// </summary>
        /// <param name="incidentId"></param>
        /// <param name="bookmarkId"></param>
        /// <returns></returns>
        public async Task<string> CreateIncidentRelation(string incidentId, string bookmarkId)
        {
            try
            {
                var insId = Utils.SelectInstance(azureConfigs);

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
        public async Task<string> DeleteIncidentRelation(string incidentId, string relationId)
        {
            try
            {
                var insId = Utils.SelectInstance(azureConfigs);

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
        public async Task<string> GetIncidentRelationByName(string incidentId, string relationId)
        {
            try
            {
                var insId = Utils.SelectInstance(azureConfigs);

                var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}/relations/{relationId}?api-version={azureConfigs[insId].PreviewApiVersion}";
                var request = new HttpRequestMessage(HttpMethod.Get, url);
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
        /// Get all incident relations under an incident
        /// </summary>
        /// <param name="incidentId"></param>
        /// <returns></returns>
        public async Task GetIncidentRelations(string incidentId)
        {
            try
            {
                var insId = Utils.SelectInstance(azureConfigs);

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

                    var resources = new JArray();
                    
                    foreach(JToken value in values)
                    {
                        var properties = value["properties"];
                        var relatedResourceId = properties!=null ? properties["relatedResourceId"]: null;
                        
                        if (relatedResourceId != null)
                        {
                            var resourceUrl = $"{Domain}{relatedResourceId}?api-version={azureConfigs[insId].ApiVersion}";
                            var resourcerequest = new HttpRequestMessage(HttpMethod.Get, resourceUrl);
                            await authenticationService.AuthenticateRequest(resourcerequest, insId);
                            var resourceHttp = new HttpClient();
                            var resourceRes = await resourceHttp.SendAsync(resourcerequest);
                            
                            if (resourceRes.IsSuccessStatusCode)
                            {
                                string resourceDataStr = await resourceRes.Content.ReadAsStringAsync();
                                JObject resourceData = JsonConvert.DeserializeObject<JObject>(resourceDataStr);
                                resources.Add(resourceData);
                            }
                        }
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

                    Utils.WriteJsonStringToFile($"GetIncidentRelations_{azureConfigs[insId].InstanceName}.json",
                        JsonConvert.SerializeObject(values, Formatting.Indented), false);

                    Console.WriteLine(JsonConvert.SerializeObject(values, Formatting.Indented));
                    Console.WriteLine("related resources:");
                    Console.WriteLine(JsonConvert.SerializeObject(resources, Formatting.Indented));
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
    }
}
