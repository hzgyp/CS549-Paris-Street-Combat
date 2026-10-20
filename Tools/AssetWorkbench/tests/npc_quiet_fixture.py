"""Explicit nonlethal Follow mode for retained navigation/perception regressions.

Default Scout and live damage are exercised separately by test_npc_squad.
"""
from app.npc_engine import World as TacticalWorld


class World(TacticalWorld):
    def __init__(self, *args, parameters=None, **kwargs):
        super().__init__(*args, parameters={'allied_mode': 0, 'combat_damage': 0, 'search_duration': 6, 'tactical_coordination': 0, **(parameters or {})}, **kwargs)
