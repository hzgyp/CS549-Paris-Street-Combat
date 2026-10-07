"""Reference event contract; motion values remain in licensed native assets."""
from dataclasses import dataclass


@dataclass
class RecoilObserver:
    seen_shot: int = 0
    seen_generation: int = 0
    observed: bool = False
    active: bool = False
    started_at: float = 0
    starts: int = 0
    error: str = ""

    def update(self, shot, generation, ready, dead, now, next_shot, duration=.8):
        if not self.observed:
            self.seen_shot, self.seen_generation, self.observed = shot, generation, True
            return False
        if generation != self.seen_generation or shot < self.seen_shot or dead or not ready:
            self.seen_shot, self.seen_generation, self.active = shot, generation, False
            return False
        if shot > self.seen_shot:
            if shot - self.seen_shot != 1:
                self.error, self.active = "multiple unseen shots", False
            elif not self.error:
                self.started_at, self.active = next_shot - .25, True
                self.starts += 1
            self.seen_shot = shot
        if self.active and max(0, now - self.started_at) >= duration:
            self.active = False
        return self.active
