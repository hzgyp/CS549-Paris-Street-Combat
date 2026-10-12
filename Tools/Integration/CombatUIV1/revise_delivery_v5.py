from pathlib import Path
base=Path(__file__).resolve().parent
p=base/'document_result.py';t=p.read_text('utf-8')
t=t.replace('performance_ui_v4','performance_ui_v5').replace('ui_pages_v4','ui_pages_v5').replace('candidate_ui_v4','candidate_ui_v5').replace('MI032–035','MI032–036').replace('v1–v3','v1–v4')
t=t.replace('v3→v4仅保存引导有效期及其诊断断言改变。','v3→v4仅保存引导有效期及其诊断断言改变；v4→v5仅UI探针实际点击Ready开始，不再假定旧选择。')
t=t.replace('实际像素重新验收。没有覆盖失败源','MI036明确点击原Ready开始按钮，正常退出无RESULT不算通过。实际像素重新验收。没有覆盖失败源')
p.write_text(t,encoding='utf-8')
p=base/'record_visual_review.py';t=p.read_text('utf-8').replace('candidate_ui_v4','candidate_ui_v5').replace('_v4/','_v5/').replace("_v4'","_v5'");p.write_text(t,encoding='utf-8')
p=base/'deliver.py';t=p.read_text('utf-8')
old="'candidate_ui_v3: stale save guide / MI034 and invalid restore alias fixture / MI035; retained']"
assert old in t
t=t.replace(old,"'candidate_ui_v3: stale save guide / MI034 and invalid restore alias fixture / MI035; retained','candidate_ui_v4: Ready Enter selects Exit, no RESULT / MI036; retained']")
p.write_text(t,encoding='utf-8')
