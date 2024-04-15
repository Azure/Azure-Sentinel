using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Clients.ActiveDirectory;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Teams.CustomConnector.Common;
using Teams.CustomConnector.Models;


/// <summary>
/// 
/// </summary>
namespace Teams.CustomConnector.Processor
{
    public class Processor
    {
        private string AadInstance = string.Empty;
        private string TenantId = string.Empty;
        private string ClientId = string.Empty;
        private string ClientSecret = string.Empty;

        private readonly ILogger log;

        private readonly string publisherGuid = Environment.GetEnvironmentVariable(Constants.PublisherGUID);

        private readonly string ContentType = Environment.GetEnvironmentVariable(Constants.ContentType);

        public Processor(ILogger log)
        {
            this.log = log;
            AadInstance = Environment.GetEnvironmentVariable(Constants.AADInstance);
            TenantId = Environment.GetEnvironmentVariable(Constants.TenantId);

        }

        /// <summary>Processes the specified start time.</summary>
        /// <param name="startTime">The start time.</param>
        /// <param name="endTime">The end time.</param>
        /// <returns></returns>
        public async Task<List<AuditDetailedReport>> Process(string startTime, string endTime)
        {
            

            log.LogInformation(Constants.OMSRequestProcessStarted);
            string urlParameters = $"?contentType=Audit.General&PublisherIdentifier={publisherGuid}&startTime={startTime}&endTime={endTime}";

            string url = $"https://manage.office.com/api/v1.0/" + TenantId + "/activity/feed/subscriptions/content";

            int pageCounter = 0;
            List<AuditDetailedReport> FinalAuditReports = new List<AuditDetailedReport>();
            AuditInitialDataObject auditInitialDataObject;
            try
            {
                do
                {
                    // Get teh initial data entry for the data pull
                    auditInitialDataObject = await GetInitialDataObject(url, urlParameters);

                    log.LogInformation($"Total pages count {++pageCounter}");
                    log.LogInformation($"Total count of initial data object {(auditInitialDataObject.AuditInitialReports == null ? 0 : auditInitialDataObject.AuditInitialReports.Count)}");

                    if (auditInitialDataObject.AuditInitialReports == null)
                    {
                        log.LogWarning("No Audit Logs Found");
                        return FinalAuditReports;
                    }

                    // Get the next page URI to form the next parameter call
                    if (auditInitialDataObject.AuditNextPageUri != "")
                        urlParameters = "?" + auditInitialDataObject.AuditNextPageUri.Split('?')[1];

                    //List of JSON objects from the initial data call
                    List<AuditInitialReport> auditInitialReports = auditInitialDataObject.AuditInitialReports;

                    // parallal request to improve performance
                    int maxCalls = 1;
                    Parallel.ForEach(auditInitialReports, new ParallelOptions { MaxDegreeOfParallelism = maxCalls }, async (auditInitialReport) =>
                    {
                        List<AuditDetailedReport> auditDetailReports = await GetAuditDetailDataAsync(auditInitialReport.ContentUri);

                        //If teams is configured
                        var logs = auditDetailReports.Where(x => x.RecordType == "25").ToList();

                        FinalAuditReports.AddRange(auditDetailReports);
                      
                    });
                } while (auditInitialDataObject.AuditNextPageUri != "");

                log.LogInformation(Constants.OMSRequestProcessCompleted);

                return FinalAuditReports;
            }
            catch (Exception ex)
            {
                log.LogWarning(Constants.OMSRequestProcessFailed);
                log.LogError(ex.InnerException.ToString());
                throw ex;
            }
        }


        /// <summary>Gets the authentication token.</summary>
        /// <returns></returns>
        private async Task<string> GetAuthToken()
        {
            bool.TryParse(Environment.GetEnvironmentVariable(Constants.KeyVaultEnabled), out bool isKeyVaultEnabled);
            if (isKeyVaultEnabled)
            {
                ClientId = await KeyVaultHelper.GetKeyValueAsync(Constants.ClientId);
                ClientSecret = await KeyVaultHelper.GetKeyValueAsync(Constants.ClientSecret);
            }
            else
            {
                ClientId = Environment.GetEnvironmentVariable(Constants.ClientId);
                ClientSecret = Environment.GetEnvironmentVariable(Constants.ClientSecret);
            }

            string ResourceId = Environment.GetEnvironmentVariable(Constants.ResourceId);

            var authContext = CreateAuthenticationContext();

            try
            {
                log.LogInformation(Constants.OAuthBearerTokenGenerationStarted);
                ClientCredential clientCredential = new ClientCredential(ClientId, ClientSecret);
                var token = await authContext.AcquireTokenAsync(ResourceId, clientCredential);
                log.LogInformation(Constants.OAuthBearerTokenGenerationCompleted);
                return token.AccessToken;
            }
            catch (Exception ex)
            {
                log.LogInformation(Constants.OAuthBearerTokenGenerationFailed);
                log.LogInformation(ex.InnerException.ToString());
                throw ex;
            }

        }


