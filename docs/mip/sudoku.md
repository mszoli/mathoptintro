---
tags:
  - mip
  - puzzle
---

# Sudoku

Play online: <a href="https://www.puzzle-sudoku.com/" target="_blank">www.puzzle-sudoku.com</a>

## Rules

There is a *grid* of size $9\times 9$.
The goal is to write a number from $1,\ldots,9$ in each cell, such that each column, each row, and each of the nine $3\times 3$ subgrids that compose the grid contains all numbers exactly once.
Some numbers are pre-given.

For example:
```text
Task:                         Solution:
┌───────┬───────┬───────┐     ┌───────┬───────┬───────┐
│ · · 4 │ 6 · · │ 3 5 · │     │ 2 1 4 │ 6 8 7 │ 3 5 9 │
│ · · · │ · · 4 │ · · 7 │     │ 5 9 3 │ 1 2 4 │ 6 8 7 │
│ 8 · · │ 5 · · │ · · 2 │     │ 8 6 7 │ 5 3 9 │ 1 4 2 │
├───────┼───────┼───────┤     ├───────┼───────┼───────┤
│ 1 · 5 │ 3 · · │ · 6 · │     │ 1 7 5 │ 3 4 2 │ 9 6 8 │
│ · · · │ · · · │ · · · │     │ 4 8 2 │ 7 9 6 │ 5 1 3 │
│ · 3 · │ · · 1 │ 2 · 4 │     │ 6 3 9 │ 8 5 1 │ 2 7 4 │
├───────┼───────┼───────┤     ├───────┼───────┼───────┤
│ 7 · · │ · · 3 │ · · 1 │     │ 7 5 8 │ 2 6 3 │ 4 9 1 │
│ 3 · · │ 9 · · │ · · · │     │ 3 4 6 │ 9 1 8 │ 7 2 5 │
│ · 2 1 │ · · 5 │ 8 · · │     │ 9 2 1 │ 4 7 5 │ 8 3 6 │
└───────┴───────┴───────┘     └───────┴───────┴───────┘
```

## MIP formulation

Rows and columns are indexed from 1 to 9 (left to right, and top to bottom, respectively).
Let $G_{ij}$ denote the pre-given number for cell $(i,j)$, if any, otherwise $G_{ij} = \emptyset$.

### Variables

Let binary variable $\mathbf{x}_{ijk}$ indicate whether number $k$ is written into cell $(i,j)$.

Note that $\sum_{k=1}^n k \cdot \mathbf{x}_{ijk}$ expresses the number written in cell $(i,j)$.

### Constraints

There is exactly one number in a cell:
$$
\sum_{k=1}^9 \mathbf{x}_{ijk} = 1\quad \text{for all}\ i=1,\ldots,9,\ j=1,\ldots,9
$$

Each number occurs exactly once in a row:
$$
\sum_{j=1}^9 \mathbf{x}_{ijk} = 1\quad \text{for all}\ i=1,\ldots,9,\ k=1,\ldots,9
$$

Each number occurs exactly once in a column:
$$
\sum_{i=1}^9 \mathbf{x}_{ijk} = 1\quad \text{for all}\ j=1,\ldots,9,\ k=1,\ldots,9
$$

Each number occurs exactly once in a subgrid:
$$
\sum_{i=3p-2}^{3p}\sum_{j=3q-2}^{3q} \mathbf{x}_{ijk} = 1\ \quad\ \text{for all}\ k=1,\ldots,9,\ p=1,\ldots,3,\ q=1,\ldots,3
$$

Pre-given numbers:
$$
\mathbf{x}_{i,j,G(i,j)} = 1 \quad 
\text{for all}\ i=1,\ldots,9,\ j=1,\ldots,9,\ :\ G(i,j) \neq \emptyset
$$

### Objective

There is no objective, since it is a feasibility problem.

## Implementation

For the full code, see file <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/sudoku.py" target="_blank">`src/sudoku.py`</a>.
For the description of the input format, go to [Sudoku](../cp/sudoku.md).

### Solver

```python
import itertools as it

def _solve_sudoku_mip( grid:list[list[int]] ) -> list[list[int]]:
    """
    Solves Sudoku as a MIP with OR-Tools MathOpt.
    
    Args
    ----
    grid : list[list[int]]
        A 9x9 Sudoku grid as a list of row-lists.
        Filled cells are integers, empty cells are None.

    Returns
    -------
    grid : list[list[int]]
        A 9x9 Sudoku grid as a list of row-lists.
    """
    from ortools.math_opt.python import mathopt

    n = 3 
    N = range(n*n)

    assert len(grid) == n*n, 'invalid matrix size!'

    # BUILD MODEL
    model = mathopt.Model()

    # variables: x[i][j][k] = 1 <-> the number k+1 written into cell (i,j)
    x = [ [ [ model.add_binary_variable( name= f'x_{i}_{j}_{k}' ) for k in N ] for j in N ] for i in N ]

    # constraints: pre-given numbers
    for (i,j) in it.product(N,N):
        if grid[i][j] != None:
            x[i][j][grid[i][j]-1].lower_bound = 1
    
    # constraints: exactly one number in a cell
    for (i,j) in it.product(N,N):
        model.add_linear_constraint( sum( x[i][j][k] for k in N ) == 1 )

    # constraints: each number occurs exactly once in a row
    for (i,k) in it.product(N,N):
        model.add_linear_constraint( sum( x[i][j][k] for j in N ) == 1 )

    # constraints: each number occurs exactly once in a column
    for (j,k) in it.product(N,N):
        model.add_linear_constraint( sum( x[i][j][k] for i in N ) == 1 )

    # constraints: each number occurs exactly once in a 3x3 subgrid
    for (p,q,k) in it.product(range(n),range(n),N):
       model.add_linear_constraint( sum( x[i+n*p][j+n*q][k] for (i,j) in it.product(range(n),range(n)) ) == 1 )

    # SOLVE PROBLEM
    result = mathopt.solve( model, solver_type= mathopt.SolverType.HIGHS )
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL, f'status: {result.termination.reason.name}'

    # return solution
    return [ [ sum( (k+1)*int(round(result.variable_values(x[i][j][k]))) for k in N ) for j in N ] for i in N ]
```
