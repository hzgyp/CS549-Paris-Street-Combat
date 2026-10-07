"""Read-only wood response inspection; outputs use an unoccupied identity."""
import argparse, json, sys, importlib.util
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-wear-v13/finish_v2'
NAME='GermanRifle_CoordinatedWear_V13'
spec=importlib.util.spec_from_file_location('v13',ROOT/'Tools/AssetCreation/GermanRifleWoodWear_v13/main.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out).resolve()
    assert not out.exists();out.mkdir(parents=True)
    guard={str(BASE/(NAME+'.'+s)):M.W.sha(BASE/(NAME+'.'+s)) for s in ['blend','glb']}
    bpy.ops.wm.open_mainfile(filepath=str(BASE/(NAME+'.blend')),load_ui=False,use_scripts=False)
    rows=[]
    for name in ['V12_M1_Oiled_Walnut','V13_Stock','V13_Handguard']:
        mat=bpy.data.materials[name];bs=mat.node_tree.nodes.get('Principled BSDF')
        row={'material':name,'specular_ior_level':bs.inputs['Specular IOR Level'].default_value,
             'ior':bs.inputs['IOR'].default_value,'coat':bs.inputs['Coat Weight'].default_value,'images':[]}
        for im in M.inputs(mat):
            px=M.W.pixels(im);rgb=px[:,:,:3]
            row['images'].append({'name':im.name,'size':list(im.size),'space':im.colorspace_settings.name,
               'filepath':im.filepath,'pixel_100_100':px[100,100].tolist(),
               'mean':rgb.mean((0,1)).tolist(),'min':rgb.min((0,1)).tolist(),'max':rgb.max((0,1)).tolist()})
        rows.append(row)
    assert all(M.W.sha(Path(f))==s for f,s in guard.items())
    (out/'diagnostic.json').write_text(json.dumps({'inputs':guard,'unchanged':True,'wood':rows},indent=2),encoding='utf-8')
    print(json.dumps(rows),flush=True)
if __name__=='__main__':main()
