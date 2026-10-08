import argparse
import json
from pathlib import Path

from grid_core import grid_spec, write_candidates

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('nav',type=Path);p.add_argument('out',type=Path)
    p.add_argument('--spec',type=Path)
    a=p.parse_args()
    nav=json.loads(a.nav.read_text(encoding='utf-8'))
    spec=json.loads(a.spec.read_text(encoding='utf-8')) if a.spec else grid_spec(nav)
    _,meta=write_candidates(nav,spec,a.out)
    print(json.dumps({'candidates':meta['candidate_count'],'omitted_polygons':len(meta['omitted_polygons']),'spec':spec}))
