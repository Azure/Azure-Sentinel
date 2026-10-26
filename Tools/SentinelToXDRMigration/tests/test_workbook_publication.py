import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

from sentinel_xdr_migration import cli, workbook_publication as public, workbooks
from test_workbook_updates import (
    update_case, native_solution, migrated_solution, accepted, apply, updates, powershell_scan,
)


def legacy(case):
    root, path, baseline, _, _ = case
    document = json.loads(path.read_bytes())
    document["contentProvenance"]["authoredReview"] = updates.review_workbook_update(
        root, path.relative_to(root).as_posix(), baseline, accepted(case))
    path.write_text(json.dumps(document), encoding="utf-8")
    return path.read_bytes()


def cleanup_review(root, path):
    review = public.plan_publication(root, path.relative_to(root).as_posix())
    review.update(actor="private-reviewer-account", reference="private session authorization",
                  decision="accept")
    return review


def test_legacy_cleanup_retains_exact_private_proof_not_public_history(update_case):
    root, path, _, _, _ = update_case
    original = legacy(update_case)
    before = json.loads(original)
    review = cleanup_review(root, path)
    result = public.clean_publication(root, path.relative_to(root).as_posix(),
                                      public._sha(original), review)
    clean = json.loads(path.read_bytes())
    assert {k: v for k, v in clean.items() if k != "contentProvenance"} == {
        k: v for k, v in before.items() if k != "contentProvenance"}
    assert set(clean["contentProvenance"]) == {
        "format", "origin", *public.DEPENDENCIES}
    serialized = json.dumps(clean)
    for forbidden in ("actor", "reference", "decision", "queries", "reversePayloadChanges",
                      "authoredReview", "nativeReview", "conversion", "private-reviewer-account",
                      "private session authorization", "reviewer-fixture"):
        assert forbidden not in serialized
    receipt_path = Path(result["localReceipt"])
    assert receipt_path.is_relative_to(root / "Logs")
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt["evidence"]["inputArtifact"].encode("utf-8") == original
    assert receipt["evidence"]["review"] == review
    assert receipt["evidence"]["sourceArtifacts"]
    assert public.publication_errors(root, clean) == []
    receipt_path.unlink()
    for folder in ("Workbook Sources", "Workbooks"):
        if (root / folder).exists():
            shutil.rmtree(root / folder)
    # Structure is portable; private acceptance is neither claimed nor inferred.
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 0
    assert public.publication_errors(root, clean)


@pytest.mark.parametrize("field", ["actor", "reference", "decision", "queries", "conversion", "authoredReview"])
def test_public_metadata_rejects_reembedded_review_history(update_case, field):
    root, path, _, _, _ = update_case
    apply(update_case)
    document = json.loads(path.read_bytes())
    document["contentProvenance"][field] = "not public metadata"
    assert workbooks.authored_schema_errors(document)
    assert public.publication_errors(root, document)


@pytest.mark.parametrize("mutation", ["hash", "actor", "decision", "current-payload"])
def test_cleanup_is_hash_bound_and_never_changes_input_on_failure(update_case, mutation):
    root, path, _, index, _ = update_case
    original = legacy(update_case)
    review = cleanup_review(root, path)
    if mutation == "hash":
        review["inputSha256"] = "0" * 64
    elif mutation == "actor":
        review["actor"] = " "
    elif mutation == "decision":
        review["decision"] = None
    else:
        document = json.loads(original)
        document["items"][index]["content"]["query"] += " | take 10"
        path.write_text(json.dumps(document), encoding="utf-8")
    unchanged = path.read_bytes()
    with pytest.raises(ValueError):
        public.clean_publication(root, path.relative_to(root).as_posix(),
                                 public._sha(original), review)
    assert path.read_bytes() == unchanged


def test_public_baseline_needs_fresh_explicit_review_for_later_edits(update_case):
    root, path, baseline, index, _ = update_case
    apply(update_case)
    baseline.write_bytes(path.read_bytes())
    document = json.loads(path.read_bytes())
    document["items"][index]["content"]["query"] += " | take 9"
    path.write_text(json.dumps(document), encoding="utf-8")
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 0
    assert public.publication_errors(root, document)
    apply(update_case)
    assert public.publication_errors(root, json.loads(path.read_bytes())) == []


