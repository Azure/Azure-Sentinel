// ***********************************************************************
// Assembly         : RDAPQuery
// Author           : Matt Egen @FlyingBlueMonkey
// Created          : 04-16-2021
//
// Last Modified By : Matt Egen @FlyingBlueMonkey
// Last Modified On : 05-30-2021
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace RDAPQuery
{
    /// <summary>
    /// Contains the logic to call LogAnalytics for querying and writing data
    /// </summary>
    class LogAnalytics
    {
        // Update customerId to your Log Analytics workspace ID
        /// <summary>
        /// The workspace identifier
        /// </summary>
        static string workspaceID = QueryEngine.GetEnvironmentVariable("WorkspaceID");

        // For sharedKey, use either the primary or the secondary Connected Sources client authentication key   
        /// <summary>
        /// The shared key
        /// </summary>
        static string sharedKey = QueryEngine.GetEnvironmentVariable("SharedKey");

        // LogName is name of the event type that is being submitted to Azure Monitor
        /// <summary>
        /// The log name
        /// </summary>
        static string LogName = QueryEngine.GetEnvironmentVariable("LogName");

        // You can use an optional field to specify the timestamp from the data. If the time field is not specified, Azure Monitor assumes the time is the message ingestion time
        /// <summary>
        /// The time stamp field
        /// </summary>
        static string TimeStampField = "";

        /// <summary>
        /// Gets the bearer token that we need to query LogAnalytics
        /// </summary>
        /// <returns>Token</returns>
        private static async Task<Token> GetBearerToken()
        {
            #region Local Variables
            string tenant_id = QueryEngine.GetEnvironmentVariable("tenant_id");
            string baseAddress = string.Format("https://login.microsoftonline.com/{0}/oauth2/token", tenant_id);
            string grant_type = QueryEngine.GetEnvironmentVariable("grant_type");
            string client_id = QueryEngine.GetEnvironmentVariable("client_id");
            string client_secret = QueryEngine.GetEnvironmentVariable("client_secret");
            string resource = QueryEngine.GetEnvironmentVariable("resource");
            Token token = null;
            HttpClient client = new HttpClient();
            #endregion
            Console.Write("Received Call to GetbearerToken");
            // Set the base address of the HttpClient object
            client.BaseAddress = new Uri(baseAddress);
            // Add an Accept header for JSON format.
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            var form = new Dictionary<string, string>
                {
                    {"grant_type", grant_type},
                    {"client_id", client_id},
                    {"client_secret", client_secret},
                    {"resource",resource }
                };

            HttpResponseMessage tokenResponse = await client.PostAsync(baseAddress, new FormUrlEncodedContent(form));
            if (tokenResponse.IsSuccessStatusCode)
            {
                var jsonContent = await tokenResponse.Content.ReadAsStringAsync();
                token = JsonConvert.DeserializeObject<Token>(jsonContent);
            }
            else
            {
                Console.WriteLine("{0} ({1})", (int)tokenResponse.StatusCode, tokenResponse.ReasonPhrase);
            }
            // Dispose of the client since all HttpClient calls are complete.
            client.Dispose();
            return token;

        }


        /// <summary>
        /// Represents an OAUTH2 token object
        /// </summary>
        internal class Token
        {
            /// <summary>
            /// Gets or sets the access token.
            /// </summary>
            /// <value>The access token.</value>
            [JsonProperty("access_token")]
            public string AccessToken { get; set; }

            /// <summary>
            /// Gets or sets the type of the token.
            /// </summary>
            /// <value>The type of the token.</value>
            [JsonProperty("token_type")]
            public string TokenType { get; set; }

            /// <summary>
            /// Gets or sets the expires in.
            /// </summary>
            /// <value>The expires in.</value>
            [JsonProperty("expires_in")]
            public int ExpiresIn { get; set; }

            /// <summary>
            /// Gets or sets the refresh token.
            /// </summary>
            /// <value>The refresh token.</value>
            [JsonProperty("refresh_token")]
            public string RefreshToken { get; set; }
        }


        /// <summary>
        /// Writes the json payload to LogAnalytics
        /// </summary>
        /// <param name="jsonPayload">The json payload.</param>
        public static void WriteData(string jsonPayload)
        {
            // Create a hash for the API signature
            var datestring = DateTime.UtcNow.ToString("r");
            var jsonBytes = Encoding.UTF8.GetBytes(jsonPayload);
            string stringToHash = "POST\n" + jsonBytes.Length + "\napplication/json\n" + "x-ms-date:" + datestring + "\n/api/logs";
            string hashedString = BuildSignature(stringToHash, sharedKey);
            string signature = "SharedKey " + workspaceID + ":" + hashedString;

            PostData(signature, datestring, jsonPayload);
        }

        /// <summary>
        /// Builds a message signature
        /// </summary>
        /// <param name="message">message to sign</param>
        /// <param name="secret">The secret.</param>
        /// <returns>string.</returns>
        public static string BuildSignature(string message, string secret)
        {
            var encoding = new System.Text.ASCIIEncoding();
            byte[] keyByte = Convert.FromBase64String(secret);
            byte[] messageBytes = encoding.GetBytes(message);
            using (var hmacsha256 = new HMACSHA256(keyByte))
            {
                byte[] hash = hmacsha256.ComputeHash(messageBytes);
                return Convert.ToBase64String(hash);
            }
        }
        /// <summary>
        /// Queries the data.
        /// </summary>
        /// <param name="query">The query.</param>
        /// <returns>QueryResults.</returns>
        public static async Task<QueryResults> QueryData(string query)
        {
            Console.Write("Received Call to QueryData, calling GetBearerToken");
            //Get the authorization bearer token
            Task<Token> task = GetBearerToken();
            Token token = task.Result;
            //Now that we have the token, we can use it to call the LogAnalytics service and run our query
            HttpClient client = new HttpClient();
            string baseAddress = string.Format("https://api.loganalytics.io/v1/workspaces/{0}/query", workspaceID);
            // Set the base address of the HttpClient object
            client.BaseAddress = new Uri(baseAddress);
            // Add an Accept header for JSON format.
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            //Add the AccessToken to the header
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token.AccessToken);

            var data = new StringContent(query, Encoding.UTF8, "application/json");
            try
            {
                Console.WriteLine("Calling LogAnalytics in QueryData");
                HttpResponseMessage queryResponse = await client.PostAsync(baseAddress, data);
                if (queryResponse.IsSuccessStatusCode)
                {
                    var jsonContent = await queryResponse.Content.ReadAsStringAsync();
                    var jsonObject = JsonConvert.DeserializeObject<QueryResults>(jsonContent);
                    client.Dispose();
                    return jsonObject;
                }
                else
                {
                    Console.WriteLine("{0} ({1})", (int)queryResponse.StatusCode, queryResponse.ReasonPhrase);
                }
                // Dispose of the client since all HttpClient calls are complete.
                client.Dispose();
                return null;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                client.Dispose();
                return null;
            }

        }

        /// <summary>
        /// Posts the data to the LogAnalytics service
        /// </summary>
        /// <param name="signature">The signature</param>
        /// <param name="date">The date</param>
        /// <param name="json">JSON body to post</param>
        public static void PostData(string signature, string date, string json)
        {
            try
            {
                string url = "https://" + workspaceID + ".ods.opinsights.azure.com/api/logs?api-version=2016-04-01";

                System.Net.Http.HttpClient client = new System.Net.Http.HttpClient();
                client.DefaultRequestHeaders.Add("Accept", "application/json");
                client.DefaultRequestHeaders.Add("Log-Type", LogName);
                client.DefaultRequestHeaders.Add("Authorization", signature);
                client.DefaultRequestHeaders.Add("x-ms-date", date);
                client.DefaultRequestHeaders.Add("time-generated-field", TimeStampField);

                System.Net.Http.HttpContent httpContent = new StringContent(json, Encoding.UTF8);
                httpContent.Headers.ContentType = new MediaTypeHeaderValue("application/json");
                Task<System.Net.Http.HttpResponseMessage> response = client.PostAsync(new Uri(url), httpContent);

                System.Net.Http.HttpContent responseContent = response.Result.Content;
                string result = responseContent.ReadAsStringAsync().Result;
                Console.WriteLine("Return Result: " + result);
            }
            catch (Exception excep)
            {
                Console.WriteLine("API Post Exception: " + excep.Message);
            }
        }

    }
    // Root myDeserializedClass = JsonConvert.DeserializeObject<Root>(myJsonResponse); 
    /// <summary>
    /// Class Column.
    /// </summary>
    public class Column
        {
        /// <summary>
        /// Gets or sets the name.
        /// </summary>
        /// <value>The name.</value>
        public string name { get; set; }
        /// <summary>
        /// Gets or sets the type.
        /// </summary>
        /// <value>The type.</value>
        public string type { get; set; }
        }

    /// <summary>
    /// Class Table
    /// </summary>
    /// <remarks>Defines the table object returned from a call to LogAnalytics</remarks>
    public class Table
        {
        /// <summary>
        /// Gets or sets the name.
        /// </summary>
        /// <value>The name.</value>
        public string name { get; set; }
        /// <summary>
        /// Gets or sets the columns.
        /// </summary>
        /// <value>The columns.</value>
        public List<Column> columns { get; set; }
        /// <summary>
        /// Gets or sets the rows.
        /// </summary>
        /// <value>The rows.</value>
        public List<List<string>> rows { get; set; }
        }

    /// <summary>
    /// Class QueryResults.
    /// </summary>
    public class QueryResults
        {
        /// <summary>
        /// Gets or sets the tables.
        /// </summary>
        /// <value>The tables.</value>
        public List<Table> tables { get; set; }
        }



}
