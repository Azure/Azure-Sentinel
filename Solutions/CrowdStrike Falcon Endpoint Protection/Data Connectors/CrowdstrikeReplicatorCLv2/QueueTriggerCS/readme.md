# Azure Storage Queue Trigger Function App for CrowdStrike

The `QueueTriggerCS` makes it incredibly easy to react to new Queues inside of Azure Queue Storage. The messages are ingested into this queue using `Replicator` Function app. Based on the inputs received, S3 bucket is downloaded and ingested into log analytics using DCR endpoint after customization of the event.

## How it works

For `QueueTriggerCS` to work, Replicator function app ingest data into the associated Azure Storage Queue. If the bucket is not processed properly, the message would land into poison queue, which would have to be processed manually.

## Learn more

Azure Storage Queue trigger-based function app fires for each new entry in the queue. This would read the message and execute the following steps:
1.	Download the bucket and decompress it in chunks.
2.	Classify each event row into suitable schema and extract the required fields. This would leave the remaining as a JSON in AdditionalFields.
3.	Send the event row to the suitable stream of Data Collection Rule (DCR) and finally land the data into Normalized Tables.
4.	For the remaining event rows which could not be mapped into one of the suitable schemas, send them to a single custom table (CLv2).
