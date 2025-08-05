using System;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;
using AsimParserValidation.Models;
using AsimParserValidation.Configuration;

namespace AsimParserValidation.Services
{
    /// <summary>
    /// Service for HTTP operations and YAML parsing
    /// </summary>
    public interface IHttpYamlService
    {
        /// <summary>
        /// Downloads and parses YAML content from a URL
        /// </summary>
        /// <param name="url">URL to download YAML from</param>
        /// <returns>Parsed YAML object or null if failed</returns>
        Task<ParserYaml?> ReadYamlFromUrlAsync(string url);

        /// <summary>
        /// Checks if a URL is accessible (returns 200 OK)
        /// </summary>
        /// <param name="url">URL to check</param>
        /// <returns>True if accessible, false otherwise</returns>
        Task<bool> IsUrlAccessibleAsync(string url);

        /// <summary>
        /// Downloads content from a URL as string
        /// </summary>
        /// <param name="url">URL to download from</param>
        /// <returns>Content as string or null if failed</returns>
        Task<string?> DownloadContentAsync(string url);
    }

    /// <summary>
    /// Implementation of HTTP and YAML service
    /// </summary>
    public class HttpYamlService : IHttpYamlService, IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<HttpYamlService> _logger;
        private readonly IDeserializer _yamlDeserializer;
        private bool _disposed;

        public HttpYamlService(HttpClient httpClient, ILogger<HttpYamlService> logger)
        {
            _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));

            // Configure YAML deserializer
            _yamlDeserializer = new DeserializerBuilder()
                .WithNamingConvention(PascalCaseNamingConvention.Instance)
                .IgnoreUnmatchedProperties()
                .Build();

            // Configure HTTP client timeout
            _httpClient.Timeout = TimeSpan.FromSeconds(30);
        }

        /// <inheritdoc />
        public async Task<ParserYaml?> ReadYamlFromUrlAsync(string url)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(url))
                {
                    _logger.LogWarning("URL is null or empty");
                    return null;
                }

                _logger.LogDebug("Downloading YAML from URL: {Url}", url);

                var content = await DownloadContentAsync(url);
                if (string.IsNullOrWhiteSpace(content))
                {
                    _logger.LogWarning("No content received from URL: {Url}", url);
                    return null;
                }

                var yamlObject = _yamlDeserializer.Deserialize<ParserYaml>(content);
                _logger.LogDebug("Successfully parsed YAML from URL: {Url}", url);
                
                return yamlObject;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error reading YAML from URL: {Url}", url);
                return null;
            }
        }

        /// <inheritdoc />
        public async Task<bool> IsUrlAccessibleAsync(string url)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(url))
                {
                    return false;
                }

                using var response = await _httpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);
                var isAccessible = response.IsSuccessStatusCode;
                
                _logger.LogDebug("URL accessibility check for {Url}: {IsAccessible}", url, isAccessible);
                return isAccessible;
            }
            catch (Exception ex)
            {
                _logger.LogDebug(ex, "URL not accessible: {Url}", url);
                return false;
            }
        }

        /// <inheritdoc />
        public async Task<string?> DownloadContentAsync(string url)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(url))
                {
                    return null;
                }

                using var response = await _httpClient.GetAsync(url);
                
                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogWarning("HTTP request failed for URL {Url} with status code: {StatusCode}", 
                        url, response.StatusCode);
                    return null;
                }

                var content = await response.Content.ReadAsStringAsync();
                _logger.LogDebug("Successfully downloaded content from URL: {Url} (Length: {Length})", 
                    url, content.Length);
                
                return content;
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "HTTP request exception for URL: {Url}", url);
                return null;
            }
            catch (TaskCanceledException ex)
            {
                _logger.LogError(ex, "Request timeout for URL: {Url}", url);
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error downloading content from URL: {Url}", url);
                return null;
            }
        }

        /// <summary>
        /// Disposes the HTTP client
        /// </summary>
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <summary>
        /// Protected dispose method
        /// </summary>
        /// <param name="disposing">Whether disposing</param>
        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed && disposing)
            {
                _httpClient?.Dispose();
                _disposed = true;
            }
        }
    }
}
