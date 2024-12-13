using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public abstract class JsonFilesLoader
    {
        protected const int TestFolderDepth = 6;
        private const string FileExtensionFilter = "*.json";

        protected abstract List<string> GetDirectoryPaths();

        public virtual List<string> GetFilesNames()
        {
            try
            {
                var directoryPaths = GetDirectoryPaths();

                if (directoryPaths == null)
                {
                    return new List<string>();
                }

                var gitHubApiClient = GitHubApiClient.Create();
                var basePath = Utils.GetTestDirectory(TestFolderDepth);
                var prFilesListModified = GetModifiedFilePaths(gitHubApiClient, basePath);

                return directoryPaths
                    .SelectMany(directoryPath => Directory.GetFiles(directoryPath, FileExtensionFilter, SearchOption.AllDirectories))
                    .Where(file => prFilesListModified.Any(prFile => file.Contains(prFile)))
                    .ToList();
            }
            catch (Exception ex)
            {
                // Log or rethrow the exception for better error handling
                Console.WriteLine("Error occurred while processing files. Error message: " + ex.Message + " Stack trace: " + ex.StackTrace);
                throw; // Rethrow the exception to indicate the failure.
            }
        }

        private List<string> GetModifiedFilePaths(GitHubApiClient gitHubApiClient, string basePath)
        {
            try
            {
                var prFiles = gitHubApiClient.GetPullRequestFiles();
                return prFiles.Select(file => Path.Combine(basePath, file.FileName.Replace('/', Path.DirectorySeparatorChar)))
                              .ToList();
            }
            catch (Exception ex)
            {
                // Log or rethrow the exception for better error handling
                Console.WriteLine("Error occurred while getting the files from PR. Error message: " + ex.Message + " Stack trace: " + ex.StackTrace);
                throw; // Rethrow the exception to indicate the failure.
            }
        }    
    }
}