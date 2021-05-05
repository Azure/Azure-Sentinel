using System;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.Actions.Models;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Serialization;

namespace AzureSentinel_ManagementAPI.Actions
{
    public class ActionsController
    {
        private readonly AzureSentinelApiConfiguration[] azureConfigs;
        private readonly AuthenticationService authenticationService;
        private bool cliMode;

        public ActionsController(
            AzureSentinelApiConfiguration[] azureConfig,
            IConfigurationRoot rawConfig,
            AuthenticationService authenticationService)
        {
            azureConfigs = azureConfig;
            this.authenticationService = authenticationService;
            cliMode = rawConfig.GetValue<bool>("Climode");
        }

        /// <summary>
        /// Create action from payload json
        /// </summary>
        /// <param name="ruleId"></param>
        /// <returns></returns>
        public async Task CreateAction(string ruleId, int insId, string logicAppResourceId = "")
        {
            ActionRequestPayload[] actions = Utils.LoadPayload<ActionRequestPayload[]>("ActionPayload.json", cliMode);
            
            foreach (ActionRequestPayload payload in actions)
            {
                try
                {
                    string subscription = azureConfigs[insId].SubscriptionId;
                    string resourceGroup = azureConfigs[insId].ResourceGroupName;
                    payload.PropertiesPayload.LogicAppResourceId = string.Format(payload.PropertiesPayload.LogicAppResourceId, subscription, resourceGroup);

                    string actionId = Guid.NewGuid().ToString();
                    string url = $"{azureConfigs[insId].BaseUrl}/alertRules/{ruleId}/actions/{actionId}?api-version={azureConfigs[insId].ApiVersion}";
                    if (!string.IsNullOrEmpty(logicAppResourceId))
                    {
                        payload.PropertiesPayload.LogicAppResourceId = logicAppResourceId;
                    }

                    string serialized = JsonConvert.SerializeObject(payload, new JsonSerializerSettings
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
        /// Delete an action by rule id and action id
        /// </summary>
        /// <param name="ruleId"></param>
        /// <param name="actionId"></param>
        /// <returns></returns>
        public async Task<string> DeleteAction(string ruleId, string actionId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/alertRules/{ruleId}/actions/{actionId}?api-version={azureConfigs[insId].ApiVersion}";

                var request = new HttpRequestMessage(HttpMethod.Delete, url);
                await authenticationService.AuthenticateRequest(request, insId);

                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode) return await response.Content.ReadAsStringAsync();
                
                if (response.StatusCode == HttpStatusCode.NotFound)
                    throw new Exception("Not found, please create a new Action first...");
                
                
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
        /// Get an action by rule id and action id
        /// </summary>
        /// <param name="ruleId"></param>
        /// <param name="actionId"></param>
        /// <returns></returns>
        public async Task<string> GetActionById(string ruleId, string actionId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/alertRules/{ruleId}/actions/{actionId}?api-version={azureConfigs[insId].ApiVersion}";
               
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
        /// Get an action by rule id and action id by instance
        /// </summary>
        /// <param name="ruleName"></param>
        /// <param name="insId"></param>
        /// <returns></returns>
        public async Task<string> GetAlertRuleByName(string ruleName, int insId)
        {
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

        /// <summary>
        /// Get all actions under a rule
        /// </summary>
        /// <param name="ruleId"></param>
        /// <returns></returns>
        public async Task<string> GetActionsByRule(string ruleId, int insId)
        {
            try
            {
                await GetAlertRuleByName(ruleId, insId);

                var url = $"{azureConfigs[insId].BaseUrl}/alertRules/{ruleId}/actions?api-version={azureConfigs[insId].ApiVersion}";

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

                    Utils.WriteJsonStringToFile($"GetActionsByRule_{azureConfigs[insId].InstanceName}.json", cliMode, JsonConvert.SerializeObject(values, Formatting.Indented), false);
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