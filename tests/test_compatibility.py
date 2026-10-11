import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reader', ROOT / 'scripts/context_status.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class CompatibilityTests(unittest.TestCase):
    def assert_subset(self, expected, actual):
        if isinstance(expected, dict):
            self.assertIsInstance(actual, dict)
            for key, value in expected.items():
                self.assertIn(key, actual)
                self.assert_subset(value, actual[key])
        else:
            self.assertEqual(expected, actual)

    def test_documented_format_matrix(self):
        cases = json.loads((ROOT / 'tests/fixtures/compatibility.json').read_text())['cases']
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'synthetic.jsonl'
            for case in cases:
                with self.subTest(case=case['name']):
                    path.write_text(''.join(json.dumps(record) + '\n' for record in case['records']))
                    data = reader.inspect(path, 'fixture-chat')
                    self.assert_subset(case['expect'], data)
                    self.assertNotIn('PRIVATE-', json.dumps(data))
                    self.assertNotIn('unsupported version', json.dumps(data).lower())

    def test_producer_version_is_optional_and_strictly_sanitized(self):
        for value in (None, '', [], {}, 'PRIVATE-/path', '1.2.3\n', '1.2.3-' + 'a' * 100):
            self.assertIsNone(reader.cli_version(value))
        for value in ('0.162.0-alpha.17.2', '1.2.3', '1.2.3+test'):
            self.assertEqual(reader.cli_version(value), value)

    def test_partial_tail_and_malformed_lines_have_separate_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'synthetic.jsonl'
            path.write_bytes(b'{"type":"session_meta","payload":{"id":"fixture-chat"}}\ninvalid\n{"partial":')
            data = reader.inspect(path, 'fixture-chat')
            self.assertEqual(data['ignored_malformed_lines'], 1)
            self.assertTrue(data['compatibility']['incomplete_trailing_record'])
            self.assertIsNone(data['compatibility']['recorded_cli_version'])
            self.assertEqual(data['status'], 'unavailable')

    def test_identity_failure_discards_all_format_and_version_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'synthetic.jsonl'
            path.write_text('{"type":"session_meta","payload":{"id":"other","cli_version":"1.2.3"}}\n')
            data = reader.collect(Path(tmp), 'fixture-chat', path)
            self.assertNotIn('compatibility', data)
            self.assertEqual(data['diagnostics']['failure_code'], 'identity_mismatch')
            self.assertEqual(data['diagnostics']['checks'][-1]['status'], 'not_checked')


if __name__ == '__main__':
    unittest.main()
