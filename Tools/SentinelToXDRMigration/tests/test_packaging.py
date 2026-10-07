from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

from sentinel_xdr_migration.packaging import package_solution_v4


class PackagingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repository = Path(self.temp.name)
        self.solution = self.repository / "Solutions" / "Sample"
        data = self.solution / "Data"
        detections = self.solution / "XDR Detections"
        package = self.solution / "Package"
        script = (
            self.repository
            / "Tools"
            / "Create-Azure-Sentinel-Solution"
            / "V4"
            / "createSolutionV4.ps1"
        )
        data.mkdir(parents=True)
        detections.mkdir()
        package.mkdir()
        script.parent.mkdir(parents=True)
        script.write_text("", encoding="utf-8")
        (detections / "Detection.yaml").write_text("kind: CustomDetection\n", encoding="utf-8")
        (data / "Solution_Sample.json").write_text(
            json.dumps({
                "Name": "Sample",
                "Version": "1.2.3",
                "XDR Detections": ["XDR Detections/Detection.yaml"],
            }),
            encoding="utf-8",
        )
        for name in (
            "mainTemplate.json",
            "createUiDefinition.json",
            "testParameters.json",
        ):
            (package / name).write_text("{}", encoding="utf-8")
        with zipfile.ZipFile(package / "1.2.3.zip", "w") as archive:
            archive.writestr("mainTemplate.json", "{}")
            archive.writestr("createUiDefinition.json", "{}")

    def tearDown(self) -> None:
        self.temp.cleanup()

    @mock.patch(
        "sentinel_xdr_migration.packaging.subprocess.run",
        return_value=CompletedProcess(
            args=[],
            returncode=0,
            stdout="=======Starting Package Creation using V4 tool=========",
            stderr="",
        ),
    )
    @mock.patch(
        "sentinel_xdr_migration.packaging.shutil.which",
        return_value=r"C:\Program Files\PowerShell\7\pwsh.exe",
    )
    def test_runs_v4_and_returns_workflow_evidence(
        self,
        which: mock.Mock,
        run: mock.Mock,
    ) -> None:
        result = package_solution_v4(self.solution, version_bump="none")

        self.assertEqual("V4", result["packager"])
        self.assertEqual(1, result["xdrDetectionCount"])
        self.assertEqual("V4", result["workflowArtifacts"]["packager"])
        self.assertTrue(Path(result["packageReport"]).is_file())
        command = run.call_args.args[0]
        self.assertIn("createSolutionV4.ps1", command[3])
        self.assertEqual("none", command[-1])
        self.assertEqual(self.repository, run.call_args.kwargs["cwd"])
        which.assert_called_once_with("pwsh")

    def test_rejects_missing_xdr_reference_before_packaging(self) -> None:
        data = self.solution / "Data" / "Solution_Sample.json"
        document = json.loads(data.read_text(encoding="utf-8"))
        document["XDR Detections"] = ["XDR Detections/Missing.yaml"]
        data.write_text(json.dumps(document), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "does not exist"):
            package_solution_v4(self.solution, version_bump="none")


if __name__ == "__main__":
    unittest.main()
