using System;
using System.Collections.Generic;

namespace Varonis.Sentinel.Functions.Helpers
{
    public static class AlertExtensions
    {
        public static Dictionary<string, int> StatusesMap { get; } =
            new Dictionary<string, int>(StringComparer.InvariantCultureIgnoreCase)
            {
                ["New"] = 1,
                ["Under Investigation"] = 2,
                ["Closed"] = 3,
                ["Action Required"] = 4,
                ["Auto-Resolved"] = 5
            };

        public static Dictionary<string, int> SeverityMap { get; } =
            new Dictionary<string, int>(StringComparer.InvariantCultureIgnoreCase)
            {
                ["High"] = 0,
                ["Medium"] = 1,
                ["Low"] = 2
            };
    }
}
