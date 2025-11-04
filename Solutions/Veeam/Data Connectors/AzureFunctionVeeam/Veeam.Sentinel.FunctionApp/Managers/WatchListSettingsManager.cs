using System.Net.Http.Headers;
using System.Text.Json;
using Azure.Core;
using Azure.Identity;
using Microsoft.Extensions.Logging;
using Sentinel.Constants;
using Sentinel.Models;

namespace Sentinel.Managers
{
    internal class WatchListSettingsManager : ISettingsManager
    {
        private readonly string _subscriptionId;
        private readonly string _resourceGroupName;
        private readonly string _workspaceName;
        private readonly string _vbrWatchlistAlias;
        private readonly string _voneWatchlistAlias;
        private readonly string _cowareWatchlistAlias;
        private readonly HttpClient _httpClient;
        private readonly DefaultAzureCredential _credential;
        private readonly ILogger<SecretsManagerImpl> _logger;


        public WatchListSettingsManager(ILogger<SecretsManagerImpl> logger)
        {
            _subscriptionId = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.SubscriptionIdLabel) ?? throw new InvalidOperationException($"The environment variable '{EnvironmentVariablesConstants.SubscriptionIdLabel}' is not set.");
            _resourceGroupName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.ResourceGroupNameLabel) ?? throw new InvalidOperationException($"The environment variable '{EnvironmentVariablesConstants.ResourceGroupNameLabel}' is not set.");
            _workspaceName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.WorkspaceNameLabel) ?? throw new InvalidOperationException($"The environment variable '{EnvironmentVariablesConstants.WorkspaceNameLabel}' is not set.");
            _vbrWatchlistAlias = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.VbrWatchlistAliasLabel) ?? throw new InvalidOperationException($"The environment variable '{EnvironmentVariablesConstants.VbrWatchlistAliasLabel}' is not set.");
            _voneWatchlistAlias = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.VoneWatchlistAliasLabel) ?? throw new InvalidOperationException($"The environment variable '{EnvironmentVariablesConstants.VoneWatchlistAliasLabel}' is not set.");
            _cowareWatchlistAlias = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.CowareWatchlistAliasLabel) ?? throw new InvalidOperationException($"The environment variable '{EnvironmentVariablesConstants.CowareWatchlistAliasLabel}' is not set.");

            _credential = new DefaultAzureCredential();
            _httpClient = new HttpClient();

            _logger = logger;
        }

        private string GetServerNameColumn(string watchlistAlias)
        {
            return watchlistAlias switch
            {
                var alias when alias == _vbrWatchlistAlias => "Veeam Server Name",
                var alias when alias == _voneWatchlistAlias => "Veeam Server Name",
                var alias when alias == _cowareWatchlistAlias => "Coveware Server Name",
                _ => throw new ArgumentException($"Unknown watchlist alias: {watchlistAlias}")
            };
        }

        private async Task<string> GetColumnFromWatchlist(string watchlistAlias, string id, string columnName)
        {
            _logger.LogInformation($"Calling {nameof(GetColumnFromWatchlist)} for \"{id}\" for {columnName}");

            // Get access token for Azure Management API
            var tokenRequestContext = new TokenRequestContext(new[] { "https://management.azure.com/.default" });
            var accessToken = await _credential.GetTokenAsync(tokenRequestContext);

            // Construct the REST API URL to get watchlist items
            var url = $"https://management.azure.com/subscriptions/{_subscriptionId}/resourceGroups/{_resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{_workspaceName}/providers/Microsoft.SecurityInsights/watchlists/{watchlistAlias}/watchlistItems?api-version=2023-02-01";

            _logger.LogInformation($"Making Get API call to: {url}");

            // Create HTTP request
            var request = new HttpRequestMessage(HttpMethod.Get, url);
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", accessToken.Token);

            // Make the API call
            var response = await _httpClient.SendAsync(request);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError($"REST API call failed with status {response.StatusCode}: {errorContent}");
                throw new HttpRequestException($"Failed to retrieve watchlist data: {response.StatusCode}");
            }

            var jsonContent = await response.Content.ReadAsStringAsync();

            // to not log same watchlist many times (for password, username, etc.) just log one time for baseUrl 
            if (columnName == VbrRestApiConstants.VbrBaseUrlAlias)
                _logger.LogInformation($"REST API response received {jsonContent}");

            // Deserialize JSON response to strongly typed models
            var watchlistResponse = JsonSerializer.Deserialize<WatchlistItemsResponse>(jsonContent, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            if (watchlistResponse?.Value == null || !watchlistResponse.Value.Any())
            {
                throw new KeyNotFoundException($"No watchlist items found in watchlist \"{watchlistAlias}\"");
            }

            // Determine the correct server name column based on watchlist type
            var serverNameColumn = GetServerNameColumn(watchlistAlias);

            // Find the item with matching server identifier
            var matchingItem = watchlistResponse.Value.FirstOrDefault(item =>
                item.Properties.ItemsKeyValue.ContainsKey(serverNameColumn) &&
                item.Properties.ItemsKeyValue[serverNameColumn].ToString() == id);

            if (matchingItem == null)
            {
                throw new KeyNotFoundException($"No item found with {serverNameColumn} \"{id}\"");
            }

            if (!matchingItem.Properties.ItemsKeyValue.ContainsKey(columnName))
            {
                throw new KeyNotFoundException($"No {columnName} found for \"{id}\"");
            }

            var value = matchingItem.Properties.ItemsKeyValue[columnName]?.ToString();
            if (string.IsNullOrEmpty(value))
            {
                throw new KeyNotFoundException($"No {columnName} found for \"{id}\"");
            }

            _logger.LogInformation($"Retrieved {columnName} for watchlist \"{id}\", it's equal {value}");
            return value;
        }

        public async Task<string> GetVbrPasswordAliasAsync(string vbrId)
        {
            _logger.LogInformation($"Calling {nameof(GetVbrPasswordAliasAsync)} for \"{vbrId}\"");
            return await GetColumnFromWatchlist(_vbrWatchlistAlias, vbrId, VbrRestApiConstants.VbrPasswordAlias);
        }

        public async Task<string> GetVbrUsernameAliasAsync(string vbrId)
        {
            _logger.LogInformation($"Calling {nameof(GetVbrUsernameAliasAsync)} for \"{vbrId}\"");
            return await GetColumnFromWatchlist(_vbrWatchlistAlias, vbrId, VbrRestApiConstants.VbrUsernameAlias);
        }

        public async Task<string> GetVbrBaseUrlAsync(string vbrId)
        {
            _logger.LogInformation($"Calling {nameof(GetVbrBaseUrlAsync)} for \"{vbrId}\"");
            return await GetColumnFromWatchlist(_vbrWatchlistAlias, vbrId, VbrRestApiConstants.VbrBaseUrlAlias);
        }

        public async Task<string> GetVoneBaseUrlAsync(string voneId)
        {
            _logger.LogInformation($"Calling {nameof(GetVoneBaseUrlAsync)} for \"{voneId}\"");
            return await GetColumnFromWatchlist(_voneWatchlistAlias, voneId, VoneRestApiConstants.VoneBaseUrlAlias);
        }

        public Task<string> GetVonePasswordAliasAsync(string voneId)
        {
            _logger.LogInformation($"Calling {nameof(GetVonePasswordAliasAsync)} for \"{voneId}\"");
            return GetColumnFromWatchlist(_voneWatchlistAlias, voneId, VoneRestApiConstants.VonePasswordAlias);
        }

        public Task<string> GetVoneUsernameAliasAsync(string voneId)
        {
            _logger.LogInformation($"Calling {nameof(GetVoneUsernameAliasAsync)} for \"{voneId}\"");
            return GetColumnFromWatchlist(_voneWatchlistAlias, voneId, VoneRestApiConstants.VoneUsernameAlias);
        }

        public Task<string> GetCovewarePasswordAliasAsync(string cowareId)
        {
            _logger.LogInformation($"Calling {nameof(GetCovewarePasswordAliasAsync)} for \"{cowareId}\"");
            return GetColumnFromWatchlist(_cowareWatchlistAlias, cowareId, CovewareWatchlistConstants.CovewarePasswordAlias);
        }

        public Task<string> GetCovewareUsernameAliasAsync(string cowareId)
        {
            _logger.LogInformation($"Calling {nameof(GetCovewareUsernameAliasAsync)} for \"{cowareId}\"");
            return GetColumnFromWatchlist(_cowareWatchlistAlias, cowareId, CovewareWatchlistConstants.CovewareUsernameAlias);
        }

        public Task<string> GetCovewareClientIdAliasAsync(string cowareId)
        {
            _logger.LogInformation($"Calling {nameof(GetCovewareClientIdAliasAsync)} for \"{cowareId}\"");
            return GetColumnFromWatchlist(_cowareWatchlistAlias, cowareId, CovewareWatchlistConstants.CovewareClientIdAlias);
        }

        public Task<string> GetCovewareBaseUrlAsync(string cowareId)
        {
            _logger.LogInformation($"Calling {nameof(GetCovewareBaseUrlAsync)} for \"{cowareId}\"");
            return GetColumnFromWatchlist(_cowareWatchlistAlias, cowareId, CovewareWatchlistConstants.CovewareBaseUrlAlias);
        }
    }
}