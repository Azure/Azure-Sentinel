using System;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.AlertRules.Models;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Serialization;

namespace AzureSentinel_ManagementAPI.AlertRules
{
    public class AlertRulesController
    {
        private readonly AzureSentinelApiConfiguration[] azureConfigs;
        private readonly AuthenticationService authenticationService;

        public AlertRulesController(AzureSentinelApiConfiguration[] azureConfig,
            AuthenticationService authenticationService)
        {
            azureConfigs = azureConfig;
            this.authenticationService = authenticationService;
        }

        /// <summary>
        /// Create funsion alert rule for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task CreateFusionAlertRule()
        {
            var insId = Utils.SelectInstanceOrApplyAll(azureConfigs);
            
            if (insId != -1)
            {
                await CreateFusionAlertRuleByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await CreateFusionAlertRuleByInstance(i);
                }
            }
        }

        /// <summary>
        /// Create funsion alert rule for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        public async Task CreateFusionAlertRuleByInstance(int i)
        {
            var alertRules = Utils.LoadPayload<FusionAlertRulePayload[]>("FusionAlertRulePayload.json");
            
            foreach (var payload in alertRules)
            {
                try
                {
                    var ruleId = Guid.NewGuid().ToString();
                    var url =
                        $"{azureConfigs[i].BaseUrl}/alertRules/{ruleId}?api-version={azureConfigs[i].ApiVersion}";

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
        /// Create Microsoft security incident creation alert rule for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task CreateMicrosoftSecurityIncidentCreationAlertRule()
        {
            var insId = Utils.SelectInstanceOrApplyAll(azureConfigs);
            
            if (insId != -1)
            {
                await CreateMSSecurityIncidentAlertRuleByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await CreateMSSecurityIncidentAlertRuleByInstance(i);
                }
            }
        }

        /// <summary>
        /// Create Microsoft security incident creation alert rule for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        public async Task CreateMSSecurityIncidentAlertRuleByInstance(int i)
        {
            var alertRules = Utils.LoadPayload<SecurityIncidentCreationAlertRulePayload[]>("SecurityAlertRulePayload.json");
            
            foreach (var payload in alertRules)
            {
                try
                {
                    var alertRuleId = Guid.NewGuid().ToString();
                    var url =
                        $"{azureConfigs[i].BaseUrl}/alertRules/{alertRuleId}?api-version={azureConfigs[i].ApiVersion}";

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
        /// Create scheduled alert rule for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task CreateScheduledAlertRule()
        {
            var insId = Utils.SelectInstanceOrApplyAll(azureConfigs);
            
            if (insId != -1)
            {
                await CreateScheduledAlertRuleByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await CreateScheduledAlertRuleByInstance(i);
                }
            }
        }

        /// <summary>
        /// Create scheduled alert rule for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        public async Task CreateScheduledAlertRuleByInstance(int i)
        {
            var alertRules = Utils.LoadPayload<ScheduledAlertRulePayload[]>("ScheduledAlertRulePayload.json");
            
            foreach (var payload in alertRules)
            {
                try
                {
                    var alertRuleId = Guid.NewGuid().ToString();
                    var url =
                        $"{azureConfigs[i].BaseUrl}/alertRules/{alertRuleId}?api-version={azureConfigs[i].ApiVersion}";

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
        /// Delete an alert rule by id
        /// </summary>
        /// <param name="ruleId"></param>
        /// <returns></returns>
        public async Task<string> DeleteAlertRule(string ruleId)
        {
            try
            {
                var insId = Utils.SelectInstance(azureConfigs);

                var url =
                    $"{azureConfigs[insId].BaseUrl}/alertRules/{ruleId}?api-version={azureConfigs[insId].ApiVersion}";

                var request = new HttpRequestMessage(HttpMethod.Delete, url);
                await authenticationService.AuthenticateRequest(request, insId);

                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode) return await response.Content.ReadAsStringAsync();
                
                if (response.StatusCode == HttpStatusCode.NotFound)
                    throw new Exception("Not found, please create a new Alert first...");

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
        /// Get funsion alert rule by id
        /// </summary>
        /// <param name="ruleId"></param>
        /// <returns></returns>
        public async Task<string> GetFusionAlertRule(string ruleId)
        {
            return await GetAlertRuleByName(ruleId);
        }

        /// <summary>
        /// Get Microsoft security incident creation alert rule by id
        /// </summary>
        /// <param name="ruleId"></param>
        /// <returns></returns>
        public async Task<string> GetMicrosoftSecurityIdentityCreationAlertRule(string ruleId)
        {
            return await GetAlertRuleByName(ruleId);
        }

        /// <summary>
        /// Get scheduled alert rule by id
        /// </summary>
        /// <param name="ruleId"></param>
        /// <returns></returns>
        public async Task<string> GetScheduledAlertRule(string ruleId)
        {
            return await GetAlertRuleByName(ruleId);
        }

        /// <summary>
        /// Get alert rule by rule id
        /// </summary>
        /// <param name="ruleName"></param>
        /// <returns></returns>
        private async Task<string> GetAlertRuleByName(string ruleName)
        {
            try
            {
                var insId = Utils.SelectInstance(azureConfigs);

                var url = $"{azureConfigs[insId].BaseUrl}/alertRules/{ruleName}?api-version={azureConfigs[insId].ApiVersion}";
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
        /// Get all alert rules for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task GetAlertRules()
        {
            var insId = Utils.SelectInstanceOrApplyAll(azureConfigs);
            
            if (insId != -1)
            {
                await GetAlertRulesByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await GetAlertRulesByInstance(i);
                }
            }
        }

        /// <summary>
        /// Get alert rules for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        private async Task GetAlertRulesByInstance(int i)
        {
            try
            {
                var url = $"{azureConfigs[i].BaseUrl}/alertRules?api-version={azureConfigs[i].ApiVersion}";

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

                    var formattedRes = JsonConvert.SerializeObject(values, Formatting.Indented);
                    Utils.WriteJsonStringToFile($"GetAlertRules_{azureConfigs[i].InstanceName}.json", formattedRes, false);
                    Console.WriteLine(formattedRes);
                    return;
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
}