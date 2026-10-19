"""Run the repository's existing template checks for this new parser pair."""

import importlib.util
from pathlib import Path
import unittest
import yaml


ROOT = Path(__file__).resolve().parents[3]
DIRECTORY = ROOT / "Parsers" / "ASimEmailEvent"
SUFFIX = "EmailEventMicrosoftDefenderOffice365"
spec = importlib.util.spec_from_file_location(
    "asim_template_verifier",
    ROOT / ".script" / "tests" / "asimParsersTest" / "VerifyASimParserTemplate.py",
)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class EmailEventsTemplateTests(unittest.TestCase):
    def test_repository_template_contract(self):
        for prefix, union in (("ASim", "ASimEmailEvent"), ("vim", "imEmailEvent")):
            with self.subTest(variant=prefix):
                parser = yaml.safe_load((DIRECTORY / "Parsers" / (prefix + SUFFIX + ".yaml")).read_text(encoding="utf-8"))
                unifier = yaml.safe_load((DIRECTORY / "Parsers" / (union + ".yaml")).read_text(encoding="utf-8"))
                checks = verifier.extract_and_check_properties(
                    parser, unifier, prefix, str(ROOT / "Sample Data" / "ASIM")
                )
                failures = [check for check in checks if "Fail" in str(check[2])]
                self.assertFalse(failures, "\n".join(str(check) for check in failures))
                print(f"{prefix}: {len(checks)} repository template checks passed")


if __name__ == "__main__":
    unittest.main()
