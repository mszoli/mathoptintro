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

Consider a $(\bar{x},\bar{\pi})$ primal-dual solution pair.
That is, $\bar{x}$ is a feasible solution for the primal problem, and $\bar{\pi}$ is a feasible solution for the dual problem.
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
