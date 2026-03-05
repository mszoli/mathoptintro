import networkx as nx
import itertools as it
import random
import math

def random_euclidean_graph( nnodes:int, seed:int= 0 ) -> nx.DiGraph:
    """
    Returns a random directed complete graph with the given number of nodes.
    Each node has the attribute 'pos' with the coordinates of the node.
    Each edge has the attribute 'cost' with the Euclidean distance of the corresponding nodes.

    Args
    ----
    nnodes: int
        Desired number of nodes.
    seed: int
        Random seed.

    Returns
    -------
    graph: nx.DiGraph
        Directed complete graph with node attributes 'pos', and edge attributes 'cost'.
    """
    # initialize
    random.seed( seed )

    NODES = range(nnodes)

    # CREATE GRAPH
    graph = nx.DiGraph()

    # generate random coordinates 
    coords = { u : (random.randint(0,100),random.randint(0,100)) for u in NODES }

    # add nodes to the graph with attribute 'pos'
    for u in NODES:
        graph.add_node( u, pos= coords[u] )

    # add edges to the graph with attribute 'cost'
    for (u,v) in it.permutations(graph.nodes,2):
        graph.add_edge( u, v, cost= math.dist( coords[u], coords[v] ) )

    return graph

def tetrahedron_instance( n:int, m:int ) -> nx.DiGraph:
    """
    Return the corresponding tetrahedron graph (with 3(n+m)-2 nodes) based on the following paper:

    Hougardy, S., & Zhong, X. (2021).
    *Hard to solve instances of the euclidean traveling salesman problem*.
    Mathematical Programming Computation, 13, 51-74.

    Args
    ----
    n: int
        The n-parameter of the tetrahedron graph.
    m: int
        The m-parameter of the tetrahedron graph.
        
    Returns
    -------
    graph: nx.DiGraph
        Directed complete graph with node attributes 'pos', and edge attributes 'cost'.
    """
    graph = nx.DiGraph()

    # nodes
    for i in range(n):
        graph.add_node( len(graph.nodes), pos= (n - i/2, i*math.sqrt(3)/2) )
        graph.add_node( len(graph.nodes), pos= (n/2 - i/2, (n-i)*math.sqrt(3)/2) )
        graph.add_node( len(graph.nodes), pos= (i, 0) )

    for j in range(1,m):
        graph.add_node( len(graph.nodes), pos= (j*n/(2*m), j*n/(2*math.sqrt(3)*m) ) )
        graph.add_node( len(graph.nodes), pos= (n - j*n/(2*m), j*n/(2*math.sqrt(3)*m) ) )
        graph.add_node( len(graph.nodes), pos= (n/2, n*math.sqrt(3)/2 - j*n/(math.sqrt(3)*m) ) )

    graph.add_node( len(graph.nodes), pos= (n/2, n/(2*math.sqrt(3)) ) )

    # edges
    pos = nx.get_node_attributes( graph, 'pos' )
    for (u,v) in it.permutations(graph.nodes,2):
        graph.add_edge( u, v, cost= math.dist( pos[u], pos[v] ) )

    return graph
