using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;

namespace Kqlvalidations.Tests
{
    public static class TemplatesSchemaValidationsReader
    {
        private const string WhiteListTemplateIdsFileName = "SkipValidationsTemplates.json";
        private const string ValidConnectorIdsFileName = "ValidConnectorIds.json";

        static TemplatesSchemaValidationsReader()
        {
            WhiteListTemplateIds = getTemplatesSchemaValidationsData(WhiteListTemplateIdsFileName);
            ValidConnectorIds = getTemplatesSchemaValidationsData(ValidConnectorIdsFileName);
        }

        private static IEnumerable<string> getTemplatesSchemaValidationsData(string fileName)
        {
            var jsonFilePath = Path.Combine(DetectionsYamlFilesTestData.GetSkipTemplatesPath(), fileName);
            using (StreamReader r = new StreamReader(jsonFilePath))
            {
                string json = r.ReadToEnd();
                return JsonConvert.DeserializeObject<IEnumerable<string>>(json);
            }
        }

        public static IEnumerable<string> WhiteListTemplateIds { get; private set; }
        public static IEnumerable<string> ValidConnectorIds { get; private set; }
    }
}