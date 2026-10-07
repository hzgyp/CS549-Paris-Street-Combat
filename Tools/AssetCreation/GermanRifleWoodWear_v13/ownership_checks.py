"""Verify isolated exposed furniture faces, not material-envelope guessing."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
import preflight as P
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(P.BASE/'GermanRifle_M1Texture_V12.blend'),load_ui=False,use_scripts=False)
rows={}
for name in ['Guard_OpenBow','Furniture_FrontBand','Furniture_RearBand','Furniture_ButtPlate']:
    ob=bpy.data.objects[name]
    if 'Band' in name:faces=set(range(58,116))
    elif name=='Guard_OpenBow':faces={f.index for f in ob.data.polygons if len(f.vertices)==4}
    else:faces={f.index for f in ob.data.polygons if f.normal.x<-.9}
    xyz,ids,conf=P.raster(ob,faces,1024)
    rows[name]={'faces':sorted(faces),'occupied':int((ids>=0).sum()),'conflicts':int(conf.sum())}
    assert not conf.any(),(name,'isolation failed')
(out/'ownership.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps({k:{a:v for a,v in row.items() if a!='faces'} for k,row in rows.items()}))
