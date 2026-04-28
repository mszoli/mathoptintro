# Mini-Project 2/2

## General Information

1. **Tasks**:

    - Each student must choose **exactly one** of the tasks listed below.

2. **Solution**:

    - The solution must be implemented in **Python**.
    - A **short report** (in PDF format; in Hungarian or in English) must also be submitted.

3. **Deadline**:

    - The files (program code and documentation) must be sent to **marko.horvath (at) sztaki (dot) hu** no later than **May 6**, 2026 (EOD).

4. **Presentation**:

    - The solutions will be presented **in person** (individually).
    - The presentations are scheduled to take place at the beginning of the course on **May 14**.
    - Upon prior arrangement, solutions may also be presented at another time at SZTAKI.

5. **Generative AI**:

    - Please use generative AI tools sparingly.
    I am interested in your own understanding and creativity, not in AI-generated solutions.

6. **Questions**:

    - If you have any questions, do not hesitate to contact me by e-mail.
    Please make sure to clarify any misunderstandings or bugs before the final submission.

---

## Task #1: Branch-and-cut for a lot-sizing problem

The goal is to implement a **branch-and-cut approach** for the LS-U problem.

---

### The uncapacitated lot-sizing (LS-U) problem

!!! quote "Single-item uncapacitated lot-sizing"
    Pochet, Y., & Wolsey, L. A. (2006).
    *Single-item uncapacitated lot-sizing*.
    Production Planning by Mixed Integer Programming, 207-234.
    <a href="https://sci-hub.red/10.1007/0-387-33477-7_8" target="_blank">10.1007/0-387-33477-7_8</a>

The LS-U problem is defined in Section 7.1 (Pochet, Y., & Wolsey, L. A., 2006).
There is a *planning horizon* of $n$ periods.
The demand for the item in period $t= 1,\ldots,n$ is $d_t$.
For each period, there are 

- unit production costs;
- unit storage costs for stock remaining at the end of the period; and
- a fixed set-up (or order placement) cost which is incurred to allow production to take place in period, but is independent of the amount produced.

The goal is to fulfill the demands while the costs are minimized.

The problem is formulated by constraints (7.1)-(7.6), where we can assume that the opening and closing stocks are zero.

From Section 7.2, we only use the notation $d_{k\ell} = \sum_{u=k}^{\ell} d_u$.

In Section 7.4, the authors introduce a class of valid inequalities, called $(\ell,S)$-inequalitites (Proposition 7.4, and form (7.11)), for which they also propose a separation procedure.

---

### Mini-Project

1. Implement a method to generate instances of varying sizes (e.g., small, medium, large) and cost structures, or use appropriate benchmark instances from the literature.

2. Implement a method that solves the formulation (7.1)-(7.6), using the **OR-Tools MathOpt** package.

3. Implement a branch-and-cut callback to seperate the $(\ell,S)$-inequalities.
Note that some solvers do not support such callbacks.

4. Create a report that consists of the description of the problem; the formulation and the separation procedure; and computational results comparing runs with and without the custom cuts.

## Task #2: Column generation for a driver scheduling problem

The goal is to implement a **column generation approach** for a driver scheduling problem.

---

### Driver scheduling problem

There is a set $\mathcal{T}$ of trips, where each *trip* is described by a tuple $(A,B,t_A,t_B)$.
This means that a vehicle — with a driver — is needed to transport passengers from origin location $A$ to destination location $B$, departing at time $t_A$ and arriving at time $t_B$.

??? example "Example of trips"
    Departure and arrival locations/times for three trips:

    trip | departure | arrival
    -----|-----------|----------
    1    | 1 / 10:00 | 2 / 11:00
    2    | 1 / 11:15 | 3 / 12:00
    3    | 3 / 11:45 | 2 / 12:30

    The corresponding input (times are converted into minutes from midnight):

    ```python
    trips = [
        (1,2,600,660),
        (1,3,675,720),
        (3,2,705,750),
    ]
    ```

In the driver scheduling problem, the goal is to assign drivers to trips while minimizing the total operating cost (which, in this case, is the number of drivers).

A subset of trips is *vehicle-feasible* if they can be performed by the same vehicle.
That is, there must be enough time to travel empty from the destination of one trip to the origin of the next trip.

??? example "Example of empty travel times"
    The travel time matrix:

    .     | Depot |  1 |  2 |  3
    ------|-------|----|----|---
    Depot |     0 | 20 | 20 | 30
    1     |    20 |  0 | 30 | 20
    2     |    20 | 30 |  0 | 20
    3     |    30 | 20 | 20 |  0

    The corresponding input (times are converted into minutes from midnight):

    ```python
    minutes = [
        [0,20,20,30],
        [20,0,30,20],
        [20,30,0,20],
        [30,20,20,0],
    ]
    ```

A vehicle-feasible subset of trips is *driver-feasible* if it satisfies additional working regulations.
Drivers start and finish their daily shifts at the depot, and their shifts must satisfy rules such as a maximum working time (e.g., a driver cannot drive more than 8 hours per day).
A driver-feasible subset of trips is called *duty*.

---

### Auxiliary graph

