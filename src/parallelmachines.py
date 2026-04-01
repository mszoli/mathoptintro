from ortools.math_opt.python import mathopt

import itertools as it

from time import perf_counter

# EXERCISES
# 1.1 Implement a solution procedure for the subproblems which is also efficient for larger instances.

def solve_upmsp_as_a_mip( processing_times:list[list[int]], setup_times:list[list[list[int]]], solver_type:mathopt.SolverType= mathopt.SolverType.GSCIP ):
    """
    Solves the given instance for the **Unrelated Parallel Machine Scheduling Problem** with **machine- and sequence-dependent setup times**
    as a **MIP** with **OR-Tools MathOpt** based on:

    Tran, T. T., Araujo, A., & Beck, J. C. (2016).
    *Decomposition methods for the parallel machine scheduling problem with setups*.
    INFORMS Journal on Computing, 28(1), 83-95.

    Args
    ----
    processing_times: list[list[int]]
        Processing times: proc_times[i][j] is the processing time of job j (j=0,...,n-1) on machine i (i=0,...,m-1).
    setup_times: list[list[list[int]]]
        Setup times: setup_times[i][j][k] is the setup time of from job j (j=0,...,n) to job k (k=0,...,n-1) on machine i (i=0,...,m-1),
        where setup_times[i][n][k] refers to the case when job k is the first job to be processed on machine i.
    solver_type: mathopt.SolverType
        The underlying solver to use (e.g., GSCIP, HIGHS, GUROBI).
    """
    # INIT
    m = len(processing_times)
    n = len(processing_times[0])

    JOBS = range(n)
    EXTENDED_JOBS = range(n+1)
    MACHINES = range(m)

    # BUILD MODEL
    model = mathopt.Model( name= 'upmsp' )

    # variables: x[i][j] = 1 if and only if job j is assigned to machine i | x[i][-1] refers to the dummy job on machine i
    x = [ [ model.add_binary_variable( name= f'x_{i}_{j}' ) for j in EXTENDED_JOBS ] for i in MACHINES ]

    # variables: y[i][j][k] = 1 if and only if job k is processed directly after job j on machine i
    y = [ [ [ model.add_binary_variable( name= f'y_{i}_{j}_{k}' ) for k in EXTENDED_JOBS ] for j in EXTENDED_JOBS ] for i in MACHINES ]

    # variables: z[i] is the total setup time on machine i
    z = [ model.add_variable( lb= 0, name= f'xi_{i}' ) for i in MACHINES ]

    # variables: C[j] is the completion time of job j
    C = [ model.add_variable( lb= 0, name= f'C_{j}' ) for j in EXTENDED_JOBS ]

    # variables: makespan
    Cmax = model.add_variable( lb= 0, name= 'Cmax' )

    # constraints: each job is assigned to exactly one machine
    for j in JOBS:
        model.add_linear_constraint( sum( x[i][j] for i in MACHINES ) == 1 )

    # constraints: dummy job is always assigned
    for i in MACHINES:
        x[i][-1].lower_bound = 1
    
    # constraints: each (real) job has exactly one predecessor
    for (i,k) in it.product( MACHINES, EXTENDED_JOBS ):
        model.add_linear_constraint( x[i][k] == sum( y[i][j][k] for j in EXTENDED_JOBS ) )
    
    # constraints: each (real) job has exactly one successor
    for (i,j) in it.product( MACHINES, EXTENDED_JOBS ):
        model.add_linear_constraint( x[i][j] == sum( y[i][j][k] for k in EXTENDED_JOBS ) )

    # constraints: completion time for dummy job
    C[-1].upper_bound = 0

    # constraints: completion times for real jobs
    for (i,j,k) in it.product( MACHINES, EXTENDED_JOBS, JOBS ):
        BIGM = sum( processing_times[i] ) + n * max( setup_times[i][p][k] for p in EXTENDED_JOBS )
        model.add_linear_constraint( C[k] >= C[j] + setup_times[i][j][k] + processing_times[i][k] - BIGM * (1 - y[i][j][k]) )

    # constraints - total setup time on machines
    for i in MACHINES:
        model.add_linear_constraint( z[i] == sum( y[i][j][k] * setup_times[i][j][k] for j in EXTENDED_JOBS for k in JOBS ) )

    # constraints - makespan
    for i in MACHINES:
        model.add_linear_constraint( z[i] + sum( x[i][j] * processing_times[i][j] for j in JOBS ) <= Cmax )

    # objective: makespan
    model.minimize( Cmax )

    # SOLVE PROBLEM
    result = mathopt.solve( model, solver_type= solver_type )

    if result.termination.reason not in [mathopt.TerminationReason.OPTIMAL,mathopt.TerminationReason.FEASIBLE]:
        return

    print( f'status: {result.termination.reason.name} | time: {result.solve_time().total_seconds():.1f} | objval: {result.objective_value():.2f} | lb: {result.best_objective_bound():.2f} | gap: {(result.objective_value()-result.best_objective_bound())/result.best_objective_bound():.4f}' )

    for i in MACHINES:
        machine_sequence = [-1]

        while True:
            next_job = next( ( k for k in JOBS if 0.5 < result.variable_values( y[i][machine_sequence[-1]][k] ) ), None )

            if next_job is None:
                break

            machine_sequence.append(next_job)

        machine_makespan = int(round(result.variable_values(C[machine_sequence[-1]]))) if 1 < len(machine_sequence) else 0
        print( f'  machine {i:2d} | makespan: {machine_makespan:4d} | jobs: {" -> ".join( map( str, machine_sequence[1:] ) )} ' )

