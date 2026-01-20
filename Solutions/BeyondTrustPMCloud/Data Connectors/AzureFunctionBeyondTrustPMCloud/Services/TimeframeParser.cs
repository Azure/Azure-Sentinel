using Microsoft.Extensions.Logging;
using System.Text.RegularExpressions;

namespace BeyondTrustPMCloud.Services;

/// <summary>
/// Parses and validates historical data timeframe strings.
/// </summary>
public static class TimeframeParser
{
    private static readonly Regex TimeframeRegex = new Regex(@"^\s*(\d+)\s*([dhm])?\s*$", RegexOptions.IgnoreCase | RegexOptions.Compiled);

    /// <summary>
    /// Parses a timeframe string and calculates the appropriate start timestamp.
    /// </summary>
    /// <param name="timeframeString">The timeframe string (e.g., "7d", "12h", "10m", "0")</param>
    /// <param name="currentTime">The current UTC time to calculate from</param>
    /// <param name="logger">Logger for warnings</param>
    /// <returns>The calculated start timestamp in UTC</returns>
    public static DateTime ParseTimeframe(string timeframeString, DateTime currentTime, ILogger? logger = null)
    {
        // Remove all whitespace
        var normalized = timeframeString?.Replace(" ", "") ?? string.Empty;

        if (string.IsNullOrWhiteSpace(normalized))
        {
            logger?.LogWarning("HistoricalDataTimeframe is empty or null. Defaulting to 1 day.");
            return currentTime.AddDays(-1);
        }

        var match = TimeframeRegex.Match(normalized);
        
        if (!match.Success)
        {
            logger?.LogWarning("Invalid HistoricalDataTimeframe format: '{Timeframe}'. Expected format: number followed by 'd' (days), 'h' (hours), or 'm' (minutes). Defaulting to 1 day.", timeframeString);
            return currentTime.AddDays(-1);
        }

        if (!int.TryParse(match.Groups[1].Value, out var value) || value < 0)
        {
            logger?.LogWarning("Invalid HistoricalDataTimeframe value: '{Timeframe}'. Value must be a non-negative integer. Defaulting to 1 day.", timeframeString);
            return currentTime.AddDays(-1);
        }

        // Handle zero value - start from current time minus 1 minute
        if (value == 0)
        {
            logger?.LogInformation("HistoricalDataTimeframe set to 0. Starting from current time minus 1 minute (no historical data).");
            return currentTime.AddMinutes(-1);
        }

        // Get the unit (default to 'd' if not specified)
        var unit = match.Groups[2].Success ? match.Groups[2].Value.ToLowerInvariant() : "d";

        DateTime startTime = unit switch
        {
            "d" => currentTime.AddDays(-value),
            "h" => currentTime.AddHours(-value),
            "m" => currentTime.AddMinutes(-value),
            _ => currentTime.AddDays(-1) // Should never happen due to regex, but fallback to 1 day
        };

        var unitName = unit switch
        {
            "d" => value == 1 ? "day" : "days",
            "h" => value == 1 ? "hour" : "hours",
            "m" => value == 1 ? "minute" : "minutes",
            _ => "day"
        };

        logger?.LogInformation("HistoricalDataTimeframe parsed: {Value} {Unit}. Starting from {StartTime:yyyy-MM-dd HH:mm:ss} UTC", 
            value, unitName, startTime);

        return startTime;
    }

    /// <summary>
    /// Validates a timeframe string format without calculating the timestamp.
    /// </summary>
    /// <param name="timeframeString">The timeframe string to validate</param>
    /// <returns>True if the format is valid, false otherwise</returns>
    public static bool IsValidFormat(string timeframeString)
    {
        if (string.IsNullOrWhiteSpace(timeframeString))
            return false;

        var normalized = timeframeString.Replace(" ", "");
        var match = TimeframeRegex.Match(normalized);
        
        if (!match.Success)
            return false;

        if (!int.TryParse(match.Groups[1].Value, out var value) || value < 0)
            return false;

        return true;
    }
}
