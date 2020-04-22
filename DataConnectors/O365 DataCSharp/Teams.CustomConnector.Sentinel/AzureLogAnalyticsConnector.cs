using System;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace Teams.CustomConnector.Sentinel
{
    public class AzureLogAnalyticsConnector
    {

        private String WkSpaceId { get; set; }
        private String SharedKey { get; set; }
        private String ApiVersion { get; set; }
        private String LogType { get; set; }


        public AzureLogAnalyticsConnector(String workspaceId, String sharedKey, String logType, String apiVersion = "2016-04-01")
        {
            this.WkSpaceId = workspaceId;
            this.SharedKey = sharedKey;
            this.LogType = logType;
            this.ApiVersion = apiVersion;
        }
        public void Post(string json)
        {
            string requestUriString = $"https://{WkSpaceId}.ods.opinsights.azure.com/api/logs?api-version={ApiVersion}";
            DateTime dateTime = DateTime.UtcNow;
            string dateString = dateTime.ToString("r");
            string signature = GetSignature("POST", json.Length, "application/json", dateString, "/api/logs");
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(requestUriString);
            PrepareRequest(dateString, signature, request);

            byte[] content = Encoding.UTF8.GetBytes(json);

            using (Stream requestStreamAsync = request.GetRequestStream())
            {
                requestStreamAsync.Write(content, 0, content.Length);
            }
            using (HttpWebResponse responseAsync = (HttpWebResponse)request.GetResponse())
            {
                if (responseAsync.StatusCode != HttpStatusCode.OK && responseAsync.StatusCode != HttpStatusCode.Accepted)
                {
                    Stream responseStream = responseAsync.GetResponseStream();
                    if (responseStream != null)
                    {
                        using (StreamReader streamReader = new StreamReader(responseStream))
                        {
                            throw new Exception(streamReader.ReadToEnd());
                        }
                    }
                }
            }
        }

        private void PrepareRequest(string dateString, string signature, HttpWebRequest request)
        {
            request.ContentType = "application/json";
            request.Method = "POST";
            request.Headers["Log-Type"] = LogType;
            request.Headers["x-ms-date"] = dateString;
            request.Headers["Authorization"] = signature;
        }

        private string GetSignature(string method, int contentLength, string contentType, string date, string resource)
        {
            string message = $"{method}\n{contentLength}\n{contentType}\nx-ms-date:{date}\n{resource}";
            byte[] bytes = Encoding.UTF8.GetBytes(message);
            using (HMACSHA256 encryptor = new HMACSHA256(Convert.FromBase64String(SharedKey)))
            {
                return $"SharedKey {WkSpaceId}:{Convert.ToBase64String(encryptor.ComputeHash(bytes))}";
            }
        }

    }
}
