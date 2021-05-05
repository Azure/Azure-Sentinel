using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

namespace AzureSentinel_ManagementAPI.Infrastructure.Authentication
{
    //Access token class to authenticate and obtain AAD Token for future calls
    public class AuthenticationService
    {
        private ClientCredential credential;
        private AuthenticationContext authContext;
        private readonly AzureSentinelApiConfiguration[] azureConfigs;

        public AuthenticationService(AzureSentinelApiConfiguration[] azureConfig)
        {
            azureConfigs = azureConfig;
        }

        /// <summary>
        /// Get token by instance id
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        public async Task<AuthenticationResult> GetToken(int id)
        {
            try
            {
                var azureConfig = azureConfigs[id];
                authContext = new AuthenticationContext("https://login.microsoftonline.com/" + azureConfig.TenantId);
                credential = new ClientCredential(azureConfig.AppId, azureConfig.AppSecret);
                return
                    await authContext.AcquireTokenAsync("https://management.azure.com", credential);
            }
            catch (Exception ex)
            {
                throw new Exception("Error Acquiring Access Token: \n" + ex.Message);
            }
        }

        /// <summary>
        /// Get authorization token by instance and make the request authorized
        /// </summary>
        /// <param name="request"></param>
        /// <param name="id"></param>
        /// <returns></returns>
        public async Task AuthenticateRequest(HttpRequestMessage request, int id)
        {
            var token = await GetToken(id);
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token.AccessToken);
        }
    }
}