from .simulator import RestaurantSimulator
from .policies import Greedy1by1, GreedyBatch, SmartPolicy

sims = [
    RestaurantSimulator(f"smart_{n}", Greedy1by1(), n_couriers=n) for n in range(1, 31)
]

RestaurantSimulator.run_all(sims)

