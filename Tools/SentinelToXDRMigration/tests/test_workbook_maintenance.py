from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4

import pytest

from solution_manager.authoring import workbook_maintenance as maintenance
from solution_manager.authoring import workbook_publication as publication

REMOTE = "https://example.invalid/approved/published.git"


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True,
    ).stdout.decode("utf-8").strip()


def write(path, document):
    path.write_text(json.dumps(document), encoding="utf-8")


def workbook():
    return {
        "version": "Notebook/1.0",
        "items": [{"type": 3, "content": {
            "queryType": "advancedHunting", "query": "EmailEvents | take 1",
        }}],
        "xdrMetadata": {
            "contentId": str(uuid4()), "instanceId": str(uuid4()), "version": "3.2.0",
            "schemaVersion": "1.0.0", "displayName": "Published fixture",
        },
        "contentProvenance": {
            "format": "public-workbook-v1", "origin": "native-xdr",
            "requiredWorkloads": [{"workload": "mdo", "dataTypes": ["EmailEvents"]}],
            "requiredDataConnectors": [], "requiredWorkspaceFunctions": [],
        },
    }


@pytest.fixture
def published(request):
    # Keep all test writes isolated, including Git fixture commits.
    repo = Path.cwd() / (".workbook-maintenance-test-" + str(uuid4()))
    root = repo / "Solutions" / "Sample"
    for directory in ("Data", "XDR Workbooks", "Data Connectors", "Parsers"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    data = root / "Data" / "Solution_Sample.json"
    path = root / "XDR Workbooks" / "published.json"
    write(data, {"Name": "Sample", "XDR Workbooks": ["XDR Workbooks/published.json"]})
    write(path, workbook())
    write(root / "Data Connectors" / "connector.json", {"id": "same-id", "implementation": 1})
    (root / "Parsers" / "parser.kql").write_text("EmailEvents | take 1\n", encoding="utf-8")
    (repo / ".gitignore").write_text("Logs/\n", encoding="utf-8")
    git(repo, "init", "--quiet")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "remote", "add", "origin", REMOTE)
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Published workbook fixture")
    commit = git(repo, "rev-parse", "HEAD")

    def cleanup():
        for item in (repo / ".git").rglob("*"):
            if item.is_file():
                item.chmod(0o700)
        shutil.rmtree(repo)

    request.addfinalizer(cleanup)
    return root, path, data, commit


def plan(case):
    root, _, _, commit = case
    return maintenance.plan_maintenance(root, public_ref=commit, repository_url=REMOTE)


def approved(case):
    result = plan(case)
    result.update(actor="fixture reviewer", reference="explicit published repository approval",
                  decision="accept")
    return result


