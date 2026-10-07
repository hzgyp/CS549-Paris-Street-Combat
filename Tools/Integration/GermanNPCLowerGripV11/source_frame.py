"""ONE diagnosed frame correction; exact retained wood targets, source lengths."""
from pathlib import Path
p=Path(__file__).with_name('stock_section.py')
source=p.read_text(encoding='utf-8-sig')
source=source.replace("OUT=BASE/'stock_section_v2'","OUT=BASE/'source_frame_v4'",1)
needle="GLB,MARK,Path(__file__),p,BASE/'mature_reuse_v1/result.json',ROOT/"
assert needle in source
source=source.replace(needle,"GLB,MARK,Path(__file__),p,Path(__file__).with_name('stock_section.py'),Path(__file__).with_name('nearest_surface.py'),BASE/'mature_reuse_v1/result.json',BASE/'stock_section_v2/result.json',BASE/'nearest_surface_v3/result.json',BASE/'reach_diagnosis_v1/result.json',BASE/'frame_diagnosis_v1/result.json',ROOT/",1)
source=source.replace("    for digit,fan in zip(DIGITS,(.3,0,-.3)):","    retained=read(BASE/'nearest_surface_v3/result.json')\n    for digit in DIGITS:\n        fan=0.0",1)
start=source.index('        rootlocal=transform(')
end=source.index('        turn=np.array',start)
source=source[:start]+'''        rootlocal=transform(root[None],np.linalg.inv(gm))[0];section_y=float(rootlocal[1])
        rec=retained['actual_stock_section_targets'][digit]
        wood=np.array(rec['wood_world_cm']);normal=np.array(rec['wood_normal_world'])
        target=np.array(rec['pad_target_world_cm']);face=int(np.where(stock==rec['wood_face_id'])[0][0])
        pad=p0[tri[padfaces[digit]]].mean((0,1))
        assert np.linalg.norm(pad-np.array(rec['pad_before_world_cm']))<.0001
        padnormal=sn[padfaces[digit]].mean(0);padnormal/=np.linalg.norm(padnormal)
''' +source[end:]
source=source.replace('line=(goal-root)/reach;bend=down-line*(down@line)',
 'line=(goal-root)/reach;bend=(elbow-root)-line*((elbow-root)@line)',1)
start=source.index('        for n,pos,oldvec,newvec in (')
end=source.index('        new[c]=terminal',start)
source=source[:start]+'''        rootturn=np.array(Vector(elbow-root).rotation_difference(Vector(newelbow-root)).to_matrix(),float)
        pipturn=np.array(Vector(rootturn@(wrist-elbow)).rotation_difference(Vector(goal-newelbow)).to_matrix(),float)@rootturn
        for n,pos,rotation in ((a,root,rootturn),(b,newelbow,pipturn)):
            new[n][:3,:3]=rotation@bones[n][:3,:3];new[n][:3,3]=pos
''' +source[end:]
source=source.replace('Fixed MCP roots; actual stock sections; oriented skin pads; source-length two-link chains',
 'Exact retained lower wood targets; closest original bend plane; transported source-length chain frames',1)
exec(compile(source,str(Path(__file__)),'exec'))
