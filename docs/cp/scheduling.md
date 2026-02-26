---
tags:
  - cp
  - scheduling
  - interval variables
  - non-overlapping constraints
---

# Machine Scheduling with Constraint Programming

Machine scheduling is about to schedule the processing of a set $\mathcal{J}$ of *jobs* on a set $\mathcal{M}$ of *machines* such that each machine can process at most one job at a time, and each job can be processed on at most one machine at a time.
For a more detailed introduction, check the page [Machine Scheduling](../../intro/scheduling).

Here, we focus on a **single-machine problem** and solve it using constraint programming. 
We will get familiar with the *interval variables* and the *no-overlap constraints*.

## Problem definition

We consider the problem $1|r_j|\sum w_j C_j$.
That is, each job $j\in\mathcal{J}$ has:

- a **processing time** $p_j$,
- a priority **weight** $w_j$,
- a **release date** $r_j$,

and the goal is to minimize the **weighted sum of completion times**.

## CP formulation

Let $\mathcal{J}=\{1,\ldots,n\}$.

### Variables (and constraints)

!!! tip "Interval variables"
    An **interval variable** allows to model an interval of time.

    Actually, it is both a variable and a constraint.
    It is a constraint, since it ties together multiple variables (start, duration, end, etc.) and enforces their relationships.
    It is a variable, since it can appear in multiple constraints.

    OR-Tools CP-SAT provides several types of interval variables, for example:
    `new_interval_var`, `new_fixed_size_interval_var`, `new_optional_interval_var`, and `new_optional_fixed_size_interval_var`.

Let variables $\mathbf{S}_j$ and $\mathbf{C}_j$ denote the start and the completion of job $j \in \mahtcal{J}$ and let $\mathbf{I}_j = [\mathbf{S}_j,\mathbf{C}_j]$ be the corresponding interval variable with fixed size $p_j$.
That is, $\mathbf{C}_j = \mathbf{S}_j + p_j$ must hold.

Let's notice that $\operatorname{UB} = \max_j r_j + \sum_{j=1}^n p_j$ is a valid upper bound on the makespan of the optimal schedule.
Thus, we can use this value as an upper bound of the variables: $\mathbf{S}_j \in [r_j,\operatorname{UB}-p_j]$ and $\mathbf{C}_j \in [r_j+p_j,\operatorname{UB}]$.

### Constraints

!!! tip "Non-overlapping constraints"
    A **disjuncive constraint** (or **non-overlapping constraint**) ensures that the given intervals do not overlap.

    For example, OR-Tools CP-SAT provides the constraint `add_no_overlap`.

    Check the `disjunctive` constraint in the [Global Constraint Catalog](https://sofdem.github.io/gccat/gccat/Cdisjunctive.html#uid19717).    

With such a constraint, we can easily formulate the scheduling constraints:

$$
\operatorname{disjunctive}(\mathbf{I}_1,\ldots,\mathbf{I}_n)
$$

### Objective

The objective is to minimize the weighted sum of completion times:

$$
\operatorname{minimize} \sum_{j=1}^n w_j\mathbf{C}_j
$$

## Implementation

For the full code, see file <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/scheduling.py" target="_blank">`src/scheduling.py`</a>.

```python
def schedule_jobs_on_a_single_machine( processing_times:list[int], weights:list[int], release_times:list[int] ) -> None:
    """
    Solves scheduling problem "1 | r_j | sum w_jC_j" as a CP with OR-Tools CP-SAT.
    
    Args
    ----
    processing_times: list[int]
        List of processing times.
    weights: list[int]
        List of weights.
    release_times: list[int]
        List of release times.
    """
    # INIT
    n = len(processing_times)
    UB = max(release_times) + sum(processing_times) # upper bound on the makespan
    
    JOBS = range(n)
    
    # BUILD MODEL
    model = cp_model.CpModel()

    # variables: interval variables ~ start times
    jobs = [ model.new_fixed_size_interval_var(
        start= model.new_int_var( release_times[i], UB, f'start_{i}' ),
        size=  processing_times[i],
        name=  f'job_{i}'
    ) for i in JOBS ]

    # constraint: jobs cannot overlap
    model.add_no_overlap( jobs )

    # objective: weighted sum of completion times
    model.minimize( sum( weights[i] * jobs[i].end_expr() for i in JOBS ) )
    
    # SOLVE PROBLEM
    solver = cp_model.CpSolver()
    #solver.parameters.log_search_progress = True
    #solver.parameters.max_time_in_seconds = 30
    status = solver.solve( model )

    print( f'status: {solver.status_name(status)} | total time: {solver.WallTime():.2f} | objective: {int(solver.objective_value)}  (best lb: {int(solver.best_objective_bound)})' )

    if status in [ cp_model.FEASIBLE, cp_model.OPTIMAL ]:
        _print_schedule( processing_times, weights, release_times, [ solver.value(jobs[i].start_expr()) for i in JOBS ] )
```

### Exercises

1. Modify function `schedule_jobs_on_a_single_machine` to minimize the makespan of the schedule.
    
    Hint: check method/constraint `model.add_max_equality`.

2. Implement function `schedule_jobs_on_identical_machines` to schedule jobs on identical parallel machines.

    Hint: use optional interval variables: `model.new_optional_fixed_size_interval_var`.
    
3. Implement a function that solves a job-shop scheduling problem.

4. Implement function _draw_schedule for GANTT chart vizualization (see Plotly, for an example).
