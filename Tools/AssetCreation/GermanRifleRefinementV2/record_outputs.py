"""Hash-only unselected refinement inventory; verifies previous pilot untouched."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
store=root/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2'
dest=root/'Assets/Integration/GERMAN_RIFLE_REFINEMENT_INVENTORY_20261003.json'
if dest.exists():raise RuntimeError('Preserve occupied inventory')
def entry(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return {'path':p.relative_to(root).as_posix(),'size_bytes':p.stat().st_size,'sha256':h.hexdigest()}
old=json.loads((root/'Assets/Integration/GERMAN_RIFLE_PILOT_INVENTORY_20261003.json').read_text())
old_bad=[r['path'] for r in old['files']+old['source_files'] if entry(root/r['path'])!=r]
if old_bad:raise RuntimeError('Previous pilot changed: '+str(old_bad))
guards=[json.loads((store/'evidence'/n).read_text()) for n in ('protected_before.json','protected_after.json')]
assert all(g['all_pass'] for g in guards)
validation=json.loads((store/'evidence/final_v3/validation.json').read_text())
rep=json.loads((store/'evidence/reproduction_comparison.json').read_text())
files=[entry(p) for p in sorted(store.rglob('*')) if p.is_file()]
sources=[entry(p) for p in sorted(Path(__file__).parent.glob('*.py'))]
data={'schema_version':1,'date':'2026-10-03','status':'local_refinement_visual_gate_failed','owner':'yg745',
      'restoration_authority':'None: unselected local drafts, not CATALOG/SFTP/native restore',
      'cloud_calls_this_refinement':0,'credit_debit_this_refinement':0,'previous_pilot_files_unchanged':len(old['files']),
      'previous_pilot_sources_unchanged':len(old['source_files']),'production_visual_pass':False,'basic_export_checks_passed':sum(validation['checks'].values()),
      'triangles':validation['triangles'],'mesh_count':len(validation['parts']),'exact_glb_reproduction':rep['exactBytesEqual'],
      'different_reproduction_buffer_views':len(rep['differentBufferViews']),'protected_native_action_guards':guards,
      'source_base_sha256':'a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60',
      'limitations':['Stock cut interfaces/fins fail visual acceptance','Some exterior supports remain block-like','Overbright new steel highlights','Whole-plane hull closure stopped','No exact GLB byte reproduction','Detail master not runtime LOD','No matched bolt/reload action','Museum replacement sling/historical loadout unapproved','No UE or SFTP acceptance'],
      'files':files,'source_files':sources,'sensitive_state_excluded':True}
dest.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({'manifest':str(dest),'private_files':len(files),'sources':len(sources),'old_unchanged':True,'visual_pass':False}))
