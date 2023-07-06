using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Schema.Generation;
using Newtonsoft.Json.Schema;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;

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

                return directoryPaths.Aggregate(new List<string>(), (accumulator, directoryPath) =>
                {
                    var files = Directory.GetFiles(directoryPath, "*.json", SearchOption.AllDirectories)?.ToList();

                    if (files != null)
                    {
                        files.ForEach(filePath =>
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
                    }
                    else
                    {
                        Console.WriteLine("No JSON files found in directory: " + directoryPath);
                    }

                    return accumulator.Concat(validFiles).ToList();
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine("An error occurred while retrieving directory paths.");
                Console.WriteLine("Error message: " + ex.Message);
            }

            return validFiles;
        }
    }
}