from ortools.math_opt.python import mathopt

# EXERCISES:
# 1. Terminate the column generation procedure if the improvement in the last x iterations is under a tolerance. 
# 2. Use the packing obtained with the first-fit-decreasing procedure as in initial packing for column generation.
# 3. Implement the natural MIP formulation for the problem.

def first_fit_decreasing( capacity:int, items:list[int] ) -> list[list[int]]:
    """
    Solves the given instance for the Bin Packing Problem with the First Fit Decreasing heuristic.
    
    Args
    ----
    capacity: int
        Uniform bin capacity.
    items: list[int]
        List of items (item sizes).

    Returns
    -------
    bins: list[list[int]]
        List of bins, where each bin is a list of items.
    """
    bins:list[list[int]] = []

    for item in sorted( items, reverse= True ):
        assert item <= capacity, f'First Fit Decreasing: item size {item} exceeds the uniform bin capacity {capacity}!'

        for bin in bins:
            if sum( bin ) + item <= capacity:
                bin.append( item )
                break
        else: # no bin found
            bins.append( [ item ] )

    return bins

def column_generation_binpacking( capacity:int, items:list[int], initial_packings:list[list[int]]= None, solver_type:mathopt.SolverType= mathopt.SolverType.HIGHS ) -> list[list[int]]:
    """
    Solves the given instance for the **Bin Packing Problem** with **column generation**
    with **OR-Tools MathOpt**.

    Args
    ----
    capacity: int
        Uniform bin capacity.
    items: list[int]
        List of items (item sizes).
    initial_packings: list[list[int]]
        Initial packings (columns) to start with. Optional.
    solver_type: mathopt.SolverType
        The underlying solver to use (HIGHS, Gurobi).

    Returns
    -------
    bins: list[list[int]]
        List of bins, where each bin is a list of items.
    """
    from knapsack import solve_knapsack_mip
    
    # INIT
    n = len(items)
    N = range(n)

    # initial columns
    initial_columns = [ [ int(i==j) for j in N ] for i in N ] if not initial_packings else initial_packings

    # BUILD MODEL
    model = mathopt.Model( name= 'binpacking')

    # initial variables
    # NOTE: use integers instead of binaries to avoid problems with handling upper bounds
    x = [ model.add_variable( lb= 0, name= f'x{j}' ) for j in range(len(initial_columns)) ]

    # initial constraints
    conss = [ model.add_linear_constraint( 1 <= sum( x[j] * column[i] for j, column in enumerate(initial_columns) ), name= f'cover{i}' ) for i in N ]

    # objective
    model.minimize( sum( x ) )

    # COLUMN GENERATION
    # solve LP iteratively
    iter = 0
    while True:
        iter += 1

        # solve the LP-relaxation of the problem
        lp_result = mathopt.solve( model, solver_type= solver_type )

        # get dual values
        master_objval = lp_result.objective_value()
        dual_values = [ lp_result.dual_values(conss[i]) for i in N ]

        # solve subproblem (pricing problem)
        sub_objval, column = solve_knapsack_mip( dual_values, items, capacity, binary= True )

        # add new pattern to the problem, if any
        if sub_objval <= 1 + 1e-6:
            break

        x_new = model.add_variable( lb= 0, name= f'x{len(x)}' )
        for j in N:
            conss[j].set_coefficient( x_new, column[j] )
        model.objective.add_linear( x_new )
        x.append( x_new )

        # update progress bar
        print( f'[Column Generation] Iteration: {iter:3d} | Objective value: {master_objval:8.4f} | Reduced cost: {sub_objval:.4f}' )
    
    # retrieve integer solution
    for var in x:
        var.integer = True
        
    mip_result = mathopt.solve( model, solver_type= solver_type )

    return [ [ conss[i].get_coefficient( var ) for i in N ] for var in x if 0.5 < mip_result.variable_values( var ) ]

if __name__ == '__main__':
    from packing_instances import random_binpacking_instance_triplets

    items, capacity = random_binpacking_instance_triplets( t= 20 ) # NOTE: the optimal number of bins equals to t

    ffd_bins = first_fit_decreasing( capacity, items )
    print( f'[First Fit Decreasing] Number of bins used: {len(ffd_bins)}' )

    # mip_bins = column_generation_binpacking( capacity, items, solver_type= mathopt.SolverType.HIGHS )
    # print( f'[Column Generation] Number of bins used: {len(mip_bins)}' )
