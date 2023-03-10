An ABAP script example provided as-is that can help estimate a few of the key log sizes between selected dates (For a period of up to 12 months).
The tools helps with rough estimations while actual production figures can vary significantly.

The evaluated logs are:
- Application log header (BALHDR)
- Change document header* (CDHDR)
- Security audit log

How to use:
1. Manually create a new report (SE38), named: ZLOG_STATISTICS.
2. Paste the code snippet as-is, save the changes and activate the report.
3. Run the report on Production system or Production copy system.

* Extrapolation is needed between number of change document headers and actual (POS) records, this should be carried in consultancy with the SAP team. We typically assume a 1:6 ratio POC records for each header record ; the actual figures can vary