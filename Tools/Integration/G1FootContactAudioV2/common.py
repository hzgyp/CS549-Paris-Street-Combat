import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/g1-foot-contact-audio-v2-20261009'
PARENT=ROOT/'tmp/g1-recorded-foley-20261009'
PY=Path('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
FF=Path('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
def row(p,base):return dict(path=p.relative_to(base).as_posix(),size_bytes=p.stat().st_size,sha256=digest(p))
