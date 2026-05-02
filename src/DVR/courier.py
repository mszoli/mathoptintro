import simpy
from typing import Optional
from .order import Order
from .settings import RESTAURANT, travel_time
from .route_log import RouteRecord, StopEvent


class Courier:
    def __init__(self, env: simpy.Environment, courier_id: int, on_return) -> None:
        self.env = env
        self.id = courier_id
        self.location: tuple[int, int] = RESTAURANT
        self.is_available: bool = True
        self.estimated_return_time: Optional[int] = None
        self.completed_routes: list[RouteRecord] = []
        self._on_return = on_return

    def assign(self, orders: list[Order]) -> None:
        self.is_available = False
        t = max(self.env.now, max(o.ready_time for o in orders))
        loc = RESTAURANT
        for order in orders:
            t += travel_time(loc, order.location)
            loc = order.location
        t += travel_time(loc, RESTAURANT)
        self.estimated_return_time = t
        self.env.process(self._run_route(orders))

    def _run_route(self, orders: list[Order]):
        batch_ready = max(o.ready_time for o in orders)
        if self.env.now < batch_ready:
            yield self.env.timeout(batch_ready - self.env.now)

        departure_time = self.env.now
        stops = []

        for order in orders:
            yield self.env.timeout(travel_time(self.location, order.location))
            self.location = order.location
            order.delivery_time = self.env.now
            stops.append(StopEvent(order.id, order.location, self.env.now))

        yield self.env.timeout(travel_time(self.location, RESTAURANT))
        self.location = RESTAURANT
        self.is_available = True
        self.estimated_return_time = None
        self.completed_routes.append(RouteRecord(self.id, departure_time, stops, self.env.now))
        self._on_return(self)
