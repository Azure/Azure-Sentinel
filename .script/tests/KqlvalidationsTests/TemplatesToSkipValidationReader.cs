using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace Kqlvalidations.Tests
{
    public static class TemplatesToSkipValidationReader
    {
        private const string WhiteListTemplateIds_MalformedQueries_FileName = "SkipValidationsTemplates_MalformedQuery.json";
        private const string WhiteListTemplateIds_TemplatesWithMalformedQueries_FileName = "SkipValidationsTemplates_MalformedTemplateStructure.json";

        static TemplatesToSkipValidationReader()
        {
            var jsonFilePath = Path.Combine(DetectionsYamlFilesTestData.GetSkipTemplatesPath(), WhiteListTemplateIds_MalformedQueries_FileName);
            using (StreamReader r = new StreamReader(jsonFilePath))
            {
                string json = r.ReadToEnd();
                WhiteListTemplateIds_MalformedQueries = JsonConvert.DeserializeObject<IEnumerable<string>>(json);
            }

            jsonFilePath = Path.Combine(DetectionsYamlFilesTestData.GetSkipTemplatesPath(), WhiteListTemplateIds_TemplatesWithMalformedQueries_FileName);
            using (StreamReader r = new StreamReader(jsonFilePath))
            {
                string json = r.ReadToEnd();
                WhiteListTemplateIds_MalformedTemplateStructure = JsonConvert.DeserializeObject<IEnumerable<string>>(json);
            }
        }

        public static IEnumerable<string> WhiteListTemplateIds_MalformedQueries { get; private set; }

        public static IEnumerable<string> WhiteListTemplateIds_MalformedTemplateStructure { get; private set; }
    }
}