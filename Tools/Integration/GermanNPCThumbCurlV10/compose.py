"""Original-pixel before/after layout; no stock/thumb retouch."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'GermanNPCTriggerLowerV7/compose.py'
source=p.read_text(encoding='utf-8-sig')
changes={
    'Evidence/GermanNPCTriggerLowerV7/review_v1':'Evidence/GermanNPCThumbCurlV10/review_v1',
    '德军 V7 · 保留抬起的拇指 / 扳机支点 / 枪托下压 8°':'德军 V10 · 保留枪位与双手 / 仅右拇指末节弯曲',
    '橙色：右拇指，蓝色：食指；左手整臂随枪转动。灰模诊断，仍有接触问题，未正式采用。':
    '橙色：右拇指，蓝色：食指；腕臂、枪、左手不动。保留已认可轻微重叠，未正式采用。',
    '修改前（已抬拇指）':'修改前（已认可 V9）',
    '修改后（枪托下压）':'修改后（拇指末节弯曲）',
    '左手扶枪随动':'左手与枪保持原位',
}
for a,b in changes.items():
    assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
exec(compile(source,str(Path(__file__)),'exec'))
