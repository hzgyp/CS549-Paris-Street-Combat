"""Static diagnostic figure of recorded animation samples and actual sound edges."""
import json,sys
from common import OUT,save,row
sys.path.insert(0,str(OUT/'plot_deps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def main():
    case=OUT/'checks_solo/actions';paths=list(case.glob('audio_events_*.json'));assert len(paths)==1
    data=json.loads(paths[0].read_text('utf-8-sig'));samples=data['foot_samples'];events=data['events']
    motion=json.loads((case/'result.json').read_text('utf-8-sig'))['samples']
    def interval(name):
        start=next(e['time'] for e in motion if e['step']==name)
        end=max(e['time'] for e in motion if e['step']==name)
        return start,end
    fig,axes=plt.subplots(3,1,figsize=(12,8),constrained_layout=True)
    windows=[]
    for ax,name in zip(axes,['walk','run','slow']):
        start,end=interval(name);end=min(end,start+4.2);rows=[s for s in samples if start<=s['time']<=end]
        ax.plot([s['time']-start for s in rows],[s['left_z'] for s in rows],label='Evaluated left foot',color='#1764a3')
        ax.plot([s['time']-start for s in rows],[s['right_z'] for s in rows],label='Evaluated right foot',color='#b24b25')
        hits=[e for e in events if start<=e['time']<=end and e['contact_foot']!='None']
        for e in hits:ax.axvline(e['time']-start,color='#1764a3' if e['contact_foot']=='foot_l' else '#b24b25',alpha=.6,ls='--')
        ax.set_title(name.capitalize()+' / dashed lines = actual player audio events');ax.set_ylabel('Foot joint Z in mesh (cm)');ax.set_xlabel('Time from input phase (s)');ax.grid(alpha=.2)
        windows.append(dict(phase=name,start=start,end=end,events=hits))
    axes[0].legend(loc='upper right');fig.suptitle('Existing animation contact phase and emitted steps\nNot sole-floor collision or human listening acceptance')
    path=case/'foot_contact_plot.png';fig.savefig(path,dpi=140);plt.close(fig)
    save(case/'foot_contact_plot.json',dict(figure=row(path,case),windows=windows))
    print(path)
if __name__=='__main__':main()
