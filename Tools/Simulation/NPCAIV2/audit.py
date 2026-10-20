"""Read exact selected source/native dependencies; do not write their directories."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SELECTOR = ROOT/'Docs/Development/CURRENT_TUTORIAL_SOURCE_PENDING.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect():
    selector=json.loads(SELECTOR.read_text(encoding='utf-8-sig'))
    manifest_path=ROOT/selector['source_manifest']
    source_manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    source=[]
    for row in source_manifest['files']:
        p=ROOT/selector['source_project']/row['path']
        actual=sha(p) if p.is_file() else None
        source.append({'path':str(p),'size_bytes':p.stat().st_size if p.is_file() else None,
                       'sha256':actual,'manifest_match':actual==row['sha256'] and p.stat().st_size==row['size_bytes']})
    inventory=ROOT/'Docs/Development/NPCInteractionV1/NPC_INTERACTION_V1_DRAFT_INVENTORY_20261004.json'
    native=[]
    for row in json.loads(inventory.read_text(encoding='utf-8-sig'))['files']:
        p=ROOT/row['path']
        actual=sha(p) if p.is_file() else None
        native.append({'package':row['package'],'path':str(p),'size_bytes':p.stat().st_size if p.is_file() else None,
                       'sha256':actual,'historical_inventory_match':actual==row['sha256']})
    guards=[]
    for relative in ('Assets/Sync/CATALOG.json','Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json',
                     'Docs/Development/CURRENT_TUTORIAL_AUDIO_PLAYTEST_REVIEW.json',
                     'tmp/map-survey-continuation-20261013/PROGRESS.json',
                     'tmp/map-survey-overnight-20261013/RUN_RESERVATION.json',
                     'tmp/map-survey-overnight-20261013/BATCH_QUEUE.json',
                     'Unreal/ParisStreetCombat/Content/ParisCombat/Maps/L_ParisMissionG1.umap'):
        p=ROOT/relative
        if p.is_file():
            guards.append({'path':str(p),'size_bytes':p.stat().st_size,'sha256':sha(p)})
    return {'scope':'read_only_current_source_and_registered_NPC_native_dependency_identity',
            'selector_sha256':sha(SELECTOR),'source_revision':selector['source_revision'],
            'source_project':selector['source_project'],'source_manifest_sha256':sha(manifest_path),
            'manifest_identity_match':sha(manifest_path)==selector['source_manifest_sha256'],
            'source':source,'native_inventory_sha256':sha(inventory),'native':native,'guards':guards,
            'source_matches':sum(r['manifest_match'] for r in source),
            'native_historical_matches':sum(r['historical_inventory_match'] for r in native),
            'not_decompiled_or_runtime_verified':True,
            'selector_stale_field_caveat':'Selector contains older runtime_scope/audio_preferences fields alongside revision10 matching build evidence. Route using selected manifest and current result, not these inherited fields.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--compare');args=parser.parse_args()
    out=Path(args.out).resolve()
    if out.exists():
        raise SystemExit('Audit receipt already exists; preserve it and use a new path')
    receipt=collect()
    if args.compare:
        prior=json.loads(Path(args.compare).read_text(encoding='utf-8'))
        receipt['protected_bytes_unchanged']=all(receipt[k]==prior[k] for k in ('selector_sha256','source','native','guards'))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt.get(k) for k in ('source_revision','source_matches','native_historical_matches','manifest_identity_match','protected_bytes_unchanged')}))


if __name__=='__main__':main()
