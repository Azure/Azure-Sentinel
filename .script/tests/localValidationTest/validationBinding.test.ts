import { spawnSync } from "child_process";
import crypto from "crypto";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { expect } from "chai";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const bindingScript = path.join(repoRoot, ".script/local-validation/validation-binding.ps1");
const runnerScript = path.join(repoRoot, ".script/local-validation/build-and-validate.ps1");
const fixtureRoot = path.join(path.dirname(fileURLToPath(import.meta.url)), `.validation-binding-${process.pid}`);
const actualContentRoot = process.env.AZURE_SENTINEL_CONTENT_ROOT
  ? path.resolve(process.env.AZURE_SENTINEL_CONTENT_ROOT)
  : undefined;
const actualSolutionNames = ["CiscoASA", "Azure Activity", "Syslog"];
const actualSolutionPaths = actualContentRoot
  ? actualSolutionNames.map(name => path.join(actualContentRoot, "Solutions", name))
  : [];
const actualSolutionsAvailable =
  actualSolutionPaths.length === actualSolutionNames.length &&
  actualSolutionPaths.every(solution => fs.existsSync(solution));
const powershellAvailable = spawnSync("pwsh", ["--version"], { encoding: "utf8" }).status === 0;

function getPythonExecutable(): string {
  for (const command of ["python3.12", "python3", "python"]) {
    const result = spawnSync(command, [
      "-c", "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)",
    ], { encoding: "utf8" });
    if (result.status === 0) {
      return command;
    }
  }
  throw new Error("Python 3.12 or newer is required for validation-binding identity tests.");
}

