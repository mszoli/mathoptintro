import math

RESTAURANT: tuple[int, int] = (0, 0)
T_DEADLINE: int = 60
CANCEL_COST: int = T_DEADLINE ** 2

MAP_SIZE: int = 30
PREP_TIME_MIN: int = 5
PREP_TIME_MAX: int = 20
WEIGHT_MIN: int = 1
WEIGHT_MAX: int = 5


def travel_time(a: tuple[int, int], b: tuple[int, int]) -> int:
    return math.ceil(math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2))
