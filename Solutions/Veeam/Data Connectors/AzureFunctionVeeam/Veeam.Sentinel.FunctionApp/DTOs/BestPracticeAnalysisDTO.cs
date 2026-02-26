using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Sentinel.DTOs
{
    public class BestPracticeAnalysisDTO
    {
        [JsonPropertyName("VbrHostName")]
        public string? VbrHostName { get; set; }

        [JsonPropertyName("Status")]
        public string? Status { get; set; }

        [JsonPropertyName("Id")]
        public Guid? Id { get; set; }

        [JsonPropertyName("BestPractice")]
        public string? BestPractice { get; set; }

        [JsonPropertyName("Note")]
        public string? Note { get; set; }


    }
}
