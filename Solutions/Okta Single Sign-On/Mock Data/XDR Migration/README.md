# Okta SSO migration mock

`DeviceRegistrationMaliciousIP.json` contains two correlated synthetic events:
a successful device registration and an Okta ThreatInsight event whose actor
display name is the registration source IP. It validates `Device Registration
from Malicious IP`.

The records follow the raw `Custom-OktaSSO_CL` stream contract, not the
destination table schema. Ingest them only into a non-production lab through a
DCR using the authoritative connector transform. Refresh both `published`
values together when validating a rule with a short lookback.
