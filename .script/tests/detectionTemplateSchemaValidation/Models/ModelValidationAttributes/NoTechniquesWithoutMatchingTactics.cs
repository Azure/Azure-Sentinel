using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class NoTechniquesWithoutMatchingTactics : ValidationAttribute
    {
        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            var ruleProperties = value as ScheduledTemplateInternalModel;
            if (ruleProperties?.RelevantTechniques != null)
            {

                foreach (string technique in ruleProperties?.RelevantTechniques)
                {
                    var correspondingTactics = KillChainTechniquesHelper.GetCorrespondingKillChainIntent(technique.ExtractTechnique()).AsAttackTactics();
                    bool isTacticExists = correspondingTactics.Any((AttackTactic tactic) => ruleProperties?.Tactics?.Contains(tactic) ?? false);

                    if (!isTacticExists || correspondingTactics.Count == 0)
                    {
                        return new ValidationResult($"No valid tactic corresponding to the technique {technique} was provided in the tactics field.");
                    }
                }
            }

            return ValidationResult.Success;
        }
    }

    public static class AttackTacticExtensions
    {
        public static List<AttackTactic> AsAttackTactics(this KillChainIntent intent)
        {
            List<AttackTactic> tactics = new List<AttackTactic>();
            foreach (KillChainIntent value in Enum.GetValues(intent.GetType()))
            {
                if (intent.HasFlag(value))
                {
                    if (Enum.TryParse(value.ToString(), out AttackTactic correspondingTactic))
                    {
                        tactics.Add(correspondingTactic);
                    }
                }
            }

            return tactics;
        }
    }
}
