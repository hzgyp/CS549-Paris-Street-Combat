"""Freeze the rejected references and acquire licensed published Foley references."""
import hashlib,json,re,shutil,urllib.request,zipfile
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/g1-recorded-foley-20261009'
PY=Path(__file__)

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save_json(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n','utf-8')
def row(p,base):return dict(path=p.relative_to(base).as_posix(),size_bytes=p.stat().st_size,sha256=digest(p))
def fetch(url,path):
    if path.exists():return path.read_bytes()
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; ParisStreetCombat Foley Reference)'})
    with urllib.request.urlopen(req,timeout=30) as r:data=r.read()
    path.write_bytes(data);return data

def freeze():
    if (OUT/'freeze.json').exists():return
    OUT.mkdir(parents=True,exist_ok=True)
    selector=json.loads((ROOT/'Docs/Development/CURRENT_LOCAL_REPAIR.json').read_text('utf-8-sig'))
    manifest=ROOT/selector['source_manifest']
    assert digest(manifest)==selector['source_manifest_sha256']
    source=ROOT/selector['source_snapshot']
    for r in json.loads(manifest.read_text('utf-8-sig'))['files']:
        assert digest(source/r['path'])==r['sha256']
    game=ROOT/'tmp/Playtest-G1-AV-20261009/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert digest(game)==selector['game_sha256']
    failed=OUT/'rejected_avv3';failed.mkdir()
    shutil.copytree(ROOT/'tmp/Playtest-G1-AV-20261009/Windows/WW2FranceLiberation/Audio',failed/'Audio')
    shutil.copytree(ROOT/'Tools/Integration/G1PresentationAVV1',failed/'Tools')
    module=source/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
    shutil.copyfile(module/'ParisBridgeMissionV1.cpp',failed/'observer.cpp')
    shutil.copyfile(module/'ParisGameplayAV.cpp',failed/'runtime_audio.cpp')
    files=[row(p,failed) for p in sorted(failed.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    references=[]
    for name in ['Assets/LocalShared/Deliverables/Assignment3/DemoDraft02_20261009/Paris_G1_MVP_Draft_02.mp4',
                 'tmp/g1-demo-draft02-20261009/probe/2026-10-09 19-50-56.mkv',
                 'tmp/g1-demo-draft02-20261009/probe/game.log']:
        p=ROOT/name
        if p.exists():references.append(row(p,ROOT))
    receipt=dict(at=datetime.now().astimezone().isoformat(),parent=selector,private_copies=files,
                 references=references,approved_fire=row(failed/'Audio/fire.wav',failed),
                 rejected='Footsteps and reload acoustic realism; fire approved; turn logged, no new recording',
                 recording='HOLD pending human acceptance')
    save_json(OUT/'freeze.json',receipt)
    save_json(ROOT/'Failures/MI015-20261009-audio-realism-turn/MANIFEST.json',dict(
        private_root=OUT.relative_to(ROOT).as_posix(),receipt_sha256=digest(OUT/'freeze.json'),
        retained_copies=files,references=references,approved_fire_sha256=digest(failed/'Audio/fire.wav'),
        recording_hold=True))

def acquire():
    intake=OUT/'intake';intake.mkdir(exist_ok=True);records=[]
    sources=[('m1_reload',460855,'MPierluissi'),('m1_back',460857,'MPierluissi'),
             ('m1_forward',460856,'MPierluissi'),('boots_stone',521590,'Fission9'),
             ('boots_rock_walk_run',770084,'Vrymaa'),('body_dirt',504626,'leonelmail'),
             ('coat',538930,'Federico_Casazza'),('kar98',508747,'AugustSandberg')]
    for name,identifier,author in sources:
        url=f'https://freesound.org/people/{author}/sounds/{identifier}/'
        record=dict(name=name,author=author,page=url,license='CC0-1.0',status='unverified')
        try:
            html=fetch(url,intake/(name+'.html')).decode('utf-8')
            assert 'creativecommons.org/publicdomain/zero' in html,'No CC0 link in retrieved primary page'
            matches=re.findall(r'https://cdn\.freesound\.org/previews/[^\s\"\'<>]+-hq\.(?:ogg|mp3)',html)
            assert matches,'No publicly published HQ reference in page'
            preview=matches[0].replace('&amp;','&')
            ext='.ogg' if preview.endswith('.ogg') else '.mp3'
            data=fetch(preview,intake/(name+ext))
            record.update(status='acquired_public_hq_preview_not_original_wav',media=preview,
                          local=name+ext,size_bytes=len(data),sha256=digest(intake/(name+ext)),
                          primary_html_sha256=digest(intake/(name+'.html')))
        except Exception as e:record.update(status='intake_failed_preserved',error=str(e))
        records.append(record)
        save_json(intake/'sources.json',records)
    print(json.dumps(records,ensure_ascii=False,indent=2))

if __name__=='__main__':freeze();acquire()
