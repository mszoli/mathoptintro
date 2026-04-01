import networkx as nx
import itertools as it
import matplotlib.pyplot as plt

from ortools.math_opt.python import mathopt
from time import perf_counter

# EXERCISES
# 1.1 Implement the Gravish-Graves formulation in function solve_tsp_gg.
# 1.2 Implement the branch-and-cut procedure for the Gravish-Graves formulation.

def _draw_graph( graph:nx.DiGraph, edge_labels= None ) -> None:
    """
    Draws the given graph.
    
    Args
    ----
    graph: nx.DiGraph
        Directed graph.
    edge_labels:
        edge labels (optional)
    """
    nx.draw( graph, pos= nx.get_node_attributes( graph, 'pos' ), node_size= 50 )

    if edge_labels is not None:
        nx.draw_networkx_edge_labels( graph,  pos= nx.get_node_attributes( graph, 'pos' ), edge_labels= edge_labels, label_pos= 0.75 )

    plt.show( block= True ) # NOTE: blocks the execution!

def _log( model:mathopt.Model, result:mathopt.SolveResult, *, ncuts:int= 0, build_time:float= None, solve_time:float= None ) -> None:
    """
    Prints log.

    Args
    ----
    model: mathopt.Model
        Model.
    result: mathopt.SolveResult
        Solve result.
    ncuts: int
        Number of separated subtour elimination constraints, if any.
    build_time: float
        Time to build the model.
    solve_time: float
        Time to solve the model.
    """
    buffer = [
        f'{model.name:10s}',
        f'{result.termination.reason.name:10s}',
        f'{model.get_num_variables():5d}',
        f'{model.get_num_linear_constraints():5d}',
        f'{ncuts:5d}',
        f'{result.objective_value():6.1f}',
        f'{build_time:7.4f}' if build_time else "       ",
        f'{solve_time if solve_time else result.solve_stats.solve_time.total_seconds():7.4f}',
    ]
    print( ' │ '.join(buffer) )

def solve_tsp_dfj( graph:nx.DiGraph, solver_type:mathopt.SolverType= mathopt.SolverType.GSCIP, draw_instance:bool= False, draw_solution:bool= False ) -> None:
    """
    Solves TSP as a MIP (DFJ formulation) with **OR-Tools MathOpt**.
    All subtour-elimination constraints are added to the model in advance.

    Dantzig, G. B., Fulkerson, D. R., & Johnson, S. M. (1959).
    *On a linear-programming, combinatorial approach to the traveling-salesman problem*.
    Operations Research, 7(1), 58-66.

    Args
    ----
    graph: nx.DiGraph
        A digraph where each edge has the attribute 'cost'.
    solver_type: mathopt.SolverType
        The underlying solver to use (e.g., GSCIP, HIGHS, GUROBI).
    draw_instance: bool
        Should we draw the instance graph?
    draw_solution:
        Should we draw the optimal Hamiltonian tour?
    """
    if draw_instance:
        _draw_graph( graph )

    # BUILD MODEL
    build_start = perf_counter()

    model = mathopt.Model( name= 'DFJ' )

    # variables: x[(u,v)] = 1 <-> edge (u,v) is included in the tour
    x = { (u,v) : model.add_binary_variable( name= f'x{u}_{v}' ) for (u,v) in graph.edges }

    # objective
    edge_costs = nx.get_edge_attributes( graph, 'cost' )
    model.minimize( sum( x[edge] * edge_costs[edge] for edge in graph.edges ) )

    # constraints for nodes: in = out = 1
    for v in graph.nodes:
        model.add_linear_constraint( sum( x[edge] for edge in graph.out_edges(v) ) == 1 )
        model.add_linear_constraint( sum( x[edge] for edge in graph.in_edges(v) ) == 1 )

    # subtour-elimination constraints    
    def nodesets( graph:nx.DiGraph ):
        """ Returns an iterator for the non-trivial node subsets of the given graph."""
        return it.chain.from_iterable( it.combinations( graph.nodes, size ) for size in range(2,graph.number_of_nodes() ) )

    for subset in nodesets(graph):
        vars = [ x[(u,v)] for (u,v) in graph.edges if u in subset and v in subset ]

        if 1 <= len(vars): # at least one variable is needed for a constraint
            model.add_linear_constraint( sum(vars) <= len(subset)-1 )

    build_end = perf_counter()

    # SOLVE PROBLEM
    result = mathopt.solve( model, solver_type= solver_type )

    _log( model, result, build_time=build_end-build_start )

    if draw_solution and result.termination.reason in [mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE]:
        _draw_graph( graph.edge_subgraph( edge for edge in graph.edges if 0.9 < result.variable_values(x[edge]) ) )

