# Repository agent instructions

## Protected agent and tooling implementation

During normal repository tasks, treat agent definitions, skills, instructions,
tooling backends, schemas, tests, dependency metadata, workflow definitions,
safety gates, permission checks, packaging behavior, and capabilities as
immutable.

Do not create, edit, delete, rename, patch, bypass, or replace implementation
under these paths to recover from a task, environment, dependency,
authentication, conversion, validation, packaging, deployment, or runtime
failure:

- `AGENTS.md`;
- `.github/agents/**`;
- `.github/skills/**`; or
- `Tools/**`.

Stop the affected operation and report that a maintainer change is required.
Implementation changes are allowed only in a separate development task where
the user explicitly states that they are acting as a repository/toolkit
maintainer and requests the specific implementation change. Requests to run,
retry, continue, migrate, package, validate, deploy, or fix generated content
never grant permission to change agent or tooling implementation.

The XDR Solution Manager is stricter: it can never make agent or tooling
implementation changes, even when explicitly requested by an owner or
maintainer. Route such work to a different development agent or require it to
be performed manually.

When a request involves Sentinel-to-Defender-XDR migration, XDR Detections,
hybrid solution packaging, or AR/CD qualification:

1. Read and follow
   `Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`.
2. Treat that file as the canonical workflow; do not redefine its stages or
   gates in this adapter.
3. Keep deterministic work in the repository Python and PowerShell tools.
4. Require the user to explicitly select `authoring` or `qualification`. There
   is no default.
5. Deployment, mock ingestion, and alert parity are Qualification-only actions
   and require explicit exact-scope approval.
6. Use packaging V4 for XDR Detections. V3 is Sentinel-only.
7. Resume from `workflow-state.json` and record artifacts and evidence.
8. Require explicit approval immediately before any environment write.
