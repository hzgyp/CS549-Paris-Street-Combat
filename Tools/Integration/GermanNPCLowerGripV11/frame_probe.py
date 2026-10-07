"""Read-only chain-frame diagnosis using retained actual targets; no skin candidate."""
from pathlib import Path
p=Path(__file__).with_name('reach_probe.py')
source=p.read_text(encoding='utf-8-sig')
source=source.replace("OUT=BASE/'reach_diagnosis_v1'","OUT=BASE/'frame_diagnosis_v1'",1)
start=source.index('    reports={}')
end=source.index("    r['actual_wood_reach_diagnosis']",start)
source=source[:start]+'''    import math
    retained=read(BASE/'nearest_surface_v3/result.json');reports={}
    for digit in DIGITS:
        a,b,c=[digit+'_'+i+'_r' for i in ('01','02','03')]
        root,elbow,end=[bones[n][:3,3] for n in (a,b,c)]
        rec=retained['actual_stock_section_targets'][digit];goal=np.array(rec['terminal_target_world_cm'])
        target=np.array(rec['pad_target_world_cm']);normal=np.array(rec['wood_normal_world'])
        pad=p0[tri[padfaces[digit]]].mean((0,1));pn=sn[padfaces[digit]].mean(0);pn/=np.linalg.norm(pn)
        turn=np.array(Vector(pn).rotation_difference(Vector(-normal)).to_matrix(),float)
        A=np.linalg.norm(elbow-root);B=np.linalg.norm(end-elbow);reach=np.linalg.norm(goal-root)
        line=(goal-root)/reach;closest=(elbow-root)-line*((elbow-root)@line);closest/=np.linalg.norm(closest)
        along=(A*A-B*B+reach*reach)/(2*reach);side=math.sqrt(A*A-along*along);newelbow=root+along*line+side*closest
        rot1=np.array(Vector(elbow-root).rotation_difference(Vector(newelbow-root)).to_matrix(),float)
        rot2=np.array(Vector(rot1@(end-elbow)).rotation_difference(Vector(goal-newelbow)).to_matrix(),float)@rot1
        new={n:v.copy() for n,v in bones.items()}
        for n,rot,pos in ((a,rot1,root),(b,rot2,newelbow),(c,turn,goal)):
            new[n][:3,:3]=rot@bones[n][:3,:3];new[n][:3,3]=pos
        angles={n:tm.angle(encode(np.linalg.inv(bones[parents[n]])@bones[n])['q'],encode(np.linalg.inv(new[parents[n]])@new[n])['q']) for n in (a,b,c)}
        oldplane=np.cross(elbow-root,end-elbow);oldplane/=np.linalg.norm(oldplane)
        newplane=np.cross(newelbow-root,goal-newelbow);newplane/=np.linalg.norm(newplane)
        reports[digit]={'retained_target_world_cm':target.tolist(),'new_elbow_world_cm':newelbow.tolist(),
          'predicted_local_rotation_delta_deg':angles,'source_plane_turn_deg':math.degrees(math.acos(float(np.clip(oldplane@newplane,-1,1)))),
          'actual_target_changed':False,'source_lengths_changed':False}
    print(json.dumps(reports,indent=2))
''' +source[end:]
source=source.replace("r['actual_wood_reach_diagnosis']=reports;r['status']='read_only_surface_reach_diagnosis'","r['source_frame_diagnosis']=reports;r['status']='read_only_source_frame_diagnosis'",1)
exec(compile(source,str(Path(__file__)),'exec'))
