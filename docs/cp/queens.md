---
tags:
  - cp
  - puzzle
---

# n-queens

## Rules

Place $n$ queens on an $n\times n$ chessboard in such a way that no two queens threaten each other (i.e., no two share a row, column, or diagonal).

For example ($n=5$):
```text
· · ♕ · ·
· · · · ♕
· ♕ · · ·
· · · ♕ ·
♕ · · · ·
```

## CP formulation

Rows and columns (more precisely *ranks* and *files*) are indexed from 1 to $n$ (left to right and top to bottom, respectively).

### Variables

Let the variable $\mathbf{x}_i$ with domain $D_i = \{1,\ldots,n\}$ denote the column of the queen in row $i$ ($i=1,\ldots,n$).
That is $\mathbf{x}_i = j$ if and only if there is a queen on square $(i,j)$.

!!! remark
    Note that this definition uses the fact that there is exactly one queen in each row.
    It enforces the placement of exactly $n$ queens on the board and guarantees that no two queens share a row.

### Constraints

There is **exactly one queen** in each column:

$$
\operatorname{alldifferent}(\mathbf{x}_1,\ldots,\mathbf{x}_n)
$$

!!! tip "Observation"
    Queens on squares $(i_1,j_1)$ and $(i_2,j_2)$ share a diagonal if and only if $|i_1-i_2| = |j_1-j_2|$, i.e., in terms of our variables, $|i_1-i_2| = |\mathbf{x}_{i_1}-\mathbf{x}_{i_2}|$.

There is **at most one queen** on each "\" diagonal:

$$
\operatorname{alldifferent}(\mathbf{x}_1,\mathbf{x}_2 + 1,\ldots,\mathbf{x}_n+(n-1))
$$

There is **at most one queen** on each "/" diagonal:

$$
\operatorname{alldifferent}(\mathbf{x}_1,\mathbf{x}_2 - 1,\ldots,\mathbf{x}_n-(n-1))
$$

### Objective

There is no objective, as this is a feasibility problem.

Note that the problem is infeasible for certain values of $n$ (for example, $n=2,3$).

## Implementation

For the full code, see file <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/queens.py" target="_blank">`src/queens.py`</a>.

```python
from ortools.sat.python import cp_model

def solve_queens_cp( n:int ) -> None:
    """
    Solves the n-queens puzzle as a CP with Google OR-Tools CP-SAT.

    Args
    ----
    n : int
        The size of the board (and the number of queens).
    """
    # BUILD MODEL
    model = cp_model.CpModel()

    # variables: x[i] = j if and only if the queen of row i is in column j
    # NOTE: by definition, there is only one queen in each row
    x = [ model.new_int_var( 0, n-1, f'x_{i}' ) for i in range(n) ]
 
    # constraints: queens cannot share columns
    model.add_all_different( x )

    # constraints: queens cannot share / diagonals
    model.add_all_different( x[i] + i for i in range(n) )
    
    # constraints: queens cannot share \ diagonals
    model.add_all_different( x[i] - i for i in range(n) )

    # SOLVE PROBLEM
    solver = cp_model.CpSolver()
    status = solver.Solve( model )

    print( f'status: {solver.status_name(status)} | total time: {solver.WallTime():.2f}' )

if __name__ == '__main__':
    solve_queens( 5 )
```

### Enumerating all solutions

Sometimes, there are several solutions for a CSP.
It is easy to see, that if we have a feasible placement of queens for an $n\geq 4$, we can obtain another solution by reflecting this placement.
Sometimes rotation also yields a different solution.

Constraint programming allows us to enumerate all feasible solutions of a problem.
With OR-Tools CP-SAT it is very easy to make it: we just have to set the appropriate parameter before calling the solution process:

```python
solver.parameters.enumerate_all_solutions = True
```

!!! note "Solution callback"
    In `src/cp/queens.py`, we define and set a callback – which are called by the solver for each feasible solution found – to print out solutions.
