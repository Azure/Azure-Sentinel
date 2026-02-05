using System;
using System.Collections.Generic;
using System.Net.Http.Headers;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using System.Net.Http.Json;
using Varonis.Sentinel.Functions.Search.Model;

namespace Varonis.Sentinel.Functions.DatAlert
{
    internal class DatAlertClientFake : IDatAlertClient
    {
        private readonly Uri _baseUri;
        private readonly string _apikey;
        private readonly ILogger _log;

        private string _dateFormat;

        public DatAlertClientFake(Uri baseUri, string apikey, ILogger log, string dateFormat = "yyyy-MM-ddTHH:mm:ss")
        {
            _baseUri = baseUri;
            _apikey = apikey;
            _log = log;
            _dateFormat = dateFormat;
        }

        public async Task<IReadOnlyCollection<AlertItem>> GetDataAsync(DatAlertParams parameters)
        {
            var token = await GetAccessTokenAsync(_baseUri, _apikey).ConfigureAwait(false);

            _log.LogInformation($"Access token was received: {token.Substring(0, 10)}");

            using var client = new HttpClient();
            client.BaseAddress = _baseUri;
            var payload = new
            {
                StartDate = parameters.Start.ToUniversalTime().ToString(_dateFormat),
                EndDate = parameters.End.ToUniversalTime().ToString(_dateFormat)
            };
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

            var response = await client.PostAsJsonAsync("/Alert/alerts-post", payload)
                .ConfigureAwait(false);

            var data = await response.Content.ReadFromJsonAsync<AlertItem[]>()
                .ConfigureAwait(false);

            return data;
        }

        private static async Task<string> GetAccessTokenAsync(Uri baseUri, string apikey)
        {
            using var client = new HttpClient();
            client.BaseAddress = baseUri;
            var payload = new Dictionary<string, string>
            {
                { "grant_type", "varonis-custom" },
                { "x-api-key", apikey }
            };
            var response = await client.PostAsync("/Auth", new FormUrlEncodedContent(payload))
                .ConfigureAwait(false);

            return await response.Content.ReadAsStringAsync()
                .ConfigureAwait(false);
        }
    }
}
