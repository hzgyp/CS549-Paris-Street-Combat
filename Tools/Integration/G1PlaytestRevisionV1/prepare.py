"""Prepare a new private G1 playtest wrapper from exact tested V13 source."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
from revise_source import revise

def main():
    p=argparse.ArgumentParser();p.add_argument('identity');a=p.parse_args()
    assert a.identity.replace('_','').isalnum()
    out=ROOT/'tmp/g1-playtest-revision-20261008'/a.identity
    assert not out.exists(),'Preserve occupied revision identity'
    source=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/delivery_v1'
    delivery=json.loads((source/'delivery_receipt.json').read_text())
    assert delivery['game_binary_sha256']=='965bf17c967d313e67e717fbd24080ab5b6093237dcf927355d387a3c111c4e3'
    assert delivery['zip_sha256']=='760dbf44028acae9486c3ff9f5883715d5cf17a1c6fe338f65f20c8caecf9d01'
    for row in delivery['source_patch_files']:
        assert digest(source/'SourcePatch'/row['path'])==row['sha256']
    assert verify_source()['source_files']==758
    rows=guard_rows();assert len(rows)==703 and guards_match(rows)
    manifest=json.loads((ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json').read_text())
    for row in manifest['files']:
        path=ROOT/row['path'];assert path.stat().st_size==row['size_bytes'] and digest(path)==row['sha256']
    inventory=json.loads((ROOT/'Assets/Integration/PLAYER_ACTIONS_DRAFT_INVENTORY_20261003.json').read_text())
    action=next(r for r in inventory['files'] if r['package'].endswith('BP_PCParisPlayerActionsV6'))
    # The dated inventory predates the user-confirmed 4 October accidental save.
    # Verify the preserved recovery receipt and today's protected epoch instead
    # of restoring old bytes or rewriting either historical inventory.
    recovery_path=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadIndexContactV6/map_recovery_v1/result.json'
    recovery=json.loads(recovery_path.read_text())
    assert recovery['status']=='formal_map_byte_exact_restored_accidental_version_backed_up'
    current=next(r for r in rows if r['path']==action['path'])
    retained=next(r for r in recovery['files'] if r['path']==action['path'])
    assert all(current[k]==retained[k] for k in ('path','sha256','size_bytes'))
    assert digest(ROOT/action['path'])==current['sha256']=='572a0d9929ad65aa6fec0b206960524979314e1591eeaec27af2e75e8f22fbe8'
    action=dict(current,package=action['package'],selection='private_candidate_only_not_formal',
                historical_inventory_sha256=action['sha256'],recovery_receipt_sha256=digest(recovery_path))
    project=out/'Project';shutil.copytree(source/'SourcePatch',project)
    subprocess.run(['cmd','/c','mklink','/J',str(project/'Content'),str((ROOT/'Unreal/ParisStreetCombat/Content').resolve())],check=True,capture_output=True)
    revise(project)
    (project/'Source/WW2FranceLiberationEditor.Target.cs').write_text('''using UnrealBuildTool;
public class WW2FranceLiberationEditorTarget : TargetRules {
 public WW2FranceLiberationEditorTarget(TargetInfo Target) : base(Target) {
  Type=TargetType.Editor; DefaultBuildSettings=BuildSettingsVersion.Latest;
  IncludeOrderVersion=EngineIncludeOrderVersion.Latest; ExtraModuleNames.Add("WW2FranceLiberation");
 }
}
''',encoding='utf-8')
    config=project/'Config/DefaultGame.ini'
    config.write_text(config.read_text(encoding='utf-8')+'\n+DirectoriesToAlwaysCook=(Path="/Game/ParisCombat/Blueprints/PlayerActionsV1")\n',encoding='utf-8')
    nav_path=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/G1MissionV1/author_v3_20261008/saved_navmesh.json'
    nav=json.loads(nav_path.read_text());assert len(nav['polygons'])==1656
    image=Image.new('RGB',(1024,1024),(23,29,27));draw=ImageDraw.Draw(image)
    bounds=[0,-25000,10000,-15000]
    rejected={(5263,-20596,140),(5491,-20691,120),(5491,-20748,140),(4940,-20748,130),(5035,-20520,150)}
    skipped=0
    for poly in nav['polygons']:
        vertices=poly['vertices_cm']
        if {tuple(round(v) for v in p) for p in vertices}==rejected:
            skipped+=1;continue
        points=[((p[0]-bounds[0])/(bounds[2]-bounds[0])*1024,(bounds[3]-p[1])/(bounds[3]-bounds[1])*1024) for p in vertices]
        draw.polygon(points,fill=(119,129,111))
    assert skipped==1,'Static map must reflect the witnessed native exclusion'
    ui=out/'UI';ui.mkdir();image.save(ui/'g1_minimap.png')
    (ui/'map_identity.json').write_text(json.dumps(dict(source=str(nav_path.relative_to(ROOT)),source_sha256=digest(nav_path),bounds_cm=bounds,polygons=1656,excluded_geometry_count=skipped,scope='G1 surveyed ground navigation, not full city elevations'),indent=2)+'\n')
    receipt=dict(status='prepared_runtime_unverified',identity=a.identity,project=str(project),
        tested_baseline_game_sha256=delivery['game_binary_sha256'],source_contract_files=758,
        protected_files=rows,selected_native_files=359,action=action,
        private_source_files=[dict(path=str(f.relative_to(project)),sha256=digest(f)) for area in ['Config','Source','Plugins'] for f in (project/area).rglob('*') if f.is_file()],
        minimap_sha256=digest(ui/'g1_minimap.png'),scope='New private UX/actions/checkpoint candidate; no canonical save or selection')
    (out/'prepare_revision.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['protected_files','private_source_files','action']},indent=2))

if __name__=='__main__':main()
