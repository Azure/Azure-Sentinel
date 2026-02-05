using System.Net.Http.Headers;

namespace VoneApiClient.Configuration
{
    public class VoneConfiguration
    {
        public string BasePath { get; set; }

        private string _accessToken;
        public string AccessToken
        {
            get => _accessToken;
            set
            {
                _accessToken = value;
                HttpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _accessToken);
            }
        }

        public HttpClient HttpClient { get; set; }

        public VoneConfiguration()
        {
        }

        public VoneConfiguration(string basePath)
        {
            BasePath = basePath;
        }
    }
}

