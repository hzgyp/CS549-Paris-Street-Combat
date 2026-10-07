"""One user-region seating move and actual fore-end/palm 3D pivot rotation."""
import math
import transform_math as tm

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def sub(a,b): return [a[i]-b[i] for i in range(3)]
def add(a,b): return [a[i]+b[i] for i in range(3)]

def derive(measurement,before,forward,right):
    marks=measurement['landmarks']
    web=tm.point(before['bones']['hand_r'],marks['right_web_region']['hand_local_cm'])
    palm=tm.point(before['bones']['hand_l'],marks['left_palm_region']['hand_local_cm'])
    gun=before['gun_world']
    neck=tm.point(gun,marks['stock_neck_region']['gun_local_cm'])
    foreend=tm.point(gun,marks['foreend_lower_region']['gun_local_cm'])
    # Two requested screen-plane axes only. Hidden lateral depth remains
    # measured and reported, not silently "solved" from one picture.
    diff=sub(web,neck)
    horizontal=dot(diff,forward)
    delta=[horizontal*forward[i]+([0,0,1][i])*diff[2] for i in range(3)]
    assert horizontal<0 and delta[2]<0, 'Not the requested left/down direction'
    assert math.dist(delta,[0,0,0])<=4, 'Seating translation exceeds declared cap'
    seated={**gun,'t':add(gun['t'],delta)}
    pivot=add(neck,delta)
    a=sub(add(foreend,delta),pivot)
    # Actual recorded visible left-palm skin, with 1.5mm vertical diagnostic
    # clearance; this is not claimed to clear every palm/thumb triangle.
    target=add(palm,[0,0,.15])
    b=sub(target,pivot)
    ua=[v/math.dist(a,[0,0,0]) for v in a]
    ub=[v/math.dist(b,[0,0,0]) for v in b]
    cross=[ua[1]*ub[2]-ua[2]*ub[1],ua[2]*ub[0]-ua[0]*ub[2],ua[0]*ub[1]-ua[1]*ub[0]]
    theta=math.acos(max(-1,min(1,dot(ua,ub))))
    assert 0<math.degrees(theta)<=15, 'Rotation exceeds cap'
    raw=[*cross,1+dot(ua,ub)]
    norm=math.sqrt(dot(raw,raw))
    dq=[v/norm for v in raw]
    axis=[v/math.dist(cross,[0,0,0]) for v in cross]
    final={**seated,'q':tm.qmul(dq,seated['q']),
           't':add(pivot,tm.rotate(dq,sub(seated['t'],pivot)))}
    pivot_after=tm.point(final,marks['stock_neck_region']['gun_local_cm'])
    end_after=tm.point(final,marks['foreend_lower_region']['gun_local_cm'])
    assert math.dist(pivot,pivot_after)<1e-6
    assert end_after[2]<foreend[2], 'Fore-end did not lower toward support'
    return {'seating_delta_world_cm':delta,'seating_horizontal_cm':horizontal,
        'seating_length_cm':math.dist(delta,[0,0,0]),'seated_gun_world':seated,
        'pivot_world_cm':pivot,'hand_web_world_cm':web,
        'preserved_lateral_web_gap_cm':dot(sub(pivot,web),right),
        'rotation_world_axis':axis,'rotation_deg':math.degrees(theta),
        'rotation_quaternion_xyzw':dq,'final_gun_world':final,
        'left_palm_world_cm':palm,'support_target_world_cm':target,
        'foreend_before_world_cm':foreend,'foreend_after_world_cm':end_after,
        'support_point_gap_before_cm':math.dist(foreend,target),
        'support_point_gap_after_cm':math.dist(end_after,target),
        'support_projected_gap_after_cm':math.hypot(dot(sub(end_after,target),forward),end_after[2]-target[2]),
        'pivot_drift_cm':math.dist(pivot,pivot_after)}

if __name__=='__main__':
    from common import BASE,read
    m=read(BASE/'marked_web_surface_v6c/result.json')
    assert not m['errors'] and m['inputs_unchanged']
    p=read(BASE/'fit_v5/result.json')
    fit=derive(m,p['after'],[1,0,0],[0,1,0])
    print({k:v for k,v in fit.items() if k not in ('seated_gun_world','final_gun_world')})
