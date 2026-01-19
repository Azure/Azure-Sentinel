using BeyondTrustPMCloud.Models;
using Microsoft.Extensions.Logging;
using System.Text;
using System.Text.Json;

namespace BeyondTrustPMCloud.Services;

public interface IBeyondTrustAuthService
{
    Task<string> GetAccessTokenAsync();
}

public class BeyondTrustAuthService : IBeyondTrustAuthService
{
    private readonly HttpClient _httpClient;
    private readonly BeyondTrustConfiguration _config;
    private readonly ILogger<BeyondTrustAuthService> _logger;
    
    private string? _accessToken;
    private DateTime _tokenExpiry = DateTime.MinValue;
    private readonly object _tokenLock = new();

    public BeyondTrustAuthService(
        HttpClient httpClient,
        BeyondTrustConfiguration config,
        ILogger<BeyondTrustAuthService> logger)
    {
        _httpClient = httpClient;
        _config = config;
        _logger = logger;
    }

    public async Task<string> GetAccessTokenAsync()
    {
        lock (_tokenLock)
        {
            // Return cached token if still valid (with 5 minute buffer)
            if (!string.IsNullOrEmpty(_accessToken) && DateTime.UtcNow < _tokenExpiry.AddMinutes(-5))
            {
                return _accessToken;
            }
        }

        try
        {
            _logger.LogDebug("Requesting new OAuth access token from BeyondTrust PM Cloud: {TokenUrl}", _config.OAuthTokenUrl);

            var tokenRequest = new List<KeyValuePair<string, string>>
            {
                new("grant_type", "client_credentials"),
                new("client_id", _config.ClientId),
                new("client_secret", _config.ClientSecret),
                new("scope", "urn:management:api")
            };

            var content = new FormUrlEncodedContent(tokenRequest);
            
            var response = await _httpClient.PostAsync(_config.OAuthTokenUrl, content);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("❌ Failed to obtain OAuth token. Status: {StatusCode}, Response: {Response}", 
                    response.StatusCode, errorContent);
                throw new HttpRequestException($"Failed to obtain OAuth token: {response.StatusCode}");
            }

            var responseContent = await response.Content.ReadAsStringAsync();
            var tokenResponse = JsonSerializer.Deserialize<OAuthTokenResponse>(responseContent);

            if (tokenResponse?.AccessToken == null)
            {
                throw new InvalidOperationException("Invalid token response from BeyondTrust PM Cloud");
            }

            lock (_tokenLock)
            {
                _accessToken = tokenResponse.AccessToken;
                _tokenExpiry = DateTime.UtcNow.AddSeconds(tokenResponse.ExpiresIn);
            }

            _logger.LogDebug("Successfully obtained OAuth access token, expires at {Expiry}", _tokenExpiry);
            return _accessToken;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error obtaining OAuth access token from BeyondTrust PM Cloud");
            throw;
        }
    }
}
