namespace Sentinel.DTOs
{
    public record CovewareTokens(string? AccessToken, string? RefreshToken, string? IdToken)
    {
        public override string? ToString()
        {
            return $"AccessToken = {AccessToken}, RefreshToken = {RefreshToken}, IdToken = {IdToken}";
        }
    };
}

