using Newtonsoft.Json;
using System.Collections.Generic;
using System.IO;

namespace NonAsciiValidations.Tests
{
    public class SkipTemplate
    {
        public string id;
        public string templateName;
        public string validationFailReason;

    }

    public static class TemplatesToSkipValidationReader
    {
        private const string SKipJsonFileName = "SkipValidationsTemplates.json";

        static TemplatesToSkipValidationReader()
        {
            var jsonFilePath = Path.Combine(FilesTestData.GetSkipTemplatesPath(), SKipJsonFileName);
            using (StreamReader r = new StreamReader(jsonFilePath))
            {
                string json = r.ReadToEnd();
                WhiteListTemplates = JsonConvert.DeserializeObject<IEnumerable<SkipTemplate>>(json);
            }
        }

        public static IEnumerable<SkipTemplate> WhiteListTemplates { get; private set; }
    }
}
