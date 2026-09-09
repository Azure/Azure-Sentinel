# CollectExchSec Configuration Editor (WinForms Modular)

Features:
- Modular multi-file architecture
- Responsive multi-column question layout (FlowLayoutPanel, auto re-wrap on resize)
- Full conditional visibility + rehydration
- Per-field restore, validation (regex + hook)
- Array & addons editors
- UDS Log Processor and Instance Configuration grids
- Undo/Redo stack (Ctrl+Z / Ctrl+Y) with full state snapshots
- Logging (plain text) & telemetry (JSON lines) with session id
- Export of only changed settings (File > Export Changed Settings…)
- Clipboard operations (load, paste dialog, copy current JSON)
- Raw JSON preview & diff summary before saving
- Read-only toggle

Run:
```powershell
pwsh -ExecutionPolicy Bypass -File .\Scripts\WinFormsMod\Main.ps1 -ConfigPath .\Config\CollectExchSecConfiguration.json
```

Logs:
- Created under `Scripts/WinFormsMod/logs/`
  - actions_*.log: human readable
  - telemetry_*.jsonl: structured events

Exporting Changed Settings:
- Produces JSON with:
  - Questions: dictionary of path->new value
  - UDSLogProcessor: array of modified rows (full rows)
  - InstanceConfiguration: hash of modified instances (full sub-objects)

Customization:
- Adjust `$Global:QuestionPanelBaseWidth` & related constants in `UI.Sections.ps1`.
- Increase undo history via `UndoMax` in `State.ps1`.
- Extend validation hooks in `Validate-Question` (Utilities.ps1).
- Add encryption for secure fields prior to save if required.

Future Ideas:
- Debounced undo snapshotting
- JSON schema validation
- Theming / high contrast
- Telemetry opt-in/out flag