using Sentinel.DTOs;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Extensions
{
    public static class BestPracticesComplianceModelExtensions
    {
        public static BestPracticeAnalysisDTO? ToDTO(this BestPracticesComplianceModel model, string vbrHostName)
        {
            return new BestPracticeAnalysisDTO()
            {
                VbrHostName = vbrHostName,
                BestPractice = model.BestPractice,
                Id = model.Id,
                Note = model.Note,
                Status = model.Status.ToString()
            };
        }

    }
}
