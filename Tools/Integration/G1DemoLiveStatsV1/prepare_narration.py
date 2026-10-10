"""Reuse approved A voice except the obsolete pending ending; synthesize one new line."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'tmp/g1-demo-draft04-20261010'
RUNTIME=ROOT/'tmp/g1-voice-audition-20261009';sys.path.insert(0,str(RUNTIME/'runtime'))
import numpy as np,onnxruntime as ort,soundfile as sf
from kokoro_onnx import Kokoro
out=WORK/'narration_normalized_v1';assert not out.exists();out.mkdir()
parent=json.loads((ROOT/'tmp/g1-demo-draft03-20261009/narration_normalized_v1/NARRATION.json').read_text())
rows=[r for r in parent['segments'] if r['id']!='ending']
text='The live panel shows frame times, process memory, and video memory during this recording.'
opt=ort.SessionOptions();opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
k=Kokoro.from_session(ort.InferenceSession(str(RUNTIME/'models/kokoro-v1.0.onnx'),sess_options=opt,providers=['CPUExecutionProvider']),str(RUNTIME/'models/voices-v1.0.bin'))
a,sr=k.create(text,voice='am_michael',speed=1.0,lang='en-us');a=np.asarray(a,dtype=np.float32).ravel()
assert sr==24000 and np.isfinite(a).all() and np.max(np.abs(a))>.001
raw=out/'ending_raw.wav';sf.write(raw,a,sr,subtype='FLOAT')
norm=out/'ending.wav';ff=Path(r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
r=subprocess.run([str(ff),'-hide_banner','-nostdin','-i',str(raw),'-af','loudnorm=I=-20:TP=-3:LRA=11:print_format=json','-ar','48000','-ac','1','-c:a','pcm_s24le',str(norm)],capture_output=True,text=True,check=True)
(out/'ending.log').write_text(r.stderr,'utf-8')
rows.append(dict(id='ending',text=text,duration=len(a)/sr,voice='am_michael',speed=1.0,path=str(raw),normalized_path=str(norm),sha256=hashlib.sha256(raw.read_bytes()).hexdigest()))
parent['segments']=rows;(out/'NARRATION.json').write_text(json.dumps(parent,indent=2)+'\n','utf-8')
print(json.dumps(rows[-1]))
