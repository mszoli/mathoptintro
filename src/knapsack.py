from ortools.math_opt.python import mathopt

def solve_knapsack_mip( profits:list[float], weights:list[float], capacity:float, binary:bool= False ) -> tuple[float,list[int]]:
    """
    Solves the given instance for the **Binary/Integer Knapsack Problem** as a MIP with **OR-Tools MathOpt**.

    Args
    ----
    profits: list[float]
        Profits: profits[i] is the profit of item i.
    weights: list[float]
        Weights: weights[i] is the weight of item i.
    capacity: float
        Capacity of the knapsack.
    binary: bool
        Indicates whether each item can be selected only once.

    Returns
    -------
    : float
        Objective value.
    : list[int]
        List of multiplicities of items in the knapsack.
    """
    assert len(profits) == len(weights), 'the lists are of different lengths!'

    # INIT
    ITEMS = range( len(profits) )

    # BUILD MODEL
    model = mathopt.Model( name= 'knapsack' )

    # variables: x[i] is the multiplicity of item i in the knapsack    
    x = [ model.add_binary_variable( name = f'x{i}') if binary else model.add_integer_variable( lb= 0, name = f'x{i}' ) for i in ITEMS ]

    # constraint: total weight of selected items must respect the capacity limit
    # NOTE: equivalent method: model.add_constr( xsum( weights[i] * x[i] for i in ITEMS ) <= capacity, 'capacity' )
    model.add_linear_constraint( sum( weights[i] * x[i] for i in ITEMS ) <= capacity, name= 'capacity' )

    # objective: maximize the profit
    model.maximize( sum( profits[i] * x[i] for i in ITEMS ) )

    # SOLVE PROBLEM
    result = mathopt.solve( model, solver_type= mathopt.SolverType.HIGHS )

    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL, f'could not solve problem to optimality (status= {model.status})'

    # return the objective value and the solution (i.e., the multiplicity of the items)
    return result.objective_value(), [ int(round(result.variable_values(x[i]))) for i in ITEMS ]

if __name__ == '__main__':
    from packing_instances import random_knapsack_instance

    profits, weights, capacity = random_knapsack_instance( 20 )
    value, solution = solve_knapsack_mip( profits, weights, capacity, True )

    print( f'objective: {value}' )
    print( f'solution : {solution}' )
