"""Deterministic Lane B contract model. Reference for Blueprint implementation, not runtime AI."""
from dataclasses import dataclass, field
from enum import Enum
from math import dist


class ActionResult(str, Enum):
    STARTED = "Started"
    RUNNING = "Running"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


@dataclass(frozen=True)
class ActionReply:
    status: ActionResult
    reason: str
    task_id: int
    request_id: int
    restore_generation: int


@dataclass
class MoveTracker:
    """Observable movement contract used by the native task adapter."""
    task_id: int
    request_id: int
    restore_generation: int
    origin: tuple[float, float, float]
    last_position: tuple[float, float, float]
    path_points: tuple[tuple[float, float, float], ...]
    retries: int = 0
    distance_travelled: float = 0.0
    stopped_position: tuple[float, float, float] | None = None

    def sample(self, position):
        position = tuple(position)
        segment = dist(self.last_position, position)
        self.distance_travelled += segment
        self.last_position = position
        return segment

    def request_replan(self):
        if self.retries >= 2:
            return False
        self.retries += 1
        return True

    def stop(self, position):
        self.sample(position)
        self.stopped_position = tuple(position)

    def remains_stopped(self, position, tolerance=1.0):
        return self.stopped_position is not None and dist(self.stopped_position, tuple(position)) <= tolerance

    def callback_is_current(self, task_id, request_id, generation):
        return (task_id, request_id, generation) == (
            self.task_id, self.request_id, self.restore_generation
        )


@dataclass
class NPCMemory:
    npc_id: str
    team_id: int
    role: str
    restore_generation: int = 0
    target_id: str | None = None
    last_seen_position: tuple[float, float, float] | None = None
    last_seen_time: float | None = None
    has_visible_target: bool = False
    search_deadline: float | None = None
    chase_task_id: int | None = None
    chase_origin: tuple[float, float, float] | None = None
    chase_travel_distance: float = 0.0
    current_action: str | None = None
    current_task_id: int | None = None
    current_request_id: int | None = None
    retry_count: int = 0
    reservation_id: int | None = None
    trace: list[dict] = field(default_factory=list)

    def observe(self, target_id, target_team, visible, position, now, search_duration=15.0):
        if target_team == self.team_id:
            self.trace.append({"condition": "candidate friendly", "result": "Rejected", "reason": "same team"})
            return False
        if visible:
            self.target_id = target_id
            self.last_seen_position = tuple(position)
            self.last_seen_time = now
            self.has_visible_target = True
            self.search_deadline = None
            return True
        if self.target_id == target_id and self.has_visible_target:
            self.has_visible_target = False
            self.search_deadline = now + search_duration if self.team_id == 1 else None
        return False

    def search_active(self, now):
        return (
            self.team_id == 1
            and not self.has_visible_target
            and self.last_seen_position is not None
            and self.search_deadline is not None
            and now < self.search_deadline
        )

    def expire_search(self, now):
        if self.search_deadline is not None and now >= self.search_deadline:
            self.target_id = None
            self.last_seen_position = None
            self.last_seen_time = None
            self.search_deadline = None
            return True
        return False

    def begin_chase(self, task_id, position):
        # A BT restart/new target may issue a new task, but not a new budget.
        # Only completed regroup or lifecycle restore ends this chase episode.
        if self.chase_task_id is None:
            self.chase_task_id = task_id
            self.chase_origin = tuple(position)
            self.chase_travel_distance = 0.0

    def add_chase_segment(self, previous, current):
        self.chase_travel_distance += dist(previous, current)

    def chase_allowed(self, player_distance, max_distance=1000.0):
        return player_distance <= max_distance and self.chase_travel_distance <= max_distance

    def end_chase_after_regroup(self):
        self.chase_task_id = None
        self.chase_origin = None
        self.chase_travel_distance = 0.0

    def request_action(self, action, task_id, request_id, generation, *, armed=True, loaded=1, reserve=1):
        if generation != self.restore_generation:
            return ActionReply(ActionResult.REJECTED, "stale restore generation", task_id, request_id, generation)
        if self.current_action is not None:
            if (task_id, request_id) == (self.current_task_id, self.current_request_id):
                return ActionReply(ActionResult.RUNNING, "same request already running", task_id, request_id, generation)
            return ActionReply(ActionResult.REJECTED, "another action running", task_id, request_id, generation)
        if action == "Fire" and (not armed or loaded <= 0):
            return ActionReply(ActionResult.REJECTED, "no valid armed discharge", task_id, request_id, generation)
        if action == "Reload" and (not armed or loaded > 0 or reserve <= 0):
            return ActionReply(ActionResult.REJECTED, "reload admission failed", task_id, request_id, generation)
        self.current_action, self.current_task_id, self.current_request_id = action, task_id, request_id
        return ActionReply(ActionResult.STARTED, "admitted", task_id, request_id, generation)

    def finish_action(self, task_id, request_id, generation, cancelled=False):
        if generation != self.restore_generation or (task_id, request_id) != (self.current_task_id, self.current_request_id):
            return ActionReply(ActionResult.REJECTED, "stale callback", task_id, request_id, generation)
        self.current_action = self.current_task_id = self.current_request_id = None
        return ActionReply(ActionResult.CANCELLED if cancelled else ActionResult.COMPLETED,
                           "cancelled" if cancelled else "physical completion observed", task_id, request_id, generation)

    def restore(self, generation):
        self.restore_generation = generation
        self.current_action = self.current_task_id = self.current_request_id = None
        self.retry_count = 0
        self.reservation_id = None
        self.target_id = self.last_seen_position = self.last_seen_time = None
        self.has_visible_target = False
        self.search_deadline = None
        self.end_chase_after_regroup()


@dataclass
class Reservation:
    reservation_id: int
    npc_id: str
    point: tuple[float, float, float]
    task_id: int
    arrived: bool = False


class ReservationCoordinator:
    def __init__(self, minimum_separation=150.0):
        self.minimum_separation = minimum_separation
        self.reservations: dict[int, Reservation] = {}
        self.next_id = 1

    def reserve(self, npc_id, point, task_id):
        if any(dist(point, row.point) < self.minimum_separation for row in self.reservations.values()):
            return None
        rid = self.next_id
        self.next_id += 1
        self.reservations[rid] = Reservation(rid, npc_id, tuple(point), task_id)
        return rid

    def arrive(self, reservation_id):
        self.reservations[reservation_id].arrived = True

    def release(self, reservation_id, reason):
        assert reason in {"reassigned", "failed", "dead", "restored"}
        return self.reservations.pop(reservation_id, None) is not None


def friendly_hit_contract(shooter_team, target_team, friendly_fire_enabled, normal_damage):
    friendly = shooter_team == target_team
    return {
        "blocks_projectile": True,
        "damage": normal_damage if (not friendly or friendly_fire_enabled) else 0.0,
        "retaliation_or_team_change": False,
    }
