"""ONE source thumb03 bend limited by measured first stock surface; no angle scan."""
from pathlib import Path
p=Path(__file__).with_name('fit.py')
source=p.read_text(encoding='utf-8-sig')
changes={
    "OUT=BASE/'distal_reuse_v1'":"OUT=BASE/'surface_limit_v2'",
    "CHANGED=('thumb_02_r','thumb_03_r')":"CHANGED=('thumb_03_r',)",
    "('thumb_01_r',*CHANGED)]":"('thumb_01_r','thumb_02_r','thumb_03_r')]",
    "GLB,MARK,Path(__file__),ROOT/":"GLB,MARK,Path(__file__),p,BASE/'distal_reuse_v1/result.json',ROOT/",
    "r['status']='distal_existing_grasp_candidate_requires_actual_views'":"r['status']='surface_limited_distal_grasp_requires_actual_views'",
}
for a,b in changes.items():
    assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
start=source.index('    for n in CHANGED:\n')
end=source.index('    assert max(angles.values())<30',start)
source=source[:start]+'''    from mathutils import Matrix,Quaternion
    import math
    n='thumb_03_r';parent=parents[n]
    oldlocal=np.linalg.inv(bones[parent])@bones[n]
    mature=np.linalg.inv(src[parent])@src[n]
    local=oldlocal.copy()
    local[:3,:3]=mature[:3,:3]/np.linalg.norm(mature[:3,:3],axis=0)*np.linalg.norm(oldlocal[:3,:3],axis=0)
    full=bones[parent]@local;delta=full@np.linalg.inv(bones[n])
    u,s,vh=np.linalg.svd(delta[:3,:3]);rot=u@vh
    q=Matrix(rot).to_quaternion();axis=np.array(q.axis,float);axis/=np.linalg.norm(axis)
    maxangle=float(q.angle);assert 0<maxangle<math.radians(30)
    pivot=bones[n][:3,3]
    component=transform(rest,bones[n]@np.linalg.inv(refs[names.index(n)]))
    influence=w[:,names.index(n)]/w.sum(1)
    padvertices=np.unique(tri[padfaces].flatten());limits=[]
    for vid in padvertices:
        loc,normal,face,distance=top_tree.find_nearest(Vector(p0[vid]));assert loc is not None
        normal=np.array(normal,float)
        if normal@up<0:normal=-normal
        assert normal@up>.5
        v=component[vid]-pivot;perp=v-axis*(axis@v)
        A=float(influence[vid]*(normal@perp));B=float(influence[vid]*(normal@np.cross(axis,v)))
        height=float(normal@(p0[vid]-np.array(loc,float)));C=height-A-.08
        assert height>.08,('Distal pad baseline already below safe clearance',int(vid),height)
        radius=math.hypot(A,B)
        if radius<1e-10 or abs(C)>radius:continue
        phi=math.atan2(B,A);offset=math.acos(float(np.clip(-C/radius,-1,1)))
        roots=[(phi+sign*offset)%(2*math.pi) for sign in (-1,1)]
        valid=[theta for theta in roots if 1e-7<theta<=maxangle]
        if valid:limits.append({'vertex_id':int(vid),'angle_rad':min(valid),'normal_world':normal.tolist(),
            'stock_face_id':int(upper[face]),'before_signed_height_cm':height,'wood_point_cm':list(loc)})
    assert limits,'No bounded first-surface angle; do not guess another amplitude'
    limiter=min(limits,key=lambda v:v['angle_rad']);theta=limiter['angle_rad']
    applied=np.array(Quaternion(Vector(axis),theta).to_matrix(),float)
    new[n][:3,:3]=applied@bones[n][:3,:3]
    local=np.linalg.inv(bones[parent])@new[n];after_bones[n]=encode(new[n]);qlocals[n]=encode(local)['q']
    angles[n]=tm.angle(encode(oldlocal)['q'],qlocals[n])
    ts[n]={'translation_error_cm':float(np.max(abs(local[:3,3]-oldlocal[:3,3]))),
        'scale_error':float(np.max(abs(np.linalg.norm(local[:3,:3],axis=0)-np.linalg.norm(oldlocal[:3,:3],axis=0))))}
    r.update(surface_limiting_point=limiter,retained_existing_max_bend_deg=math.degrees(maxangle),
        actual_limited_bend_deg=math.degrees(theta),source_bend_fraction=theta/maxangle,
        surface_clearance_cm=.08,rotation_axis_world=axis.tolist(),last_joint_pivot_cm=pivot.tolist(),
        no_angle_scan=True,authorized_bones=[n])
''' +source[end:]
exec(compile(source,str(Path(__file__)),'exec'))
