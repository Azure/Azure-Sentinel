namespace VoneApiClient.Models
{
    public class TokenLoginSpec
    {
        public string Username { get; set; } = "string";
        public string Password { get; set; } = "string";
        public string GrantType { get; set; } = LoginGrantType.Password;
        public string RefreshToken { get; set; } = "string";
    }
}