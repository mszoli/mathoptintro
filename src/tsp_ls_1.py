import networkx as nx
import random
import itertools as it
import matplotlib.pyplot as plt
import matplotlib.animation as animation

VERBOSITY_LEVEL = 1 # 0: off, 1: relevant, 2: detailed

from tsp_instances import random_euclidean_graph, tetrahedron_instance

# EXERCISES
# 1. Implement function _improve_by_node_swaps to improve the solution by swapping two nodes.
# 2. Implement function _improve_by_2_opt to improve the solution by 2-opt.
# 3. Use operators node relocation, node swap, and 2-opt in a variable neighborhood search (VNS) procedure.

def _edgelist( nodes:list[int] ) -> list[tuple[int,int]]:
    """
    Returns the edges of the tour given as a sequence of nodes.

    Args
    ----
    nodes: list[int]
        A Hamiltonian tour as a permutation of the nodes.

    Returns
    -------
    : list[tuple[int,int]]
        A Hamiltonian tour as a sequence of edges.
    """
    return [ (nodes[i-1],nodes[i]) for i in range(1,len(nodes)) ] + [ (nodes[-1],nodes[0]) ]

def _evaluate_solution( graph:nx.DiGraph, solution:list[int] ) -> float:
    """
    Returns the cost of the given solution.
    
    Args
    ----
    graph: nx.DiGraph
        A networkx digraph (with 'cost' edge attribute).
    solution: list[int]
        A permutation of the nodes.

    Returns
    -------
    : float
        Sum of the edge costs.
    """
    return sum( graph.edges[edge]['cost'] for edge in _edgelist(solution) )

def _log( operator:str, objval:float ) -> None:
    """
    Prints log.
    
    Args
    ----
    operator: str
        Name of the local search operator.
    objval: float
        Current objective value.
    """
    print( f'{operator[:20]:20s} │ {objval:8.2f}' )

def _log_table( config:str= 'm' ) -> None:
    """
    Prints log table.
    
    Args
    ----
    config: str
        't' for top rule, 'h' for header, 'm' for midrule, 'b' for bottomrule
    """
    if VERBOSITY_LEVEL == 0:
        return
    
    for c in config:
        if c == 't':
            print( '─────────────────────┬────────────' )
        elif c == 'h':
            print( 'operator             │ objval     ' )
        elif c == 'm': 
            print( '─────────────────────┼────────────' )
        elif c == 'b':        
            print( '─────────────────────┴────────────' )

def _animate_search( graph:nx.DiGraph, solutions:list[list[int]] ) -> None:
    """
    Creates an animation from the given solutions and shows it.
    
    Args
    ----
    graph: nx.DiGraph
        A networkx digraph (with 'pos' and 'cost' attributes).
    solutions: list[list[int]]
        A list of Hamiltonian tours given as permutations of the nodes.
    """
    fig, ax = plt.subplots()

    pos = nx.get_node_attributes( graph, 'pos' )

    def update(frame):
        ax.clear()    
        nx.draw_networkx_nodes( graph, pos, node_size= 50, ax= ax )
        nx.draw_networkx_edges( graph, pos, edgelist= _edgelist(solutions[frame]), ax= ax )
        plt.xlabel( f'Length: {_evaluate_solution( graph, solutions[frame] ):.2f}' )

    _ = animation.FuncAnimation( fig, update, frames= len(solutions), interval= 500, repeat= False )

    plt.show()

def _improve_by_node_relocations( graph:nx.digraph, solution:list ):
    """
    Tries to improve the given solution by node relocations.

    Args
    ----
    graph: nx.DiGraph
        A networkx directed graph.
    solution: list[int]
        A Hamiltonian tour as a permutation of the nodes.

    Returns
    -------
    best_solution: list[int]
        Best found solution (a permutation of the nodes).
    best_cost: float
        Cost of the best solution.
    improved: bool
        Whether the solution was improved.
    """
    assert len(graph) == len(solution), 'solution does not fit to graph!'

    init_cost     = _evaluate_solution( graph, solution )
    best_cost     = init_cost
    best_solution = solution[:] # copy !
    improved      = False

    # check all index permutations
    for (i,j) in it.permutations( range(1,len(solution)), 2 ): # NOTE : keep 0 in the first place!
        # relocate node from position i to position j
        working_solution = solution[:i] + solution[i+1:]                               # "remove" element from position i
        working_solution = working_solution[:j] + [solution[i]] + working_solution[j:] # "insert" element to position j

        # evaluate solution
        working_cost = _evaluate_solution( graph, working_solution )

        # update best solution, if possible
        if working_cost + 0.001 < best_cost:
            best_cost     = working_cost
            best_solution = working_solution[:] # copy !
            improved      = True
            
            if 2 <= VERBOSITY_LEVEL:
                _log( '', best_cost )

    if improved:
        _log( 'relocate node', best_cost )
    
    return best_solution, best_cost, improved

