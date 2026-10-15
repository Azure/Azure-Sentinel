import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    'VerifyASimParserTemplate',
    Path(__file__).with_name('VerifyASimParserTemplate.py'),
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ParserNameValidationTests(unittest.TestCase):
    def validate_name(self, name, file_type):
        parser = {
            'ParserName': name,
            'EquivalentBuiltInParser': '_ASim_Dns_Test' if file_type == 'ASim' else '_Im_Dns_Test',
            'Parser': {
                'Title': 'Test parser',
                'Version': '1.0.0',
                'LastUpdated': 'Oct 15, 2026',
            },
            'Normalization': {'Schema': 'Dns', 'Version': '1.0.0'},
            'References': [{'Title': 'ASIM', 'Link': 'https://aka.ms/AboutASIM'}],
            'ParserQuery': 'print EventVendor="Test", EventProduct="Test"',
        }
        union = {
            'ParserQuery': name or '',
            'Parsers': [parser['EquivalentBuiltInParser']],
        }
        with patch.object(validator.os.path, 'exists', return_value=True):
            return validator.extract_and_check_properties(parser, union, file_type, '')

    def test_valid_names_preserve_existing_validation(self):
        for file_type in ('ASim', 'vim'):
            for suffix in ('Product', 'Product_V2', 'Product__'):
                with self.subTest(file_type=file_type, suffix=suffix):
                    results = self.validate_name(f'{file_type}Dns{suffix}', file_type)
                    self.assertTrue(all(result[-1] == 'Pass' for result in results), results)

    def test_invalid_characters_fail_even_with_valid_prefix(self):
        for file_type in ('ASim', 'vim'):
            for suffix in ('-Product', ' Product', '.Product', 'Product\n', '\u00e9'):
                with self.subTest(file_type=file_type, suffix=suffix):
                    results = self.validate_name(f'{file_type}Dns{suffix}', file_type)
                    failures = [result for result in results if result[-1] != 'Pass']
                    self.assertEqual(len(failures), 1, failures)
                    self.assertIn('ParserName must match', failures[0][1])

    def test_valid_identifier_still_requires_schema_prefix(self):
        for file_type in ('ASim', 'vim'):
            with self.subTest(file_type=file_type):
                results = self.validate_name('OtherParser', file_type)
                self.assertTrue(any(
                    'ParserName must match' in result[1] and result[-1] != 'Pass'
                    for result in results
                ))


if __name__ == '__main__':
    unittest.main()
