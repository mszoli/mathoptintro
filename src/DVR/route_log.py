from dataclasses import dataclass


@dataclass
class StopEvent:
    order_id: int
    location: tuple[int, int]
    delivery_time: int


@dataclass
class RouteRecord:
    courier_id: int
    departure_time: int
    stops: list[StopEvent]
    return_time: int
