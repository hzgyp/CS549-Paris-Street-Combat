"""Match real distal-inner index skin and working blade surface; no digit edit."""
from pathlib import Path
entry=Path(__file__).with_name('blender_trigger_surface_v10b.py')
source=entry.read_text(encoding='utf-8')
start=source.index('    # One transform per actual curved face')
end=source.index("    assert best is not None",start)
replacement='''    # Actual volar/inner distal pads, not the inherited forward terminal tip.
    distal=weights[:,names.index('index_03_r')]>.5
    sf=tri[np.all(distal[tri],axis=1)]
    st=body[sf];sc=st.mean(1)
    sn=-np.cross(st[:,1]-st[:,0],st[:,2]-st[:,0]);sn/=np.linalg.norm(sn,axis=1)[:,None]
    inward=bones['middle_03_r'][:3,3]-bones['index_03_r'][:3,3]
    inward/=np.linalg.norm(inward)
    valid=np.flatnonzero((np.linalg.norm(sc-pad,axis=1)<3)&(sn@inward>.2))
    assert len(valid)>=3
    # Permit actual curved blade side faces too; this is a position/contact
    # calibration, not physical trigger-actuation simulation.
    selected=np.flatnonzero((centers[:,2]<-.9)&(centers[:,2]>-2.7))
    possibilities=[]
    for k in valid:
        desired=-sn[k];target=sc[k]+sn[k]*.10
        for j in selected:
            old=transform(centers[j][None,:],g)[0]
            normal_world=g[:3,:3]@normals[j];normal_world/=np.linalg.norm(normal_world)
            initial=swing(normal_world,desired)
            a=initial@(-old);b=-target
            a-=desired*np.dot(a,desired);b-=desired*np.dot(b,desired)
            if np.linalg.norm(a)<1e-6 or np.linalg.norm(b)<1e-6:continue
            twist=math.atan2(np.dot(desired,np.cross(a,b)),np.dot(a,b))
            rot=np.array(Quaternion(Vector(desired),twist).to_matrix(),float)@initial
            angle=math.degrees(math.acos(np.clip((np.trace(rot)-1)/2,-1,1)))
            seat=target-rot@old
            if angle>30 or np.linalg.norm(seat)>3:continue
            c=np.eye(4);c[:3,:3]=rot;c[:3,3]=seat
            rank=float(np.linalg.norm(seat)+angle*.025+np.linalg.norm(sc[k]-pad)*.1)
            possibilities.append((rank,k,j,c,angle,seat))
    possibilities.sort(key=lambda item:item[0])
    r.update(actual_distal_inner_faces=len(valid),feasible_surface_pairs=len(possibilities),
             terminal_point_only_tangency_failed=True)
    write(OUT/'result.json',r)
    best=None;bestscore=float('inf')
    terminalpad=pad.copy()
    for rank,k,j,c,angle,seat in possibilities[:80]:
        pad=sc[k]
        aftergun=c@g;ct=contact(aftergun)
        count=sum(ct['digits']['index'].values())
        score=count*10+ct['actual_pad_to_blade_cm']
        record={'actual_blade_triangle':int(bladeids[j]),'actual_index_skin_vertices':sf[k].tolist(),
                'pad_world_cm':(pad+origin).tolist(),'pad_normal_native':sn[k].tolist(),
                'terminal_pad_distance_cm':float(np.linalg.norm(pad-terminalpad)),
                'surface_local_cm':centers[j].tolist(),'normal_local':normals[j].tolist(),
                'angle_deg':angle,'seat_cm':seat.tolist(),'contact':ct}
        r['evaluations'].append(record);write(OUT/'result.json',r)
        print('pad fit',len(r['evaluations']),'angle',round(angle,2),'seat',round(np.linalg.norm(seat),3),
              'gap',round(ct['actual_pad_to_blade_cm'],4),'index',ct['digits']['index'],flush=True)
        if score<bestscore:bestscore=score;best=(c,aftergun,record)
        if count==0 and ct['actual_pad_to_blade_cm']<=.15:break
    if best is not None:pad=np.array(best[2]['pad_world_cm'])-origin
'''
source=source[:start]+replacement+source[end:]
changes={
    "from mathutils import Vector,Matrix":"from mathutils import Vector,Matrix,Quaternion",
    "OUT=BASE/'trigger_surface_v10b'":"OUT=BASE/'trigger_pad_v10d'",
    "paths=(PREVIOUS,MEASURE,GEOMETRY,TOPO,HELPER,Path(__file__))":"paths=(PREVIOUS,MEASURE,GEOMETRY,TOPO,HELPER,Path(__file__),entry)",
    'trigger_surface_v10b_local_geometry_pass':'trigger_pad_v10d_local_geometry_pass',
    'trigger_surface_v10b_residual_retained':'trigger_pad_v10d_residual_retained',
}
for old,new in changes.items():
    assert source.count(old)==1,old
    source=source.replace(old,new)
exec(compile(source,str(entry)+':pad_v10d','exec'),globals())
