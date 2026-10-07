"""ONE actual-stock-section fingertip placement; closed-form source-length chains."""
from pathlib import Path
p=Path(__file__).with_name('fit.py')
source=p.read_text(encoding='utf-8-sig')
changes={
    "OUT=BASE/'mature_reuse_v1'":"OUT=BASE/'stock_section_v2'",
    "GLB,MARK,Path(__file__),ROOT/":"GLB,MARK,Path(__file__),p,BASE/'mature_reuse_v1/result.json',ROOT/",
    "source_clip=cache['clips']['owner_reload']['asset'],source_phase_s=2.2":
    "source_clip=cache['clips']['owner_idle']['asset'],source_phase_s=0.0",
    "r['status']='mature_lower_grasp_candidate_requires_actual_views'":
    "r['status']='stock_section_lower_grasp_requires_actual_views'",
}
for a,b in changes.items():
    assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
start=source.index("    sample=cache['clips']['owner_reload']")
end=source.index('    p1=skin(new);before=contacts',start)
source=source[:start]+'''    import math
    localtree=BVHTree.FromPolygons([Vector(v) for v in gp],gt[stock].tolist(),all_triangles=True)
    gm=mat(gun);gr=gm[:3,:3]/np.linalg.norm(gm[:3,:3],axis=0)
    down=-gr[:,2];new={n:b.copy() for n,b in bones.items()};after_bones=dict(old['after_bones']);qlocals={};angles={};ts={};targets={};lengthchecks={}
    for digit,fan in zip(DIGITS,(.3,0,-.3)):
        a,b,c=[digit+'_'+i+'_r' for i in ('01','02','03')]
        root,elbow,wrist=[bones[n][:3,3] for n in (a,b,c)]
        rootlocal=transform(root[None],np.linalg.inv(gm))[0];section_y=float(rootlocal[1]+fan)
        top,tn,tf,td=localtree.ray_cast(Vector((0,section_y,80)),Vector((0,0,-1)),160)
        bottom,bn,bf,bd=localtree.ray_cast(Vector((0,section_y,-80)),Vector((0,0,1)),160)
        assert top is not None and bottom is not None,('Missing actual wood section',digit)
        z=float((top.z+bottom.z)/2)
        loc,normal,face,distance=localtree.ray_cast(Vector((40,section_y,z)),Vector((-1,0,0)),80)
        assert loc is not None,('Missing opposite-palm wood face',digit)
        normal=np.array(normal,float)
        if normal[0]<0:normal=-normal
        assert normal[0]>.3,('Wrong wood-facing side',digit,normal)
        normal=gr@normal;normal/=np.linalg.norm(normal)
        wood=transform(np.array([list(loc)]),gm)[0];target=wood+normal*.08
        pad=p0[tri[padfaces[digit]]].mean((0,1))
        padnormal=sn[padfaces[digit]].mean(0);padnormal/=np.linalg.norm(padnormal)
        turn=np.array(Vector(padnormal).rotation_difference(Vector(-normal)).to_matrix(),float)
        terminal=bones[c].copy();terminal[:3,:3]=turn@bones[c][:3,:3]
        goal=target-turn@(pad-wrist);terminal[:3,3]=goal
        A=float(np.linalg.norm(elbow-root));B=float(np.linalg.norm(wrist-elbow));reach=float(np.linalg.norm(goal-root))
        assert abs(A-B)+1e-4<reach<A+B-1e-4,('Original-length finger unreachable',digit,reach,A,B)
        line=(goal-root)/reach;bend=down-line*(down@line)
        assert np.linalg.norm(bend)>1e-6;bend/=np.linalg.norm(bend)
        along=(A*A-B*B+reach*reach)/(2*reach);side=math.sqrt(max(0,A*A-along*along))
        newelbow=root+along*line+side*bend
        flex=math.degrees(math.acos(float(np.clip((A*A+B*B-reach*reach)/(2*A*B),-1,1))))
        assert 20<flex<160,('Straight/collapsed chain',digit,flex)
        for n,pos,oldvec,newvec in ((a,root,elbow-root,newelbow-root),(b,newelbow,wrist-elbow,goal-newelbow)):
            rotation=np.array(Vector(oldvec).rotation_difference(Vector(newvec)).to_matrix(),float)
            new[n][:3,:3]=rotation@bones[n][:3,:3];new[n][:3,3]=pos
        new[c]=terminal
        lengthchecks[digit]={'first_cm':A,'second_cm':B,'first_error_cm':float(abs(np.linalg.norm(newelbow-root)-A)),
            'second_error_cm':float(abs(np.linalg.norm(goal-newelbow)-B)),'reach_cm':reach,'internal_joint_angle_deg':flex}
        targets[digit]={'section_gun_y_cm':section_y,'declared_fan_cm':fan,'wood_face_id':int(stock[face]),
            'wood_world_cm':wood.tolist(),'wood_normal_world':normal.tolist(),'pad_target_world_cm':target.tolist(),
            'pad_before_world_cm':pad.tolist(),'terminal_target_world_cm':goal.tolist()}
        for n in (a,b,c):
            parent=parents[n];oldlocal=np.linalg.inv(bones[parent])@bones[n];local=np.linalg.inv(new[parent])@new[n]
            after_bones[n]=encode(new[n]);qlocals[n]=encode(local)['q'];angles[n]=tm.angle(encode(oldlocal)['q'],qlocals[n])
            ts[n]={'translation_error_cm':float(np.max(abs(local[:3,3]-oldlocal[:3,3]))),
                'scale_error':float(np.max(abs(np.linalg.norm(local[:3,:3],axis=0)-np.linalg.norm(oldlocal[:3,:3],axis=0))))}
    r.update(actual_stock_section_targets=targets,original_length_finger_checks=lengthchecks,no_angle_scan=True,
        mechanism='Fixed MCP roots; actual stock sections; oriented skin pads; source-length two-link chains')
    assert max(angles.values())<=90,('Local adaptation angular budget',angles)
    assert max(v['translation_error_cm'] for v in ts.values())<.0001
    assert max(v['scale_error'] for v in ts.values())<1e-5
''' +source[end:]
exec(compile(source,str(Path(__file__)),'exec'))
