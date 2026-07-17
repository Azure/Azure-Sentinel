using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using VoneApiClient.Configuration;
using VoneApiClient.Constants;
using VoneApiClient.Models;

namespace VoneApiClient
{
    public class LoginApi : ILoginApi
    {
        public VoneConfiguration Configuration { get; set; }
        private readonly ILogger _logger;

        public LoginApi(VoneConfiguration configuration, ILogger logger)
        {
            Configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public async Task<VoneTokenModel> CreateTokenAsync(TokenLoginSpec tokenLoginSpec)
        {
            if (tokenLoginSpec == null)
                throw new ArgumentNullException(nameof(tokenLoginSpec));

            var requestBody = $"username={Uri.EscapeDataString(tokenLoginSpec.Username ?? "string")}" +
                              $"&password={Uri.EscapeDataString(tokenLoginSpec.Password ?? "string")}" +
                              $"&grant_type={Uri.EscapeDataString(tokenLoginSpec.GrantType.ToString())}" +
                              $"&refresh_token={Uri.EscapeDataString(tokenLoginSpec.RefreshToken ?? "string")}";

            var content = new StringContent(requestBody, Encoding.UTF8, "application/x-www-form-urlencoded");

            var requestMessage = new HttpRequestMessage(HttpMethod.Post, "/api/token") { Content = content };

            requestMessage.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

            var response = await Configuration.HttpClient.SendAsync(requestMessage);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();

                //_logger.LogError($"Error response from /api/token: {errorContent}");

                var errorResponse = JsonSerializer.Deserialize<VoneBadResponseModel>(errorContent, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                // in case of incorrect credentials, the API returns a 400 with a specific error message
                if (errorResponse != null && !string.IsNullOrEmpty(errorResponse.Title)
                        && errorResponse.Title == ApiConstants.LoginFailedIncorrectCredentials)
                    throw new UnauthorizedAccessException("Login failed. Incorrect credentials.");

                throw new Exception($"Failed to create token: {response.StatusCode}, response content: {await response.Content.ReadAsStringAsync()}");
            }

            var responseContent = await response.Content.ReadAsStringAsync();

            //_logger.LogInformation($"Response from /api/token: {responseContentString}");

            var tokenResponse = JsonSerializer.Deserialize<VoneTokenModel>(responseContent, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

            if (tokenResponse == null || string.IsNullOrEmpty(tokenResponse.AccessToken))
                throw new InvalidOperationException("Token response is invalid or missing access token.");

            return tokenResponse;
        }
    }
}
