# CylancePROTECT

Author: acnccd, Accelerynt

Here you will find two versions of the same parser. The second version, added with this documentation, has a workaround for the Event Type column not properly populating. The changes made were not applied to the original parser because it appears the issue is not with the parser itself, but because some of the SyslogMessage values have this attribute title missing before the value. This version can be used to extract the Event Type attribute value in cases where its header is missing.
