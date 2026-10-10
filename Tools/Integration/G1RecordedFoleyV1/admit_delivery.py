"""Admit the occupied trial only after exact launcher recovery and independent checks."""
import json
from pathlib import Path
from intake import ROOT,OUT,digest,save_json,row
from deliver import finish

prepared=json.loads((OUT/'candidate_v1/prepare.json').read_text('utf-8'))
build=json.loads((OUT/'candidate_v1/build.json').read_text('utf-8-sig'))
assert json.loads((OUT/'delivery_launcher_failure/recovery.json').read_text('utf-8'))['status']=='restored_exact_parent_launcher_and_detached_mutable_candidate_links'
parent=Path(prepared['reuse_archive']);archive=OUT/'candidate_v1/Archive';trial=ROOT/'tmp/Playtest-G1-Foley-20261009'
for r in prepared['archive_files']:
    assert digest(parent/r['path'])==r['sha256'],('Parent closure drift',r['path'])
    if r['path'].endswith('/Binaries/Win64/WW2FranceLiberation.exe'):expected=build['game_sha256']
    else:expected=r['sha256']
    assert digest(archive/r['path'])==expected
    if r['path']!='PLAY_G1_REVISION.cmd':assert digest(trial/r['path'])==expected
variant=ROOT/'Unreal/Variants/G1RecordedFoley20261009';source=variant/'Project';working=Path(prepared['project'])
for r in prepared['source_files']:
    for base in [source,working]:assert digest(base/r['path'])==r['sha256']
assert len([p for p in source.rglob('*') if p.is_file()])==42
for r in json.loads((variant/'AUDIO_MANIFEST.json').read_text('utf-8'))['files']:
    for base in [OUT/'candidate_v1/Audio',archive/'Windows/WW2FranceLiberation/Audio',trial/'Windows/WW2FranceLiberation/Audio']:
        assert digest(base/r['path'])==r['sha256']
assert trial.joinpath('PLAY_G1_REVISION.cmd').stat().st_nlink==1 and archive.joinpath('PLAY_G1_REVISION.cmd').stat().st_nlink==1
finish(trial,variant,source,working,prepared,build)
save_json(OUT/'admission.json',dict(status='pass_exact_source_audio_parent_closure_and_independent_launchers',source_files=42,normal_trial_files=91,
    original_parent_archive_files=len(prepared['archive_files']),recording_hold=True,recovery='delivery_launcher_failure/recovery.json',
    scope='No rerun of occupied delivery; no new Game test or OBS recording; existing compiled/game-playback identities exact'))
print('Independent91-file review trial admitted; parent archive closure/source/audio exact; human review pending')
