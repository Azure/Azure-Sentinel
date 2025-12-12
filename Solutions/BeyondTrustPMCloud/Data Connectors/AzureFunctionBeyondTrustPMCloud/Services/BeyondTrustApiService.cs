using BeyondTrustPMCloud.Models;
using Microsoft.Extensions.Logging;
using System.Text;
using System.Text.Json;
using System.Web;

namespace BeyondTrustPMCloud.Services;

public interface IBeyondTrustApiService
{
    Task<ActivityAuditsResponse> GetActivityAuditsAsync(DateTime fromDate, DateTime toDate, int pageNumber = 1, int pageSize = 200);
    Task<ClientEventsResponse> GetClientEventsAsync(DateTime fromDate, int recordSize = 1000);
}

public class BeyondTrustApiService : IBeyondTrustApiService
{
    private readonly HttpClient _httpClient;
    private readonly BeyondTrustConfiguration _config;
    private readonly IBeyondTrustAuthService _authService;
    private readonly IRateLimitService _rateLimitService;
    private readonly ILogger<BeyondTrustApiService> _logger;

    public BeyondTrustApiService(
        HttpClient httpClient,
        BeyondTrustConfiguration config,
        IBeyondTrustAuthService authService,
        IRateLimitService rateLimitService,
        ILogger<BeyondTrustApiService> logger)
    {
        _httpClient = httpClient;
        _config = config;
        _authService = authService;
        _rateLimitService = rateLimitService;
        _logger = logger;
    }

    public async Task<ActivityAuditsResponse> GetActivityAuditsAsync(DateTime fromDate, DateTime toDate, int pageNumber = 1, int pageSize = 200)
    {
        await _rateLimitService.WaitForRateLimitAsync();

        try
        {
            var accessToken = await _authService.GetAccessTokenAsync();

            var fromDateString = fromDate.ToString("yyyy-MM-ddTHH:mm:ss.fffZ");
            var toDateString = toDate.ToString("yyyy-MM-ddTHH:mm:ss.fffZ");

            var queryParams = HttpUtility.ParseQueryString(string.Empty);
            queryParams["Pagination.PageSize"] = pageSize.ToString();
            queryParams["Pagination.PageNumber"] = pageNumber.ToString();
            queryParams["Filter.Created.Dates"] = fromDateString;
            queryParams.Add("Filter.Created.Dates", toDateString);
            queryParams["Filter.Created.SelectionMode"] = "Range";

            var url = $"{_config.ApiBaseUrl}/v3/ActivityAudits/Details?{queryParams}";

            using var request = new HttpRequestMessage(HttpMethod.Get, url);
            request.Headers.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken);

            _logger.LogDebug("Requesting Activity Audits from {FromDate} to {ToDate}, page {PageNumber} using API: {ApiUrl}", 
                fromDate, toDate, pageNumber, url);

            var response = await _httpClient.SendAsync(request);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("❌ Failed to get Activity Audits. Status: {StatusCode}, Response: {Response}", 
                    response.StatusCode, errorContent);
                throw new HttpRequestException($"Failed to get Activity Audits: {response.StatusCode}");
            }

            var content = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<ActivityAuditsResponse>(content, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            if (result == null)
            {
                throw new InvalidOperationException("Failed to deserialize Activity Audits response");
            }

            _logger.LogInformation("Retrieved {RecordCount} Activity Audits from page {PageNumber} of {PageCount}", 
                result.Data.Count, result.PageNumber, result.PageCount);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error retrieving Activity Audits from {FromDate} to {ToDate}", fromDate, toDate);
            throw;
        }
    }

    public async Task<ClientEventsResponse> GetClientEventsAsync(DateTime fromDate, int recordSize = 1000)
    {
        await _rateLimitService.WaitForRateLimitAsync();

        try
        {
            var accessToken = await _authService.GetAccessTokenAsync();

            var startDateString = fromDate.ToString("yyyy-MM-ddTHH:mm:ss.fffZ");

            var queryParams = HttpUtility.ParseQueryString(string.Empty);
            queryParams["StartDate"] = startDateString;
            queryParams["RecordSize"] = recordSize.ToString();

            var url = $"{_config.ApiBaseUrl}/v3/Events/FromStartDate?{queryParams}";

            using var request = new HttpRequestMessage(HttpMethod.Get, url);
            request.Headers.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken);

            _logger.LogDebug("Requesting Client Events from {StartDate} with record size {RecordSize} using API: {ApiUrl}", 
                fromDate, recordSize, url);

            var response = await _httpClient.SendAsync(request);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("❌ Failed to get Client Events. Status: {StatusCode}, Response: {Response}", 
                    response.StatusCode, errorContent);
                throw new HttpRequestException($"Failed to get Client Events: {response.StatusCode}");
            }

            var content = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<ClientEventsResponse>(content, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            if (result == null)
            {
                throw new InvalidOperationException("Failed to deserialize Client Events response");
            }

            _logger.LogInformation("Retrieved {RecordCount} Client Events from {StartDate}", 
                result.TotalRecordsReturned, fromDate);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error retrieving Client Events from {StartDate}", fromDate);
            throw;
        }
    }
}
