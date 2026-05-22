import dataclasses
import json
import unittest
from pathlib import Path

from src.processors.extract_iocs import ExtractIOCs

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = "output"


class TestFolderData(unittest.TestCase):

    def test_domain_shadowing_pdf(self):
        url = "https://unit42.paloaltonetworks.com/domain-shadowing/?pdf=download&lg=en&_wpnonce=2c5aefd0ad"
        result = ExtractIOCs(url).extract_iocs()

        output_path = Path(__file__).parent / OUTPUT_DIR / "domain_shadowing_iocs.json"
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(dataclasses.asdict(result), f, indent=2)
        print(f"\nResults written to {output_path}")

        self.assertIsNotNone(result.report_title)
        self.assertEqual(result.total_domains_found, 13)

    def test_high_risk_gen_ai(self):
        url = "https://unit42.paloaltonetworks.com/high-risk-gen-ai-browser-extensions/?pdf=download&lg=en&_wpnonce=2c5aefd0ad"
        result = ExtractIOCs(url).extract_iocs()
        output_path = Path(__file__).parent / OUTPUT_DIR / "high_risk_gen_ai.json"
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(dataclasses.asdict(result), f, indent=2)
        print(f"\nResults written to {output_path}")
