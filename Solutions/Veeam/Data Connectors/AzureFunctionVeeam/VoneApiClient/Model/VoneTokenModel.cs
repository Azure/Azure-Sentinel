using System.Text.Json.Serialization;

namespace VoneApiClient.Models
{
    public class VoneTokenModel
    {
        [JsonPropertyName("access_token")]
        public string AccessToken { get; set; }

        [JsonPropertyName("refresh_token")]
        public string RefreshToken { get; set; }

        [JsonPropertyName("token_type")]
        public string TokenType { get; set; }

        [JsonPropertyName("expires_in")]
        public int ExpiresIn { get; set; }

        [JsonPropertyName("user")]
        public string User { get; set; }

        [JsonPropertyName("user_role")]
        public string UserRole { get; set; }
    }
}
