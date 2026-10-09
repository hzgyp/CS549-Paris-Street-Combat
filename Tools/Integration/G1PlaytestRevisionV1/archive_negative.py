"""Copy finite negative evidence to the dedicated private failure archive."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest
def main():
    p=argparse.ArgumentParser();p.add_argument('identity');a=p.parse_args();assert a.identity.replace('_','').isalnum()
    source=ROOT/'tmp/g1-playtest-revision-20261008'/a.identity
    r=json.loads((source/'read_only_audit.json').read_text());assert r['status']=='stopped_negative_retained_integrity_only'
    out=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/Failures/MI012'/a.identity
    assert not out.exists();out.mkdir();rows=[]
    for f in source.glob('*'):
        if not f.is_file():continue
        dst=out/f.name;shutil.copyfile(f,dst);assert digest(f)==digest(dst)
        rows.append(dict(original=str(f.relative_to(ROOT)),archive=str(dst.relative_to(ROOT)),size_bytes=dst.stat().st_size,sha256=digest(dst)))
    (out/'manifest.json').write_text(json.dumps(dict(status=r['numeric_status'],files=rows,source_inputs='Matched private build recipe and frozen source retained; no rollback or native deletion'),indent=2)+'\n')
    print(json.dumps(dict(identity=a.identity,files=len(rows))))
if __name__=='__main__':main()
