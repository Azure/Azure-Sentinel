using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Schema.Generation;
using Newtonsoft.Json.Schema;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

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
            //Console.WriteLine("PR number printed "+Environment.GetEnvironmentVariable("PrNumberNew"));
            Console.WriteLine("PR number printed direct "+Environment.GetEnvironmentVariable("System.PullRequest.PullRequestNumber"));
            Console.WriteLine("PR number printed "+Environment.GetEnvironmentVariable("PrNumberNew"));
            var directoryPaths = GetDirectoryPaths();
            return directoryPaths.Aggregate(new List<string>(), (accumulator, directoryPath) =>
            {
                var files = Directory.GetFiles(directoryPath, "*.json", SearchOption.AllDirectories).ToList();
                List<string> validFiles = new List<string>();
                files.ForEach(filePath =>
                {
                    JSchema dataConnectorJsonSchema = JSchema.Parse(File.ReadAllText("DataConnectorSchema.json"));

                    var jsonString = File.ReadAllText(filePath);
                    try
                    {
                        JObject dataConnectorJsonObject = JObject.Parse(jsonString);
                        if (dataConnectorJsonObject.IsValid(dataConnectorJsonSchema))
                        {
                            validFiles.Add(filePath);
                        }
                    }
                    catch (Exception)
                    {
                        Console.WriteLine("Invalid Json file: " + filePath);
                    }
                    
                });
                
                return accumulator.Concat(validFiles).ToList();
            });
        }
    }
}
