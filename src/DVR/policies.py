import math

from .order import Order
from .policy import Policy, SimState
from .settings import RESTAURANT, travel_time, T_DEADLINE, CANCEL_COST


def route_cost(t_available: int, orders: list[Order]) -> int:
    """
    we have a single courier here that becomes available at t_available
    and we just calculate the total cost of the courier delivering some orders in the given order
    """
    if not orders:
        return 0
    t = max(t_available, max(o.ready_time for o in orders))
    loc = RESTAURANT
    total = 0
    for order in orders:
        t += travel_time(loc, order.location)
        loc = order.location
        lateness = max(0, t - order.arrival_time - T_DEADLINE)
        total += order.weight * lateness ** 2
    return total


def greedy_assign(orders: list[Order], couriers: list[tuple], max_batch: int) -> dict:
    """
    we sort the orders by arrival time and then try to insert them one by one
    into the schedule of every courier...we choose the insertion that
    increases the total cost by the minimal amount
    """
    sequences = {c: [] for c, _ in couriers}
    avail = {c: t for c, t in couriers}

    for order in sorted(orders, key=lambda o: o.arrival_time):
        best_increase = math.inf
        best_courier = None
        best_pos = None

        for c, _ in couriers:
            seq = sequences[c]
            if len(seq) >= max_batch:
                continue
            for k in range(len(seq) + 1):
                # we try to insert the order at every position...
                new_seq = seq[:k] + [order] + seq[k:]
                increase = route_cost(avail[c], new_seq) - route_cost(avail[c], seq)
                if increase < best_increase:
                    best_increase = increase
                    best_courier = c
                    best_pos = k

        if best_courier is not None:
            sequences[best_courier].insert(best_pos, order)

    return sequences


class Greedy1by1(Policy):
    """
    naivly, if there is an available courier,
    accept the order and send the courier out with just this order
    """
    def decide_cancellation(self, order: Order, state: SimState) -> bool:
        return len(state.available_couriers) == 0

    def decide_routing(self, state: SimState) -> dict:
        assignments = {}
        pending = list(state.pending_orders)
        for courier in state.available_couriers:
            if not pending:
                break
            assignments[courier] = [pending.pop(0)]
        return assignments


class GreedyBatch(Policy):
    """
    we have a batch param, we keep accepting orders until we reach
    batch number of them, then we send those out once we have an available courier
    (batch=1 is similar to the greedy above, but not exactly the same,
    as we still accept a single order even if there is no courier available atm)
    """
    def __init__(self, batch: int) -> None:
        self.batch = batch

    def decide_cancellation(self, order: Order, state: SimState) -> bool:
        return len(state.pending_orders) >= self.batch

    def decide_routing(self, state: SimState) -> dict:
        assignments = {}
        pending = list(state.pending_orders)
        for courier in state.available_couriers:
            if not pending:
                break
            assignments[courier] = pending[:self.batch]
            pending = pending[self.batch:]
        return assignments


class SmartPolicy(Policy):
    """
    we always plan with couriers that are available now or
    will become available soon...

    we use the greedy assignment from above,
    and for cancellation we check the cost difference of accepting vs rejecting the order
    (using our greedy assignment speculatively)...
    """
    def __init__(self, return_window: int = 20) -> None:
        self.return_window = return_window

    def _planning_couriers(self, state: SimState) -> list[tuple]:
        """
        we plan with couriers that are available now or will become available
        soon (within return window minutes)
        """
        couriers = [(c, state.current_time) for c in state.available_couriers]
        for c in state.all_couriers:
            if not c.is_available and c.estimated_return_time is not None:
                if c.estimated_return_time <= state.current_time + self.return_window:
                    couriers.append((c, c.estimated_return_time))
        return couriers

    def decide_cancellation(self, order: Order, state: SimState) -> bool:
        """
        we try the greedy assignment with and without this new order
        if we see that with the order the total cost increases by more than
        what it would cost us to cancel it, then we just cancel...
        """
        couriers = self._planning_couriers(state)
        if not couriers:
            return True
        avail = {c: t for c, t in couriers}

        seq_without = greedy_assign(state.pending_orders, couriers, state.max_batch_size)
        seq_with = greedy_assign(state.pending_orders + [order], couriers, state.max_batch_size)

        cost_without = sum(route_cost(avail[c], seq) for c, seq in seq_without.items())
        cost_with = sum(route_cost(avail[c], seq) for c, seq in seq_with.items())

        return cost_with - cost_without > order.weight * CANCEL_COST

    def decide_routing(self, state: SimState) -> dict:
        """
        we just do the greedy assignment from above...
        """
        couriers = self._planning_couriers(state)
        sequences = greedy_assign(state.pending_orders, couriers, state.max_batch_size)
        return {c: seq for c, seq in sequences.items() if c.is_available and seq}
