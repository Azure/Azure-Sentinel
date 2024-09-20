using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Utils;
using Newtonsoft.Json;
using System;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.ModelValidations
{
    public class ScheduledTemplateTriggerOperatorConverter : JsonConverter
    {
        public override bool CanConvert(Type objectType)
        {
            return objectType == typeof(string);
        }

        public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
        {
            if (reader.TokenType == JsonToken.Null)
            {
                return null;
            }

            try
            {
                var value = serializer.Deserialize<String>(reader);

                switch (value)
                {
                    case "GreaterThan":
                        return AlertTriggerOperator.GreaterThan;

                    case "LessThan":
                        return AlertTriggerOperator.LessThan;

                    case "Equal":
                        return AlertTriggerOperator.Equal;

                    case "NotEqual":
                        return AlertTriggerOperator.NotEqual;

                    case "gt":
                        return AlertTriggerOperator.GreaterThan;

                    case "lt":
                        return AlertTriggerOperator.LessThan;

                    case "eq":
                        return AlertTriggerOperator.Equal;

                    case "ne":
                        return AlertTriggerOperator.NotEqual;

                    default:
                        throw new ArgumentException($"trigger operator value is not as expected. value: {value}");
                }
            }
            catch (Exception ex)
            {
                string message = $"Value:{reader.Value}, Exception:{ex}, Relational operator format is expected, value could be: gt, lt, er and ne. Path '{reader.Path}'";
                throw new JsonSerializationException($"{message} {JsonConverterUtils.GetDeserializationErrorPathMessage(reader)}");
            }
        }

        public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
        {
            throw new NotImplementedException();
        }
    }
}