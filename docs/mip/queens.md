---
tags:
  - mip
  - constraint generation
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

## MIP formulation

Rows and columns (more precisely *ranks* and *files*) are indexed from 1 to $n$ (left to right and top to bottom, respectively).

### Variables

Let the binary variable $\mathbf{x}_{ij}$ indicate whether a queen is placed on square $(i,j)$, i.e., in row $i$ and column $j$.

### Constraints

There is **exactly one queen** in each row:
$$
\sum_{j=1}^n \mathbf{x}_{ij} = 1 \quad \text{for all}\ i=1,\ldots,n
$$

There is **exactly one queen** in each column:
$$
\sum_{i=1}^n \mathbf{x}_{ij} = 1 \quad \text{for all}\ j=1,\ldots,n
$$

There is **at most one queen** on each "\" diagonal (where the *difference* between the row and column indices is constant):
$$
\sum_{i,j:\ i-j=d} \mathbf{x}_{ij} \leq 1 \quad \text{for all}\ d = 1-n,\ldots n-1
$$

There is **at most one queen** on each "/" diagonal (where the *sum* of the row and column indices is constant):
$$
\sum_{i,j:\ i+j=s} \mathbf{x}_{ij} \leq 1 \quad \text{for all}\ s = 2,\ldots,2n
$$

### Objective

There is no objective, as this is a feasibility problem.

Note that the problem is infeasible for certain values of $n$ (for example, $n=2,3$).
One could, however, reformulate the problem to maximize the number of queens placed.
In this case, the objective would be $\sum_{i,j}\mathbf{x}_{ij}$, but the row and column constraints should then be replaced by inequalities ($\leq 1$) instead of equations.

## Implementation

For the full code, see file <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/queens.py" target="_blank">`src/queens.py`</a>.

```python
def solve_queens_mip( n:int ) -> None:
    """
    Solves the n-queens puzzle as a MIP with Google OR-Tools MathOpt.

    Args
    ----
    n : int
        The size of the board (and the number of queens).
    """
    from ortools.math_opt.python import mathopt
    
    # BUILD MODEL
    model = mathopt.Model()

    # variables: x[i][j] = 1 if and only if the queen of row i is in column j
    x = [ [ model.add_binary_variable( name= f'x_{i}_{j}' ) for j in range(n) ] for i in range(n) ]
 
    # constraints: queens cannot share columns
    for i in range(n):
        model.add_linear_constraint( sum( x[i][j] for j in range(n) ) == 1 )

    # constraints: queens cannot share rows
    for j in range(n):
        model.add_linear_constraint( sum( x[i][j] for i in range(n) ) == 1 )

    # constraints: queens cannot share / diagonals
    for s in range(0,2*n-1): # 0,1,...,2n-2
        model.add_linear_constraint( sum( x[i][j] for i in range(n) for j in range(n) if i+j == s ) <= 1 )
    
    # constraints: queens cannot share \ diagonals
    for d in range(-n+1,n): # -(n-1),...,n-1
        model.add_linear_constraint( sum( x[i][j] for i in range(n) for j in range(n) if i-j == d ) <= 1 )

    # SOLVE PROBLEM
    result = mathopt.solve( model, mathopt.SolverType.HIGHS )
    
    print( f'status: {result.termination.reason.name} | total time: {result.solve_stats.solve_time.total_seconds():.2f}' )

    if result.termination.reason in [mathopt.TerminationReason.FEASIBLE,mathopt.TerminationReason.OPTIMAL]:
        CHARS = '·×' # empty | queen
        for i in range(n):
            print( ' '.join( [ CHARS[1] if 0.5 < result.variable_values(x[i][j]) else CHARS[0] for j in range(n) ] ) ) 
        print( '' )
```

## Find all solutions

To obtain all feasible solutions of the n-queens problem, we need to solve the problem iteratively.
After a solution is found, we add a new constraint to the model to exclude it and re-solve the problem.
This process is repeated until the problem becomes infeasible.
We call this method **constraint generation**.

Let $\bar{\mathbf{x}}_{ij}$ denote the current (integer) solution.
That is, the queens are placed on the squares $S = \{ (i,j) : \bar{\mathbf{x}}_{ij} = 1 \}$, so that $\sum_{(i,j)\in S} \bar{\mathbf{x}}_{ij} = n$.
This solution can then be excluded by adding the following constraint:

$$
\sum_{(i,j)\in S} \mathbf{x}_{ij} \leq n-1
$$

``` mermaid
flowchart LR
    A([start]) --> B[build model]
    B --> C[solve]
    C --> D{feasible?}
    D -- no --> E([stop])
    D -- yes --> F["x' ← solution<br/>S = {(i,j) : x'<sub>ij</sub> = 1}"]
    F --> G["add to the model:<br/>∑<sub>(i,j)∈S</sub> x<sub>ij</sub> ≤ n−1"]
    G --> C
```

We need to rewrite the "solve part" of the code:

```python
# SOLVE PROBLEM
for iter in range(1,1000):
    result = mathopt.solve( model, mathopt.SolverType.HIGHS )

    if result.termination.reason not in [mathopt.TerminationReason.FEASIBLE,mathopt.TerminationReason.OPTIMAL]:
        break

    CHARS = '·×' # empty | queen
    print( f'solution #{iter}:' )
    for i in range(n):
        print( ' '.join( [ CHARS[1] if 0.5 < result.variable_values(x[i][j]) else CHARS[0] for j in range(n) ] ) ) 
    print( '' )    

    # exclude current solution
    model.add_linear_constraint( sum( x[i][j] for i in range(n) for j in range(n) if 0.5 < result.variable_values(x[i][j]) ) <= n-1 )
```
