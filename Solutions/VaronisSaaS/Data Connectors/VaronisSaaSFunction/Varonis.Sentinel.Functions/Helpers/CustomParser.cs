using System;
using System.Linq;
using System.Text.Json;

namespace Varonis.Sentinel.Functions.Helpers
{
    internal static class CustomParser
    {
        public static DateTime ParseDate(string dateRange)
        {
            if (DateTime.TryParse(dateRange, out var date))
            { 
                return date;
            }

            var rangeArr = dateRange.Split(' ', StringSplitOptions.RemoveEmptyEntries);

            if (rangeArr.Length != 2 || !int.TryParse(rangeArr[0], out var number))
            {
                goto FormatException;
            }

            var sufix = rangeArr[1];
            var now = DateTime.UtcNow;

            if (sufix.StartsWith("sec")) return now.AddSeconds(-number);
            if (sufix.StartsWith("min")) return now.AddMinutes(-number);
            if (sufix.StartsWith("hour")) return now.AddHours(-number);
            if (sufix.StartsWith("day")) return now.AddDays(-number);
            if (sufix.StartsWith("week")) return now.AddDays(-number*7);
            if (sufix.StartsWith("month")) return now.AddMonths(-number);
            if (sufix.StartsWith("year")) return now.AddYears(-number);

            FormatException:
                throw new FormatException($"{dateRange} is not valid date.");
        }

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