@pytest.mark.parametrize("operation", ["update", "cleanup"])
def test_rekeyed_receipt_cannot_reuse_old_authorization_for_new_settings(update_case, operation):
    root, path, _, _, _ = update_case
    if operation == "update":
        applied = apply(update_case)
    else:
        legacy(update_case)
        review = cleanup_review(root, path)
        applied = public.clean_publication(root, path.relative_to(root).as_posix(),
                                           review["inputSha256"], review)
    document = json.loads(path.read_bytes())
    receipt = json.loads(Path(applied["localReceipt"]).read_bytes())
    document["isLocked"] = not document["isLocked"]
    receipt["canonicalDocumentSha256"] = public.digest(document)
    receipt["evidence"]["publicDocument"] = document
    receipt.pop("receiptSha256")
    receipt["receiptSha256"] = public.digest(receipt)
    public._receipt_path(root, document).write_text(json.dumps(receipt), encoding="utf-8")
    path.write_text(json.dumps(document), encoding="utf-8")
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 0
    assert public.publication_errors(root, document)


def test_reauthorization_archives_previous_local_receipt_without_shipping_it(update_case):
    root, path, _, _, _ = update_case
    first = apply(update_case)
    receipt_path = Path(first["localReceipt"])
    original = receipt_path.read_bytes()
    review = cleanup_review(root, path)
    public.clean_publication(root, path.relative_to(root).as_posix(), review["inputSha256"], review)
    assert receipt_path.read_bytes() != original
    assert any(candidate.read_bytes() == original for candidate in receipt_path.parent.glob("*.json"))
    assert public.publication_errors(root, json.loads(path.read_bytes())) == []


def test_reproduction_is_explicit_git_ref_bound_and_not_local_authoring_acceptance(update_case, request, monkeypatch):
    root, path, _, index, _ = update_case
    result = apply(update_case)
    document = json.loads(path.read_bytes())
    receipt_path = Path(result["localReceipt"])
    receipt_path.unlink()
    for folder in ("Workbook Sources", "Workbooks"):
        if (root / folder).exists():
            shutil.rmtree(root / folder)
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    def writable_git_objects():
        for item in (root / ".git").rglob("*"):
            if item.is_file():
                item.chmod(0o700)
    request.addfinalizer(writable_git_objects)
    (root / ".gitignore").write_text("Logs/\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "--", ".gitignore",
                    path.relative_to(root).as_posix(), "Data"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "--quiet", "-m", "Public baseline"],
                   check=True)
    assert public.publication_errors(root, document)
    assert public.publication_errors(root, document, public_ref="HEAD") == []
    assert public.publication_errors(root, document, public_ref="missing-ref")
    monkeypatch.setenv("SENTINEL_XDR_WORKBOOK_PUBLIC_REF", "HEAD")
    if shutil.which("pwsh"):
        run = powershell_scan(root, path)
        assert run.returncode == 0, run.stdout + run.stderr
    assert public.publication_errors(root, document)
    document["items"][index]["content"]["query"] += " | take 11"
    path.write_text(json.dumps(document), encoding="utf-8")
    assert public.publication_errors(root, document, public_ref="HEAD")
    if shutil.which("pwsh"):
        assert powershell_scan(root, path).returncode != 0


