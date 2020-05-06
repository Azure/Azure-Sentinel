using System;
using System.Collections.Generic;
using System.Text;

namespace SampleDataIngestTool
{
    public class AppConfig
    {
        // Update customerId to your Log Analytics workspace ID
        private readonly static string _customerId = "<enter_your_workspaceId_here>";

        // For sharedKey, use either the primary or the secondary Connected Sources client authentication key   
        private readonly static string _sharedKey = "<enter_your_workspace_primary_key_here>";

        // Update your application credentials to use Log Analytics API
        private readonly static string _clientId = "<enter_your_workspaceId_here>";
        private readonly static string _clientSecret = "<enter_your_client_secret_here>";
        private readonly static string _domain = "<enter_your_domain_here>";

        public AppConfig()
        {
           
        }

        public Dictionary<string, string> GetCredentials(string customerId, string key, string clientId, string clientSecret, string domain)
        {
            try
            {
                var dictionary = new Dictionary<string, string>();
                dictionary.Add("workspaceId", customerId = _customerId);
                dictionary.Add("sharedkey", key = _sharedKey);
                dictionary.Add("clientId", clientId = _clientId);
                dictionary.Add("clientSecret", clientSecret = _clientSecret);
                dictionary.Add("domain", domain = _domain);

                return dictionary;
            }
            catch(Exception ex)
            {
                throw new Exception("Error getting credentials " + ex.Message);
            }
        }
    }
}
