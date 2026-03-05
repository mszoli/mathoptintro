from ortools.math_opt.python import mathopt

import networkx as nx

def _draw_masyu():
    pass

def solve_masyu( task:str, draw_task:bool= False, draw_solution:bool= False ) -> None:
    """
    Solves the given Masyu instance as an MIP with **OR-Tools MathOpt**.

    Args
    ----
    task : str
        A Masyu instance encoded as a string.
    draw_task : bool
        Should we draw the task?
    draw_solution : bool
        Should we draw the solution?
    """
    raise NotImplementedError( 'function is not implemented' )

if __name__ == '__main__':
    TASKS = [
        'BWcBcBkBWaWcWbWbBa',
        'dWBWaWbWcBcWaWWaWWgBb',
        'fWaWWaWfWWbWWcWaBeWbWaBcBbWaWWaWaWWaWbBc',
        'bWjWcWdWWbWcBaBaWkBcWgWaBc',
        'jBiBaBcBdBcWbWaWaWWfWiWaBa',
        'eBaWWbWeWBaBbWWeWcWaWbWaWWbWaBeWiBWaWWaWaWBcWaWaWaWaWaBeWeWa',
        'BeWbBbWaWkWbBbWbBaWcWjWWaWaBhBaWaWaWgWaWaWbBhBaWa',
        'jWWfBcWBWtWBaBaWbWcWcWbBbBbWdWbWcWdWeBf',
        'BWgWbWWaWBWbWBBfWcWBbWbWBWWWWWbWaWbWaWfWBWcWbWaBdWWaBbWaWbBbBbWaBdWgBdWcBWBbWWaBWWfWaBWWbWeWcWaBeBWaBbWdBWBaWcWaBWcWaWaWjWaBWWaWBcWbBeWB',
        'aWeWbWWkWaBbWaBaWaWbBWgBbWgWgBcWoWWWWbWWWdWbWiWaWaWbWeBWdWaWdWbBBaBbWbWaBhWqBgBcWaWjBhBBcBdWb',
        'gBbWeBcWdBgBaWaWeBfWfBkBdWaBnBdBaBWdBeBBgBkBcWWaBcBiBbWdBbWeWbBfWcWbWfWbWgWWfWWhWaB',
        'aWfWWbWhWWcWaWBcWaWWaWWBaWbWWbWaWaBbBaBWaBaWBbWWBcWaBBbBiWWdWaBWBWaWbBWWdWWeWdWWBcWWWBcBcWBWbWWbBdWbWBeWpBcWWaWbWWBBWcBaWeBaBbBaWbBdWiWWbWaBBaWbWWbWaWcBaWdWaWaWaWWaBWdBdWWBaBeWWdWeWaBcWaWaBWeBgBaWdBaBbWbBfWbWaWfWbWbWWbWeWBWbWgWbWcB',
        'bWcWeWbWkBcWeWWbWhWcWaBdWaBbBWbBfBaWbBbBcWWbWaWaWcWfWdBjBbBcWcBbBaWbWeBcBaBeWaBbBeWaBcBgBbWaWfBbWWWaWtWaWWeBbWaWbBcWbBbBBdWaWbWdWaBiWeWWfBdWbBWWBWWcWeWgWcBaWbWaWdWaWaWaWeWbWbWbWcWcWaWbBbWeWeWh',
        'BdBbWeBhWeWWfWWaWbBbWeWbWcBcWaWWaBcBaWcBbWmWdWbBeBaWaBiWWfWjBBbWaWcBdBWfWbBWcWBbBfWeBgWbWaWdBdWbWdWaBaWiWcWWdWcBeWaWcWdWaWbWWcWWiWlBaBaWWcBaBbWcBdBcWBdWWbWfWdBeBbWaBbWcWbBeWhWgBeB',
        'bWbBfWcBcWbWcBWBWcWWaBWaWWBaWBjBaWeWbWcBWbBaBdWcWWbWcWaWeBbWWBWdWbBbWWfWWbWcWWaWWdBWaBWbWhBeBeWdWWBaBfBdWaWWaWaWfBdBaBbWaWbWcWaWdWlWkBBhBbBbWaWaWBWbWWaBWaBaBWaWBbWWaWWhWaWWcWBWWcWbWWBWBWaWWaWBcBWaBeWbBaWbWhWbWdWcBWaBcWaWdWWaWjWcWWBaWcWcBWWBaWBWaWgBbWaWBWbBcBcBaWbWWBeWBWbWcBWWaBWcBWaBaWiBcWbWeWBbWBfWWcWbWaBWaBWeBWaBWcWWcBaWbWBcBWcWWbWWdWeWbWaBjWWbWaWdWb',
        'dBaWbWbWbWeWeBhWaWbWcWiBcWdWaBcBbWcBcWWcWBcWBaBaWdWaWaWcWcBbWfBbWdBaWaWaWdWWaBgBdWcWdWeBaBhWbBaBbBWWeBaBbBaBaWjBaWeWgWaWWBcWaBfWbWaBaBcWdWWcWeWeWbBWWhWBaWdWkBhBdWbBaBbWWcWcWdWWhWgBWdWWWbWWiBeBeWWbWaWWbWeBdWgWeWbWgWWaWaBcWWdWaWbBaWfWWaWWaBbWWbWaWfWfWmBdWaWBdWaBcWWcBbWdWeBeWbBjBaWbWaWdWbBcWBaBjBaWe',
        'eBhWaBdWcBmWiWbWfWWWgBaBWaWaWbBbBfWcWhWeBWeWBWWaWdBkBaWfBaBgBWcWaBbWbBcWbWaWWBcBbWbBoBWWcBaBdBBdBhWeWbBWcBbBaBaWbWbBdWeWiWeBcWbWaWWbWbWbWWfWfWeBfBaBcWWeWbWaWbWaWaBaWgBhBWaWfBaWcWbWbWaWWeWaWWbBaWbBhWbBWeWbWWcBWWeWbWaWaWaBbWgWBaWaWWWfWcWbWbWkWhWaBcBbBWWfWWbWkWWbBaBbBWWcWaWdBgWWeWcWbBBfWfBdWe',
    ]

    task = TASKS[0]
    
    solution = solve_masyu( task, draw_task= False, draw_solution= True )
    
    print( f'task     = \'{task}\'')
    print( f'solution = \'{solution}\'' )
