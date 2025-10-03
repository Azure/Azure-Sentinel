using CovewareApiClient.Models;
using Sentinel.DTOs;

namespace Sentinel.Extensions
{
    public static class CovewareFindingExtensions
    {
        public static CovewareFindingDTO ToDTO(this CovewareFinding finding, string covewareHostName, string eventId)
        {
            return new CovewareFindingDTO
            {
                CovewareHostName = covewareHostName,
                Artifact = finding.Artifact,
                EventType = finding.EventType,
                TechniqueId = finding.TechniqueId,
                EventTime = finding.EventTime,
                FirstRunOrAccessed = finding.FirstRunOrAccessed,
                Hostname = finding.Hostname,
                EventActivity = finding.EventActivity,
                Country = finding.Country,
                Id = finding.Id,
                Md5Hash = finding.FileHashes?.Md5 ?? "",
                Sha1Hash = finding.FileHashes?.Sha1 ?? "",
                Sha256Hash = finding.FileHashes?.Sha256 ?? "",
                MachineId = finding.MachineId,
                RiskLevel = finding.RiskLevel,
                ScanTime = finding.ScanTime,
                Username = finding.Username,
                EventId = eventId
            };
        }
    }
}