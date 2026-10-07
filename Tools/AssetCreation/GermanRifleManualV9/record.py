"""Freeze private V9 partial work metadata after actual final evidence review."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9';DEST=ROOT/'Assets/Integration/GERMAN_RIFLE_MANUAL_INVENTORY_20261003.json'
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args()
if a.verify:
    d=json.loads(DEST.read_text());bad=[r['path'] for r in d['files']+d['source_files'] if not (ROOT/r['path']).is_file() or row(ROOT/r['path'])!=r];print(json.dumps({'files':len(d['files']),'sources':len(d['source_files']),'mismatches':bad}));assert not bad
else:
    assert not DEST.exists();audit=json.loads((BASE/'front_audit_v1/audit.json').read_text());assert audit['all_pass']
    names=['whole_right','whole_left','whole_top','whole_bottom','muzzle','muzzle_reverse','muzzle_top','muzzle_right']
    reviewed=[BASE/'barrel_v1'/f'{n}.png' for n in ('muzzle','muzzle_top','muzzle_reverse','whole_right')]
    reviewed += [BASE/d/f'{n}.png' for d in ('front_gray_v2','front_finish_v1') for n in names]
    reviewed += [BASE/'front_audit_v1'/f'fresh_{n}.png' for n in ('whole_right','whole_left','whole_top','whole_bottom','quarter','reverse','top_detail','muzzle')]
    assert len(reviewed)==28 and all(p.is_file() for p in reviewed)
    assert json.loads((BASE/'protected_after.json').read_text())['allPass']
    old=json.loads((ROOT/'Assets/Integration/GERMAN_RIFLE_TOPOLOGY_INVENTORY_20261003.json').read_text());assert all(row(ROOT/r['path'])==r for r in old['files']+old['source_files'])
    d={'date':'2026-10-03','status':'partial_joined_front_verified_receiver_skin_stopped_not_selected','purpose':'Private LocalWorking experiment, NOT SFTP/Catalog/production/teammate restore authority','plan':'Docs/Development/GERMAN_RIFLE_MANUAL_V9.md','result':'Docs/Development/GERMAN_RIFLE_MANUAL_RESULT_20261003.md','failure_case':'Failures/GP008-20261003-kar98k-manual-skin/FAILURE_ANALYSIS.md','cloud_calls':0,'credits_spent':0,'ue_or_m1_changes':False,'native_files_guarded':50,'prior_private_files_guarded':414,'prior_source_files_guarded':59,'m1_reference_files_guarded':4,'triangles':audit['triangles'],'meshes':audit['fresh_import_meshes'],'candidate':(BASE/'front_finish_v1/Kar98k_ManualFront_V9.glb').relative_to(ROOT).as_posix(),'glb_sha256':audit['glb_sha256'],'clean_rebuild_glb_byte_exact':True,'generated_pngs':len(list(BASE.rglob('*.png'))),'actual_reviewed_pngs':len(reviewed),'actual_reviewed_png_paths':[p.relative_to(ROOT).as_posix() for p in reviewed],'files':[row(f) for f in sorted(BASE.rglob('*')) if f.is_file() and '__pycache__' not in f.parts],'source_files':[row(f) for f in sorted(Path(__file__).resolve().parent.iterdir()) if f.is_file()]}
    DEST.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps({'files':len(d['files']),'sources':len(d['source_files']),'generated_pngs':d['generated_pngs'],'reviewed_pngs':len(reviewed)}))
