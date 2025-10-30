using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text.RegularExpressions;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class ValidEntityMappingsAttribute : ValidationAttribute
    {
        private readonly int _entityMappingsMinLength;
        private readonly int _entityMappingsMaxLength;
        private readonly int _fieldMappingsMinLength;
        private readonly int _fieldMappingsMaxLength;
        private readonly int _laColumnNameMaxLength = 500; // 500 is the max length of a column name in LA

        // field mapping column name should start with a letter or an underscore and contain only alphanumeric English characters (i.e. [a-zA-Z0-9_])
        private readonly Regex _laColumnNameRegex = new Regex("^[a-zA-Z_]+\\w*$");

        public ValidEntityMappingsAttribute(int entityMappingsMinLength, int entityMappingsMaxLength, int fieldMappingsMinLength, int fieldMappingsMaxLength)
        {
            _entityMappingsMinLength = entityMappingsMinLength;
            _entityMappingsMaxLength = entityMappingsMaxLength;
            _fieldMappingsMinLength = fieldMappingsMinLength;
            _fieldMappingsMaxLength = fieldMappingsMaxLength;
        }

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                return ValidationResult.Success;
            }

            var entityMappings = (List<EntityMapping>)value;
            var fieldName = validationContext.MemberName;

            if (entityMappings.Count < _entityMappingsMinLength || entityMappings.Count > _entityMappingsMaxLength)
            {
                return new ValidationResult($"Invalid length of '{entityMappings.Count}' for '{fieldName}'. '{fieldName}' length should be between '{_entityMappingsMinLength}' and '{_entityMappingsMaxLength}'");
            }

            foreach (EntityMapping entityMapping in entityMappings)
            {
                if (entityMapping.FieldMappings.Count < _fieldMappingsMinLength || entityMapping.FieldMappings.Count > _fieldMappingsMaxLength)
                {
                    return new ValidationResult($"Invalid length of '{entityMapping.FieldMappings.Count}' for '{nameof(EntityMapping.FieldMappings)}'. '{nameof(EntityMapping.FieldMappings)}' length should be between '{_fieldMappingsMinLength}' and '{_fieldMappingsMaxLength}'");
                }

                var entityType = entityMapping.EntityType;
                var requiredIdentifiers = EntityMappingIdentifiers.EntityIdentifiersMap[entityType].RequiredIdentifiers;
                var validIdentifiers = EntityMappingIdentifiers.EntityIdentifiersMap[entityType].Identifiers;
                var usedIdentifiers = new HashSet<string>();

                foreach (FieldMapping fieldMapping in entityMapping.FieldMappings)
                {
                    // Check for invalid identifier
                    if (!validIdentifiers.Contains(fieldMapping.Identifier))
                    {
                        return new ValidationResult($"Invalid identifier '{fieldMapping.Identifier}' for entity type '{entityType}' encountered. Valid identifiers are: [{string.Join(", ", validIdentifiers)}]");
                    }

                    // Check for duplicate identifier
                    if (usedIdentifiers.Contains(fieldMapping.Identifier))
                    {
                        return new ValidationResult($"Identifier '{fieldMapping.Identifier}' is defined multiple times. Identifiers used in '{fieldName}' must be unique.");
                    }

                    if (fieldMapping.ColumnName?.Length > _laColumnNameMaxLength)
                    {
                        return new ValidationResult($"Maximum length of ColumnName '{fieldMapping.ColumnName}' exceeded. ColumnName length should be less than or equal to {_laColumnNameMaxLength}.");
                    }

                    // Check for invalid column name structure
                    if (!_laColumnNameRegex.IsMatch(fieldMapping.ColumnName))
                    {
                        return new ValidationResult($"The ColumnName '{fieldMapping.ColumnName}' is invalid. The value must start with a letter or underscore, and contain only alphanumeric English characters.");
                    }

                    usedIdentifiers.Add(fieldMapping.Identifier);
                }

                bool hasRequiredFields = requiredIdentifiers.Any(identifiers => identifiers.All(identifier => usedIdentifiers.Contains(identifier)));

                if (!hasRequiredFields)
                {
                    string requiredIdentifiersRepresentation = string.Join("; ", requiredIdentifiers.Select(identifiers => string.Join(", ", identifiers)));
                    return new ValidationResult($"Missing required identifiers in '{fieldName}' for type '{entityType}'. Required identifiers are one of the following combinations: {requiredIdentifiersRepresentation}");
                }
            }

            return ValidationResult.Success;
        }
    }
}
