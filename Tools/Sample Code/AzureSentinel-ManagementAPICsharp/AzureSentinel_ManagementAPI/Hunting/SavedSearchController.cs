using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.Hunting.Models;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Serialization;

namespace AzureSentinel_ManagementAPI.Hunting
{
    public class SavedSearchController
    {
        private readonly AzureSentinelApiConfiguration[] azureConfigs;
        private readonly AuthenticationService authenticationService;
        private bool cliMode;
        private const string savedSearchApiVersion = "2020-08-01";

        public SavedSearchController(
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
        /// Create saved search
        /// </summary>
        /// <param name="insId"></param>
        /// <returns></returns>
        public async Task CreateSavedSearch(int insId)
        {
            if (insId != -1)
            {
                await CreateSavedSearchByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await CreateSavedSearchByInstance(i);
                }
            }
        }

        /// <summary>
        /// Create saved search by instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        public async Task CreateSavedSearchByInstance(int i)
        {
            var savedSearches = Utils.LoadPayload<SavedSearchPayload[]>("SavedSearchPayload.json", cliMode);

            foreach (var payload in savedSearches)
            {
                try
                {
                    var savedSearchId = Guid.NewGuid().ToString();

                    var url =
                        $"{azureConfigs[i].OperationInsightBaseUrl}/savedSearches/{savedSearchId}?api-version={savedSearchApiVersion}";

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
        /// Update saved search data by instance
        /// </summary>
        /// <param name="savedSearchId"></param>
        /// <param name="insId"></param>
        /// <returns></returns>
        public async Task<string> UpdateSavedSearch(string savedSearchId, int insId)
        {
            var savedSearch = await GetSavedSearchById(savedSearchId, insId);

            try
            {
                JObject jobject = JObject.Parse(savedSearch);
                var savedSearchObj = JsonConvert.DeserializeObject<SavedSearchPayload>(jobject.ToString());

                var savedSearchs = Utils.LoadPayload<SavedSearchPayload[]>("SavedSearchPayload.json", cliMode);
                // Get the first one to update
                var payload = savedSearchs[0];
                payload.Etag = savedSearchObj.Etag;

                var url = $"{azureConfigs[insId].OperationInsightBaseUrl}/savedSearches/{savedSearchId}?api-version={savedSearchApiVersion}";

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
        /// Delete saved search by id and instance
        /// </summary>
        /// <param name="savedSearchId"></param>
        /// <param name="insId"></param>
        /// <returns></returns>
        public async Task<string> DeleteSavedSearch(string savedSearchId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].OperationInsightBaseUrl}/savedSearches/{savedSearchId}?api-version={savedSearchApiVersion}";

                var request = new HttpRequestMessage(HttpMethod.Delete, url);
                await authenticationService.AuthenticateRequest(request, insId);

                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode) return await response.Content.ReadAsStringAsync();

                if (response.StatusCode == HttpStatusCode.NotFound)
                    throw new Exception("Not found, please create a new SavedSearch first...");

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
        /// Get a specific saved search by id and instance
        /// </summary>
        /// <param name="savedSearchId"></param>
        /// <param name="i"></param>
        /// <returns></returns>
        public async Task<string> GetSavedSearchById(string savedSearchId, int i)
        {
            try
            {
                var url = $"{azureConfigs[i].OperationInsightBaseUrl}/savedSearches/{savedSearchId}?api-version={savedSearchApiVersion}";
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

        public async Task GetSavedSearches(int insId)
        {
            if (insId != -1)
            {
                await GetSavedSearchesByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await GetSavedSearchesByInstance(i);
                }
            }
        }

        /// <summary>
        /// Get all saved searches by instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        private async Task GetSavedSearchesByInstance(int i)
        {
            try
            {
                var url = $"{azureConfigs[i].OperationInsightBaseUrl}/savedSearches?api-version={savedSearchApiVersion}";
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
                    Utils.WriteJsonStringToFile($"GetSavedSearches_{azureConfigs[i].InstanceName}.json", cliMode, formattedRes, false);
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
