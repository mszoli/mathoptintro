# Greedy1by1 vs GreedyBatch with different batch sizes...

import os
import matplotlib.pyplot as plt
from .simulator import RestaurantSimulator, RESULTS_DIR
from .policies import Greedy1by1, GreedyBatch

BATCHES = [1, 2, 3, 4, 5, 6]

sims = [
    RestaurantSimulator("exp1_1by1", Greedy1by1(), n_couriers=5),
    *[RestaurantSimulator(f"exp1_batch{b}", GreedyBatch(b), n_couriers=5) for b in BATCHES],
]

results = RestaurantSimulator.run_all(sims)

labels = ["1by1"] + [f"batch={b}" for b in BATCHES]
costs = [results[s.name].cost for s in sims]

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(labels, costs)
ax.set_ylabel("cost")
ax.set_title("Greedy1by1 vs GreedyBatch (5 couriers, λ=0.3)")
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, "exp1_plot.png"))
plt.show()
