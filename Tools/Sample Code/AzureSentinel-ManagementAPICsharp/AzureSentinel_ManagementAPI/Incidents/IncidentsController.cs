using System;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.Incidents.Models;
using AzureSentinel_ManagementAPI.Incidents.Models.Comments;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Serialization;

namespace AzureSentinel_ManagementAPI.Incidents
{
    public class IncidentsController
    {
        public const string INCIDENT_NAME = "incident-1";
        private const string INCIDENT_COMMENT_NAME = "incident-comment-1";
        private string incidentId = Guid.NewGuid().ToString();
        private string commentId = Guid.NewGuid().ToString();

        private readonly AzureSentinelApiConfiguration[] azureConfigs;
        private readonly AuthenticationService authenticationService;
        private bool cliMode;

        public IncidentsController(
            AzureSentinelApiConfiguration[] azureConfig,
            IConfigurationRoot rawConfig,
            AuthenticationService authenticationService)
        {
            azureConfigs = azureConfig;
            this.authenticationService = authenticationService;
            cliMode = rawConfig.GetValue<bool>("Climode");
        }

        /// <summary>
        /// Create an incident for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task CreateIncident(int insId = -1)
        {            
            if (insId != -1)
            {
                await CreateIncidentByInstance(insId);
            } 
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await CreateIncidentByInstance(i);
                }
            }
        }

        /// <summary>
        /// Create an incident for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        private async Task CreateIncidentByInstance(int i)
        {
            var incidents = Utils.LoadPayload<IncidentPayload[]>("IncidentPayload.json", cliMode);
            
            foreach (var payload in incidents)
            {
                try
                {
                    incidentId = Guid.NewGuid().ToString();
                    var url = $"{azureConfigs[i].BaseUrl}/incidents/{incidentId}?api-version={azureConfigs[i].ApiVersion}";

                    var serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
                    {
                        ContractResolver = new DefaultContractResolver
                        {
                            NamingStrategy = new CamelCaseNamingStrategy()
                        }
                    });

                    var request = new HttpRequestMessage(HttpMethod.Put, url)
                    {
                        Content = new StringContent(serialized, Encoding.UTF8, "application/json")
                    };
                    await authenticationService.AuthenticateRequest(request, i);

                    var http = new HttpClient();
                    var response = await http.SendAsync(request);

                    if (response.IsSuccessStatusCode)
                    {
                        var res = await response.Content.ReadAsStringAsync();
                        Console.WriteLine(JToken.Parse(res).ToString(Formatting.Indented));
                        continue;
                    }

                    var error = await response.Content.ReadAsStringAsync();
                    var formatted = JsonConvert.DeserializeObject(error);
                    throw new WebException("Error calling the API: \n" +
                                                JsonConvert.SerializeObject(formatted, Formatting.Indented));
                }
                catch (Exception ex)
                {
                    throw new Exception($"Something went wrong on {azureConfigs[i].InstanceName}: \n"
                        + ex.Message);
                }
            }
        }

        /// <summary>
        /// Update an incident by id
        /// </summary>
        /// <param name="incidentId"></param>
        /// <returns></returns>
        public async Task<string> UpdateIncident(string incidentId, int insId)
        {
            var incident = await GetIncidentById(incidentId, insId);

            try
            {
                JObject jobject = JObject.Parse(incident);
                var incidentObj = JsonConvert.DeserializeObject<IncidentPayload>(jobject.ToString());

                var incidents = Utils.LoadPayload<IncidentPayload[]>("IncidentPayload.json", cliMode);
                // Get the first one to update
                var payload = incidents[0];
                payload.Etag = incidentObj.Etag;

                var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}?api-version={azureConfigs[insId].ApiVersion}";

                var serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
                {
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
        /// Batch update incidents for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task BatchUpdateIncidents(int insId)
        {           
            if (insId != -1)
            {
                await BatchUpdateIncidentsByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await BatchUpdateIncidentsByInstance(i);
                }
            }
        }

        /// <summary>
        /// Batch update incidents for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        private async Task BatchUpdateIncidentsByInstance(int i)
        {
            var incidentUpdates = Utils.LoadPayload<IncidentPayload[]>("IncidentPayload.json", cliMode);
            var insName = azureConfigs[i].InstanceName;
            try
            {
                var incidents = await GetIncidentsByInstance(i, azureConfigs[i].FilterQuery);

                foreach (var incidentObj in incidents)
                {
                    // Get the first one to update
                    var payload = incidentUpdates[0];
                    var etag = (string)incidentObj["etag"];
                    payload.Etag = etag;
                    var incidentId = (string)incidentObj["name"];

                    var url = $"{azureConfigs[i].BaseUrl}/incidents/{incidentId}?api-version={azureConfigs[i].ApiVersion}";

                    var serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
                    {
                        ContractResolver = new DefaultContractResolver
                        {
                            NamingStrategy = new CamelCaseNamingStrategy()
                        }
                    });

                    var request = new HttpRequestMessage(HttpMethod.Put, url)
                    {
                        Content = new StringContent(serialized, Encoding.UTF8, "application/json")
                    };
                    await authenticationService.AuthenticateRequest(request, i);

                    var http = new HttpClient();
                    var response = await http.SendAsync(request);

                    if (response.IsSuccessStatusCode)
                    {
                        var res = await response.Content.ReadAsStringAsync();
                        Console.WriteLine(JToken.Parse(res).ToString(Formatting.Indented));
                        continue;
                    }

                    var error = await response.Content.ReadAsStringAsync();
                    var formatted = JsonConvert.DeserializeObject(error);
                    Console.WriteLine("Error calling the API: \n" +
                                           JsonConvert.SerializeObject(formatted, Formatting.Indented));

                }
            }
            catch (Exception ex)
            {
                throw new Exception($"Something went wrong on {insName}: \n"
                    + ex.Message);
            }
        }

        /// <summary>
        /// Batch update incidents from json payload file
        /// </summary>
        /// <returns></returns>
        public async Task BatchUpdateIncidentsFromJson()
        {
            var insId = Utils.SelectInstance(azureConfigs);
            var incidentUpdates = Utils.LoadPayload<IncidentPayload[]>("GetIncidents0.json", cliMode);
            var incidentIds = incidentUpdates.Select(x => x.Name);
            Console.WriteLine("Updating incidents:");
            Console.WriteLine("[{0}]", string.Join(", ", incidentIds));
            
            foreach (var payload in incidentUpdates)
            {
                try
                {
                    var incidentId = payload.Name;

                    var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}?api-version={azureConfigs[insId].ApiVersion}";

                    var serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
                    {
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

                    if (response.IsSuccessStatusCode)
                    {
                        var res = await response.Content.ReadAsStringAsync();
                        Console.WriteLine(JToken.Parse(res).ToString(Formatting.Indented));
                        continue;
                    }

                    var error = await response.Content.ReadAsStringAsync();
                    var formatted = JsonConvert.DeserializeObject(error);
                    Console.WriteLine("Error calling the API: \n" +
                                           JsonConvert.SerializeObject(formatted, Formatting.Indented));
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Something went wrong: \n" + ex.Message);
                }
            }
        }

        /// <summary>
        /// Delete an incident by id
        /// </summary>
        /// <param name="incidentId"></param>
        /// <returns></returns>
        public async Task<string> DeleteIncident(string incidentId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}?api-version={azureConfigs[insId].ApiVersion}";

                var request = new HttpRequestMessage(HttpMethod.Delete, url);
                await authenticationService.AuthenticateRequest(request, insId);

                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode) return await response.Content.ReadAsStringAsync();
                
                if (response.StatusCode == HttpStatusCode.NotFound)
                    throw new Exception("Not found, please create a new Incident first...");

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
        /// Get an incident by id
        /// </summary>
        /// <param name="incidentId"></param>
        /// <param name="i"></param>
        /// <returns></returns>
        public async Task<string> GetIncidentById(string incidentId, int i)
        {
            try
            {
                var url = $"{azureConfigs[i].BaseUrl}/incidents/{incidentId}?api-version={azureConfigs[i].ApiVersion}";
                var request = new HttpRequestMessage(HttpMethod.Get, url);
                await authenticationService.AuthenticateRequest(request, i);
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
        /// Get all incidents for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task GetIncidents(int insId)
        {           
            if (insId != -1)
            {
                var values = await GetIncidentsByInstance(insId, azureConfigs[insId].FilterQuery);
                var formattedRes = JsonConvert.SerializeObject(values, Formatting.Indented);
                Utils.WriteJsonStringToFile($"GetIncidents_{azureConfigs[insId].InstanceName}.json", cliMode,formattedRes, false);
                Console.WriteLine(formattedRes);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    var values = await GetIncidentsByInstance(i, azureConfigs[i].FilterQuery);
                    var formattedRes = JsonConvert.SerializeObject(values, Formatting.Indented);
                    Utils.WriteJsonStringToFile($"GetIncidents_{azureConfigs[i].InstanceName}.json", cliMode, formattedRes, false);
                    Console.WriteLine(formattedRes);
                    continue;
                }
            }
        }

        /// <summary>
        /// Get all incidents for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <param name="filter"></param>
        /// <returns></returns>
        public async Task<JArray> GetIncidentsByInstance(int i, string filter = "")
        {
            try
            {
                var insName = azureConfigs[i].InstanceName;
                var url = $"{azureConfigs[i].BaseUrl}/incidents?api-version={azureConfigs[i].ApiVersion}";
                
                if (!string.IsNullOrEmpty(filter))
                {
                    url = $"{url}{filter}";
                }

                var request = new HttpRequestMessage(HttpMethod.Get, url);
                await authenticationService.AuthenticateRequest(request, i);
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
                            await authenticationService.AuthenticateRequest(request, i);
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
                                Console.WriteLine($"Error calling the nextLink on {insName}: \n" + err);
                                break;
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error in parsing nextLink on {insName}: \n" + ex.Message);
                            break;
                        }
                    }

                    return values;
                }

                var error = await response.Content.ReadAsStringAsync();
                var formatted = JsonConvert.DeserializeObject(error);
                throw new WebException($"Error calling the API {insName}: \n" +
                                       JsonConvert.SerializeObject(formatted, Formatting.Indented));
            }
            catch (Exception ex)
            {
                throw new Exception($"Something went wrong on {azureConfigs[i].InstanceName}: \n"
                    + ex.Message);
            }
        }

        /// <summary>
        /// Create an incident comment for an incident
        /// </summary>
        /// <param name="incidentId"></param>
        /// <returns></returns>
        public async Task CreateIncidentComment(string incidentId)
        {
            var insId = Utils.SelectInstance(azureConfigs);

            var comments = Utils.LoadPayload<IncidentCommentPayload[]>("IncidentCommentPayload.json", cliMode);
            
            foreach (var payload in comments)
            {
                try
                {
                    commentId = Guid.NewGuid().ToString();
                    var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}/comments/{commentId}?api-version={azureConfigs[insId].ApiVersion}";

                    var serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
                    {
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

                    if (response.IsSuccessStatusCode)
                    {
                        var res = await response.Content.ReadAsStringAsync();
                        Console.WriteLine(JToken.Parse(res).ToString(Formatting.Indented));
                        continue;
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

        /// <summary>
        /// Get an incident comment by id
        /// </summary>
        /// <param name="incidentId"></param>
        /// <param name="commentId"></param>
        /// <returns></returns>
        public async Task<string> GetIncidentCommentById(string incidentId, string commentId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}/comments/{commentId}?api-version={azureConfigs[insId].ApiVersion}";
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
        /// Get all incident comments under an incident
        /// </summary>
        /// <param name="incidentId"></param>
        /// <returns></returns>
        public async Task<string> GetAllIncidentComments(string incidentId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/incidents/{incidentId}/comments?api-version={azureConfigs[insId].ApiVersion}";
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

                    Utils.WriteJsonStringToFile($"GetAllIncidentComments_{azureConfigs[insId].InstanceName}.json", cliMode, JsonConvert.SerializeObject(values, Formatting.Indented), false);
                    return res;
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