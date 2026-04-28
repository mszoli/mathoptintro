import simpy
import itertools as it

# EXERCISES:
# 1. Implement a policy, where the vehicle waits at its current location, if the waiting time at the next visit, if any, would be long.

ORDERS = [
    {
        "location":       [10,0],
        "release_time":   2,
        "service_time":   5,
        "earliest_start": 32
    },
    {
        "location":       [0,5],
        "release_time":   5,
        "service_time":   5,
        "earliest_start": 5
    },
    {
        "location":       [5,10],
        "release_time":   16,
        "service_time":   5,
        "earliest_start": 26
    },
    {
        "location":       [10,10],
        "release_time":   25,
        "service_time":   5,
        "earliest_start": 40
    }
]

def travel_time( origin:tuple[int,int], destination:tuple[int,int] ) -> int:
    """
    Returns the Manhattan-distance-based travel time between the given locations.
    """
    return abs( origin[0] - destination[0] ) + abs( origin[1] - destination[1] )

class Visit:
    def __init__(self) -> None:
        # base data
        self.location:tuple[int,int] = None
        self.release_time:int = 0
        self.earliest_service_start_time:int = 0
        self.service_time:int = 0

        # simulation data
        self._arrival_time:int = None
        self._service_start_time:int = None
        self._service_end_time:int = None
        self._departure_time:int = None

        self.rejected:bool = False

class Model:
    def __init__( self ) -> None:
        self.env = simpy.Environment()

        # visits
        self.visits:list[Visit] = []

        # vehicle
        self.previous_visits:list[Visit] = []
        self.current_visit:Visit = None
        self.next_visits:list[Visit] = []

        # init
        self.current_visit = Visit()
        self.current_visit.location = (0,0)        
        self.current_visit._arrival_time = 0
        self.current_visit._service_start_time = 0
        self.current_visit._service_end_time = 0

    @property
    def previous_visit(self) -> Visit:
        """Returns the previous visit, if any."""
        return self.previous_visits[-1]
    
    @property
    def next_visit(self) -> Visit:
        """Returns the next visit, if any."""
        return next( iter(self.next_visits), None )
    
    @property
    def vehicle_is_idle(self) -> bool:
        """Returns whether the vehicle is idle."""
        return self.current_visit is not None and self.current_visit._service_end_time is not None

    def run( self, dynamic:bool = False ):
        """Starts simulation."""
        if dynamic:
            self.env.process( self.__dynamic_visits() )
        else:
            self.env.process( self.__static_visits() )

        print( f'{self.env.now:5d} | START' )
        self.env.run()
        print( f'{self.env.now:5d} | END' )

    def __load_visits( self ) -> list[Visit]:
        visits = []

        for raw_visit in ORDERS:
            visit = Visit()
            visit.location = tuple(raw_visit['location'])
            visit.service_time = raw_visit['service_time']
            visit.release_time = raw_visit['release_time']
            visit.earliest_service_start_time = raw_visit['earliest_start']

            visits.append( visit )

        return visits

    def __static_visits(self):
        """Generates "static" visits."""
        self.visits = self.__load_visits()
        
        if self.vehicle_is_idle:
            self.env.process( self.__routing() )

        yield self.env.timeout(0)

    def __dynamic_visits(self):
        """Generates visits on the fly."""
        visits = self.__load_visits()
        visits.sort( key= lambda visit : visit.release_time )

        for visit in visits:
            yield self.env.timeout( visit.release_time - self.env.now )

            self.visits.append( visit )
            print( f'{self.env.now:5d}*| visit is requested at {visit.location} (earliest_start {visit.earliest_service_start_time})' )
            
            if self.vehicle_is_idle:
                self.env.process( self.__routing() )

        print( f'{self.env.now:5d} | no more requests' )

    def __start_vehicle(self):
        """Executes the current route of the vehicle, if any."""
        assert self.vehicle_is_idle, 'could not start vehicle since it is not idle'

        if self.next_visit is None:
            return # nothing to do

        while self.next_visit is not None:
            # departure
            self.current_visit._departure_time = self.env.now
            self.previous_visits.append( self.current_visit )
            self.current_visit = None

            print( f'{self.env.now:5d} | vehicle is departed from location {self.previous_visit.location} to location {self.next_visit.location}' )

            # travel
            yield self.env.timeout( travel_time( self.previous_visit.location, self.next_visit.location ) )            

            # arrival
            self.current_visit = self.next_visit
            self.current_visit._arrival_time = self.env.now            
            self.next_visits = self.next_visits[1:]

            print( f'{self.env.now:5d} | vehicle is arrived at location {self.current_visit.location}' )

            # service start
            if self.env.now < self.current_visit.earliest_service_start_time:
                print( f'{self.env.now:5d} | wait until time {self.current_visit.earliest_service_start_time}...' )

                yield self.env.timeout( self.current_visit.earliest_service_start_time - self.env.now )

            self.current_visit._service_start_time = self.env.now

            print( f'{self.env.now:5d} | service is started' )

            # service
            yield self.env.timeout( self.current_visit.service_time )

            # service end
            self.current_visit._service_end_time = self.env.now

            print( f'{self.env.now:5d} | service is finished' )

        self.env.process( self.__routing() )

    def __routing(self):
        """Routing process."""
        visits_to_do = [ visit for visit in self.visits if not visit.rejected and visit._service_start_time is None ]

        if len(visits_to_do) == 0:            
            print( f'{self.env.now:5d} | there are no more visits at the moment' )
            return
    
        print( f'{self.env.now:5d} | routing for {len(visits_to_do)} visit(s)...' )

        self.next_visits = routing_algorithm( self.env.now, self.current_visit, visits_to_do )
        
        if 0 == len(self.next_visits):
            print( f'{self.env.now:5d} | routing is finished | no route' )
        else:
            finish_time = calculate_finish_time( self.env.now, self.current_visit, self.next_visits )
            print( f'{self.env.now:5d} | routing is finished | expected finish time: {finish_time}' )

        yield self.env.process( self.__start_vehicle() )

def calculate_finish_time( current_time:int, current_visit:Visit, visits_to_do:list[Visit] ) -> int:
    """
    Calculates the finish time of the route for the IDLE vehicle.
    """
    finish_time = current_time

    previous_visit = current_visit
    for visit in visits_to_do:
        finish_time += travel_time( previous_visit.location, visit.location )
        finish_time = max( finish_time, visit.earliest_service_start_time )
        finish_time += visit.service_time

        previous_visit = visit

    return finish_time

def routing_algorithm( current_time:int, current_visit:Visit, visits_to_do:list[Visit] ) -> list[Visit]:
    """Naive routing algorithm."""    
    return min( it.permutations(visits_to_do), key= lambda route: calculate_finish_time( current_time, current_visit, route ) )

if __name__ == '__main__':
    Model().run( dynamic= False )
