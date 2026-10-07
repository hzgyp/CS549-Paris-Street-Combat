"""Non-secret, non-selected split candidate inventory; preserve every old byte."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3'
DEST=ROOT/'Assets/Integration/GERMAN_RIFLE_PART_SPLIT_INVENTORY_20261003.json'
def entry(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':h.hexdigest()}
if DEST.exists():raise RuntimeError('Preserve occupied inventory')
previous=[]
for name in ('GERMAN_RIFLE_PILOT_INVENTORY_20261003.json','GERMAN_RIFLE_REFINEMENT_INVENTORY_20261003.json'):
    m=json.loads((ROOT/'Assets/Integration'/name).read_text())
    records=m['files']+m['source_files']
    bad=[r['path'] for r in records if entry(ROOT/r['path'])!=r]
    if bad:raise RuntimeError('Previous byte differences: '+str(bad))
    previous.append({'manifest':name,'verifiedFiles':len(m['files']),'verifiedSources':len(m['source_files'])})
guards=[json.loads((STORE/n).read_text()) for n in ('protected_before.json','protected_after.json')]
assert all(g['all_pass'] for g in guards)
task=json.loads((STORE/'api-state/task.json').read_text())
audit=json.loads((STORE/'evidence/part_audit/audit.json').read_text())
partition=json.loads((STORE/'evidence/full_partition_check.json').read_text())
reproduced=[]
for name in ('audit.json','colored_right.png','colored_top.png','colored_quarter.png','isolated_part_0.png','isolated_part_1.png'):
    x=entry(STORE/'evidence/part_audit'/name);y=entry(STORE/'evidence/part_audit_reproduced'/name)
    item={'file':name,'shaIdentical':x['sha256']==y['sha256']}
    if name.endswith('.png'):
        with Image.open(STORE/'evidence/part_audit'/name) as first,Image.open(STORE/'evidence/part_audit_reproduced'/name) as second:
            diff=ImageChops.difference(first.convert('RGB'),second.convert('RGB'))
            item.update(pixelsExact=diff.getbbox() is None,maxChannelDelta=max(x[1] for x in diff.getextrema()))
    reproduced.append(item)
assert reproduced[0]['shaIdentical']
print(json.dumps({'diagnosticReproduction':reproduced}))
data={'schema_version':1,'date':'2026-10-03','owner':'yg745','status':'local_semantic_split_diagnostic',
      'restoration_authority':'None; not Catalog/SFTP/native or production selection',
      'taskId':task['taskId'],'submittedTasks':1,'giftDebit':task['actualDebit'],
      'giftBalanceAfter':task['balanceAfter'],'reservedGiftCredits':40,'paidTopUp':False,
      'quoteApi':'PRICING_ITEM_NOT_QUOTABLE; official pricing page observed30/40 before submit',
      'sourceSha256':audit['originalSha256'],'resultSha256':audit['sourceSha256'],
      'partCount':len(audit['parts']),'triangles':audit['resultTriangles'],
      'partsObserved':['Entire rifle including wood/metal/bolt/sights','Sling'],
      'usefulWoodMetalBoltSeparationPassed':False,'allFacesAndCornerUvsExact':partition['allFacePositionsWindingAndCornerUvsExact'],
      'packedImagesExact':partition['packedImagesExact'],'initialImagesActuallyInspected':15,
      'diagnosticReproduction':reproduced,
      'production_visual_pass':False,'previousBytesVerified':previous,'nativeGuards':guards,
      'sensitive_state_excluded':True,
      'files':[entry(p) for p in sorted(STORE.rglob('*')) if p.is_file() and 'api-state' not in p.relative_to(STORE).parts],
      'source_files':[entry(p) for p in sorted(Path(__file__).parent.glob('*.py'))]}
DEST.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({'manifest':str(DEST),'files':len(data['files']),'previousBytesUnchanged':True,
                  'nativeUnchanged':True,'parts':data['partCount'],'debit':data['giftDebit']}))
