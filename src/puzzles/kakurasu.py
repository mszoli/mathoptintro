from ortools.sat.python import cp_model

def _decode_kakurasu_string( task:str ) -> tuple[list[int],list[int]]:
    """
    Decodes the given Kakurasu instance.

    Args
    ----
    task : str
        A Kakurasu instance encoded as a string
        that consist of the target values for columns (from left to right) and for rows (from top to bottom) separated by slashes '/'.

    Returns
    -------
    : list[str]
        List of the target values for columns (left to right).
    : list[str]
        List of the target values for rows (top to bottom).
    """
    numbers = list( map( int, task.split('/') ) )
    n = len( numbers ) // 2

    return numbers[:n], numbers[n:]

def _encode_kakurasu_grid( grid:list[list[int]] ) -> str:
    """
    Encodes the given Kakurasu solution as a string.

    Args
    ----
    grid : list[list[int]]
        The solution grid as a list of row-lists, with 0/1 values (1: marked, 0: unmarked).

    Returns
    -------
    : str
        The solution encoded as a string.
    """    
    return ''.join( ''.join( map( str, row ) ) for row in grid )

def _print_kakurasu( colnums:list[int], rownums:list[int], grid:list[list[int]]= None ) -> None:
    """
    Prints the given instance (and solution) of Kakurasu.
    
    Args
    ----
    colnums : list[int]
        List of target values for columns.
    rownums : list[int]
        List of target values for rows.
    grid : list[list[int]]
        The solution grid as a list of row-lists, with 0/1 values.
    """
    n = len( rownums )

    CHARS = ' ×' # empty|filled

    headers = []
    if n < 10:
        headers.append( list( range(1,n+1) ) )
    else:
        headers.append( list( map( lambda num : str(num // 10) if 10 <= num else ' ', range(1,n+1) ) ) )
        headers.append( list( map( lambda num : str(num % 10), range(1,n+1) ) ) )

    footers = []
    if max( colnums ) < 10:
        footers.append( colnums )
    else:
        footers.append( list( map( lambda num : str(num // 10) if 10 <= num else ' ', colnums ) ) )
        footers.append( list( map( lambda num : str(num % 10), colnums ) ) )
    
    for header in headers:
        print( '    ', ' '.join( map( str, header ) ) )
        
    print( f'   ┌{"─"*(2*n+1)}┐' )

    for i in range(n):
        print( f'{i+1:2d} │ {" ".join( CHARS[1] if grid != None and grid[i][j] == 1 else CHARS[0] for j in range(n))} │ {rownums[i]}' )

    print( f'   └{"─"*(2*n+1)}┘' )

    for footer in footers:
        print( '    ', ' '.join( map( str, footer ) ) )

def _solve_kakurasu( colnums:list[int], rownums:list[int] ) -> list[list[int]]:
    """
    Solves Kakurasu.

    Args
    ----
    colnums : list[int]
        List of target values for columns.
    rownums : list[int]
        List of target values for rows.

    Returns
    -------
    grid : list[list[int]]
        The solution grid as a list of row-lists, with 0/1 values.
    """
    model = cp_model.CpModel()
    vars = [ [ model.new_int_var( 0, 1, f'x_{i}_{j}' ) for j in range(len(colnums)) ] for i in range(len(rownums)) ]
    
    for i in range(len(rownums)):
        model.add( sum( vars[i][j]*(j+1) for j in range(len(colnums)) ) == rownums[i] )
    for j in range(len(colnums)):
        model.add( sum( vars[i][j]*(i+1) for i in range(len(rownums)) ) == colnums[j] )
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status.name == 'INFEASIBLE':
        raise ValueError( 'INFEASIBLE...' )

    return [ [ solver.value( vars[i][j] ) for j in range(len(colnums)) ] for i in range(len(rownums)) ]

def solve_kakurasu( task:str, print_task:bool= False, print_solution:bool= False ) -> str:
    """
    Solves the given Kakurasu instance.

    Args
    ----
    task : str
        A Kakurasu instance encoded as a string
        that consist of the target values for columns (from left to right) and for rows (from top to bottom) separated by slashes '/'.
    print_task : bool
        Should we print the task?
    print_solution : bool, optional
        Should we print the solution?

    Returns
    -------
    solution : str
        The solution encoded as a string.
    """
    # decode (and print) task
    colnums, rownums = _decode_kakurasu_string( task )
    if print_task:
        _print_kakurasu( colnums, rownums )

    # solve problem (and print solution)
    solution = _solve_kakurasu( colnums, rownums )
    if print_solution:
        _print_kakurasu( colnums, rownums, solution )

    return _encode_kakurasu_grid( solution )

if __name__ == '__main__':
    TASKS = [
        '5/3/4/7/5/4/2/8',
        '10/1/1/3/10/5/1/1',
        '4/5/3/7/8/4/6/10/5/5',
        '9/2/9/2/13/5/7/6/9/8',
        '4/11/1/11/5/10/10/6/11/2/7/10',
        '16/13/4/6/18/13/13/11/5/8/16/14',
        '9/7/10/3/8/7/11/7/8/21/2/5/14/3',
        '20/13/12/4/23/12/16/21/11/24/15/13/11/13',
        '3/9/3/15/2/18/7/20/4/28/4/6/21/12/16/4',
        '31/18/30/19/28/22/7/13/11/21/15/9/16/18/32/14',
        '18/22/13/4/3/12/4/11/1/16/1/13/10/18/10/8/1/2',
        '19/2/17/14/10/27/20/21/12/19/38/1/31/5/26/30/8/9',
    ]

    task = TASKS[0]
    
    solution = solve_kakurasu( task, print_task= True, print_solution= True )
    
    print( f'task     = \'{task}\'')
    print( f'solution = \'{solution}\'' )
    