using System.Net;
using System.Net.Http.Headers;
using System.Text;
using CovewareApiClient.Exceptions;
using CovewareApiClient.Models;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using CovewareConfiguration = CovewareApiClient.Configuration.CovewareConfiguration;

namespace CovewareApiClient
{
    public class CovewareLoginApi : ICovewareLoginApi
    {
        private readonly ILogger _logger;
        private readonly string _tokenBasePath;

        public CovewareLoginApi(CovewareConfiguration configuration, ILogger logger)
        {
            _tokenBasePath = configuration.AuthBasePath ?? throw new ArgumentNullException(nameof(configuration.AuthBasePath));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public async Task<CovewareAuthResponse> CreateTokenAsync(ICovewareAuthRequest authRequest)
        {
            if (authRequest == null)
                throw new ArgumentNullException(nameof(authRequest));

            var jsonContent = JsonConvert.SerializeObject(authRequest);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/x-amz-json-1.1");

            var requestMessage = new HttpRequestMessage(HttpMethod.Post, _tokenBasePath) { Content = content };

            // Add required AWS Cognito headers
            requestMessage.Headers.Add("X-Amz-Target", "AWSCognitoIdentityProviderService.InitiateAuth");
            requestMessage.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/x-amz-json-1.1"));

            using var cognitoHttpClient = new HttpClient();
            var response = await cognitoHttpClient.SendAsync(requestMessage);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();

                // Log different messages based on auth flow type
                var authFlow = authRequest.AuthFlow;
                if (authFlow == CovewareAuthRequestType.RefreshTokenAuth)
                {
                    _logger.LogError("Error response from AWS Cognito refresh token: {ErrorContent}", errorContent);
                    if (response.StatusCode == HttpStatusCode.Unauthorized)
                        throw new ApiCovewareException("Refresh token is invalid or expired.", (int)response.StatusCode, errorContent);
                }
                else
                {
                    _logger.LogError("Error response from AWS Cognito InitiateAuth: {ErrorContent}", errorContent);
                    if (response.StatusCode == HttpStatusCode.Unauthorized)
                        throw new ApiCovewareException("Login failed. Incorrect credentials.", (int)response.StatusCode, errorContent);
                }

                throw new Exception($"Failed to {(authFlow == "REFRESH_TOKEN_AUTH" ? "refresh" : "create")} token: {response.StatusCode}");
            }

            var responseContent = await response.Content.ReadAsStringAsync();
            var authResponse = JsonConvert.DeserializeObject<CovewareAuthResponse>(responseContent);

            if (authResponse?.AuthenticationResult == null || string.IsNullOrEmpty(authResponse.AuthenticationResult.IdToken))
                throw new InvalidOperationException("Auth response is invalid or missing id token.");

            return authResponse;
        }
    }
}