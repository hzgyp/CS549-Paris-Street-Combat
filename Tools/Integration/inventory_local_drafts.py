"""Emit hash metadata only; no release authority or asset-byte publication."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
e=STORE/'Evidence/P2'
reports=[json.loads((e/p).read_text(encoding='utf-8')) for p in (
    'Movement/authoring.json','Retarget/directional_author_v1.json',
    'Retarget/stride_author_v1.json','Lifecycle/authoring_v1.json')]
packages=reports[0]['bridge']['assets']+[reports[0]['map']]
for r in reports[1:]:
    packages += r['assets']
packages.append('/Game/ParisCombat/Tests/Integration/P2_CharacterPreview_20261001')
stride_scene=e/'Lifecycle/stride_scene_v1.json'
if stride_scene.exists():
    packages+=json.loads(stride_scene.read_text(encoding='utf-8'))['assets']
files=[]
for package in sorted(set(p.split('.')[0] for p in packages)):
    relative=package.removeprefix('/Game/')+('.umap' if '/Tests/Integration/' in package else '.uasset')
    path=STORE/'Content'/relative
    files.append({'package':package,'workspace_path':'Content/'+relative,
        'editor_alias_path':'Unreal/ParisStreetCombat/Content/'+relative,
        'size_bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'storage':'unpublished_sftp_workspace_draft','remote_immutable_path':None})
print(json.dumps({'schema_version':1,'status':'LOCAL_DRAFT_NOT_PUBLISHED',
    'owner':'yg745','engine':'UE 5.8.2','source_revision_at_start':'37de53688530d379d73115a22604bd7ee02c03c9',
    'canonical_workspace':'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1',
    'catalog_selected':False,'restore_authority':False,
    'note':'Inventory only: not an active manifest, immutable release or permission to restore/overwrite. Source clone still needs the selected external baseline and a later verified release of these drafts. No credentials or vendor bytes.',
    'baseline_dependency':'Assets/Sync/manifests/character-ue582-integration-baseline.json',
    'file_count':len(files),'size_bytes':sum(f['size_bytes'] for f in files),'files':files},indent=2))
