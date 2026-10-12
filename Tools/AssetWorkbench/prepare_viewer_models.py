"""Read-only browser derivatives of existing project exchanges; no native asset writes."""
import bpy,json,hashlib,traceback,sys
from pathlib import Path
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[2]
EXCHANGE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Exchange'
OUT=ROOT/'Assets/LocalWorking/AssetWorkbench/3d/export-v3'
# Each conversion attempt has a new identity; never overwrite an indexed preview.
OUT.mkdir(parents=True,exist_ok=False)
CLIPS=['Rifle_Idle','Rifle_WalkFwdLoop','Rifle_RunFwdLoop','Rifle_ShootOnce','Rifle_Reload_2','Rifle_Hit_C_1','Rifle_Death_3']
SOURCES={'german-soldier':EXCHANGE/'SK_WWII_GermanSoldier_varA.blend','allied-soldier':EXCHANGE/'SK_WWII_US_Paratrooper_simple.blend','m1-garand':EXCHANGE/'SK_M1_Garand.blend',
 'first-person':ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadRepairV5/sleeve_weights_offline_v2/SleeveWeightsV5.blend'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'scope':'Existing mesh and source clip browser derivatives; native grip/retarget overrides are not included','models':[],'errors':[],'inputs':{}}

def input_file(p):report['inputs'][p.relative_to(ROOT).as_posix()]=sha(p)
def save_report():
    report['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in report['inputs'].items())
    (OUT/'export-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

try:
 for aid,p in SOURCES.items():
    if '--only' in sys.argv and aid!=sys.argv[sys.argv.index('--only')+1]:continue
    input_file(p);bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
    # Resolve original material files before loading animation libraries.
    for im in bpy.data.images:
        if im.source=='FILE' and not im.packed_file:
            path=Path(bpy.path.abspath(im.filepath)).resolve()
            if path.is_file():im.filepath=str(path);input_file(path)
            elif im.users:raise RuntimeError('Missing original material image: '+str(path))
        if im.source=='FILE' and max(im.size)>1024:
            factor=1024/max(im.size);im.scale(round(im.size[0]*factor),round(im.size[1]*factor))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    for o in list(bpy.context.scene.objects):
        if o.type not in ('MESH','ARMATURE','EMPTY'):bpy.data.objects.remove(o,do_unlink=True)
    row={'id':aid,'source':p.relative_to(ROOT).as_posix(),'source_sha256':sha(p),'clips':[],'mesh_count':len(meshes),'triangles':0,'vertices':sum(len(m.data.vertices) for m in meshes),'materials':sorted({m.name for o in meshes for m in o.data.materials if m})}
    for m in meshes:m.data.calc_loop_triangles();row['triangles']+=len(m.data.loop_triangles)
    if rigs:
        assert len(rigs)==1;rig=rigs[0];rig.animation_data_clear()
        bpy.context.scene.render.fps=30;bpy.context.scene.render.fps_base=1
        # Strip prior diagnostic poses from the viewing copy, keeping the source rest rig/weights.
        for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4);pb.rotation_mode='QUATERNION'
        row['bones']=len(rig.data.bones)
        ordered=sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive))
        bpy.context.view_layer.update()
        target_world=rig.matrix_world.copy();target_inv=target_world.inverted()
        all_actions=[]
        for clip in CLIPS:
            source=EXCHANGE/(clip+'.blend');input_file(source)
            with bpy.data.libraries.load(str(source),link=False) as (data_from,data_to):data_to.objects=[n for n in data_from.objects]
            loaded=[o for o in data_to.objects if o]
            for o in loaded:bpy.context.scene.collection.objects.link(o)
            bpy.context.view_layer.update()
            src=next(o for o in loaded if o.type=='ARMATURE');src_action=src.animation_data.action
            first,last=map(int,src_action.frame_range);source_world=src.matrix_world.copy()
            A=target_inv@source_world;invA=A.inverted()
            common=set(src.data.bones.keys())&set(rig.data.bones.keys())
            assert {'pelvis','spine_01','upperarm_l','upperarm_r','hand_l','hand_r'}<=common
            rest_error=max((target_world@(A@src.data.bones[n].matrix_local).translation-target_world@rig.data.bones[n].matrix_local.translation).length for n in common)
            # Existing compatible meshes have different proportions (Allied ~23 mm).
            # The rest-relative transform below preserves each target bind pose.
            assert rest_error<.05,('incompatible reference bones',aid,clip,rest_error)
            action=bpy.data.actions.new(clip);rig.animation_data_create();rig.animation_data.action=action
            bone_samples=[]
            for frame in range(first,last+1):
                bpy.context.scene.frame_set(frame)
                poses={}
                for pb in ordered:
                    n=pb.name;rest=rig.data.bones[n].matrix_local
                    if n in common:posed=A@src.pose.bones[n].matrix@src.data.bones[n].matrix_local.inverted()@invA@rest
                    elif pb.parent:posed=poses[pb.parent.name]@rig.data.bones[pb.parent.name].matrix_local.inverted()@rest
                    else:posed=rest.copy()
                    poses[n]=posed
                    pb.matrix_basis=(rest.inverted()@rig.data.bones[pb.parent.name].matrix_local@poses[pb.parent.name].inverted()@posed) if pb.parent else rest.inverted()@posed
                    for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(data_path=prop,frame=frame-first,group=n)
                if frame in (first,(first+last)//2,last):
                    bpy.context.view_layer.update()
                    pose_error=max(abs(pb.matrix[i][j]-poses[pb.name][i][j]) for pb in ordered for i in range(4) for j in range(4))
                    assert pose_error<.01,('pose conversion error',aid,clip,frame,pose_error)
                    bone_samples.append({'time':(frame-first)/30,'hand_l':list((target_world@poses['hand_l']).translation),'foot_l':list((target_world@poses['foot_l']).translation) if 'foot_l' in poses else None})
            action.use_fake_user=True;all_actions.append(action)
            row['clips'].append({'name':clip,'duration':(last-first)/30,'frames':last-first+1,'shared_bones':len(common),'rest_head_difference_m':rest_error,'samples':bone_samples})
            rig.animation_data.action=None
            for o in loaded:bpy.data.objects.remove(o,do_unlink=True)
            if src_action.users==0:bpy.data.actions.remove(src_action)
        # Dedicated NLA strips preserve clip names and independent ranges in GLB.
        for action in all_actions:
            track=rig.animation_data.nla_tracks.new();track.name=action.name
            track.strips.new(action.name,0,action)
            track.mute=True
        for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
        rig.animation_data.action=None
    bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','ARMATURE','EMPTY'):o.select_set(True)
    # Private GLB only: exporter writes no native or original file.
    path=OUT/(aid+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=bool(rigs),export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_force_sampling=True,export_def_bones=False,export_all_influences=True,export_skins=True,export_yup=True,export_cameras=False,export_lights=False)
    row.update(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size)
    report['models'].append(row);save_report();print('EXPORTED',aid,row['bytes'],flush=True)
except Exception:
 report['errors'].append(traceback.format_exc());raise
finally:save_report()