def test_fresh_checkout_reuse_requires_explicit_review_and_writes_nothing(published):
    root, path, _, commit = published
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert publication.publication_errors(root, json.loads(path.read_bytes()))
    first = plan(published)
    assert first == plan(published)
    assert first["repository"] == REMOTE and first["commit"] == commit
    assert first["workbooks"][0]["acceptance"] == "published-baseline"
    assert first["actor"] == first["reference"] == "" and first["decision"] is None
    with pytest.raises(ValueError, match="explicit"):
        maintenance.validate_maintenance(root, first)
    review = approved(published)
    record = maintenance.review_maintenance(root, review)
    assert record == review and record is not review
    assert record["workbooks"] is not review["workbooks"]
    assert maintenance.validate_maintenance(root, record) is None
    assert not (root / "Logs").exists()
    assert before == {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert publication.publication_errors(root, json.loads(path.read_bytes()))


@pytest.mark.parametrize("ref", ["HEAD", "main", "HEAD~1", "a" * 39, "0" * 40])
def test_reject_symbolic_and_unavailable_baselines(published, ref):
    with pytest.raises(ValueError, match="commit|baseline"):
        maintenance.plan_maintenance(published[0], public_ref=ref, repository_url=REMOTE)


def test_remote_mismatch_and_removed_source_fail(published):
    root, _, _, commit = published
    with pytest.raises(ValueError, match="remote"):
        maintenance.plan_maintenance(root, public_ref=commit, repository_url=REMOTE + "/other")
    review = approved(published)
    git(root, "remote", "remove", "origin")
    with pytest.raises(ValueError, match="remote"):
        maintenance.validate_maintenance(root, review)


@pytest.mark.parametrize("remote", [
    "https://token@example.invalid/org/repo.git",
    "https://user:password@example.invalid/org/repo.git",
    "https://example.invalid/org/repo.git?token=private-token",
    "https://example.invalid/org/repo.git#private-token",
    "https://example.invalid/org/repo.git?",
    "https://example.invalid/org/repo.git#",
    "https://example.invalid/org/repo.git%3Ftoken=private-token",
    "https://example.invalid/org/repo.git%23private-token",
    "ssh://git:password@example.invalid/org/repo.git",
    "ssh://git%3Apassword@example.invalid/org/repo.git",
    "git:password@example.invalid:org/repo.git",
    "git@example.invalid:org/repo.git?token=private-token",
    "git@example.invalid:org/repo.git#private-token",
    "https://example.invalid/org/repo.git\nprivate-token",
    "https://example.invalid/org/repo.git%0aprivate-token",
])
def test_secret_bearing_remote_shapes_fail_before_git_and_do_not_echo_input(remote, monkeypatch):
    def unexpected_git(*args, **kwargs):
        pytest.fail("Secret-bearing repository URLs must be rejected before Git inspection")

    monkeypatch.setattr(maintenance, "_git", unexpected_git)
    with pytest.raises(ValueError, match="credential-free") as error:
        maintenance.plan_maintenance(".", public_ref="a" * 40, repository_url=remote)
    assert remote not in str(error.value)
    assert "private-token" not in str(error.value)


@pytest.mark.parametrize("remote", [
    REMOTE,
    "https://example.invalid:8443/org/repo.git",
    "https://dev.azure.com/org/My%20Project/_git/repo",
    "ssh://git@example.invalid/org/repo.git",
    "ssh://git@example.invalid:2222/org/repo.git",
    "ssh://reviewer@example.invalid/org/repo.git",
    "git@example.invalid:org/repo.git",
    "git@ssh.dev.azure.com:v3/org/project/repo",
    "example.invalid:org/repo.git",
])
def test_reportable_https_and_ssh_remotes_preserve_explicit_identity(published, remote):
    root, _, _, commit = published
    git(root, "remote", "set-url", "origin", remote)
    review = maintenance.plan_maintenance(root, public_ref=commit, repository_url=remote)
    assert review["repository"] == remote
    review.update(actor="fixture reviewer", reference="explicit policy-level baseline trust",
                  decision="accept")
    maintenance.validate_maintenance(root, review)


@pytest.mark.parametrize("field,value", [
    ("actor", ""), ("reference", " "), ("decision", None), ("decision", "reject"),
    ("actor", 3), ("reference", []),
])
def test_non_authorization_is_rejected(published, field, value):
    review = approved(published)
    review[field] = value
    with pytest.raises(ValueError, match="explicit"):
        maintenance.review_maintenance(published[0], review)


@pytest.mark.parametrize("mutation", ["hash", "document", "raw", "acceptance", "extra", "missing"])
def test_plan_tampering_rejected(published, mutation):
    review = approved(published)
    if mutation == "hash":
        review["planSha256"] = "0" * 64
    elif mutation == "extra":
        review["trusted"] = True
    elif mutation == "missing":
        review.pop("dependencies")
    else:
        key = {"document": "documentSha256", "raw": "fileSha256",
               "acceptance": "acceptance"}[mutation]
        review["workbooks"][0][key] = "tampered"
        review["planSha256"] = publication.digest({
            key: value for key, value in review.items()
            if key not in {"actor", "reference", "decision", "planSha256"}
        })
    with pytest.raises(ValueError, match="shape|stale|tampered"):
        maintenance.validate_maintenance(published[0], review)


def test_edited_workbook_without_receipt_needs_local_review(published):
    root, path, _, _ = published
    review = approved(published)
    document = json.loads(path.read_bytes())
    document["items"][0]["content"]["query"] += " | take 2"
    write(path, document)
    with pytest.raises(ValueError, match="local authoring review required"):
        plan(published)
    with pytest.raises(ValueError, match="local authoring review required"):
        maintenance.validate_maintenance(root, review)


@pytest.mark.parametrize("relative", [
    "Parsers/parser.kql", "Data Connectors/connector.json", "Parsers/untracked.txt",
    "Data Connectors/untracked.py",
])
def test_dependency_implementation_and_untracked_drift_requires_review(published, relative):
    root, _, _, _ = published
    review = approved(published)
    target = root / relative
    if target.suffix == ".json":
        write(target, {"id": "same-id", "implementation": 2})
    else:
        target.write_text("implementation changed", encoding="utf-8")
    with pytest.raises(ValueError, match="dependency inventory changed"):
        maintenance.validate_maintenance(root, review)


def test_dependency_deletion_requires_review(published):
    review = approved(published)
    (published[0] / "Parsers" / "parser.kql").unlink()
    with pytest.raises(ValueError, match="dependency inventory changed"):
        maintenance.validate_maintenance(published[0], review)


def test_selection_drift_is_rejected(published):
    root, _, data, _ = published
    review = approved(published)
    write(data, {"Name": "Sample", "XDR Workbooks": []})
    with pytest.raises(ValueError, match="stale"):
        maintenance.validate_maintenance(root, review)
    write(data, {"Name": "Sample"})
    with pytest.raises(ValueError, match="explicit"):
        plan(published)


def test_two_distinct_published_workbooks_and_duplicate_identity(published):
    root, path, data, _ = published
    second = path.with_name("second.json")
    write(second, workbook())
    write(data, {"Name": "Sample", "XDR Workbooks": [
        "XDR Workbooks/second.json", "XDR Workbooks/published.json",
    ]})
    git(root, "add", ".")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Second workbook fixture")
    case = (root, path, data, git(root, "rev-parse", "HEAD"))
    review = approved(case)
    assert [row["path"] for row in review["workbooks"]] == [
        "XDR Workbooks/second.json", "XDR Workbooks/published.json",
    ]
    assert all(row["acceptance"] == "published-baseline" for row in review["workbooks"])
    maintenance.validate_maintenance(root, review)
    write(second, json.loads(path.read_bytes()))
    with pytest.raises(ValueError, match="Duplicate authored workbook identity"):
        plan(case)


def test_whitespace_baseline_comparison_but_exact_review_byte_freeze(published):
    root, path, _, _ = published
    path.write_text(json.dumps(json.loads(path.read_bytes()), indent=2), encoding="utf-8")
    review = approved(published)
    assert review["workbooks"][0]["acceptance"] == "published-baseline"
    with path.open("a", encoding="utf-8") as output:
        output.write("\n")
    with pytest.raises(ValueError, match="stale"):
        maintenance.validate_maintenance(root, review)


def test_legacy_requires_cleanup_and_invalid_public_dependencies_fail(published):
    _, path, _, _ = published
    document = json.loads(path.read_bytes())
    legacy = deepcopy(document)
    legacy["contentProvenance"].pop("format")
    write(path, legacy)
    with pytest.raises(ValueError, match="workbook-publication-plan/clean"):
        plan(published)
    document["contentProvenance"]["requiredWorkloads"] = []
    write(path, document)
    with pytest.raises(ValueError, match="dependencies"):
        plan(published)


def test_workbook_and_dependency_symlinks_rejected(published):
    root, path, _, _ = published
    link = root / "Parsers" / "linked.kql"
    try:
        link.symlink_to(path)
    except OSError:
        pytest.skip("Symlinks unavailable for this test account")
    with pytest.raises(ValueError, match="[Ss]ymlink"):
        plan(published)


def test_operational_artifacts_are_not_dependency_inputs(published):
    root, _, _, _ = published
    review = approved(published)
    logs = root / "Parsers" / "Logs"
    logs.mkdir()
    (logs / "receipt.json").write_text("private evidence", encoding="utf-8")
    maintenance.validate_maintenance(root, review)


@pytest.mark.parametrize("change", ["workbook", "dependency", "new"])
def test_local_review_requires_real_private_receipt_and_rechecks_it(published, change):
    root, path, data, _ = published
    if change == "dependency":
        (root / "Parsers" / "parser.kql").write_text("EmailEvents | take 2\n", encoding="utf-8")
    elif change == "new":
        path = path.with_name("new.json")
        write(path, workbook())
        write(data, {"Name": "Sample", "XDR Workbooks": ["XDR Workbooks/new.json"]})
    else:
        document = json.loads(path.read_bytes())
        document["items"][0]["content"]["query"] += " | take 3"
        write(path, document)
    with pytest.raises(ValueError, match="local authoring review required"):
        plan(published)
    content = path.relative_to(root).as_posix()
    cleanup = publication.plan_publication(root, content)
    cleanup.update(actor="local content reviewer", reference="explicit local content review",
                   decision="accept")
    result = publication.clean_publication(root, content, cleanup["inputSha256"], cleanup)
    review = approved(published)
    assert review["workbooks"][0]["acceptance"] == "local-review"
    maintenance.validate_maintenance(root, review)
    serialized = json.dumps(review)
    for private in ("inputArtifact", "local content reviewer", "explicit local content review"):
        assert private not in serialized
    Path(result["localReceipt"]).unlink()
    with pytest.raises(ValueError, match="local authoring review required"):
        maintenance.validate_maintenance(root, review)


def test_full_tag_object_sha_is_not_an_immutable_commit(published):
    root, _, _, _ = published
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "tag", "-a", "published-tag", "-m", "Fixture tag")
    tag = git(root, "rev-parse", "published-tag")
    with pytest.raises(ValueError, match="exact commit"):
        maintenance.plan_maintenance(root, public_ref=tag, repository_url=REMOTE)


def test_baseline_symlink_rejected_without_platform_symlink_privilege(published):
    root, _, _, _ = published
    blob = subprocess.run(
        ["git", "-C", str(root), "hash-object", "-w", "--stdin"],
        input=b"../XDR Workbooks/published.json", capture_output=True, check=True,
    ).stdout.decode().strip()
    git(root, "update-index", "--add", "--cacheinfo",
        f"120000,{blob},Solutions/Sample/Parsers/linked.kql")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Unsafe baseline fixture")
    with pytest.raises(ValueError, match="Unsafe symlink"):
        maintenance.plan_maintenance(root, public_ref=git(root, "rev-parse", "HEAD"),
                                     repository_url=REMOTE)


def test_solution_path_binding_prevents_cross_solution_replay(published):
    root, _, _, _ = published
    review = approved(published)
    review["solutionPath"] = "Solutions/Different"
    review["planSha256"] = publication.digest({
        key: value for key, value in review.items()
        if key not in {"actor", "reference", "decision", "planSha256"}
    })
    with pytest.raises(ValueError, match="stale"):
        maintenance.validate_maintenance(root, review)
