"""Align pending documentation/delivery to final v4, not earlier failed identities."""
from pathlib import Path
base=Path(__file__).resolve().parent
p=base/'document_result.py';t=p.read_text('utf-8')
t=t.replace('performance_ui_v3','performance_ui_v4').replace('ui_pages_v3','ui_pages_v4').replace('candidate_ui_v3','candidate_ui_v4').replace('enemy_clear26项','enemy_clear27项')
t=t.replace('v2→v3去除换行差异后仅opt-in截图探针改变。','v2→v3去除换行差异后仅opt-in截图探针改变；v3→v4仅保存引导有效期及其诊断断言改变。')
t=t.replace('MI032保留首候选受保护API/TObjectPtr编译失败；MI033保留第二候选截图同帧切页错位。v3等待截图完成才切页，实际像素重新验收。','MI032保留首候选受保护API/TObjectPtr编译失败；MI033保留第二候选截图同帧切页错位，等待截图完成才切页。MI034保存类引导残留改为按当前操作可用性清除；MI035将旧v16 seed用例正确映射为原restore_equipment模式，最终实跑兼容。实际像素重新验收。')
t=t.replace('MI032/033原件保留','MI032–035原件保留')
p.write_text(t,encoding='utf-8')
p=base/'deliver.py';t=p.read_text('utf-8')
old="'candidate_ui_v2: UI runtime checks pass, screenshot labels mismatch / MI033; retained']"
assert old in t
t=t.replace(old,"'candidate_ui_v2: UI runtime checks pass, screenshot labels mismatch / MI033; retained','candidate_ui_v3: stale save guide / MI034 and invalid restore alias fixture / MI035; retained']")
p.write_text(t,encoding='utf-8')
p=base.parents[2]/'Failures/MI034-20261011-ui-stale-save-hint/ANALYSIS.md'
t=p.read_text('utf-8').replace('19项原检查结果','已完成的原检查结果');p.write_text(t,encoding='utf-8')
