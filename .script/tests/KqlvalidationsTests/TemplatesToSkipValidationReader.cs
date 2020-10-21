using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace Kqlvalidations.Tests
{
    public static class TemplatesToSkipValidationReader
    {
        private const string SKipJsonFileName = "SkipValidationsTemplates.json";

        static TemplatesToSkipValidationReader()
        {
            var jsonFilePath = Path.Combine(DetectionsYamlFilesTestData.GetSkipTemplatesPath(), SKipJsonFileName);
            using (StreamReader r = new StreamReader(jsonFilePath))
            {
                string json = r.ReadToEnd();
                WhiteListTemplateIds = JsonConvert.DeserializeObject<IEnumerable<string>>(json);
            }
        }

        public static IEnumerable<string> WhiteListTemplateIds { get; private set; }
    }
}
