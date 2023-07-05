using Octokit;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Microsoft.Sentinel.ValidationFramework.Common
{
    public class GitHubHelper
    {
        private readonly GitHubClient _gitHubClient;

        public GitHubHelper(string accessToken)
        {
            _gitHubClient = new GitHubClient(new ProductHeaderValue("YourAppName"))
            {
                Credentials = new Credentials(accessToken)
            };
        }

        public async Task<string> GetFileContent(string repositoryOwner, string repositoryName, string filePath)
        {
            try
            {
                var fileContentBytes = await _gitHubClient.Repository.Content.GetRawContent(repositoryOwner, repositoryName, filePath);
                string fileContent = Encoding.UTF8.GetString(fileContentBytes);
                return fileContent;
            }
            catch (Exception ex)
            {
                // Handle exceptions or log errors as needed
                Console.WriteLine($"Error fetching file content: {ex.Message}");
                return string.Empty;
            }
        }

    }
}
