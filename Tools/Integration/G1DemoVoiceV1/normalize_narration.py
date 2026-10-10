"""Normalize selected A voice stems without replacing captured game sound."""
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'tmp/g1-demo-draft03-20261009'
FF=Path(r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
def main():
    rows=json.loads((WORK/'narration_v1/NARRATION.json').read_text())['segments']
    dest=WORK/'narration_normalized_v1';dest.mkdir()
    for row in rows:
        target=dest/(row['id']+'.wav')
        command=[str(FF),'-hide_banner','-nostdin','-i',row['path'],'-af','loudnorm=I=-20:TP=-3:LRA=11:print_format=json','-ar','48000','-ac','1','-c:a','pcm_s24le',str(target)]
        r=subprocess.run(command,capture_output=True,text=True,check=True)
        (dest/(row['id']+'.log')).write_text(r.stderr,'utf-8');row['normalized_path']=str(target.resolve())
    (dest/'NARRATION.json').write_text(json.dumps(dict(voice='A / Michael / am_michael',type='AI narration',target_lufs=-20,target_true_peak_db=-3,segments=rows),indent=2),'utf-8')
    print(str(dest.resolve()),flush=True)
if __name__=='__main__':main()