We define a directed graph $D=(V,A)$ as follows:

- $V$ is the set of locations. Two special nodes, $s$ and $t$, represent the same depot (start and end of a shift).
- For each trip, there is an arc from the corresponding origin node to the corresponding destination node.
  The length of such an arc equals the duration of the trip.
- For each trip, there is an arc from node $s$ to its origin node, and an arc from its destination node to node $t$.
  The lengths of these arcs equal the travel time between the corresponding locations.
- For each pair of trips, there is an arc from the destination of the first trip to the origin of the second trip if they can be performed in this order.
  The length of such an arc equals the timespan between the corresponding departure and arrival times.

Note that each path from $s$ to $t$ corresponds to a vehicle-feasible subset of trips.
An $s$-$t$ path is *driver-feasible* if it satisfies all driver-related constraints (e.g., maximum working time).

---

### MIP formulation

Similarly to the [bin packing problem](./mip/binpacking.md), we consider a set-covering formulation.
Let $\mathcal{S}$ be the set of all duties.
Each subset $S \in \mathcal{S}$ is associated with a binary variable $\mathbf{x}_S$ indicating whether a driver is assigned to the duty.
Each constraint corresponds to a trip.

The primal LP-relaxation:

$$
\begin{align*}
\operatorname{minimize} \sum_{S\in \mathcal{S}} \mathbf{x}_S &&\\
\sum_{S\in \mathcal{S}:\ t \in S} \mathbf{x}_S & \geq 1 && \text{for all}\ t \in \mathcal{T} \\
\mathbf{x}_S & \geq 0 && \text{for all}\ S \in \mathcal{S}
\end{align*}
$$

The corresponding dual problem is:

$$
\begin{align*}
\operatorname{maximize} \sum_{t\in \mathcal{T}} \pi_t && \\
\sum_{t \in S} \pi_t & \leq 1 && \text{for all}\ S \in \mathcal{S} \\
\pi_t & \geq 0 && \text{for all}\ t \in \mathcal{T}
\end{align*}
$$

---

### Column generation

The initial *restricted master problem* consists of a set of duties for which the problem has a feasible solution.

Let $(\bar{x},\bar{\pi})$ be the optimal primal-dual solution pair.
Then, the pricing problem is about to find a duty $S$, if any, where

\[
    \sum_{t\in S} \bar{\pi}_t > 1
\]

If in the auxiliary graph each trip arc is associated with the corresponding $\bar{\pi}$ value, then the previous condition means that the cost of the corresponding $s$-$t$ path is greater than 1.
Thus, the pricing problem is reduced to a longest path problem in an acyclic graph.
However, due to the working regulations, the path must satisfy other constraints as well.

---

### Mini-project

1. Implement a method to generate instances (i.e., set of trips and empty travel times) of varying sizes (e.g., small, medium, large), or use appropriate benchmark instances from the literature.

2. Define a working regulation (e.g., the total duration of a shift cannot exceed 8 hours) which makes the pricing problem not trivial.

3. Implement a method that solves the LP-relaxation of the problem with column generation, using the **OR-Tools MathOpt** package.
Note that some solvers do not provide dual feasible solutions.

4. Obtain an integer solution with the resulted set of duties.
Note that the solution might be post-processed to ensure that each trip is assigned to exactly one duty.

5. Visualize the solution in an appropriate understable way.

6. Create a report that consists of the description of the problem; the formulation and the pricing procedure; and computational results comparing runs with and without the custom cuts.

---

## Task #3: Dynamic Vehicle Routing

The goal is to implement a **simulator** for a dynamic vehicle routing problem.

---

### Sketch of the problem

A restaurant offers home delivery. The restaurant has a few in-house couriers who deliver the orders that arrive continuously throughout the day. A courier can pick up multiple orders at the restaurant and deliver them in a single route, after which they return to the restaurant and, if needed, can carry out further deliveries.

However, a delivery route cannot be interrupted: a courier cannot return to the restaurant to pick up new orders until all previously collected orders have been delivered.

---

### Mini-project

1. Define the problem freely, but precisely. Specify travel times, locations, whether food preparation time, parking, or any other factors are taken into account, etc.

2. Decide what policy will be used to assign orders to couriers, that is, what delivery routes will be planned. It may be useful to define some metric for evaluating the solution, for example customer satisfaction: do customers receive their orders within one hour? Or how much later do they receive them? etc.

3. The solution must be implemented via the `simpy` package.
It may be useful to reuse parts of the example discussed in class.

    1. You will need a function that generates orders on the fly.

    2. You will need a function that assigns deliverable orders among the couriers. There are two cases in which it may be worthwhile to plan routes:
    
        (i) when a new order arrives and there is an available courier;
        
        (ii) when a courier returns to the restaurant and there are still undelivered orders.

    3. You will need a function that executes, that is, simulates, a route assigned to a courier. It may be useful to organize the vehicles — that is, the couriers — into a separate class.

4. Create a report that consists of the description of the problem; a brief description of how the simulator works; and a short analysis (for example, what happens if the number of vehicles is changed, or if a different assignment policy is used, or any similar variations).
