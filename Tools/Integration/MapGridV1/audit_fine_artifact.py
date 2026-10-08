"""Audit actual fine masks, physical station thresholds and inherited failed footprint."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from grid_core import digest

def audit(entry):
    manifest=json.loads((entry/'derived/manifest.json').read_text());spec=json.loads((entry/'grid_spec.json').read_text());counts={};excluded=0
    for scope in ('saved','full'):
        with np.load(entry/'derived'/f'{scope}_filters.npz') as a:data={k:a[k] for k in a.files}
        assert data['count2'].max()<=13 and data['count3'].max()<=29
        assert not data['base'][data['quarantine']].any() and not data['task'][data['quarantine']].any()
        assert not data['count2'][data['quarantine']].any() and not data['count3'][data['quarantine']].any()
        excluded+=int(data['quarantine'].sum())
        assert not (data['task']&~data['base']).any()
        nodes=json.loads((entry/('saved_links' if scope=='saved' else 'links')/'nodes.json').read_text())
        road_groups={int(data['group'][n['id']]) for n in nodes if n['road'] and not data['quarantine'][n['id']]}
        assert all(int(g) in road_groups for g in set(data['group'][data['base']].tolist()))
        for layer in range(manifest['scopes'][scope]['layers']):
            for mode,flag in [('walk',data['base']),('task',data['task']),('encounter',np.zeros(len(nodes),dtype=bool))]+[(f'spawn_{radius}_{minimum}',data['base']&(sites>=minimum)) for radius,sites in ((2,data['count2']),(3,data['count3'])) for minimum in (3,5,6)]:
                path=entry/'derived'/f'{scope}_{mode}_L{layer}.png';image=Image.open(path);assert image.mode=='1' and image.size==(4032,4032)
                pixels=np.array(image,dtype=bool);expected=np.zeros((4032,4032),dtype=bool);use=flag&(data['layer']==layer);expected[data['r'][use],data['c'][use]]=True
                assert np.array_equal(pixels,expected)
                # Complete previous 1m square is 4x4 new cells, never white.
                assert not pixels[2560:2564,2604:2608].any()
                count=int(pixels.sum());assert count==manifest['scopes'][scope]['purpose_counts'][f'{mode}_L{layer}']
                counts[path.name]={'white_cells':count,'sha256':digest(path)}
        del nodes,data
    result={'status':'pass_fine_mask_audit','cell_cm':25,'raster':[4032,4032],'native_sample_interpolation':False,
            'quarantined_native_nodes':excluded,'old_quarantine_world_footprint_preserved_cells':16,'purpose_masks':counts,
            'station_min_spacing_cm':100,'task_arm_cm':100,'encounter_fine_unmeasured_excluded':True,'manual_browser_qa':False}
    target=entry/'artifact/audit_masks.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(counts),'masks')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);audit(p.parse_args().entry)
