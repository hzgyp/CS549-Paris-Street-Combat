import unittest
from vehicle_prefix import intersects, near_case

class ConservativeExclusion(unittest.TestCase):
    def test_path_crosses_with_both_endpoints_outside(self):
        self.assertTrue(intersects((-10, 5), (20, 5), (0, 0, 10, 10)))
        self.assertFalse(intersects((-10, 11), (20, 11), (0, 0, 10, 10)))

    def test_tangent_and_zero_length_are_excluded(self):
        self.assertTrue(intersects((-1, -1), (0, 0), (0, 0, 10, 10)))
        self.assertTrue(intersects((5, 5), (5, 5), (0, 0, 10, 10)))
        self.assertFalse(intersects((-1, 5), (-1, 5), (0, 0, 10, 10)))

    def test_height_cannot_evade_xy_exclusion(self):
        case = {"source_cm": [-10, 5, 10000], "goal_cm": [20, 5, 10000],
                "path_cm": [[-10, 5, 10000], [20, 5, 10000]]}
        self.assertTrue(near_case(case, (0, 0, 10, 10)))

    def test_actual_trace_checked_even_when_query_goes_around(self):
        case = {"source_cm": [-10, 5, 0], "goal_cm": [20, 5, 0],
                "path_cm": [[-10, 5, 0], [-10, 20, 0], [20, 20, 0], [20, 5, 0]],
                "samples": [{"body_cm": [-10, 5, 100]}, {"body_cm": [20, 5, 100]}]}
        self.assertTrue(near_case(case, (0, 0, 10, 10)))

if __name__ == "__main__": unittest.main()
