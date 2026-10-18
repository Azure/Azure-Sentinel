"""Local-only review/export controls; persisted migration results are never changed."""

from __future__ import annotations

from collections import Counter
from html import escape
import json
import re
from typing import Any


def review_candidates(report: dict[str, Any]) -> list[dict[str, Any]]:
    ids = Counter(str((rule.get("analyticRule") or {}).get("id") or "") for rule in report["rules"])
    result = []
    for index, rule in enumerate(report["rules"]):
        if not any("one tactic" in str(reason).lower() for reason in rule["customDetection"].get("reviewReasons") or []):
            continue
        classification = rule.get("attackClassification") or {}
        tactics = classification.get("sourceTactics")
        techniques = classification.get("sourceTechniques")
        source_id = str((rule.get("analyticRule") or {}).get("id") or "")
        digest = str(rule.get("sourceSha256") or "")
        reason = ""
        if not source_id or ids[source_id] != 1:
            reason = "Review individually: a unique source rule ID is required."
        elif not re.fullmatch(r"[a-f0-9]{64}", digest):
            reason = "Regenerate the report first: source file hash is not recorded."
        elif not isinstance(tactics, list) or not tactics or not all(isinstance(value, str) and value for value in tactics):
            reason = "Review individually: source tactic choices are unavailable."
        elif not isinstance(techniques, list) or not techniques or not all(
            isinstance(value, str) and re.fullmatch(r"T[0-9]{4}(?:\.[0-9]{3})?", value)
            for value in techniques
        ):
            reason = "Review individually: supported source technique IDs are unavailable."
        result.append({
            "index": index, "id": source_id, "name": str(rule["name"]),
            "sourceFile": rule.get("sourceFile"), "sourceSha256": digest,
            "tactics": tactics if isinstance(tactics, list) else [],
            "techniques": techniques if isinstance(techniques, list) else [],
            "eligible": not reason, "reason": reason,
        })
    return result


