using Newtonsoft.Json;

namespace CovewareApiClient.Models
{
    public interface ICovewareAuthRequest
    {
        string AuthFlow { get; set; }
        string ClientId { get; set; }
    }

    public static class CovewareAuthRequestType
    {
        public const string UserPasswordAuth = "USER_PASSWORD_AUTH";
        public const string RefreshTokenAuth = "REFRESH_TOKEN_AUTH";
    }

    public class CovewareAuthRequest : ICovewareAuthRequest
    {
        [JsonProperty("AuthFlow")] 
        public string AuthFlow { get; set; } = CovewareAuthRequestType.UserPasswordAuth;

        [JsonProperty("ClientId")] 
        public string ClientId { get; set; } = "";

        [JsonProperty("AuthParameters")] 
        public AuthParameters AuthParameters { get; set; } = new();
    }

    public class CovewareRefreshTokenRequest : ICovewareAuthRequest
    {
        [JsonProperty("AuthFlow")] 
        public string AuthFlow { get; set; } = CovewareAuthRequestType.RefreshTokenAuth;

        [JsonProperty("ClientId")] 
        public string ClientId { get; set; } = "";

        [JsonProperty("AuthParameters")] 
        public RefreshTokenAuthParameters AuthParameters { get; set; } = new();
    }

    public class AuthParameters
    {
        [JsonProperty("USERNAME")] 
        public string Username { get; set; } = "";

        [JsonProperty("PASSWORD")] 
        public string Password { get; set; } = "";
    }

    public class RefreshTokenAuthParameters
    {
        [JsonProperty("REFRESH_TOKEN")] 
        public string RefreshToken { get; set; } = "";
    }
}