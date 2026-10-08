"""Meaningful coordinate, stack and boundary contracts independent of Paris data."""
import unittest

from grid_core import candidate_rows, cell_xy, connected_components, grid_spec, world_cell


def nav(polys):
    return {"active_tiles": 1, "exported_tiles": 1, "invalid_records": 0,
            "sampling_version": "native_specific_polygon_surface_v2", "polygons": polys}


def square(pid, z, lo=0, hi=200):
    return {"id": str(pid), "vertices_cm": [[lo,lo,z], [hi,lo,z], [hi,hi,z], [lo,hi,z]],
            "surface_cm": [(lo+hi)/2, (lo+hi)/2, z]}


class GridContract(unittest.TestCase):
    def test_centers_round_trip_and_axis(self):
        s = grid_spec(nav([square(1, 0, -200, 300)]))
        for c in range(s["columns"]):
            for r in range(s["rows"]):
                self.assertEqual(world_cell(s, *cell_xy(s,c,r)), (c,r))
        self.assertEqual(cell_xy(s,0,0), [-150,250])
        self.assertIsNone(world_cell(s,s["xmax_cm"],0))
        self.assertIsNone(world_cell(s,0,s["ymin_cm"]-1))

    def test_stacked_surfaces_do_not_merge(self):
        n = nav([square(1,0), square(2,400)])
        rows, omitted = candidate_rows(n,grid_spec(n))
        self.assertEqual(len(rows),8)
        self.assertFalse(omitted)
        at_cell = [r for r in rows if r['c']==0 and r['r']==0]
        self.assertEqual({r['p'] for r in at_cell},{'1','2'})

    def test_convex_shape_does_not_fill_bounding_box(self):
        p = {'id':'1','vertices_cm':[[0,0,0],[300,0,0],[0,300,0]],'surface_cm':[100,100,0]}
        rows, _ = candidate_rows(nav([p]),grid_spec(nav([p])))
        self.assertEqual(len(rows),6)
        self.assertNotIn((2,0),[(r['c'],r['r']) for r in rows])

    def test_oneway_links_do_not_prove_mutual_access(self):
        groups = connected_components([0,1,2],[(0,1),(1,0),(1,2)])
        self.assertEqual(groups,[[0,1],[2]])


if __name__ == '__main__': unittest.main()
