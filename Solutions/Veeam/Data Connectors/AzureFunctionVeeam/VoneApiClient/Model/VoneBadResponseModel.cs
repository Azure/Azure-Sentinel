using System.Text.Json.Serialization;

namespace VoneApiClient.Models
{
    public class VoneBadResponseModel
    {
        [JsonPropertyName("type")]
        public string Type { get; set; }

        [JsonPropertyName("title")]
        public string Title { get; set; }

        [JsonPropertyName("status")]
        public int Status { get; set; }

        [JsonPropertyName("detail")]
        public string Detail { get; set; }

        [JsonPropertyName("instance")]
        public string Instance { get; set; }

        [JsonPropertyName("extensions")]
        public VoneErrorExtensions Extensions { get; set; }
    }
    public class VoneErrorExtensions
    {
        [JsonPropertyName("exceptionType")]
        public string ExceptionType { get; set; }
    }
}
