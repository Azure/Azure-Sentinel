using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;

namespace Kqlvalidations.Tests
{
    public static class TemplatesSchemaValidationsReader
    {
        private const string WhiteListStructureTestsTemplateIdsFileName = "SkipValidationsTemplates.json";
        private const string WhiteListConnectorIdsTestsTemplateIdsFileName = "SkipValidationsTemplates.json";
        private const string ValidConnectorIdsFileName = "ValidConnectorsIds.json";

        static TemplatesSchemaValidationsReader()
        {
            WhiteListStructureTestsTemplateIds = GetTemplatesSchemaValidationsData(WhiteListStructureTestsTemplateIdsFileName);
            WhiteListConnectorIdsTestsTemplateIds = GetTemplatesSchemaValidationsData(WhiteListConnectorIdsTestsTemplateIdsFileName);
            ValidConnectorIds = GetTemplatesSchemaValidationsData(ValidConnectorIdsFileName);
        }

        private static IEnumerable<string> GetTemplatesSchemaValidationsData(string fileName)
        {
            var jsonFilePath = Path.Combine(DetectionsYamlFilesTestData.GetSkipTemplatesPath(), fileName);
            using (StreamReader r = new StreamReader(jsonFilePath))
            {
                string json = r.ReadToEnd();
                return JsonConvert.DeserializeObject<IEnumerable<string>>(json);
            }
        }

        public static IEnumerable<string> WhiteListStructureTestsTemplateIds { get; private set; }
        public static IEnumerable<string> WhiteListConnectorIdsTestsTemplateIds { get; private set; }
        public static IEnumerable<string> ValidConnectorIds { get; private set; }
    }
}