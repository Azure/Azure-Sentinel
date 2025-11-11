using Newtonsoft.Json;

namespace CovewareApiClient.Models
{
    public class CovewareAuthResponse
    {
        [JsonProperty("AuthenticationResult")]
        public AuthenticationResult? AuthenticationResult { get; set; }

        [JsonProperty("ChallengeName")]
        public string? ChallengeName { get; set; }

        [JsonProperty("Session")]
        public string? Session { get; set; }
    }

    public class AuthenticationResult
    {
        [JsonProperty("AccessToken")]
        public string AccessToken { get; set; } = "";

        [JsonProperty("ExpiresIn")]
        public int ExpiresIn { get; set; }

        [JsonProperty("TokenType")]
        public string TokenType { get; set; } = "";

        [JsonProperty("RefreshToken")]
        public string? RefreshToken { get; set; }

        [JsonProperty("IdToken")]
        public string? IdToken { get; set; }
    }
}
