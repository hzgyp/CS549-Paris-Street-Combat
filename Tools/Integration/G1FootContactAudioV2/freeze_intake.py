"""Freeze human-reviewed parent and acquire a genuinely recorded CC0 M1 report."""
import json,re,urllib.request,subprocess,sys,importlib.util
import wave,numpy as np
from common import ROOT,OUT,PARENT,FF,digest,save,row

def main():
    assert not (OUT/'freeze.json').exists(),'Preserve occupied attempt identity'
    OUT.mkdir(exist_ok=True)
    parent=json.loads((ROOT/'Docs/Development/CURRENT_AUDIO_REVIEW.json').read_text('utf-8-sig'))
    assert parent['candidate_id']=='g1-recorded-foley-v1-20261009'
    manifest=ROOT/parent['source_manifest'];assert digest(manifest)==parent['source_manifest_sha256']
    source=ROOT/parent['source_snapshot'];files=json.loads(manifest.read_text('utf-8-sig'))['files'];assert len(files)==42
    for r in files:assert digest(source/r['path'])==r['sha256']
    trial=ROOT/'tmp/Playtest-G1-Foley-20261009';game=trial/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert digest(game)==parent['game_sha256']
    spec=importlib.util.spec_from_file_location('npc_guard_contract',ROOT/'Tools/Integration/NPCInteractionV1/common.py')
    contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    guards=contract.guard_rows();assert len(guards)==703 and contract.guards_match(guards)
    oldaudio=PARENT/'candidate_v1/Audio'
    audio=[row(p,oldaudio) for p in sorted(oldaudio.rglob('*')) if p.is_file()];assert sum(r['path'].endswith('.wav') for r in audio)==31
    archive=PARENT/'candidate_v1/Archive'
    payload=[row(p,archive) for p in sorted(archive.rglob('*')) if p.is_file() and 'Audio' not in p.parts];assert len(payload)==47
    snapshot=OUT/'rejected_distance_helper.cpp';snapshot.write_bytes((source/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp').read_bytes())
    save(OUT/'freeze.json',dict(parent=parent,source_files=files,parent_audio=audio,reuse_archive=str(archive),archive_files=payload,protected_files=guards,
      preserved_distance_helper=row(snapshot,OUT),human_feedback='Improved Foley, player cadence mismatch and missing audible jump; actual fire replacement authorized',recording_hold=True))
    save(ROOT/'Failures/MI016-20261009-player-foot-contact-jump/MANIFEST.json',dict(private_root=OUT.relative_to(ROOT).as_posix(),freeze_sha256=digest(OUT/'freeze.json'),
      rejected_implementation=row(snapshot,OUT),parent_game_sha256=parent['game_sha256'],parent_source_manifest_sha256=parent['source_manifest_sha256'],recording_hold=True))
    intake=OUT/'intake';intake.mkdir()
    page='https://freesound.org/people/MPierluissi/sounds/460851/'
    def fetch(url,p):
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (ParisStreetCombat audio reference)'})
        with urllib.request.urlopen(req,timeout=30) as response:data=response.read()
        p.write_bytes(data);return data
    html=fetch(page,intake/'m1_live_fire.html').decode('utf-8')
    assert 'creativecommons.org/publicdomain/zero' in html
    assert 'Field recording of an M1 Garand being shot in a small room.' in html
    matches=re.findall(r'https://cdn\.freesound\.org/previews/[^\s\"\'<>]+-hq\.(?:ogg|mp3)',html);assert matches
    media=matches[0].replace('&amp;','&');local=intake/('m1_live_fire'+Path(media).suffix)
    fetch(media,local)
    decoded=intake/'m1_live_fire.wav'
    subprocess.run([str(FF),'-nostdin','-v','error','-i',str(local),'-ac','1','-ar','48000','-c:a','pcm_s16le','-bitexact',str(decoded)],check=True)
    with wave.open(str(decoded),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(48000,1,2)
        x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
    n=240;env=np.array([np.sqrt(np.mean(x[i:i+n]**2)) for i in range(0,len(x),n)])
    active=np.where(env>max(.006,float(env.max())*.15))[0];groups=[]
    for i in active:
        if not groups or i-groups[-1][-1]>16:groups.append([int(i)])
        else:groups[-1].append(int(i))
    clusters=[dict(start=g[0]*.005,end=(g[-1]+1)*.005,peak_time=(g[0]+int(np.argmax(env[g[0]:g[-1]+1])))*.005) for g in groups]
    receipt=dict(author='MPierluissi',page=page,license='CC0-1.0',media=media,local=local.name,sha256=digest(local),html_sha256=digest(intake/'m1_live_fire.html'),decoded_sha256=digest(decoded),
       source_type='Live-fire M1 Garand indoor field recording; official lossy HQ preview, not original lossless WAV',seconds=len(x)/48000,peak=float(np.abs(x).max()),clusters=clusters,
       k98='No exact freely reusable live-fire source established; keep existing German cue, explicit gap')
    save(intake/'source.json',receipt);print(json.dumps(receipt))

if __name__=='__main__':
    from pathlib import Path
    main()
