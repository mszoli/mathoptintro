import random

def random_knapsack_instance( n:int, seed:int= 0 ) -> tuple[list[int],list[int],int]:
    """
    A simple instance generator for the **Binary/Integer Knapsack Problem**.

    Args
    ----
    n: int
        Desired number of items. Should be a positive integer (not checked).
    seed: int
        Random seed.

    Returns
    -------
    profits: list[int]
        Profits: profits[j] is the profit of item j (j=0,...,n-1).
    weights: list[int]
        Weights: weights[j] is the weight (size) of item j (j=0,...,n-1).
    capacity: int
        Capacity of the knapsack.
    """
    random.seed( seed )

    profits = [ random.randint(20,50) for _ in range(n) ]
    weights = [ random.randint(20,50) for _ in range(n) ]
    capacity = int(sum( weights ) * 0.75)

    return profits, weights, capacity

def random_binpacking_instance_uniform( n:int= 120, seed:int= 0 ) -> tuple[list[int],int]:
    """
    Returns a random instance for the **Bin Packing Problem** based on the following paper:

    Martello, S., & Toth, P. (1990).
    *Lower bounds and reduction procedures for the bin packing problem*.
    Discrete applied mathematics, 28(1), 59-70.
    
    Args
    ----
    n: int
        Desired number of items. Should be a positive integer (not checked).
    seed: int
        Random seed.

    Returns
    -------
    items: list[int]
        Items: items[j] is the size of item j (j=0,...,n-1).
    capacity: int
        Bin capacity.
    """
    random.seed(seed)

    # Three classes of randomly generated item sizes:
    # (1) sizes uniformly random between  1 and 100
    # (2) sizes uniformly random between 20 and 100
    # (3) sizes uniformly random between 50 and 100
    items = [ random.randint(20,100) for _ in range(n) ]

    # For each class, three capacity values have been considered: 100, 120, and 150.
    capacity = 150 

    return items, capacity

def random_binpacking_instance_triplets( t:int= 20, seed:int= 0 ) -> tuple[list[int],int]:
    """
    Returns a random instance for the **Bin Packing Problem** based on the following paper:

    Falkenauer, E. (1996).
    *A hybrid grouping genetic algorithm for bin packing*.
    Journal of heuristics, 2(1), 5-30.
    
    Args
    ----
    t: int
        Desired number of triplets (resulting 3t items). Should be a positive integer (not checked).
    seed: int
        Random seed.

    Returns
    -------
    items: list[int]
        Items: items[j] is the size of item j (j=0,...,3t-1).
    capacity: int
        Bin capacity.
    """
    random.seed(seed)

    # Considering bin capacity of 1000.
    capacity = 1000

    # An item was first generated with a size drawn uniformly from the range [380,490].
    # That left a space s of between 510 and 620 in the bin of 1000.
    # The size of the second item was drawn uniformly from [250,s/2].
    # The third item completed the bin.
    items = []

    for _ in range(t):
        items.append( random.randint(380,490) )
        items.append( random.randint(250,(1000 - items[-1])//2 ) )
        items.append( 1000 - items[-1] - items[-2] )

    return items, capacity
