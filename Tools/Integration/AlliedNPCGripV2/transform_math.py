"""Pure xyz/xyzw transform arithmetic; no Unreal constructor coercion."""
import math

def qmul(a,b):
    x,y,z,w=a
    X,Y,Z,W=b
    return [w*X+x*W+y*Z-z*Y, w*Y-x*Z+y*W+z*X,
            w*Z+x*Y-y*X+z*W, w*W-x*X-y*Y-z*Z]

def qinv(q):
    norm=sum(v*v for v in q)
    assert norm>1e-12
    return [-q[0]/norm,-q[1]/norm,-q[2]/norm,q[3]/norm]

def rotate(q,p):
    return qmul(qmul(q,[*p,0]),qinv(q))[:3]

def point(t,p):
    v=rotate(t['q'],[p[i]*t['s'][i] for i in range(3)])
    return [v[i]+t['t'][i] for i in range(3)]

def inverse_point(t,p):
    v=rotate(qinv(t['q']),[p[i]-t['t'][i] for i in range(3)])
    return [v[i]/t['s'][i] for i in range(3)]

def local_q(parent,child):
    return qmul(qinv(parent['q']),child['q'])

def angle(a,b):
    dot=abs(sum(x*y for x,y in zip(a,b)))
    norm=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
    return math.degrees(2*math.acos(min(1,dot/norm)))

def index_errors(old,new):
    return {child:angle(local_q(old[parent],old[child]),local_q(new[parent],new[child]))
        for child,parent in (('index_01_r','hand_r'),('index_02_r','index_01_r'),('index_03_r','index_02_r'))}

def landmarks(fit,before):
    old=fit['pose_source']
    pad_hand=inverse_point(old['bone_world']['hand_r'],point(old['mesh_world'],fit['pad_cm']))
    blade_local=inverse_point(old['gun_world'],point(old['mesh_world'],fit['blade_cm']))
    pad_world=point(before['bones']['hand_r'],pad_hand)
    blade_world=point(before['gun_world'],blade_local)
    delta=[pad_world[i]-blade_world[i] for i in range(3)]
    return {'pad_hand_cm':pad_hand,'blade_gun_cm':blade_local,'pad_world_cm':pad_world,
        'blade_before_world_cm':blade_world,'delta_world_cm':delta,
        'translation_length_cm':math.sqrt(sum(v*v for v in delta))}
