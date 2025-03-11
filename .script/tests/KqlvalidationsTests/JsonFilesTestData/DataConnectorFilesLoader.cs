using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Schema;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class DataConnectorFilesLoader : JsonFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            var solutionDirectories = Path.Combine(basePath, "Solutions");
            var dataconnectorDir = Directory.GetDirectories(solutionDirectories, "Data Connectors", SearchOption.AllDirectories);

            return dataconnectorDir.ToList();
        }

        //over ride GetFilesNames method
        public override List<string> GetFilesNames()
        {
            List<string> validFiles = new List<string>();

            try
            {
                var directoryPaths = GetDirectoryPaths();
                var gitHubApiClient = GitHubApiClient.Create();

                // Fetch the PR number using the singleton instance
                int prNumber = gitHubApiClient.GetPullRequestNumber();

                var basePath = Utils.GetTestDirectory(TestFolderDepth);
                var prFilesListModified = new List<string>();

                if (prNumber != 0)
                {
                    // Fetch pull request files using the singleton instance
                    var prFiles = gitHubApiClient.GetPullRequestFiles();

                    foreach (var file in prFiles)
                    {
                        var modifiedFile = Path.Combine(basePath, file.FileName.Replace('/', Path.DirectorySeparatorChar));
                        prFilesListModified.Add(modifiedFile);
                    }
                }

                foreach (var directoryPath in directoryPaths)
                {
                    var files = Directory.GetFiles(directoryPath, "*.json", SearchOption.AllDirectories);

                    if (prNumber != 0 && prFilesListModified != null && prFilesListModified.Count != 0)
                    {
                        files = files.Where(file => prFilesListModified.Contains(file)).ToArray();
                    }

                    foreach (var filePath in files)
                    {
                        try
                        {
                            JSchema dataConnectorJsonSchema = JSchema.Parse(File.ReadAllText("DataConnectorSchema.json"));

                            var jsonString = File.ReadAllText(filePath);
                            JObject dataConnectorJsonObject = JObject.Parse(jsonString);

                            if (dataConnectorJsonObject.IsValid(dataConnectorJsonSchema))
                            {
                                validFiles.Add(filePath);
                            }
                            else
                            {
                                throw new Exception("Invalid JSON schema for file: " + filePath);
                            }
                        }
                        catch (Exception ex)
                        {
                            // Log the error and continue processing other files
                            Console.WriteLine("An error occurred while processing file: " + filePath);
                            Console.WriteLine("Error message: " + ex.Message);
                        }
                    }
                }

                if (validFiles.Count == 0)
                {
                    validFiles.Add("NoFile.json");
                }

                return validFiles;
            }
            catch (Exception ex)
            {
                // Log the error
                Console.WriteLine("An error occurred while retrieving directory paths.");
                Console.WriteLine("Error message: " + ex.Message);
            }

            return validFiles;
        }
    }
}