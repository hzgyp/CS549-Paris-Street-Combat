import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];base=root/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Exchange'
bpy.ops.wm.open_mainfile(filepath=str(base/'SK_WWII_GermanSoldier_varA.blend'),load_ui=False,use_scripts=False)
bpy.context.view_layer.update();dst=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
with bpy.data.libraries.load(str(base/'Rifle_Idle.blend'),link=False) as (f,t):t.objects=list(f.objects)
for o in t.objects:bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.update();src=next(o for o in t.objects if o.type=='ARMATURE')
for rig in [dst,src]:
 print('RIG',rig.name,'world',[list(r) for r in rig.matrix_world],'parent',rig.parent,'scale',list(rig.scale))
 for n in ['pelvis','hand_l','foot_l']:print(n,'local',list(rig.data.bones[n].head_local),'world',list(rig.matrix_world@rig.data.bones[n].head_local))
