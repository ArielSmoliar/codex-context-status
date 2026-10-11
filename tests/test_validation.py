import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('validation', ROOT / 'scripts/prepare_validation.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class ValidationTests(unittest.TestCase):
    def test_complete_kit_separates_receiver_and_evaluator(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = kit.generate(Path(tmp) / 'kit')
            cases = json.loads(kit.CATALOG.read_text())['cases']
            for case in cases:
                workspace = output / 'receivers' / case['id']
                actual = {str(p.relative_to(workspace)): p.read_text()
                          for p in workspace.rglob('*') if p.is_file() and '.git' not in p.parts}
                self.assertEqual(actual, {**case['files'], **case.get('dirty', {})})
                facilitator = output / 'facilitator' / case['id']
                self.assertEqual(json.loads((facilitator / 'rubric.json').read_text())['status'], 'NOT RUN')
                example = (facilitator / 'resume-example.txt').read_text()
                self.assertEqual('[Paste the reviewed handoff here]' in example, case['handoff'] is None)
            self.assertEqual(list((output / 'receivers/06').iterdir()), [])
            self.assertFalse((output / 'facilitator/06/source-workspace').exists())
            source = json.loads((output / 'facilitator/05/source-workspace/state.json').read_text())
            receiver = json.loads((output / 'receivers/05/state.json').read_text())
            self.assertEqual((source['status'], receiver['status']), ('open', 'merged'))
            metadata = json.loads((output / 'SOURCE.json').read_text())
            self.assertEqual(metadata['model_trials'], 'NOT RUN')
            self.assertEqual(len(metadata['sha256']), 7)
            self.assertIn('NOT RUN', (output / 'results.md').read_text())
            demo = (output / 'demo.html').read_text()
            self.assertIn('sandbox="allow-scripts"', demo)
            self.assertNotIn('allow-same-origin', demo)
            self.assertIn("default-src 'none'", demo)
            self.assertIn('Example data only', demo)
            self.assertFalse((output / 'demo-fragment.html').exists())

    def test_git_ignores_inherited_target_and_global_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / 'gitconfig'
            config.write_text('[commit]\n gpgSign = true\n[core]\n hooksPath = /missing/hook/directory\n')
            with patch.dict(os.environ, {'GIT_DIR': '/wrong', 'GIT_WORK_TREE': '/wrong',
                                         'GIT_CONFIG_GLOBAL': str(config),
                                         'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'commit.gpgsign',
                                         'GIT_CONFIG_VALUE_0': 'true'}):
                output = kit.generate(root / 'kit')
                workspace = output / 'receivers/02'
                self.assertEqual(kit.git(workspace, 'branch', '--show-current'), 'trial-main')
                self.assertEqual(kit.git(workspace, 'show', 'HEAD:notes.txt'), 'original note')
                self.assertEqual(kit.git(workspace, 'status', '--porcelain'), 'M notes.txt')
                before = (workspace / 'notes.txt').read_bytes()
                result = subprocess.run([sys.executable, 'check.py'], cwd=workspace,
                                        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                                        capture_output=True, text=True, check=True)
                self.assertIn('banner check passed', result.stdout)
                self.assertEqual((workspace / 'notes.txt').read_bytes(), before)
                self.assertEqual(kit.git(workspace, 'status', '--porcelain'), 'M notes.txt')

    def test_existing_targets_are_never_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / 'existing'
            existing.mkdir()
            marker = existing / 'keep'
            marker.write_text('untouched')
            link = root / 'link'
            link.symlink_to(existing, target_is_directory=True)
            dangling = root / 'dangling'
            dangling.symlink_to(root / 'missing')
            for target in (existing, marker, link, dangling):
                with self.assertRaises(FileExistsError):
                    kit.generate(target)
            self.assertEqual(marker.read_text(), 'untouched')
            self.assertTrue(link.is_symlink())

    def test_failure_cleans_only_new_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'kit'
            with patch.object(kit, 'make_workspace', side_effect=OSError('synthetic failure')):
                with self.assertRaisesRegex(OSError, 'synthetic failure'):
                    kit.generate(output)
            self.assertFalse(output.exists())

    def test_prompt_extraction_matches_canonical_without_evaluation(self):
        source = (ROOT / 'assets/inspector.html').read_text()
        result = kit.prompts(source)
        self.assertTrue(result['prepare'].startswith('Write a concise handoff'))
        self.assertTrue(result['resume'].startswith('Resume the task'))
        for changed in (source.replace('const handoffPrompts', 'const otherPrompts'),
                        source.replace('prepare: `', 'prepare: `\\n'),
                        source.replace('prepare: `', 'prepare: `${call()}'),
                        source.replace('[Paste the reviewed handoff here]', '[new placeholder]')):
            with self.assertRaises(ValueError):
                kit.prompts(changed)

    def test_unsafe_fixture_paths_fail_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = json.loads(kit.CATALOG.read_text())
            for name in ('../escape', '/absolute', '.git/config', 'a/../b', 'a\\b', 'C:/x'):
                original['cases'][0]['files'] = {name: 'bad'}
                fixture = root / 'fixture.json'
                fixture.write_text(json.dumps(original))
                with patch.object(kit, 'CATALOG', fixture):
                    with self.assertRaises(ValueError):
                        kit.generate(root / 'out')
                self.assertFalse((root / 'out').exists())

    def test_archive_without_git_metadata_still_labels_provenance_unknown(self):
        real_git = kit.git
        def archive_git(directory, *args):
            if directory == ROOT:
                raise subprocess.CalledProcessError(128, 'git')
            return real_git(directory, *args)
        with tempfile.TemporaryDirectory() as tmp, patch.object(kit, 'git', archive_git):
            output = kit.generate(Path(tmp) / 'kit')
            metadata = json.loads((output / 'SOURCE.json').read_text())
            self.assertIsNone(metadata['commit'])
            self.assertIsNone(metadata['checkout_dirty'])

    def test_cli_reports_failure_without_claiming_trials_ran(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/prepare_validation.py'),
                                     '--output', tmp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Kit not created', result.stderr)
            self.assertNotIn('Synthetic kit:', result.stdout)


if __name__ == '__main__':
    unittest.main()
