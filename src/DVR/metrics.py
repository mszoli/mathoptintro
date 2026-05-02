from dataclasses import dataclass


@dataclass
class Metrics:
    cost: float
    mean_waiting_time: float
    n_orders: int
    n_delivered: int
    n_cancelled: int
    n_unresolved: int
