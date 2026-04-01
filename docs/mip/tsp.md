---
tags:
  - mip
  - constraint generation
  - big-M formulation
  - lifting inequalities
  - branch-and-cut
---

# Travelling Salesman Problem

Given a directed graph $D=(V,A)$ and a cost function $c: A\to \mathbb{R}$ defined on the arcs, the goal is to find a minimum-cost tour that visits every node exactly once (i.e., a Hamiltonian cycle).

In the following sections, we investigate several MIP formulations for the problem.
Meanwhile, we will become familiar with concepts such as *constraint generation*, *extended formulation*, *big-M formulation*, *lifting inequalities*, *branch-and-cut*, etc.

!!! quote "Classification of MIP formulations for the TSP"
    Langevin, A., Soumis, F., & Desrosiers, J. (1990).
    *Classification of travelling salesman problem formulations*.
    Operations Research Letters, 9(2), 127-132.

!!! quote "Comparison of MIP formulations for the TSP"
    Bazrafshan, R., Hashemkhani Zolfani, S., & Mirzapour Al-e-hashem, S. M. J. (2021).
    *Comparison of the sub-tour elimination methods for the asymmetric traveling salesman problem applying the SECA method*.
    Axioms, 10(1), 19.

## Basic formulation

### Variables

Let the binary variable $\mathbf{x}_{ij}$ indicate whether arc $(i,j) \in A$ is included in the tour.

Note that the notation $\mathbf{x}_{(i,j)}$ (and $c_{(i,j)}$) would be more precise, however, we can assume that the graph is simple and thus has no multiple edges.

### Objective

The objective — to minimize the cost of the tour — is straightforward:

$$
\operatorname{minimize}\ \sum_{(i,j)\in A} c_{ij}\mathbf{x}_{ij}
$$

### Constraints

Each node is visited exactly once, that is, there is exactly one incoming and one outgoing arc:

$$
\begin{align*}
\sum_{j:\ (j,i)\in A} \mathbf{x}_{ji} = 1 & &\text{for all}\ i\in V\\
\sum_{j:\ (i,j)\in A} \mathbf{x}_{ij} = 1 & &\text{for all}\ i\in V
\end{align*}
$$

If we solve the problem with only these constraints, the result may not be a single Hamiltonian tour, but rather a set of *subtours*.
Therefore, we need to add some kind of **subtour elimination constraints** (*SECs*), see the next sections.

## Dantzig-Fulkerson-Johnson (DFJ) formulation

!!! quote "Dantzig-Fulkerson-Johnson (DFJ) formulation"
    Dantzig, G., Fulkerson, R., & Johnson, S. (1954).
    *Solution of a large-scale traveling-salesman problem.*
    Journal of the operations research society of America, 2(4), 393-410.

### Subtour elimination constraints

We can ensure that the tour leaves every non-empty proper subset of nodes by adding exponentially many constraints:

$$
\sum_{(i,j)\in A:\ i\in S,\ j\notin S} \mathbf{x}_{ij} \geq 1 \quad \text{for all}\ \emptyset\neq S \subsetneq V
$$

Equivalently (since $\sum_{i\in S} \sum_{j:\ (i,j)\in A} \mathbf{x}_{ij} = |S|$):

$$
\sum_{(i,j)\in A:\ i\in S,\ j\in S} \mathbf{x}_{ij} \leq |S|-1 \quad \text{for all}\ \emptyset\neq S \subsetneq V
$$

### Constraint generation

Actually, we do not need to include these constraints for *all* subsets of nodes.
Instead, we can apply an iterative solution procedure, similar to the one used for the [n-queens problem](./queens.md) (although the goal there was different).

Specifically, we first solve the problem without any subtour elimination constraints.
If, by luck, the result is a single Hamiltonian tour, we can stop.
Otherwise, we identify the subtours in the current solution, add the corresponding elimination constraints to the model, and re-solve the problem.
This procedure is repeated until the solution consists of a single tour.

``` mermaid
flowchart LR
    A([start]) --> B[build model<br/>without SECs]
    B --> C[solve]
    C --> D{single tour?}
    D -- yes --> E([stop])
    D -- no --> F["Add SECs<br/>for the resulted subtours"]
    F --> C
```

## Miller-Tucker-Zemlin (MTZ) formulation

!!! quote "Miller-Tucker-Zemlin (MTZ) formulation"
    Miller, C. E., Tucker, A. W., & Zemlin, R. A. (1960).
    *Integer programming formulation of traveling salesman problems.*
    Journal of the ACM (JACM), 7(4), 326-329.

