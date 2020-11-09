using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;

namespace Kqlvalidations.Tests
{
    public static class TemplatesToSkipValidationReader
    {
        private const string WhiteListTemplateIdsFileName = "SkipValidationsTemplates.json";

        static TemplatesToSkipValidationReader()
        {
            var jsonFilePath = Path.Combine(DetectionsYamlFilesTestData.GetSkipTemplatesPath(), WhiteListTemplateIdsFileName);
            using (StreamReader r = new StreamReader(jsonFilePath))
            {
                string json = r.ReadToEnd();
                WhiteListTemplateIds = JsonConvert.DeserializeObject<IEnumerable<string>>(json);
            }
        }

        public static IEnumerable<string> WhiteListTemplateIds { get; private set; }
    }
}