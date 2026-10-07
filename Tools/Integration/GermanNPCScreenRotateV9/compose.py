"""Labels/layout only: V8 total4deg left, V9 total6deg right; no pixel retouch."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'GermanNPCTriggerLowerV7/compose.py'
source = p.read_text(encoding='utf-8-sig')
replacements = {
    'Evidence/GermanNPCTriggerLowerV7/review_v1': 'Evidence/GermanNPCScreenRotateV9/review_v1',
    '德军 V7 · 保留抬起的拇指 / 扳机支点 / 枪托下压 8°':
    '德军 V9 · 同轴追加 2° / 左侧累计 4° / 右侧累计 6°',
    '修改前（已抬拇指）': '修改前（累计 4°）',
    '修改后（枪托下压）': '修改后（累计 6°）',
}
for a, b in replacements.items():
    assert source.count(a) == 1, (a, source.count(a))
    source = source.replace(a, b)
exec(compile(source, str(Path(__file__)), 'exec'))
