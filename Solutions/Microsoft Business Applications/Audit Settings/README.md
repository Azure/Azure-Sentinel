# Audit Settings for Dataverse

These packages include predefined audit settings, provided as a [managed solution](https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm), that can be imported into Dataverse to quickly enable auditing for common out of the box entities. The included `.zip` files can be extracted and modified to include additional custom entities used within your organization.

For detailed instructions on importing solutions, refer to the [Microsoft documentation](https://learn.microsoft.com/power-apps/maker/data-platform/import-update-export-solutions).

---

## Audit Configuration - Dataverse

[AuditSettingsDataverse_1_0_0_1_managed.zip](AuditSettingsDataverse_1_0_0_1_managed.zip) contains auditing settings for default entities on a vanilla Dataverse instance.

| Entity Name             | Audit Enabled | Retrieve Audit | Retrieve Multiple Audit |
|-------------------------|---------------|----------------|--------------------------|
| Account                 | ✅            | ✅             | ✅                       |
| ActivityMimeAttachment | ✅            | ✅             | ✅                       |
| Annotation              | ✅            | ✅             | ✅                       |
| BusinessUnit            | ✅            | ✅             | ✅                       |
| Contact                 | ✅            | ✅             | ✅                       |
| Email                   | ✅            | ✅             | ✅                       |
| ExpiredProcess          | ✅            | ✅             | ✅                       |
| FieldPermission         | ✅            | ✅             | ✅                       |
| FieldSecurityProfile    | ✅            | ✅             | ✅                       |
| Goal                    | ✅            | ✅             | ✅                       |
| GoalRollupQuery         | ✅            | ✅             | ✅                       |
| KbArticle               | ✅            | ✅             | ✅                       |
| KnowledgeArticle        | ✅            | ✅             | ✅                       |
| Metric                  | ✅            | ✅             | ✅                       |
| NewProcess              | ✅            | ✅             | ✅                       |
| Organization            | ✅            | ✅             | ✅                       |
| Position                | ✅            | ✅             | ✅                       |
| QueueItem               | ✅            | ✅             | ✅                       |
| Report                  | ✅            | ✅             | ✅                       |
| Role                    | ✅            | ✅             | ✅                       |
| SharePointSite          | ✅            | ✅             | ✅                       |
| SocialProfile           | ✅            | ✅             | ✅                       |
| SystemUser              | ✅            | ✅             | ✅                       |
| Team                    | ✅            | ✅             | ✅                       |
| TeamTemplate            | ✅            | ✅             | ✅                       |
| Template                | ✅            | ✅             | ✅                       |
| TransactionCurrency     | ✅            | ✅             | ✅                       |
| TranslationProcess      | ✅            | ✅             | ✅                       |

---

## Audit Configuration - Dataverse with Dynamics 365 CE Apps

[AuditSettings_1_0_0_3_managed.zip](AuditSettings_1_0_0_3_managed.zip) contains auditing settings for default entities on a Dataverse instance with Dynamics 365 CE Apps enabled.

| Entity Name                    | Audit Enabled | Retrieve Audit | Retrieve Multiple Audit |
|-------------------------------|---------------|----------------|--------------------------|
| Account                       | ✅            | ✅             | ✅                       |
| ActivityMimeAttachment        | ✅            | ✅             | ✅                       |
| Annotation                    | ✅            | ✅             | ✅                       |
| BulkOperation                 | ✅            | ✅             | ✅                       |
| BusinessUnit                  | ✅            | ✅             | ✅                       |
| Campaign                      | ✅            | ✅             | ✅                       |
| Competitor                    | ✅            | ✅             | ✅                       |
| Contact                       | ✅            | ✅             | ✅                       |
| Contract                      | ✅            | ✅             | ✅                       |
| Discount                      | ✅            | ✅             | ✅                       |
| DiscountType                  | ✅            | ✅             | ✅                       |
| Email                         | ✅            | ✅             | ✅                       |
| Entitlement                   | ✅            | ✅             | ✅                       |
| ExpiredProcess                | ✅            | ✅             | ✅                       |
| FieldPermission               | ✅            | ✅             | ✅                       |
| FieldSecurityProfile          | ✅            | ✅             | ✅                       |
| Goal                          | ✅            | ✅             | ✅                       |
| GoalRollupQuery               | ✅            | ✅             | ✅                       |
| Incident                      | ✅            | ✅             | ✅                       |
| Invoice                       | ✅            | ✅             | ✅                       |
| KbArticle                     | ✅            | ✅             | ✅                       |
| KnowledgeArticle              | ✅            | ✅             | ✅                       |
| Lead                          | ✅            | ✅             | ✅                       |
| LeadToOpportunitySalesProcess| ✅            | ✅             | ✅                       |
| List                          | ✅            | ✅             | ✅                       |
| Metric                        | ✅            | ✅             | ✅                       |
| NewProcess                    | ✅            | ✅             | ✅                       |
| Opportunity                   | ✅            | ✅             | ✅                       |
| OpportunitySalesProcess       | ✅            | ✅             | ✅                       |
| Organization                  | ✅            | ✅             | ✅                       |
| PhoneToCaseProcess            | ✅            | ✅             | ✅                       |
| Position                      | ✅            | ✅             | ✅                       |
| PriceLevel                    | ✅            | ✅             | ✅                       |
| Product                       | ✅            | ✅             | ✅                       |
| ProductPriceLevel             | ✅            | ✅             | ✅                       |
| QueueItem                     | ✅            | ✅             | ✅                       |
| Quote                         | ✅            | ✅             | ✅                       |
| Report                        | ✅            | ✅             | ✅                       |
| Role                          | ✅            | ✅             | ✅                       |
| SalesLiterature               | ✅            | ✅             | ✅                       |
| Service                       | ✅            | ✅             | ✅                       |
| SharePointSite                | ✅            | ✅             | ✅                       |
| SocialProfile                 | ✅            | ✅             | ✅                       |
| SystemUser                    | ✅            | ✅             | ✅                       |
| Team                          | ✅            | ✅             | ✅                       |
| TeamTemplate                  | ✅            | ✅             | ✅                       |
| Template                      | ✅            | ✅             | ✅                       |
| TransactionCurrency           | ✅            | ✅             | ✅                       |
| TranslationProcess            | ✅            | ✅             | ✅                       |
