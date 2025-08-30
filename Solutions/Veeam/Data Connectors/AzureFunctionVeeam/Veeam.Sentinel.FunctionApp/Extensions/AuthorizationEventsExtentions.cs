using Sentinel.DTOs;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Extensions
{
    public static class AuthorizationEventsExtensions
    {
        public static AuthorizationEventsDTO? ToDTO(this AuthorizationEventModel model, string vbrHostName)
        {
            if (model == null) return null;

            return new AuthorizationEventsDTO
            {
                VbrHostName = vbrHostName,
                CreatedBy = model.CreatedBy,
                CreationTime = model.CreationTime,
                Description = model.Description,
                ExpirationTime = model.ExpirationTime,
                Id = model.Id,
                Name = model.Name,
                ProcessedBy = model.ProcessedBy,
                ProcessedTime = model.ProcessedTime,
                State = model.State.ToString()
            };
        }
    }
}
