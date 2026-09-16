# Netskope AlertEvents migration mock

`DLPIncidentSpike.json` contains eleven correlated synthetic DLP incidents for
`mock.netskope@example.test` and one benign policy control. It validates
`Netskope - DLP Incident Spike`.

The records follow the raw `Custom-NetskopeAlertEvents` stream contract, not the
destination table schema. Ingest them only into a non-production lab through a
DCR using the authoritative connector transform. Azure may replace stale event
times with ingestion time; regenerate timestamps when exact historical timing
is part of the detection hypothesis.
