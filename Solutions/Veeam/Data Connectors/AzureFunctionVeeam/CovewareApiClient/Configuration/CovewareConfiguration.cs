﻿namespace CovewareApiClient.Configuration
{
    public class CovewareConfiguration
    {
        public string AuthBasePath { get; set; }

        public string DataBasePath { get; set; }

        public string? IdToken { get; set; }

        public string EarliestEventTime { get; set; }

        public CovewareConfiguration()
        {
        }

        public CovewareConfiguration(string authBasePath, string eventsBasePath,
            string earliestEventTime)
        {
            EarliestEventTime = earliestEventTime;
            AuthBasePath = authBasePath;
            DataBasePath = eventsBasePath;
        }
    }
}