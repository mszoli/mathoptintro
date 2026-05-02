# increasing the number of couriers for the smart policy

import os
import matplotlib.pyplot as plt
from .simulator import RestaurantSimulator, RESULTS_DIR
from .policies import SmartPolicy

COURIERS = list(range(1, 31))

sims = [
    RestaurantSimulator(f"exp3_{n}c", SmartPolicy(), n_couriers=n)
    for n in COURIERS
]

results = RestaurantSimulator.run_all(sims)

costs = [results[s.name].cost for s in sims]

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(COURIERS, costs, marker="o")
ax.set_xlabel("number of couriers")
ax.set_ylabel("cost")
ax.set_title("SmartPolicy: cost vs number of couriers (λ=0.3)")
ax.set_xticks(COURIERS)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, "exp3_plot.png"))
plt.show()
