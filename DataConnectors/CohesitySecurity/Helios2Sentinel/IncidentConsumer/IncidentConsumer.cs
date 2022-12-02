using Microsoft.Azure.WebJobs.Host;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Clients.ActiveDirectory;
using System.IO;
using System.Net;
using System.Reflection;
using System.Windows;
using System;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace IncidentConsumer
{
    public class IncidentConsumer
    {
        string TenantId = Environment.GetEnvironmentVariable("TenantId");
        string ClientId = Environment.GetEnvironmentVariable("ClientId");
        string ClientKey = Environment.GetEnvironmentVariable("ClientKey");
        const string ARM_ENDPOINT = "https://management.azure.com/";

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
            Uri uri = new Uri(String.Format(URI));

            // Create the request
            var httpWebRequest = (HttpWebRequest) WebRequest.Create(uri);
            httpWebRequest.Headers.Add(HttpRequestHeader.Authorization, "Bearer " + token);
            httpWebRequest.ContentType = "application/json";
            httpWebRequest.Method = "PUT";

            try
            {
                using (var streamWriter = new StreamWriter(httpWebRequest.GetRequestStream()))
                {
                    streamWriter.Write(body);
                    streamWriter.Flush();
                    streamWriter.Close();
                }
            }
            catch (Exception ex)
            {
                log.LogError("ex --> 1 " + ex.Message);
            }

            // Get the response
            HttpWebResponse httpResponse = null;
            string result = null;
            try
            {
                httpResponse = (HttpWebResponse) httpWebRequest.GetResponse();
            }
            catch (Exception ex)
            {
                log.LogError("URI --> 2 " + URI);
                log.LogError("body --> 2 " + body);
                log.LogError("ex --> 2 " + ex.Message);
                using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
                {
                    result = streamReader.ReadToEnd();
                    log.LogError("result --> 1 " + result);
                }
                return result;
            }

            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                result = streamReader.ReadToEnd();
            }
            return result;
        }

        [FunctionName("IncidentConsumer")]
        public void Run([QueueTrigger("cohesity-incidents", Connection = "AzureWebJobsStorage")]string queueItem, ILogger log)
        {
            log.LogInformation("queueItem --> " + queueItem);
            string token = GetAccessTokenAsync(ARM_ENDPOINT).Result;
            log.LogInformation("token --> " + token);
            string subscription = Environment.GetEnvironmentVariable("subscription");
            string resourceGroup = Environment.GetEnvironmentVariable("resourceGroup");
            string workspace = Environment.GetEnvironmentVariable("workspace");
            dynamic body = JsonConvert.DeserializeObject(queueItem);
            string incidentID = Guid.NewGuid().ToString();
            string URI = $"{ARM_ENDPOINT}subscriptions/{subscription}/resourceGroups/{resourceGroup}/providers/Microsoft.OperationalInsights/workspaces/{workspace}/providers/Microsoft.SecurityInsights/incidents/{incidentID}?api-version=2021-10-01";
            string result = doPUT(URI, body.ToString(), token, log);
            log.LogInformation("result --> " + result);
        }
    }
}