def solve_subproblem_by_enumeration( processing_times:list[int], setup_times:list[list[int]], jobs:list[int] ) -> tuple[int,list[int]]:
    """
    Solves the the given LBBD subproblem (an instance for problem 1|sds|Cmax) with a naiv enumeration procedure.

    Args
    ----
    processing_times: list[int]
        Processing times: proc_times[j] is the processing time of job j (j = 0,...,n-1).
    setup_times: list[list[int]]
        Setup times: setup_times[j][k] is the setup time of from job j (j = 0,...,n) to job k (k = 0,...,n-1),
        where setup_times[n][k] refers to the case when job k is the first job to be processed.
    jobs: list[int]
        The subset of jobs {0,...,n-1} to schedule.

    Returns
    -------
    best_makespan: int
        Optimal makespan value for the problem.
    best_sequence: list[int]
        Optimal job sequence for the problem.
    """
    if len(jobs) == 0:
        return 0, jobs
    
    if len(jobs) == 1:
        return setup_times[-1][jobs[0]] + processing_times[jobs[0]], jobs
    
    best_sequence = None
    best_makespan = None

    for sequence in it.permutations(jobs):
        makespan = setup_times[-1][sequence[0]] + processing_times[sequence[0]]        
        makespan += sum( setup_times[sequence[idx-1]][sequence[idx]] + processing_times[sequence[idx]] for idx in range(1,len(sequence)) )
        
        if best_sequence is None or makespan < best_makespan:
            best_makespan = makespan
            best_sequence = sequence[:]

    return best_makespan, best_sequence