def solve_tsp_dfj_constraint_generation( graph:nx.DiGraph, solver_type:mathopt.SolverType= mathopt.SolverType.GSCIP, draw_instance:bool= False, draw_solution:bool= False ) -> None:
    """
    Solves TSP as a MIP (DFJ formulation) with **OR-Tools MathOpt** iteratively,
    that is, subtour-elimination constraints are added to the model when needed.

    Args
    ----
    graph: nx.DiGraph
        A digraph where each edge has the attribute 'cost'.
    solver_type: mathopt.SolverType
        The underlying solver to use (e.g., GSCIP, HIGHS, GUROBI).
    draw_instance: bool
        Should we draw the instance graph?
    draw_solution:
        Should we draw the optimal Hamiltonian tour?
    """
    if draw_instance:
        _draw_graph( graph )

    # BUILD MODEL
    build_start = perf_counter()

    model = mathopt.Model( name= 'CONS-GEN' )

    # variables: x[(u,v)] = 1 <-> edge (u,v) is included in the tour
    x = { (u,v) : model.add_binary_variable( name= f'x{u}_{v}' ) for (u,v) in graph.edges }

    # objective
    edge_costs = nx.get_edge_attributes( graph, 'cost' )
    model.minimize( sum( x[edge] * edge_costs[edge] for edge in graph.edges ) )

    # constraints for nodes: in = out = 1
    for v in graph.nodes:
        model.add_linear_constraint( sum( x[edge] for edge in graph.out_edges(v) ) == 1 )
        model.add_linear_constraint( sum( x[edge] for edge in graph.in_edges(v) ) == 1 )

    # constraints: subtour-elimination for edges
    for (u,v) in it.combinations(graph.nodes,2):
        if (u,v) in graph.edges and (v,u) in graph.edges:
            model.add_linear_constraint( x[(u,v)] + x[(v,u)] <= 1 )

    build_end = perf_counter()

    # CONSTRAINT GENERATION
    noriginal_conss = model.get_num_linear_constraints()
    
    solve_start = perf_counter()

    while True:
        # solve problem
        result = mathopt.solve( model, solver_type= solver_type )

        if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
            break

        # check connectivity
        subgraph = graph.edge_subgraph( edge for edge in graph.edges if 0.9 < result.variable_values(x[edge]) )

        if draw_solution:
            _draw_graph( subgraph )

        if nx.is_strongly_connected( subgraph ):
            break # everything is awesome
        
        # add new subtour-elimination constraints to the model
        for component in nx.strongly_connected_components( subgraph ):
            vars = [ x[edge] for edge in graph.edges if edge[0] in component and edge[1] in component ]

            if 1 <= len(vars): # at least one variable is needed for a constraint
                model.add_linear_constraint( sum(vars) <= len(component)-1 )

    solve_end = perf_counter()

    _log( model, result, ncuts= model.get_num_linear_constraints()-noriginal_conss, build_time=build_end-build_start, solve_time= solve_end-solve_start )

class TSPCutSeparator:
    def __init__( self, graph:nx.DiGraph, x:dict ):
        self.graph:nx.DiGraph = graph
        self.x:dict = x
        self.ncuts:int = 0
        self.nodepairs:list = []
        self.MINIMUM_VIOLATION = 0.1
        
        # for each node we store its farthest partner
        edge_costs = nx.get_edge_attributes( graph, 'cost' )
        for node in graph.nodes:
            longest_edge = None

            for (i,j) in graph.out_edges(node):
                if longest_edge is None or edge_costs[longest_edge] < edge_costs[(i,j)]:
                    longest_edge = (i,j)

            self.nodepairs.append( (node,j) )

    def __call__( self, callback_data:mathopt.CallbackData ) -> mathopt.CallbackResult:
        result = mathopt.CallbackResult()
        flowgraph = nx.DiGraph()

        for (u,v) in self.graph.edges:
            flowgraph.add_edge( u, v, capacity= callback_data.solution[self.x[(u,v)]] )

        for (s,t) in self.nodepairs:           
            value, (subset, _) = nx.minimum_cut( flowgraph, s, t )

            if value + self.MINIMUM_VIOLATION < 1:
                vars = [ self.x[(u,v)] for (u,v) in self.graph.edges if u in subset and v in subset ]

                if 1 <= len(vars): # at least one variable is needed for a constraint
                    result.add_user_cut( sum( vars ) <= len(subset) - 1 )
                    self.ncuts += 1

        return result

