"""Run existing ASIM template checks against the local parser pair."""

import argparse
import importlib.util
import json
from pathlib import Path

import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    validator = root / ".script" / "tests" / "asimParsersTest" / "VerifyASimParserTemplate.py"
    spec = importlib.util.spec_from_file_location("repository_asim_validator", validator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results = []
    for prefix, union in (("ASim", "ASimEmailEvent"), ("vim", "imEmailEvent")):
        folder = root / "Parsers" / "ASimEmailEvent" / "Parsers"
        source = yaml.safe_load((folder / (prefix + "EmailEventProofpointPOD.yaml")).read_text())
        unified = yaml.safe_load((folder / (union + ".yaml")).read_text())
        checks = module.extract_and_check_properties(
            source, unified, prefix, str(root / "Sample Data" / "ASIM")
        )
        results.append({
            "parser": source["ParserName"],
            "checks": [
                {"value": str(value), "check": name, "result": outcome}
                for value, name, outcome in checks
            ],
        })
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    failed = [
        check for result in results for check in result["checks"]
        if "Fail" in check["result"]
    ]
    for result in results:
        print(result["parser"], len(result["checks"]), "checks")
    if failed:
        raise SystemExit(json.dumps(failed, indent=2))
    print("All existing repository template checks passed")


if __name__ == "__main__":
    main()
