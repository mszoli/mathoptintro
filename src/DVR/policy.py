from abc import ABC, abstractmethod
from dataclasses import dataclass
from .order import Order


@dataclass
class SimState:
    current_time: int
    pending_orders: list[Order]
    available_couriers: list
    all_couriers: list
    max_batch_size: int


class Policy(ABC):
    @abstractmethod
    def decide_cancellation(self, order: Order, state: SimState) -> bool:
        ...

    @abstractmethod
    def decide_routing(self, state: SimState) -> dict:
        """
        return dict should be like:
        {
            courier_0: [order_3, order_7],
            courier_1: [order_1],
        }
        """
        ...
