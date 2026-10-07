"""Read-only actual wood/reach diagnosis; no candidate or angle sweep."""
from pathlib import Path
p=Path(__file__).with_name('fit.py')
source=p.read_text(encoding='utf-8-sig')
start=source.index('BASE=STORE/')
source=source[:start]+source[start:].replace("OUT=BASE/'mature_reuse_v1'","OUT=BASE/'reach_diagnosis_v1'",1)
start=source.index("    sample=cache['clips']['owner_reload']")
end=source.index('\nexcept Exception:',start)
source=source[:start]+'''    gm=mat(gun);gr=gm[:3,:3]/np.linalg.norm(gm[:3,:3],axis=0)
    reports={}
    for digit in DIGITS:
        a,b,c=[digit+'_'+i+'_r' for i in ('01','02','03')]
        root,elbow,end=[bones[n][:3,3] for n in (a,b,c)]
        pad=p0[tri[padfaces[digit]]].mean((0,1));pn=sn[padfaces[digit]].mean(0);pn/=np.linalg.norm(pn)
        loc,nor,face,gap=stocktree.find_nearest(Vector(pad))
        loc=np.array(loc,float);nor=np.array(nor,float)
        if nor@(pad-loc)<0:nor=-nor
        turn=np.array(Vector(pn).rotation_difference(Vector(-nor)).to_matrix(),float)
        goal=loc+nor*.08-turn@(pad-end)
        reports[digit]={'root_gun_cm':transform(root[None],np.linalg.inv(gm))[0].tolist(),
          'pad_gun_cm':transform(pad[None],np.linalg.inv(gm))[0].tolist(),
          'nearest_wood_gun_cm':transform(loc[None],np.linalg.inv(gm))[0].tolist(),
          'nearest_wood_normal_gun':(gr.T@nor).tolist(),'nearest_face_id':int(stock[face]),
          'current_pad_normal_gun':(gr.T@pn).tolist(),'nearest_gap_cm':float(gap),
          'reach_to_oriented_pad_goal_cm':float(np.linalg.norm(goal-root)),
          'two_links_cm':[float(np.linalg.norm(elbow-root)),float(np.linalg.norm(end-elbow))],
          'pad_offset_cm':float(np.linalg.norm(pad-end))}
    r['actual_wood_reach_diagnosis']=reports;r['status']='read_only_surface_reach_diagnosis'
    print(json.dumps(reports,indent=2))
''' +source[end:]
exec(compile(source,str(Path(__file__)),'exec'))
