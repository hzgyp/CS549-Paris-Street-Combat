"""Private measured trajectories and shot counts; not a proposed map layout."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tmp/pure-map-survey-v1/plot-deps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
fontManager.addfont('C:/Windows/Fonts/msyh.ttc')
plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False,'font.size':10})
BASE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FormalMapVerificationV1'
summary=json.loads((BASE/'final_summary_v1_20261007/summary.json').read_text())
squad=json.loads((BASE/'squad_v1_20261007/result.json').read_text())
fig=plt.figure(figsize=(14,9),facecolor='#f4f6fa');grid=fig.add_gridspec(2,3,hspace=.43,wspace=.3)
fig.suptitle('正式角色地图验证 · 实测结果',fontsize=20,fontweight='bold',x=.07,ha='left',y=.98)
fig.text(.07,.925,'三个冻结路段｜全部坐标仅用于测试｜保留负面，未确定出生点、任务点或遭遇地点',fontsize=11,color='#465367')
for col,cid,title in ((0,'allied_follow_0_out','平地正向跟队：1名队员未到达'),(1,'allied_follow_1_back','窄路返程跟队：1名队员未到达')):
    ax=fig.add_subplot(grid[0,col]);c=next(c for c in squad['cases'] if c['id']==cid);origin=c['source_cm']
    for index,color in ((1,'#3578bc'),(2,'#d25438')):
        member=next(m for m in c['members'] if m['index']==index)
        rows=[next(r for r in s['members'] if r['index']==index) for s in c['samples']]
        points=[member['standing']['body_cm']]+[r['body_cm'] for r in rows]
        x=[(p[0]-origin[0])/100 for p in points];y=[(p[1]-origin[1])/100 for p in points]
        ax.plot(x,y,color=color,lw=2,label=f'盟军{index} 实际轨迹');ax.scatter(x[0],y[0],marker='s',s=40,color=color)
        last=rows[-1];goal=last['held_goal_cm'];gx,gy=(goal[0]-origin[0])/100,(goal[1]-origin[1])/100
        ax.scatter(gx,gy,marker='X',s=90,color=color);ax.scatter(x[-1],y[-1],s=55,facecolor='white',edgecolor=color,zorder=4)
        if index==2:
            ax.plot([x[-1],gx],[y[-1],gy],color=color,ls=':',lw=2)
            ax.annotate(f"距原生目标 {member['body_goal_error_cm']/100:.2f} m",((x[-1]+gx)/2,(y[-1]+gy)/2),xytext=(0,14),textcoords='offset points',color=color,fontsize=10)
    ax.set_title(title,fontsize=12,pad=12);ax.set_xlabel('相对测试起点 X（m）');ax.set_ylabel('相对测试起点 Y（m）')
    ax.grid(alpha=.15);ax.legend(loc='best',fontsize=8);ax.margins(.22)
    ax.text(.01,-.24,'□ 开始　○ 最后实体位置　× 原生 HeldGoal',transform=ax.transAxes,fontsize=8,color='#596779')
ax=fig.add_subplot(grid[0,2]);ax.axis('off')
ax.text(0,1,'本轮验证范围',fontsize=15,fontweight='bold',va='top')
stats=[('正式角色单人往返','36 / 36'),('盟军两人跟队','4 / 6'),('德军三人并行通行','6 / 6'),('双方对向通行','2 / 2'),('双方发现敌对 NPC','3 / 3'),('双方对敌开枪并造成伤害','2 / 3')]
for i,(label,value) in enumerate(stats):
    y=.83-i*.13;ax.text(0,y,label,fontsize=10);ax.text(1,y,value,ha='right',fontsize=13,fontweight='bold',color='#ba5139' if value in ('4 / 6','2 / 3') else '#20736b')
ax.text(0,-.05,'德军并行通行不等于领队编队。\n高差首次初始化失败单独保留。',fontsize=9,color='#596779',va='top')
for col,e,title in zip(range(3),summary['encounters'],('平地遭遇 · 负面','窄路遭遇 · 通过','高差遭遇 · 通过')):
    r=json.loads((BASE/e['identity']/'result.json').read_text());c=r['cases'][0];ax=fig.add_subplot(grid[1,col])
    times=[0]+[s['game_seconds']-c['started_game_seconds'] for s in c['samples']]
    for team,color,label in ((0,'#207b64','盟军'),(1,'#b35739','德军')):
        shots=[0]+[sum(row['resources'][3] for row in s['members'] if row['team']==team) for s in c['samples']]
        ax.step(times,shots,where='post',color=color,lw=2.2,label=f'{label} {shots[-1]}发')
    ax.set_title(title,fontsize=12,pad=12);ax.set_xlim(0,31);ax.set_ylim(-.2,8);ax.set_yticks(range(0,9,2))
    ax.set_xlabel('交战启用后的游戏时间（s）');ax.set_ylabel('原生累计射击次数');ax.grid(alpha=.15);ax.legend(loc='upper right',fontsize=9)
    ax.text(.01,-.24,f"双方已感知；敌对伤害已观察；阵亡 盟军{e['casualties_allied_german'][0]} / 德军{e['casualties_allied_german'][1]}",transform=ax.transAxes,fontsize=8,color='#596779')
fig.subplots_adjust(top=.865,bottom=.13,left=.065,right=.965)
fig.text(.065,.025,'来源：独立移动／交互审计。原生射击曲线含全部事务；敌对射击门槛另查目标、LOS与新序列增量。此图不代表全地图、平衡、视觉或MVP验收。',fontsize=9,color='#465367')
target=BASE/'final_summary_v1_20261007/formal_verification_results_20261007.png';assert not target.exists()
fig.savefig(target,dpi=130,facecolor=fig.get_facecolor());print(target)
