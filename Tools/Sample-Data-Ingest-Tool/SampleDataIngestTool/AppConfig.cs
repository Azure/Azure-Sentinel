using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace SampleDataIngestTool
{
    public class AppConfig
    {
        public AppConfig()
        {
           
        }

        public Dictionary<string, string> GetCredentials()
        {
            try
            {
                var currentDirectory = System.IO.Directory.GetCurrentDirectory();
                var basePath = currentDirectory.Split(new string[] { "\\bin" }, StringSplitOptions.None)[0];
                var filePath = basePath + "\\config.txt";

                using (StreamReader streamReader = new StreamReader(filePath))
                {
                    var json = streamReader.ReadToEnd();
                    var dictionary = JsonConvert.DeserializeObject<Dictionary<string, string>>(json);
                    return dictionary;
                }
            }
            catch(Exception ex)
            {
                throw new Exception("Error getting credentials " + ex.Message);
            }
        }
    }
}