def solve_tsp_mtz( graph:nx.DiGraph, solver_type:mathopt.SolverType= mathopt.SolverType.GSCIP, strengthened:bool= False, separation:bool= False, draw_instance:bool= False, draw_solution:bool= False ) -> None:
    """
    Solves TSP as a MIP (MTZ formulation) with **OR-Tools MathOpt**.

    Miller, C. E., Tucker, A. W., & Zemlin, R. A. (1960).
    *Integer programming formulation of traveling salesman problems*.
    Journal of the ACM (JACM), 7(4), 326-329.
    
    Desrochers, M., & Laporte, G. (1991).
    *Improvements and extensions to the Miller-Tucker-Zemlin subtour elimination constraints*.
    Operations Research Letters, 10(1), 27-36.
        
    Args
    ----
    graph: nx.DiGraph
        A digraph where each edge has the attribute 'cost'.
    solver_type: mathopt.SolverType
        The underlying solver to use (e.g., GSCIP, GUROBI).
        NOTE that HIGHS does not support branch-and-cut.
    strengthened: bool
        Should we use strengthened big-M constraints?
    separation: bool
        Should we separate subtour-elimination constraints?
    draw_instance: bool
        Should we draw the instance graph?
    draw_solution:
        Should we draw the optimal Hamiltonian tour?
    """
    if draw_instance:
        _draw_graph( graph )

    # INIT
    M = nx.number_of_nodes(graph)-1

    # BUILD MODEL
    model = mathopt.Model( name= f'MTZ{"-S" if strengthened else ""}{"-SEP" if separation else ""}' )

    # variables: x[(u,v)] = 1 <-> edge (u,v) is included in the tour
    x = { (u,v) : model.add_binary_variable( name= f'x{u}_{v}' ) for (u,v) in graph.edges }

    # objective
    edge_costs = nx.get_edge_attributes( graph, 'cost' )
    model.minimize( sum( x[edge] * edge_costs[edge] for edge in graph.edges ) )

    # variables: y[u] is an index of node u
    y = { u : model.add_variable( lb= 0, ub= M, name= f'y_{u}' ) for u in graph.nodes }

    # constraints: incoming = outgoing = 1
    for v in graph.nodes:
        model.add_linear_constraint( sum( x[edge] for edge in graph.out_edges(v) ) == 1 )
        model.add_linear_constraint( sum( x[edge] for edge in graph.in_edges(v) ) == 1 )

    # constraints: x(u,v) = 1 => y(u) + 1 <= y(v)
    s = list( graph.nodes )[0]
    y[s].upper_bound = 0

    for (u,v) in graph.edges:
        if v == s:
            continue
        
        # model.add_indicator_constraint( indicator= x[(u,v)], implied_constraint= y[u] + 1 <= y[v] )
        # continue

        if strengthened and (v,u) in graph.edges:
            model.add_linear_constraint( y[u] - y[v] + M*x[(u,v)] + (M-2)*x[(v,u)] <= M-1 )
        else:
            model.add_linear_constraint( y[u] + 1 <= y[v] + M*(1-x[(u,v)]) )

    # SOLVE PROBLEM
    callback_reg = mathopt.CallbackRegistration( events={mathopt.Event.MIP_NODE}, add_cuts= True ) if separation else None # TODO: MIP_NODE: GUROBI only ?
    cb = TSPCutSeparator( graph, x ) if separation else None

    result = mathopt.solve( model, solver_type= solver_type, callback_reg= callback_reg, cb= cb )

    _log( model, result, ncuts= cb.ncuts if separation else 0 )

    if draw_solution and result.termination.reason in [mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE]:
        _draw_graph( graph.edge_subgraph( edge for edge in graph.edges if 0.9 < x[edge].x ) )

def solve_tsp_gg( graph:nx.DiGraph, solver_type:mathopt.SolverType= mathopt.SolverType.GSCIP, draw_instance:bool= False, separation:bool= False, draw_solution:bool= False ) -> None:
    """
    Solves TSP as a MIP (GG formulation) with **OR-Tools MathOpt**.

    Gavish, B., & Graves, S. C. (1978).
    *The travelling salesman problem and related problems*.
        
    Args
    ----
    graph: nx.DiGraph
        A digraph where each edge has the attribute 'cost'.
    solver_type: mathopt.SolverType
        The underlying solver to use (e.g., GSCIP, GUROBI).
        NOTE that HIGHS does not support branch-and-cut.
    separation: bool
        Should we separate subtour-elimination constraints?
    draw_instance: bool
        Should we draw the instance graph?
    draw_solution:
        Should we draw the optimal Hamiltonian tour?
    """
    raise NotImplementedError( 'function solve_tsp_gg is not implemented' )

if __name__ == '__main__':
    from tsp_instances import random_euclidean_graph, tetrahedron_instance

    D = random_euclidean_graph( 12 )
    # D = tetrahedron_instance( 4,4 )

    solver_type = mathopt.SolverType.GSCIP # NOTE: HIGHS do not support branch-and-cut!

    print( '───────────┬────────────┬───────┬───────┬───────┬────────┬─────────┬────────' )
    print( 'model      │ status     │  vars │ conss │  cuts │ objval │   build │   solve' )
    print( '───────────┼────────────┼───────┼───────┼───────┼────────┼─────────┼────────' )

    solve_tsp_dfj( D, solver_type= solver_type, draw_solution= True ) # check D with nnodes= 15
    # solve_tsp_dfj_constraint_generation( D, solver_type= solver_type, draw_solution= False )
    # solve_tsp_mtz( D, solver_type= solver_type )
    # solve_tsp_mtz( D, solver_type= solver_type, strengthened= True )
    # solve_tsp_mtz( D, solver_type= solver_type, separation= True )
    # solve_tsp_mtz( D, solver_type= solver_type, strengthened= True, separation= True )
    # solve_tsp_gg( D, separation= False )
    # solve_tsp_gg( D, separation= True )

    print( '───────────┴────────────┴───────┴───────┴───────┴────────┴─────────┴────────' )
