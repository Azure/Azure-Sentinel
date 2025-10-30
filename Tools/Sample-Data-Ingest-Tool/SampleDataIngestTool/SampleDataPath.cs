using System;

namespace SampleDataIngestTool
{
    public class SampleDataPath
    {
        static readonly string subDirPath = "\\Sample Data\\Custom\\";
        public SampleDataPath()
        {

        }
        
        public string GetDirPath()
        {
            try
            {
                var currentDirectory = System.IO.Directory.GetCurrentDirectory();
                var basePath = currentDirectory.Split(new string[] { "\\Tools" }, StringSplitOptions.None)[0];
                var dirPath = basePath + subDirPath;

                return dirPath;
            }
            catch (Exception ex)
            {
                Console.WriteLine("Get Directory Path Error" + ex.Message);
                return "Get Directory Path Error";
            }
            
        }

    }
}
