"""Small synthetic restoration checks; never a teammate/runtime acceptance test."""
import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('restore', Path(__file__).with_name('restore_native_playtest.py'))
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)

class RestoreTests(unittest.TestCase):
    def setUp(self):
        task_tmp = Path(__file__).resolve().parents[2] / 'tmp'
        task_tmp.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='restore-unit-', dir=task_tmp)
        self.original = restore.ROOT, restore.STAGE
        restore.ROOT = Path(self.temp.name)
        restore.STAGE = restore.ROOT / 'tmp/native-playtest-restore'
        restore.STAGE.mkdir(parents=True)
        self.sample = restore.STAGE / 'sample.txt'
        self.sample.write_text('new version', encoding='utf-8')
        self.e = {'path': 'Unreal/ParisStreetCombat/Content/ParisCombat/synthetic.uasset',
                  'sha256': restore.sha(self.sample), 'size_bytes': self.sample.stat().st_size,
                  'remote_path': '/objects/sha256/aa/synthetic'}
        (restore.STAGE / self.e['sha256']).write_bytes(self.sample.read_bytes())
        self.args = argparse.Namespace(backup_conflicts=False)

    def tearDown(self):
        restore.ROOT, restore.STAGE = self.original
        self.temp.cleanup()

    def test_escape_refused(self):
        for path in ('../outside', '/outside', 'C:/outside', 'a\\b'):
            with self.assertRaises(RuntimeError):
                restore.safe_path(path)

    def test_restore_then_verify_and_remove_disposable_stage(self):
        restore.apply(self.args, [], [self.e])
        self.assertTrue(restore.same(restore.safe_path(self.e['path']), self.e))
        self.assertFalse((restore.STAGE / self.e['sha256']).exists())

    def test_conflict_refused_without_touching_original(self):
        target = restore.safe_path(self.e['path'])
        target.parent.mkdir(parents=True)
        target.write_text('my local edit', encoding='utf-8')
        with self.assertRaises(RuntimeError):
            restore.apply(self.args, [], [self.e])
        self.assertEqual(target.read_text(), 'my local edit')

    def test_explicit_conflict_backup_retained(self):
        target = restore.safe_path(self.e['path'])
        target.parent.mkdir(parents=True)
        target.write_text('my local edit', encoding='utf-8')
        self.args.backup_conflicts = True
        restore.apply(self.args, [], [self.e])
        backups = list(restore.STAGE.glob('backups-*/' + self.e['path']))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'my local edit')

    def test_wrong_download_does_not_place(self):
        (restore.STAGE / self.e['sha256']).write_text('corrupt', encoding='utf-8')
        with self.assertRaises(RuntimeError):
            restore.apply(self.args, [], [self.e])
        self.assertFalse(restore.safe_path(self.e['path']).exists())

    def test_private_native_module_and_manifest_restore_outside_content(self):
        plugin = 'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18/Binaries/Win64/'
        records = [{**self.e, 'path': plugin + name,
            'remote_path': '/objects/sha256/' + self.e['sha256'][:2] + '/' + self.e['sha256']}
            for name in ('UnrealEditor-ParisGripBindingV18.dll', 'UnrealEditor.modules')]
        restore.apply(self.args, [], records)
        self.assertTrue(all(restore.same(restore.safe_path(e['path']), e) for e in records))
        self.assertFalse((restore.STAGE / self.e['sha256']).exists())

    def test_manifest_hash_and_duplicate_paths_rejected(self):
        sync = restore.ROOT / 'Assets/Sync'
        sync.mkdir(parents=True)
        catalog = {'active_manifests': []}
        for aid in restore.ASSETS:
            p = sync / (aid + '.json')
            m = {'asset_id': aid, 'asset_version': 'test', 'files': [self.e]}
            p.write_text(json.dumps(m), encoding='utf-8')
            catalog['active_manifests'].append({'asset_id': aid, 'asset_version': 'test',
                'path': p.relative_to(restore.ROOT).as_posix(), 'sha256': restore.sha(p)})
        (sync / 'CATALOG.json').write_text(json.dumps(catalog), encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'Conflicting'):
            restore.entries()
        p.write_text('tampered', encoding='utf-8')
        # Tamper first manifest to fail before duplicate owner detection.
        (sync / (restore.ASSETS[0] + '.json')).write_text('tampered', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'hash'):
            restore.entries()

if __name__ == '__main__':
    unittest.main()
