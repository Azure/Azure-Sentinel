namespace VoneApiClient.Exceptions
{
    public class TokenExpiredException : UnauthorizedAccessException
    {
        public int StatusCode { get; } = 401;

        public TokenExpiredException()
            : base("Token expired or invalid. Please refresh the token.")
        {
        }

        public TokenExpiredException(string message)
            : base(message)
        {
        }

        public TokenExpiredException(string message, Exception inner)
            : base(message, inner)
        {
        }

        public TokenExpiredException(string message, int statusCode)
            : base(message)
        {
            StatusCode = statusCode;
        }
    }
}
