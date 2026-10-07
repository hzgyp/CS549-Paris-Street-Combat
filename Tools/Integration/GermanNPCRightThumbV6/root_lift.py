"""One measured intact-thumb root lift; mature distal bends and all other bones fixed."""
from pathlib import Path
import sys

# Reuse reviewed immutable data/contact loading, not its ten-pose loop or any
# stopped envelope/native animation owner. New result identity and mechanism.
p=Path(__file__).with_name('compare.py')
source=p.read_text(encoding='utf-8-sig')
source=source.replace("OUT=BASE/'compare_v1'","OUT=BASE/'root_lift_v1'")
source=source.replace("before=d['skin'];tri=", "cached_skin=d['skin'];tri=")
needle="    # Identify existing GLB stock triangle membership, not a guessed coordinate box."
fresh="""    before=np.zeros_like(rest)
    for j,n in enumerate(names):before+=weights[:,j,None]*transform(rest,bones[n]@np.linalg.inv(refs[j]))
    before/=weights.sum(1)[:,None]
    r['cached_skin_reencoding_error_cm']=float(np.linalg.norm(before-cached_skin,axis=1).max())
    assert r['cached_skin_reencoding_error_cm']<.01
"""+needle
assert source.count(needle)==1;source=source.replace(needle,fresh)
start=source.index('    options={}')
end=source.index('except Exception:')
source=source[:start]+'''    pad=before[tri[padfaces]].mean((0,1))
    root=bones['thumb_01_r'][:3,3]
    loc,normal,face,gap=top_tree.find_nearest(Vector(pad));assert loc is not None
    target=np.array(loc,float)+up*.1
    a=pad-root;b=target-root
    rotation=Vector(a).rotation_difference(Vector(b))
    angle=float(rotation.angle)*180/np.pi;assert angle<=70,('Root lift cap',angle)
    change=np.array(rotation.to_matrix(),float)
    new={n:m.copy() for n,m in bones.items()}
    new['thumb_01_r'][:3,:3]=change@bones['thumb_01_r'][:3,:3]
    for n in NAMES[1:]:new[n]=new[parents[n]]@np.linalg.inv(bones[parents[n]])@bones[n]
    after=np.zeros_like(rest)
    for j,n in enumerate(names):after+=weights[:,j,None]*transform(rest,new[n]@np.linalg.inv(refs[j]))
    after/=weights.sum(1)[:,None]
    c,crossings=contact(after);selfset=selfpairs(after)
    lengths_before=[float(np.linalg.norm(bones[NAMES[i+1]][:3,3]-bones[NAMES[i]][:3,3])) for i in range(2)]
    lengths_after=[float(np.linalg.norm(new[NAMES[i+1]][:3,3]-new[NAMES[i]][:3,3])) for i in range(2)]
    edge1=np.linalg.norm(after[edges[:,0]]-after[edges[:,1]],axis=1)
    locals_q={n:encode(np.linalg.inv(new[parents[n]])@new[n])['q'] for n in NAMES}
    c.update(identity='existing_idle_root_lift',clip=cache['clips']['owner_idle']['asset'],phase_s=0.0,
        local_rotations=locals_q,root_lift_deg=angle,root_axis_world=list(rotation.axis),
        pad_before_cm=pad.tolist(),target_upper_stock_cm=target.tolist(),
        target_upper_stock_face_id=int(upper[face]),radial_mismatch_cm=float(abs(np.linalg.norm(a)-np.linalg.norm(b))),
        true_unaffected_skin_cm=float(np.linalg.norm(after[~positive]-before[~positive],axis=1).max()),
        other_digit_shared_skin_cm=float(np.linalg.norm(after[shared]-before[shared],axis=1).max()) if shared.any() else 0,
        new_thumb_other_self_pairs=len(selfset-baseself),thumb_other_self_pairs=len(selfset),
        new_severe_edges=int(np.sum((edge1>edge0*3)&(edge1-edge0>2))),
        max_extra_edge_cm=float((edge1-edge0).max()),thumb_joint_lengths_before_cm=lengths_before,
        thumb_joint_lengths_after_cm=lengths_after)
    # Actual index contact skin, distinct from proximal mixed thumb/index boundary.
    im=weights[:,[names.index(n) for n in ('index_02_r','index_03_r')]].sum(1)>0
    c['distal_index_skin_delta_cm']=float(np.linalg.norm(after[im]-before[im],axis=1).max())
    r['chosen']=c;write(OUT/'result.json',r)
    assert c['true_unaffected_skin_cm']<.0001 and c['distal_index_skin_delta_cm']<.0001
    assert c['stock_faces']<baseline['stock_faces'] and c['pad_gap_cm']<baseline['pad_gap_cm']
    assert c['pad_height_over_upper_stock_cm']>baseline['pad_height_over_upper_stock_cm']
    assert not c['new_thumb_other_self_pairs'] and not c['new_severe_edges']
    assert max(abs(a-b) for a,b in zip(lengths_before,lengths_after))<.0001
    after_bones=dict(old['after_bones'])
    for n in NAMES:after_bones[n]=encode(new[n])
    assert all(after_bones[n]==old['after_bones'][n] for n in names if n not in NAMES)
    r.update(status='root_lift_candidate_requires_actual_views',bone_names=names,parents=parents,
        before_bones=old['after_bones'],after_bones=after_bones,before_gun_world=gun,after_gun_world=gun,
        mesh_world=old['mesh_world'],trigger_pivot_gun_cm=old['trigger_pivot_gun_cm'],
        stock_pivot_gun_cm=old['stock_pivot_gun_cm'],left_palm_target_world_cm=old['left_palm_target_world_cm'],
        new_severe_edges=c['new_severe_edges'],protected_bones=[n for n in names if n not in NAMES])
    np.savez_compressed(OUT/'geometry.npz',skin=after,before_skin=before,skin_triangles=tri,gun_local_cm=gp,
        gun_triangles=gt,rest_native_cm=rest,weights=weights,reference_matrices=refs)
    write(OUT/'binding.json',{'authorized_bones':list(NAMES),'local_rotations':locals_q,
        'mechanism':'Existing mature distal bends preserved; one measured thumb_01_r root lift',
        'root_axis_world':list(rotation.axis),'root_lift_deg':angle,'source_cache':row(CACHE),
        'gun_left_index_wrist_unchanged':True,'formal_selected':False})
''' + source[end:]
exec(compile(source,str(Path(__file__)),'exec'))
