import unittest
import numpy as np
from fine_filters import filters

class FineFilters(unittest.TestCase):
    def line(self,remove=None):
        c=np.arange(25,dtype=np.int32);r=c*0;z=c*0.;g=c*0;base=np.ones(25,dtype=bool)
        a=[];b=[]
        for i in range(24):
            if i==remove:continue
            a.extend((i,i+1));b.extend((i+1,i))
        return filters(c,r,z,g,base,np.array(a),np.array(b))
    def test_station_spacing_stays_one_meter(self):
        two,three,task=self.line();self.assertEqual(two[12],5);self.assertEqual(three[12],7);self.assertFalse(task.any())
    def test_missing_intermediate_quarter_meter_link(self):
        two,_,_=self.line(13);self.assertEqual(two[12],3)
    def test_task_requires_complete_four_meter_arms(self):
        coords=[(0,0)]+[(dx*k,dy*k) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)) for k in range(1,5)]
        lookup={xy:i for i,xy in enumerate(coords)};a=[];b=[]
        for xy,i in lookup.items():
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                j=lookup.get((xy[0]+dx,xy[1]+dy))
                if j is not None:a.append(i);b.append(j)
        c,r=map(np.array,zip(*coords));n=len(c)
        args=(c,r,np.zeros(n),np.zeros(n,dtype=int),np.ones(n,dtype=bool))
        _,_,task=filters(*args,np.array(a),np.array(b));self.assertTrue(task[0])
        keep=[k for k,(i,j) in enumerate(zip(a,b)) if set((i,j))!={1,2}]
        _,_,task=filters(*args,np.array(a)[keep],np.array(b)[keep]);self.assertFalse(task[0])
    def test_quarantine_blocks_local_sites(self):
        c=np.arange(9);n=len(c);base=np.ones(n,dtype=bool);base[5]=False
        a=np.r_[np.arange(8),np.arange(1,9)];b=np.r_[np.arange(1,9),np.arange(8)]
        two,_,_=filters(c,c*0,c*0.,c*0,base,a,b);self.assertEqual(two[4],2);self.assertEqual(two[5],0)

if __name__=='__main__':unittest.main()
