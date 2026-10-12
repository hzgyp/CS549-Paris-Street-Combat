"""Bounded read-only supplier filename inventory; absence is not full semantic proof."""
from pathlib import Path
import json,collections
from prepare import ROOT,OUT,sha,load
def main():
    original=ROOT/'Assets/LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1'
    assert original.exists()
    terms=['reload','aim','m1_garand','magazine','enbloc','clip','bolt']
    found={x:[] for x in terms}
    files=[p for p in original.rglob('*') if p.is_file()]
    for p in files:
        for term in terms:
            if term in p.name.lower():found[term].append(dict(path=p.relative_to(ROOT).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)))
    p1=load(ROOT/'tmp/g1-team-feedback-p1-20261010/checks/ammo_v4/RESULT.json')
    r=dict(status='read_only_supplier_inventory_complete',original_files=len(files),counts={x:len(v) for x,v in found.items()},matches=found,current_native_ready_assets=p1['ready_assets'],current_native_reload_assets=p1['reload_assets'],source_receipt_sha256=sha(ROOT/'tmp/g1-team-feedback-p1-20261010/checks/ammo_v4/RESULT.json'),limitations='Filename inventory and unchanged prior runtime inventory; no new UE skeletal or complete visual acceptance. No absent-name inference about unnamed embedded parts.')
    dst=OUT/'supplier_inventory.json';assert not dst.exists();dst.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=r['status'],original_files=len(files),counts=r['counts'],reload_names=[Path(x['path']).stem for x in found['reload']]),ensure_ascii=False))
if __name__=='__main__':main()
