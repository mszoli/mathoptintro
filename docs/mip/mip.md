# Integer programming

If, in a [linear programming problem](../mip/lp.md), we require some variables to take integer values, we obtain a **mixed-integer linear program** (*MILP*).
For simplicity, we will refer to such problems as **integer programming problems**, and use the abbreviation *MIP*.

$$
\begin{aligned}
\text{minimize} \quad & \sum_{j=1}^n c_j \mathbf{x}_j \\
\text{subject to} \quad 
& \sum_{j=1}^n a_{ij} \mathbf{x}_j \geq b_i && \text{for all } i = 1,\ldots,m \\
& \mathbf{x}_j \geq 0 && \text{for all } j = 1,\ldots,n\\
& \mathbf{x}_j \in \mathbb{Z} && \text{for all } j = 1,\ldots,n
\end{aligned}
$$

In contrast to LPs, the feasible region of a MIP is not explicitly described as a convex set.
The feasible solutions are the integer points in an explicitly given polyhedron.

The feasible region is the convex hull of these feasible integer points, called the *integer hull*.
If the coefficients $a_{ij}$ and $b_i$ are rational, then this integer hull is again a polyhedron (although it may require exponentially many inequalities to describe explicitly).

In general, MIP is NP-hard.
But note, that if we had an explicit linear description of the integer hull with only polynomially many inequalities, then we could solve the problem in polynomial time by linear programming.

## LP-based branch-and-bound

If some constraints are omitted from a problem, we speak about a *relaxation*.
The **LP-relaxation** of a MIP is obtained by removing the integrality constraints.

The classic way to solve a MIP is the LP-based **branch-and-bound** procedure.
That is, similarly to [constraint programming](../cp/cp.md), the optimization is embedded into a tree search scheme; however, bounds obtained from LP relaxations are used to prune the search tree.

During the search, we maintain a set of open nodes, a global upper bound $UB$, and a global lower bound $LB$.
Initially, the set of open nodes consists of a single node corresponding to the original problem; the global upper bound, which refers to the objective value of the currently best solution, is $\infty$; and the global lower bound is $-\infty$;.
The procedure is:

1. If there are no open nodes, we are done. The best found solution is optimal, if any; otherwise the problem is infeasible.

2. We select an open node and solve its LP-relaxation, obtaining a solution $\bar{\mathbf{x}} \in \mathbb{R}^n_{0\leq}$.
    The selected node is removed from the set of open nodes.

    1. If the LP relaxation is infeasible, the node is pruned.
    
    2. If the objective value of the LP solution is greater then the current upper bound, i.e., $UB < c\bar{\mathbf{x}}$, we prune the node, since no better solution can be obtained from this branch.
    
    3. If the solution is integer, the global upper bound may be updated.

    4. If the solution is fractional, we branch. We select a fractional variable, say $\mathbf{x}_i$, and create two child nodes, i.e. two branches,
    
        - one with the additional constraint $\mathbf{x}_i \leq \lfloor \bar{\mathbf{x}} \rfloor$, 
        - and one with the constraint $\lceil \bar{\mathbf{x}} \rceil \leq \mathbf{x}_i$.

3. Go to the first step.

In practice, solvers do not rely on pure branch-and-bound, but instead use a **branch-and-cut approach**.
At a given node, the LP relaxation may be solved in multiple rounds: if the solution is fractional, additional valid constraints, called *cuts*, are generated and added to the model in order to cut off the current fractional solution.

Modern MIP solvers apply a wide range of techniques to further improve performance, for example:

- **Presolve**, where redundant constraints and variables are removed, coefficients are tightened, and the model is simplified before the actual search starts.
- **Primal heuristics**, which aim to quickly find feasible integer solutions.
    Good heuristic solutions improve the global upper bound early and help prune large parts of the search tree.
- **Symmetry detection and symmetry breaking**, which prevent the solver from exploring equivalent regions of the search space multiple times.
- **Parallelization**, where multiple nodes of the search tree are processed simultaneously using several CPU cores.
For example, in the presolve phase, duplciated columns, redundant rows are eliminited, and severel simplification are applied.
The solvers actually apply a **branch-and-cut** procedure, where solving a node consists of multiple rounds: if the solution is fractional, new constraints (called *cuts*), which cuts off that solution may be added to the corresponding problem.

## Solvers

In practice, LPs and MIPs are solved using highly optimized software packages called solvers.
They differ in performance, licensing model, and supported features.
See the most popular solvers in the following table.

| Solver                           | License Type                                            | Supported Problem Types |
| -------------------------------- | ------------------------------------------------------- | ----------------------- |
| **Gurobi** Optimization          | Commercial                                              | LP, MILP, MIQP, MIQCP   |
| IBM ILOG **CPLEX**               | Commercial                                              | LP, MILP, MIQP, MIQCP   |
| FICO **Xpress**                  | Commercial                                              | LP, MILP, MIQP          |
| Zuse Institute Berlin **SCIP**   | Open-source (Apache2)                                   | LP, MILP, MINLP, CIP    |
| COIN-OR **CBC**                  | Open-source (EPL)                                       | LP, MILP                |
| **HiGHS**                        | Open-source (MIT)                                       | LP, MILP, QP            |

Note that commercial solvers often provide *academic licence* for students and researchers.
