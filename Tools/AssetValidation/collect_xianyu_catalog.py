"""Collect local delivery facts and archive headers without extraction or secrets."""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog'
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tmp/weapon-intake-20261001/pydeps'))
import py7zr

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()
report={'date':'2026-10-03','scope':'Local delivery/previous native facts; archive listing does not establish runtime validation.',
        'deliveries':[],'archives':[]}
char=load('Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/FinalInventory/ue_load_inventory.json')['assets']
weap=load('Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1/Evidence/ue_load_inventory.json')['assets']
for key,mount,assets,manifest in [
    ('german','GermanSoldier',char,'german-soldier-original'),
    ('us','USParatrooper',char,'us-paratrooper-original'),
    ('rifle_old','RifleAnimsetPro',char,'rifle-animset-pro-original'),
    ('d059','Rifle_01',weap,'rifle-pro-mocap-original'),
    ('arms','ShooterStarter',weap,None)]:
    subset=[x for x in assets if x['path'].startswith('/Game/'+mount+'/')]
    entry={'key':key,'mount':mount,'classes':dict(collections.Counter(x['class'] for x in subset)),
           'assets':subset,'inventory_basis':'Prior real UE load; fresh file presence checked separately this turn'}
    if manifest:
        m=load('Assets/Sync/manifests/'+manifest+'.json')
        entry['original_files']=len(m['files']);entry['original_bytes']=sum(x['size_bytes'] for x in m['files'])
        entry['present']=sum((ROOT/x['path']).is_file() and (ROOT/x['path']).stat().st_size==x['size_bytes'] for x in m['files'])
    else:
        base=ROOT/'Assets/LocalWorking/Intake/2026-10-01/01_ShooterStarter_FPS_Arm_A'
        files=[x for x in base.rglob('*') if x.is_file()]
        entry.update(original_files=len(files),original_bytes=sum(x.stat().st_size for x in files),present=len(files))
    report['deliveries'].append(entry)
    print(json.dumps({'delivery':key,'classes':entry['classes'],'files':entry['original_files'],'present':entry['present']}),flush=True)

base=ROOT/'Assets/LocalWorking/Intake/2026-10-01/03_UE4_Animation_Collection'
for path in sorted(base.rglob('*.7z')):
    password=None
    for parent in path.parents:
        match=re.search(r'(?:解压密码|密码|password|pwd)\s*[:：=]?\s*(.+)$',parent.name,re.I)
        if match: password=match.group(1).strip();break
        if parent==base:break
    row={'title':path.name,'compressed_bytes':path.stat().st_size,
         'preview_files':[x.name for x in path.parent.iterdir() if x.is_file() and x.stem==path.stem and x.suffix.lower() in ('.png','.jpg','.jpeg')]}
    try:
        with py7zr.SevenZipFile(path,mode='r',password=password) as archive:
            infos=[x for x in archive.list() if not x.is_directory]
            names=[x.filename for x in infos]
            row.update(member_count=len(names),expanded_bytes=sum(x.uncompressed or 0 for x in infos),
                       extensions=dict(collections.Counter(Path(x).suffix.lower() for x in names)),
                       native_files=[x for x in names if Path(x).suffix.lower() in ('.uasset','.umap','.uexp','.ubulk')],
                       other_formats=dict(collections.Counter(Path(x).suffix.lower() for x in names if Path(x).suffix.lower() in ('.fbx','.ma','.mb','.blend','.bvh','.obj'))),
                       top_folders=sorted({x.replace('\\','/').split('/')[0] for x in names}),
                       unsafe_paths=any('..' in Path(x.replace('\\','/')).parts or x.startswith(('/', '\\')) or ':' in x for x in names),
                       status='header_listed_not_extracted_or_runtime_tested')
    except Exception as exc:row.update(status='header_failed',error_type=type(exc).__name__)
    report['archives'].append(row)
    (OUT/'catalog_facts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'archive':path.name,'members':row.get('member_count'),'status':row['status']},ensure_ascii=True),flush=True)
blend=ROOT/'Assets/LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library/MW2_Guns_Asset_Library.blend'
stat=blend.stat();report['gun_source']={'name':blend.name,'size_bytes':stat.st_size,'sha256':digest(blend),'mtime_ns':stat.st_mtime_ns}
assert (stat.st_size,stat.st_mtime_ns)==(blend.stat().st_size,blend.stat().st_mtime_ns)
(OUT/'catalog_facts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'archives':len(report['archives']),'failed':sum(x['status']=='header_failed' for x in report['archives']),'gun_sha256':report['gun_source']['sha256']}),flush=True)