@pytest.mark.skipif(not shutil.which("pwsh"), reason="PowerShell 7 required")
def test_package_resource_and_archive_contain_only_public_dependencies(update_case):
    root, path, _, _, _ = update_case
    result = apply(update_case)
    document = json.loads(path.read_bytes())
    # Exercise the actual registration/installation constructors, not a live build.
    script = Path(__file__).resolve().parents[3] / "Tools" / "Create-Azure-Sentinel-Solution" / "common" / "commonFunctions.ps1"
    def literal(value):
        return "'" + str(value).replace("'", "''") + "'"
    command = (
        "$ErrorActionPreference='Stop'; . " + literal(script) + "; "
        "$doc=Get-Content -LiteralPath " + literal(path) + " -Raw | ConvertFrom-Json; "
        "Assert-DefenderWorkbookDocument -Document $doc -SolutionRoot " + literal(root)
        + " -SolutionName " + literal(root.name) + " -ContentPath " + literal(path.relative_to(root).as_posix()) + "; "
        "$resolved=[pscustomobject]@{packageId='fixture';packageVersion=$doc.xdrMetadata.version;"
        "contentId=$doc.xdrMetadata.contentId;contentVersion=$doc.xdrMetadata.version}; "
        "$notebook=$doc | ConvertTo-Json -Depth 100 | ConvertFrom-Json; "
        "$notebook.PSObject.Properties.Remove('xdrMetadata');$notebook.contentProvenance=$resolved; "
        "$resource=[pscustomobject]@{import='MicrosoftSecurity';type='Microsoft.Security/workbooks@2026-06-01-preview';"
        "properties=[pscustomobject]@{id=$doc.xdrMetadata.instanceId;content=$notebook}}; "
        "$install=New-DefenderWorkbookInstallDeployment -DeploymentName fixture -WorkbookResource $resource -ParserDependencies @(); "
        "$registration=New-DefenderWorkbookRegistration -DeploymentName fixture -InstallDeployment $install "
        "-Document $doc -ResolvedProvenance $resolved -PackageName fixture; "
        "[pscustomobject]@{resources=@($install,$registration)} | ConvertTo-Json -Depth 100 -Compress"
    )
    run = subprocess.run(["pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
                         capture_output=True, text=True, encoding="utf-8",
                         env={**os.environ, "SENTINEL_XDR_PYTHON": sys.executable})
    assert run.returncode == 0, run.stdout + run.stderr
    package = json.loads(run.stdout)
    archive = root / "fixture-package.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("mainTemplate.json", json.dumps(package))
    with zipfile.ZipFile(archive) as output:
        assert output.namelist() == ["mainTemplate.json"]
        text = output.read("mainTemplate.json").decode("utf-8")
    assert Path(result["localReceipt"]).exists()
    for forbidden in ("authoredReview", "nativeReview", "reversePayloadChanges", '"actor"',
                      '"reference"', '"decision"', "reviewer-fixture", '"queries"'):
        assert forbidden not in text
    registration = package["resources"][1]["properties"]
    assert registration["version"] == document["xdrMetadata"]["version"]
    assert registration["contentProvenance"]["contentVersion"] == document["xdrMetadata"]["version"]
    assert registration["contentId"] == document["xdrMetadata"]["contentId"]
    installed = package["resources"][0]["properties"]["template"]["resources"]["workbook"]["properties"]
    assert installed["id"] == document["xdrMetadata"]["instanceId"]
    assert installed["content"]["version"] == "Notebook/1.0"
    assert installed["content"]["items"] == document["items"]


def test_clean_cli_preserves_local_authorization(update_case, capsys):
    root, path, _, _, _ = update_case
    legacy(update_case)
    args = ["--solution", str(root), "--content", path.relative_to(root).as_posix()]
    assert cli.main(["workbook-publication-plan", *args]) == 0
    plan = json.loads(capsys.readouterr().out)
    plan.update(actor="local account", reference="user authorization", decision="accept")
    review = root / "Logs" / "publication-review.json"
    review.parent.mkdir(exist_ok=True)
    review.write_text(json.dumps(plan), encoding="utf-8")
    assert cli.main(["workbook-publication-clean", *args, "--review", str(review),
                     "--expected-sha256", plan["inputSha256"]]) == 0
    receipt = Path(json.loads(capsys.readouterr().out)["localReceipt"])
    assert json.loads(receipt.read_bytes())["evidence"]["review"]["reference"] == "user authorization"
    receipt.unlink()
    assert cli.main(["workbook-publication-validate", *args, "--mode", "structural"]) == 0
    capsys.readouterr()
    assert cli.main(["workbook-publication-validate", *args, "--mode", "authoring"]) == 1
    capsys.readouterr()
    assert cli.main(["native-workbook-validate", "--solution", str(root)]) == 1
