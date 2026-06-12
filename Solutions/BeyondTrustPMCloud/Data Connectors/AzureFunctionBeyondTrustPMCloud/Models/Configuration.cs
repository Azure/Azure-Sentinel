namespace BeyondTrustPMCloud.Models;

/// <summary>
/// Configuration for BeyondTrust PM Cloud API integration.
/// 
/// URL Transformation Examples:
/// - Input: "https://yourcompany.beyondtrustcloud.com" 
///   → API: "https://yourcompany-services.beyondtrustcloud.com/management-api"
///   → OAuth: "https://yourcompany-services.beyondtrustcloud.com/oauth/connect/token"
/// 
/// - Input: "yourcompany.beyondtrustcloud.com/" (with trailing slash)
///   → API: "https://yourcompany-services.beyondtrustcloud.com/management-api"
/// 
/// - Input: "https://yourcompany-services.beyondtrustcloud.com" (already has -services)
///   → API: "https://yourcompany-services.beyondtrustcloud.com/management-api"
/// </summary>
public class BeyondTrustConfiguration
{
    public string PMCloudBaseUrl { get; set; } = string.Empty;
    public string ClientId { get; set; } = string.Empty;
    public string ClientSecret { get; set; } = string.Empty;
    public int ActivityAuditsPollingIntervalMinutes { get; set; } = 15;
    public int ClientEventsPollingIntervalMinutes { get; set; } = 5;
    public string HistoricalDataTimeframe { get; set; } = "1d";

    // Computed properties for CRON expressions
    // These will be set at startup and used by timer triggers
    public string ActivityAuditsCron { get; set; } = "0 */15 * * * *";
    public string ClientEventsCron { get; set; } = "0 */5 * * * *";

    // Computed properties for actual API URLs
    public string ApiBaseUrl => BuildApiBaseUrl();
    public string OAuthTokenUrl => BuildOAuthTokenUrl();

    private string BuildApiBaseUrl()
    {
        var normalizedUrl = NormalizeBaseUrl(PMCloudBaseUrl);
        return $"{normalizedUrl}/management-api";
    }

    private string BuildOAuthTokenUrl()
    {
        var normalizedUrl = NormalizeBaseUrl(PMCloudBaseUrl);
        return $"{normalizedUrl}/oauth/connect/token";
    }

    private string NormalizeBaseUrl(string baseUrl)
    {
        if (string.IsNullOrWhiteSpace(baseUrl))
            return string.Empty;

        // Remove trailing slash if present
        var url = baseUrl.TrimEnd('/');

        // Ensure HTTPS protocol
        if (!url.StartsWith("http://") && !url.StartsWith("https://"))
        {
            url = $"https://{url}";
        }

        // Parse the URL to work with the hostname
        if (Uri.TryCreate(url, UriKind.Absolute, out var uri))
        {
            var host = uri.Host;
            
            // Check if '-services' is already present
            if (!host.Contains("-services"))
            {
                // Find the first dot to identify the subdomain
                var firstDotIndex = host.IndexOf('.');
                if (firstDotIndex > 0)
                {
                    // Insert '-services' after the first subdomain
                    var subdomain = host.Substring(0, firstDotIndex);
                    var domain = host.Substring(firstDotIndex);
                    host = $"{subdomain}-services{domain}";
                }
                else
                {
                    // If no dots found, just append -services
                    host = $"{host}-services";
                }
            }

            // Rebuild the URL with the modified host
            var builder = new UriBuilder(uri)
            {
                Host = host
            };
            return builder.Uri.ToString().TrimEnd('/');
        }

        // Fallback if URI parsing fails
        return url;
    }
}

/// <summary>
/// Configuration for Azure Monitor Logs Ingestion API.
/// Uses Data Collection Endpoints (DCE) and Data Collection Rules (DCR) for secure, 
/// schema-controlled ingestion with Managed Identity authentication.
/// </summary>
public class LogAnalyticsConfiguration
{
    /// <summary>
    /// Data Collection Endpoint URL for log ingestion.
    /// Example: https://myorg-dce-abcd.eastus-1.ingest.monitor.azure.com
    /// </summary>
    public string DataCollectionEndpoint { get; set; } = string.Empty;
    
    /// <summary>
    /// Immutable ID of the Data Collection Rule for Activity Audits.
    /// Format: dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    /// </summary>
    public string ActivityAuditsDcrImmutableId { get; set; } = string.Empty;
    
    /// <summary>
    /// Immutable ID of the Data Collection Rule for Client Events.
    /// Format: dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    /// </summary>
    public string ClientEventsDcrImmutableId { get; set; } = string.Empty;
    
    /// <summary>
    /// Stream name for Activity Audits in the Data Collection Rule.
    /// Must match the stream name defined in the DCR.
    /// </summary>
    public string ActivityAuditsStreamName { get; set; } = "Custom-BeyondTrustPM_ActivityAudits";
    
    /// <summary>
    /// Stream name for Client Events in the Data Collection Rule.
    /// Must match the stream name defined in the DCR.
    /// </summary>
    public string ClientEventsStreamName { get; set; } = "Custom-BeyondTrustPM_ClientEvents";
}
