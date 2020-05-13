namespace Teams.CustomConnector.Models
{
    public partial class Error
    {
        public ErrorClass ErrorError { get; set; }
    }

    public partial class ErrorClass
    {
        public string Code { get; set; }
        public string Message { get; set; }
    }

}
