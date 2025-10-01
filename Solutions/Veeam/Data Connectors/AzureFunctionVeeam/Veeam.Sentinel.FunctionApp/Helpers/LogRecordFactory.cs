using System.Text.Json;
using System.Text.Json.Serialization;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Helpers
{
    static internal class LogRecordFactory
    {
        static internal JsonElement CreateFrom(SuspiciousActivityEventModel model, string vbrHostName)
        {
            var jsonNode = JsonSerializer.SerializeToNode(model,
                    new JsonSerializerOptions
                    {
                        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
                    })
                ?.AsObject()
                ?? throw new JsonException("SerializeToNode returned null");

            jsonNode["vbrHostName"] = vbrHostName;

            var logRecord = JsonSerializer.Deserialize<JsonElement>(jsonNode.ToJsonString());

            return logRecord;
        }
    }
}