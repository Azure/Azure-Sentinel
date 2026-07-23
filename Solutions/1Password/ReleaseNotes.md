| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     |
|-------------|--------------------------------|----------------------------------------|
| 3.0.4       | 23-07-2026                     | Updated CCP **Data Connector** to use 1Password Events API **v2** endpoints (signinattempts, auditevents, itemusages) and added v2 fields (account_uuid, actor_type, actor_account_uuid, user_type, user_account_uuid) to the **OnePasswordEventLogs_CL** table. |
| 3.0.3       | 06-07-2026                     | Fixed CCP **Data Connector** to use cursor-based (PersistentToken) polling so late-synced item usage events (e.g. reveal, secure-copy) are no longer dropped. |
| 3.0.2       | 21-10-2024                     | Added new CCP **Data Connector**.               | 
| 3.0.1       | 27-06-2024                     | Fixed typo error in **Analytic Rule**  1Password - Changes to SSO configuration.yaml. </br> Fixed Logo link and typo in CreateUI.              |
| 3.0.0       | 12-06-2024                     | Initial Solution Release.               | 