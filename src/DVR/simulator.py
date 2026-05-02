import json
import os
import random
import simpy
import dataclasses
from typing import Optional
from .order import Order
from .courier import Courier
from .policy import Policy, SimState
from .metrics import Metrics
from .route_log import RouteRecord
from .settings import MAP_SIZE, PREP_TIME_MIN, PREP_TIME_MAX, WEIGHT_MIN, WEIGHT_MAX

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


class RestaurantSimulator:
    def __init__(
        self,
        name: str,
        policy: Policy,
        n_couriers: int,
        arrival_rate: float = 0.3,
        sim_duration: int = 600, # corresponds to 10 hours, kinda reasonable
        max_batch_size: int = 10,
        seed: int = 42,
        log: bool = True,
    ) -> None:
        self.name = name
        self.policy = policy
        self.arrival_rate = arrival_rate
        self.sim_duration = sim_duration
        self.max_batch_size = max_batch_size
        self.log = log
        self.seed = seed

        self.env = simpy.Environment()
        self.all_orders: list[Order] = []
        self.pending_orders: list[Order] = []
        self.route_log: list[RouteRecord] = []
        self.couriers: list[Courier] = [
            Courier(self.env, i, self._on_courier_return)
            for i in range(n_couriers)
        ]

    def run(self) -> Metrics:
        # reset the random here so that every sim with the same seed is identical and comparable
        random.seed(self.seed)
        self.env.process(self._order_generator())
        self.env.run()
        if self.log:
            # each courier takes care of logging its own stuff
            for courier in self.couriers:
                self.route_log.extend(courier.completed_routes)
        return self.metrics()

    @classmethod
    def run_all(cls, sims: list["RestaurantSimulator"]) -> dict:
        results = {}
        for sim in sims:
            metrics = sim.run()
            out_dir = os.path.join(RESULTS_DIR, sim.name)
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "metrics.json"), "w") as f:
                json.dump(dataclasses.asdict(metrics), f, indent=2)
            if sim.log:
                with open(os.path.join(out_dir, "routes.json"), "w") as f:
                    json.dump([dataclasses.asdict(r) for r in sim.route_log], f, indent=2)
                with open(os.path.join(out_dir, "orders.json"), "w") as f:
                    json.dump([dataclasses.asdict(o) for o in sim.all_orders], f, indent=2)
            print(f"{sim.name}: cost={metrics.cost} delivered={metrics.n_delivered} "
                  f"cancelled={metrics.n_cancelled} unresolved={metrics.n_unresolved}")
            results[sim.name] = metrics
        return results

    def _order_generator(self):
        order_id = 0
        while self.env.now < self.sim_duration:
            yield self.env.timeout(max(1, round(random.expovariate(self.arrival_rate))))
            if self.env.now >= self.sim_duration:
                break

            order = Order(
                id=order_id,
                location=(random.randint(0, MAP_SIZE), random.randint(0, MAP_SIZE)),
                arrival_time=self.env.now,
                prep_time=random.randint(PREP_TIME_MIN, PREP_TIME_MAX),
                weight=random.randint(WEIGHT_MIN, WEIGHT_MAX),
            )
            order_id += 1
            self.all_orders.append(order)

            state = self._make_state()
            if self.policy.decide_cancellation(order, state):
                order.cancelled = True
            else:
                self.pending_orders.append(order)
                self._trigger_routing()

    def _on_courier_return(self, _: Courier) -> None:
        # we don't care who returned, we just trigger the recalc...
        if self.pending_orders:
            self._trigger_routing()

    def _trigger_routing(self) -> None:
        if not any(c.is_available for c in self.couriers) or not self.pending_orders:
            return
        state = self._make_state()
        assignments = self.policy.decide_routing(state)
        for courier, orders in assignments.items():
            if orders:
                for order in orders:
                    self.pending_orders.remove(order)
                courier.assign(orders)

    def _make_state(self) -> SimState:
        # this is what we give to the policy
        return SimState(
            current_time=self.env.now,
            pending_orders=list(self.pending_orders),
            available_couriers=[c for c in self.couriers if c.is_available],
            all_couriers=list(self.couriers),
            max_batch_size=self.max_batch_size,
        )

    def metrics(self) -> Metrics:
        delivered = [o for o in self.all_orders if o.delivery_time is not None]
        cancelled = [o for o in self.all_orders if o.cancelled]
        unresolved = [o for o in self.all_orders if o.delivery_time is None and not o.cancelled]

        total_weight = sum(o.weight for o in self.all_orders)
        finished = delivered + cancelled

        cost = sum(o.cost for o in finished) / total_weight
        mean_waiting_time = (
            sum(o.weight * o.waiting_time for o in delivered)
            / sum(o.weight for o in delivered)
        ) if delivered else 0.0

        return Metrics(
            cost=round(cost, 3),
            mean_waiting_time=round(mean_waiting_time, 3),
            n_orders=len(self.all_orders),
            n_delivered=len(delivered),
            n_cancelled=len(cancelled),
            n_unresolved=len(unresolved),
        )
