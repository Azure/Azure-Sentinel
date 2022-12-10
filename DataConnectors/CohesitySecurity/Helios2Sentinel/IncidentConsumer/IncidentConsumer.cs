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
                throw new Exception();
                }
        }

        [FunctionName("IncidentConsumer")]
        [FixedDelayRetry(5, "00:05:00")]
        public void Run([QueueTrigger("%CohesityQueueName%", Connection = "AzureWebJobsStorage")]string queueItem, ILogger log)
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
