using Newtonsoft.Json;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Utils
{
    public class JsonConverterUtils
    {
        public static string GetDeserializationErrorPathMessage(JsonReader reader)
        {
            string pathMessage = $"Path '{reader.Path}'";
            var jsonTextReader = reader as JsonTextReader;
            if (jsonTextReader != null)
            {
                pathMessage += $", line {jsonTextReader.LineNumber}, position {jsonTextReader.LinePosition}.";
            }
            return pathMessage;
        }
    }
}
