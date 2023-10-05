using System;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Utils;
using Newtonsoft.Json;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.ModelValidations
{
    public class ScheduledTemplateTimeSpanConverter : JsonConverter
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

                if (TimeSpan.TryParse(value, out TimeSpan timespan))
                {
                    return timespan;
                }

                var timeFormatSpecifier = value[value.Length - 1];
                var timeValue = int.Parse(value.Substring(0, value.Length - 1));

                switch (timeFormatSpecifier)
                {
                    case 'm':
                        return new TimeSpan(days: 0, hours: 0, minutes: timeValue, seconds: 0);

                    case 'h':
                        return new TimeSpan(days: 0, hours: timeValue, minutes: 0, seconds: 0);

                    case 'd':
                        return new TimeSpan(days: timeValue, hours: 0, minutes: 0, seconds: 0);

                    default:
                        throw new FormatException($"Time identifier <m\\h\\d> is missing or invalid, value: {value}");
                }
            }
            catch (Exception ex)
            {
                string message = $"Value:{reader.Value}, Exception:{ex}, <number><m\\h\\d> date format is expected. Path '{reader.Path}'";
                throw new JsonSerializationException($"{message} {JsonConverterUtils.GetDeserializationErrorPathMessage(reader)}");
            }
        }

        public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
        {
            throw new NotImplementedException();
        }
    }
}