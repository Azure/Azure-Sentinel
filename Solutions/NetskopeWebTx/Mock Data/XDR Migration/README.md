# Netskope WebTx migration mock

`HighVolumeUnmanagedDevice.json` contains one synthetic 1.5 GB upload from an
unmanaged browser device and one benign 10 MB managed-client control. It
validates `Netskope - Anomalous User Behavior (High Volume from Unmanaged
Device)`.

The records follow the raw `Custom-NetskopeWebTx` stream contract, not the
destination table schema. Ingest them only into a non-production lab through a
DCR using the authoritative connector transform. Azure may replace stale event
times with ingestion time; regenerate timestamps when exact historical timing
is part of the detection hypothesis.
