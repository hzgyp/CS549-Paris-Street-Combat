"""One exact checkpoint and bounded map recovery before formal adoption."""
import shutil
from common import *

assert not (BASE/'preflight').exists(),'Preserve occupied checkpoint'
spec=importlib.util.spec_from_file_location('old_allied_guard',ROOT/'Tools/Integration/AlliedNPCUEV15/common.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
assert old.guards(False)==611
draft=read(STORE/'Evidence/AlliedNPCUEV15/draft_asset_read_v17/result.json')
assert not draft['errors'] and all(exact(f) for f in draft['files'])
assert sha(CONFIG)==draft['config_sha256']
before=BASE/'preflight';before.mkdir(parents=True)
for source,name in ((MAP,'map_before.umap'),(DESCRIPTOR,'descriptor_before.uproject')):
    dest=before/name
    assert dest.resolve().is_relative_to(STORE.resolve())
    shutil.copy2(source,dest);assert sha(source)==sha(dest)
write(before/'result.json',{'guards':old.checkpoint.guard_rows(),'descriptor':row(DESCRIPTOR),
    'descriptor_json':read(DESCRIPTOR),'config':row(CONFIG),'candidate_files':draft['files'],
    'human_acceptance':'Yupu reports current V16 preview satisfactory and requests all Allied NPCs adopt it,6 October2026',
    'old_user_editor_pid':50884,'old_user_editor_exit':'process absent/log normal shutdown; OS exit code unavailable',
    'accepted_algorithm_files':[row(PLUGIN/'Source/ParisNPCGripV15'/p) for p in
        ('Public/ParisNPCGripV15.h','Private/ParisNPCGripV15.cpp')]})
print('611 exact; accepted candidates protected; map/descriptor recovery verified')
