---
tags:
  - cp
  - packing
  - interval variables
  - non-overlapping constraints
---

# Rectangle packing

A set of rectangles must be packed into a container rectangle without overlaps. The rectangles must be aligned parallel to the container.
If the total area of the rectangles equals the area of the container, this is called a **perfect rectangle packing**.

A **perfect squared square** is a square that can be dissected into smaller squares of different sizes.

## CP formulation (without rotation)

Let $\mathcal{R} = \{1,\ldots,n\}$ be the set of rectangles, where

- $w_j$ and $h_i$ is the width and the height of the rectangle $j$;
- $W_C$ and $H_C$ is the width and the height of the container rectangle $C$.

### Variables

Let variables $\mathbf{x}_j$ and $\mathbf{y}_j$ denote the coordinates of the bottom-left corner of rectangle $j\in \mathcal{R}$ in the packing.
Clearly, $0 \leq \mathbf{x}_j \leq W_C - w_j$ and $0 \leq \mathbf{y}_j \leq H_C - h_j$.

Let the interval variables $\mathbf{I}^x_j = [\mathbf{x}_j,\mathbf{x}_j + w_j]$ and $\mathbf{I}^y_j = [\mathbf{y}_j,\mathbf{y}_j + h_j]$ associated with rectangle $j$ express the projection of the rectangle (as intervals) onto the $x$ and $y$ axes, respectively.

### Constraints

!!! tip "Multi-dimensional non-overlapping constraints"
    A **disjoint constraint** (or **multi-dimensional non-overlapping constraint**) ensures that the given rectangles (or more generally, orthotopes) do not overlap.

    For example, OR-Tools CP-SAT provides the constraint `add_no_overlap_2d` for two-dimensional intervals.

    Check the `diffn` (or `disjoint`) constraint in the [Global Constraint Catalog](https://sofdem.github.io/gccat/gccat/Cdiffn.html).

With such a constraint, we can easily formulate the packing constraints:

$$
\operatorname{disjoint}((\mathbf{I}^x_1,\ldots,\mathbf{I}^x_n),(\mathbf{I}^y_1,\ldots,\mathbf{I}^y_n))
$$

### Objective

If we are certain that all rectangles can be packed, i.e., the problem is feasible, no objective function is needed.
Otherwise, one can maximize the number of packed rectangles, which requires additional variables and constraints.

## Implementation

For the full code, see file <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/rectangle.py" target="_blank">`src/rectangle.py`</a>.

```python
def solve_rectangle_packing_without_rotation( container:tuple[int,int], rectangles:list[tuple[int,int]] ) -> None:
    """
    Solves the given instance of **Rectangle Packing without rotation** as a CP with **OR-Tools CP-SAT**.

    Args
    ----
    container: tuple[int,int]
        Size of the container as a (width,height) tuple.
    rectangles: list[tuple[int,int]]
        List of rectangles as (width,height) tuples.
    """
    n = len(rectangles)

    # BUILD MODEL
    model = cp_model.CpModel()

    # variables: x- and y-coordinates for the bottom-left corners
    x = [ model.new_int_var( 0, container[0] - rectangles[i][0], f'x_{i}' ) for i in range(n) ]
    y = [ model.new_int_var( 0, container[1] - rectangles[i][1], f'y_{i}' ) for i in range(n) ]

    # variables: intervals for projection on x- and y-axes
    xint = [ model.new_fixed_size_interval_var( x[i], rectangles[i][0], f'xint_{i}' ) for i in range(n) ]
    yint = [ model.new_fixed_size_interval_var( y[i], rectangles[i][1], f'yint_{i}' ) for i in range(n) ]

    # constraints: no overlap
    model.add_no_overlap_2d( xint, yint )

    # SOLVE PROBLEM
    solver = cp_model.CpSolver()
    status = solver.solve( model )

    print( f'status: {solver.status_name(status)} | total time: {solver.WallTime():.2f}' )

    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        draw_rectangle_packing( container, rectangles, [ ( solver.value(x[i]), solver.value(y[i]) ) for i in range(n) ] )
```

### Exercises

1. Modify function `solve_rectangle_packing_without_rotation` to maximize the number of packed rectangles (see the infeasible cases).

    Hint: use optional interval variables: `new_optional_fixed_size_interval_var`.

2. Implement function `solve_rectangle_packing_with_rotation`, where rectangles can be rotated by 90 degrees.

    Hint: rectangle widths and heights are not fixed anymore (see, `new_int_var_from_domain` and `cp_model.Domain.from_values` along with `model.add_allowed_assignments`).
