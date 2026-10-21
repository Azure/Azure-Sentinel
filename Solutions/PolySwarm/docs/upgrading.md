# Upgrading from the earlier enrichment-only playbooks

This is for anyone who already deployed the earlier, enrichment-only version of this
integration (three playbooks, plus the custom connector, with no per-playbook folder
layout and no Key Vault requirement). That earlier work is preserved for reference at
`reference/existing-enrichment-README.md`; it is not packaged or shipped from this
repository. This solution supersedes it and adds sandbox detonation, data connectors,
analytics rules, hunting queries, and entity-triggered variants.

## What changed

- **The PolySwarm API key moved from a deployment parameter to Azure Key Vault.**
  Every playbook in this solution reads its key at runtime through its own Key Vault
  API connection and managed identity, using the `KeyVaultName` and
  `KeyVaultSecretName` parameters. The earlier playbooks took the key directly as a
  `securestring` deployment parameter. See `README.md`, "Key Vault setup".
- **The folder layout changed.** The earlier playbooks lived as flat files under
  `playbooks/`, one file per entity type
  (`playbooks/polyswarm-enrich-hash-from-incident.json`, and so on), each named like
  `PolySwarm-Enrich-FileHash-IncidentTriggered` was not yet a convention. This
  solution gives every playbook its own folder under `Playbooks/` (for example
  `Playbooks/PolySwarm-Enrich-FileHash/`), holding both an incident-triggered and, for
  the enrichment playbooks, an entity-triggered template, plus that playbook's own
  `readme.md`.
- **Entity triggers were added.** The earlier playbooks were incident-triggered only,
  running against every matching entity on an incident. This solution adds an
  entity-triggered variant for each enrichment playbook, so an analyst can run
  enrichment against a single selected entity instead of the whole incident.
- **Sandbox detonation, data connectors, analytics rules and hunting queries are new.**
  None of these existed in the earlier enrichment-only version. They are additive; you
  do not need to change anything about your existing enrichment deployment to add
  them, beyond the Key Vault migration below, which every playbook in this solution
  (including enrichment) requires.

What did not change: the two-call hash design, the response fields each playbook
reads, the serial (`concurrency: 1`) loop structure, and the retry policy on every
PolySwarm HTTP call. If your earlier deployment's comments looked a certain way, this
solution's enrichment playbooks produce the same shape of comment, just from a
per-folder template that reads its key from Key Vault instead of a parameter.

## How to move over

1. **Create the Key Vault secret.** Create (or reuse) an Azure Key Vault in the same
   tenant as your Sentinel workspace, with `enabledForTemplateDeployment` set to
   `true`, and add your PolySwarm API key as a secret (for example named
   `PolySwarmApiKey`). See `README.md`, "Key Vault setup", for the full steps,
   including the **Key Vault Secrets User** role each playbook's managed identity
   needs on it.
2. **Deploy the new playbooks.** Deploy the enrichment playbooks you already had
   (`PolySwarm-Enrich-FileHash`, `PolySwarm-Enrich-Url`, `PolySwarm-Enrich-Ip`) from
   their new locations under `Playbooks/`, supplying `KeyVaultName` and, if you did
   not use the default secret name, `KeyVaultSecretName`. Add
   `PolySwarm-Enrich-Domain` and any sandbox playbooks, data connectors, analytics
   rules, or hunting queries you now also want; each deploys and is configured
   independently. See `docs/deployment.md` for the full deployment order and role
   assignments.
3. **Repoint automation rules.** Each new playbook deploys as a separate Logic App
   resource with a new name (for example `PolySwarm-Enrich-FileHash-IncidentTriggered`
   rather than whatever name your earlier deployment used), so it does not replace the
   old Logic App in place. Update every automation rule that currently runs an old
   playbook to run the corresponding new one instead. An automation rule left pointed
   at the old playbook keeps running it, which duplicates PolySwarm's API usage and
   posts duplicate comments once both playbooks are attached to overlapping
   automation rules.
4. **Delete the old Logic Apps.** Once every automation rule has been repointed and
   you have confirmed the new playbooks are commenting correctly on test incidents,
   delete the old enrichment Logic Apps (and their now-unused API connections and
   securestring parameter values) from your resource group. Leaving them in place
   costs nothing to run on their own, but an old Logic App still attached to any
   automation rule you missed in step 3 will keep firing.

## What you do not need to do

- You do not need to re-request a PolySwarm API key; the same key works once it is
  stored as a Key Vault secret.
- You do not need to migrate any historical incident comments; nothing in this
  solution reads or rewrites comments an earlier playbook already posted.
- You do not need to deploy every new component. Sandbox detonation, the data
  connectors, analytics rules and hunting queries are each optional and gated on their
  own PolySwarm entitlement; deploy only what your account and use case need. See
  `README.md`, "Prerequisites".
