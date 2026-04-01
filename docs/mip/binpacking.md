---
tags:
  - mip
  - packing
  - column generation
---

# Bin Packing Problem

Given a set $\mathcal{I} = \{1,\ldots,m\}$ of *items*, where each item $i$ has a positive *size* $s_i$.
The goal is to pack all items into a minimum number of *bins* with uniform capacity $C$.

## First-Fit-Decreasing heuristic

The First-Fit procedure iterates over the items and assigns each current item to the first bin into which it fits (opening a new empty bin if necessary).

For the online version of the problem (where items arrive one by one and are not known in advance), this procedure has an approximation ratio of 1.7.
That is, the obtained solution uses at most 1.7 times as many bins as the optimal solution.

The First-Fit Decreasing procedure first sorts the items in non-increasing order of size, and then applies First-Fit.
This significantly improves the performance: the asymptotic approximation ratio is about 1.222.

!!! quote "Absolute approximation ratio for First-Fit Bin Packing"
    Dósa, G., & Sgall, J. (2013).
    *First fit bin packing: A tight analysis*.
    In 30th International symposium on theoretical aspects of computer science (STACS 2013) (pp. 538-549). Schloss Dagstuhl–Leibniz-Zentrum fuer Informatik.

## A natural MIP formulation

Let $\operatorname{N}$ be an upper bound on the number of necessary bins (e.g., $m$ or the number of bins obtained with First-Fit-Decreasing).

Let the binary variable $\mathbf{x}_j$ indicate whether bin $j$ is used ($1\leq j\leq N$), and let the binary variable $\mathbf{y}_{ij}$ indicate whether item $i$ is assigned to bin $j$ ($1\leq i\leq m$, $1\leq j\leq N$).

The objective is to minimize the number of bins used, such that each item is assigned to exactly one bin, and the total size of the items assigned to a bin does not exceed its capacity.

$$
\begin{align*}
\operatorname{minimize}\ \sum\limits_{j=1}^N \mathbf{x}_j &\quad \\
\sum\limits_{j=1}^N \mathbf{y}_{ij} = 1 \quad 1\leq i\leq m \\
\sum\limits_{i=1}^m s_i\mathbf{y}_{ij} \leq C\mathbf{x}_j &\quad 1\leq j\leq N\\
\mathbf{x}_j \in \{0,1\} &\quad 1\leq j\leq N\\
\mathbf{y}_{ij} \in \{0,1\} &\quad 1\leq i\leq m,\ 1\leq j\leq N
\end{align*}
$$

Note that the following *symmetry breaking constraints* can be used:

$$
\mathbf{x}_1 \geq \mathbf{x}_2 \geq \ldots \geq \mathbf{x}_N 
$$

## Column generation

Consider the following *set-partitioning* formulation of the bin packing problem.

Let each column correspond to a feasible packing *pattern*, that is, to a subset of items that can be packed into a single bin.
Let $\mathcal{P}$ denote the set of all feasible packing patterns.
For each pattern $p \in \mathcal{P}$, let $a_{ip}$ indiciate whether item $i$ is included in pattern $p$.
Since each pattern represents a feasible packing, it satisfies $\sum_{i=1}^m s_i a_{ip} \leq C$.

Let the binary variable $\mathbf{x}_p$ indicate whether pattern $p \in \mathcal{P}$ is selected.
Then, the problem can be written as:

$$
\begin{align*}
\operatorname{minimize} \sum_{p \in \mathcal{P}} \mathbf{x}_p && \\
\sum_{p \in \mathcal{P}} a_{ip} \mathbf{x}_p = 1 && 1 \leq i \leq m \\
\mathbf{x}_p \in \{0,1\} && p \in \mathcal{P}
\end{align*}
$$

An important feature of this model is that the bin-capacity constraints are encoded implicitly in the columns.
This is especially useful in problems where the feasibility of a column is difficult to express explicitly in a compact formulation.

The drawback is that the number of feasible packing patterns can be enormous, typically exponential in the number of items.
Therefore, we do not generate all columns in advance; instead, we apply a column generation procedure

### Restricted master problem

The initial restricted master problem (RMP) contains only a subset $\mathcal{P}' \subseteq \mathcal{P}$ of the columns, chosen so that the restricted problem is feasible.
For example, we may start with the $m$ singleton patterns, that is, one bin for each item.
A better initial column set may be obtained from the bins produced by the First-Fit-Decreasing heuristic.

