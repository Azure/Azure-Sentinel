# Microsoft Sentinel Transformations Library

This repository contains samples for multiple scenarios that are possible thanks to the new Log Analytics Custom Logs v2 and pipeline transformation features.

### Filtering

Ingestion time transformation allows you to drop specific fields from events or even full evets that you don't need to have in the workspace.

1. [Dropping fields](./Filtering#dropping-fields)
2. [Dropping entire records](./Filtering#dropping-rows)
3. [Dropping fields just for some vendors or devices](./Filtering#dropping-fields-just-for-some-vendors-or-devices)
4. [Multiple workspaces for independent entities](./Filtering#multiple-workspaces-for-idependent-entities)

### Enrichment/Tagging

Adding additional context to an event can greatly help analysts in their scoping and investigation process.

1. [Enriching an event or a field in the event with additional meaningful information](./Tagging#enriching-an-event-with-additional-meaningful-information)
2. [Translating a value into a customer’s business related value (Geo, Departments,…)](./Tagging#translating-a-value-into-a-customers-business-related-value)


### PII Masking/Obfuscation

Another scenario is obfuscation or masking of PII information. This can be Social Security Numbers, email addresses, phone numbers, etc.

1. [Masking last 4 digits of SSN](./Masking#masking-last-4-digits-of-social-security-number)
2. [Removing email addresses](./Masking#removing-personal-identifiable-information)

### Logstash

Among other enhancements, the new custom logs API allows you to ingest custom data into some Microsoft tables: SecurityEvent, WindowsEvent, CommonSecurityLog and Syslog. We have also updated the Microsoft Sentinel Logastash plugin to work with the new API.

1. [Perform log aggregation with Logastsh and then ingest into Syslog table](./Logstash#aggregation)