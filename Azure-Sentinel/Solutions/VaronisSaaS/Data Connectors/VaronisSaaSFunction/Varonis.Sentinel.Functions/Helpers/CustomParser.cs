using System;
using System.Linq;
using System.Text.Json;

namespace Varonis.Sentinel.Functions.Helpers
{
    internal static class CustomParser
    {
        public static string[] ParseArrayFromCSV(string propValue)
        {
            return propValue
                ?.Split(',', StringSplitOptions.RemoveEmptyEntries)
                ?.Select(x => x.Trim())
                ?.ToArray() ?? Array.Empty<string>();
        }

        public static (string token, string token_type, int expiresIn)? ParseTokenInfo(string json)
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
