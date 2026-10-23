import { spawnSync } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { expect } from "chai";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const validatorPath = path.join(repoRoot, ".script/local-validation/validate.js");
const buildRunnerPath = path.join(repoRoot, ".script/local-validation/build-and-validate.ps1");
const hyperlinkValidatorPath = path.join(repoRoot, ".script/package-automation/hyperlink-validation.ps1");

function validateJsonInPath(solutionPath: string) {
  return spawnSync("node", [validatorPath, "--path", solutionPath, "--only", "json", "--json"], {
    cwd: repoRoot,
    encoding: "utf8",
  });
}

describe("local validation folder scope", () => {
  for (const solutionFolder of ["CiscoASA", "Endpoint Threat Protection Essentials"]) {
    it(`validates only current JSON files under Solutions/${solutionFolder}`, () => {
      const result = validateJsonInPath(path.join("Solutions", solutionFolder));
      expect(result.status, result.stderr).to.be.oneOf([0, 1]);

      const report = JSON.parse(result.stdout);
      expect(report.results.length).to.be.greaterThan(0);
      expect(report.results.every((entry: { filePath: string }) =>
        entry.filePath.startsWith(`Solutions/${solutionFolder}/`))).to.equal(true);
      if (solutionFolder === "CiscoASA") {
        expect(report.results.some((entry: { filePath: string }) =>
          entry.filePath === "Solutions/CiscoASA/Package/mainTemplate.json")).to.equal(true);
      }
    });
  }

  it("rejects a nonexistent explicit folder rather than validating another scope", () => {
    const result = validateJsonInPath("Solutions/this-solution-folder-does-not-exist");
    expect(result.status).to.equal(2);
    expect(result.stderr).to.contain("existing directory");
    expect(result.stdout).to.equal("");
  });

  it("does not treat a similarly prefixed solution as part of the requested folder", () => {
    const target = "Solutions/CiscoASA";
    const siblingFolders = fs.readdirSync(path.join(repoRoot, "Solutions"))
      .filter(name => name.startsWith("CiscoASA") && name !== "CiscoASA");
    const result = validateJsonInPath(target);
    expect(result.status, result.stderr).to.be.oneOf([0, 1]);

    const report = JSON.parse(result.stdout);
    for (const sibling of siblingFolders) {
      expect(report.results.some((entry: { filePath: string }) =>
        entry.filePath.startsWith(`Solutions/${sibling}/`))).to.equal(false);
    }
  });

  it("uses an explicitly selected content root instead of the toolkit checkout", () => {
    const fixtureRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/content");
    const reportPath = path.join(repoRoot, ".script/tests/localValidationTest/cross-root-results.json");
    fs.rmSync(reportPath, { force: true });

    try {
      const result = spawnSync("node", [
        validatorPath,
        "--path", "Solutions/RootProbe",
        "--repository-root", fixtureRoot,
        "--only", "json",
        "--json-file", reportPath,
      ], { cwd: repoRoot, encoding: "utf8" });

      expect(result.status, result.stderr).to.equal(1);
      expect(result.stdout).to.contain("Complete TypeScript validation results written");
      expect(fs.existsSync(reportPath)).to.equal(true);
      const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
      expect(report.summary.failed).to.equal(1);
      expect(report.results[0].validator).to.equal("JSON Syntax");
      expect(report.results[0].filePath).to.equal("Solutions/RootProbe/Data/invalid.json");
      expect(report.results[0].passed).to.equal(false);
      expect(report.results[0].error).to.be.a("string").and.not.empty;
      expect(report.results.some((entry: { filePath: string }) =>
        /Solutions\/RootProbe\/(Logs|Reports|Evidence)\//.test(entry.filePath))).to.equal(false);

      fs.rmSync(reportPath, { force: true });
      const toolkitFixtureRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/toolkit");
      const toolkitResult = spawnSync("node", [
        validatorPath,
        "--path", "Solutions/RootProbe",
        "--repository-root", toolkitFixtureRoot,
        "--only", "json",
        "--json-file", reportPath,
      ], { cwd: repoRoot, encoding: "utf8" });
      expect(toolkitResult.status, toolkitResult.stderr).to.equal(0);
      const toolkitReport = JSON.parse(fs.readFileSync(reportPath, "utf8"));
      expect(toolkitReport.summary.failed).to.equal(0);
    } finally {
      fs.rmSync(reportPath, { force: true });
    }
  });

  it("writes complete structured results larger than captured console output", () => {
    const fixtureRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/content");
    const dataDirectory = path.join(fixtureRoot, "Solutions/RootProbe/Data/large-output");
    const reportPath = path.join(repoRoot, ".script/tests/localValidationTest/large-cross-root-results.json");
    fs.mkdirSync(dataDirectory, { recursive: true });
    for (let index = 0; index < 180; index++) {
      fs.writeFileSync(path.join(dataDirectory, `invalid-${index}.json`), "{\"invalid\":", "utf8");
    }

    try {
      const result = spawnSync("node", [
        validatorPath,
        "--path", "Solutions/RootProbe",
        "--repository-root", fixtureRoot,
        "--only", "json",
        "--json-file", reportPath,
      ], { cwd: repoRoot, encoding: "utf8" });
      expect(result.status).to.equal(1);
      expect(result.stdout.length).to.be.lessThan(1024);
      const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
      expect(report.summary.failed).to.equal(181);
      expect(fs.statSync(reportPath).size).to.be.greaterThan(16000);
    } finally {
      fs.rmSync(dataDirectory, { recursive: true, force: true });
      fs.rmSync(reportPath, { force: true });
    }
  });

  it("counts scoped .NET exclusions as skipped, not passed or failed", () => {
    const fixtureRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/content");
    const reportPath = path.join(repoRoot, ".script/tests/localValidationTest/skipped-cross-root-results.json");
    fs.rmSync(reportPath, { force: true });
    try {
      const result = spawnSync("node", [
        validatorPath,
        "--path", "Solutions/RootProbe",
        "--repository-root", fixtureRoot,
        "--only", "kql",
        "--json-file", reportPath,
      ], { cwd: repoRoot, encoding: "utf8" });
      expect(result.status).to.equal(0);
      const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
      expect(report.summary).to.deep.equal({ total: 1, passed: 0, failed: 0, skipped: 1 });

      const displayResult = spawnSync("node", [
        validatorPath,
        "--path", "Solutions/RootProbe",
        "--repository-root", fixtureRoot,
        "--only", "kql",
      ], { cwd: repoRoot, encoding: "utf8" });
      expect(displayResult.status).to.equal(0);
      expect(displayResult.stdout).to.contain("⏭ KQL Validation");
      expect(displayResult.stdout).not.to.contain("✅ KQL Validation");
    } finally {
      fs.rmSync(reportPath, { force: true });
    }
  });

  it("passes the selected content root to standalone .NET validators", () => {
    const contentRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/content");
    const stubDirectory = path.join(repoRoot, ".script/tests/localValidationTest", `.dotnet-stub-${process.pid}`);
    const markerPath = path.join(stubDirectory, "selected-content-root.txt");
    const reportPath = path.join(repoRoot, ".script/tests/localValidationTest", `cross-root-dotnet-${process.pid}.json`);
    const stubPath = path.join(stubDirectory, process.platform === "win32" ? "dotnet.cmd" : "dotnet");
    fs.mkdirSync(stubDirectory, { recursive: true });
    fs.writeFileSync(stubPath, process.platform === "win32"
      ? "@echo off\r\nif \"%1\"==\"--version\" (echo 8.0.100 & exit /b 0)\r\necho %SENTINEL_VALIDATION_CONTENT_ROOT%>%DOTNET_CONTENT_ROOT_MARKER%\r\necho Stubbed dotnet test\r\nexit /b 0\r\n"
      : "#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then printf '8.0.100\\n'; exit 0; fi\nprintf '%s' \"$SENTINEL_VALIDATION_CONTENT_ROOT\" > \"$DOTNET_CONTENT_ROOT_MARKER\"\nprintf 'Stubbed dotnet test\\n'\n", "utf8");
    fs.chmodSync(stubPath, 0o755);

    try {
      const result = spawnSync("node", [
        validatorPath,
        "--repository-root", contentRoot,
        "--files", "Solutions/RootProbe/Data/invalid.json",
        "--only", "kql",
        "--json-file", reportPath,
      ], {
        cwd: repoRoot,
        encoding: "utf8",
        env: {
          ...process.env,
          PATH: `${stubDirectory}${path.delimiter}${process.env.PATH ?? ""}`,
          DOTNET_CONTENT_ROOT_MARKER: markerPath,
        },
      });

      expect(result.status, result.stderr).to.equal(0);
      expect(fs.readFileSync(markerPath, "utf8").trim()).to.equal(contentRoot);
      const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
      const kqlResult = report.results.find((entry: { validator: string }) =>
        entry.validator === "KQL Validation");
      expect(kqlResult?.passed).to.equal(true);
      expect(kqlResult?.filePath).to.equal(path.join(repoRoot, ".script/tests/KqlvalidationsTests/Kqlvalidations.Tests.csproj"));
    } finally {
      fs.rmSync(stubDirectory, { recursive: true, force: true });
      fs.rmSync(reportPath, { force: true });
    }
  });

  it("rejects a content root without Solutions instead of falling back to the toolkit root", () => {
    const result = spawnSync("node", [
      validatorPath,
      "--path", "Solutions/CiscoASA",
      "--repository-root", path.join(repoRoot, ".script/tests/localValidationTest"),
      "--only", "json",
      "--json",
    ], { cwd: repoRoot, encoding: "utf8" });

    expect(result.status).to.equal(2);
    expect(result.stderr).to.contain("repository directory containing Solutions/");
    expect(result.stdout).to.equal("");
  });

  const powershellAvailable = spawnSync("pwsh", ["--version"], { encoding: "utf8" }).status === 0;
  (powershellAvailable ? it : it.skip)("checks selected-root publishable links but excludes private path segments", () => {
    const contentRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/content");
    const solutionPath = path.join(contentRoot, "Solutions/RootProbe");
    const fixtureDirectory = path.join(solutionPath, "Data/hyperlink-test-temp");
    const privateDirectories = [
      "lOgS/hyperlink-test-temp/nested",
      "RePoRtS/hyperlink-test-temp/nested",
      "eViDeNcE/hyperlink-test-temp/nested",
    ].map(relative => path.join(solutionPath, relative));
    const privateFile = path.join(privateDirectories[0], "packaging.v3_1.json");
    const requestMarker = path.join(fixtureDirectory, "requests.txt");
    const selectedLinks = [
      "https://public.example.test/current-content",
      "https://public.example.test/Reports.md.json",
      "https://public.example.test/LogsArchive/current",
      "https://public.example.test/Evidence-notes/current",
    ];
    const privateLogText = "templateURL=https://public.example.test/historical/mainTemplate.json; trackingId=fixture-only";

    fs.mkdirSync(fixtureDirectory, { recursive: true });
    privateDirectories.forEach(directory => fs.mkdirSync(directory, { recursive: true }));
    fs.writeFileSync(path.join(fixtureDirectory, "current.json"), JSON.stringify({ url: selectedLinks[0] }), "utf8");
    fs.writeFileSync(path.join(fixtureDirectory, "Reports.md.json"), JSON.stringify({ url: selectedLinks[1] }), "utf8");
    fs.writeFileSync(path.join(fixtureDirectory, "LogsArchive.json"), JSON.stringify({ url: selectedLinks[2] }), "utf8");
    fs.writeFileSync(path.join(fixtureDirectory, "Evidence-notes.json"), JSON.stringify({ url: selectedLinks[3] }), "utf8");
    fs.writeFileSync(privateFile, JSON.stringify({ log: privateLogText }), "utf8");
    fs.writeFileSync(path.join(privateDirectories[1], "report.json"), JSON.stringify({ url: "https://private.example.test/reports" }), "utf8");
    fs.writeFileSync(path.join(privateDirectories[2], "evidence.json"), JSON.stringify({ url: "https://private.example.test/evidence" }), "utf8");

    try {
      const runValidator = (cwd: string) => spawnSync("pwsh", ["-NoProfile", "-Command", [
        "function global:Invoke-WebRequest { param([string]$Uri, [int]$TimeoutSec); [System.IO.File]::AppendAllText($env:REQUEST_MARKER, \"$Uri`n\"); [pscustomobject]@{ StatusCode = 200 } }",
        "& $env:HYPERLINK_VALIDATOR_PATH -runId test -pullRequestNumber 0 -instrumentationKey '' -baseFolderPath $env:CONTENT_ROOT -SolutionPath $env:SOLUTION_PATH",
      ].join("; ")], {
        cwd,
        encoding: "utf8",
        env: {
          ...process.env,
          HYPERLINK_VALIDATOR_PATH: hyperlinkValidatorPath,
          CONTENT_ROOT: contentRoot,
          SOLUTION_PATH: solutionPath,
          REQUEST_MARKER: requestMarker,
        },
      });
      for (const cwd of [repoRoot, contentRoot]) {
        fs.rmSync(requestMarker, { force: true });
        const result = runValidator(cwd);
        expect(result.status, result.stderr).to.equal(0);
        expect(result.stdout).to.contain("Hyperlink validation scoped to current files");
        const requestedLinks = fs.readFileSync(requestMarker, "utf8").trim().split(/\r?\n/).sort();
        expect(requestedLinks).to.deep.equal([...selectedLinks].sort());
        expect(requestedLinks.some(url => url.includes("mainTemplate.json;"))).to.equal(false);
      }
    } finally {
      fs.rmSync(fixtureDirectory, { recursive: true, force: true });
      privateDirectories.forEach(directory => fs.rmSync(directory, { recursive: true, force: true }));
    }
  }).timeout(15000);

  (powershellAvailable ? it : it.skip)("fails explicitly when a selected-root hyperlink file disappears during discovery", () => {
    const contentRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/content");
    const solutionPath = path.join(contentRoot, "Solutions/RootProbe");
    const fixtureDirectory = path.join(solutionPath, "Data/hyperlink-missing-test-temp");
    const missingFile = path.join(fixtureDirectory, "missing-on-read.json");
    fs.mkdirSync(fixtureDirectory, { recursive: true });
    fs.writeFileSync(missingFile, JSON.stringify({ reference: "https://public.example.test/docs" }), "utf8");

    const result = spawnSync("pwsh", ["-NoProfile", "-Command", [
      "function global:Invoke-WebRequest { param([string]$Uri, [int]$TimeoutSec, [string]$ErrorAction); [pscustomobject]@{ StatusCode = 200 } }",
      "function global:Get-ChildItem { [CmdletBinding()] param([Parameter(Position=0)][string[]]$Path, [switch]$Recurse, [switch]$File); $items = Microsoft.PowerShell.Management\\Get-ChildItem -Path $Path -Recurse:$Recurse -File:$File; if ($Path -contains $env:SOLUTION_PATH) { Remove-Item -LiteralPath $env:MISSING_EVIDENCE_FILE -Force }; return $items }",
      "& $env:HYPERLINK_VALIDATOR_PATH -runId test -pullRequestNumber 0 -instrumentationKey '' -baseFolderPath $env:CONTENT_ROOT -SolutionPath $env:SOLUTION_PATH",
    ].join("; ")], {
      cwd: repoRoot,
      encoding: "utf8",
      env: {
        ...process.env,
        HYPERLINK_VALIDATOR_PATH: hyperlinkValidatorPath,
        CONTENT_ROOT: contentRoot,
        SOLUTION_PATH: solutionPath,
        MISSING_EVIDENCE_FILE: missingFile,
      },
    });

    try {
      expect(result.status).to.equal(1);
      expect(result.stdout).to.contain(`Content file does not exist under the selected content root: '${missingFile}'`);
    } finally {
      fs.rmSync(fixtureDirectory, { recursive: true, force: true });
    }
  });

  (powershellAvailable ? it : it.skip)("fails when a publishable selected-root URL is actually invalid", () => {
    const contentRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/content");
    const solutionPath = path.join(contentRoot, "Solutions/RootProbe");
    const fixtureDirectory = path.join(solutionPath, "Data/hyperlink-invalid-test-temp");
    const invalidUrl = "https://public.example.test/not-found";
    const linkFile = path.join(fixtureDirectory, "current.json");
    fs.mkdirSync(fixtureDirectory, { recursive: true });
    fs.writeFileSync(linkFile, JSON.stringify({ url: invalidUrl }), "utf8");

    const result = spawnSync("pwsh", ["-NoProfile", "-Command", [
      "function global:Invoke-WebRequest { param([string]$Uri, [int]$TimeoutSec); $exception = [System.Exception]::new('Not Found'); $exception | Add-Member -MemberType NoteProperty -Name Response -Value ([pscustomobject]@{ StatusCode = 404 }); throw $exception }",
      "& $env:HYPERLINK_VALIDATOR_PATH -runId test -pullRequestNumber 0 -instrumentationKey '' -baseFolderPath $env:CONTENT_ROOT -SolutionPath $env:SOLUTION_PATH",
    ].join("; ")], {
      cwd: repoRoot,
      encoding: "utf8",
      env: {
        ...process.env,
        HYPERLINK_VALIDATOR_PATH: hyperlinkValidatorPath,
        CONTENT_ROOT: contentRoot,
        SOLUTION_PATH: solutionPath,
      },
    });

    try {
      expect(result.status).to.equal(1);
      expect(result.stdout).to.contain(invalidUrl);
      expect(result.stdout).to.contain(": Invalid URL");
    } finally {
      fs.rmSync(fixtureDirectory, { recursive: true, force: true });
    }
  });

  (powershellAvailable ? it : it.skip)("accepts a separate content worktree in validation-only mode", () => {
    const contentRoot = path.join(repoRoot, ".script/tests/localValidationTest/crossRootFixtures/content");
    const gitDirectory = path.join(contentRoot, ".git");
    const evidenceParent = path.join(repoRoot, ".script/local-validation/Logs", `cross-root-runner-${process.pid}-${Date.now()}`);
    const before = fs.readFileSync(path.join(contentRoot, "Solutions/RootProbe/Data/invalid.json"));

    try {
      const init = spawnSync("git", ["init", "--quiet", contentRoot], { cwd: repoRoot, encoding: "utf8" });
      expect(init.status, init.stderr).to.equal(0);
      const result = spawnSync("pwsh", [
        "-NoProfile", "-File", buildRunnerPath,
        "-SolutionName", "RootProbe",
        "-ContentRoot", contentRoot,
        "-SkipPackaging",
        "-SkipValidation",
        "-VersionBump", "none",
        "-EvidenceDirectory", evidenceParent,
      ], { cwd: repoRoot, encoding: "utf8" });

      expect(result.status, result.stderr).to.equal(0);
      expect(result.stdout).to.contain(`Content Root: ${contentRoot}`);
      expect(result.stdout).to.contain("[REPORT_START]");
      expect(result.stdout).to.contain("[REPORT_END]");
      expect(fs.readFileSync(path.join(contentRoot, "Solutions/RootProbe/Data/invalid.json"))).to.deep.equal(before);
    } finally {
      fs.rmSync(gitDirectory, { recursive: true, force: true });
      fs.rmSync(evidenceParent, { recursive: true, force: true });
    }
  });
});
