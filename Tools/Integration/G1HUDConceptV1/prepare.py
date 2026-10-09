"""Freeze V10; admit one private rendering-only cpp and licensed UI sidecars."""
import json,shutil,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
BASE=ROOT/'tmp/g1-playtest-revision-20261008'
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
CPP='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp'

def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)

def expected(source):
    start=source.index('void AParisBridgeHUD::DrawHUD()\n')
    end=source.index('\nnamespace ParisPronePrediction\n',start)
    result=source[:start]+(HERE/'HUD.inc').read_text(encoding='utf-8').rstrip()+'\n'+source[end:]
    result=once(result,'#include "Misc/Paths.h"\n','#include "Misc/Paths.h"\n#include "CanvasItem.h"\n#include "Fonts/CompositeFont.h"\n#include "Fonts/SlateFontInfo.h"\n#include "GlobalRenderResources.h"\n')
    result=once(result,'DrawDebugCircle(GetWorld(),BridgeheadFeet+FVector(0,0,7),CheckpointRadius,64,FColor(145,225,111),false,-1,0,5,FVector(1,0,0),FVector(0,1,0),false);',
        'DrawDebugCircle(GetWorld(),BridgeheadFeet+FVector(0,0,7),CheckpointRadius,128,FColor(202,171,105),false,-1,0,1.25,FVector(1,0,0),FVector(0,1,0),false);')
    for old,new in [('Enter the green checkpoint circle','Enter the gold checkpoint circle'),('enter the green checkpoint circle','enter the gold checkpoint circle')]:
        if old in result:result=result.replace(old,new)
    return result

def main():
    old=BASE/'candidate_v10';out=BASE/'hud_v1';assert not out.exists()
    previous=json.loads((old/'prepare_revision.json').read_text())
    built=json.loads((old/'build_revision.json').read_text(encoding='utf-8-sig'))
    project=Path(previous['project']);frozen=old/'FrozenSource';assert not frozen.exists()
    assert verify_source()['source_files']==758
    guards=guard_rows();assert len(guards)==703 and guards_match(guards)
    native=json.loads((ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json').read_text())
    assert len(native['files'])==359
    for r in native['files']:assert digest(ROOT/r['path'])==r['sha256']
    descriptor=project/'WW2FranceLiberation.uproject';assert digest(descriptor)==previous['descriptor_sha256']
    for r in previous['private_source_files']:assert digest(project/r['path'])==r['sha256']
    archive=old/'Archive';archive_rows=[]
    for f in sorted(archive.rglob('*')):
        if f.is_file():archive_rows.append(dict(path=f.relative_to(archive).as_posix(),size_bytes=f.stat().st_size,sha256=digest(f)))
    assert len(archive_rows)==44 and digest(archive/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==built['game_sha256']
    for r in previous['cooked_files']:assert digest(project/'Saved/Cooked/Windows'/r['path'])==r['sha256']
    assets=ROOT/'tmp/g1-hud-concept-20261009/Assets';font=(assets/'Cinzel.ttf').read_bytes()
    assert font[:4]==b'\x00\x01\x00\x00'
    count=struct.unpack('>H',font[4:6])[0]
    tags={font[12+16*i:16+16*i] for i in range(count)}
    assert {b'name',b'cmap',b'glyf',b'fvar'}<=tags and 'SIL OPEN FONT LICENSE' in (assets/'Cinzel-OFL.txt').read_text()
    assert 'Cinzel'.encode('utf-16-be') in font
    for r in previous['private_source_files']:
        dst=frozen/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(project/r['path'],dst)
    shutil.copyfile(descriptor,frozen/descriptor.name)
    evidence=STORE/'Evidence/G1HUDConceptV1/reference';evidence.mkdir(parents=True,exist_ok=False)
    concept=Path('C:/Users/hzgyp/.codex/generated_images/01a0ffda-767d-75a1-89b9-cece3671d966/exec-87544f5d-3766-42bf-aec8-563b5ef851b4.png')
    shutil.copyfile(concept,evidence/'approved_concept.png')
    failed=STORE/'Evidence/Failures/MI013/rejected_v10';failed.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(frozen/CPP,failed/'ParisBridgeMission.cpp')
    shutil.copyfile(ROOT/'Tools/Integration/G1PlaytestRevisionV1/RevisionHUD.inc',failed/'RevisionHUD.inc')
    for identity,name in [('plain_small_v10','ready.png'),('checkpoint_v5','checkpoint_prompt.png')]:
        shutil.copyfile(BASE/identity/name,failed/(identity+'_'+name))
    failure_rows=[dict(path=f.name,size_bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(failed.iterdir())]
    (failed/'MANIFEST.json').write_text(json.dumps(dict(scope='Rejected presentation only; functional V10/archive/user checkpoints preserved',files=failure_rows),indent=2)+'\n')
    source=(frozen/CPP).read_text(encoding='utf-8');new=expected(source)
    (project/CPP).write_text(new,encoding='utf-8')
    changed=[Path(r['path']).as_posix() for r in previous['private_source_files'] if digest(project/r['path'])!=r['sha256']]
    assert changed==[CPP] and (project/CPP).read_text(encoding='utf-8')==expected(source)
    out.mkdir();shutil.copytree(old/'UI',out/'UI')
    for name in ['Cinzel.ttf','Cinzel-OFL.txt']:shutil.copyfile(assets/name,out/'UI'/name)
    provenance=dict(family='Cinzel',modified=False,license='SIL Open Font License 1.1',
        font_source='https://raw.githubusercontent.com/google/fonts/main/ofl/cinzel/Cinzel%5Bwght%5D.ttf',
        license_source='https://raw.githubusercontent.com/google/fonts/main/ofl/cinzel/OFL.txt',
        font_sha256=digest(out/'UI/Cinzel.ttf'),license_sha256=digest(out/'UI/Cinzel-OFL.txt'))
    (out/'UI/Cinzel-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    result=dict(previous,identity='hud_v1',observer_only_game_build=False,private_method_only_game_build=True,
        reuse_archive=str(archive),archive_files=archive_rows,v3_game_sha256=built['game_sha256'],changed_implementation_paths=changed,
        reuse_scope='One private cpp rendering-only HUD/includes/ring/colour wording change; all other source, headers/defaults/schema/config/observer/assets/cooked payload exact. No recook. Licensed font sidecars only.',
        save_schema_config_and_nonrender_policy_exact=True,protected_files=guards,
        approved_concept_sha256=digest(evidence/'approved_concept.png'),font=provenance,
        private_source_files=[dict(r,sha256=digest(project/r['path'])) for r in previous['private_source_files']])
    (out/'prepare_revision.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status='prepared_runtime_unverified',identity='hud_v1',changed=changed,font=provenance['font_sha256']),indent=2))
if __name__=='__main__':main()
