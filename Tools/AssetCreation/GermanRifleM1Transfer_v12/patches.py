"""Inspect hand-selected M1 atlas regions before any target material authoring."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
TEX=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Textures/USParatrooper/Textures/M1_Garand'
# Normalized top-left pixel coordinates, manually selected from actually viewed atlas.
PATCHES={'wood':(.278,.037,.631,.249),'steel':(.50,.45,.60,.55)}
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
out=Path(a.out).resolve();assert not out.exists();out.mkdir(parents=True)
report={'patches':{},'sources':{}}
for suffix in ['D','N','ORM']:
    path=TEX/('T_M1_Garand_'+suffix+'.png');im=Image.open(path).convert('RGB')
    report['sources'][suffix]={'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    for name,rect in PATCHES.items():
        box=tuple(round(v*im.size[k%2]) for k,v in enumerate(rect));crop=im.crop(box)
        crop.save(out/(name+'_'+suffix+'.png'))
        if suffix=='ORM':
            data=np.asarray(crop)/255
            report['patches'][name]={'rect_top_left_uv':rect,'pixel_box':box,
                'size':list(crop.size),'metallic_percentiles':np.percentile(data[:,:,2],[0,5,50,95,100]).tolist(),
                'roughness_percentiles':np.percentile(data[:,:,1],[5,50,95]).tolist(),
                'metallic_gt_05_fraction':float((data[:,:,2]>.5).mean())}
(out/'patch_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report['patches']))
