from prepare import ROOT, OUT, prepare, write, rows, sha
prepare('candidate_mine_v2','candidate_mine_v1')
p=OUT/'candidate_mine_v2/Project'
private=p/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
m=private/'ParisBridgeMission.cpp';b=m.read_bytes()
old=b'if(DeathLedger.Contains(TEXT("Player"))) { SetPhase(TEXT("Lost")); Feedback=TEXT("Player lost to a remaining hazard.'
new=b'if(DeathLedger.Contains(TEXT("Player"))) { SetCheckpointDialog(TEXT("None"),FString()); CheckpointPromptVisible=false; SetPhase(TEXT("Lost")); Feedback=TEXT("Player lost to a remaining hazard.'
assert b.count(old)==1;m.write_bytes(b.replace(old,new))
src=ROOT/'Tools/Integration/TacticalEquipmentV1/ParisPressureMineChecks.inl'
(private/src.name).write_bytes(src.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
mesh=ROOT/'Tools/Integration/TacticalEquipmentV1/ParisPressureMineMesh.inl'
(private/mesh.name).write_bytes(mesh.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
base=OUT/'candidate_mine_v1/Project'
paths=[f.relative_to(base).as_posix() for name in ['Config','Source','Plugins'] for f in (base/name).rglob('*') if f.is_file() and 'Intermediate' not in f.parts and 'Binaries' not in f.parts]
changed=[s for s in paths if sha(p/s)!=sha(base/s)]
assert set(changed)=={'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp','Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisPressureMineChecks.inl','Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisPressureMineMesh.inl'},changed
write(OUT/'candidate_mine_v2/revision.json',dict(parent='candidate_mine_v1',changed=changed,reason='Use UE native triangle normal convention; clear save modal on actual post-clear death; extend diagnostics with real frag death and spent-mine fresh restore. Authored GLB/maps and contact rule remain exact.'))
