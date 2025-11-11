using Sentinel.DTOs;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Extensions
{
    public static class SessionModelExtensions
    {
        public static SessionModelDTO? ToDTO(this SessionModel model, string vbrHostName)
        {
            if (model == null) return null;

            return new SessionModelDTO
            {
                VbrHostName = vbrHostName,
                SessionType = model.SessionType.ToString(),
                State = model.State.ToString(),
                PlatformName = model.PlatformName.ToString(),
                Id = model.Id,
                Name = model.Name,
                JobId = model.JobId, 
                CreationTime = model.CreationTime,
                EndTime = model.EndTime,
                ProgressPercent = model.ProgressPercent,
                Result = model.Result.ToString(),
                ResourceId = model.ResourceId,
                ResourceReference = model.ResourceReference,
                ParentSessionId = model.ParentSessionId,
                Usn = model.Usn,
                PlatformId = model.PlatformId,
                ResultStatus = model.Result.Result.ToString(),
                ResultMessage = model.Result.Message,
                ResultIsCanceled = model.Result.IsCanceled ?? false
            };
        }
    }
}
