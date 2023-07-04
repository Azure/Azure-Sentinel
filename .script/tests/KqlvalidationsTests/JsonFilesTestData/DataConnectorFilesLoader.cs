using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Schema;
using Octokit;
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
                var prFiles = GetPRFiles();

                var filteredFiles = directoryPaths
                    .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.json", SearchOption.AllDirectories))
                    .Where(file => prFiles.Contains(file))
                    .ToList();

                filteredFiles.ForEach(filePath =>
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
                    catch (JsonReaderException ex)
                    {
                        Console.WriteLine("Invalid JSON file: " + filePath);
                        Console.WriteLine("Error message: " + ex.Message);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("An error occurred while processing file: " + filePath);
                        Console.WriteLine("Error message: " + ex.Message);
                    }
                });

                if (validFiles.Count == 0)
                {
                    validFiles.Add("NoFile.json");
                }

                return validFiles;
            }
            catch (Exception ex)
            {
                Console.WriteLine("An error occurred while retrieving directory paths.");
                Console.WriteLine("Error message: " + ex.Message);
            }

            return validFiles;
        }


        private List<string> GetPRFiles()
        {
            int prNumber;
            int.TryParse(System.Environment.GetEnvironmentVariable("PRNUM"), out prNumber);
            if (prNumber ==0)
            {
                prNumber = 8414;
            }
            var client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
            var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
            var prFilesListModified = new List<string>();
            var basePath = Utils.GetTestDirectory(TestFolderDepth);

            foreach (var file in prFiles)
            {
                var modifiedFile = Path.Combine(basePath, file.FileName);
                prFilesListModified.Add(modifiedFile);
                //prFilesListModified.Add(modifiedFile.Replace("/", "\\"));
            }

            return prFilesListModified;
        }


    }
}