function sha256(value: Buffer | string): string {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function pythonJsonStringify(value: unknown): string {
  const json = JSON.stringify(value);
  if (json === undefined) {
    throw new Error("fixture value is not JSON serializable");
  }
  return json.replace(/[\u007f-\uffff]/g, character =>
    `\\u${character.charCodeAt(0).toString(16).padStart(4, "0")}`,
  );
}

function quotePowerShell(value: string): string {
  return `'${value.replace(/'/g, "''")}'`;
}

function createFixture(name: string) {
  const root = path.join(fixtureRoot, name);
  const solution = path.join(root, "content", "Solutions", "FixtureSolution");
  const evidence = path.join(root, "evidence", "run-1");
  const packageDirectory = path.join(solution, "Package");
  const reportDirectory = path.join(solution, "Logs", "sentinel-xdr-migration", "run-1");
  fs.mkdirSync(path.join(solution, "Data"), { recursive: true });
  fs.mkdirSync(path.join(solution, "Data Connectors"), { recursive: true });
  fs.mkdirSync(path.join(solution, "azure NRT"), { recursive: true });
  fs.mkdirSync(path.join(solution, "New-CloudShell"), { recursive: true });
  fs.mkdirSync(path.join(solution, "Hunting Queries"), { recursive: true });
  fs.mkdirSync(packageDirectory, { recursive: true });
  fs.mkdirSync(reportDirectory, { recursive: true });
  fs.mkdirSync(evidence, { recursive: true });
  fs.writeFileSync(path.join(solution, "Data", "source.json"), "{\"source\":true}\n", "utf8");
  fs.writeFileSync(path.join(solution, "Data", "café.json"), "{\"label\":\"é\"}\n", "utf8");
  fs.writeFileSync(
    path.join(solution, "Data Connectors", "connector.json"),
    "{\"connector\":true}\n",
    "utf8",
  );
  fs.writeFileSync(path.join(solution, "azure NRT", "azure.json"), "{\"azure\":true}\n", "utf8");
  fs.writeFileSync(
    path.join(solution, "New-CloudShell", "shell.json"),
    "{\"shell\":true}\n",
    "utf8",
  );

  const artifacts = {
    mainTemplate: ["Package/mainTemplate.json", "{\"resources\":[]}\n"],
    createUiDefinition: ["Package/createUiDefinition.json", "{\"createUiDefinition\":{}}\n"],
    testParameters: ["Package/testParameters.json", "{}\n"],
    zip: ["Package/3.1.1.zip", "fixture archive bytes\n"],
  } as const;
  const packageArtifactHashes: Record<string, string> = {};
  for (const [name, [relative, content]] of Object.entries(artifacts)) {
    fs.writeFileSync(path.join(solution, relative), content, "utf8");
    packageArtifactHashes[name] = sha256(content);
  }
  const sourceInputHash = sha256(pythonJsonStringify([
    {
      path: "Data/café.json",
      sha256: sha256("{\"label\":\"é\"}\n"),
    },
    {
      path: "Data/source.json",
      sha256: sha256("{\"source\":true}\n"),
    },
    {
      path: "Data Connectors/connector.json",
      sha256: sha256("{\"connector\":true}\n"),
    },
    {
      path: "New-CloudShell/shell.json",
      sha256: sha256("{\"shell\":true}\n"),
    },
    {
      path: "azure NRT/azure.json",
      sha256: sha256("{\"azure\":true}\n"),
    },
  ]));
  const packageReportPath = path.join(reportDirectory, "packaging.v3_1.json");
  fs.writeFileSync(packageReportPath, JSON.stringify({
    packager: "V3.1",
    version: "3.1.1",
    packageAttemptId: "attempt-fixture-1",
    workflowRunId: "run-1",
    packageInputs: { after: { sha256: sourceInputHash } },
    packageArtifactsSha256: "a".repeat(64),
    packageArtifactHashes,
    mainTemplate: artifacts.mainTemplate[0],
    createUiDefinition: artifacts.createUiDefinition[0],
    testParameters: artifacts.testParameters[0],
    zip: artifacts.zip[0],
  }, null, 2), "utf8");

  return { root, solution, evidence, packageReportPath };
}

function runSnapshot(
  fixture: ReturnType<typeof createFixture>,
  options: {
    mutateSource?: boolean;
    mutatePackage?: boolean;
    staleSource?: boolean;
    validationFailed?: boolean;
    windowsPackageIdentity?: boolean;
    snapshotOnly?: boolean;
  } = {},
) {
  const command = [
    `. ${quotePowerShell(bindingScript)}`,
    ...(options.windowsPackageIdentity
      ? [
        `$packageReport = Get-Content -LiteralPath ${quotePowerShell(fixture.packageReportPath)} -Raw | ConvertFrom-Json`,
        `$windowsPackageInputs = Get-ValidationFileFingerprints -Root ${quotePowerShell(fixture.solution)} -ExcludeDirectories @("package","logs","evidence",".git",".venv","__pycache__") -PathOrder Windows`,
        "$packageReport.packageInputs.after.sha256 = Get-ValidationInputFingerprintHash -Files $windowsPackageInputs",
        `[System.IO.File]::WriteAllText(${quotePowerShell(fixture.packageReportPath)}, ($packageReport | ConvertTo-Json -Depth 30))`,
      ]
      : []),
    options.staleSource
      ? `[System.IO.File]::WriteAllText(${quotePowerShell(path.join(fixture.solution, "Data", "source.json"))}, '{\"source\":stale}')`
      : "",
    `$before = Get-ValidationEvidenceSnapshot -ToolkitRoot ${quotePowerShell(repoRoot)} -ContentRoot ${quotePowerShell(path.join(fixture.root, "content"))} -SolutionPath ${quotePowerShell(fixture.solution)} -PackageReportPath ${quotePowerShell(path.relative(fixture.solution, fixture.packageReportPath))}`,
    ...(options.snapshotOnly
      ? ["$before | ConvertTo-Json -Depth 30 -Compress"]
      : [
        ...(options.mutateSource
          ? [
            `[System.IO.File]::WriteAllText(${quotePowerShell(path.join(fixture.solution, "Data", "source.json"))}, '{\"source\":false}')`,
            `$packageReport = Get-Content -LiteralPath ${quotePowerShell(fixture.packageReportPath)} -Raw | ConvertFrom-Json`,
            `$packageInputs = Get-ValidationFileFingerprints -Root ${quotePowerShell(fixture.solution)} -ExcludeDirectories @("package","logs","evidence",".git",".venv","__pycache__") -PathOrder Posix`,
            "$packageReport.packageInputs.after.sha256 = Get-ValidationInputFingerprintHash -Files $packageInputs",
            `[System.IO.File]::WriteAllText(${quotePowerShell(fixture.packageReportPath)}, ($packageReport | ConvertTo-Json -Depth 30))`,
          ]
          : []),
        options.mutatePackage
          ? `[System.IO.File]::WriteAllText(${quotePowerShell(path.join(fixture.solution, "Package", "mainTemplate.json"))}, '{\"resources\":[1]}')`
          : "",
        `$after = Get-ValidationEvidenceSnapshot -ToolkitRoot ${quotePowerShell(repoRoot)} -ContentRoot ${quotePowerShell(path.join(fixture.root, "content"))} -SolutionPath ${quotePowerShell(fixture.solution)} -PackageReportPath ${quotePowerShell(path.relative(fixture.solution, fixture.packageReportPath))}`,
        `$entries = @(@{ Step = 2; Status = "${options.validationFailed ? "failed" : "passed"}" })`,
        `$binding = Complete-ValidationEvidenceBinding -Before $before -After $after -ValidationEntries $entries -PackagingSkipped $true -ValidationSkipped $false -EvidenceRunPath ${quotePowerShell(fixture.evidence)}`,
        `$receipt = Write-ValidationEvidenceBinding -EvidenceRunPath ${quotePowerShell(fixture.evidence)} -Binding $binding`,
        "[ordered]@{ binding = $binding; receipt = $receipt } | ConvertTo-Json -Depth 30 -Compress",
      ]),
  ].filter(Boolean).join("; ");
  return spawnSync("pwsh", ["-NoProfile", "-Command", command], { encoding: "utf8" });
}

describe("V3.1 validation evidence producer", () => {
  afterEach(() => {
    fs.rmSync(fixtureRoot, { recursive: true, force: true });
  });

  it("wires evidence capture, completion, and receipt reporting into the existing runner", () => {
    const runner = fs.readFileSync(runnerScript, "utf8");
    expect(runner.match(/Get-ValidationEvidenceSnapshot/g)).to.have.length(2);
    expect(runner).to.contain("Complete-ValidationEvidenceBinding");
    expect(runner).to.contain("Write-ValidationEvidenceBinding");
    expect(runner).to.contain("Validation binding SHA256:");
    expect(runner).to.contain("-PackageReportPath requires validation-only mode");
  });

  (powershellAvailable ? it : it.skip)("uses Python-compatible JSON escaping for fingerprint paths", () => {
    const value = `café"\\path.json`;
    const result = spawnSync(
      "pwsh",
      [
        "-NoProfile",
        "-Command",
        `. ${quotePowerShell(bindingScript)}; ConvertTo-ValidationJsonString -Value ${quotePowerShell(value)}`,
      ],
      { encoding: "utf8" },
    );
    expect(result.status, result.stderr).to.equal(0);
    expect(result.stdout.trim()).to.equal(pythonJsonStringify(value));
  });

  (powershellAvailable ? it : it.skip)("matches POSIX and PureWindowsPath identities for three solution trees", function () {
    this.timeout(15000);
    const identityRoot = path.join(fixtureRoot, "identity-roundtrip");
    const solutions = ["CiscoASA", "AzureFirewall", "Syslog"].map(name =>
      path.join(identityRoot, name),
    );
    for (const [index, solution] of solutions.entries()) {
      fs.mkdirSync(path.join(solution, "Data"), { recursive: true });
      fs.mkdirSync(path.join(solution, "Data Connectors"), { recursive: true });
      fs.mkdirSync(path.join(solution, "Analytic Rules"), { recursive: true });
      fs.mkdirSync(path.join(solution, "azure NRT"), { recursive: true });
      fs.mkdirSync(path.join(solution, "New-CloudShell"), { recursive: true });
      fs.mkdirSync(path.join(solution, "Hunting Queries"), { recursive: true });
      fs.writeFileSync(
        path.join(solution, "Data", `Solution_${index}.json`),
        JSON.stringify({ solution: index }),
        "utf8",
      );
      fs.writeFileSync(
        path.join(solution, "Data Connectors", `connector_${index}.json`),
        JSON.stringify({ connector: index }),
        "utf8",
      );
      fs.writeFileSync(
        path.join(solution, "Analytic Rules", `rule_${index}.yaml`),
        `id: rule-${index}\n`,
        "utf8",
      );
      fs.writeFileSync(
        path.join(solution, "azure NRT", `azure_${index}.json`),
        JSON.stringify({ azure: index }),
        "utf8",
      );
      fs.writeFileSync(
        path.join(solution, "New-CloudShell", `shell_${index}.json`),
        JSON.stringify({ shell: index }),
        "utf8",
      );
      fs.writeFileSync(
        path.join(solution, "Hunting Queries", "AnomalousAzureOperationModel.yaml"),
        "id: anomalous-azure\n",
        "utf8",
      );
      fs.writeFileSync(
        path.join(solution, "Hunting Queries", "Anomalous_Listing_Of_Storage_Keys.yaml"),
        "id: anomalous-storage\n",
        "utf8",
      );
    }

    const python = spawnSync(
      getPythonExecutable(),
      [
        "-c",
        [
          "import hashlib,json,os,sys",
          "from pathlib import Path,PurePosixPath,PureWindowsPath",
          "from sentinel_xdr_migration.packaging import package_input_identity",
          "excluded={'package','logs','evidence','.git','.venv','__pycache__'}",
          "def identity(root,path_type):",
          "    root=Path(root)",
          "    files=[{'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in root.rglob('*') if p.is_file() and not any(part.lower() in excluded or part.lower()=='.env' or part.lower().startswith('.env.') for part in p.relative_to(root).parts)]",
          "    files.sort(key=lambda item:path_type(item['path']))",
          "    return hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()",
          "roots=sys.argv[1:]",
          "punctuation_order=sorted(['AnomalousAzureOperationModel.yaml','Anomalous_Listing_Of_Storage_Keys.yaml'],key=PureWindowsPath)",
          "print(json.dumps({'posix':[identity(root,PurePosixPath) for root in roots],'windows':[identity(root,PureWindowsPath) for root in roots],'native':[package_input_identity(root)['sha256'] for root in roots],'nativeSemantics':'windows' if os.name=='nt' else 'posix','punctuationOrder':punctuation_order}))",
        ].join("\n"),
        ...solutions,
      ],
      {
        cwd: repoRoot,
        env: {
          ...process.env,
          PYTHONPATH: path.join(repoRoot, "Tools/SentinelToXDRMigration"),
        },
        encoding: "utf8",
      },
    );
    expect(python.status, python.stderr).to.equal(0);
    const powershell = [
      `. ${quotePowerShell(bindingScript)}`,
    "$posixHashes = [System.Collections.Generic.List[string]]::new()",
    "$windowsHashes = [System.Collections.Generic.List[string]]::new()",
    `foreach ($root in @(${solutions.map(quotePowerShell).join(",")})) {`,
    `  $posixFiles = Get-ValidationFileFingerprints -Root $root -ExcludeDirectories @("package","logs","evidence",".git",".venv","__pycache__") -PathOrder Posix`,
    `  $windowsFiles = Get-ValidationFileFingerprints -Root $root -ExcludeDirectories @("package","logs","evidence",".git",".venv","__pycache__") -PathOrder Windows`,
    "  $posixHashes.Add((Get-ValidationInputFingerprintHash -Files $posixFiles))",
    "  $windowsHashes.Add((Get-ValidationInputFingerprintHash -Files $windowsFiles))",
    "}",
    "[ordered]@{ posix = $posixHashes.ToArray(); windows = $windowsHashes.ToArray() } | ConvertTo-Json -Depth 10 -Compress",
    ].join("; ");
    const result = spawnSync("pwsh", ["-NoProfile", "-Command", powershell], {
      encoding: "utf8",
    });
    expect(result.status, result.stderr).to.equal(0);
    const expected = JSON.parse(python.stdout);
    const actual = JSON.parse(result.stdout);
    expect(actual.posix).to.deep.equal(expected.posix);
    expect(actual.windows).to.deep.equal(expected.windows);
    expect(expected.native).to.deep.equal(
      expected[expected.nativeSemantics as "posix" | "windows"],
    );
    expect(expected.punctuationOrder).to.deep.equal([
      "Anomalous_Listing_Of_Storage_Keys.yaml",
      "AnomalousAzureOperationModel.yaml",
    ]);
    for (let index = 0; index < expected.posix.length; index++) {
      expect(expected.windows[index]).to.not.equal(expected.posix[index]);
    }
  });

  (powershellAvailable && actualSolutionsAvailable ? it : it.skip)(
    "matches Python Path identities for read-only actual CiscoASA, Azure Activity, and Syslog trees",
    function () {
      this.timeout(30000);
      const python = spawnSync(
        getPythonExecutable(),
        [
          "-c",
          [
            "import hashlib,json,os,sys",
            "from pathlib import Path,PurePosixPath,PureWindowsPath",
            "from sentinel_xdr_migration.packaging import package_input_identity",
            "excluded={'package','logs','evidence','.git','.venv','__pycache__'}",
            "def identity(root,path_type):",
            "    root=Path(root)",
            "    files=[]",
            "    for p in root.rglob('*'):",
            "        relative=p.relative_to(root)",
            "        parts=relative.parts",
            "        if any(part.lower() in excluded or part.lower()=='.env' or part.lower().startswith('.env.') for part in parts): continue",
            "        if p.is_symlink(): raise ValueError(f'unsafe symlink: {relative}')",
            "        if p.is_file(): files.append({'path':relative.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})",
            "    files.sort(key=lambda item:path_type(item['path']))",
            "    return hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()",
            "roots=sys.argv[1:]",
            "print(json.dumps({'posix':[identity(root,PurePosixPath) for root in roots],'windows':[identity(root,PureWindowsPath) for root in roots],'native':[package_input_identity(root)['sha256'] for root in roots],'nativeSemantics':'windows' if os.name=='nt' else 'posix'}))",
          ].join("\n"),
          ...actualSolutionPaths,
        ],
        {
          cwd: repoRoot,
          env: {
            ...process.env,
            PYTHONPATH: path.join(repoRoot, "Tools/SentinelToXDRMigration"),
          },
          encoding: "utf8",
        },
      );
      expect(python.status, python.stderr).to.equal(0);
      const powershell = [
        `. ${quotePowerShell(bindingScript)}`,
        "$posixHashes = [System.Collections.Generic.List[string]]::new()",
        "$windowsHashes = [System.Collections.Generic.List[string]]::new()",
        `foreach ($root in @(${actualSolutionPaths.map(quotePowerShell).join(",")})) {`,
        `  $posixFiles = Get-ValidationFileFingerprints -Root $root -ExcludeDirectories @("package","logs","evidence",".git",".venv","__pycache__") -PathOrder Posix`,
        `  $windowsFiles = Get-ValidationFileFingerprints -Root $root -ExcludeDirectories @("package","logs","evidence",".git",".venv","__pycache__") -PathOrder Windows`,
        "  $posixHashes.Add((Get-ValidationInputFingerprintHash -Files $posixFiles))",
        "  $windowsHashes.Add((Get-ValidationInputFingerprintHash -Files $windowsFiles))",
        "}",
        "[ordered]@{ posix = $posixHashes.ToArray(); windows = $windowsHashes.ToArray() } | ConvertTo-Json -Depth 10 -Compress",
      ].join("; ");
      const result = spawnSync("pwsh", ["-NoProfile", "-Command", powershell], {
        encoding: "utf8",
      });
      expect(result.status, result.stderr).to.equal(0);
      const expected = JSON.parse(python.stdout);
      const actual = JSON.parse(result.stdout);
      expect(actual.posix).to.deep.equal(expected.posix);
      expect(actual.windows).to.deep.equal(expected.windows);
      expect(expected.native).to.deep.equal(
        expected[expected.nativeSemantics as "posix" | "windows"],
      );
      for (let index = 0; index < expected.posix.length; index++) {
        expect(expected.windows[index]).to.not.equal(expected.posix[index]);
      }
    },
  );

  (powershellAvailable && actualSolutionsAvailable ? it : it.skip)(
    "round-trips an actual Azure Activity package snapshot and rejects stale copied inputs",
    function () {
      this.timeout(30000);
      const solution = actualSolutionPaths[1];
      const copiedSolution = path.join(
        fixtureRoot,
        "actual-snapshot",
        "Solutions",
        "Azure Activity",
      );
      const copy = spawnSync(
        getPythonExecutable(),
        [
          "-c",
          [
            "import hashlib,json,shutil,sys",
            "from pathlib import Path,PureWindowsPath",
            "from sentinel_xdr_migration.packaging import package_input_identity",
            "excluded={'package','logs','evidence','.git','.venv','__pycache__'}",
            "def ignore(directory,names): return [name for name in names if name.lower() in excluded or name.lower()=='.env' or name.lower().startswith('.env.')]",
            "source=Path(sys.argv[1]); destination=Path(sys.argv[2])",
            "source_identity=package_input_identity(source)",
            "shutil.copytree(source,destination,ignore=ignore)",
            "copied_identity=package_input_identity(destination)",
            "if source_identity['sha256'] != copied_identity['sha256']: raise ValueError('read-only content copy changed the V3.1 input identity')",
            "files=[]",
            "for p in destination.rglob('*'):",
            "    relative=p.relative_to(destination); parts=relative.parts",
            "    if any(part.lower() in excluded or part.lower()=='.env' or part.lower().startswith('.env.') for part in parts): continue",
            "    if p.is_symlink(): raise ValueError(f'unsafe symlink: {relative}')",
            "    if p.is_file(): files.append({'path':relative.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})",
            "files.sort(key=lambda item:PureWindowsPath(item['path']))",
            "windows_hash=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()",
            "print(json.dumps({'sourceInputSha256':source_identity['sha256'],'copyInputSha256':copied_identity['sha256'],'windowsInputSha256':windows_hash}))",
          ].join("\n"),
          solution,
          copiedSolution,
        ],
        {
          cwd: repoRoot,
          env: {
            ...process.env,
            PYTHONPATH: path.join(repoRoot, "Tools/SentinelToXDRMigration"),
          },
          encoding: "utf8",
        },
      );
      expect(copy.status, copy.stderr).to.equal(0);
      const identities = JSON.parse(copy.stdout);
      expect(identities.copyInputSha256).to.equal(identities.sourceInputSha256);

      const packageDirectory = path.join(copiedSolution, "Package");
      const reportDirectory = path.join(
        copiedSolution,
        "Logs",
        "sentinel-xdr-migration",
        "roundtrip",
      );
      fs.mkdirSync(packageDirectory, { recursive: true });
      fs.mkdirSync(reportDirectory, { recursive: true });
      const artifacts = {
        mainTemplate: ["Package/mainTemplate.json", "{\"resources\":[]}\n"],
        createUiDefinition: ["Package/createUiDefinition.json", "{\"createUiDefinition\":{}}\n"],
        testParameters: ["Package/testParameters.json", "{}\n"],
        zip: ["Package/3.1.1.zip", "fixture archive bytes\n"],
      } as const;
      const packageArtifactHashes: Record<string, string> = {};
      for (const [name, [relative, content]] of Object.entries(artifacts)) {
        fs.writeFileSync(path.join(copiedSolution, relative), content, "utf8");
        packageArtifactHashes[name] = sha256(content);
      }
      const packageReportRelativePath =
        "Logs/sentinel-xdr-migration/roundtrip/packaging.v3_1.json";
      fs.writeFileSync(
        path.join(copiedSolution, packageReportRelativePath),
        JSON.stringify({
          packager: "V3.1",
          version: "3.1.1",
          packageAttemptId: "actual-azure-activity-snapshot",
          workflowRunId: "actual-tree-roundtrip",
          packageInputs: { after: { sha256: identities.windowsInputSha256 } },
          packageArtifactsSha256: sha256(JSON.stringify(packageArtifactHashes)),
          packageArtifactHashes,
          mainTemplate: artifacts.mainTemplate[0],
          createUiDefinition: artifacts.createUiDefinition[0],
          testParameters: artifacts.testParameters[0],
          zip: artifacts.zip[0],
        }, null, 2),
        "utf8",
      );
      const contentRoot = path.join(fixtureRoot, "actual-snapshot");
      const staleSource = path.join(
        copiedSolution,
        "Hunting Queries",
        "AnomalousAzureOperationModel.yaml",
      );
      const command = [
        `. ${quotePowerShell(bindingScript)}`,
        `$windowsFiles = Get-ValidationFileFingerprints -Root ${quotePowerShell(copiedSolution)} -ExcludeDirectories @("package","logs","evidence",".git",".venv","__pycache__") -PathOrder Windows`,
        `$windowsHash = Get-ValidationInputFingerprintHash -Files $windowsFiles`,
        `if ($windowsHash -ne ${quotePowerShell(identities.windowsInputSha256)}) { throw "actual copied-tree Windows hash mismatch: $windowsHash" }`,
        `$before = Get-ValidationEvidenceSnapshot -ToolkitRoot ${quotePowerShell(repoRoot)} -ContentRoot ${quotePowerShell(contentRoot)} -SolutionPath ${quotePowerShell(copiedSolution)} -PackageReportPath ${quotePowerShell(packageReportRelativePath)}`,
        `$after = Get-ValidationEvidenceSnapshot -ToolkitRoot ${quotePowerShell(repoRoot)} -ContentRoot ${quotePowerShell(contentRoot)} -SolutionPath ${quotePowerShell(copiedSolution)} -PackageReportPath ${quotePowerShell(packageReportRelativePath)}`,
        "$entries = @(@{ Step = 2; Status = 'passed' })",
        `$binding = Complete-ValidationEvidenceBinding -Before $before -After $after -ValidationEntries $entries -PackagingSkipped $true -ValidationSkipped $false -EvidenceRunPath ${quotePowerShell(path.join(fixtureRoot, "actual-snapshot-evidence"))}`,
        "if ($binding.validationResult -ne 'PASSED' -or $before.sourcePathSemantics -ne 'windows') { throw 'unchanged actual-tree snapshot was not accepted with Windows Path semantics' }",
        `[System.IO.File]::AppendAllText(${quotePowerShell(staleSource)}, '# stale')`,
        "$staleRejected = $false",
        `try { $null = Get-ValidationEvidenceSnapshot -ToolkitRoot ${quotePowerShell(repoRoot)} -ContentRoot ${quotePowerShell(contentRoot)} -SolutionPath ${quotePowerShell(copiedSolution)} -PackageReportPath ${quotePowerShell(packageReportRelativePath)} } catch { if ($_.Exception.Message -match 'stale against current solution inputs under both POSIX and Windows Path ordering') { $staleRejected = $true } else { throw } }`,
        "if (-not $staleRejected) { throw 'changed actual-tree source input was accepted as current' }",
        "[ordered]@{ validationResult = $binding.validationResult; sourcePathSemantics = $before.sourcePathSemantics; staleRejected = $staleRejected } | ConvertTo-Json -Compress",
      ].join("; ");
      const result = spawnSync("pwsh", ["-NoProfile", "-Command", command], {
        encoding: "utf8",
      });
      expect(result.status, result.stderr).to.equal(0);
      const roundtrip = JSON.parse(result.stdout);
      expect(roundtrip.validationResult).to.equal("PASSED");
      expect(roundtrip.sourcePathSemantics).to.equal("windows");
      expect(roundtrip.staleRejected).to.equal(true);
    },
  );

  (powershellAvailable ? it : it.skip)("selects packager Windows Path ordering from the report hash on a cross-host runner", function () {
    this.timeout(15000);
    const fixture = createFixture("windows-packager-order");
    const result = runSnapshot(fixture, {
      windowsPackageIdentity: true,
      snapshotOnly: true,
    });
    expect(result.status, result.stderr).to.equal(0);
    const snapshot = JSON.parse(result.stdout);
    expect(snapshot.sourcePathSemantics).to.equal("windows");
    expect(snapshot.producerPlatform).to.equal(process.platform === "win32" ? "windows" : "posix");
  });

  (powershellAvailable ? it : it.skip)("keeps sparse PASS/SKIP entries working in the actual build report function", () => {
    const fixture = createFixture("build-report");
    const reportPath = path.join(fixture.evidence, "build-and-validate-report.md");
    const command = [
      `. ${quotePowerShell(bindingScript)}`,
      "$tokens = $null; $parseErrors = $null",
      `$runnerAst = [System.Management.Automation.Language.Parser]::ParseFile(${quotePowerShell(runnerScript)}, [ref]$tokens, [ref]$parseErrors)`,
      "if ($parseErrors.Count) { throw ($parseErrors -join '; ') }",
      "$functions = $runnerAst.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -in @('Format-Duration','Write-BuildReport') }, $true)",
      "foreach ($functionAst in $functions) { Invoke-Expression $functionAst.Extent.Text }",
      `$toolkitRoot = ${quotePowerShell(repoRoot)}`,
      `$ContentRoot = ${quotePowerShell(path.join(fixture.root, "content"))}`,
      "$SkipPackaging = $true",
      "$entries = [System.Collections.ArrayList]::new()",
      "$null = $entries.Add([pscustomobject]@{ Step = 2; Name = 'TypeScript validation'; Status = 'passed'; Passed = 1; Failed = 0; Skipped = 0 })",
      "$null = $entries.Add([pscustomobject]@{ Step = 4; Name = 'ARM-TTK'; Status = 'skipped'; SkipReason = 'not installed' })",
      `$meta = @{ StartTime = (Get-Date).AddSeconds(-3); SolutionName = 'FixtureSolution'; EvidenceRunPath = ${quotePowerShell(fixture.evidence)} }`,
      "Write-BuildReport -Meta $meta -Entries $entries -Success $true",
      `$report = [System.IO.File]::ReadAllText(${quotePowerShell(reportPath)})`,
      "if (-not $report.Contains('| TS | TypeScript validation | PASS |') -or -not $report.Contains('| CI-PS | ARM-TTK | SKIP |') -or -not $report.Contains('Total: 2 validators | 1 passed | 0 failed | 1 skipped')) { throw 'PASS/SKIP report rows were not emitted' }",
      "Write-Output 'Actual build report PASS/SKIP output verified'",
    ].join("; ");
    const result = spawnSync("pwsh", ["-NoProfile", "-Command", command], {
      encoding: "utf8",
    });
    expect(result.status, result.stderr).to.equal(0);
    expect(result.stdout).to.contain("Actual build report PASS/SKIP output verified");
  });

  (powershellAvailable ? it : it.skip)("writes a successful binding from the exact V3.1 report and unchanged artifacts", () => {
    const fixture = createFixture("success");
    const result = runSnapshot(fixture);
    expect(result.status, result.stderr).to.equal(0);
    const output = JSON.parse(result.stdout);
    expect(output.binding.validationResult).to.equal("PASSED");
    expect(output.binding.packagingSkipped).to.equal(true);
    expect(output.binding.package.version).to.equal("3.1.1");
    expect(output.binding.package.packageAttemptId).to.equal("attempt-fixture-1");
    expect(output.binding.package.packageArtifactHashes.mainTemplate).to.equal(
      sha256("{\"resources\":[]}\n"),
    );
    expect(output.binding.inputFilesBefore).to.deep.equal(output.binding.inputFilesAfter);
    expect(output.binding.packageFilesBefore).to.deep.equal(output.binding.packageFilesAfter);
    const bindingPath = output.receipt.path as string;
    expect(fs.existsSync(bindingPath)).to.equal(true);
    expect(sha256(fs.readFileSync(bindingPath))).to.equal(output.receipt.sha256);
  });

  (powershellAvailable ? it : it.skip)("fails the binding when source inputs change during validation", () => {
    const fixture = createFixture("changed-source");
    const result = runSnapshot(fixture, { mutateSource: true });
    expect(result.status, result.stderr).to.equal(0);
    const output = JSON.parse(result.stdout);
    expect(output.binding.validationResult).to.equal("FAILED");
    expect(output.binding.issues).to.include("solution input bytes changed during validation");
  });

  (powershellAvailable ? it : it.skip)("fails when an existing validator fails", () => {
    const fixture = createFixture("validator-failure");
    const result = runSnapshot(fixture, { validationFailed: true });
    expect(result.status, result.stderr).to.equal(0);
    const output = JSON.parse(result.stdout);
    expect(output.binding.validationResult).to.equal("FAILED");
    expect(output.binding.validatorSummary.failed).to.equal(1);
  });

  (powershellAvailable ? it : it.skip)("rejects stale package artifacts before producing a successful binding", () => {
    const fixture = createFixture("stale-package");
    const result = runSnapshot(fixture, { mutatePackage: true });
    expect(result.status).to.not.equal(0);
    expect(result.stderr + result.stdout).to.contain("V3.1 package artifact is stale");
  });

  (powershellAvailable ? it : it.skip)("rejects source inputs that changed after V3.1 packaging", () => {
    const fixture = createFixture("stale-source");
    const result = runSnapshot(fixture, { staleSource: true });
    expect(result.status).to.not.equal(0);
    expect(result.stderr + result.stdout).to.contain(
      "V3.1 package report is stale against current solution inputs",
    );
  });
});
