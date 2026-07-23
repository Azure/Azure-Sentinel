using Microsoft.Extensions.Logging;
using Sentinel.Constants;
using Sentinel.DTOs;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Client;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Client
{
    public abstract class AuthenticatedVbrClientHandler : AuthenticatedClientHandlerBase
    {
        private readonly ILoginApi _loginApi;
        protected readonly Configuration _apiConfig;

        public AuthenticatedVbrClientHandler(string baseUrl, string vbrId, ISecretsManager secretsManager, ILogger<AuthenticatedVbrClientHandler> logger)
            : base(vbrId, secretsManager, logger)
        {
            _apiConfig = CreateApiConfig(baseUrl);
            _loginApi = new LoginApi(_apiConfig);
        }

        [Obsolete("For test only.")]
        public AuthenticatedVbrClientHandler(ILoginApi loginApi, string baseUrl, string vbrId, ISecretsManager secretsManager, ILogger<AuthenticatedVbrClientHandler> logger)
            : base(vbrId, secretsManager, logger)
        {
            _apiConfig = CreateApiConfig(baseUrl);
            _loginApi = loginApi;
            _loginApi.Configuration = _apiConfig;
        }

        protected override bool IsUnauthorizedException(Exception ex)
        {
            return ex is ApiException apiEx && apiEx.ErrorCode == 401;
        }


        protected override bool IsTokenPresent()
        {
            return !string.IsNullOrEmpty(_apiConfig.AccessToken);
        }

        protected override async Task CreateNewTokensUsingUsernamePasswordAsync()
        {
            _logger.LogInformation($"Calling {nameof(CreateNewTokensUsingUsernamePasswordAsync)} for \"{_clientId}\"");

            var credentials = await _secretsManager.GetVbrCredentialsAsync(_clientId);

            var username = credentials.Username;
            var password = credentials.Password;

            if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
                throw new ArgumentNullException("Username or password not empty or null");

            _logger.LogInformation($"Calling /api/oauth2/token to create new tokens for \"{_clientId}\"");

            var spec = new TokenLoginSpec(ELoginGrantType.Password, username, password, null, null, null, null);

            var response = await _loginApi.CreateTokenAsync(spec);
            _apiConfig.AccessToken = response.AccessToken;

            var tokens = new Tokens(response.AccessToken, response.RefreshToken);

            _logger.LogInformation($"Got tokens using /api/oauth2/token for \"{_clientId}\"");
            await _secretsManager.SaveTokensAsync(_clientId, tokens);
        }

        protected override async Task RefreshTokenInternalAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation($"Try to update tokens using refresh_token for \"{_clientId}\"");
            var oldTokens = await _secretsManager.GetTokensAsync(_clientId);

            var spec = new TokenLoginSpec(ELoginGrantType.Refresh_token, null, null, oldTokens.RefreshToken, null, null, null);

            _logger.LogInformation($"Calling /api/oauth2/token to create new tokens for \"{_clientId}\" using refreshToken {oldTokens.RefreshToken}");
            var response = await _loginApi.CreateTokenAsync(spec);

            var tokens = new Tokens(response.AccessToken, response.RefreshToken);
            _apiConfig.AccessToken = response.AccessToken;

            _logger.LogInformation($"Tokens updated for \"{_clientId}\"");

            await _secretsManager.SaveTokensAsync(_clientId, tokens);
        }

        protected static Configuration CreateApiConfig(string baseUrl)
        {
            var apiConfig = new Configuration() { BasePath = baseUrl };
            apiConfig.AddDefaultHeader(VbrRestApiConstants.ApiVersionHeaderLabel, VbrRestApiConstants.ApiVersion);

            apiConfig.AddDefaultHeader("x-api-version", "1.2-rev0");

            apiConfig.DateTimeFormat = LogAnalyticsConstants.DefaultTimeFormat;

            apiConfig.AddApiKeyPrefix(VbrRestApiConstants.Authorization, VbrRestApiConstants.Bearer);
            apiConfig.ApiClient.RestClient.RemoteCertificateValidationCallback = new CertificateValidation("").Callback;
            return apiConfig;
        }
    }
}