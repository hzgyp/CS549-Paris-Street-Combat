"""Physical-meter conservative station stencils over measured 25 cm reciprocal links."""
import numpy as np

def filters(c,r,z,group,base,a,b):
    size=len(c);origin=np.arange(size,dtype=np.int32)
    # Successors only use reciprocal edges passed by the caller. One nearest-height
    # surface per cardinal direction; omitting alternatives is conservative.
    valid=base[a]&base[b]&(group[a]==group[b])&(np.abs(z[a]-z[b])<=20)
    a,b=a[valid],b[valid]
    direction=np.where(c[b]>c[a],0,np.where(c[b]<c[a],1,np.where(r[b]>r[a],2,3)))
    key=a.astype(np.int64)*4+direction
    order=np.lexsort((np.abs(z[a]-z[b]),key));key=key[order];b=b[order]
    keep=np.r_[True,key[1:]!=key[:-1]] if len(key) else np.zeros(0,dtype=bool)
    successors=np.full(size*4,-1,dtype=np.int32);successors[key[keep]]=b[keep];successors=successors.reshape(size,4)
    def path(dx,dy,xfirst=True):
        targets=origin.copy();alive=base.copy()
        axes=[(abs(dx)*4,0 if dx>0 else 1),(abs(dy)*4,2 if dy>0 else 3)]
        if not xfirst:axes.reverse()
        for steps,d in axes:
            for _ in range(steps):
                targets=successors[np.maximum(targets,0),d]
                alive&=(targets>=0)
                alive&=np.abs(z[np.maximum(targets,0)]-z)<=20
        return alive
    count2=base.astype(np.uint8);count3=count2.copy()
    task=base.copy()
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):task&=path(dx,dy)
    for dx in range(-3,4):
        for dy in range(-3,4):
            d2=dx*dx+dy*dy
            if not d2 or d2>9:continue
            admitted=path(dx,dy)
            if dx and dy:admitted|=path(dx,dy,False)
            count3+=admitted
            if d2<=4:count2+=admitted
    return count2,count3,task
