from ortools.sat.python import cp_model

class QueensSolutionCallback( cp_model.CpSolverSolutionCallback ):
    """
    Solution printer for n-queens.

    Attributes
    ----------
    x : list[IntVar]
        List of variables: x[i] = j if and only if the queen of row i is in column j.
    nsols : int
        Number of found solutions.
    """
    def __init__( self, x ):
        super().__init__()

        self.x = x
        self.nsols = 0

    @property
    def number_of_solutions( self ):
        return self.nsols

    def on_solution_callback( self ):
        """
        Draws solution (called by the solver for each feasible solution found).
        """
        CHARS = '·×' # empty | queen

        self.nsols += 1
        
        print( f'solution #{self.nsols}:' )
        for i in range(len(self.x)):
            print( ' '.join( [ CHARS[1] if self.Value(self.x[i]) == j else CHARS[0] for j in range(len(self.x)) ] ) ) 
        print( '' )

def solve_queens_cp( n:int, enumerate_all_solutions:bool= False ) -> None:
    """
    Solves the n-queens puzzle as a CP with Google OR-Tools CP-SAT.

    Args
    ----
    n : int
        The size of the board (and the number of queens).
    enumerate_all_solutions: bool
        Should we enumerate all solutions? (default: `False`)
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
    solver.parameters.enumerate_all_solutions = enumerate_all_solutions
    cb = QueensSolutionCallback(x)
    status = solver.Solve( model, solution_callback= cb )

    print( f'status: {solver.status_name(status)} | total time: {solver.WallTime():.2f} | number of solutions: {cb.number_of_solutions}' )

def solve_queens_mip( n:int, enumerate_all_solutions:bool= False ) -> None:
    """
    Solves the n-queens puzzle as a MIP with Google OR-Tools MathOpt.

    Args
    ----
    n : int
        The size of the board (and the number of queens).
    enumerate_all_solutions: bool
        Should we enumerate all solutions? (default: `False`)
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
    CHARS = '·×' # empty | queen

    if not enumerate_all_solutions:
        result = mathopt.solve( model, mathopt.SolverType.HIGHS )
        
        print( f'status: {result.termination.reason.name} | total time: {result.solve_stats.solve_time.total_seconds():.2f}' )

        if result.termination.reason in [mathopt.TerminationReason.FEASIBLE,mathopt.TerminationReason.OPTIMAL]:
            for i in range(n):
                print( ' '.join( [ CHARS[1] if 0.5 < result.variable_values(x[i][j]) else CHARS[0] for j in range(n) ] ) ) 
            print( '' )    

    else:
        for iter in range(1,1000):
            result = mathopt.solve( model, mathopt.SolverType.HIGHS )

            if result.termination.reason not in [mathopt.TerminationReason.FEASIBLE,mathopt.TerminationReason.OPTIMAL]:
                break

            print( f'solution #{iter}:' )
            for i in range(n):
                print( ' '.join( [ CHARS[1] if 0.5 < result.variable_values(x[i][j]) else CHARS[0] for j in range(n) ] ) ) 
            print( '' )    

            # exclude current solution
            model.add_linear_constraint( sum( x[i][j] for i in range(n) for j in range(n) if 0.5 < result.variable_values(x[i][j]) ) <= n-1 )

if __name__ == '__main__':
    solve_queens_cp( 5 )
    # solve_queens_mip( 5 )