def solve_upmsp_with_lbbd( proc_times:list[list[int]], setup_times:list[list[list[int]]], solver_type:mathopt.SolverType= mathopt.SolverType.GSCIP ):
    """
    Solves the given instance for the Unrelated Parallel Machine Scheduling Problem (UPMSP) with machine- and sequence-dependent setup times
    with a **Logic-Based Benders Decomposition (LBBD)** based on:

    Tran, T. T., Araujo, A., & Beck, J. C. (2016).
    *Decomposition methods for the parallel machine scheduling problem with setups*.
    INFORMS Journal on Computing, 28(1), 83-95.

    Args
    ----
    proc_times: list[list[int]]
        Processing times: proc_times[i][j] is the processing time of job j (j = 0,...,n-1) on machine i (i = 0,...,m).
    setup_times: list[list[list[int]]]
        Setup times: setup_times[i][j][k] is the setup time of from job j (j = 0,...,n) to job k (k = 0,...,n-1) on machine i (i = 0,...,m),
        where setup_times[i][n][k] refers to the case when job k is the first job to be processed on machine i.
    solver_type: mathopt.SolverType
        The underlying solver to use (e.g., GSCIP, HIGHS, GUROBI).
    """
    # INIT
    m = len(proc_times)
    n = len(proc_times[0])

    JOBS = range(n)
    EXTENDED_JOBS = range(n+1) # EXTENDED_JOBS[n] (or EXTENDED_JOBS[-1]) refers to the dummy job
    MACHINES = range(m)

    # BUILD MASTER MODEL
    # NOTE: there are no completion time variables and constraints
    # NOTE: binary precedence variables are relaxed
    model = mathopt.Model( name= 'upmsp_master' )

    # variables: x[i][j] = 1 if and only if job j is assigned to machine i
    x = [ [ model.add_binary_variable( name= f'x_{i}_{j}' ) for j in EXTENDED_JOBS ] for i in MACHINES ]

    # variables: y[i][j][k] = 1 if and only if job k is processed directly after job j on machine i
    y = [ [ [ model.add_variable( lb= 0, ub= 1, name= f'y_{i}_{j}_{k}' ) for k in EXTENDED_JOBS ] for j in EXTENDED_JOBS ] for i in MACHINES ]

    # variables: z[i] is the total setup time on machine i
    z = [ model.add_variable( lb= 0, name= f'z_{i}' ) for i in MACHINES ]

    # variables: makespan
    Cmax = model.add_variable( lb= 0, name= 'Cmax' )

    # constraints: each (real) job is assigned to exactly one machine
    for j in JOBS:
        model.add_linear_constraint( sum( x[i][j] for i in MACHINES ) == 1 )

    # constraints: dummy job is assigned for all machines
    for i in MACHINES:
        x[i][-1].lower_bound = 1
    
    # constraints: each (real) job has exactly one predecessor
    for (i,k) in it.product( MACHINES, EXTENDED_JOBS ):        
        model.add_linear_constraint( x[i][k] == sum( y[i][j][k] for j in EXTENDED_JOBS ) )
    
    # constraints: each (real) job has exactly one successor
    for (i,j) in it.product( MACHINES, EXTENDED_JOBS ):        
        model.add_linear_constraint( x[i][j] == sum( y[i][j][k] for k in EXTENDED_JOBS ) )

    # constraints: total setup time on machines
    for i in MACHINES:
        model.add_linear_constraint( z[i] == sum( y[i][j][k] * setup_times[i][j][k] for j in EXTENDED_JOBS for k in JOBS ) )

    # constraints: makespan
    for i in MACHINES:
        model.add_linear_constraint( z[i] + sum( x[i][j] * proc_times[i][j] for j in JOBS ) <= Cmax )

    # objective: makespan
    model.minimize( Cmax )

    # SOLVE PROBLEM
    opt_start = perf_counter()
    for iter in range(1,1000):
        print( f'iteration: {iter}' )

        # SOLVE MASTER PROBLEM
        iter_start = perf_counter()
        result = mathopt.solve( model, solver_type= solver_type )
        iter_end = perf_counter()
        print( f'  status: {result.termination.reason.name} | time: {iter_end-iter_start:.2f} (total: {iter_end-opt_start:.2f})')

        if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
            break

        master_makespan = int(round(result.objective_value()))
        print( f'  makespan: {master_makespan}' )

        # SOLVE SUBPROBLEMS
        are_subproblems_feasible = True

        for i in MACHINES:
            # solve subproblem
            assigned_jobs = [ j for j in JOBS if 0.5 < result.variable_values( x[i][j] ) ]

            machine_makespan, machine_sequence = solve_subproblem_by_enumeration( proc_times[i], setup_times[i], assigned_jobs )

            # check feasibility
            feasible = machine_makespan <= master_makespan

            print( f'  [{"FEAS" if feasible else "INF "}] machine {i} | makespan: {machine_makespan} | jobs: {" -> ".join( map( str, machine_sequence ) )} ' )

            if feasible:
                continue

            are_subproblems_feasible = False

            # add Benders cut
            model.add_linear_constraint( Cmax >= machine_makespan - sum( (1 - x[i][j]) * (proc_times[i][j] + max( setup_times[i][k][j] for k in assigned_jobs )) for j in assigned_jobs ) )

        if are_subproblems_feasible:
            break

if __name__ == '__main__':
    from scheduling_instances import random_upmsp_instance

    proc_times, setup_times = random_upmsp_instance( n= 10, m= 5 )

    solver_type = mathopt.SolverType.GSCIP

    solve_upmsp_as_a_mip( proc_times, setup_times, solver_type )
    # solve_upmsp_with_lbbd( proc_times, setup_times, solver_type )
    