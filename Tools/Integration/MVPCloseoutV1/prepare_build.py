"""Create an isolated G1 cook wrapper; never resave selected native inputs."""
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Integration/NPCInteractionV1'))
from common import digest, guard_rows, guards_match
sys.path.insert(0, str(ROOT / 'Tools/Integration'))
from verify_team_source import verify_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identity')
    args = parser.parse_args()
    if not args.identity.replace('_', '').replace('-', '').isalnum():
        raise ValueError('Invalid identity')
    out = ROOT / 'tmp/mvp-closeout-20261008' / args.identity
    if out.exists():
        raise RuntimeError('Preserve occupied identity')
    rows = guard_rows()
    assert len(rows) == 703 and guards_match(rows), 'Current protected epoch differs'
    source = verify_source()
    manifest = json.loads((ROOT / 'Assets/Sync/manifests/paris-gameplay-native-playtest.json').read_text())
    for row in manifest['files']:
        path = ROOT / row['path']
        assert path.stat().st_size == row['size_bytes'] and digest(path) == row['sha256'], str(path)
    original = ROOT / 'Unreal/ParisStreetCombat'
    project = out / 'Project'
    project.mkdir(parents=True)
    shutil.copytree(original / 'Config', project / 'Config')
    selected = ['ParisGripBindingV18', 'ParisNPCGripV15', 'ParisBridgeMissionV1', 'ParisMuzzleFlashV1']
    for plugin in selected:
        shutil.copytree(original / 'Plugins' / plugin, project / 'Plugins' / plugin,
                        ignore=shutil.ignore_patterns('Intermediate', 'Saved', '.git'))
    subprocess.run(['cmd', '/c', 'mklink', '/J', str(project / 'Content'),
                    str((original / 'Content').resolve())], check=True, capture_output=True)
    descriptor = json.loads((original / 'WW2FranceLiberation.uproject').read_text())
    descriptor['Plugins'].append({'Name': 'ParisBridgeMissionV1', 'Enabled': True})
    (project / 'WW2FranceLiberation.uproject').write_text(json.dumps(descriptor, indent=2)+'\n')
    engine = project / 'Config/DefaultEngine.ini'
    engine.write_text(engine.read_text().replace('/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1',
                                                '/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1'))
    game = project / 'Config/DefaultGame.ini'
    game.write_text(game.read_text().replace('/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1',
                                            '/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1') +
                    '\n+DirectoriesToAlwaysCook=(Path="/Game/ParisCombat/VFX/MuzzleFlashV1")\n'
                    '+DirectoriesToAlwaysCook=(Path="/Game/RifleAnimsetPro/Animations/InPlace")\n')
    receipt = dict(identity=args.identity, baseline_revision=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), source=source,
        native_version=manifest['asset_version'], selected_native_files=len(manifest['files']),
        protected_files=rows, source_wrapper=str(project),
        entry='/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1',
        scope='Isolated private G1 Development package; no runtime/MVP acceptance yet',
        wrapper_files=[dict(path=str(p.relative_to(project)), sha256=digest(p))
                       for p in sorted(project.rglob('*')) if p.is_file() and 'Content' not in p.relative_to(project).parts])
    (out / 'prepare.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('protected_files','wrapper_files')}))


if __name__ == '__main__':
    main()
