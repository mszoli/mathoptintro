from ortools.sat.python  import cp_model

# EXERCISES
# 1. Modify function schedule_jobs_on_a_single_machine to minimize the makespan of the schedule.
#    (Hint: model.add_max_equality)
# 2. Implement function schedule_jobs_on_identical_machines to schedule jobs on identical parallel machines.
#    (Hint: model.new_optional_fixed_size_interval_var)
# -------------------------------------------------------------------------------------------------
# + Implement a function that solves a job-shop scheduling problem.
# + Implement function _draw_schedule for GANTT chart vizualization (see Plotly, for an example).

def _draw_schedule( processing_times:list[int], start_times:list[int] ) -> None:
    """
    Draws the given schedule.

    Args
    ----
    processing_times: list[int]
        List of processing times.
    start_times: list[int]
        List of start times.
    """
    raise NotImplementedError( 'drawing is not implemented' )

def _print_schedule( processing_times:list[int], weights:list[int], release_times:list[int], start_times:list[int] ) -> None:
    """
    Prints the given schedule.

    Args
    ----
    processing_times: list[int]
        List of processing times.
    weights: list[int]
        List of weights.
    release_times: list[int]
        List of release times.
    start_times: list[int]
        List of start times.
    """
    n = len(processing_times)

    print( '────┬─────┬─────┬─────┬─────────────' )
    print( 'job │  w  │  p  │  r  │  interval   ' )
    print( '────┼─────┼─────┼─────┼─────────────' )
    for i in sorted( range(n), key= lambda i : start_times[i] ):
        print( f'{i:3d} │ {weights[i]:3d} │ {processing_times[i]:3d} │ {release_times[i]:3d} │ {start_times[i]:4d} -- {start_times[i]+processing_times[i]}')
    print( '────┴─────┴─────┴─────┴─────────────' )

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


    # minimize makespan
    #span = model.new_int_var(0, UB, "span")
    #model.add_max_equality(span, [j.end_expr() for j in jobs])
    #model.minimize(span)

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

def schedule_jobs_on_identical_machines( processing_times:list[int], weights:list[int]= None, release_times:list[int]= None, nmachines:int= 2 ) -> None:
    """
    Solves scheduling problem "P || Cmax" as a CP with OR-Tools CP-SAT.
        
    Args
    ----
    processing_times : list[int]
        List of processing times.
    weights : list[int]
        List of weights.
    release_times : list[int]
        List of release times.
    nmachines : int
        Number of machines.
    """

    # INIT
    n = len(processing_times)
    UB = max(release_times) + sum(processing_times) # upper bound on the makespan (could be more clever)
    
    JOBS = range(n)
    
    # BUILD MODEL
    model = cp_model.CpModel()

    flags = [ [model.new_bool_var(f"on_{i}_{j}") for j in range(nmachines)] for i in range(n) ]
    
    for i in range(n):
        model.add(sum(flags[i]) == 1)
    
    jobs = [ model.new_optional_fixed_size_interval_var(
        start= model.new_int_var( release_times[i], UB, f'start_{i}_{j}' ),
        size=  processing_times[i],
        is_present= flags[i][j],
        name=  f'job_{i}_{j}'
    ) for i in range(n) for j in range(nmachines) ]

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


if __name__ == '__main__':
    from scheduling_instances import random_single_machine_instance
    
    # random instances
    p, w, d, r = random_single_machine_instance( 16 )
    #p, w, d, r = random_single_machine_instance( 17 ) # struggling (check log, set time limit)

    # solve problem
    schedule_jobs_on_a_single_machine( p, w, r )
    schedule_jobs_on_identical_machines( p, w, r, 2 )

    