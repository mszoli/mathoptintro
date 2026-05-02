# GreedyBatch(3) vs SmartPolicy across arrival rates

import os
import numpy as np
import matplotlib.pyplot as plt
from .simulator import RestaurantSimulator, RESULTS_DIR
from .policies import GreedyBatch, SmartPolicy

RATES = [0.1, 0.3, 0.5, 1.0, 1.5, 2.0]
COURIERS = 5

sims = []
for rate in RATES:
    label = str(rate).replace(".", "")
    sims.append(RestaurantSimulator(f"exp2_batch_{label}", GreedyBatch(3), n_couriers=COURIERS, arrival_rate=rate))
    sims.append(RestaurantSimulator(f"exp2_smart_{label}", SmartPolicy(), n_couriers=COURIERS, arrival_rate=rate))

results = RestaurantSimulator.run_all(sims)

batch_costs = [results[f"exp2_batch_{str(r).replace('.', '')}"].cost for r in RATES]
smart_costs = [results[f"exp2_smart_{str(r).replace('.', '')}"].cost for r in RATES]

batch_delivered = [results[f"exp2_batch_{str(r).replace('.', '')}"].n_delivered for r in RATES]
batch_cancelled = [results[f"exp2_batch_{str(r).replace('.', '')}"].n_cancelled for r in RATES]
smart_delivered = [results[f"exp2_smart_{str(r).replace('.', '')}"].n_delivered for r in RATES]
smart_cancelled = [results[f"exp2_smart_{str(r).replace('.', '')}"].n_cancelled for r in RATES]

x = np.arange(len(RATES))
w = 0.35

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

ax1.bar(x - w / 2, batch_costs, w, label="GreedyBatch(3)")
ax1.bar(x + w / 2, smart_costs, w, label="SmartPolicy")
ax1.set_xticks(x)
ax1.set_xticklabels([f"λ={r}" for r in RATES])
ax1.set_ylabel("cost")
ax1.set_title(f"Cost ({COURIERS} couriers)")
ax1.legend()

ax2.bar(x - w / 2, batch_delivered, w, label="GreedyBatch(3) delivered", color="tab:blue")
ax2.bar(x - w / 2, batch_cancelled, w, bottom=batch_delivered, label="GreedyBatch(3) cancelled", color="tab:blue", alpha=0.4)
ax2.bar(x + w / 2, smart_delivered, w, label="SmartPolicy delivered", color="tab:orange")
ax2.bar(x + w / 2, smart_cancelled, w, bottom=smart_delivered, label="SmartPolicy cancelled", color="tab:orange", alpha=0.4)
ax2.set_xticks(x)
ax2.set_xticklabels([f"λ={r}" for r in RATES])
ax2.set_ylabel("orders")
ax2.set_title(f"Delivered / cancelled ({COURIERS} couriers)")
ax2.legend(fontsize=8)

fig.suptitle("GreedyBatch vs SmartPolicy across arrival rates")
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, "exp2_plot.png"))
plt.show()
