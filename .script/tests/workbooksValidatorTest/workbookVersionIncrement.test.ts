import { expect } from "chai";
import { spawnSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const baseSha = "a".repeat(40);
const headSha = "b".repeat(40);
const metadataPath = "Workbooks/WorkbooksMetadata.json";

function entry(workbookKey: string, version: string, templateRelativePath = `${workbookKey}.json`) {
  return {
    workbookKey, version, templateRelativePath,
    logoFileName: "", description: "Nested } and ], { text",
    dataTypesDependencies: ["CommonSecurityLog"], dataConnectorsDependencies: [],
    previewImagesFileNames: ["TestPreviewImages/Image1White.png", "TestPreviewImages/Image1Black.png"],
    title: workbookKey, subtitle: "", provider: "Microsoft",
    source: { kind: "Solution", name: "SOC Handbook" },
    categories: { domains: ["Security"] },
  };
}

interface Scenario {
  base?: string;
  head?: string;
  changed?: string[];
  missingCommit?: boolean;
  fetchError?: boolean;
  showError?: boolean;
  noPr?: boolean;
  invalidSha?: boolean;
  publicMetadata?: boolean;
  realRepository?: string;
  baseSha?: string;
  headSha?: string;
}

const runner = `
  import { mock } from "node:test";
  import { pathToFileURL } from "node:url";
  import path from "node:path";
  import fs from "node:fs";
  import os from "node:os";
  const config = JSON.parse(process.env.WORKBOOK_VERSION_SCENARIO);
  const root = process.cwd();
  const url = relative => pathToFileURL(path.resolve(root, relative)).href;
  const calls = [];
  const pr = {
    base: { sha: config.baseSha, ref: "mutable-base", repo: { clone_url: "base-repository" } },
    head: { sha: config.invalidSha ? undefined : config.headSha, ref: "mutable-head", repo: { clone_url: "head-repository" } }
  };
  mock.module(url(".script/utils/gitHubWrapper.js"), { namedExports: {
    GetPRDetails: async () => config.noPr ? undefined : pr,
    GetDiffFiles: async (kinds, suffixes, prefixes) => {
      calls.push(["changedFiles", kinds, suffixes, prefixes]);
      return config.changed;
    }
  } });
  if (!config.realRepository) {
    mock.module("simple-git", { defaultExport: () => ({
      catFile: async args => {
        calls.push(["catFile", args]);
        if (config.missingCommit) throw new Error("commit missing");
      },
      fetch: async args => {
        calls.push(["fetch", args]);
        if (config.fetchError) throw new Error("fetch denied");
      },
      show: async args => {
        calls.push(["show", args]);
        if (config.showError) throw new Error("snapshot unreadable");
        return args[0].startsWith(config.baseSha + ":") ? config.base : config.head;
      }
    }) });
  } else {
    process.chdir(config.realRepository);
  }
  let temporary;
  try {
    let result;
    if (config.publicMetadata) {
      // Suppress only the CLI autorun; invoke the complete exported validator below.
      mock.module(url(".script/utils/changedFilesValidator.js"), {
        namedExports: { runCheckOverChangedFiles: () => {} }
      });
      temporary = fs.mkdtempSync(path.join(os.tmpdir(), "workbook-metadata-"));
      const file = path.join(temporary, "metadata.json");
      fs.writeFileSync(file, config.head);
      const { IsValidWorkbookMetadata } = await import(url(".script/workbooksMetadataValidator.js"));
      result = await IsValidWorkbookMetadata(file);
    } else {
      const { isVersionIncrementedOnModification } = await import(url(".script/utils/workbookCheckers/isVersionIncrementedOnModification.js"));
      result = await isVersionIncrementedOnModification();
    }
    console.log(JSON.stringify({ result, calls }));
  } catch (error) {
    console.log(JSON.stringify({ error: error.message, name: error.name, calls }));
  } finally {
    if (temporary) fs.rmSync(temporary, { recursive: true });
  }
`;

function validate(scenario: Scenario = {}) {
  const result = spawnSync(process.execPath, ["--experimental-test-module-mocks", "--input-type=module", "--eval", runner], {
    cwd: repoRoot,
    encoding: "utf8",
    env: { ...process.env, WORKBOOK_VERSION_SCENARIO: JSON.stringify({
      base: JSON.stringify([entry("AzureSentinelCost", "1.5.1"), entry("ADXvsLA", "1.0.0")]),
      head: JSON.stringify([entry("AzureSentinelCost", "1.6.4"), entry("ADXvsLA", "1.0.0")]),
      changed: ["Workbooks/AzureSentinelCost.json", metadataPath],
      baseSha, headSha, ...scenario,
    }) },
  });
  expect(result.error, result.stderr).to.equal(undefined);
  expect(result.status, result.stderr).to.equal(0);
  return JSON.parse(result.stdout.trim().split(/\r?\n/).pop()!) as {
    result?: number; error?: string; name?: string; calls: [string, string[]][];
  };
}

function fails(scenario: Scenario, message: string) {
  const result = validate(scenario);
  expect(result.name).to.equal("WorkbookValidationError");
  expect(result.error).to.contain(message);
}

describe("workbook version increment public validator", () => {
  it("accepts the Cost bump without assigning it to the following unchanged ADX entry", () => {
    expect(validate().result).to.equal(0);
    fails({ changed: ["Workbooks/ADXvsLA.json"] }, "workbook ADXvsLA.json");
  });

  it("accepts the reported 1.5.1 -> 1.6.2 regression through the complete metadata validator", () => {
    const result = validate({
      head: JSON.stringify([entry("AzureSentinelCost", "1.6.2"), entry("ADXvsLA", "1.0.0")]),
      publicMetadata: true,
    });
    expect(result.result, result.error).to.equal(0);
  });

  it("propagates a version failure through the complete metadata validator", () => {
    fails({
      head: JSON.stringify([entry("AzureSentinelCost", "1.5.1"), entry("ADXvsLA", "1.0.0")]),
      publicMetadata: true,
    }, "must be greater");
  });

  for (const indentation of [undefined, 2, 4]) {
    for (const newline of ["\n", "\r\n"]) {
      it(`ignores formatting, reordered fields, nested arrays/objects and braces in strings (${indentation}, ${JSON.stringify(newline)})`, () => {
        const head = [entry("AzureSentinelCost", "1.6.4"), entry("ADXvsLA", "1.0.0")]
          .map(item => Object.fromEntries(Object.entries(item).reverse()));
        expect(validate({ head: JSON.stringify(head, null, indentation).replace(/\n/g, newline) }).result).to.equal(0);
      });
    }
  }

  it("uses only exact PR SHAs for snapshot reads, even when branches already exist", () => {
    const result = validate({ missingCommit: true });
    expect(result.result).to.equal(0);
    expect(result.calls.filter(([name]) => name === "show")).to.deep.equal([
      ["show", [`${baseSha}:${metadataPath}`]], ["show", [`${headSha}:${metadataPath}`]],
    ]);
    expect(result.calls.filter(([name]) => name === "fetch")).to.deep.equal([
      ["fetch", ["--no-tags", "--no-recurse-submodules", "--depth=1", "base-repository", baseSha]],
      ["fetch", ["--no-tags", "--no-recurse-submodules", "--depth=1", "head-repository", headSha]],
    ]);
  });

  for (const version of ["1.5.1", "1.4.9", "1.5.1.0"]) {
    it(`rejects unchanged, decreased, or equivalent version ${version}`, () => {
      fails({ head: JSON.stringify([entry("AzureSentinelCost", version)]) }, "must be greater");
    });
  }

  for (const version of [undefined, "", "1.x.2", "1.2.3-beta", "1.2.3+build", " 1.6.4"]) {
    it(`rejects missing or ambiguous version ${version}`, () => {
      fails({ head: JSON.stringify([{ ...entry("AzureSentinelCost", "1.0"), version }]) }, "Missing or invalid");
    });
  }

  for (const [oldVersion, newVersion, passes] of [
    ["1.9.9", "1.10.0", true], ["1.10.0", "1.9.9", false],
    ["1.0", "1.1", true], ["1.0", "1.0.1", true],
    ["2.0.0", "10.0.0", true], ["1.9007199254740993", "1.9007199254740992", false],
  ] as const) {
    it(`orders numeric dotted versions ${oldVersion} -> ${newVersion}`, () => {
      const result = validate({
        base: JSON.stringify([entry("AzureSentinelCost", oldVersion)]),
        head: JSON.stringify([entry("AzureSentinelCost", newVersion)]),
      });
      if (passes) expect(result.result).to.equal(0);
      else expect(result.error).to.contain("must be greater");
    });
  }

  it("requires independent bumps for multiple modified workbooks", () => {
    const scenario = {
      changed: ["Workbooks/AzureSentinelCost.json", "Workbooks/ADXvsLA.json"],
      head: JSON.stringify([entry("AzureSentinelCost", "1.6.4"), entry("ADXvsLA", "1.0.1")]),
    };
    expect(validate(scenario).result).to.equal(0);
    fails({ ...scenario, head: JSON.stringify([entry("AzureSentinelCost", "1.6.4"), entry("ADXvsLA", "1.0.0")]) }, "ADXvsLA");
  });

  it("ignores unmapped auxiliary JSON alongside a correctly bumped gallery template", () => {
    const changed = [
      "Workbooks/use cases mapper workbook/deployment.json",
      "Workbooks/AzureSentinelCost.json",
      metadataPath,
    ];
    const result = validate({ changed, publicMetadata: true });
    expect(result.result, result.error).to.equal(0);
    fails({
      changed,
      head: JSON.stringify([entry("AzureSentinelCost", "1.5.1"), entry("ADXvsLA", "1.0.0")]),
    }, "must be greater");
  });

  it("ignores an auxiliary-only change absent from both metadata snapshots", () => {
    const result = validate({ changed: ["Workbooks/use cases mapper workbook/deployment.json"] });
    expect(result.result, result.error).to.equal(0);
  });

  for (const snapshot of ["base", "head"] as const) {
    it(`rejects missing mappings in the ${snapshot} snapshot`, () => {
      fails({ [snapshot]: "[]" }, "Missing or ambiguous metadata");
    });
    it(`rejects duplicate workbook keys in the ${snapshot} snapshot`, () => {
      fails({ [snapshot]: JSON.stringify([entry("AzureSentinelCost", "1.5.1"), entry("AzureSentinelCost", "1.6.4")]) }, "Duplicate workbookKey");
    });
    it(`rejects malformed JSON in the ${snapshot} snapshot`, () => {
      fails({ [snapshot]: "[{" }, "Unable to parse");
    });
    it(`rejects a non-array ${snapshot} snapshot`, () => {
      fails({ [snapshot]: "{}" }, "Expected a metadata array");
    });
    it(`rejects invalid metadata entries in the ${snapshot} snapshot`, () => {
      fails({ [snapshot]: "[null]" }, "Missing or invalid");
    });
    it(`rejects missing versions in the ${snapshot} snapshot`, () => {
      const { version: _version, ...withoutVersion } = entry("AzureSentinelCost", "1.5.1");
      fails({ [snapshot]: JSON.stringify([withoutVersion]) }, "Missing or invalid");
    });
  }

  it("requires every shared-template entry to increase independently, regardless of order", () => {
    const first = entry("first", "1.0", "AzureSentinelCost.json");
    const second = entry("second", "2.0", "AzureSentinelCost.json");
    const base = JSON.stringify([first, second]);
    fails({ base, head: JSON.stringify([{ ...second, version: "2.1" }, first]) }, "workbookKey first");
    fails({ base, head: JSON.stringify([second, { ...first, version: "1.1" }]) }, "workbookKey second");
    expect(validate({ base, head: JSON.stringify([{ ...second, version: "2.1" }, { ...first, version: "1.1" }]) }).result).to.equal(0);
  });

  it("rejects a removed shared entry or a replacement workbook key instead of borrowing a bump", () => {
    fails({
      base: JSON.stringify([entry("first", "1.0", "AzureSentinelCost.json"), entry("second", "1.0", "AzureSentinelCost.json")]),
      head: JSON.stringify([entry("first", "1.1", "AzureSentinelCost.json")]),
    }, "Missing or ambiguous");
    fails({ head: JSON.stringify([entry("replacement", "1.6.4", "AzureSentinelCost.json")]) }, "Missing or ambiguous");
  });

  it("propagates Git read and fetch failures as validation failures", () => {
    fails({ showError: true }, "snapshot unreadable");
    fails({ missingCommit: true, fetchError: true }, "fetch denied");
    fails({ invalidSha: true }, "Missing or invalid PR commit SHA");
  });

  it("retains no-PR and no-modified-workbook behavior without Git reads", () => {
    for (const scenario of [{ noPr: true }, { changed: [] }, { changed: [metadataPath] }]) {
      const result = validate(scenario);
      expect(result.result).to.equal(0);
      expect(result.calls.filter(([name]) => name !== "changedFiles")).to.deep.equal([]);
    }
  });

  it("keeps the existing modified-only discovery contract for additions, deletions and renames", () => {
    expect(validate({ changed: [] }).calls).to.deep.equal([
      ["changedFiles", ["Modified"], [".json"], ["Workbooks/"]],
    ]);
  });

  if (process.env.WORKBOOK_VERSION_REPLAY_BASE_SHA || process.env.WORKBOOK_VERSION_REPLAY_HEAD_SHA) {
    it("replays the Cost workbook PR using explicitly supplied local commit snapshots", () => {
      const base = process.env.WORKBOOK_VERSION_REPLAY_BASE_SHA;
      const head = process.env.WORKBOOK_VERSION_REPLAY_HEAD_SHA;
      expect(base).to.match(/^[a-f0-9]{40}$/i);
      expect(head).to.match(/^[a-f0-9]{40}$/i);
      const result = validate({ realRepository: repoRoot, baseSha: base, headSha: head });
      expect(result.result, result.error).to.equal(0);
    });
  }

  it("reads actual Git snapshots, not the current worktree or mutable branch names", () => {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), "workbook-version-git-"));
    function git(...args: string[]) {
      const result = spawnSync("git", args, { cwd: directory, encoding: "utf8" });
      expect(result.status, result.stderr).to.equal(0);
      return result.stdout.trim();
    }
    try {
      git("init", "--quiet");
      git("config", "user.name", "Workbook validator test");
      git("config", "user.email", "test@example.invalid");
      git("config", "commit.gpgsign", "false");
      fs.mkdirSync(path.join(directory, "Workbooks"));
      const file = path.join(directory, "Workbooks", "WorkbooksMetadata.json");
      fs.writeFileSync(file, JSON.stringify([entry("AzureSentinelCost", "1.5.1"), entry("ADXvsLA", "1.0.0")]));
      git("add", ".");
      git("commit", "--quiet", "-m", "base");
      const base = git("rev-parse", "HEAD");
      fs.writeFileSync(file, JSON.stringify([entry("AzureSentinelCost", "1.6.4"), entry("ADXvsLA", "1.0.0")], null, 2));
      git("commit", "--quiet", "-am", "head");
      const head = git("rev-parse", "HEAD");
      fs.writeFileSync(file, "invalid uncommitted JSON");
      expect(validate({ realRepository: directory, baseSha: base, headSha: head }).result).to.equal(0);
      fails({ realRepository: directory, baseSha: base, headSha: base }, "must be greater");
    } finally {
      fs.rmSync(directory, { recursive: true });
    }
  });
});
