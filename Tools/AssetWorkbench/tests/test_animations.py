import json,struct,hashlib,threading
from pathlib import Path
import pytest
from app.animations import AnimationLibrary
from app.security import WorkbenchError

@pytest.fixture
def library(tmp_path):
 state=tmp_path/'Assets/LocalWorking/AssetWorkbench';records=state/'private-records';records.mkdir(parents=True)
 clips=[{'id':'clip-a','name':'Walk','path':'/Game/Walk.Walk','sha256':'a'*64},{'id':'clip-b','name':'Run','path':'/Game/Run.Run','sha256':'b'*64}]
 (records/'animation-packs.json').write_text(json.dumps({'packs':{'pack':{'id':'pack','default_clip':'clip-a','external_mannequin':False,'clips':clips}}}))
 return AnimationLibrary(tmp_path,state)

def cache(library,source='a'*64):
 folder=library.base/'cache/clip-a';folder.mkdir(parents=True)
 doc=json.dumps({'asset':{'version':'2.0'},'animations':[{'name':'Walk'}]}).encode();doc+=b' '*(-len(doc)%4)
 raw=struct.pack('<III',0x46546c67,2,20+len(doc))+struct.pack('<II',len(doc),0x4e4f534a)+doc
 file=folder/'model.glb';file.write_bytes(raw)
 (folder/'glb-result.json').write_text(json.dumps({'status':'ready','path':str(file),'sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':source}))
 return file

def test_registered_clips_only_and_cached_identity(library):
 assert library.directory('pack')['clips'][0]['name']=='Walk'
 assert 'sha256' not in library.directory('pack')['clips'][0]
 with pytest.raises(WorkbenchError):library.prepare('pack','../../outside')
 with pytest.raises(WorkbenchError):library.directory('absent')
 file=cache(library);assert library.status('pack','clip-a')['status']=='ready'
 assert library.file('pack','clip-a')[0]==file.read_bytes()
 file.write_bytes(b'tampered')
 with pytest.raises(WorkbenchError,match='哈希'):library.file('pack','clip-a')

def test_changed_source_rejects_old_preview(library):
 cache(library,source='c'*64)
 with pytest.raises(WorkbenchError,match='登记动作'):library.status('pack','clip-a')
 with pytest.raises(WorkbenchError):library.file('pack','clip-a')

def test_single_worker_deduplication_and_busy(library,monkeypatch):
 release=threading.Event();entered=threading.Event();calls=[]
 def run(pack,clip):
  calls.append(clip['id']);entered.set();release.wait(5)
  with library.lock:library.active=None
 monkeypatch.setattr(library,'_run',run)
 try:
  assert library.prepare('pack','clip-a')['status']=='preparing';assert entered.wait(2)
  assert library.prepare('pack','clip-a')['status']=='preparing'
  with pytest.raises(WorkbenchError,match='其他动作'):library.prepare('pack','clip-b')
  assert calls==['clip-a']
 finally:release.set()
