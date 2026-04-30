from ortools.math_opt.python import mathopt
import math
import networkx as nx
import matplotlib.pyplot as plt

DXY_VECTOR = [(-1, 0), (0, 1), (1, 0), (0, -1)] # just to help with directions
DRAWING_MAP = {
    'W': '○',
    'B': '●',
    '.': '·',
}
COLORS_MAP = {
    'W': 'white',
    'B': 'black',
    '.': 'gray',
}

def _decode_masyu_task(task: str) -> tuple[int, list, dict]:
    """
    gives us:
    n (length of the grid)
    cell coordinates (just a 2d list of (0, 0), (0, 1), ...)
    circles (dict of coordinates -> circle color)
    """
    cell_list = []
    for c in task:
        if c in ['W', 'B']:
            cell_list.append(c)
        else:
            cell_list += ['.']*(ord(c)-ord('a')+1)
    n = math.isqrt(len(cell_list))
    assert n*n == len(cell_list), 'wait whaaaat i thought the board had a square shape'
    cells = [(i//n, i%n) for i, _ in enumerate(cell_list)]
    circles = {(i//n, i%n): v for i, v in enumerate(cell_list) if v in ['W', 'B']}
    return n, cells, circles

def _draw_masyu(n: int, circles: dict, used_edges: list = None) -> None:

    used_edge_set = set(used_edges) if used_edges is not None else set()

    for i in range(n):
        line = ''
        for j in range(n):
            cell = (i, j)
            line += DRAWING_MAP[circles.get(cell, '.')]
            if j + 1 < n:
                line += '-' if ((cell, (i, j+1)) in used_edge_set or ((i, j+1), cell) in used_edge_set) else ' '
        print(line)
        if i + 1 < n:
            line = ''
            for j in range(n):
                cell = (i, j)
                line += '|' if ((cell, (i+1, j)) in used_edge_set or ((i+1, j), cell) in used_edge_set) else ' '
                if j + 1 < n:
                    line += ' '
            print(line)

def _draw_masyu_nx(n: int, circles: dict, used_edges: list = None) -> None:
    G = nx.grid_2d_graph(n, n)
    if used_edges is not None:
        G.add_edges_from(used_edges)
    # so that we adjust to the nx coordinate system...
    pos = {(i, j): (j, -i) for i in range(n) for j in range(n)}
    node_colors = [COLORS_MAP[circles.get((i, j), '.')] for i in range(n) for j in range(n)]
    edge_colors = []
    edge_widths = []
    for a, b in G.edges():
        if used_edges is not None and ((a, b) in used_edges or (b, a) in used_edges):
            edge_colors.append('red')
            edge_widths.append(5)
        else:
            edge_colors.append('gray')
            edge_widths.append(1)
    fig, ax = plt.subplots(figsize=(10, 10))
    node_size = 500 if n <= 10 else 100
    nx.draw(G, pos=pos, ax=ax, with_labels=False, node_color=node_colors, edge_color=edge_colors, width=edge_widths, node_size=node_size)
    fig.set_facecolor('lightgreen')
    ax.set_facecolor('lightgreen')
    plt.show()


def _edge_var(n: int, x: dict, a: tuple[int, int], b: tuple[int, int]) -> mathopt.Variable | None:
    if a[0]<0 or a[0]>=n or a[1]<0 or a[1]>=n:
        return None
    if b[0]<0 or b[0]>=n or b[1]<0 or b[1]>=n:
        return None
    if b < a:
        a, b = b, a
    return x[(a, b)]

def _edge_var_or_zero(e: mathopt.Variable | None) -> mathopt.LinearExpression:
    # just helps to write the constraints cleanly without checking for 'None's later
    return e if e is not None else 0

def _add_cell_and_edge_variables(model: mathopt.Model, cells: list, edges: list) -> tuple[dict, dict]:
    x = {(a, b): model.add_binary_variable(name=f'x_{a}_{b}') for a, b in edges}
    y = {cell: model.add_binary_variable(name=f'y_{cell}') for cell in cells}
    return x, y

def _add_degree_rules(model: mathopt.Model, x: dict, y: dict, incident_edges: dict) -> None:
    for cell, var in y.items():
        model.add_linear_constraint(sum(x[edge] for edge in incident_edges[cell]) == 2*var)

def _add_visit_circle_rules(model: mathopt.Model, y: dict, circles: dict) -> None:
    for circle in circles:
        model.add_linear_constraint(y[circle] == 1)

def _add_black_circle_rules(model: mathopt.Model, x: dict, n: int, circles: dict, incident_edges: dict) -> None:
    for circle, color in circles.items():
        if color != 'B':
            continue
        horizontal_edges = [edge for edge in incident_edges[circle] if edge[0][0] == edge[1][0]]
        # sum of horizontal incident edges used must be 1 (because the sum of incident edges used is 2, and we must turn)
        model.add_linear_constraint(sum(x[edge] for edge in horizontal_edges) == 1)

        # also, we must go straight for 1 more step before and after the circle:
        for dx, dy in DXY_VECTOR:
            touching_edge = _edge_var(n, x, (circle[0]+dx, circle[1]+dy), circle)
            if touching_edge is None:
                continue
            other_edge = _edge_var(n, x, (circle[0]+dx, circle[1]+dy), (circle[0]+2*dx, circle[1]+2*dy))
            model.add_linear_constraint(_edge_var_or_zero(other_edge) >= _edge_var_or_zero(touching_edge))

def _add_white_circle_rules(model: mathopt.Model, x: dict, n: int, circles: dict, incident_edges: dict) -> None:
    for circle, color in circles.items():
        if color != 'W':
            continue
        # add a helper variable (0: we go through the circle vertically, 1: we go through horizontally)
        z = model.add_binary_variable(name=f'z_{circle}')
        # so now the sum of horizontal edges used must be 2*z
        horizontal_edges = [edge for edge in incident_edges[circle] if edge[0][0] == edge[1][0]]
        model.add_linear_constraint(sum(x[edge] for edge in horizontal_edges) == 2*z)
        
        # now we consider the edges 1 step further in both horizontal and vertical directions
        horizontal_further_edge_vars = []
        vertical_further_edge_vars = []
        for dx, dy in DXY_VECTOR:
            e = _edge_var_or_zero(_edge_var(n, x, (circle[0]+dx, circle[1]+dy), (circle[0]+2*dx, circle[1]+2*dy)))
            if dx == 0:
                horizontal_further_edge_vars.append(e)
            else:
                vertical_further_edge_vars.append(e)

        # in case of z=0, we should have sum(vertical)<=1
        # and in case of z=1, we should have sum(horizontal<=1)
        # we can write these in a combined way (easy to check that these constraints together work for both cases):
        model.add_linear_constraint(sum(horizontal_further_edge_vars) <= 2-z)
        model.add_linear_constraint(sum(vertical_further_edge_vars) <= 1+z)

def _find_solution_components(result: mathopt.SolveResult, x: dict, y: dict, cells: list, edges: list):
    used_cells = [cell for cell in cells if result.variable_values(y[cell]) > 0.5]
    used_edges = [edge for edge in edges if result.variable_values(x[edge]) > 0.5]
    G = nx.Graph()
    G.add_nodes_from(used_cells)
    G.add_edges_from(used_edges) 
    components = list(nx.connected_components(G))
    return components

def _add_DFJ_cuts(model: mathopt.Model, x: dict, edges: list, circles: dict, components: list) -> None:
    for component in components:
        # check that actually this component covers all circles:
        covers_all_circles = True
        for c in circles:
            if c not in component:
                covers_all_circles = False

        if not covers_all_circles:
            component_edges = [edge for edge in edges if edge[0] in component and edge[1] in component]
            model.add_linear_constraint(sum(x[edge] for edge in component_edges) <= len(component)-1)

def solve_masyu(task:str, draw_task:bool= False, draw_solution:bool= False) -> None:
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

    n, cells, circles = _decode_masyu_task(task)

    if draw_task:
        print('task:')
        _draw_masyu_nx(n, circles)

    edges = []
    incident_edges = {cell: [] for cell in cells}
    for (i, j) in cells:
        if i + 1 < n:
            edges.append(((i, j), (i+1, j)))
            incident_edges[(i, j)].append(((i, j), (i+1, j)))
            incident_edges[(i+1, j)].append(((i, j), (i+1, j)))
        if j + 1 < n:
            edges.append(((i, j), (i, j+1)))
            incident_edges[(i, j)].append(((i, j), (i, j+1)))
            incident_edges[(i, j+1)].append(((i, j), (i, j+1)))

    model = mathopt.Model(name='masyu')
    
    # x: edges is used (0/1), y: cell is visited (0/1)
    x, y = _add_cell_and_edge_variables(model, cells, edges)

    _add_degree_rules(model, x, y, incident_edges)
    _add_visit_circle_rules(model, y, circles)
    _add_black_circle_rules(model, x, n, circles, incident_edges)
    _add_white_circle_rules(model, x, n, circles, incident_edges)

    num_DFJ_cuts = 0
    while True:
        result = mathopt.solve(model, solver_type=mathopt.SolverType.HIGHS)
        assert result.termination.reason == mathopt.TerminationReason.OPTIMAL, f"interesting...solver somehow failed? : {result.termination.reason}"
        components = _find_solution_components(result, x, y, cells, edges)
        if len(components) == 1:
            # letsgooo done!!!
            break
        _add_DFJ_cuts(model, x, edges, circles, components)
        num_DFJ_cuts += len(components)

    used_edges = [edge for edge in edges if result.variable_values(x[edge]) > 0.5]
    if draw_solution:
        _draw_masyu_nx(n, circles, used_edges)

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


    for task in TASKS:
        print(f'task: {task}')
        solve_masyu(task, draw_task=False, draw_solution=True)
        print('\n\n')