Since column generation is an LP-based approach, we relax the integrality constraints and solve the LP relaxation of the restricted master problem:

$$
\begin{align*}
\operatorname{minimize} \sum_{p \in \mathcal{P}'} \mathbf{x}_p && \\
\sum_{p \in \mathcal{P}'} a_{ip} \mathbf{x}_p \geq 1 && 1 \leq i \leq m \\
\mathbf{x}_p \geq 0 && p \in \mathcal{P}'
\end{align*}
$$

Here we use a set-covering relaxation instead of the original set-partitioning formulation.
This relaxation has several advantages.

First, any feasible set-partitioning solution is also feasible for the set-covering formulation.
Moreover, any integer set-covering solution can be converted into a feasible set-partitioning solution by removing redundant item assignments from overloaded coverage, since removing items from a bin cannot violate the capacity constraint.

Second, the dual variables corresponding to the covering constraints are nonnegative, which leads to a particularly convenient pricing problem.

Third, since there are no upper bounds $\mathbf{x}_p \leq 1$, there are no dual variables for them.

Finally, if we solve the final integer problem only on the generated column set, the set-partitioning model may become infeasible because some necessary columns were never generated.
The set-covering version is more robust in this respect, since it may still admit a feasible solution on the restricted column set.

After the column generation phase terminates, the generated columns can be used in a final integer optimization model, typically over the restricted column set.

### Pricing problem

The dual of the restricted master problem is

$$
\begin{align*}
\operatorname{maximize} \sum_{i=1}^m \pi_i &&\\
\sum_{i=1}^m \pi_i a_{ip} \leq 1 && p \in \mathcal{P}' \\
\pi_i \geq 0 && 1 \leq i \leq m
\end{align*}
$$

Let $(\bar{x}, \bar{\pi})$ be an optimal primal-dual solution pair for the restricted master problem.
The pricing problem is to decide whether there exists a column $a_p$ with negative reduced cost.

Since each column has objective coefficient $1$, the reduced cost of a column $a_p$ is

$$
\bar{c}_p = 1 - \sum_{i=1}^m \bar{\pi}_i a_{ip}.
$$

Therefore, the pricing problem is the following optimization problem:

$$
\begin{align*}
\operatorname{maximize} \sum_{i=1}^m \bar{\pi}_i \mathbf{a}_i && \\
\sum_{i=1}^m s_i \mathbf{a}_i \leq C && \\
\mathbf{a}_i \in \{0,1\} && 1 \leq i \leq m
\end{align*}
$$

If the optimal value of this problem is greater than $1$, then the corresponding column has negative reduced cost and should be added to the restricted master problem.
Otherwise, no improving column exists, and the current restricted solution is optimal for the LP relaxation of the master problem.

!!! tip "It's a knapsack problem!"
    In bin packing, the pricing problem is a 0-1 knapsack problem.

## Branch-and-price

The previous approach could be called *price-and-branch*, since the LP relaxation is first solved to optimality using column generation, and then an integer feasible solution is obtained by solving the MIP over the generated column set.
From another viewpoint, we solve an MIP where new columns are generated only at the root node.

Clearly, the resulting integer solution is not necessarily optimal for the original full problem.
Moreover, it is possible that no integer solution exists using only the generated columns.
However, there is a way to solve the integer problem to optimality within a column generation framework.

In a branch-and-price approach, the LP relaxation at each node of the search tree is solved via column generation.
However, this introduces some complications.

First, the default 0–1 branching on fractional variables is not effective.
Since the number of columns increases dynamically, fixing a variable to zero typically has only a minor effect.
Thus, problem-specific branching strategies are required.
Moreover, branching decisions must be incorporated into the pricing problem.

For the Bin Packing Problem, a widely used approach is **Ryan–Foster branching**.
The key observation is that in any fractional solution, there exist two items, say $i$ and $k$, that are covered together in some columns but not in others.
Thus, two branches are created:

- in the *same* branch, the items are required to be assigned to the same bin;
- in the *different* branch, they are required to be assigned to different bins.

If the pricing problem is formulated as a MIP, these conditions can be enforced by adding the constraints
$\mathbf{a}_i = \mathbf{a}_k$ and $\mathbf{a}_i + \mathbf{a}_k \leq 1$, respectively.

!!! quote "Ryan-Foster branching scheme"
    Ryan, D. M., & Foster, B. A. (1981).
    *An integer programming approach to scheduling*.
    Computer scheduling of public transport urban passenger vehicle and crew scheduling, 269–280.
    