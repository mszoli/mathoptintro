import datetime

from ortools.math_opt.python import mathopt

import itertools as it

def _log( model:mathopt.Model, result:mathopt.SolveResult, *, ncuts:int= 0 ) -> None:
    """
    Prints log.

    Args
    ----
    model: mathopt.Model
        Model.
    result: mathopt.SolveResult
        Solve result.
    ncuts: int
        Number of separated parallel inequalities, if any.
    """
    feasible = result.termination.reason in [mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE]
    
    buffer = [
        f'{model.name:10s}',
        f'{result.termination.reason.name[:10]:10s}',
        f'{result.objective_value():7.1f}' if feasible else '    inf',
        f'{result.best_objective_bound():7.1f}',
        f'{(result.objective_value()-result.best_objective_bound())/result.best_objective_bound():.4f}' if feasible else '   inf',
        f'{ncuts:4d}',
        f'{result.solve_stats.solve_time.total_seconds():7.4f}',
    ]
    print( ' │ '.join(buffer) )

class SchedulingCutSeparator:
    """
    Callable class to seperate the parallel inequalities.
    """
    def __init__( self, processing_times:list[int], C:list[mathopt.Variable] ):
        self.p:list[int] = processing_times
        self.C:list[mathopt.Variable] = C

        self.JOBS = range(len(self.p))
        self.ncuts:int = 0
        self.MINIMUM_VIOLATION:float = 0.1

    def __call__( self, callback_data:mathopt.CallbackData ) -> mathopt.CallbackResult:
        result = mathopt.CallbackResult()
        
        # separation procedure to find the most violated cut, if any
        best_set   = None
        best_value = 0
        curr_set   = []
        curr_value = 0
        delta      = 0

        c_values = [ callback_data.solution[var] for var in self.C ]

        for j in sorted( self.JOBS, key= lambda i : c_values[i] ):
            curr_set.append(j)
            delta += self.p[j]
            curr_value += self.p[j]*(delta-c_values[j])

            if best_value + self.MINIMUM_VIOLATION < curr_value:
                best_value = curr_value
                best_set   = curr_set[:] # copy!

        if not best_set:
            return result        

        # add violated cut to the model
        self.ncuts += 1
        
        result.add_user_cut( 0.5 * ( sum( self.p[j]**2 for j in best_set ) + sum( self.p[j] for j in best_set )**2 ) <= sum( self.p[j]*self.C[j] for j in best_set ) )

        return result

def schedule_jobs_on_a_single_machine( processing_times:list[int], weights:list[int], release_times:list[int], separation:bool= False, solver_type:mathopt.SolverType= mathopt.SolverType.GSCIP, params:mathopt.SolveParameters= None ) -> None:
    """
    Solves scheduling problem "1 | r_j | sum w_jC_j" (or "1 || sum w_jC_j") as an MIP with OR-Tools MathOpt.

    NOTE: The problem "1 || sum w_jC_j" can be solved in polynomial time (jobs should be scheduled in order of non-increasing w/p ratios).
          This is just a proof-of-concept for branch-and-cut.
    
    Args
    ----
    processing_times: list[int]
        List of processing times.
    weights: list[int]
        List of weights.
    release_times: list[int]
        Optional list of release times.
    separation: bool
        Should we separate the parallel inequalities?
    solver_type: mathopt.SolverType
        The underlying solver to use (e.g., GSCIP, GUROBI).
        NOTE that HIGHS does not support branch-and-cut.
    params: mathopt.SolveParameters
        Configuration of the underlying solver.
    """
    # INIT
    n = len(processing_times)
    M = sum(processing_times) + max( release_times ) if release_times else sum(processing_times)
    
    JOBS = range(n)
    
    # BUILD MODEL
    model = mathopt.Model( name= f'BIGM{"-SEP" if separation else ""}' )

    # completion time variables: p[j] <= C[j] <= M
    C = [ model.add_variable( lb= processing_times[j] + release_times[j] if release_times else processing_times[j], ub= M, name= f'C_{j}' ) for j in JOBS ]

    # objective: weighted sum of completion times
    model.minimize( sum( weights[j]*C[j] for j in JOBS ) )

    # precedence variables: y[i][j] = 1 <=> job i precedes job j (NOTE: i<j)
    y = [ [ model.add_binary_variable( name= f'y_{i}_{j}' ) if i < j else None for j in JOBS ] for i in JOBS ]

    # no-overlap constraints: y[i][j] = 1 => C[i] <= C[j] - p[j] and y[i][j] = 0 => C[j] <= C[i] - p[i]
    for (i,j) in it.combinations(JOBS,2):
        model.add_linear_constraint( C[i] <= C[j] - processing_times[j] + M*(1-y[i][j]) )
        model.add_linear_constraint( C[j] <= C[i] - processing_times[i] + M*y[i][j] )
    
    callback_reg = mathopt.CallbackRegistration( events={mathopt.Event.MIP_NODE}, add_cuts= True ) if separation else None # TODO: MIP_NODE: GUROBI only ?
    cb = SchedulingCutSeparator( processing_times, C ) if separation else None

    result = mathopt.solve(
        model,
        solver_type= solver_type,
        params= params,
        callback_reg= callback_reg,
        cb= cb
    )

    _log( model, result, ncuts= cb.ncuts if separation else 0 )

if __name__ == '__main__':
    from scheduling_instances import random_single_machine_instance

    solver_type = mathopt.SolverType.GSCIP
    params = mathopt.SolveParameters( time_limit= datetime.timedelta(seconds= 10) )

    proc_times, weights, due_dates, release_times = random_single_machine_instance( 17 )
    release_times = None

    print( '───────────┬────────────┬─────────┬─────────┬────────┬──────┬────────' )
    print( 'model      │ status     │  objval │   bound │    gap │ cuts │   time ' )
    print( '───────────┼────────────┼─────────┼─────────┼────────┼──────┼────────' )

    schedule_jobs_on_a_single_machine( proc_times, weights, release_times, separation= False, solver_type= solver_type, params= params )
    schedule_jobs_on_a_single_machine( proc_times, weights, release_times, separation= True, solver_type= solver_type, params= params )

    print( '───────────┴────────────┴─────────┴─────────┴────────┴──────┴────────' )