def render_bulk_review(report: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return ""
    payload = {
        "runId": (report.get("workflow") or {}).get("runId"),
        "generatedAt": report.get("generatedAt"),
        "solution": report.get("solutionPath") or report["solution"],
        "candidates": candidates,
    }
    return (
        '<section class="panel" id="bulk-review" data-review-payload="'
        + escape(json.dumps(payload, ensure_ascii=False), quote=True)
        + '"><details><summary>Review and export tactic overrides — no automatic application</summary>'
        '<p><strong>Historical review compatibility:</strong> multiple source tactics no longer require selection of one tactic '
        'for authoring. Regeneration preserves all source tactics in source order. These optional legacy exports correct '
        'techniques only for the named source tactic; they do not narrow or reorder tactics. '
        'V3.1 ARM packaging carries only the first tactic; direct Graph deployment still requires a single tactic. '
        'Neither operation proves classification parity.</p>'
        '<p>Select eligible rules in the table below, or select the currently visible eligible rules. '
        'A bulk tactic choice is applied only to rules listing that source tactic. Techniques are never chosen automatically: '
        'confirm their compatibility and observable behavior individually for every rule. '
        'Source tactic and technique lists are independent, not a verified compatibility matrix.</p>'
        '<p><strong>Pending export decisions are separate from recorded results.</strong> Nothing here resolves a finding, '
        'changes a query, accepts warning/review text, or clears a workflow gate. Data loss and timing mismatches cannot be '
        'bulk accepted as equivalent. This interface only downloads files; no local write service or cloud call is used.</p>'
        '<button type="button" id="select-visible">Select visible eligible rules</button> '
        '<button type="button" id="clear-selection">Clear selection and pending decisions</button>'
        '<p id="selection-count" role="status" aria-live="polite"></p>'
        '<label for="bulk-tactic">Source tactic whose techniques need correction</label> '
        '<select id="bulk-tactic"><option value="">Choose a tactic</option></select> '
        '<button type="button" id="set-bulk-tactic">Set tactic — leave techniques unselected</button>'
        '<p id="bulk-feedback" role="status" aria-live="polite"></p>'
        '<div id="decision-editor"></div>'
        '<h3>Preserve existing migration configuration</h3>'
        '<p>Import the existing complete configuration as JSON before merging. JSON is accepted by the migration '
        'tool as YAML. For an existing YAML file, first create its JSON equivalent using the documented local command. '
        'Unrelated root fields, rule overrides, and fields within selected rule overrides are retained.</p>'
        '<label for="review-config-file">Existing JSON configuration</label> '
        '<input type="file" id="review-config-file" accept=".json,application/json">'
        '<p><label><input type="checkbox" id="new-config"> I confirm no existing migration configuration needs preserving.</label></p>'
        '<p id="config-status" role="status">Import a configuration, or explicitly confirm that none exists.</p>'
        '<button type="button" id="preview-decisions">Preview exact merged configuration and review manifest</button>'
        '<p id="review-feedback" role="status" aria-live="polite"></p>'
        '<section id="review-preview" hidden><h3>Pending export — not applied or resolved</h3>'
        '<p>Inspect every selected ID and replacement below. For selected rules, only tactic and techniques are replaced; '
        'all other imported settings are preserved. The manifest records source-file SHA-256 hashes from this report.</p>'
        '<pre id="decision-preview"></pre>'
        '<h4>Merged configuration</h4><pre id="config-preview"></pre>'
        '<h4>Separate review manifest</h4><pre id="manifest-preview"></pre>'
        '<p><strong>Stale snapshot warning:</strong> compare the source IDs and file hashes with the current checkout before '
        'applying. The migration tool does not validate this review manifest or automatically reject a stale export. '
        'Re-import/re-export if the underlying configuration changed after import.</p>'
        '<button type="button" id="download-config" disabled>Download merged migration-reviewed-overrides.json</button> '
        '<button type="button" id="download-manifest" disabled>Download migration-reviewed-overrides.review.json</button>'
        '<h4>Apply only after reviewing the downloaded files</h4>'
        '<pre>sentinel-xdr-migration convert --solution "&lt;solution-path&gt;" --run-id "&lt;run-id&gt;" '
        '--config "&lt;downloaded-merged-config.json&gt;" --overwrite\n'
        'sentinel-xdr-migration solution-report --solution "&lt;solution-path&gt;" --run-id "&lt;run-id&gt;"</pre>'
        '<p>Use the selected run shown above and the existing workflow approval process. Conversion may overwrite '
        'same-provenance drafts; inspect the resulting changes and continue required validation. '
        'Do not pass the separate review manifest as --config. Exporting alone does not change the report statuses.</p>'
        '</section></details></section>'
    )


BULK_SCRIPT = """
(() => {
  const root = document.getElementById("bulk-review");
  if (!root) return;
  const payload = JSON.parse(root.dataset.reviewPayload);
  const candidates = new Map(payload.candidates.filter(r => r.eligible).map(r => [r.id, r]));
  const selected = new Set();
  const decisions = new Map();
  const byId = id => document.getElementById(id);
  const checks = [...document.querySelectorAll(".review-select:not(:disabled)")];
  let imported = null;
  let preview = null;
  let importGeneration = 0;
  function object(value) { return value !== null && typeof value === "object" && !Array.isArray(value); }
  function own(value, key) { return Object.prototype.hasOwnProperty.call(value, key); }
  function invalidate() {
    preview = null;
    byId("review-preview").hidden = true;
    byId("download-config").disabled = true;
    byId("download-manifest").disabled = true;
    byId("review-feedback").textContent = "Pending decisions only; recorded migration results are unchanged.";
  }
  function state(id) {
    if (!decisions.has(id)) decisions.set(id, {tactic: "", techniques: new Set(), confirmed: false});
    return decisions.get(id);
  }
  function node(tag, text) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    return element;
  }
  function tacticOptions(select, values, chosen) {
    select.replaceChildren(new Option("Choose one tactic", ""));
    [...new Set(values)].forEach(value => select.add(new Option(value, value)));
    select.value = chosen;
  }
  function render() {
    invalidate();
    byId("selection-count").textContent = `${selected.size} selected; ${[...selected].filter(id => state(id).confirmed).length} individually confirmed pending decisions`;
    const available = [...selected].flatMap(id => candidates.get(id).tactics);
    tacticOptions(byId("bulk-tactic"), available, byId("bulk-tactic").value);
    const editor = byId("decision-editor");
    editor.replaceChildren();
    for (const id of selected) {
      const rule = candidates.get(id), choice = state(id);
      const section = node("fieldset");
      section.dataset.decisionId = id;
      section.append(node("legend", `${rule.name} — ${id}`));
      const tacticLabel = node("label", "Source tactic to correct ");
      const tactic = node("select");
      tactic.dataset.choice = "tactic";
      tacticOptions(tactic, rule.tactics, choice.tactic);
      tacticLabel.append(tactic);
      section.append(tacticLabel);
      section.append(node("p", "Select compatible source techniques/subtechniques individually; no pairing is inferred."));
      const confirmationLabel = node("label");
      const confirmation = node("input");
      confirmation.type = "checkbox";
      confirmation.dataset.choice = "confirmed";
      confirmation.checked = choice.confirmed;
      function resetConfirmation() {
        choice.confirmed = false;
        confirmation.checked = false;
        invalidate();
        byId("selection-count").textContent = `${selected.size} selected; ${[...selected].filter(key => state(key).confirmed).length} individually confirmed pending decisions`;
      }
      for (const technique of [...new Set(rule.techniques)]) {
        const label = node("label");
        label.className = "chip";
        const input = node("input");
        input.type = "checkbox";
        input.dataset.choice = "technique";
        input.value = technique;
        input.checked = choice.techniques.has(technique);
        input.addEventListener("change", () => {
          if (input.checked) choice.techniques.add(technique); else choice.techniques.delete(technique);
          resetConfirmation();
        });
        label.append(input, document.createTextNode(` ${technique} `));
        section.append(label);
      }
      tactic.addEventListener("change", () => {
        choice.tactic = tactic.value;
        choice.techniques.clear();
        choice.confirmed = false;
        render();
      });
      confirmationLabel.append(confirmation, document.createTextNode(
        " I individually verified that these techniques/subtechniques belong to this tactic and describe this rule's observable behavior."
      ));
      const line = node("p"); line.append(confirmationLabel); section.append(line);
      confirmation.addEventListener("change", () => {
        choice.confirmed = confirmation.checked;
        invalidate();
        byId("selection-count").textContent = `${selected.size} selected; ${[...selected].filter(key => state(key).confirmed).length} individually confirmed pending decisions`;
      });
      editor.append(section);
    }
  }
  checks.forEach(input => input.addEventListener("change", () => {
    if (input.checked) selected.add(input.dataset.reviewId);
    else { selected.delete(input.dataset.reviewId); decisions.delete(input.dataset.reviewId); }
    render();
  }));
  byId("select-visible").addEventListener("click", () => {
    checks.filter(input => !input.closest("tbody.rule").hidden).forEach(input => {
      input.checked = true; selected.add(input.dataset.reviewId);
    });
    render();
  });
  byId("clear-selection").addEventListener("click", () => {
    selected.clear(); decisions.clear(); checks.forEach(input => { input.checked = false; });
    byId("bulk-feedback").textContent = ""; render();
  });
  byId("set-bulk-tactic").addEventListener("click", () => {
    const tactic = byId("bulk-tactic").value;
    if (!tactic || !selected.size) {
      byId("bulk-feedback").textContent = "Select rules and a source tactic to correct first."; return;
    }
    let applied = 0;
    const skipped = [];
    for (const id of selected) {
      const rule = candidates.get(id);
      if (!rule.tactics.includes(tactic)) {
        decisions.delete(id);
        skipped.push(`${rule.name}: ${tactic} is not in the source tactic list; previous pending choice cleared.`);
        continue;
      }
      decisions.set(id, {tactic, techniques: new Set(), confirmed: false});
      applied++;
    }
    render();
    byId("bulk-feedback").textContent = `Set tactic on ${applied} compatible rules. No techniques or confirmations selected. ${skipped.join(" ")}`;
  });
  function validateConfig(value) {
    if (!object(value)) throw new Error("The complete configuration must be a JSON object.");
    if (own(value, "ruleOverrides")) {
      if (!object(value.ruleOverrides)) throw new Error("ruleOverrides must be an object.");
      for (const [id, entry] of Object.entries(value.ruleOverrides)) {
        if (!object(entry)) throw new Error(`Override ${id} must be an object; import was not accepted.`);
      }
    }
    return value;
  }
  byId("review-config-file").addEventListener("change", async event => {
    const generation = ++importGeneration;
    imported = null;
    byId("new-config").checked = false;
    invalidate();
    const file = event.target.files[0];
    if (!file) { byId("config-status").textContent = "No configuration imported."; return; }
    try {
      const text = await file.text();
      if (generation !== importGeneration) return;
      imported = validateConfig(JSON.parse(text.replace(/^\\uFEFF/, "")));
      byId("config-status").textContent = `Imported ${file.name}; unrelated settings will be preserved.`;
    } catch (error) {
      if (generation !== importGeneration) return;
      byId("config-status").textContent = `Import rejected: ${error.message} Convert YAML to JSON locally first if needed.`;
    }
  });
  byId("new-config").addEventListener("change", () => {
    ++importGeneration;
    imported = null;
    byId("review-config-file").value = "";
    invalidate();
    byId("config-status").textContent = byId("new-config").checked ?
      "Explicitly starting a new configuration; no existing settings will be merged." :
      "Import the complete configuration or confirm that none exists.";
  });
  byId("preview-decisions").addEventListener("click", () => {
    invalidate();
    try {
      if (!selected.size) throw new Error("Select at least one eligible rule.");
      if (!imported && !byId("new-config").checked) throw new Error("Import the existing configuration or explicitly confirm that none exists.");
      const config = imported ? JSON.parse(JSON.stringify(imported)) : {};
      const oldOverrides = own(config, "ruleOverrides") ? config.ruleOverrides : {};
      // Null-prototype dictionaries keep imported or source-provided keys as data.
      const overrides = Object.create(null);
      for (const [key, value] of Object.entries(oldOverrides)) overrides[key] = value;
      const audit = [];
      for (const id of selected) {
        const rule = candidates.get(id), choice = state(id);
        if (!choice.tactic || !rule.tactics.includes(choice.tactic)) throw new Error(`${rule.name}: choose a tactic from this rule's source list.`);
        if (!choice.techniques.size) throw new Error(`${rule.name}: explicitly select at least one compatible technique/subtechnique.`);
        if ([...choice.techniques].some(value => !rule.techniques.includes(value))) throw new Error(`${rule.name}: technique is not in this source snapshot.`);
        if (!choice.confirmed) throw new Error(`${rule.name}: individual compatibility/behavior confirmation is required.`);
        const prior = own(oldOverrides, id) ? oldOverrides[id] : {};
        const entry = Object.create(null);
        for (const [key, value] of Object.entries(prior)) entry[key] = value;
        entry.tactic = choice.tactic;
        entry.techniques = [...choice.techniques];
        overrides[id] = entry;
        audit.push({
          sourceId: id, sourceFile: rule.sourceFile, sourceSha256: rule.sourceSha256,
          sourceTactics: rule.tactics, sourceTechniques: rule.techniques,
          selectedTactic: choice.tactic, selectedTechniques: [...choice.techniques],
          compatibilityIndividuallyConfirmed: true,
          previousSelection: {
            tactic: own(prior, "tactic") ? prior.tactic : null,
            techniques: own(prior, "techniques") ? prior.techniques : null
          }
        });
      }
      config.ruleOverrides = overrides;
      const manifest = {
        schemaVersion: "1.0", kind: "PendingReviewedTacticOverrides",
        runId: payload.runId, reportGeneratedAt: payload.generatedAt,
        exportedAt: new Date().toISOString(), solution: payload.solution,
        applied: false, snapshotEnforcement: "Manual comparison required; not enforced by migration tool",
        decisions: audit
      };
      preview = {config: JSON.stringify(config, null, 2), manifest: JSON.stringify(manifest, null, 2)};
      byId("decision-preview").textContent = JSON.stringify(audit, null, 2);
      byId("config-preview").textContent = preview.config;
      byId("manifest-preview").textContent = preview.manifest;
      byId("review-preview").hidden = false;
      byId("download-config").disabled = false;
      byId("download-manifest").disabled = false;
      byId("review-feedback").textContent = `${audit.length} individually confirmed decisions previewed; pending export/application. Persisted results remain unchanged.`;
    } catch (error) {
      byId("review-feedback").textContent = error.message;
    }
  });
  function download(kind, name) {
    if (!preview) return;
    const url = URL.createObjectURL(new Blob([preview[kind] + "\\n"], {type: "application/json"}));
    const link = node("a"); link.href = url; link.download = name;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    byId("review-feedback").textContent = "Download requested. Decisions are still pending application; no findings or gates were resolved.";
  }
  byId("download-config").addEventListener("click", () => download("config", "migration-reviewed-overrides.json"));
  byId("download-manifest").addEventListener("click", () => download("manifest", "migration-reviewed-overrides.review.json"));
  render();
})();
"""
