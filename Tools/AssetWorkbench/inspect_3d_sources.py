import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
base=root/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Exchange'
out=root/'Assets/LocalWorking/AssetWorkbench/3d';out.mkdir(parents=True,exist_ok=True)
rows=[]
for name in ['SK_WWII_GermanSoldier_varA','SK_WWII_US_Paratrooper_simple','SK_M1_Garand','Rifle_Idle','Rifle_WalkFwdLoop','Rifle_Reload_2']:
    p=base/(name+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
    rows.append(dict(name=name,objects=[dict(name=o.name,type=o.type,scale=list(o.scale),dimensions=list(o.dimensions),bones=len(o.data.bones) if o.type=='ARMATURE' else None) for o in bpy.data.objects],actions=[dict(name=a.name,frames=list(a.frame_range)) for a in bpy.data.actions],images=[dict(name=i.name,path=i.filepath,size=list(i.size),packed=bool(i.packed_file)) for i in bpy.data.images],materials=[dict(name=m.name,nodes=[n.type for n in m.node_tree.nodes] if m.use_nodes else []) for m in bpy.data.materials]))
(out/'source-inspection.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('INSPECTION_COMPLETE',len(rows))
