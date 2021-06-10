using System;
using System.ComponentModel.DataAnnotations;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class NoTemplateVersionWithoutTemplateName : ValidationAttribute
    {
        public NoTemplateVersionWithoutTemplateName()
            : base("Invalid Properties for Scheduled alert rule: 'templateVersion' can only be used if 'alertRuleTemplateName' is not empty")
        { }

        public override bool IsValid(object value)
        {
            if (value == null)
            {
                return true;
            }
            var model = value as QueryBasedAlertRuleArmModelPropertiesBase;

            if (model.AlertRuleTemplateName == null && model.TemplateVersion != null)
            {
                return false;
            }
            return true;
        }
    }
}
