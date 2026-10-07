"""ONE measured nearest-lower-wood correction; preserve failed opposite-wall reach."""
from pathlib import Path
p=Path(__file__).with_name('stock_section.py')
source=p.read_text(encoding='utf-8-sig')
source=source.replace("OUT=BASE/'stock_section_v2'","OUT=BASE/'nearest_surface_v3'",1)
needle="GLB,MARK,Path(__file__),p,BASE/'mature_reuse_v1/result.json',ROOT/"
assert needle in source
source=source.replace(needle,"GLB,MARK,Path(__file__),p,Path(__file__).with_name('stock_section.py'),BASE/'mature_reuse_v1/result.json',BASE/'stock_section_v2/result.json',BASE/'reach_diagnosis_v1/result.json',ROOT/",1)
source=source.replace("    for digit,fan in zip(DIGITS,(.3,0,-.3)):","    for digit in DIGITS:\n        fan=0.0",1)
start=source.index('        rootlocal=transform(')
end=source.index('        turn=np.array',start)
source=source[:start]+'''        rootlocal=transform(root[None],np.linalg.inv(gm))[0];section_y=float(rootlocal[1])
        pad=p0[tri[padfaces[digit]]].mean((0,1))
        loc,normal,face,distance=stocktree.find_nearest(Vector(pad))
        assert loc is not None,('Missing nearest actual wood',digit)
        wood=np.array(loc,float);normal=np.array(normal,float)
        if normal@(pad-wood)<0:normal=-normal
        normal/=np.linalg.norm(normal)
        assert (gr.T@normal)[2]<-.3,('Not measured lower stock surface',digit,normal)
        target=wood+normal*.08
        padnormal=sn[padfaces[digit]].mean(0);padnormal/=np.linalg.norm(padnormal)
''' +source[end:]
source=source.replace('Fixed MCP roots; actual stock sections; oriented skin pads; source-length two-link chains',
 'Fixed MCP roots; diagnosed nearest lower wood faces; oriented existing skin pads; source-length two-link chains',1)
exec(compile(source,str(Path(__file__)),'exec'))
