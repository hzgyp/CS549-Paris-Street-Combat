from prepare import OUT
import argparse,shutil
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
base=OUT/a.revision/'Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
for name in ['ParisTacticalEquipment.h','ParisTacticalEquipment.cpp']:shutil.copyfile(__file__.replace('author_inventory.py',name),base/name)
p=base/'ParisBridgeMissionV1.cpp';old=p.read_bytes()
assert b'ParisTacticalEquipment' not in old
new=b'#include "ParisTacticalEquipment.h"\r\n'+old
new=new.replace(b'  ParisGameplayAV::Initialize();',b'  ParisTacticalEquipment::Initialize();\r\n  ParisGameplayAV::Initialize();',1)
new=new.replace(b' void ShutdownModule()override{',b' void ShutdownModule()override{ParisTacticalEquipment::Shutdown();',1)
assert new.count(b'ParisTacticalEquipment::Initialize')==1 and new.count(b'ParisTacticalEquipment::Shutdown')==1
p.write_bytes(new)
print('Independent read-only inventory source authored')
