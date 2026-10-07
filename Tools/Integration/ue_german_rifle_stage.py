"""One-time editor staging only. Native Blueprint owns subsequent gun transforms."""
from pathlib import Path
import unreal
from german_rifle_ue_common import ROOT, STORE, read, sha, guard


def integration_records():
    imported = read(STORE / 'Evidence/GermanRifleUEV1/import_v3/result.json')
    authored = read(STORE / 'Evidence/GermanRifleUEV1/author_v2/result.json')
    assert not imported['errors'] and imported['status'].startswith('native_import_checked')
    assert not authored['errors'] and authored['status'].startswith('saved_unselected_native')
    records = imported['native_files'] + authored['native_files']
    for row in records:
        p = ROOT / row['path']
        assert p.stat().st_size == row['size_bytes'] and sha(p) == row['sha256'], row['path']
    return imported, authored, records


def stage_german_rifles():
    guard()
    imported, authored, files = integration_records()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    soldiers = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.Character)
                and a.get_class().get_name().startswith('BP_PCParis')
                and a.get_editor_property('TeamId') == 1]
    assert len(soldiers) == 3, [a.get_actor_label() for a in soldiers]
    r = []
    for soldier in soldiers:
        assert soldier.get_editor_property('TeamId') == 1
        assert soldier.get_editor_property('WeaponAppearance') is None, 'Do not replace unique equipped work'
        gun = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(authored['package']), soldier.get_actor_location(), unreal.Rotator())
        assert gun
        gun.set_actor_label('PC_GermanRifleUETrial_' + soldier.get_actor_label())
        gun.set_editor_property('Combatant', soldier)
        gun.set_editor_property('GripMesh', soldier.mesh)
        gun.set_owner(soldier)
        gun.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        assert gun.attach_to_component(soldier.mesh, 'hand_r', unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
        soldier.set_editor_property('WeaponAppearance', gun)
        r.append({'soldier': soldier.get_actor_label(), 'gun': gun.get_actor_label(),
                  'mesh': imported['mesh'], 'action_state': str(soldier.get_editor_property('ActionState'))})
    return {'new_german_weapons': r, 'native_files': files, 'map_saved': False}
