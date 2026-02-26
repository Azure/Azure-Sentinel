namespace Sentinel.DTOs
{
    public record Credentials(string? Username, string? Password);
    public record Tokens(string? AccessToken, string? RefreshToken)
    {
        public override string? ToString()
        {
            return $"AccessToken = {AccessToken}, RefreshToken = {RefreshToken}";
        }
    };
}
