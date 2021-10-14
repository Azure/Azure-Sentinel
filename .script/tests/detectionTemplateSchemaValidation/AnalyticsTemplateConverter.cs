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


            if (kind == AlertRuleKind.Scheduled)
            {
                //Do not replace the creation of a new instace and the popualation with jo.ToObject<ScheduledTemplateInternalModel>() - it created an inifinte loop and stackOverflow error. Read more here: http://chrisoldwood.blogspot.com/2017/06/stack-overflow-with-custom-jsonconverter.html
                var scheduledTemplate = new ScheduledTemplateInternalModel();
                serializer.Populate(jo.CreateReader(), scheduledTemplate);
                return scheduledTemplate;
            }
            if (kind == AlertRuleKind.NRT)
            {
                //Do not replace the creation of a new instace and the popualation with jo.ToObject<NrtTemplateInternalModel>() - it created an inifinte loop and stackOverflow error. Read more here: http://chrisoldwood.blogspot.com/2017/06/stack-overflow-with-custom-jsonconverter.html
                var nrtTemplate = new NrtTemplateInternalModel();
                serializer.Populate(jo.CreateReader(), nrtTemplate);
                return nrtTemplate;
            }

            return null;
        }

        public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
        {
            throw new NotImplementedException();
        }
    }
}
