using Microsoft.Extensions.Logging;
using Sentinel.Managers;
using CovewareApiClient;
using CovewareApiClient.Exceptions;
using CovewareApiClient.Models;
using Sentinel.DTOs;
using CovewareApiClient.Configuration;
using Sentinel.Constants;

namespace Sentinel.Client;

public abstract class AuthenticatedCovewareClientHandler : AuthenticatedClientHandlerBase
{
    private readonly ICovewareLoginApi _loginApi;
    protected readonly CovewareConfiguration _apiConfig;

    public AuthenticatedCovewareClientHandler(string clientId, ISecretsManager secretsManager, ILogger logger)
        : base(clientId, secretsManager, logger)
    {
        var authUrl = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.CovewareAuthUrlLabel) ?? throw new InvalidOperationException($"{EnvironmentVariablesConstants.CovewareAuthUrlLabel} environment variable is not set");
        var baseUrl = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.CovewareBaseUrlLabel) ?? throw new InvalidOperationException($"{EnvironmentVariablesConstants.CovewareBaseUrlLabel} environment variable is not set");
        var earliestEventTime = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.CovewareEarliestEventTimeLabel) ?? throw new InvalidOperationException($"{EnvironmentVariablesConstants.CovewareEarliestEventTimeLabel} environment variable is not set");
        var maxRiskLevel = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.CovewareMaxRiskLevelLabel) ?? throw new InvalidOperationException($"{EnvironmentVariablesConstants.CovewareMaxRiskLevelLabel} environment variable is not set");

        _apiConfig = CreateApiConfig(baseUrl, authUrl, earliestEventTime, maxRiskLevel);
        _loginApi = new CovewareLoginApi(_apiConfig, logger);
    }

    protected override bool IsTokenPresent()
    {
        return !string.IsNullOrEmpty(_apiConfig.IdToken);
    }

    protected override async Task CreateNewTokensUsingUsernamePasswordAsync()
    {
        _logger.LogInformation($"Calling {nameof(CreateNewTokensUsingUsernamePasswordAsync)} for \"{_clientId}\"");

        var credentials = await _secretsManager.GetCowareCredentialsAsync(_clientId);

        var username = credentials.Username;
        var password = credentials.Password;
        var cognitoClientId = credentials.ClientId;

        if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password) || string.IsNullOrEmpty(cognitoClientId))
            throw new ArgumentException("Username, password, or ClientId cannot be null or empty");

        _logger.LogInformation($"Calling AWS Cognito InitiateAuth to create new tokens for \"{_clientId}\"");

        var authRequest = new CovewareAuthRequest
        {
            AuthFlow = CovewareAuthRequestType.UserPasswordAuth,
            ClientId = cognitoClientId,
            AuthParameters = new AuthParameters
            {
                Username = username,
                Password = password
            }
        };

        _logger.LogInformation($"AuthRequest: {authRequest.AuthParameters.Password}, {authRequest.AuthParameters.Username}, {authRequest.ClientId}");
        
        var response = await _loginApi.CreateTokenAsync(authRequest);

        if (response?.AuthenticationResult == null)
            throw new InvalidOperationException("Authentication failed - no authentication result received");

        _apiConfig.IdToken = response.AuthenticationResult.IdToken;

        var tokens = new CovewareTokens(
            response.AuthenticationResult.AccessToken,
            response.AuthenticationResult.RefreshToken,
            response.AuthenticationResult.IdToken);

        await _secretsManager.SaveCovewareTokensAsync(_clientId, tokens);
    }

    protected override async Task RefreshTokenInternalAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation($"Try to update tokens using refresh_token for \"{_clientId}\"");

        var oldTokens = await _secretsManager.GetCovewareTokensAsync(_clientId);
        var credentials = await _secretsManager.GetCowareCredentialsAsync(_clientId);

        if (string.IsNullOrEmpty(oldTokens.RefreshToken))
            throw new InvalidOperationException("No refresh token available");

        if (string.IsNullOrEmpty(credentials.ClientId))
            throw new InvalidOperationException("ClientId not available for refresh token flow");

        _logger.LogInformation($"Calling AWS Cognito InitiateAuth with REFRESH_TOKEN_AUTH for \"{_clientId}\"");

        var refreshRequest = new CovewareRefreshTokenRequest
        {
            AuthFlow = CovewareAuthRequestType.RefreshTokenAuth,
            ClientId = credentials.ClientId,
            AuthParameters = new RefreshTokenAuthParameters
            {
                RefreshToken = oldTokens.RefreshToken
            }
        };

        try
        {
            var response = await _loginApi.CreateTokenAsync(refreshRequest);

            if (response?.AuthenticationResult == null)
                throw new InvalidOperationException("Refresh token authentication failed - no authentication result received");

            _apiConfig.IdToken = response.AuthenticationResult.IdToken;

            var newTokens = new CovewareTokens(
                response.AuthenticationResult.AccessToken,
                response.AuthenticationResult.RefreshToken,
                response.AuthenticationResult.IdToken);

            _logger.LogInformation($"Successfully refreshed tokens for \"{_clientId}\"");
            await _secretsManager.SaveCovewareTokensAsync(_clientId, newTokens);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, $"Refresh token failed for \"{_clientId}\", falling back to username/password authentication");
            await CreateNewTokensUsingUsernamePasswordAsync();
        }
    }

    protected override bool IsUnauthorizedException(Exception ex)
    {
        return ex is ApiCovewareException;
    }

    protected static CovewareConfiguration CreateApiConfig(string baseUrl, string authUrl, string earliestEventTime, string maxRiskLevel)
    {
        if (string.IsNullOrEmpty(baseUrl))
            throw new ArgumentNullException(nameof(baseUrl), "Base URL cannot be null or empty");
        if (string.IsNullOrEmpty(authUrl))
            throw new ArgumentNullException(nameof(authUrl), "Auth URL cannot be null or empty");
        if (string.IsNullOrEmpty(earliestEventTime))
            throw new ArgumentNullException(nameof(earliestEventTime), "Earliest event time cannot be null or empty");
        if (string.IsNullOrEmpty(maxRiskLevel))
            throw new ArgumentNullException(nameof(maxRiskLevel), "Max risk level cannot be null or empty");

        var apiConfig = new CovewareConfiguration
        {
            EarliestEventTime = earliestEventTime,
            MaxRiskLevel = maxRiskLevel,
            AuthBasePath = authUrl,
            DataBasePath = baseUrl
        };

        return apiConfig;
    }
}