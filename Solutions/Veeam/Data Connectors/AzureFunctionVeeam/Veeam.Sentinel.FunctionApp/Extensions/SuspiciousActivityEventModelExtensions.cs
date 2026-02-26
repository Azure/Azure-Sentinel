using Sentinel.DTOs;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Extensions
{
    public static class SuspiciousActivityEventModelExtensions
    {
        public static MalwareEventsDTO? ToDTO(this SuspiciousActivityEventModel model, string vbrHostName)
        {
            if (model?.Machine == null) return null;

            return new MalwareEventsDTO
            {
                VbrHostName = vbrHostName,
                Type = model.Type.ToString(),
                State = model.State.ToString(),
                Source = model.Source.ToString(),
                Severity = model.Severity.ToString(),
                Id = model.Id,
                DetectionTimeUtc = model.DetectionTimeUtc,
                MachineDisplayName = model.Machine.DisplayName,
                MachineUuid = model.Machine.Uuid,
                MachineBackupObjectId = model.Machine.BackupObjectId,
                Details = model.Details,
                CreatedBy = model.CreatedBy,
                Engine = model.Engine
            };
        }
    }
}
