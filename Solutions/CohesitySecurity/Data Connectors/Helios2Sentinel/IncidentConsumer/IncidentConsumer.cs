using Azure.Identity;
using Microsoft.Identity.Client;
using Azure.Security.KeyVault.Secrets;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System.Dynamic;
using System.IO;
using System.Net.Http.Headers;
using System.Net.Http;
using System.Net;
using System.Text.Json;
using System.Text;
using System.Threading.Tasks;
using System;

namespace IncidentConsumer
{
    public class IncidentConsumer
    {
        private static string keyVaultName = Environment.GetEnvironmentVariable("keyVaultName");
        string TenantId = Environment.GetEnvironmentVariable("TenantId");
        string ClientId = GetSecret("ClientId");
        string ClientKey = GetSecret("ClientKey");
        const string ARM_ENDPOINT = "https://management.azure.com/";

        private static string GetSecret(string secretName)
        {
            var kvUri = $"https://{IncidentConsumer.keyVaultName}.vault.azure.net";
            var secretClient = new SecretClient(new Uri(kvUri), new DefaultAzureCredential());
            var secret = secretClient.GetSecret(secretName);
            return  secret.Value.Value;
        }

        /*
         * need to rewrite GetAccessTokenAsync function
         * as it uses obsolete technology to get the bearer token.
         */
        internal async Task<string> GetAccessTokenAsync(string uri, ILogger log)
        {
            try
            {
                string authority = $"https://login.microsoftonline.com/{TenantId}";
                IConfidentialClientApplication app = ConfidentialClientApplicationBuilder.Create(ClientId)
                                                     .WithClientSecret(ClientKey)
                                                     .WithAuthority(authority)
                                                     .Build();
                var authResult = await app.AcquireTokenForClient(
                                     new[] { uri })
                                 .ExecuteAsync()
                                 .ConfigureAwait(false);
                return authResult.AccessToken;
            }
            catch (Exception ex)
            {
                log.LogError("GetAccessTokenAsync uri --> " + uri);
                log.LogError("GetAccessTokenAsync ex --> " + ex.Message);
                return null;
            }
        }

        private static string GetResponseStream(HttpResponseMessage response)
        {
            Stream dataObjects = response.Content.ReadAsStreamAsync().Result;
            StreamReader reader = new StreamReader(dataObjects);
            return reader.ReadToEnd();
        }

        private static string DoPUT(string URI, string body, String token, ILogger log)
        {
            try
            {
                // **** Call the Http Client Service ****
                HttpClient client = new HttpClient();
                var jsonContent = new StringContent(body, Encoding.UTF8, "application/json");

                // Add an Accept header for JSON format.
                client.DefaultRequestHeaders.Add("Authorization", "Bearer " + token);
                client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                HttpResponseMessage response = client.PutAsync(URI, jsonContent).Result;
                return GetResponseStream(response);
            }
            catch (Exception ex)
            {
                log.LogError("doPUT URI --> " + URI);
                log.LogError("doPUT body --> " + body);
                log.LogError("doPUT ex --> " + ex.Message);
                return null;
            }
        }

        [FunctionName("IncidentConsumer")]
        public void Run([QueueTrigger("cohesity-incidents", Connection = "AzureWebJobsStorage")]string queueItem, ILogger log)
        {
            log.LogInformation("queueItem --> " + queueItem);
            string token = GetAccessTokenAsync($"{ARM_ENDPOINT}.default", log).Result;
            log.LogInformation("token --> " + token);
            string subscription = Environment.GetEnvironmentVariable("subscription");
            string resourceGroup = Environment.GetEnvironmentVariable("resourceGroup");
            string workspace = Environment.GetEnvironmentVariable("Workspace");
            dynamic body = JsonConvert.DeserializeObject(queueItem);
            string incidentID = Guid.NewGuid().ToString();
            string URI = $"{ARM_ENDPOINT}subscriptions/{subscription}/resourceGroups/{resourceGroup}/providers/Microsoft.OperationalInsights/workspaces/{workspace}/providers/Microsoft.SecurityInsights/incidents/{incidentID}?api-version=2021-10-01";
            string result = DoPUT(URI, body.ToString(), token, log);
            log.LogInformation("result --> " + result);
        }
    }
}