def _improve_by_node_swaps( graph:nx.digraph, solution:list ):
    """
    Tries to improve the given solution by node swaps.

    Args
    ----
    graph: nx.DiGraph
        A networkx directed graph.
    solution: list[int]
        A Hamiltonian tour as a permutation of the nodes.

    Returns
    -------
    best_solution: list[int]
        Best found solution (a permutation of the nodes).
    best_cost: float
        Cost of the best solution.
    improved: bool
        Whether the solution was improved.
    """
    raise NotImplementedError( 'operator is not implemented')

def _improve_by_2_opt( graph:nx.digraph, solution:list ):
    """
    Tries to improve the given solution by 2-opt.

    Args
    ----
    graph: nx.DiGraph
        A networkx directed graph.
    solution: list[int]
        A Hamiltonian tour as a permutation of the nodes.

    Returns
    -------
    best_solution: list[int]
        Best found solution (a permutation of the nodes).
    best_cost: float
        Cost of the best solution.
    improved: bool
        Whether the solution was improved.
    """
    raise NotImplementedError( 'operator is not implemented')

def local_search( graph:nx.DiGraph, draw_progress:bool= True, draw_solutions:bool= False ) -> list[int]:
    """
    Solves TSP with a simple local-search procedure.

    NOTE: This is a proof-of-concept implementation.
    For efficiency, it would be better
    - to use, for example, doubly linked lists instead of python lists;
    - not to copy solutions;
    - to evaluate only the delta cost of the operation instead of the full tour; etc.

    Args
    ----
    graph: nx.DiGraph
        A networkx directed graph.
    draw_progress: bool
        Should we draw the cost evolution over iterations?
    draw_solutions: bool
        Should we draw solutions?

    Returns
    -------
    best_solution: list[int]
        Best found solution (a permutation of the nodes).
    """
    # init
    solutions = []

    # create primitive initial solution
    solution = list( graph.nodes )
    random.shuffle( solution )
    solutions.append( solution[:] )
    
    _log( 'initial', _evaluate_solution( graph, solution ) )

    # improve solution
    while True:
        solution, cost, improved = _improve_by_node_relocations( graph, solution )
        #solution, cost, improved = _improve_by_node_swaps( graph, solution )
        #solution, cost, improved = _improve_by_2_opt( graph, solution )

        if not improved:
            break

        solutions.append( solution[:] )

    # visualize results
    if draw_progress:
        plt.xlabel( 'Iterations' )
        plt.ylabel( 'Cost' )
        plt.plot( [ _evaluate_solution( graph, solution ) for solution in solutions ] )
        plt.show()

    if draw_solutions:        
        _animate_search( graph, solutions )

    return solution

if __name__ == '__main__':
    graph = random_euclidean_graph( 30 )
    
    _log_table( 'thm' )

    local_search( graph, draw_progress= False, draw_solutions= False )
    
    _log_table( 'b' )

# FYI: optimal solution values for random_euclidean_graph(n):
#
#                11: 284.65     21: 354.40     31: 488.63     41: 511.48      60: 598.22
#                12: 296.56     22: 354.44     32: 491.26     42: 512.28      70: 627.60
#  3: 191.11     13: 297.13     23: 354.45     33: 491.67     43: 515.49      80: 687.79
#  4: 193.70     14: 297.81     24: 370.30     34: 491.71     44: 522.10      90: 722.55
#  5: 244.41     15: 300.48     25: 404.66     35: 492.12     45: 522.28     100: 758.56
#  6: 249.96     16: 305.05     26: 416.62     36: 501.79     46: 534.62     110: 791.41
#  7: 251.18     17: 306.31     27: 449.81     37: 502.62     47: 536.01     120: 838.39
#  8: 251.18     18: 324.09     28: 455.02     38: 510.96     48: 547.35     130: 876.79
#  9: 256.84     19: 332.72     29: 473.85     39: 511.20     49: 549.40     140: 921.44
# 10: 281.54     20: 346.15     30: 477.89     40: 511.21     50: 558.00     150: 941.17
