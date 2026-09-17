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

    def test_migration_agent_connects_generation_before_optional_testing(self):
        text = (
            ROOT
            / ".github"
            / "agents"
            / "sentinel-solution-migration.agent.md"
        ).read_text(encoding="utf-8")

        generation = text.index("sentinel-solution-mock-data-generation")
        optional_testing = text.index("sentinel-solution-optional-testing")
        self.assertLess(generation, optional_testing)
        self.assertIn("CAT.Tools is not a runtime dependency.", text)
        self.assertIn("Pass `--approve-write` only after approval", text)


if __name__ == "__main__":
    unittest.main()
