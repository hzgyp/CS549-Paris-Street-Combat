"""Selected A voice; short separate AI stems, aligned only after actual capture."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'tmp/g1-voice-audition-20261009'
OUT=ROOT/'tmp/g1-demo-draft03-20261009/narration_v1'
TEXTS={
 'opening':'Paris Street Combat. Lead an Allied squad across the bridge and secure G one.',
 'movement':'The player can walk, sprint, move quietly, jump, crouch, and crawl.',
 'navigation':'Both Allies cross the bridge using Unreal navigation and regroup near the player.',
 'combat':'The guards react and fight. Shots and reloads use finite ammunition.',
 'checkpoint':'Defeating all three guards unlocks the checkpoint. Saving requires the player to stop and confirm.',
 'restore':'Loading restores the saved resources. Defeated guards remain in their final death state.',
 'defeat':'A separate run shows enemy fire killing the player, followed by a full mission restart.',
 'ending':'Current build stress testing and teammate validation are still pending. These are the next development steps.'
}
def main():
 assert not OUT.exists(),'Retain existing narration attempt';OUT.mkdir(parents=True)
 sys.path.insert(0,str(WORK/'runtime'))
 import numpy as np,onnxruntime as ort,soundfile as sf
 from kokoro_onnx import Kokoro
 opt=ort.SessionOptions();opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
 k=Kokoro.from_session(ort.InferenceSession(str(WORK/'models/kokoro-v1.0.onnx'),sess_options=opt,providers=['CPUExecutionProvider']),str(WORK/'models/voices-v1.0.bin'))
 rows=[]
 for name,text in TEXTS.items():
  a,sr=k.create(text,voice='am_michael',speed=1.0,lang='en-us');a=np.asarray(a,dtype=np.float32).ravel()
  assert sr==24000 and np.isfinite(a).all() and np.max(np.abs(a))>.001
  path=OUT/(name+'.wav');sf.write(path,a,sr,subtype='FLOAT')
  rows.append(dict(id=name,text=text,duration=len(a)/sr,voice='am_michael',speed=1.0,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  print(json.dumps(rows[-1]),flush=True)
 (OUT/'NARRATION.json').write_text(json.dumps(dict(status='generated_not_yet_aligned_or_mixed',type='AI narration, not game audio',segments=rows),indent=2)+'\n','utf-8')
if __name__=='__main__':main()