        /// <summary>Creates the authentication context.</summary>
        /// <returns></returns>
        private AuthenticationContext CreateAuthenticationContext()
        {
            object lockContext = new object();

            AuthenticationContext context;
            var authority = string.Format(CultureInfo.InvariantCulture, AadInstance, TenantId);

            lock (lockContext)
            {
                context = new AuthenticationContext(authority);
            }

            return context;
        }


        /// <summary>Gets the initial data object.</summary>
        /// <param name="ServiceUrl">The service URL.</param>
        /// <param name="urlParameters">The URL parameters.</param>
        /// <returns></returns>
        private async Task<AuditInitialDataObject> GetInitialDataObject(string ServiceUrl, string urlParameters)
        {
            AuditInitialDataObject auditInitialDataObj = new AuditInitialDataObject();
            try
            {

                List<AuditInitialReport> auditInitialReports;

                // **** Call the Http Client Service ****
                HttpClient client = new HttpClient();
                client.BaseAddress = new Uri(ServiceUrl);

                var AuthToken = await GetAuthToken();
                // Add an Accept header for JSON format.
                client.DefaultRequestHeaders.Add("Authorization", "Bearer " + AuthToken);
                client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));


                // List data response.
                log.LogInformation(Constants.OMSInitialHttpRequestSent);
                HttpResponseMessage response = client.GetAsync(urlParameters, HttpCompletionOption.ResponseContentRead).Result; // Blocking call!
                log.LogInformation(Constants.OMSInitialHttpRequestReceived);
                string responseObj = GetResponseStream(response);
                if (response.IsSuccessStatusCode)
                {
                    log.LogInformation(Constants.OMSInitialHttpRequestSuccessful);
                    // Parse the response body. Blocking!

                    auditInitialReports = JsonConvert.DeserializeObject<List<AuditInitialReport>>(responseObj);
                    IEnumerable<string> values;


                    if (response.Headers.TryGetValues("NextPageUri", out values))
                    {
                        auditInitialDataObj.AuditNextPageUri = values.First();
                        auditInitialDataObj.AuditInitialReports = auditInitialReports;
                    }
                    else
                    {
                        auditInitialDataObj.AuditNextPageUri = "";
                        auditInitialDataObj.AuditInitialReports = auditInitialReports;
                    }
                }
                else
                {
                    log.LogError($"{(int)response.StatusCode} ({response.ReasonPhrase})");
                    log.LogError(responseObj);
                }
            }
            catch (Exception ex)
            {
                log.LogError(Constants.OMSInitialHttpRequestFailed);
                log.LogError($"Error getting initial Audit Data. Message - {ex.Message}");
                throw ex;
            }

            return auditInitialDataObj;
        }


        /// <summary>
        /// Gets the response stream.
        /// </summary>
        /// <param name="response">The response.</param>
        /// <returns></returns>
        private static string GetResponseStream(HttpResponseMessage response)
        {
            Stream dataObjects = response.Content.ReadAsStreamAsync().Result;
            StreamReader reader = new StreamReader(dataObjects);
            string responseObj = reader.ReadToEnd();
            return responseObj;
        }


        /// <summary>Gets the audit detail data.</summary>
        /// <param name="url">The URL.</param>
        /// <returns></returns>
        private async Task<List<AuditDetailedReport>> GetAuditDetailDataAsync(string url)
        {
            List<AuditDetailedReport> auditDetailData = new List<AuditDetailedReport>();
            try
            {
                log.LogInformation(Constants.OMSDetailHttpRequestSent);
           
                HttpClient client = new HttpClient();
                client.BaseAddress = new Uri(url);

                var AuthToken = await GetAuthToken();
                
                client.DefaultRequestHeaders.Add("Authorization", "Bearer " + AuthToken);
                client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

                // List data response.
                HttpResponseMessage response = client.GetAsync("", HttpCompletionOption.ResponseContentRead).Result; // Blocking call!
                log.LogInformation(Constants.OMSDetailHttpRequestReceived);
                if (response.IsSuccessStatusCode)
                {
                    log.LogInformation(Constants.OMSDetailHttpRequestSuccessful);
                    Stream dataObjects = response.Content.ReadAsStreamAsync().Result;
                    StreamReader reader = new StreamReader(dataObjects);
                    string responseObj = reader.ReadToEnd();
                    auditDetailData = JsonConvert.DeserializeObject<List<AuditDetailedReport>>(responseObj);
                }
                else
                {
                    log.LogInformation(Constants.OMSDetailHttpRequestFailed);
                    log.LogError($"{(int)response.StatusCode} ({response.ReasonPhrase})");
                }
            }
            catch (Exception ex)
            {
                log.LogError(Constants.OMSDetailHttpRequestFailed);
                log.LogError($"Error getting initial Audit Data. Message - {ex.Message}");
                throw ex;
            }
            return auditDetailData;
        }
    }

}
