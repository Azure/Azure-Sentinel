# Selective CCF Push cutover package

Build this opt-in package when an existing Microsoft Sentinel workspace needs
new Push destinations for Abuse Mailbox, Posture Change, and fallback Logs.
The workspace must already have six compatible DCR-based Abnormal Security
tables for Threat Log, Audit Log, Case, ATO Case, Vendor Case, and Remediation.

Run from the repository root with Python 3:

```bash
python3 Solutions/AbnormalSecurity/Tools/build-selective-push-package.py \
  --version 3.1.1 \
  --output ./abnormal-security-selective-push.zip
```

Choose a version greater than the source package version and any Abnormal
Security package version already installed in the target workspace. Use
`--source` to point to another local directory containing the generated
`mainTemplate.json` and `createUiDefinition.json`.

The output package provisions three `*_V2_CL` tables. Its data collection rule
routes the other six streams to the existing tables without including table
update resources for them. All input stream names stay the same. The connector
UI and bundled Sentinel content reference the new destinations.

Before handing off the package, validate both the ARM installation and the
Push connector's **Deploy** action in a non-production workspace with the six
expected tables. Validate the existing destination schemas and check for an
existing Push connector or data collection rule using the same resource names.
This package uses the standard Push connector identity.

Install the custom ARM package into the target workspace and deploy Push from
the connector page. Keep the legacy connection active until Push ingestion and
detections are verified. Update customer-specific queries and rules that use
the three original names. Keep the original tables available for historical
queries.
