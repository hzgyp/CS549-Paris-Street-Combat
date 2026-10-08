import unittest
from collections import defaultdict

from planning_data import PlanningData


def fixture():
    d=PlanningData.__new__(PlanningData)
    coords=[(0,0),(1,0),(2,0),(0,1)]
    d.nodes=[{'id':i,'c':c,'r':r,'scope':'current','feet_cm':[c*100,r*100,0],'saved':True,'road_connected':True,
              'saved_road_connected':True,'group':0,'saved_group':0,'saved_node_ids':[i]} for i,(c,r) in enumerate(coords)]
    d.by_cell=defaultdict(list)
    for n in d.nodes:d.by_cell[(n['c'],n['r'])].append(n)
    d.links={(0,1),(1,0),(1,2),(2,1)};d.saved_pairs=d.links.copy();d.current_links=d.links.copy()
    d.outgoing=defaultdict(set,{0:{1},1:{0,2},2:{1}})
    d.space_cache={};d.sight=defaultdict(set)
    return d


class PurposeSafety(unittest.TestCase):
    def test_runtime_negative_cannot_supply_local_station_or_white_cell(self):
        d=fixture();d.nodes[1]['quarantined']=True
        self.assertFalse(d.eligible(d.nodes[1],'walk',True))
        self.assertEqual(d.local_sites(d.nodes[0],True,2),[0])
    def test_nearby_across_wall_is_not_assembly_space(self):
        d=fixture()
        self.assertEqual(set(d.local_sites(d.nodes[0],True,2)),{0,1,2})
        self.assertNotIn(3,d.local_sites(d.nodes[0],True,2))

    def test_full_link_does_not_certify_saved_navigation_link(self):
        d=fixture();d.current_links.remove((1,0))
        self.assertEqual(d.local_sites(d.nodes[0],True,2),[0])
        for n in d.nodes:n['scope']='survey'
        self.assertEqual(len(d.local_sites(d.nodes[0],False,2)),3)

    def test_missing_four_way_space_rejects_task_candidate(self):
        d=fixture()
        self.assertFalse(d.eligible(d.nodes[0],'task',True))

    def test_geometric_sight_is_required_for_encounter(self):
        d=fixture()
        self.assertFalse(d.eligible(d.nodes[1],'encounter',True))


if __name__=='__main__':unittest.main()
