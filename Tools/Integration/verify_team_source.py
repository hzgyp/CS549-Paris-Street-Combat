"""Check selected team source; normal Git CRLF conversion is allowed."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'Assets/Sync/TEAM_SOURCE_CONTRACT_20261008.json'


def text_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def verify_source():
    data = json.loads(CONTRACT.read_text(encoding='utf-8-sig'))
    for entry in data['files']:
        path = ROOT / entry['path']
        if not path.resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('Source contract path escapes checkout')
        if not path.is_file() or text_sha(path) != entry['sha256_lf']:
            raise RuntimeError('Source differs from team release: ' + entry['path'])
    return {'source_files': len(data['files']), 'asset_version': data['asset_version'],
            'normalization': 'CRLF to LF only'}


def write_contract():
    paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT)
    selected = sorted({p.decode('utf-8') for p in paths.split(b'\0') if p and
        p.decode('utf-8').startswith(('Unreal/ParisStreetCombat/Plugins/',
            'Unreal/ParisStreetCombat/Config/', 'Unreal/ParisStreetCombat/Source/', 'Tools/Integration/'))})
    selected.append('Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')
    files = [{'path': p, 'sha256_lf': text_sha(ROOT / p)} for p in selected if (ROOT / p).is_file()]
    CONTRACT.write_text(json.dumps({'schema_version': 1,
        'asset_version': 'paris-native-playtest-20261008-g1-npc-vfx-v1',
        'normalization': 'CRLF to LF only; preserves all other bytes',
        'scope': 'Runtime/plugin configuration and integration source; other files selected by matching Git revision',
        'files': files}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(verify_source()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Release owner only: record current source; does not publish')
    if parser.parse_args().write:
        write_contract()
    else:
        print(json.dumps(verify_source()))