In the DFJ formulation, we worked only with the $\mathbf{x}$-variables, that is, in the *original variable space*.
Now, we consider an **extended formulation** for the TSP, where we introduce auxiliary variables.
The trade-off is that, although we have more variables, only a polynomial number of subtour elimination constraints is needed.

### Variables

Let the continous variable $\mathbf{y}_i$ indicate the sequence number of the node $i$ in the tour.

$$
0 \leq \mathbf{y}_i \leq n-1 \quad\ \text{for all}\ i\in V
$$

### Subtour elimination constraints

Let us fix an arbitrary start node, say $s$:

$$
\mathbf{y}_s = 0
$$

We need to ensure that if an arc $(i,j)$ with $j \neq s$ is included in the tour, then the sequence number of node $j$ is greater than that of node $i$:

$$
\mathbf{x}_{ij} = 1\ \to\ \mathbf{y}_i + 1 \leq \mathbf{y}_j \quad\ \text{for all}\ (i,j) \in A: j \neq s
$$

By this, the solution will be a single tour.
Otherwise, there is a subtour that does not contain the start node $s$, say $i_1 \to i_2 \to \ldots \to i_k \to i_1$.
Then, $\mathbf{y}_{i_1} < \mathbf{y}_{i_2} < \ldots < \mathbf{y}_{i_k} < \mathbf{y}_{i_1}$, which is a contradiction.

Also note that in any integral solution, each $\mathbf{y}$-variable also takes an integral value (from $0,1,\ldots,n−1$).
And thus, if $\mathbf{x}_{ij} = 1$ ($j \neq s$), then $\mathbf{y}_i + 1 = \mathbf{y}_j$.
That is why we can define $\mathbf{y}$-variables as continous variables.

!!! tip "Implicit integer variables"
    Certain solvers (e.g. SCIP) support the definition of implicit integer variables.
    A continuous variable is called an implicit integer variable if it is guaranteed to take an integer solution value in every optimal solution to every remaining subproblem after fixing all integer variables of the problem.
    Implicit integer variables are not considered for branching, but their integrality properties can still be exploited in other components of the solver, such as presolve, propagation, etc.

    Google OR-Tools MathOpt does not provide the possibility to define implicit integer variables.

The only problem is that the implication above is not a linear constraint.
To linearize it, we apply **big-M type constraints**:

$$
\mathbf{y}_i + 1 \leq \mathbf{y}_j + \operatorname{M}(1 - \mathbf{x}_{ij}) \quad\ \text{for all}\ (i,j) \in A: j \neq s
$$

where $\operatorname{M}$ is an appropriately big constant.
By this, if $\mathbf{x}_{ij} = 1$ in the solution, we have $\mathbf{y}_i + 1 \leq \mathbf{y}_j$, which is exactly what we want.
Otherwise, if $\mathbf{x}_{ij} = 0$, the big-M term makes the constraint redundant, so it is always satisfied.

!!! note "A note on Big-M formulations"
    Big-M formulations are simple to use, however, they have several disadvateges.
    The main issue is that the linear programming relaxation of a big-M constraint is often very weak.
    Even if we use the smallest possible value for the contant M, the constraint still allows a wide range of feasible values when the binary variable is fractional but close to an integer (e.g., 0.9).

What is the smallest possible value for M in our case?
The left-hand side, $\mathbf{y}_i + 1$, is maximum $n$, while the term $\mathbf{y}_j$ on the right-hand side is minimum 1.
Thus, for $\operatorname{M} = n-1$, the constraint never cuts off a feasible solution.

The final version of our constraints are:

$$
\mathbf{y}_i - \mathbf{y}_j + (n-1)\mathbf{x}_{ij} \leq n - 2 \quad\ \text{for all}\ (i,j) \in A: j \neq s
$$

!!! tip "Indicator constraints"
    Several solvers support the use of indicator constraints (a binary indicator variable together with an enforced linear constraint) to model the implications described above.
    Such constraints can usually be handled more efficiently by the solver than a big-M formulation.

    For example, OR-Tools MathOpt provides the method `add_indicator_constraint`.

### Lifted inequalities

!!! quote "Lifted MTZ inequalities"
    Desrochers, M., & Laporte, G. (1991).
    *Improvements and extensions to the Miller-Tucker-Zemlin subtour elimination constraints*.
    Operations Research Letters, 10(1), 27-36.

