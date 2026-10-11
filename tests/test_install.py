import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'scripts/install.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.home = self.root / 'codex home'
        self.target = self.home / 'skills/context-status'
        for name in mod.PACKAGE_FILES:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('synthetic package: ' + name)

    def install(self):
        return mod.apply(self.source, self.home)

    def test_preview_has_no_side_effects_and_fresh_install_is_idempotent(self):
        self.assertEqual(mod.plan(self.source, self.home)['state'], 'new')
        self.assertFalse(self.home.exists())
        result, backup = self.install()
        self.assertIsNone(backup)
        self.assertEqual((self.target / 'SKILL.md').read_bytes(), (self.source / 'SKILL.md').read_bytes())
        before = mod.tree_stamp(self.home)
        self.assertEqual(self.install()[0]['state'], 'current')
        self.assertEqual(before, mod.tree_stamp(self.home))
        self.assertFalse((self.home / 'config.toml').exists())

    def test_upgrade_preserves_extras_and_retains_complete_backup(self):
        self.install()
        (self.target / 'personal-notes.txt').write_text('keep me')
        (self.target / 'mcp/node_modules').mkdir()
        (self.target / 'mcp/node_modules/synthetic').write_text('dependency')
        (self.target / 'extra-link').symlink_to(self.root / 'nonexistent')
        original = mod.tree_stamp(self.target)
        (self.source / 'SKILL.md').write_text('new version')
        result, backup = self.install()
        self.assertEqual(result['state'], 'upgrade')
        self.assertEqual(mod.tree_stamp(backup), original)
        self.assertEqual((self.target / 'personal-notes.txt').read_text(), 'keep me')
        self.assertTrue((self.target / 'extra-link').is_symlink())
        self.assertEqual((self.target / 'mcp/node_modules/synthetic').read_text(), 'dependency')
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'new version')

    def test_local_edit_or_deletion_blocks_upgrade_without_writes(self):
        self.install()
        for deleted in (False, True):
            path = self.target / 'SKILL.md'
            if deleted:
                path.unlink()
            else:
                path.write_text('local customization')
            before = mod.tree_stamp(self.home)
            self.assertIn('SKILL.md', mod.plan(self.source, self.home)['conflicts'])
            with self.assertRaises(ValueError):
                self.install()
            self.assertEqual(before, mod.tree_stamp(self.home))

    def test_matching_manual_update_refreshes_manifest(self):
        self.install()
        for root in (self.source, self.target):
            (root / 'SKILL.md').write_text('matching new version')
        self.assertEqual(self.install()[0]['state'], 'upgrade')
        self.assertEqual(mod.plan(self.source, self.home)['state'], 'current')

    def test_adoption_requires_explicit_flag_and_matching_existing_files(self):
        shutil.copytree(self.source, self.target)
        self.assertEqual(mod.plan(self.source, self.home)['state'], 'unmanaged')
        (self.target / 'scripts/install.py').unlink()  # New package files may be added.
        self.assertEqual(mod.plan(self.source, self.home, True)['conflicts'], [])
        result, backup = mod.apply(self.source, self.home, True)
        self.assertEqual(result['state'], 'adopt')
        self.assertFalse((backup / mod.MANIFEST).exists())
        self.assertTrue((self.target / mod.MANIFEST).exists())
        (self.target / mod.MANIFEST).unlink()
        (self.target / 'SKILL.md').write_text('customized')
        self.assertIn('SKILL.md', mod.plan(self.source, self.home, True)['conflicts'])

    def test_removed_managed_file_only_deleted_when_unchanged(self):
        self.install()
        path = self.target / 'obsolete.txt'
        path.write_text('old version')
        manifest = mod.manifest_files(self.target)
        manifest['obsolete.txt'] = mod.digest(path)
        (self.target / mod.MANIFEST).write_text(json.dumps({'schema': 1, 'files': manifest}))
        path.write_text('local changes')
        self.assertIn('obsolete.txt', mod.plan(self.source, self.home)['conflicts'])
        path.write_text('old version')
        self.install()
        self.assertFalse(path.exists())

    def test_symlink_install_and_managed_symlinks_are_not_followed(self):
        self.target.parent.mkdir(parents=True)
        self.target.symlink_to(self.source)
        self.assertEqual(mod.plan(self.source, self.home)['state'], 'linked')
        with self.assertRaises(ValueError):
            self.install()
        self.target.unlink()
        self.install()
        (self.target / 'SKILL.md').unlink()
        (self.target / 'SKILL.md').symlink_to(self.source / 'SKILL.md')
        with self.assertRaises(ValueError):
            self.install()

    def test_manifest_traversal_and_invalid_data_are_rejected(self):
        self.install()
        for value in ({'schema': 99, 'files': {}}, {'schema': 1, 'files': {'../outside': '0' * 64}}):
            (self.target / mod.MANIFEST).write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                self.install()

    def test_source_symlink_and_overlapping_paths_are_rejected(self):
        (self.source / 'SKILL.md').unlink()
        outside = self.root / 'outside'
        outside.write_text('private')
        (self.source / 'SKILL.md').symlink_to(outside)
        with self.assertRaises(ValueError):
            self.install()
        (self.source / 'SKILL.md').unlink()
        (self.source / 'SKILL.md').write_text('restored')
        with self.assertRaises(ValueError):
            mod.plan(self.source, self.source / 'inside')

    def test_failed_publish_restores_previous_install(self):
        self.install()
        original = mod.tree_stamp(self.target)
        (self.source / 'SKILL.md').write_text('new')
        rename = Path.rename

        def fail_stage(path, destination):
            if path.name.startswith('.context-status-stage-'):
                raise OSError('simulated failure')
            return rename(path, destination)

        with patch.object(Path, 'rename', fail_stage), self.assertRaises(OSError):
            self.install()
        self.assertEqual(mod.tree_stamp(self.target), original)
        self.assertFalse((self.home / '.context-status-install.lock').exists())

    def test_edit_during_staging_aborts_and_preserves_new_edit(self):
        self.install()
        (self.source / 'SKILL.md').write_text('new')
        (self.target / 'notes').write_text('before')
        copytree = shutil.copytree

        def edit_after_copy(*args, **kwargs):
            result = copytree(*args, **kwargs)
            (self.target / 'notes').write_text('during copy')
            return result

        with patch.object(mod.shutil, 'copytree', side_effect=edit_after_copy), self.assertRaises(ValueError):
            self.install()
        self.assertEqual((self.target / 'notes').read_text(), 'during copy')
        self.assertNotEqual((self.target / 'SKILL.md').read_text(), 'new')

    def test_lock_prevents_two_installers(self):
        self.home.mkdir()
        (self.home / '.context-status-install.lock').mkdir()
        with self.assertRaises(ValueError):
            self.install()
        self.assertFalse(self.target.exists())

    def test_registration_commands_quote_paths_and_only_suggest_configuration(self):
        home = self.root / "path with spaces ' and $(literal)"
        commands = mod.commands(home / 'skills/context-status', home)
        npm = shlex.split(commands[0])
        self.assertEqual(npm[3], str(home / 'skills/context-status/mcp'))
        with patch.object(mod.shutil, 'which', return_value='/bin/node'):
            command = shlex.split(mod.commands(home / 'skills/context-status', home)[-1])
        self.assertEqual(command[0], 'CODEX_HOME=' + str(home))
        self.assertEqual(command[-1], str(home / 'skills/context-status/mcp/server.mjs'))
        self.assertFalse(home.exists())


if __name__ == '__main__':
    unittest.main()
