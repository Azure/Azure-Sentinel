using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.Json;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.Extensions.Logging;

namespace Varonis.Sentinel.Functions.Helpers
{
    public class CustomParser(ILogger logger)
    {
        private readonly ILogger _logger = logger;

        public string[] ParseCsvToArray(string propValue)
        {
            if (string.IsNullOrWhiteSpace(propValue))
            {
                return [];
            }

            using var reader = new StringReader(propValue);
            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = false,
                IgnoreBlankLines = true,
                TrimOptions = TrimOptions.Trim,
            };
            using var csvReader = new CsvReader(reader, config);

            if (!csvReader.Read())
                return [];

            try
            {
                var row = Enumerable.Range(0, csvReader.ColumnCount)
                    .Select(csvReader.GetField)
                    .Select(x => x?.Trim())
                    .Where(x => !string.IsNullOrEmpty(x))
                    .ToArray();

                return row;
            }
            catch (CsvHelperException ex)
            {
                _logger.LogError(ex, "Error parsing CSV data: {Message}", ex.Message);
            }

            return [];
        }

        public (string token, string token_type, int expiresIn)? ParseTokenInfo(string json)
        {
            var jelement = JsonSerializer.Deserialize<JsonElement>(json);

            return jelement.TryGetProperty("access_token", out var token)
                && jelement.TryGetProperty("token_type", out var token_type)
                && jelement.TryGetProperty("expires_in", out var expiresIn)
                ? (token.GetString(), token_type.GetString(), expiresIn.GetInt32())
                : null;
        }
    }
}
