using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.Bookmarks.Models;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Serialization;

namespace AzureSentinel_ManagementAPI.Bookmarks
{
    public class BookmarksController
    {
        private readonly AzureSentinelApiConfiguration[] azureConfigs;
        private readonly AuthenticationService authenticationService;
        private bool cliMode;

        public BookmarksController(
            AzureSentinelApiConfiguration[] azureConfig,
            IConfigurationRoot rawConfig,
            AuthenticationService authenticationService)
        {
            azureConfigs = azureConfig;
            this.authenticationService = authenticationService;
            cliMode = rawConfig.GetValue<bool>("Climode");
        }

        /// <summary>
        /// Create a bookmark for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task CreateBookmark(int insId = -1)
        {            
            if (insId != -1)
            {
                await CreateBookmarkByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await CreateBookmarkByInstance(i);
                }
            }
        }

        /// <summary>
        /// Create a bookmark for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        private async Task CreateBookmarkByInstance(int i)
        {
            var bookmarks = Utils.LoadPayload<BookmarkPayload[]>("BookmarkPayload.json", cliMode);
            
            foreach (var payload in bookmarks)
            {
                try
                {
                    var bookmarkId = Guid.NewGuid().ToString();

                    var url = $"{azureConfigs[i].BaseUrl}/bookmarks/{bookmarkId}?api-version={azureConfigs[i].ApiVersion}";

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
        /// Delete a bookmark by id
        /// </summary>
        /// <param name="bookmarkId"></param>
        /// <returns></returns>
        public async Task<string> DeleteBookmark(string bookmarkId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/bookmarks/{bookmarkId}?api-version={azureConfigs[insId].ApiVersion}";

                var request = new HttpRequestMessage(HttpMethod.Delete, url);
                await authenticationService.AuthenticateRequest(request, insId);

                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode) return await response.Content.ReadAsStringAsync();
                
                if (response.StatusCode == HttpStatusCode.NotFound)
                    throw new Exception("Not found, please create a new Bookmark first...");
                
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
        /// Get a bookmark by id
        /// </summary>
        /// <param name="bookmarkId"></param>
        /// <returns></returns>
        public async Task<string> GetBookmarkById(string bookmarkId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/bookmarks/{bookmarkId}?api-version={azureConfigs[insId].ApiVersion}";
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
        /// Get all bookmarks for all instances or for a single instance
        /// </summary>
        /// <param name="insId"></param>
        /// <returns></returns>
        public async Task GetBookmarks(int insId = -1)
        {            
            if (insId != -1)
            {
                await GetBookmarksByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await GetBookmarksByInstance(i);
                }
            }
        }

        /// <summary>
        /// Get bookmarks for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        private async Task GetBookmarksByInstance(int i)
        {
            try
            {
                var url = $"{azureConfigs[i].BaseUrl}/bookmarks?api-version={azureConfigs[i].ApiVersion}";
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
                    Utils.WriteJsonStringToFile($"GetBookmarks_{azureConfigs[i].InstanceName}.json", cliMode, formattedRes, false);
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