using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Newtonsoft.Json;
using System;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Resources;

namespace AzureSentinel_ManagementAPI
{
    static class Utils
    {
        private static ResourceManager resource = new ResourceManager("AzureSentinel_ManagementAPI.Resource1", Assembly.GetExecutingAssembly());

        /// <summary>
        /// Select one from enum type
        /// </summary>
        /// <typeparam name="TEnum"></typeparam>
        /// <returns></returns>
        public static TEnum SelectKind<TEnum>()
        {
            string[] kinds = System.Enum.GetNames(typeof(TEnum));
            
            for (int i = 0; i < kinds.Length; i++)
            {
                Console.WriteLine($"  {(i + 1).ToString()}. {kinds[i]}");
            }

            var len = kinds.Length;
            var isValid = false;
            var index = -1;
            
            while (!isValid)
            {
                Console.WriteLine($"Please type in a number between 1 and {len.ToString()}");
                var option = Console.ReadLine();
                isValid = int.TryParse(option, out index);
                isValid = isValid && index > 0 && index < len;
            }
            TEnum kind = (TEnum)Enum.Parse(typeof(TEnum), kinds[index - 1], true);
            return kind;
        }

        /// <summary>
        /// Get user input, return default value if no user input
        /// </summary>
        /// <param name="promptText"></param>
        /// <param name="defaultValue"></param>
        /// <returns></returns>
        public static string GetInput(string promptText, string defaultValue = "")
        {
            Console.WriteLine(promptText);
            var input = Console.ReadLine();
            
            if (input.Trim() == string.Empty)
            {
                input = defaultValue;
            }

            return input;
        }

        /// <summary>
        /// Select a specific instance
        /// </summary>
        /// <param name="configs"></param>
        /// <returns></returns>
        public static int SelectInstance(AzureSentinelApiConfiguration[] configs)
        {
            var isValid = false;
            var index = -1;
            int len = configs.Length;
            
            if (len == 1)
                return 0;

            while (!isValid)
            {
                Console.WriteLine($"Please select instance, Please type in a number between 1 and {len.ToString()}:");
                
                for(int i = 0; i < len; i++)
                {
                    Console.WriteLine($"{i + 1}. {configs[i].InstanceName}");
                }

                var option = Console.ReadLine();
                isValid = int.TryParse(option, out index);
                isValid = isValid && index > 0 && index <= len;
            }
            return index-1;
        }

        /// <summary>
        /// Select a specific instance to apply to all instances
        /// </summary>
        /// <param name="configs"></param>
        /// <returns></returns>
        public static int SelectInstanceOrApplyAll(AzureSentinelApiConfiguration[] configs)
        {
            int len = configs.Length;
            
            if (len == 1)
                return 0;

            Console.WriteLine($"Please select an instance, Please type in a number between 1 and {len.ToString()}, Otherwise it would apply to all:");
            
            for (int i = 0; i < len; i++)
            {
                Console.WriteLine($"{i + 1}. {configs[i].InstanceName}");
            }

            var option = Console.ReadLine();
            int index;
            bool isValid = int.TryParse(option, out index);
            isValid = isValid && index > 0 && index <= len;

            return isValid ? index - 1: -1;
        }

        /// <summary>
        /// Write json output string to a json file
        /// </summary>
        /// <param name="fileName"></param>
        /// <param name="jsonData"></param>
        /// <param name="format"></param>
        public static void WriteJsonStringToFile(string fileName, bool cliMode, string jsonData, bool format = true)
        {
            try
            {
                if (format)
                {
                    var jsonObj = JsonConvert.DeserializeObject(jsonData);
                    jsonData = JsonConvert.SerializeObject(jsonObj, Formatting.Indented);
                }

                string projectPath = cliMode ? Directory.GetCurrentDirectory() :
                    Path.GetDirectoryName(Path.GetDirectoryName(
                    Path.GetDirectoryName(Directory.GetCurrentDirectory())));
                string resultFolder = "Results";
                string filePath = Path.Combine(projectPath, resultFolder, fileName);
                System.IO.File.WriteAllText(filePath, jsonData);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        /// <summary>
        /// Load payload from json file
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="fileName"></param>
        /// <returns></returns>
        public static T LoadPayload<T>(string fileName, bool cliMode)
        {
            try {
                Console.WriteLine($"Request body from {fileName}:");
                string projectPath = cliMode ? Directory.GetCurrentDirectory() :
                    Path.GetDirectoryName(Path.GetDirectoryName(
                    Path.GetDirectoryName(Directory.GetCurrentDirectory())));

                string fileFolderName = Path.GetFileNameWithoutExtension(fileName);
                string resultFolder = Path.Combine("Templates", fileFolderName);
                string filePath = Path.Combine(projectPath, resultFolder, fileName);
                var data = System.IO.File.ReadAllText(filePath);

                Console.WriteLine(data);

                var incidentObj = JsonConvert.DeserializeObject<T>(data);
                return incidentObj;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return default;
            }
        }

        /// <summary>
        /// Get localized text from resource file by key
        /// </summary>
        /// <param name="key"></param>
        /// <returns></returns>
        public static string GetString(string key)
        {
            return resource.GetString(key, CultureInfo.CurrentCulture);
        }
    }
}
