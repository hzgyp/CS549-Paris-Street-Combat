import unittest
from model import ActionResult, MoveTracker, NPCMemory, ReservationCoordinator, friendly_hit_contract


class NPCInteractionContractTests(unittest.TestCase):
    def test_private_last_seen_and_no_hidden_tracking(self):
        a = NPCMemory("enemy-1", 1, "Guard")
        b = NPCMemory("enemy-2", 1, "Patrol")
        self.assertTrue(a.observe("player", 0, True, (10, 20, 30), 1.0))
        self.assertIsNone(b.last_seen_position)
        a.observe("player", 0, False, (10, 20, 30), 2.0)
        hidden_new_position = (999, 999, 999)
        self.assertEqual(a.last_seen_position, (10, 20, 30))
        self.assertNotEqual(a.last_seen_position, hidden_new_position)

    def test_faction_filter_and_search_timeout(self):
        german = NPCMemory("enemy-1", 1, "Guard")
        self.assertFalse(german.observe("enemy-2", 1, True, (1, 2, 3), 0.0))
        german.observe("player", 0, True, (4, 5, 6), 1.0)
        german.observe("player", 0, False, (4, 5, 6), 2.0, search_duration=15.0)
        self.assertTrue(german.search_active(16.9))
        self.assertTrue(german.expire_search(17.0))
        self.assertFalse(german.search_active(17.0))

    def test_chase_budget_survives_target_change(self):
        ally = NPCMemory("ally-1", 0, "Ally")
        ally.begin_chase(7, (0, 0, 0))
        ally.add_chase_segment((0, 0, 0), (600, 0, 0))
        ally.observe("enemy-2", 1, True, (700, 0, 0), 1.0)
        ally.begin_chase(7, (600, 0, 0))
        ally.add_chase_segment((600, 0, 0), (1100, 0, 0))
        self.assertEqual(ally.chase_travel_distance, 1100)
        self.assertFalse(ally.chase_allowed(player_distance=800))

    def test_reservation_retained_on_arrival_and_released_on_death(self):
        c = ReservationCoordinator()
        first = c.reserve("ally-1", (0, 0, 0), 1)
        self.assertIsNotNone(first)
        c.arrive(first)
        self.assertIn(first, c.reservations)
        self.assertIsNone(c.reserve("ally-2", (100, 0, 0), 2))
        self.assertTrue(c.release(first, "dead"))

    def test_chase_budget_survives_new_bt_task(self):
        ally = NPCMemory("ally-1", 0, "Ally")
        ally.begin_chase(7, (0, 0, 0))
        ally.add_chase_segment((0, 0, 0), (600, 0, 0))
        ally.begin_chase(8, (600, 0, 0))
        ally.add_chase_segment((600, 0, 0), (1100, 0, 0))
        self.assertEqual(ally.chase_origin, (0, 0, 0))
        self.assertFalse(ally.chase_allowed(800))
        ally.end_chase_after_regroup()
        ally.begin_chase(9, (100, 0, 0))
        self.assertEqual(ally.chase_travel_distance, 0)

    def test_restore_clears_search_and_chase(self):
        npc = NPCMemory("enemy-1", 1, "Guard")
        npc.observe("player", 0, True, (4, 5, 6), 1)
        npc.observe("player", 0, False, (999, 999, 999), 2)
        npc.begin_chase(7, (0, 0, 0))
        npc.add_chase_segment((0, 0, 0), (600, 0, 0))
        npc.restore(1)
        self.assertIsNone(npc.target_id)
        self.assertIsNone(npc.last_seen_position)
        self.assertFalse(npc.search_active(3))
        self.assertIsNone(npc.chase_task_id)
        self.assertEqual(npc.chase_travel_distance, 0)

    def test_generation_and_duplicate_request(self):
        npc = NPCMemory("enemy-1", 1, "Guard", restore_generation=3)
        start = npc.request_action("Fire", 10, 20, 3, armed=True, loaded=1)
        self.assertEqual(start.status, ActionResult.STARTED)
        self.assertEqual(npc.request_action("Fire", 10, 20, 3).status, ActionResult.RUNNING)
        npc.restore(4)
        self.assertEqual(npc.finish_action(10, 20, 3).reason, "stale callback")

    def test_unarmed_rejected_and_friendly_damage_modes(self):
        npc = NPCMemory("enemy-1", 1, "Guard")
        self.assertEqual(npc.request_action("Fire", 1, 1, 0, armed=False).status, ActionResult.REJECTED)
        off = friendly_hit_contract(0, 0, False, 35)
        on = friendly_hit_contract(0, 0, True, 35)
        enemy = friendly_hit_contract(0, 1, False, 35)
        self.assertTrue(off["blocks_projectile"] and on["blocks_projectile"])
        self.assertEqual((off["damage"], on["damage"], enemy["damage"]), (0.0, 35, 35))

    def test_move_continuity_stop_and_bounded_replan(self):
        move = MoveTracker(9, 4, 2, (0, 0, 0), (0, 0, 0),
                           ((0, 0, 0), (100, 0, 0), (200, 0, 0)))
        self.assertEqual(move.sample((60, 0, 0)), 60)
        self.assertEqual(move.sample((125, 0, 0)), 65)
        self.assertTrue(move.request_replan())
        self.assertTrue(move.request_replan())
        self.assertFalse(move.request_replan())
        move.stop((150, 0, 0))
        self.assertTrue(move.remains_stopped((150.5, 0, 0)))
        self.assertFalse(move.remains_stopped((199.2, 0, 0)))

    def test_move_callback_generation_and_request_isolation(self):
        move = MoveTracker(3, 8, 11, (0, 0, 0), (0, 0, 0), ((0, 0, 0),))
        self.assertTrue(move.callback_is_current(3, 8, 11))
        self.assertFalse(move.callback_is_current(3, 7, 11))
        self.assertFalse(move.callback_is_current(3, 8, 10))


if __name__ == "__main__":
    unittest.main(verbosity=2)
