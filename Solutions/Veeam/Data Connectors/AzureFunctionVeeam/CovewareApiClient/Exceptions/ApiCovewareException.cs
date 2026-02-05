namespace CovewareApiClient.Exceptions
{
    public class ApiCovewareException : Exception
    {
        public int StatusCode { get; }
        public string? ResponseContent { get; }

        public ApiCovewareException(string message, int statusCode, string? responseContent)
            : base(message)
        {
            StatusCode = statusCode;
            ResponseContent = responseContent;
        }
    }
}
