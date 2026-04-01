# Linear programming

A **linear programming** (*LP*) problem aims to find values for a set of decision **variables** that satisfy a collection of **linear constraints** while minimizing or maximizing a **linear objective function**.

We consider the following general form:

$$
\begin{aligned}
\text{minimize} \quad & \sum_{j=1}^n c_j \mathbf{x}_j \\
\text{subject to} \quad 
& \sum_{j=1}^n a_{ij} \mathbf{x}_j \geq b_i && \text{for all } i = 1,\ldots,m \\
& \mathbf{x}_j \geq 0 && \text{for all } j = 1,\ldots,n
\end{aligned}
$$

A compact way to write the problem is:

$$
\min \left\{ c\mathbf{x}\ :\ A\mathbf{x} \geq b,\ \mathbf{x} \geq 0 \right\}
$$

That is, the model consists of:
    
- $n$ continuous variables (or *columns*): $\mathbf{x}_1,\ldots,\mathbf{x}_n$;
- $m$ linear inequalities (or *rows*) (not counting the non-negativity constraints), where $a_{ij}\in\mathbb{R}$, $b_i\in\mathbb{R}$;
- and a linear objective function, where $c_j\in\mathbb{R}$ ($1\leq j\leq n$).

!!! tip "Any LP can be transformed into this general form"
    A maximization problem can be converted into a minimization problem by multiplying the objective coefficients $c_j$ by -1.
    An equation $a\mathbf{x} = b$ can be replaced by two inequalities: $a\mathbf{x} \geq b$ and $-a\mathbf{x} \geq -b$.

The set of feasible solutions is called a **polyhedron** (or *polytope* if it is bounded).
If an LP has an optimal solution, then it has an optimal solution at an *extreme point* (*vertex*) of the feasible region.

## Dual problem

Each primal LP is associated with a dual problem.

$$
\begin{aligned}
\text{maximize} \quad & \sum_{i=1}^m \pi_i b_i \\
\text{subject to} \quad 
& \sum_{i=1}^m \pi_i a_{ij} \leq c_j && \text{for all}\ j = 1,\ldots,n \\
& \pi_i \geq 0 && \text{for all}\ i = 1,\ldots,m
\end{aligned}
$$

In compact form, the dual can be written as:

$$
\max \left\{ \pi b\ :\ \pi A \leq c,\ 0 \leq \pi \right\}
$$

Consider a $(\bar{x},\bar{\pi})$ primal-dual solution pair, that is, $\bar{x}$ is a feasible solution for the primal problem, and $\bar{\pi}$ is a feasible solution for the dual problem.
Clearly, $\bar{\pi}b \leq \bar{\pi}A\bar{x} \leq c\bar{x}$, thus,

$$
\max \left\{ \pi b\ :\ \pi A \leq c,\ 0 \leq \pi \right\} \leq \min \left\{ c\mathbf{x}\ :\ A\mathbf{x} \geq b,\ \mathbf{x} \geq 0 \right\}
$$

!!! tip "Duality theorem"

    If the primal problem has an optimal solution, then the dual problem also has an optimal solution, and their objective values are equal:

    $$
    \max \left\{ \pi b\ :\ \pi A \leq c,\ 0 \leq \pi \right\} = \min \left\{ c\mathbf{x}\ :\ A\mathbf{x} \geq b,\ \mathbf{x} \geq 0 \right\}
    $$

## Solution approaches

### Simplex method

The vertex-based **simplex method** is originated from *George Dantzig*.
It starts from a basic feasible solution and moves to an adjacent vertex of the polyhedron at each step to improve the objective value (or stop when no improving adjacent vertex exists).

In theory, the worst-case running time is exponential.
However, in practice, the simplex method is extremely efficient; it solves even very large real-world LPs quickly.

!!! quote "Simplex method"
    Dantzig, G. B. (1951).
    *Maximization of a linear function of variables subject to linear inequalities*.
    Activity analysis of production and allocation, 13(1), 339-347.

### Polynomial time algorithms

Leonig Khachiyan's **ellipsoid method** proved that LPs can be solved in polynomial time.
However, it is rarely competitive in practice.

