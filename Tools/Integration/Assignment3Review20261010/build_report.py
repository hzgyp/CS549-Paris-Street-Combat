"""Two-page course report and corresponding Chinese review, from dated facts."""
import hashlib, json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'output/pdf'
EVIDENCE=ROOT/'tmp/assignment3-review-20261010'
pdfmetrics.registerFont(TTFont('ReviewZH','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('ReviewZHB','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('ReviewZH',normal='ReviewZH',bold='ReviewZHB',italic='ReviewZH',boldItalic='ReviewZHB')

def styles(lang):
    font='ReviewZH' if lang=='ZH' else 'Helvetica'
    bold='ReviewZHB' if lang=='ZH' else 'Helvetica-Bold'
    return font,bold,ParagraphStyle('body',fontName=font,fontSize=10.5,leading=15.2,textColor=HexColor('#202020'),wordWrap='CJK' if lang=='ZH' else None),ParagraphStyle('small',fontName=font,fontSize=9.5,leading=13.7,wordWrap='CJK' if lang=='ZH' else None)

def report(lang,metrics):
    zh=lang=='ZH';font,bold,body,small=styles(lang)
    path=OUT/f'Paris_Street_Combat_Assignment3_Progress_20261010_{lang}.pdf'
    c=canvas.Canvas(str(path),pagesize=(612,792));c.setTitle('Paris Street Combat - Assignment 3 Progress' if not zh else '巴黎街战 Assignment 3 进度报告')
    c.setAuthor('Paris Street Combat team')
    y=0
    def base(page):
        nonlocal y
        c.setFillColor(HexColor('#000000'));c.setFont(bold,17)
        c.drawString(44,749,'巴黎街战 | Assignment 3 进度报告' if zh else 'Paris Street Combat | Assignment 3 Progress')
        c.setFont(font,9);c.drawString(44,731,'2026年10月10日 | G1桥头MVP | 审查稿' if zh else '10 October 2026 | G1 bridgehead MVP | Review draft')
        c.setFont(font,8);c.drawString(44,29,'截止：2026年10月13日（团队确认）' if zh else 'Deadline: 13 October 2026 (team-confirmed)')
        c.drawRightString(568,29,f'{page} / 2');y=704
    def heading(text):
        nonlocal y
        if y<704:y-=12
        c.setFillColor(HexColor('#000000'));c.setFont(bold,12);c.drawString(44,y,text);y-=21
    def para(text,compact=False,gap=9):
        nonlocal y
        p=Paragraph(text,small if compact else body);_,h=p.wrap(524,700);p.drawOn(c,44,y-h);y-=h+gap
    def table(rows,widths):
        nonlocal y
        header=ParagraphStyle('tablehead',parent=small,fontName=bold)
        t=Table([[Paragraph(str(v),header if i==0 else small) for v in r] for i,r in enumerate(rows)],colWidths=widths)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#ECEFF1')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),.35,HexColor('#D6DADD'))]))
        _,h=t.wrap(524,700);t.drawOn(c,44,y-h);y-=h+12
    base(1)
    heading('计划与实际' if zh else 'Plan vs. reality')
    para('期中范围是：玩家带两名盟军过桥，消灭三名德军并攻占G1桥头；高亮存档圈提供按E确认存档。市中心、更多小队及全城战斗推迟。检查点由原提案应做项提升为本次核心功能。' if zh else 'The midterm slice is bridge crossing with two Allies, eliminating three German guards and capturing G1. A highlighted circle offers explicit E-to-save. The city-centre campaign, extra squads and full-city combat are deferred. Checkpoints moved from Should to core scope.')
    table(([
        ['技术支柱','已实现与验证范围'],
        ['动画','保留现有士兵、手指和枪械动作；已展示走、跑、静步、跳跃、蹲伏、匍匐、开火与换弹。音效V2人工复验通过；完整动态接触仍有未验项。'],
        ['碰撞检测','角色与环境碰撞，以及相机/枪口遮挡、友军挡弹有功能回归证据。碎石能阻挡匍匐；不宣称所有墙角和窄路均通过。'],
        ['寻路与导航','使用UE原生导航；原两名盟军过桥/归队及目的地预约、有限重规划已有有界验证。未实现可选自写A*。'],
        ['NPC AI / 行为树','敌我过滤、跟随/归队、驻守、追击/攻击、限时搜索与回职责已有有界证据。G1初始角色为守卫；巡逻仅在测试配置验证。']
    ] if zh else [
        ['Technical pillar','Implemented behavior and evidence scope'],
        ['Animation','Original soldiers, finger poses and weapon actions retained; walk/run/quiet/jump/crouch/prone/fire/reload demonstrated. Audio V2 passed human review; full dynamic contact remains open.'],
        ['Collision detection','Movement, camera/muzzle obstruction and friendly blocking have regression evidence. Rubble blocks prone travel; universal corner/narrow-route coverage is not claimed.'],
        ['Pathfinding / navigation','Native UE navigation: tested two-Allied bridge/regroup, distinct reservations and bounded replanning. Optional custom A* is omitted.'],
        ['NPC AI / Behavior Trees','Bounded tests: faction filtering, follow/regroup, guard, chase/attack, timed search/return. G1 starts with guards; patrol used a separate test configuration.']
    ]),[116,408])
    para('实机录像包含消灭守卫、存档后弹药变化与恢复、尸体直接恢复死亡终态，以及德军真实击杀玩家后的F6重开。音效V2已人工复验；团队于10月10日确认另一台组员电脑可运行、可玩，此项按人工报告通过，不冒充远程哈希审计。' if zh else 'Real gameplay footage includes elimination, save/change/load of ammunition, terminal corpse restoration, and genuine enemy damage/death followed by F6 restart. Audio V2 passed human playtesting. On 10 October, the team confirmed a teammate\'s second computer runs the game and is playable: Pass by human attestation, not a remote hash audit.',compact=True)
    heading('当前固定人数性能测量' if zh else 'Performance at the existing population')
    para('正式Game 53ab36d9…950aec；i9-12900F、RTX 3080 10GB、32GB；1080p High、渲染100%、光追/VSync关闭、无帧率上限、纹理池1536MiB。Windows Development离屏渲染、正常音频、OBS未录制。三轮原生CSV各12000帧，排除预定前30秒预热，保留之后全部帧。Ready画面暂停NPC决策：这三轮是原始六人场景的渲染基线。' if zh else 'Normal Game 53ab36d9…950aec; i9-12900F, RTX 3080 10 GB, 32 GB; 1080p High, 100% rendering, RT/VSync off, uncapped, 1536 MiB pool. Windows Development uses offscreen rendering, normal audio and idle OBS. Each of three native CSVs has 12000 frames; only the declared first 30 seconds are warmup. Ready gates NPC brains off: these are initial six-person render baselines.',compact=True,gap=7)
    rows=[['轮次' if zh else 'Run','测量秒数' if zh else 'Seconds','平均FPS' if zh else 'Mean FPS','p95 ms','最大ms' if zh else 'Max ms']]
    for r in metrics['runs']:rows.append([r['case'],f"{r['seconds']:.2f}",f"{r['fps']:.2f}",f"{r['p95_ms']:.2f}",f"{r['max_ms']:.2f}"])
    table(rows,[70,114,114,113,113])
    fps='/'.join(f"{r['fps']:.2f}" for r in metrics['runs'])
    d=metrics['dynamic_workload'];a=d['active_mission']
    para((f'渲染基线三轮{fps} FPS。另一次V6普通输入辅助（Game a6015c94…799472）真实过桥、交战、存读档通过；原五名NPC未增加，真实死亡减少活人数。Crossing至Won近似窗口{a["seconds"]:.2f}秒：平均{a["fps"]:.2f} FPS，p95 {a["p95_ms"]:.2f} ms；完整预热后记录最大帧{d["max_ms"]:.2f} ms含实际读档阻塞。' if zh else f'Render baselines: {fps} FPS. One V6 normal-input helper workload (Game a6015c94…799472) passes real bridge/combat/save/load with the original five NPCs; genuine deaths reduce live count. Its approximate Crossing-to-Won window is {a["seconds"]:.2f}s: {a["fps"]:.2f} mean FPS, p95 {a["p95_ms"]:.2f}ms. The full warmed capture has a {d["max_ms"]:.2f}ms maximum frame including actual load blocking.'),compact=True,gap=5)
    para('辅助含输入/20Hz记录开销；窗口按原生日志时间近似对齐，不是三轮正式Game动态测试或持续六人交战容量。旧版10月8日路线51.21-52.00 FPS仍保留。当前活跃负载的60 FPS门槛未宣称通过；本机硬件、场景和引擎的各自影响未隔离。' if zh else 'Helper input/20 Hz telemetry overhead and approximate log/CSV timing are disclosed. This is not three normal-Game active runs or sustained six-live capacity. Older 8 October route results of 51.21-52.00 FPS remain. The active-workload 60 FPS gate is not declared passed; hardware, scene and engine contributions are not isolated.',compact=True,gap=0)
    assert y>51,('Page1 overflow',lang,y)
    c.showPage();base(2)
    heading('AI工具效用与建模成本' if zh else 'AI utility and model-production cost')
    para('团队没有成员会3D建模。AI辅助对本项目的实现起到了关键作用：Codex帮助拆分需求、编写和检查UE集成代码、排查导航/碰撞/动作/存档问题、构建验证工具、整理失败案例和文档；ImageGen用于概念图与HUD设计参考。游戏不依赖运行时大语言模型或外部AI API。' if zh else 'No team member has 3D-modeling expertise. AI assistance was essential to this team\'s workflow: Codex helped decompose requirements, write and audit UE integration code, diagnose navigation/collision/animation/save issues, build validation tools, and document failures. ImageGen supplied concept and HUD design references. The game requires no runtime LLM or external AI API.')
    para('但AI辅助没有消除资产生产成本。精细人物和环境主要采用购买的现成资产；购买后仍需检查骨架、动作、材质、武器绑定及引擎兼容性。按团队估算，模型处理与适配总共花了近10个工作日，超过最初预期；这不是单独的AI推理时长。' if zh else 'AI assistance did not remove asset-production costs. Detailed characters and environment assets primarily came from purchased, existing asset packages. They still required rig, animation, material, weapon-binding and engine-compatibility checks. The team estimates nearly ten working days of model processing and adaptation, longer than expected; this is total adaptation effort, not AI inference time.')
    para('最耗时的问题之一是手部与枪械贴合：第一人称构图、盟军/德军的手掌和手指、枪托位置、原动作及枪口检测必须同时协调。单张静止图看起来改善，并不能证明运动、换弹或接触正确；出现不自然姿态、遮挡或穿插时，需要反复测量和人工审查。现有模型、已接受手指姿态及枪械/弹药/存档逻辑继续保留。' if zh else 'Hand-to-weapon fit was particularly expensive: first-person framing, Allied/German palms and fingers, stock placement, original actions and muzzle collision all had to agree. An improved still image did not prove correct movement, reload or contact. Unnatural poses, obstruction and penetration required measurement and human review. Existing models, accepted finger poses and validated weapon/ammunition/save logic remain the basis.')
    para('另一个困难是缺少合适的德军枪械。尝试新建枪模可以得到可辨认底模，但分件、纹理、拓扑和活动机械部件仍需大量处理，不能直接作为成熟成品。此前AI主导的精细人物自建路线经过38轮仍未达到团队生产质量，已经停止。经验是优先购买兼容资产，把AI用于有限适配和验证；不再让精细自建人物成为交付依赖。' if zh else 'A suitable German firearm was another asset gap. Attempts to create a new rifle produced a recognizable base, but part separation, texture quality, topology and moving mechanical components still needed substantial adaptation. A separate AI-led detailed soldier-production route remained below the team\'s required quality after 38 iterations and was stopped. The resulting strategy is to purchase compatible finished assets and use AI for bounded adaptation and validation, rather than depend on detailed character creation from scratch.')
    para('因此，AI的收益是帮助缺乏建模经验的团队完成集成、诊断和迭代，而不是保证“自动生成即可使用”或必然按预期节省时间。模型返工确实挤压了玩法打磨和交付准备的时间；这里没有把估计成本当作受控效率实验。' if zh else 'AI enabled a team without modeling expertise to integrate, diagnose and iterate; it did not guarantee immediately usable generated assets or the expected schedule. Model rework reduced time available for gameplay polish and delivery. These are qualitative workflow findings and a team effort estimate, not a controlled productivity experiment.')
    heading('通往最终版本的路线图' if zh else 'Roadmap to the final version')
    para('10-12日：保持当前1玩家/2盟军/3德军，不再执行新增12/18人方案。按固定人数补充动态瓶颈与重试验证；完成视频人工审查，更新当前性能范围说明；统一源码、构建和报告，核对评审下载入口及YouTube/Vimeo链接。13日：团队最后核对和提交。后续最终版再扩展市中心任务、行为覆盖和针对性性能优化。' if zh else '10-12 October: retain one player/two Allies/three Germans; retire the 12/18-person expansion. Complete dynamic bottleneck/retry coverage at this population, review the video and update the performance scope, align source/build/report identities, and verify reviewer download and YouTube/Vimeo access. On 13 October, the team checks and submits. The final project can extend city-centre missions, behavior coverage and targeted performance work.',compact=True)
    heading('交付状态' if zh else 'Delivery status')
    para('公开源码：<link href="https://github.com/hzgyp/CS549-Paris-Street-Combat" color="#245572">github.com/hzgyp/CS549-Paris-Street-Combat</link>，选定版本对应提交656db9b；商业资产原件单独私有恢复。试玩包已在团队SFTP共享并获另一台电脑人工验证；课程评审下载入口仍须核对。实机视频审查稿2分41秒，含英文字幕、A/Michael AI配音、游戏原声和真实死亡重开；尚未确认人工最终通过或YouTube/Vimeo上传。Assignment 2和10月13日截止日期由团队确认；未宣称课程已提交。' if zh else 'Public source: <link href="https://github.com/hzgyp/CS549-Paris-Street-Combat" color="#245572">github.com/hzgyp/CS549-Paris-Street-Combat</link>, selected-build commit 656db9b; commercial source assets require separate private licensed restoration. The team SFTP build passed second-machine human validation; reviewer download access still needs verification. The real-time video draft is 2:41 with English subtitles, A/Michael AI narration, game audio and genuine death/restart; final human approval and YouTube/Vimeo upload are not yet confirmed. Assignment 2 and the 13 October deadline are team-confirmed. Submission is not claimed.',compact=True,gap=0)
    assert y>51,('Page2 overflow',lang,y)
    c.save();return path

def main():
    metrics=json.loads((EVIDENCE/'performance/SUMMARY.json').read_text('utf-8'))
    assert len(metrics['runs'])==3 and all(r['seconds']>=60 for r in metrics['runs'])
    OUT.mkdir(parents=True,exist_ok=True)
    outputs=[report(lang,metrics) for lang in ('EN','ZH')]
    receipt={'date':'2026-10-10','outputs':[{'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs],'source_game_sha256':metrics['game_sha256'],'second_machine':'human-reported pass','new_NPCs':0,'layout_qa':'pending final rendered inspection'}
    (EVIDENCE/'REPORT_RECEIPT.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n','utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
