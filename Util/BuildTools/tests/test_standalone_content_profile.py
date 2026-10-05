import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'standalone_content_profile.py'
SPEC = importlib.util.spec_from_file_location('profile', SCRIPT)
PROFILE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROFILE)


class CatalogueTests(unittest.TestCase):
    def test_subset_reports_every_exclusion_without_mutating_input(self):
        source = {'Props': [{'Name': 'a', 'Mesh': '/Game/A.A'},
                            {'Name': 'b', 'Mesh': '/Game/B.B'}], 'Extra': 42}
        actual, excluded = PROFILE.project_catalogue(source, {'/Game/A'})
        self.assertEqual(actual['Props'], source['Props'][:1])
        self.assertEqual(actual['Extra'], 42)
        self.assertEqual(len(source['Props']), 2)
        self.assertEqual(excluded, [{'name': 'b', 'package': '/Game/B'}])

    def test_invalid_and_empty_are_not_success(self):
        for props in ([], [{'Name': 'a', 'Mesh': '/Game/../A'}],
                      [{'Name': 'a', 'Mesh': '/Engine/A'}],
                      [{'Name': 'a', 'Mesh': '/Game/A'}] * 2):
            with self.subTest(props=props), self.assertRaises(ValueError):
                PROFILE.project_catalogue({'Props': props}, {'/Game/A'})

    def test_cli_deterministic_and_repeat_preserves_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / 'Content'
            content.mkdir()
            (content / 'A.uasset').touch()
            source = root / 'source.json'
            original = '{"Props":[{"Name":"a","Mesh":"/Game/A.A"}]}'
            source.write_text(original)
            output, report = root / 'projected.json', root / 'report.json'
            command = [sys.executable, str(SCRIPT), '--catalogue', str(source),
                       '--cooked-content', str(content), '--output', str(output),
                       '--report', str(report)]
            first = subprocess.run(command, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = output.read_bytes(), report.read_bytes()
            self.assertEqual(json.loads(report.read_text())['includedCount'], 1)
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(before, (output.read_bytes(), report.read_bytes()))
            self.assertEqual(source.read_text(), original)


if __name__ == '__main__':
    unittest.main()
