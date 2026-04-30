import networkx as nx
import itertools as it
import matplotlib.pyplot as plt
import random
import numpy as np

from tsp_instances import random_euclidean_graph
from tsp_ls_1 import _evaluate_solution

def tabu_search( graph:nx.DiGraph, max_iterations:int= 100, tabu_length:int= 10, draw_progress:bool= False ) -> list:
    """
    Solves TSP with Tabu Search.

    Args
    ----
    graph: nx.DiGraph
        A networkx digraph (with 'cost' edge attributes).
    max_iterations: int
        Maximum number of iterations.
    tabu_length: int
        Length of the tabu list.
    draw_progress: bool
        Should we draw the cost evolution over iterations?

    Returns
    -------
    best_global_solution: list[int]
        Best found solution (a permutation of the nodes).
    """
    # create primitive initial solution
    curr_solution = list(graph.nodes)

    # init
    best_global_solution = curr_solution[:]
    best_global_cost = _evaluate_solution( graph, curr_solution )

    tabu_list = []
    costs = [ best_global_cost ]

    # TABU SEARCH
    print( '─────┬────────────┬─────────────' )
    print( 'iter │ current    │ best        ' )
    print( '─────┼────────────┼─────────────' )

    for iterations in range(max_iterations):
        # find best neighbor w.r.t. swaps
        best_neighbor = None
        best_neighbor_cost = float('inf')
        best_swap = None

        for (i,j) in it.combinations(range(len(curr_solution)),2):
            # check tabu list
            if (i,j) in tabu_list:
                continue

            # swap nodes i and j
            neighbor_solution = curr_solution[:]
            neighbor_solution[j], neighbor_solution[i] = curr_solution[i], curr_solution[j]

            neighbor_cost = _evaluate_solution( graph, neighbor_solution )

            # update best NEIGHBOR solution, if possible
            if neighbor_cost + 0.001 < best_neighbor_cost:
                best_neighbor = neighbor_solution[:]
                best_neighbor_cost = neighbor_cost
                best_swap = (i,j)

        if best_neighbor is None:
            break # no valid move

        # save cost
        costs.append( best_neighbor_cost )

        # adjust tabu list
        tabu_list.append( best_swap )

        if len(tabu_list) > tabu_length:
            tabu_list.pop(0)

        # update best GLOBAL solution, if possible
        log_postfix = ''
        if best_neighbor_cost + 0.001 < best_global_cost:
            best_global_solution = best_neighbor[:]
            best_global_cost = best_neighbor_cost
            log_postfix += ' +'

        # update current solution
        curr_solution = best_neighbor[:]

        print( f'{iterations:4d} │ {best_neighbor_cost:10.2f} │ {best_global_cost:10.2f}{log_postfix}' )

    print( '─────┴────────────┴─────────────' )

    # draw states
    if draw_progress:
        plt.xlabel( 'Iterations' )
        plt.ylabel( 'Cost' )
        plt.plot( costs )
        plt.plot( [ min(costs[:i+1]) for i in range(len(costs)) ] )
        plt.show()

    return best_global_solution

def simulated_annealing( graph:nx.DiGraph, temperature:float, cooling_rate:float, draw_progress:bool = False ) -> list[tuple[int,int]]:
    """
    Solves TSP with Simulated Annealing.

    Args
    ----
    graph: nx.DiGraph
        A networkx digraph (with 'cost' edge attributes).
    temperature: float
        Initial temperature.
    cooling_rate: float
        Rate at which temperature is decreased.
    draw_progress: bool
        Should we draw the cost evolution over iterations?

    Returns
    -------
    best_solution: list[int]
        Best found solution (a permutation of the nodes).
    """
    # create primitive initial solution
    curr_solution = list(graph.nodes)
    curr_cost = _evaluate_solution( graph, curr_solution )

    # init
    best_solution = curr_solution[:]
    best_cost = curr_cost

    costs = [ curr_cost ]

    # SIMULATED ANNEALING
    print( '────────────┬────────────┬───────────────' )
    print( 'temperature │ current    │ best          ' )
    print( '────────────┼────────────┼───────────────' )

    while temperature > 0.1:
        # random neighbor: swap random nodes
        i, j = random.sample(range(len(curr_solution)),2)
        new_solution = curr_solution[:]
        new_solution[j] = curr_solution[i]
        new_solution[i] = curr_solution[j]

        new_cost = _evaluate_solution( graph, new_solution )
        delta_cost = new_cost - curr_cost

        # accept?
        log_postfix = ''
        if delta_cost < -0.001 or random.random() < np.exp(-delta_cost / temperature):
            curr_solution = new_solution[:]
            curr_cost = new_cost
            costs.append( new_cost )
            log_postfix += ' +'

            if new_cost + 0.001 < best_cost:
                best_solution = new_solution[:]
                best_cost = new_cost
                log_postfix += ' +'

        # adjust temperature
        temperature *= cooling_rate

        print( f'{temperature:11.3f} │ {curr_cost:10.2f} │ {best_cost:10.2f}{log_postfix}' )

    print( '────────────┴────────────┴───────────────' )

    # draw states
    if draw_progress:
        plt.xlabel( 'Iterations' )
        plt.ylabel( 'Cost' )
        plt.plot( costs )
        plt.plot( [ min(costs[:i+1]) for i in range(len(costs)) ] )
        plt.show()

    return best_solution

