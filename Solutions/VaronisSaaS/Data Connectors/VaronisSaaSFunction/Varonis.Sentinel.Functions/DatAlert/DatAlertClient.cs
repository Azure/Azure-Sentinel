using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Varonis.Sentinel.Functions.Helpers;
using Varonis.Sentinel.Functions.Search;
using Varonis.Sentinel.Functions.Search.Model;

namespace Varonis.Sentinel.Functions.DatAlert
{
    internal class DatAlertClient : IDatAlertClient
    {
        private readonly Uri _baseUri;
        private readonly string _apikey;
        private readonly ILogger _log;

        public DatAlertClient(Uri baseUri, string apikey, ILogger log)
        {
            _baseUri = baseUri;
            _apikey = apikey;
            _log = log;
        }

        public async Task<IReadOnlyCollection<AlertItem>> GetDataAsync(DatAlertParams parameters)
        {
            var tokenJson = await GetAccessTokenAsync(_baseUri, _apikey).ConfigureAwait(false);
            var tokenInfo = CustomParser.ParseTokenInfo(tokenJson);

            if (tokenInfo is null) 
            {
                throw new Exception("Token object is not valid.");
            }

            var token = tokenInfo.Value.token;

            _log.LogInformation($"Access token was received: {token.Substring(0, 5)}...");

            using var client = new HttpClient();
            client.BaseAddress = _baseUri;
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            client.DefaultRequestHeaders.CacheControl = new CacheControlHeaderValue { NoCache = true };

            var severities = CustomParser.ParseArrayFromCSV(parameters.Severities);
            var ruleIds = await GetRuleIdsAsync(client, parameters.ThreatModel)
                .ConfigureAwait(false);
            var statuses = CustomParser.ParseArrayFromCSV(parameters.Status);

            var searchQuery = new AlertSearchQueryBuilder()
                .WithDateRange(parameters.Start, parameters.End, AlertAttributes.IngestTime)
                .WithSeverity(severities)
                .WithRules(ruleIds)
                .WithStatuses(statuses)
                .WithAggregations()
                .Build();

            var payload = new SearchRequestBuilder(searchQuery, AlertAttributes.Columns)
                .WithOrdering(AlertAttributes.IngestTime, true)
                .Build();

            var rowLink = await GetSearchResultPath(client, payload)
                .ConfigureAwait(false);

            var result = await GetAlertItemsAsync(client, $"app/dataquery/api/search/{rowLink}")
                .ConfigureAwait(false);

            return result;
        }

        private static async Task<string> GetAccessTokenAsync(Uri baseUri, string apikey)
        {
            using var client = new HttpClient { BaseAddress = baseUri  };
            var payload = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                { "grant_type", "varonis_custom" },
                //{ "x-api-key", apikey }
            });
            var content = await payload.ReadAsByteArrayAsync().ConfigureAwait(false);
            client.DefaultRequestHeaders.Add("x-api-key", apikey);
            client.DefaultRequestHeaders.Host = baseUri.Host;
            using var response = await client.PostAsync("api/authentication/api_keys/token", payload)
                .ConfigureAwait(false);

            if (!response.IsSuccessStatusCode)
            {
                throw new WebException($"Receive {response.StatusCode} while trying to get an access token.");
            }

            return await response.Content.ReadAsStringAsync()
                .ConfigureAwait(false);
        }

        private static async Task<IEnumerable<Rule>> GetRulesAsync(HttpClient client)
        {
            const int threatModelEnumID = 5821;
            using var response = await client.GetAsync($"/api/entitymodel/enum/{threatModelEnumID}")
                .ConfigureAwait(false);

            if (!response.IsSuccessStatusCode)
            {
                throw new WebException($"Receive {response.StatusCode} while trying to get a list of rules.");
            }

            var rules = await response.Content
                .ReadFromJsonAsync<IEnumerable<Rule>>()
                .ConfigureAwait(false);

            return rules;
        }

        private static async Task<int[]> GetRuleIdsAsync(HttpClient client, string threatModels) 
        {
            if (string.IsNullOrWhiteSpace(threatModels)) 
                return Array.Empty<int>();

            var allRules = await GetRulesAsync(client).ConfigureAwait(false);
            var threatModelNames = CustomParser.ParseArrayFromCSV(threatModels);

            var rules = from r in allRules
                         join tmn in threatModelNames on r.RuleName equals tmn
                         select r.RuleID;

            return rules.ToArray();
        }

        private static async Task<string> GetSearchResultPath(HttpClient client, SearchRequest payload)
        {
            using var searchRespone = await client.PostAsJsonAsync("app/dataquery/api/search/v2/search", payload)
                .ConfigureAwait(false);

            if (!searchRespone.IsSuccessStatusCode)
            {
                throw new WebException($"Receive {searchRespone.StatusCode} while trying to start searching.");
            }

            var searchLinks = await searchRespone.Content.ReadFromJsonAsync<SearchResponseLink[]>()
                .ConfigureAwait(false);
            var rowLink = searchLinks.First(x => x.DataType == SearchResultType.Rows).Location;

            return rowLink;
        }

        private async Task<IReadOnlyCollection<AlertItem>> GetAlertItemsAsync(HttpClient client, string path)
        {
            var tryings = 30;
            while (--tryings > 0)
            {
                await Task.Delay(TimeSpan.FromSeconds(1));

                using var dataResponse = await client.GetAsync(path)
                    .ConfigureAwait(false);

                if (dataResponse.StatusCode == HttpStatusCode.NotModified 
                    || dataResponse.StatusCode == HttpStatusCode.PartialContent)
                {
                    continue;
                }

                var rows = await dataResponse.Content.ReadFromJsonAsync<SearchRowsResponse>()
                    .ConfigureAwait(false);
                var rawData = SearchConverter.ConvertResponseToDictionary(rows);
                var mapper = new SearchAlertObjectMapper(_log);

                var result = mapper.MapRowsToObject(rawData);
                return result;
            }

            throw new WebException($"Search operation was not completed after {tryings} sec. {path}");
        }
    }
}