!!! quote "Ellipsoid method"
    Khachiyan, L. G. (1979).
    *A polynomial algorithm in linear programming*.
    In Doklady Akademii Nauk (Vol. 244, No. 5, pp. 1093-1096). Russian Academy of Sciences.

Later, **interior-point methods** combined the polynomial time guarantees with strong practical performance.

!!! quote "Karmarkar's algorithm"
    Karmarkar, N. (1984).
    *A new polynomial-time algorithm for linear programming*.
    Combinatorica, 4(4), 373-395.

## Column Generation

Recall the primal-dual pair:

$$
\begin{align*}
z_P &= \min \left\{ c\mathbf{x}\ :\ A\mathbf{x} \geq b,\ \mathbf{x} \geq 0 \right\}\\
z_D &= \max \left\{ \pi b\ :\ \pi A \leq c,\ 0 \leq \pi \right\}
\end{align*}
$$

Now suppose that the number of variables (columns), $n$, is extremely large.
In that case, solving the full LP directly may be impractical, since we cannot explicitly include all columns in the model.

There is a good news!
The key observation is that an LP with $m$ constraints has an optimal basic feasible solution in which at most $m$ variables are basic.
Therefore, even if the full model contains a huge number of columns, an optimal solution typically uses only a relatively small subset of them.

This motivates the idea of column generation:
instead of solving the full problem with all columns, we start with a restricted subset of columns and generate additional columns only when they are needed.

### Restricted Master Problem

Let $A'$ be a matrix consisting of only a subset of the columns of $A$ (and let $c'$ contain the objective coefficients of the selected columns).
The corresponding *restricted master problem* (RMP) is:

$$
\begin{align*}
z'_P &= \min \left\{ c\mathbf{x}\ :\ A'\mathbf{x} \geq b,\ \mathbf{x} \geq 0 \right\}\\
z'_D &= \max \left\{ \pi b\ :\ \pi A' \leq c,\ 0 \leq \pi \right\}
\end{align*}
$$

Due to the restrictions, and applying the strong duality, we have:

$$
z_D = z_P \leq z'_P = z'_D
$$

Let $(\bar{x}, \bar{\pi})$ be an optimal primal-dual solution pair for the restricted master problem.
If we extend $\bar{x}$ by setting all non-generated variables to zero, we obtain a feasible solution for the full primal (master) problem with the same objective value.

Similarly, the dual solution $\bar{\pi}$ yields the same value $\bar{\pi}b$ as in the restricted problem.
However, $\bar{\pi}$ is not necessarily feasible for the full dual (master) problem.
But if so, then we have $z_D = z_P = z'_P = z'_D$, therefore $((\bar{x},0),\bar{\pi})$ is an **optimal** primal-dual solution pair for the original problem.

The crucial question is whether $\bar{\pi}$ is also feasible for the dual master problem...

### Column generation (variable pricing)

So, we need to check whether $\bar{\pi}$ is feasible for the master dual, that is, for each column $a_j$, $\bar{\pi}a_j \leq c_j$ holds.

If there exists a column $a_j$ with negative *reduced cost* $\bar{c}_j = c_j - \bar{\pi}a_j$, then the current solution is not yet optimal for the master problem, so it should be added to the RMP.
Finding a column with negative reduced cost is called the **pricing problem**.

The overall column generation procedure is therefore:

1. Start with a restricted set of columns and solve the RMP.
2. Obtain the optimal dual solution $\bar{\pi}$ of the RMP.
3. Solve the pricing problem to search for a column with negative reduced cost.
4. If such a column exists, add it to the RMP and repeat.
5. If no improving column exists, stop: the current solution is optimal for the master LP.

``` mermaid
flowchart LR
    Start([start]) --> BuildMaster[build RMP]
    BuildMaster --> SolveMaster[solve RMP<br>π'←dual]
    SolveMaster --> SolveSub[solve pricing problem]
    SolveSub --> AllFeasible{π'A≤c?}
    AllFeasible -- yes --> Stop([stop])  
    AllFeasible -- no --> NewColumn["Add column(s) with<br>negative reduced costs"]
    NewColumn --> SolveMaster
```
