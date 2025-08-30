using System.Net;
using System.Net.Http.Headers;
using CovewareApiClient.Exceptions;
using CovewareApiClient.Models;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using CovewareApiClient.Configuration;

namespace CovewareApiClient
{
    public class CovewareFindingsApi : ICovewareFindingsApi
    {
        private readonly ILogger _logger;
        private readonly CovewareConfiguration _configuration;

        public CovewareFindingsApi(CovewareConfiguration configuration, ILogger logger)
        {
            _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public async Task<CovewareFindingsResponse> GetFindingsAsync()
        {
            using var dataRetrievalClient = new HttpClient();

            var requestUri =
                $"{_configuration.DataBasePath}/findings" +
                $"?earliest-event-time={_configuration.EarliestEventTime}" +
                $"&max-risk-level={_configuration.MaxRiskLevel}";

            var requestMessage = new HttpRequestMessage(HttpMethod.Get, requestUri);
            requestMessage.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

            var idToken = _configuration.IdToken;
        
            
            // Add authorization header if idToken is provided
            if (!string.IsNullOrEmpty(idToken))
            {
                requestMessage.Headers.Authorization = new AuthenticationHeaderValue(idToken);
            }

            var response = await dataRetrievalClient.SendAsync(requestMessage);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Error response from {RequestUri}: {ErrorContent}", requestUri, errorContent);

                if (response.StatusCode == HttpStatusCode.Unauthorized)
                    throw new ApiCovewareException("Access token is invalid or expired.", 401, errorContent);
                throw new Exception($"Failed to get findings: {response.StatusCode}, response content: {errorContent}");
            }

            var responseContent = await response.Content.ReadAsStringAsync();

            try
            {
                var findingsResponse = JsonConvert.DeserializeObject<CovewareFindingsResponse>(responseContent);

                if (findingsResponse == null)
                    throw new InvalidOperationException("Findings response deserialization resulted in null.");

                if (!findingsResponse.Metadata.Success)
                {
                    var errorMessage = findingsResponse.Metadata.Error ?? "Unknown error occurred";
                    _logger.LogError("API returned error: {Error}", errorMessage);
                    throw new Exception($"API returned error: {errorMessage}");
                }

                _logger.LogInformation("Successfully deserialized {Count} findings", findingsResponse.Data.Count);
                return findingsResponse;
            }
            catch (JsonException ex)
            {
                _logger.LogError(ex, "Failed to deserialize findings response. Response content: {ResponseContent}", responseContent);
                throw new InvalidOperationException("Failed to deserialize findings response.", ex);
            }
        }
    }
}