The MTZ SECs can be strengthed by a [lifting procedure](./mip.md#lifting-inequalities).

Consider the SEC corresponding to arc $(i,j)$ with $j\neq s$.
Clearly, only the reverse arc variable $\mathbf{x}_{ji}$, if exists, can be a candidate for lifting, since the other arcs are, in general, "independent" of $(i,j)$.
Thus, we are looking for the strengthened inequality in the following form:

$$
\mathbf{y}_i - \mathbf{y}_j + (n-1)\mathbf{x}_{ij} + \alpha\mathbf{x}_{ji} \leq n - 2
$$

Assume that $n>2$.
If $\mathbf{x}_{ji} = 0$ in a solution, we obtain the original, valid inequality independently from the value of $\alpha$.
Otherwise, if $\mathbf{x}_{ji} = 1$, then $\mathbf{y}_i - \mathbf{y}_j = 1$ and $(n-1)\mathbf{x}_{ij} = 0$, thus we have $\alpha \leq n - 3$.

Then, the lifted MTZ inequalities are:

$$
\mathbf{y}_i - \mathbf{y}_j + (n-1)\mathbf{x}_{ij} + (n-3)\mathbf{x}_{ji} \leq n - 2 \quad\ \text{for all}\ (i,j) \in A: j \neq s
$$

Note that these inequalities define facets of the corresponding TSP polytope for $n\geq 6$.

### Branch-and-cut

In the previous sections, we saw that the DFJ SECs are strong but numerous, while the MTZ SECs are few but weak.
How can we combine their advantages?

Let us take the MTZ formulation as the base model and strengthen its LP relaxation by dynamically adding DFJ subtour elimination constraints within a [**branch-and-cut**](../mip/mip.md#branch-and-cut) scheme.

!!! tip "Callback for branch-and-cut"
    Several solvers support branch-and-cut callbacks that allow generating custom cuts during the global search.

    In OR-Tools MathOpt, a `SolveCallback` can be defined and passed to the `solve` method.
    Note that the `Event.MIP_NODE` event must also be registered.
    Also note that currently only the GUROBI and GSCIP solvers support branch-and-cut callbacks.

Assume that the solution $(\bar{x},\bar{y})$ for the LP-relaxation of the current node problem is fractional.
Instead of branching, we first attempt to strengthen the LP-relaxation by cutting off this fractional solution.
To this end, we separate the DFJ SECs, that is, we look for an inequality (i.e., a non-empty subset $S$ of nodes) such that:

$$
\sum_{(i,j)\in A:\ i\in S,\ j\notin S} \bar{x}_{ij} < 1
$$

In other words, for the subset $S$, the sum of $\bar{x}$-values on the outgoing arcs is less than 1.

Thus, the separation problem of checking whether there are such violated inequalities, can be reduced to checking whether the minimum cut in the graph with respect to arc weights $\bar{x}$ is less than 1.
For this, we can check the minimum cut between all pairs of nodes.

!!! note "Separation of DFJ subtour elimination constraints"
    Note that the proposed branch-and-cut procedure is independent of the MTZ formulation and can therefore be applied to any TSP formulation (using the $\mathbf{x}$ variables).

## Gavish–Graves (GG) formulation

!!! quote "Gavish–Graves (GG) formulation"
    Gavish, B., & Graves, S. C. (1978).
    *The travelling salesman problem and related problems*.

### Variables

Let us fix an arbitrary start node, say $s$.
Each arc $(i,j)$ with $i\neq s$ is associated with a non-negative variable $\mathbf{z}_{ij}$.

### Subtour elimination constraints

$$
\begin{align*}
\mathbf{z}_{ij} &\leq (n-1)\mathbf{x}_{ij} & \text{for all}\ (i,j) \in A:\ j \neq s\\
\sum_{j:\ (i,j)\in A} \mathbf{z}_{ij} - \sum_{j \neq s:\ (j,i)\in A} \mathbf{z}_{ji} &= 1 & \text{for all}\ i \in V \setminus \{s\}
\end{align*}
$$

Consider an integral solution $(\bar{\mathbf{x}},\bar{\mathbf{z}})$ to the problem.
Due to the first constraint, $\bar{\mathbf{z}}_{ij} = 0$ for each arc $(i,j)$ not included in the subtours.
Thus, according to the second constraint, $\bar{\mathbf{z}}_{ij} + 1 \leq \bar{\mathbf{z}}_{jk}$ for each pair of arcs $(i,j)$ and $(j,k)$ that are consequtive in a subtour.
Similarly to the MTZ formulation, since $\bar{\mathbf{z}}$-values would increase infinitely in any subtour not containing node $s$, the solution must be a single tour.

Notice that for fixed $\mathbf{x}$-values, the problem is reduced to a network flow problem with integral capacities, thus the $\mathbf{z}$-variables also takes integer values.

## Implementation

The implementation of the models can be found in <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/tsp_mip.py" target="_blank">`tsp_mip.py`</a>

### Exercises

1. Implement the Gravish-Graves formulation in function `solve_tsp_gg`.

2. Implement the branch-and-cut procedure for the Gravish-Graves formulation that separates the DFJ subtour elimination constraints.
