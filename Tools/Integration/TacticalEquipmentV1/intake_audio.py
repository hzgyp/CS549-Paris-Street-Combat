"""Add licensed explosion audio without altering the accepted rifle/Foley cues."""
from prepare import OUT,write,sha
from pathlib import Path
import urllib.request,re,subprocess,wave
import imageio_ffmpeg
dest=OUT/'intake-explosion';assert not dest.exists();dest.mkdir()
page='https://freesound.org/people/qubodup/sounds/162363/'
def fetch(url,p):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (ParisStreetCombat licensed audio intake)'}),timeout=30) as r:data=r.read()
    p.write_bytes(data);return data
html=fetch(page,dest/'primary.html').decode('utf-8')
assert 'creativecommons.org/publicdomain/zero' in html
assert 'Explosion of a grenade on training grounds.' in html
matches=re.findall(r'https://cdn\.freesound\.org/previews/[^\s\"\'<>]+-hq\.(?:ogg|mp3)',html);assert matches
url=matches[0].replace('&amp;','&');source=dest/('source'+Path(url).suffix);fetch(url,source)
target=dest/'explosion.wav'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-v','error','-i',str(source),'-ac','1','-ar','48000','-c:a','pcm_s16le','-bitexact',str(target)],check=True)
with wave.open(str(target),'rb') as w:seconds=w.getnframes()/w.getframerate();assert (w.getframerate(),w.getsampwidth(),w.getnchannels())==(48000,2,1)
write(dest/'source.json',dict(page=page,author='qubodup',license='CC0-1.0',description='Recorded distant propelled-grenade explosion; adaptation for prototype grenade/trap, not identified as an exact WWII grenade recording',intake_type='official public HQ lossy preview, not original lossless FLAC',media=url,source_sha256=sha(source),primary_sha256=sha(dest/'primary.html'),wav_sha256=sha(target),seconds=seconds))
print('Licensed recorded explosion acquired; acoustic acceptance remains manual')
