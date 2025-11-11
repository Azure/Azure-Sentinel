using Newtonsoft.Json;

namespace CovewareApiClient.Models
{
    public class CovewareFindingsResponse
    {
        [JsonProperty("data")] 
        public List<CovewareFinding> Data { get; set; } = new();

        [JsonProperty("metadata")] 
        public CovewareMetadata Metadata { get; set; } = new();
    }

    public class CovewareMetadata
    {
        [JsonProperty("success")] 
        public bool Success { get; set; }

        [JsonProperty("error")] 
        public string? Error { get; set; }

        [JsonProperty("timestamp")] 
        public long Timestamp { get; set; }

        [JsonProperty("result_count")] 
        public int ResultCount { get; set; }

        [JsonProperty("total_result_count")] 
        public int TotalResultCount { get; set; }

        [JsonProperty("offset")] 
        public int Offset { get; set; }
    }
}