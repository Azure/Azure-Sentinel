using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Linq;
using System.Collections.Generic;
using System.Text;

namespace DetectionTemplateSchemaValidation.Tests
{
    public class AnalyticsTemplateConverter : JsonConverter
    {
        public override bool CanRead => true;
        public override bool CanWrite => false;
        private Dictionary<AlertRuleKind, Type> templateKindToTemplateTypeMap = new Dictionary<AlertRuleKind, Type>();


        public AnalyticsTemplateConverter()
        {
            var types = typeof(AnalyticsTemplateInternalModelBase).Assembly.GetTypes().Where(t => !t.IsAbstract && typeof(AnalyticsTemplateInternalModelBase).IsAssignableFrom(t)).ToList(); 
           foreach(var templateType in types)
            {
                var templateInstance = Activator.CreateInstance(templateType);
                var templateKind = ((AnalyticsTemplateInternalModelBase)templateInstance).Kind;
                templateKindToTemplateTypeMap.Add(templateKind, templateType);
            }
        }

        public override bool CanConvert(Type objectType)
        {
            return objectType == typeof(AnalyticsTemplateInternalModelBase);
        }

       public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
        {
            JObject jo = JObject.Load(reader);
            string kindStr = jo["kind"].Value<string>();
            string name = jo["name"].Value<string>();
            string id = jo["id"].Value<string>();
            AlertRuleKind kind;
            if (!Enum.TryParse<AlertRuleKind>(kindStr, true, out kind))
            {
                throw new JsonSerializationException($"The provided kind '{kindStr}' in template \"id: {id} name: {name}\" was not recognized as a valid template kind.");
            }


            if (templateKindToTemplateTypeMap.ContainsKey(kind))
            {
                Type templateType;
                templateKindToTemplateTypeMap.TryGetValue(kind, out templateType);
                var templateInstance = Activator.CreateInstance(templateType);
                serializer.Populate(jo.CreateReader(), templateInstance);
                return templateInstance;
            }
            else
            {
                throw new JsonSerializationException($"The provided kind '{kindStr}' in template \"id: {id} name: {name}\" was not recognized as a valid template kind.");
            }
        }

        public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
        {
            throw new NotImplementedException();
        }
    }
}
