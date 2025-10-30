# Logstash

There are still situations where logstash might be still needed to provide advanced functionality. This is the case when aggregation is needed, or if you need to enrich logs with external data.

## Aggregation

In this example, we show how logstash can be used to aggregate multiple duplicate records into a single one that has a counter with the number of times the message was repeated over a period. We then push this message to Microsoft standard table, Syslog.

In this folder you can find:

- Logstash pipeline configuration file
- DCR to ingest logs into Syslog table

### Logstash pipeline configuration file

We will just focus on the aggregation and output part of the file.

This is how the aggregation section works:

1. If the message contains a given string (```Started session``` in our case), we enter aggregation mode
2. Aggregation will happen when the Computer value is the same (```task_id``` property)
3. A block of code is executed for each event that does the following:
- In the first iteration, we set a variable (logins) to 0
- Logins variable gets incremented by 1 with each new iteration
- Computer field is also populated
- The event is discarded (```event.cancel()```)
4. The fields in the previous code block will be pushed to the event when the timeout is reach (```push_map_as_event_on_timeout```)
5. Timeout time is 15 seconds. This meanse that when a new message is detected, we will aggregate duplicated messages in the following 15 seconds
6. When the timeout is reached, a code block is executed (```timeout_code```), where Time and SyslogMessage fields are set. 

For more information on logstash aggregation's plugin, go [here](https://www.elastic.co/guide/en/logstash/current/plugins-filters-aggregate.html).

The output section uses the new Log Analytics plugin which is fully documented [here](placeholder).

### Ingestion DCR

We will focus on two sections of the LogstashDCR.json file: *streamDeclarations* and *dataFlows*.

In *streamDeclarations* we define which fields will be ingested. The names are important as these must be the same used in the logstash file.

In *dataFlows* we use the *transformKql* property to assign the fields to the proper field names. Specially important is the *outputStream* property, which points to the target table. If the table schema is defined by Microsoft, it will start with ```Microsoft-``` followed by the table name, in our case *Syslog*.

Deploy this DCR:

[![Deploy this DCR to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjaviersoriano%2Fsentinel-transformations-library%2Fmain%2FLogstash%2FLogstashDCR.json)