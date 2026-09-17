from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class SkillContractTests(unittest.TestCase):
    def test_optional_testing_invokes_generation_skill_before_folder_fallback(self):
        text = (
            ROOT
            / ".github"
            / "skills"
            / "sentinel-solution-optional-testing"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        generation = text.index("sentinel-solution-mock-data-generation")
        folder_fallback = text.index("--mock-data-folder")
        self.assertLess(generation, folder_fallback)
        self.assertIn("generationStatus=qualification-ready", text)

    def test_generation_skill_is_azure_sentinel_only(self):
        text = (
            ROOT
            / ".github"
            / "skills"
            / "sentinel-solution-mock-data-generation"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Never invoke CAT.Tools at runtime.", text)
        self.assertIn("existing-scenario", text)
        self.assertIn("generate_mock_scenario.py", text)

    def test_solution_manager_is_single_connected_agent(self):
        text = (
            ROOT
            / ".github"
            / "agents"
            / "xdr-solution-manager.agent.md"
        ).read_text(encoding="utf-8")

        generation = text.index("sentinel-solution-mock-data-generation")
        optional_testing = text.index("sentinel-solution-optional-testing")
        self.assertLess(generation, optional_testing)
        workflow = text.index("## Migration workflow")
        self.assertLess(text.index("sentinel-xdr-migration doctor"), workflow)
        self.assertLess(
            text.index("At the start of optional qualification testing", workflow),
            text.index("Reuse an existing reviewed scenario", workflow),
        )
        self.assertIn("sentinel-xdr-migration setup", text)
        self.assertIn("XDR Solution Manager", text)
        self.assertIn("do not replace the original workflow", text)
        self.assertIn("CAT.Tools is not a runtime dependency.", text)
        self.assertIn("Pass `--approve-write` only after approval", text)
        self.assertIn("Retry permission check", text)
        self.assertIn("selectable buttons", text)

        agents = list((ROOT / ".github" / "agents").glob("*.agent.md"))
        names = [
            path.read_text(encoding="utf-8").split("name:", 1)[1].splitlines()[0].strip()
            for path in agents
        ]
        self.assertEqual(["XDR Solution Manager"], names)

    def test_optional_testing_requires_startup_before_target_preflight(self):
        text = (
            ROOT
            / ".github"
            / "skills"
            / "sentinel-solution-optional-testing"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        startup = text.index("sentinel-xdr-migration doctor")
        target_preflight = text.index("target-specific DCR permission preflight")
        fixture_review = text.index("## Fixture review")
        self.assertLess(startup, target_preflight)
        self.assertLess(target_preflight, fixture_review)


if __name__ == "__main__":
    unittest.main()
