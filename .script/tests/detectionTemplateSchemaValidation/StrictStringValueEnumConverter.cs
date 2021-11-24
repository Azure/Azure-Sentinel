
using System;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Serialization;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.ModelValidations
{
    public class StrictStringValueEnumConverter : StringEnumConverter
    {
        public StrictStringValueEnumConverter()
        {
            AllowIntegerValues = false;
        }

        public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
        {
            try
            {
                return base.ReadJson(reader, objectType, existingValue, serializer);
            }
            catch (JsonSerializationException ex)
            {
                string propertyName = reader.Path.Split('.').Last();
                string propertyValue = reader.Value.ToString();

                throw new JsonSerializationException($"Field '{propertyName}' contains an invalid value '{propertyValue}'.");
            }
        }
    }
}
