using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class NewEntityMappingsAttribute : ValidationAttribute
    {
        private readonly string _oldAccountEntityMappingColumnName = "AccountCustomEntity";
        private readonly string _oldHostEntityMappingColumnName = "HostCustomEntity";
        private readonly string _oldIpEntityMappingColumnName = "IPCustomEntity";
        private readonly string _oldUrlEntityMappingColumnName = "URLCustomEntity";
        private readonly string _oldProcessEntityMappingColumnName = "ProcessCustomEntity";
        private readonly string _oldFileHashEntityMappingColumnName = "FileHashCustomEntity";
        private readonly List<string> _oldEntityMappingColumnNames;

        public NewEntityMappingsAttribute()
        {
            _oldEntityMappingColumnNames = new List<string>()
            {
                _oldAccountEntityMappingColumnName,
                _oldHostEntityMappingColumnName,
                _oldIpEntityMappingColumnName,
                _oldUrlEntityMappingColumnName,
                _oldProcessEntityMappingColumnName,
                _oldFileHashEntityMappingColumnName
            };
        }

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            var template = (ScheduledTemplateInternalModel)value;

            if (template?.Query == null)
            {
                return new ValidationResult("Invalid template or query");
            }

            foreach (string oldEntityMappingColumnName in _oldEntityMappingColumnNames)
            {
                if (template.Query.Contains(oldEntityMappingColumnName) && !HasAMatchingNewMappingEntry(template, oldEntityMappingColumnName))
                {
                    return new ValidationResult($"An old mapping for entity '{oldEntityMappingColumnName}' does not have a matching new mapping entry.");
                }
            }

            return ValidationResult.Success;
        }

        private bool HasAMatchingNewMappingEntry(ScheduledTemplateInternalModel template, string oldEntityMappingColumnName)
        {
            return template.EntityMappings != null &&
                template.EntityMappings
                    .Any(entityMapping =>
                        entityMapping.FieldMappings != null &&
                        entityMapping.FieldMappings
                            .Any(fieldMapping => fieldMapping.ColumnName == oldEntityMappingColumnName));
        }
    }
}