def genetic_algorithm( graph:nx.DiGraph, population_size:int, generations:int, mutation_rate:float, draw_progress:bool= False ) -> list[tuple[int,int]]:
    """
    Solves TSP with Genetic Algorithm.

    Args
    ----
    graph: nx.DiGraph
        A networkx digraph (with 'cost' edge attributes).
    population_size: int
        Size of the population.
    generations: int
        Number of generations.
    mutation_rate: float
        Probability of mutation.
    draw_progress: bool
        Should we draw the cost evolution over iterations?

    Returns
    -------
    best_solution: list[int]
        Best found solution (a permutation of the nodes).
    """
    # init
    population = [ list(graph.nodes) for _ in range(population_size) ]
    
    for solution in population:
        random.shuffle( solution )

    population.sort( key= lambda individual: _evaluate_solution( graph, individual ) )

    best_costs  = []
    worst_costs = []

    # GENETIC ALGORITHM
    print( '───────────┬────────────┬───────────' )
    print( 'generation │ best       │ worst     ' )
    print( '───────────┼────────────┼───────────' )

    for generation in range(generations):        
        # elitism: 10% of the fittest population goes to the next generation
        new_population = population[:population_size//10]

        # from 50% of the fittest population, individuals will mate to produce offsprings
        for _ in range( population_size // 2 ):
            # crossover: keep prefix of the first parent and extend according to the second parent
            parent1, parent2 = random.sample( population[:population_size//2], 2 )
            crossover_point = random.randint( 0, len(parent1)-1 )
            offspring = parent1[:crossover_point] + [gene for gene in parent2 if gene not in parent1[:crossover_point]]

            # mutation: swap two random nodes
            if random.random() < mutation_rate:
                i, j = random.sample( range(len(solution)), 2 )
                offspring[i], offspring[j] = offspring[j], offspring[i]

            # store individuals in population
            if parent1 not in new_population: new_population.append( parent1 )
            if parent2 not in new_population: new_population.append( parent2 )
            if offspring not in new_population: new_population.append( offspring )
        
        # adjust population
        new_population.sort( key= lambda individual: _evaluate_solution( graph, individual ) )
        population = new_population[:population_size]
    
        best_costs.append( _evaluate_solution( graph, population[0] ) )
        worst_costs.append( _evaluate_solution( graph, population[-1] ) )

        print( f'{generation:10d} │ {best_costs[-1]:10.2f} │ {worst_costs[-1]:10.2f}' )

    print( '───────────┴────────────┴───────────' )

    if draw_progress:
        plt.xlabel( 'Generations' )
        plt.ylabel( 'Fitness value (Best/Worst)' )
        plt.plot( worst_costs )
        plt.plot( best_costs )
        plt.show()

    return population[0]

if __name__ == '__main__':
    graph = random_euclidean_graph( 30 )
    
    tabu_search( graph, tabu_length= len(graph)//5, max_iterations= 10*len(graph), draw_progress= True )
    # simulated_annealing( graph, temperature= 10000, cooling_rate= 0.99, draw_progress= True )
    # genetic_algorithm( graph, population_size= len(graph), generations= 10*len(graph), mutation_rate= 0.1, draw_progress= True )
    