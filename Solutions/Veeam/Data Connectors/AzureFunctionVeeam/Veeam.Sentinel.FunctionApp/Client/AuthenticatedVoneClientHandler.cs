using Microsoft.Extensions.Logging;
using Sentinel.DTOs;
using Sentinel.Managers;
using VoneApiClient;
using VoneApiClient.Configuration;
using VoneApiClient.Exceptions;
using VoneApiClient.Models;

namespace Sentinel.Client
{
    public abstract class AuthenticatedVoneClientHandler : AuthenticatedClientHandlerBase
    {
        private ILoginApi _loginApi;
        protected VoneConfiguration _voneConfig;

        public AuthenticatedVoneClientHandler(string baseUrl, string voneId, ISecretsManager secretsManager, ILogger<AuthenticatedVoneClientHandler> logger)
            : base(voneId, secretsManager, logger)
        {
            _voneConfig = CreateVoneConfig(baseUrl);
            _loginApi = new LoginApi(_voneConfig, _logger);
        }

        protected override bool IsUnauthorizedException(Exception ex)
        {
            return ex is TokenExpiredException apiEx;
        }

        protected override bool IsTokenPresent()
        {
            return !string.IsNullOrEmpty(_voneConfig.AccessToken);
        }

        protected override async Task CreateNewTokensUsingUsernamePasswordAsync()
        {
            _logger.LogInformation($"Calling {nameof(CreateNewTokensUsingUsernamePasswordAsync)} for \"{_clientId}\"");

            var credentials = await _secretsManager.GetVoneCredentialsAsync(_clientId);

            var username = credentials.Username;
            var password = credentials.Password;

            if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
                throw new ArgumentNullException("Username or password cannot be empty or null");

            _logger.LogInformation($"Calling /api/token to create new tokens for \"{_clientId}\"");

            var spec = new TokenLoginSpec
            {
                Username = username,
                Password = password,
                GrantType = LoginGrantType.Password,
                RefreshToken = "string"
            };

            var response = await _loginApi.CreateTokenAsync(spec);
            _voneConfig.AccessToken = response.AccessToken;

            var tokens = new Tokens(response.AccessToken, response.RefreshToken);

            _logger.LogInformation($"Got tokens using /api/token for \"{_clientId}\"");
            await _secretsManager.SaveTokensAsync(_clientId, tokens);
        }

        protected override async Task RefreshTokenInternalAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation($"Try to update tokens using refresh_token for \"{_clientId}\"");
            var oldTokens = await _secretsManager.GetTokensAsync(_clientId);

            var spec = new TokenLoginSpec
            {
                GrantType = LoginGrantType.RefreshToken,
                RefreshToken = oldTokens.RefreshToken
            };

            _logger.LogInformation($"Calling /api/token to create new tokens for \"{_clientId}\" using refreshToken, {oldTokens}");
            var response = await _loginApi.CreateTokenAsync(spec);
            _voneConfig.AccessToken = response.AccessToken;

            var tokens = new Tokens(response.AccessToken, response.RefreshToken);

            _logger.LogInformation($"Tokens updated for \"{_clientId}\"");

            await _secretsManager.SaveTokensAsync(_clientId, tokens);
        }

        protected static VoneConfiguration CreateVoneConfig(string baseUrl)
        {
            var handler = new HttpClientHandler
            {
                ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator
            };

            var httpClient = new HttpClient(handler)
            {
                BaseAddress = new Uri(baseUrl)
            };

            var voneConfig = new VoneConfiguration(baseUrl)
            {
                HttpClient = httpClient
            };

            return voneConfig;
        }

        public override void Dispose()
        {
            base.Dispose();
            _voneConfig?.HttpClient?.Dispose();
        }
    }
}
