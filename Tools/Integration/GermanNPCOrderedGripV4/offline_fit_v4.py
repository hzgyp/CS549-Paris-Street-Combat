"""Bounded partial pitch instead of over-cap full support target; no gate relaxation."""
from pathlib import Path
source=Path(__file__).with_name('offline_fit.py').read_text(encoding='utf-8-sig')
replacements={
    "OUT=BASE/'offline_v1'":"OUT=BASE/'offline_v4'",
    "assert all(n in rig.data.bones for n in names)":"assert set(names)-set(rig.data.bones.keys())=={'root'}; assert np.max(abs(mat(refs['root'])-np.eye(4)))<1e-6",
    "parents={n:rig.data.bones[n].parent.name if rig.data.bones[n].parent else None for n in names}":"parents={n:(rig.data.bones[n].parent.name if rig.data.bones[n].parent else 'root') if n!='root' else None for n in names}",
    "a=np.array([list(rig.matrix_world@rig.data.bones[n].head_local)+[1] for n in names])":"a=np.array([list(rig.matrix_world@rig.data.bones[n].head_local if n!='root' else rig.matrix_world.translation)+[1] for n in names])",
    "if 'TriggerGuard' in node['name']:part='guard'":"if node['name'].startswith('Guard_'):part='guard'\n            if node['name']=='Wood_UpperHandguard':part='stock'",
    "r['measured_pitch_deg']=math.degrees(pitch)":"r['desired_support_pitch_deg']=math.degrees(pitch); pitch=max(math.radians(-12),min(0,pitch)); r['measured_pitch_deg']=math.degrees(pitch)",
}
for old,new in replacements.items():
    assert source.count(old)==1,old
    source=source.replace(old,new)
exec(compile(source,str(Path(__file__)), 'exec'))
