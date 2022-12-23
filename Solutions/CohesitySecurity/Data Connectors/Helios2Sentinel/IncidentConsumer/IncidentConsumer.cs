using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Clients.ActiveDirectory;
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
        private const string keyVaultName = "Cohesity-Vault";
        string TenantId = GetSecret("TenantId");
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
        internal async Task<string> GetAccessTokenAsync(string uri)
        {
            var credential = new ClientCredential(ClientId, ClientKey);
            var authenticationContext = new AuthenticationContext($"https://login.microsoftonline.com/{TenantId}");
            var result = await authenticationContext.AcquireTokenAsync(uri, credential);
            return result.AccessToken;
        }

        private string doPUT(string URI, string body, String token, ILogger log)
        {
            try
            {
                Uri uri = new Uri(String.Format(URI));

                // Create the request
                var httpWebRequest = (HttpWebRequest) WebRequest.Create(uri);
                httpWebRequest.Headers.Add(HttpRequestHeader.Authorization, "Bearer " + token);
                httpWebRequest.ContentType = "application/json";
                httpWebRequest.Method = "PUT";

                using (var streamWriter = new StreamWriter(httpWebRequest.GetRequestStream()))
                {
                    streamWriter.Write(body);
                    streamWriter.Flush();
                    streamWriter.Close();
                }

                // Get the response
                HttpWebResponse httpResponse = null;
                string result = null;
                httpResponse = (HttpWebResponse) httpWebRequest.GetResponse();

                using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
                {
                    result = streamReader.ReadToEnd();
                }
                return result;
            }
            catch (Exception ex)
            {
                log.LogError("URI --> " + URI);
                log.LogError("body --> " + body);
                log.LogError("ex --> " + ex.Message);
            }
            throw new Exception();
            return null;
        }

        [FunctionName("IncidentConsumer")]
        public void Run([QueueTrigger("cohesity-incidents", Connection = "AzureWebJobsStorage")]string queueItem, ILogger log)
        {
            log.LogInformation("queueItem --> " + queueItem);
            string token = GetAccessTokenAsync(ARM_ENDPOINT).Result;
            log.LogInformation("token --> " + token);
            string subscription = GetSecret("subscription");
            string resourceGroup = GetSecret("resourceGroup");
            string workspace = GetSecret("workspace");
            dynamic body = JsonConvert.DeserializeObject(queueItem);
            string incidentID = Guid.NewGuid().ToString();
            string URI = $"{ARM_ENDPOINT}subscriptions/{subscription}/resourceGroups/{resourceGroup}/providers/Microsoft.OperationalInsights/workspaces/{workspace}/providers/Microsoft.SecurityInsights/incidents/{incidentID}?api-version=2021-10-01";
            string result = doPUT(URI, body.ToString(), token, log);
            log.LogInformation("result --> " + result);
        }
    }
}
