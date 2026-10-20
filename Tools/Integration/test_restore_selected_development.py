"""Filesystem safety gates for the selected private-resource restore tool."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('selected_restore', Path(__file__).with_name('restore_selected_development.py'))
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)


def item(path, raw):
    return dict(path=path, size_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), remote_path='/objects/sha256/ab/example')


class SafetyTests(unittest.TestCase):
    def test_rejects_escape_and_command_injection(self):
        for value in ('../x', '/x', 'C:/x', 'a/../../x', 'a\\x', 'a\nx', 'a"x', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                restore.relative(value)

    def test_no_placement_occurs_before_conflict_scan_finishes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root/'cache';cache.mkdir()
            rows = [item('map/a.png', b'a'), item('map/b.png', b'b')]
            for r, raw in zip(rows, (b'a', b'b')):
                (cache/r['sha256']).write_bytes(raw)
            (root/'map').mkdir();(root/'map/b.png').write_bytes(b'human edit')
            manifests = {'paris-npc-survey-rasters': {'files': rows}}
            with self.assertRaises(RuntimeError):
                restore.apply_or_verify(root, cache, manifests, 'npc')
            self.assertFalse((root/'map/a.png').exists())
            self.assertEqual((root/'map/b.png').read_bytes(), b'human edit')

    def test_verified_restore_is_repeatable_and_does_not_change_original_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);cache=root/'cache';cache.mkdir()
            r = item('map/a.png', b'a');(cache/r['sha256']).write_bytes(b'a')
            m = {'paris-npc-survey-rasters': {'files': [r]}}
            self.assertEqual(restore.apply_or_verify(root, cache, m, 'npc'), 1)
            self.assertEqual(restore.apply_or_verify(root, cache, m, 'npc', verify=True), 1)
            self.assertEqual(restore.apply_or_verify(root, cache, m, 'npc'), 1)
            self.assertNotEqual((root/r['path']).stat().st_ino, (cache/r['sha256']).stat().st_ino)

    def test_refuses_missing_or_changed_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);cache=root/'cache';cache.mkdir()
            r=item('map/a.png', b'a');(cache/r['sha256']).write_bytes(b'changed')
            with self.assertRaises(RuntimeError):
                restore.apply_or_verify(root, cache, {'paris-npc-survey-rasters': {'files': [r]}}, 'npc')
            self.assertFalse((root/r['path']).exists())

    def test_link_traversal_is_rejected_even_within_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'real').mkdir()
            try:
                (root/'alias').symlink_to(root/'real', target_is_directory=True)
            except OSError:
                self.skipTest('Host does not permit symlinks')
            with self.assertRaises(ValueError):
                restore.inside(root, 'alias/a')

    def test_source_restore_excludes_parent_editor_binaries_and_overlays_content(self):
        city=item('Unreal/ParisStreetCombat/Content/map.uasset', b'city')
        old=item('Unreal/ParisStreetCombat/Plugins/Test/Binaries/Win64/UnrealEditor.dll', b'old dll')
        new={**item('private/map.uasset', b'new'), 'restore_path': 'Content/map.uasset'}
        m={'france-liberation-content': {'files':[city]}, 'paris-gameplay-native-playtest': {'files':[old]},
           'character-ue582-integration-baseline': {'files':[]}, 'rifle-pro-mocap-ue582-selected': {'files':[]},
           'paris-tutorial-native-overlay': {'files':[new]}, 'paris-tutorial-runtime-resources': {'files':[]}}
        out=restore.mapping(m,'tutorial-source')
        self.assertEqual(len(out), 1)
        self.assertEqual(next(iter(out.values()))['sha256'], new['sha256'])

    def test_selected_engine_integration_clips_are_included_without_original_intake(self):
        integrated=item('Assets/LocalShared/SFTP/workspaces/team/Content/Rifle/Prone.uasset', b'UE582')
        original=item('Original/Content/Rifle/Prone.uasset', b'UE4')
        m={k:{'files':[]} for k in ('france-liberation-content','paris-gameplay-native-playtest',
             'character-ue582-integration-baseline','rifle-pro-mocap-ue582-selected',
             'paris-tutorial-native-overlay','paris-tutorial-runtime-resources')}
        m['rifle-pro-mocap-ue582-selected']['files']=[integrated]
        m['rifle-animset-pro-original']={'files':[original]}
        result=restore.mapping(m,'tutorial-source')
        self.assertEqual(len(result),1)
        self.assertEqual(next(iter(result.values()))['sha256'], integrated['sha256'])

    def test_manifest_hash_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);base=root/'Assets/Sync';base.mkdir(parents=True)
            (base/'manifest.json').write_text('{}', encoding='utf-8')
            (base/'CATALOG.json').write_text(json.dumps({'active_manifests':[{'asset_id':'paris-npc-survey-rasters', 'path':'Assets/Sync/manifest.json', 'sha256':'0'*64}]}),encoding='utf-8')
            with self.assertRaises(ValueError):restore.selected(root,'npc')

    def test_wrong_source_manifest_in_otherwise_readable_zip_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);cache=root/'cache';cache.mkdir();p=cache/'archive.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('SOURCE_MANIFEST.json','{"files":[]}')
            r=item('archive.zip',p.read_bytes());r['restore_path']='Matching-Source-145.zip'
            p.rename(cache/r['sha256']);(root/'Assets/Sync').mkdir(parents=True)
            (root/'Assets/Sync/TUTORIAL_SOURCE_CONTRACT_20261017.json').write_text(json.dumps({'source_manifest_sha256':'0'*64}),encoding='utf-8')
            with self.assertRaises(ValueError):restore.zipped_files(root,cache,{'paris-tutorial-runtime-resources':{'files':[r]}},'tutorial-source')


if __name__=='__main__':
    unittest.main()
