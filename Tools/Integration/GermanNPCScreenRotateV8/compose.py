"""V8 labels/layout only; original render pixels not retouched."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'GermanNPCTriggerLowerV7/compose.py'
source=p.read_text(encoding='utf-8-sig')
replacements={
 "Evidence/GermanNPCTriggerLowerV7/review_v1":"Evidence/GermanNPCScreenRotateV8/review_v1",
 "德军 V7 · 保留抬起的拇指 / 扳机支点 / 枪托下压 8°":"德军 V8 · 保留 V7 握姿 / 扳机支点 / 枪托向镜头转出 4°",
 "修改前（已抬拇指）":"修改前（V7）",
 "修改后（枪托下压）":"修改后（向镜头转出）",
}
for a,b in replacements.items():
    assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
exec(compile(source,str(Path(__file__)),'exec'))
