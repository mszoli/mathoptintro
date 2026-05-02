from dataclasses import dataclass, field
from typing import Optional
from .settings import T_DEADLINE, CANCEL_COST


@dataclass
class Order:
    id: int
    location: tuple[int, int]
    arrival_time: int
    prep_time: int
    weight: int

    delivery_time: Optional[int] = field(default=None, init=False)
    cancelled: bool = field(default=False, init=False)

    @property
    def ready_time(self) -> int:
        return self.arrival_time + self.prep_time

    @property
    def waiting_time(self) -> Optional[int]:
        if self.delivery_time is None:
            return None
        return self.delivery_time - self.arrival_time

    @property
    def lateness(self) -> Optional[int]:
        if self.delivery_time is None:
            return None
        return max(0, self.waiting_time - T_DEADLINE)

    @property
    def cost(self) -> Optional[int]:
        if self.cancelled:
            return self.weight * CANCEL_COST
        if self.delivery_time is None:
            return None
        return self.weight * self.lateness ** 2
